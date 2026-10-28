"""freedesktop Secret Service 后端（`org.freedesktop.secrets`，走 secretstorage）。

它原来只用在"把旧版本的密码搬进 KDE 钱包"那一次迁移里；现在提升成一等后端：
在非 KDE 的桌面（或者用户就想用系统密钥环）时它是个正经选择。

属性固定用 `{"service": APP_ID, "username": screen_id}` —— **绝不能改**：
老版本（以及 `keyring` 库）写下的条目就是这个形状，改了老数据就再也找不到了。

和 KWallet 后端一样的规矩：探测只走不会弹框的调用（`check_service_availability` /
`is_locked` / `SearchItems`），只有 `unlock()` 会弹系统的解锁框，且只能由后台线程调；
secretstorage 的连接不是线程安全的，所有调用串行化在一把锁后面。
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


class SecretServiceBackend(Backend):
    key = "secretservice"
    unlock_kind = UnlockKind.SYSTEM_PROMPT

    def __init__(self, timeout: float) -> None:
        super().__init__(timeout)
        self._conn = None

    # --- 底层 ---------------------------------------------------------------
    def _connect(self):
        if self._conn is None:
            import secretstorage

            self._conn = secretstorage.dbus_init()
        return self._conn

    def _collection(self):
        """默认集合。没有就返回 None。调用方已持有锁。"""
        import secretstorage

        conn = self._connect()
        if not secretstorage.check_service_availability(conn):
            return None
        return secretstorage.get_default_collection(conn)

    def _items(self, screen_id: str | None = None) -> list:
        """本程序的条目。给定 screen_id 时只查这一条。调用方已持有锁。"""
        import secretstorage

        attributes = {"service": C.APP_ID}
        if screen_id is not None:
            attributes["username"] = screen_id
        return list(secretstorage.search_items(self._connect(), attributes))

    def _guarded(self, func, *args, **kwargs):
        """带超时地跑一段 secretstorage 操作。"""
        return call_with_timeout(lambda: func(*args, **kwargs), self.timeout)

    # --- 探测 ---------------------------------------------------------------
    def probe(self) -> SecretsStatus:
        if not self._try_lock():
            return self.status
        try:
            try:
                collection = self._guarded(self._collection)
            except SecretTimeout:
                self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
                return self.status
            except Exception as exc:  # noqa: BLE001
                self.status = SecretsStatus.NO_SERVICE
                self.status_detail = f"{type(exc).__name__}: {exc}"
                return self.status

            if collection is None:
                self.status, self.status_detail = SecretsStatus.NO_SERVICE, ""
                return self.status

            try:
                locked = self._guarded(collection.is_locked)
            except SecretTimeout:
                self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
                return self.status
            except Exception as exc:  # noqa: BLE001
                self.status = SecretsStatus.ERROR
                self.status_detail = f"{type(exc).__name__}: {exc}"
                return self.status

            self.status = SecretsStatus.LOCKED if locked else SecretsStatus.OK
            self.status_detail = ""
            return self.status
        finally:
            self._lock.release()

    def present_ids(self, candidates: Sequence[str]) -> list[str] | None:
        if not self._try_lock():
            return None
        try:
            try:
                items = self._guarded(self._items)
            except Exception:  # noqa: BLE001 - 失败/超时都当"问不到"
                return None
            known = set()
            for item in items:
                username = item.get_attributes().get("username")
                if username:
                    known.add(username)
            return [screen_id for screen_id in candidates if screen_id in known]
        finally:
            self._lock.release()

    # --- 读写 ---------------------------------------------------------------
    def get(self, screen_id: str) -> str | None:
        if not self._try_lock():
            return None
        try:
            try:
                items = self._guarded(self._items, screen_id)
                if not items:
                    return None
                secret = self._guarded(items[0].get_secret)
            except SecretTimeout:
                self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
                return None
            except Exception as exc:  # noqa: BLE001
                self.status_detail = f"{type(exc).__name__}: {exc}"
                return None
            if not secret:
                return None
            return secret.decode("utf-8", "replace")
        finally:
            self._lock.release()

    def set(self, screen_id: str, password: str) -> bool:
        if not self._try_lock():
            return False
        try:
            try:
                collection = self._guarded(self._collection)
                if collection is None or collection.is_locked():
                    return False
                self._guarded(
                    collection.create_item,
                    f"{C.APP_ID}: {screen_id}",
                    {"service": C.APP_ID, "username": screen_id},
                    password.encode("utf-8"),
                    replace=True,
                )
            except SecretTimeout:
                self.status, self.status_detail = SecretsStatus.TIMEOUT, ""
                return False
            except Exception as exc:  # noqa: BLE001
                self.status_detail = f"{type(exc).__name__}: {exc}"
                return False
            return True
        finally:
            self._lock.release()

    def delete(self, screen_id: str) -> None:
        if not self._try_lock():
            return
        try:
            for item in self._guarded(self._items, screen_id):
                item.delete()
        except Exception:  # noqa: BLE001 - 删除失败不值得打断用户
            pass
        finally:
            self._lock.release()

    def last_modified(self) -> float | None:
        """本程序条目里最新的修改时间。条目本身带 created/modified 时间戳。"""
        if not self._try_lock():
            return None
        try:
            stamps = []
            for item in self._guarded(self._items):
                try:
                    stamps.append(float(item.get_modified()))
                except Exception:  # noqa: BLE001 - 单条读不到就算了
                    continue
            return max(stamps) if stamps else None
        except Exception:  # noqa: BLE001
            return None
        finally:
            self._lock.release()

    def wipe(self, ids: Sequence[str]) -> tuple[int, list[str]]:
        """删掉给定的 id（**只删本程序的这些条目**）。"""
        if not self._try_lock():
            return 0, [tr("store is busy")]
        deleted, errors = 0, []
        try:
            for screen_id in ids:
                try:
                    items = self._guarded(self._items, screen_id)
                    for item in items:
                        item.delete()
                    deleted += 1 if items else 0
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{screen_id}: {type(exc).__name__}: {exc}")
        finally:
            self._lock.release()
        return deleted, errors

    # --- 解锁 ---------------------------------------------------------------
    def try_unlock(self) -> bool:
        """解锁默认集合 —— 可能弹系统提示框。调用方必须放后台线程。"""
        if not self._try_lock():
            return False
        try:
            try:
                collection = self._guarded(self._collection)
                if collection is None:
                    return False
                if collection.is_locked():
                    self._guarded(collection.unlock)
            except Exception:  # noqa: BLE001 - 超时/拒绝都算没解锁
                return False
            self.status, self.status_detail = SecretsStatus.OK, ""
            return True
        finally:
            self._lock.release()

    def unlock_with_secret(self, secret: str) -> UnlockResult:
        # 解锁由系统 prompter 负责，不收应用级秘密
        return UnlockResult.ERROR

    def close(self) -> None:
        self._conn = None
