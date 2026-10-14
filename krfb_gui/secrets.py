"""密码存储：KDE 钱包（KWallet）原生 D-Bus 接口 + 绝不阻塞的降级路径。

**为什么不用 freedesktop Secret Service**：krfb 的虚拟显示器只能在 KDE/KWin
上用，目标环境必然是 KDE；而 `org.freedesktop.secrets` 这个名字是**先到先得**
的 —— 只要系统里装了别的实现（gnome-keyring 等）并先占了总线名，密码就会
写进那个后端，和用户期望的"存进 KDE 钱包"完全对不上（本机实测就是如此：
`secrets` 归 gnome-keyring-daemon，用户去锁 kdewallet 毫无影响）。
`org.kde.KWallet` 才是 KDE 自己的钱包接口，只要钱包子系统开着就能用，
不受"谁抢到 Secret Service 总线名"以及"kwallet 的 secret service 接口是否
被关掉"这类配置差异影响。

顺带的好处：KWallet 的 `open()` 就是 KDE 官方的解锁入口，弹的是系统自己的
钱包密码框，不再依赖 secretstorage 那条可能永远不返回的路径。

踩过的坑（对策保持不变）：

  1. `open()` 会弹钱包密码框，而 D-Bus 调用**没有任何超时** —— 如果提示框
     弹不出来（无显示环境、从 systemd unit 启动、prompter 异常），调用**永远
     不返回**。
  2. 因此所有调用丢进 **daemon 线程**并带超时。用 `threading.Thread` 而不是
     `ThreadPoolExecutor` —— 后者会在解释器退出时 join 工作线程，被阻塞的线程
     会把整个程序拖住不退出，正好是我们要避免的失败模式。
  3. 锁定时不硬等，降级为"仅本次会话内存"，并在界面明确标注。
  4. 启动路径**永远不依赖**钱包成功。

另有一次性的旧数据迁移：早期版本把密码存在 freedesktop Secret Service 里
（见 `_read_legacy`），钱包里找不到时会顺手搬过来，只读不删。
"""

from __future__ import annotations

import secrets as _secrets
import threading
from enum import Enum

from . import constants as C
from .i18n import tr

# KWallet 的 D-Bus 坐标。kwalletd6 → kwalletd5 → 老 kwalletd，取第一个能用的。
_KWALLETD_CANDIDATES = (
    ("org.kde.kwalletd6", "/modules/kwalletd6"),
    ("org.kde.kwalletd5", "/modules/kwalletd5"),
    ("org.kde.kwalletd", "/modules/kwalletd"),
)
_WALLET_INTERFACE = "org.kde.KWallet"

# 密码写进标准文件夹「Passwords」：KWallet 的文件夹有类型，`writePassword`
# 写的是 Password 类型条目，只有 "Passwords" 这个预置文件夹的类型一定匹配。
# （自建文件夹会被判成 Unknown 类型，写 Password 条目可能被拒。）
_FOLDER = "Passwords"

# 打开钱包时传给 kwalletd 的窗口 id。0 = 不挂父窗口（本模块刻意不依赖 Qt，
# 拿不到顶层窗口句柄；KDE 会自己把提示框放到合适的位置）。
_WID = 0


class SecretsStatus(Enum):
    OK = "ok"                # 钱包子系统启用、钱包存在且已解锁
    LOCKED = "locked"        # 钱包在，但没解锁（open 会弹提示框，此时绝不能自动调）
    NO_SERVICE = "no_service"  # 会话总线上没有 kwalletd
    UNAVAILABLE = "unavailable"  # 钱包子系统被关掉，或一个钱包都没有
    TIMEOUT = "timeout"      # 调用超时，已降级
    ERROR = "error"

    @property
    def label(self) -> str:
        return tr({
            SecretsStatus.OK: "Keyring ready",
            SecretsStatus.LOCKED: "Keyring locked",
            SecretsStatus.NO_SERVICE: "No keyring service found",
            SecretsStatus.UNAVAILABLE: "Keyring unavailable",
            SecretsStatus.TIMEOUT: "Keyring not responding",
            SecretsStatus.ERROR: "Keyring error",
        }[self])

    @property
    def detail(self) -> str:
        """逐状态的人类可读说明（可翻译）。

        原始异常文本不放这里 —— 那是 `Secrets.status_detail`，语言无关的
        技术信息，不会随语言切换过期。
        """
        return tr({
            SecretsStatus.OK: "",
            SecretsStatus.LOCKED: "The KDE wallet is closed; "
                                   "passwords are kept in memory for this session only",
            SecretsStatus.NO_SERVICE: "kwalletd is not running on the session bus",
            SecretsStatus.UNAVAILABLE: "The KDE wallet subsystem is disabled, "
                                       "or no wallet exists",
            SecretsStatus.TIMEOUT: "The wallet did not respond in time; "
                                   "passwords are kept in memory for this session only",
            SecretsStatus.ERROR: "",
        }[self])

    @property
    def needs_attention(self) -> bool:
        return self is not SecretsStatus.OK


