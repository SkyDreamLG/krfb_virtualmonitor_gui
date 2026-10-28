"""KDE 钱包后端：kwalletd 的**原生** D-Bus 接口（`org.kde.KWallet`）。

为什么不用 freedesktop Secret Service：`org.freedesktop.secrets` 这个名字是先到先得
的 —— 系统里只要装了别的实现（gnome-keyring 等）并先占了总线名，密码就会写进那个
后端，和用户期望的"存进 KDE 钱包"完全对不上（本机实测就是如此）。而且 kwalletd 的
secret service 接口本身也可能被用户单独关掉。`org.kde.KWallet` 才是 KDE 自己的钱包
接口，只要钱包子系统开着就能用。

`open()` 会弹 KDE 的钱包密码框，而 D-Bus 调用**没有任何超时** —— 提示框弹不出来时
（无显示环境、从 systemd unit 启动、prompter 异常）这个调用永远不返回。因此：

  * 探测只用 `isEnabled` / `localWallet` / `isOpen` 这些不会弹框的方法；
  * 所有调用都走 `call_with_timeout`（daemon 线程 + 超时）；
  * jeepney 的连接不是线程安全的，全部调用串行化在一把锁后面；
  * **探测路径非阻塞抢锁**（`_try_lock`），抢不到就保持现状。
"""

from __future__ import annotations

from typing import Sequence

from .. import constants as C
from ..i18n import tr
from .base import (
    Backend,
    SecretTimeout,
    SecretsStatus,
    UnlockKind,
    UnlockResult,
    call_with_timeout,
)

# KWallet 的 D-Bus 坐标。kwalletd6 → kwalletd5 → 老 kwalletd，取第一个能用的。
_CANDIDATES = (
    ("org.kde.kwalletd6", "/modules/kwalletd6"),
    ("org.kde.kwalletd5", "/modules/kwalletd5"),
    ("org.kde.kwalletd", "/modules/kwalletd"),
)
_INTERFACE = "org.kde.KWallet"

# 密码写进标准文件夹「Passwords」：KWallet 的文件夹有类型，`writePassword` 写的是
# Password 类型条目，只有 "Passwords" 这个预置文件夹的类型一定匹配。
_FOLDER = "Passwords"

# 打开钱包时传给 kwalletd 的窗口 id。0 = 不挂父窗口（本模块刻意不依赖 Qt，
# 拿不到顶层窗口句柄；KDE 会自己把提示框放到合适的位置）。
_WID = 0


class KWalletBackend(Backend):
    key = "kwallet"
    unlock_kind = UnlockKind.SYSTEM_PROMPT

    def __init__(self, timeout: float) -> None:
        super().__init__(timeout)
        self._service: tuple[str, str] | None = None
        self._conn = None
        self._handle: int | None = None
        self._wallet = ""

    # --- D-Bus 底层 ---------------------------------------------------------
    def _connect(self):
        if self._conn is None:
            from jeepney.io.blocking import open_dbus_connection

            self._conn = open_dbus_connection(bus="SESSION")
        return self._conn

    def _raw_call(self, service: tuple[str, str], method: str, signature: str = "",
                  *args):
        """发一次 D-Bus 调用。调用方负责超时与加锁。

        **必须走 unwrap_msg**：jeepney 的 `send_and_get_reply` 对错误回复不抛异常，
        而是把错误消息原样返回 —— 直接读 `.body` 会把「服务不存在」这类错误文本
        当成调用结果（读密码时等于把错误信息当成了密码）。
        """
        from jeepney import DBusAddress, new_method_call
        from jeepney.wrappers import unwrap_msg

        address = DBusAddress(service[1], bus_name=service[0], interface=_INTERFACE)
        reply = self._connect().send_and_get_reply(
            new_method_call(address, method, signature, args)
        )
        body = unwrap_msg(reply)  # 错误回复在这里变成 DBusErrorResponse
        return body[0] if len(body) == 1 else body

    def _call(self, method: str, signature: str = "", *args):
        """带超时的调用；kwalletd6/5/老版依次试，记住第一个能通的。

        调用方必须**已经持有 `self._lock`**（`_try_lock` 只给探测路径用，
        其余路径用阻塞的 `_locked()`）。
        """
        candidates = list(_CANDIDATES)
        if self._service in candidates:
            candidates.remove(self._service)
            candidates.insert(0, self._service)

        last_error: Exception | None = None
        for candidate in candidates:
            try:
                value = call_with_timeout(
                    lambda c=candidate: self._raw_call(c, method, signature, *args),
                    self.timeout,
                )
            except SecretTimeout:
                raise
            except Exception as exc:  # noqa: BLE001 - 服务不在就换下一个
                last_error = exc
                continue
            self._service = candidate
            return value

        if last_error is not None:
            raise last_error
        raise RuntimeError("no kwalletd candidate")

    # --- 钱包操作 -----------------------------------------------------------
    def _wallet_name(self) -> str:
        """用户配置的"本钱包"名（KWallet 里可改，默认 kdewallet）。"""
        if self._wallet:
            return self._wallet
        name = self._call("localWallet") or ""
        if not name:
            wallets = self._call("wallets") or []
            name = wallets[0] if wallets else ""
        self._wallet = name
        return name

    def _is_open(self, wallet: str) -> bool:
        return bool(self._call("isOpen", "s", wallet))

    def _open(self, *, allow_prompt: bool) -> int | None:
        """拿钱包 handle。**只有 allow_prompt 时才允许触发解锁提示框。**

        钱包已经开着时 `open()` 不会弹框（实测：直接返回同一个 handle），
        所以普通读写路径可以放心调用它；只有钱包锁着时要拦。
        """
        wallet = self._wallet_name()
        if not wallet:
            return None
        if not allow_prompt and not self._is_open(wallet):
            return None
        handle = self._call("open", "sxs", wallet, _WID, C.APP_ID)
        if handle is None or (isinstance(handle, int) and handle < 0):
            return None
        self._handle = int(handle)
        return self._handle

    def _handle_for_rw(self) -> int | None:
        """读写用的 handle：钱包没开就返回 None（**绝不弹框**）。

        调用方已持有锁。
        """
        self._handle = None
        return self._open(allow_prompt=False)

    # --- 探测 ---------------------------------------------------------------
    def probe(self) -> SecretsStatus:
        """只用不会弹框的调用。锁被占（多半正卡在提示框上）时保持现状。"""
        if not self._try_lock():
            return self.status
        try:
            self._handle = None  # 钱包可能被随时锁上，缓存作废
            try:
                enabled = self._call("isEnabled")
            except SecretTimeout:
                self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
                return self.status
            except Exception as exc:  # noqa: BLE001 - 连不上 kwalletd 都归到这里
                self.status = SecretsStatus.NO_SERVICE
                self.status_detail = f"{type(exc).__name__}: {exc}"
                return self.status

            if not enabled:
                # 用户在系统设置里关掉了钱包子系统（kwalletrc 的 Enabled=false）
                self.status, self.status_detail = SecretsStatus.UNAVAILABLE, ""
                return self.status

            try:
                wallet = self._wallet_name()
                if not wallet:
                    self.status = SecretsStatus.UNAVAILABLE
                elif self._is_open(wallet):
                    self.status = SecretsStatus.OK
                else:
                    self.status = SecretsStatus.LOCKED
            except SecretTimeout:
                self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
                return self.status
            except Exception as exc:  # noqa: BLE001
                self.status = SecretsStatus.ERROR
                self.status_detail = f"{type(exc).__name__}: {exc}"
                return self.status

            self.status_detail = ""
            return self.status
        finally:
            self._lock.release()

    def present_ids(self, candidates: Sequence[str]) -> list[str] | None:
        """哪些候选 id 已经在钱包里。**不读密码本身**（`entryList` 只列名字）。"""
        if not self._try_lock():
            return None
        try:
            handle = self._handle_for_rw()
            if handle is None:
                return None  # 锁着 → 问不到，不能当成"没有"
            names = self._call("entryList", "iss", handle, _FOLDER, C.APP_ID) or []
            known = set(names)
            return [screen_id for screen_id in candidates if screen_id in known]
        except Exception:  # noqa: BLE001 - 探测失败一律当"问不到"
            return None
        finally:
            self._lock.release()

    # --- 读写 ---------------------------------------------------------------
    def get(self, screen_id: str) -> str | None:
        if not self._try_lock():
            return None
        try:
            handle = self._handle_for_rw()
            if handle is None:
                return None
            # KWallet 的约定：读不到（没有这条/钱包关了）返回空串，不报错
            value = self._call("readPassword", "isss", handle, _FOLDER, screen_id,
                               C.APP_ID)
            return value or None
        except SecretTimeout:
            self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
            return None
        except Exception as exc:  # noqa: BLE001
            self.status_detail = f"{type(exc).__name__}: {exc}"
            return None
        finally:
            self._lock.release()

    def set(self, screen_id: str, password: str) -> bool:
        if not self._try_lock():
            return False
        try:
            handle = self._handle_for_rw()
            if handle is None:
                return False
            result = self._call("writePassword", "issss", handle, _FOLDER, screen_id,
                                password, C.APP_ID)
            # 0 = 成功，负数 = 失败（KWallet 的约定）
            return result == 0
        except SecretTimeout:
            self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
            return False
        except Exception as exc:  # noqa: BLE001
            self.status_detail = f"{type(exc).__name__}: {exc}"
            return False
        finally:
            self._lock.release()

    def delete(self, screen_id: str) -> None:
        if not self._try_lock():
            return
        try:
            handle = self._handle_for_rw()
            if handle is not None:
                self._call("removeEntry", "isss", handle, _FOLDER, screen_id, C.APP_ID)
        except Exception:  # noqa: BLE001 - 删除失败不值得打断用户
            pass
        finally:
            self._lock.release()

    def last_modified(self) -> float | None:
        """KDE 钱包**不提供条目时间戳**（实测 `entriesList` 只回类型元数据）。"""
        return None

    def wipe(self, ids: Sequence[str]) -> tuple[int, list[str]]:
        """删掉给定的 id。**只删这些** —— 钱包里还有用户别的东西。"""
        if not self._try_lock():
            return 0, [tr("store is busy")]
        deleted, errors = 0, []
        try:
            handle = self._handle_for_rw()
            if handle is None:
                return 0, [tr("store is locked")]
            for screen_id in ids:
                try:
                    if self._call("removeEntry", "isss", handle, _FOLDER, screen_id,
                                  C.APP_ID) == 0:
                        deleted += 1
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{screen_id}: {type(exc).__name__}: {exc}")
        finally:
            self._lock.release()
        return deleted, errors

    # --- 解锁 ---------------------------------------------------------------
    def try_unlock(self) -> bool:
        """打开钱包 —— 这一步会弹 KDE 自己的钱包密码框。调用方必须放后台线程。"""
        if not self._try_lock():
            return False
        try:
            handle = self._open(allow_prompt=True)
            if handle is None:
                return False
            self.status, self.status_detail = SecretsStatus.OK, ""
            return True
        except Exception:  # noqa: BLE001 - 超时/报错都算没解锁
            return False
        finally:
            self._lock.release()

    def unlock_with_secret(self, secret: str) -> UnlockResult:
        # KDE 钱包的解锁由系统提示框负责，不需要我们收任何秘密
        return UnlockResult.ERROR

    def close(self) -> None:
        self._handle = None