def compose_detail(status: SecretsStatus, raw: str) -> str:
    """界面可用的完整说明：状态解释 + 原始异常文本（如果有）。"""
    return " · ".join(part for part in (status.detail, raw) if part)


class SecretTimeout(Exception):
    """钱包调用超时。阻塞的线程无法取消，只能丢弃。

    消息面向开发者（调用方拿到超时后会丢弃它、改用状态说明），不需要翻译。
    """


def generate_password(length: int = C.VNC_PASSWORD_LEN) -> str:
    """生成随机密码。

    默认只生成 8 位，因为 VNC 的 DES 认证**只使用前 8 个字符** ——
    更长的密码不会增加任何熵，只会让用户误以为自己更安全。
    """
    alphabet = C.PASSWORD_ALPHABET
    return "".join(_secrets.choice(alphabet) for _ in range(length))


def effective_length(password: str) -> int:
    """VNC 实际会用到的字符数（上限 8）。"""
    return min(len(password), C.VNC_PASSWORD_LEN)


def _call_with_timeout(func, timeout: float):
    """在 daemon 线程里执行 func，超时就抛 SecretTimeout。

    刻意不用 ThreadPoolExecutor：它会注册 atexit 钩子 join 工作线程，一旦线程被
    永久阻塞，解释器退出时就会被拖住 —— 正是我们要规避的失败模式。
    """
    box: dict[str, object] = {}
    done = threading.Event()

    def runner() -> None:
        try:
            box["value"] = func()
        except BaseException as exc:  # noqa: BLE001 - 要把异常原样带回调用方
            box["error"] = exc
        finally:
            done.set()

    thread = threading.Thread(target=runner, daemon=True, name="kwallet-call")
    thread.start()
    if not done.wait(timeout):
        raise SecretTimeout(f"kwallet call did not return within {timeout:.1f}s")
    if "error" in box:
        raise box["error"]  # type: ignore[misc]
    return box.get("value")


class Secrets:
    """密码读写门面。内存缓存 + KDE 钱包持久化，两者对调用方透明。"""

    def __init__(self, timeout: float = C.KEYRING_TIMEOUT_MS / 1000) -> None:
        self.timeout = timeout
        self.status = SecretsStatus.UNAVAILABLE
        self.status_detail = ""
        self._memory: dict[str, str] = {}
        self._dirty: set[str] = set()  # 只存在于内存、尚未写进钱包的项

        self._service: tuple[str, str] | None = None  # 选中的 kwalletd，None = 还没探测
        self._conn = None         # jeepney 连接（懒建）
        self._lock = threading.Lock()  # jeepney 的连接不是线程安全的
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

        address = DBusAddress(service[1], bus_name=service[0],
                              interface=_WALLET_INTERFACE)
        reply = self._connect().send_and_get_reply(
            new_method_call(address, method, signature, args)
        )
        body = unwrap_msg(reply)  # 错误回复在这里变成 DBusErrorResponse
        return body[0] if len(body) == 1 else body

    def _call(self, method: str, signature: str = "", *args):
        """带超时 + 串行化的调用；kwalletd6/5/老版依次试，记住第一个能通的。

        jeepney 的连接不是线程安全的，而调用可能来自主线程（轮询刷新）和后台
        线程（解锁），所以用一把锁串起来。
        """
        candidates = list(_KWALLETD_CANDIDATES)
        if self._service in candidates:
            candidates.remove(self._service)
            candidates.insert(0, self._service)

        last_error: Exception | None = None
        for candidate in candidates:
            def invoke(candidate=candidate):
                with self._lock:
                    return self._raw_call(candidate, method, signature, *args)

            try:
                value = _call_with_timeout(invoke, self.timeout)
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
        """读写用的 handle：钱包没开就返回 None（绝不弹框）。"""
        if self._handle is not None and self._is_open(self._wallet):
            return self._handle
        self._handle = None
        return self._open(allow_prompt=False)

    def _read_wallet(self, screen_id: str) -> str | None:
        handle = self._handle_for_rw()
        if handle is None:
            return None
        # KWallet 的约定：读不到（没有这条/钱包关了）返回空串，不报错
        value = self._call("readPassword", "isss", handle, _FOLDER, screen_id, C.APP_ID)
        return value or None

    def _write_wallet(self, screen_id: str, password: str) -> bool:
        handle = self._handle_for_rw()
        if handle is None:
            return False
        result = self._call("writePassword", "issss", handle, _FOLDER, screen_id,
                            password, C.APP_ID)
        # 0 = 成功，负数 = 失败（KWallet 的约定）
        return result == 0

    def _delete_wallet(self, screen_id: str) -> None:
        handle = self._handle_for_rw()
        if handle is None:
            return
        self._call("removeEntry", "isss", handle, _FOLDER, screen_id, C.APP_ID)

    # --- 后端探测 -----------------------------------------------------------
    def probe(self) -> SecretsStatus:
        """探测可用性与锁定状态。**只用不会弹框的调用**，保证不会挂。

        钱包可能被用户随时锁上，所以每次探测都丢掉缓存的 handle。
        """
        self._handle = None
        try:
            enabled = self._call("isEnabled")
        except SecretTimeout:
            self.status = SecretsStatus.TIMEOUT
            self.status_detail = ""
            return self.status
        except Exception as exc:  # noqa: BLE001 - 连不上 kwalletd 都归到这里
            self.status = SecretsStatus.NO_SERVICE
            self.status_detail = f"{type(exc).__name__}: {exc}"
            return self.status

        if not enabled:
            # 用户在系统设置里关掉了钱包子系统（kwalletrc 的 Enabled=false）
            self.status = SecretsStatus.UNAVAILABLE
            self.status_detail = ""
            return self.status

        try:
            wallet = self._wallet_name()
            if not wallet:
                self.status = SecretsStatus.UNAVAILABLE
                self.status_detail = ""
            elif self._is_open(wallet):
                self.status = SecretsStatus.OK
            else:
                self.status = SecretsStatus.LOCKED
        except SecretTimeout:
            self.status = SecretsStatus.TIMEOUT
            self.status_detail = ""
            return self.status
        except Exception as exc:  # noqa: BLE001
            self.status = SecretsStatus.ERROR
            self.status_detail = f"{type(exc).__name__}: {exc}"
            return self.status

        self.status_detail = ""
        return self.status

    @property
    def detail(self) -> str:
        """界面用的完整说明：状态解释 + 原始异常文本。每次访问都重新拼，
        语言切换后不会像缓存在控件里的字符串那样过期。"""
        return compose_detail(self.status, self.status_detail)

    # --- 读写 ---------------------------------------------------------------
    def get(self, screen_id: str) -> str | None:
        """先查内存（快且不会挂），再查钱包。

        钱包没解锁时**不去试** —— 那会弹密码框，而这条路径（轮询、刷新）不该
        有副作用。解锁走启动时的主动申请或设置里的按钮。
        """
        if screen_id in self._memory:
            return self._memory[screen_id]
        if self.status in (SecretsStatus.LOCKED, SecretsStatus.NO_SERVICE,
                           SecretsStatus.UNAVAILABLE):
            return None

        try:
            value = self._read_wallet(screen_id)
        except SecretTimeout:
            self.status = SecretsStatus.TIMEOUT
            self.status_detail = ""
            return None
        except Exception as exc:  # noqa: BLE001
            self.status_detail = f"{type(exc).__name__}: {exc}"
            return None

        if value is None:
            # 钱包里没有 —— 可能只是"升级前存在旧后端里"，顺手搬过来
            value = self._import_legacy(screen_id)

        if value is not None:
            self._memory[screen_id] = value
        return value

    def set(self, screen_id: str, password: str) -> bool:
        """写入密码。内存一定成功；钱包是否写成功由返回值表示。"""
        self._memory[screen_id] = password

        if self.status in (SecretsStatus.LOCKED, SecretsStatus.NO_SERVICE,
                           SecretsStatus.UNAVAILABLE):
            self._dirty.add(screen_id)
            return False

        try:
            written = self._write_wallet(screen_id, password)
        except SecretTimeout:
            self.status = SecretsStatus.TIMEOUT
            self.status_detail = ""
            self._dirty.add(screen_id)
            return False
        except Exception as exc:  # noqa: BLE001
            self.status_detail = f"{type(exc).__name__}: {exc}"
            self._dirty.add(screen_id)
            return False

        if not written:
            self._dirty.add(screen_id)
            return False
        self._dirty.discard(screen_id)
        return True

    def delete(self, screen_id: str) -> None:
        self._memory.pop(screen_id, None)
        self._dirty.discard(screen_id)
        try:
            self._delete_wallet(screen_id)
        except Exception:  # noqa: BLE001 - 删除失败不值得打断用户
            pass

    # --- 仅内存的显式操作 ---------------------------------------------------
    def remember(self, screen_id: str, password: str) -> None:
        self._memory[screen_id] = password

    def recall(self, screen_id: str) -> str | None:
        return self._memory.get(screen_id)

    def forget(self, screen_id: str) -> None:
        self._memory.pop(screen_id, None)

    @property
    def pending_ids(self) -> set[str]:
        """只存在内存、没能写进钱包的屏幕 id（退出后会丢）。"""
        return set(self._dirty)

    # --- 解锁 ---------------------------------------------------------------
    def try_unlock(self) -> bool:
        """打开钱包 —— 这一步会弹 KDE 自己的钱包密码框。会阻塞到用户回应或超时
        （最长 `max(timeout, 30s)`），界面层必须放进后台线程再调
        （见 `MainWindow._request_unlock`）。
        """
        try:
            handle = self._open(allow_prompt=True)
        except Exception:  # noqa: BLE001 - 超时/报错都算没解锁
            return False

        if handle is None:
            return False

        self.status = SecretsStatus.OK
        self.status_detail = ""
        # 把之前只存在内存里的密码补写进钱包
        for screen_id in list(self._dirty):
            password = self._memory.get(screen_id)
            if password is not None:
                self.set(screen_id, password)
        return True

    # --- 旧数据迁移 ---------------------------------------------------------
    def _import_legacy(self, screen_id: str) -> str | None:
        """从旧后端（freedesktop Secret Service）读一次并搬进钱包。

        早期版本用 `keyring` + secretstorage 存密码，本机上落到了
        gnome-keyring 里；换成 KWallet 后那些条目不会再被读到。这里**只读不删**，
        搬完就完事 —— 钱包里有了这条之后，下次不会再走到这里。
        这段可以在几个版本后整体删掉。
        """
        value = _read_legacy(screen_id, self.timeout)
        if value is None:
            return None
        try:
            self._write_wallet(screen_id, value)
        except Exception:  # noqa: BLE001 - 搬不进去也不影响本次使用
            pass
        return value


def _read_legacy(screen_id: str, timeout: float) -> str | None:
    """读旧后端里的一条密码（只读）。secretstorage 没装就直接放弃。"""
    try:
        import secretstorage
    except ImportError:
        return None

    def fetch() -> str | None:
        conn = secretstorage.dbus_init()
        if not secretstorage.check_service_availability(conn):
            return None
        items = list(secretstorage.search_items(
            conn, {"service": C.APP_ID, "username": screen_id}
        ))
        if not items:
            return None
        secret = items[0].get_secret()
        return secret.decode("utf-8", "replace") if secret else None

    try:
        return _call_with_timeout(fetch, timeout)
    except Exception:  # noqa: BLE001 - 旧后端怎样都无所谓
        return None
