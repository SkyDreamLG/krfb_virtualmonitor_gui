"""内置加密密码库：SQLite + scrypt + Fernet，主密码由用户设定。

系统里没有任何可用的密码库、或者用户就是想用自己的库时用它。

**加密设计**

  * 主密码过 `hashlib.scrypt`（n=2^16, r=8, p=1，64MB 工作集，本机实测 ~115ms）
    派生 64 字节：前 32 字节做 Fernet 密钥，后 32 字节做校验值的 HMAC 密钥。
  * **两半必须分开**：校验值如果能从加密密钥推出来，拿到库文件的人就能离线逐个
    试密码，而不必先过 scrypt。
  * 每个条目加密的是 `screen_id + \\x1f + 密码`，所以把 A 行的密文抄到 B 行会被
    识破（明文里带着自己的 id）。
  * `screen_id` 本身留明文：它本来就在 screens.json 里以明文存在，而且这是
    "锁着也能回答有没有数据"的前提（否则探测就得先解密）。
  * `maxmem` **必须显式传**：Python 默认 0 → OpenSSL 的 32MB 上限，n≥2^15 直接
    `ValueError`。参数全部存进 `meta` 表 —— 参数变了老库就再也解不开了。

**诚实的边界**（文案里也这么写）：加密保护的是"文件落到别人手里"这种情况；
挡不住已经控制了你会话的人。忘记主密码 = 数据不可恢复，重置就是删库。

**留神**：`sqlite3.connect()` 会**创建**文件，所以只有确认文件存在时才连接；
创建用 `os.open(..., O_CREAT|O_EXCL, 0o600)` 先占位，不能指望 umask。
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import sqlite3
import time
from typing import Sequence

from .. import constants as C
from ..i18n import tr
from .base import (
    Backend,
    SecretsStatus,
    UnlockKind,
    UnlockResult,
)

VAULT_VERSION = 1

# KDF 参数。存进 meta 表；改了参数只影响新建的库，老库照旧。
KDF_DEFAULTS = {
    "kdf": "scrypt",
    "kdf_n": 2 ** 16,
    "kdf_r": 8,
    "kdf_p": 1,
    "kdf_dklen": 64,
    "kdf_maxmem": 128 * 1024 * 1024,
}

# 校验值的 HMAC 上下文串（域分离，别拿它当别的用途）
_VERIFY_CONTEXT = b"krfb-virtualmonitor-gui/vault/v1"
_SEPARATOR = b"\x1f"     # 明文里 id 和密码之间的分隔符（ASCII 的 US，密码里不会出现）


def _derive(secret: str, salt: bytes, params: dict) -> bytearray:
    """主密码 → 64 字节密钥材料。慢是故意的（这就是它防爆破的方式）。"""
    raw = hashlib.scrypt(
        secret.encode("utf-8"),
        salt=salt,
        n=int(params["kdf_n"]),
        r=int(params["kdf_r"]),
        p=int(params["kdf_p"]),
        dklen=int(params["kdf_dklen"]),
        maxmem=int(params["kdf_maxmem"]),   # 不显式传会在 n≥2^15 时直接报错
    )
    # scrypt 返回的 bytes 是临时对象、零不掉，这里只能把拷贝擦掉；如实说明，
    # 不假装能擦干净（主密码本身也是不可变 str，同理）。
    return bytearray(raw)


def _fernet_key(dk: bytearray) -> bytes:
    return base64.urlsafe_b64encode(bytes(dk[:32]))


def _verifier(dk: bytearray) -> bytes:
    return hmac.new(bytes(dk[32:]), _VERIFY_CONTEXT, hashlib.sha256).digest()


class BuiltinVaultBackend(Backend):
    key = "builtin"
    unlock_kind = UnlockKind.APP_SECRET

    def __init__(self, timeout: float) -> None:
        super().__init__(timeout)
        self._conn: sqlite3.Connection | None = None
        self._fernet = None      # 解锁后才有的加密器，同时也代表"已解锁"
        self._params: dict = {}

    # --- 路径与连接 ---------------------------------------------------------
    @staticmethod
    def _path():
        # 调用时取属性：测试要能改 C.VAULT_FILE
        return C.VAULT_FILE

    def _connect(self) -> sqlite3.Connection:
        """打开库。**文件必须已存在** —— connect() 会凭空建文件，不能拿它探测。"""
        if self._conn is None:
            path = self._path()
            if not path.exists():
                raise FileNotFoundError(str(path))
            self._conn = sqlite3.connect(str(path), check_same_thread=False)
            self._conn.execute("PRAGMA secure_delete = ON")
            # 老文件可能权限偏宽（比如被别的东西创建过），顺手收紧
            try:
                if (path.stat().st_mode & 0o777) != 0o600:
                    os.chmod(path, 0o600)
            except OSError:
                pass
        return self._conn

    def _sidecars(self) -> list:
        path = self._path()
        return [path.with_name(path.name + suffix)
                for suffix in ("-journal", "-wal", "-shm")]

    # --- 元数据 -------------------------------------------------------------
    def _read_meta(self) -> dict:
        rows = self._connect().execute("SELECT key, value FROM meta").fetchall()
        return {str(k): str(v) for k, v in rows}

    def _read_params(self) -> dict:
        meta = self._read_meta()
        params = dict(KDF_DEFAULTS)
        for key in KDF_DEFAULTS:
            if key in meta:
                params[key] = int(meta[key]) if key != "kdf" else meta[key]
        return params

    # --- 探测（不弹框、不算 KDF）-------------------------------------------
    def probe(self) -> SecretsStatus:
        if not self._try_lock():
            return self.status
        try:
            if self._fernet is not None:
                self.status, self.status_detail = SecretsStatus.OK, ""
                return self.status

            path = self._path()
            if not path.exists():
                self.status, self.status_detail = SecretsStatus.NO_VAULT, ""
                return self.status

            try:
                version = self._connect().execute("PRAGMA user_version").fetchone()[0]
                meta = self._read_meta()
                if version != VAULT_VERSION:
                    self.status = SecretsStatus.UNAVAILABLE
                    self.status_detail = f"unsupported vault version: {version}"
                elif not meta.get("verifier") or not meta.get("salt"):
                    self.status = SecretsStatus.UNAVAILABLE
                    self.status_detail = "vault metadata is incomplete"
                else:
                    self._params = self._read_params()
                    self.status, self.status_detail = SecretsStatus.NEEDS_PASSWORD, ""
            except sqlite3.Error as exc:
                self.status = SecretsStatus.UNAVAILABLE
                self.status_detail = f"{type(exc).__name__}: {exc}"
            return self.status
        finally:
            self._lock.release()

    def present_ids(self, candidates: Sequence[str]) -> list[str] | None:
        """哪些候选 id 在库里。**锁着也能查**（id 是明文）—— 这正是把 id 留明文的原因。"""
        if not self._try_lock():
            return None
        try:
            if not self._path().exists():
                return []
            try:
                known = {row[0] for row in
                         self._connect().execute("SELECT screen_id FROM entries")}
            except sqlite3.Error:
                return None
            return [screen_id for screen_id in candidates if screen_id in known]
        finally:
            self._lock.release()

    def last_modified(self) -> float | None:
        if not self._try_lock():
            return None
        try:
            if not self._path().exists():
                return None
            row = self._connect().execute("SELECT MAX(updated) FROM entries").fetchone()
            return float(row[0]) if row and row[0] is not None else None
        except sqlite3.Error:
            return None
        finally:
            self._lock.release()

    # --- 读写（都必须已解锁）------------------------------------------------
    def _decrypt(self, token: bytes, expected_id: str) -> str | None:
        """解密一条。密文被改过/串过行 → 返回 None，绝不抛给调用方。

        明文里带着自己的 screen_id：**必须和行上的 id 对上**，否则说明有人把
        另一行的密文抄了过来（两行都用同一把密钥，光靠 Fernet 的 MAC 拦不住）。
        """
        from cryptography.fernet import InvalidToken

        if self._fernet is None:
            return None
        try:
            plain = self._fernet.decrypt(bytes(token))
        except (InvalidToken, TypeError, ValueError):
            return None
        embedded_id, separator, password = plain.partition(_SEPARATOR)
        if not separator or embedded_id.decode("utf-8", "replace") != expected_id:
            self.status_detail = "ciphertext does not belong to this entry"
            return None
        return password.decode("utf-8", "replace")

    def get(self, screen_id: str) -> str | None:
        if self._fernet is None or not self._try_lock():
            return None
        try:
            row = self._connect().execute(
                "SELECT token FROM entries WHERE screen_id = ?", (screen_id,)
            ).fetchone()
            if row is None:
                return None
            value = self._decrypt(row[0], screen_id)
            if value is None:
                self.status_detail = "ciphertext failed to decrypt (tampered?)"
            return value
        except sqlite3.Error as exc:
            self.status_detail = f"{type(exc).__name__}: {exc}"
            return None
        finally:
            self._lock.release()

    def set(self, screen_id: str, password: str) -> bool:
        if self._fernet is None or not self._try_lock():
            return False
        try:
            plain = screen_id.encode("utf-8") + _SEPARATOR + password.encode("utf-8")
            token = self._fernet.encrypt(plain)
            conn = self._connect()
            conn.execute(
                "INSERT INTO entries(screen_id, token, updated) VALUES(?, ?, ?) "
                "ON CONFLICT(screen_id) DO UPDATE SET token = excluded.token, "
                "updated = excluded.updated",
                (screen_id, token, time.time()),
            )
            conn.commit()
            return True
        except Exception as exc:  # noqa: BLE001 - 任何写失败都如实返回 False
            self.status_detail = f"{type(exc).__name__}: {exc}"
            return False
        finally:
            self._lock.release()

    def delete(self, screen_id: str) -> None:
        if not self._try_lock():
            return
        try:
            self._connect().execute("DELETE FROM entries WHERE screen_id = ?",
                                    (screen_id,))
            self._connect().commit()
        except sqlite3.Error:
            pass
        finally:
            self._lock.release()

    def wipe(self, ids: Sequence[str]) -> tuple[int, list[str]]:
        """删掉给定的 id（**只删这些**）。需要先解锁 —— 锁着时如实报错。"""
        if self._fernet is None:
            return 0, [tr("store is locked")]
        if not self._try_lock():
            return 0, [tr("store is busy")]
        deleted, errors = 0, []
        try:
            conn = self._connect()
            for screen_id in ids:
                try:
                    cursor = conn.execute("DELETE FROM entries WHERE screen_id = ?",
                                          (screen_id,))
                    deleted += cursor.rowcount if cursor.rowcount > 0 else 0
                except sqlite3.Error as exc:
                    errors.append(f"{screen_id}: {type(exc).__name__}: {exc}")
            conn.commit()
        finally:
            self._lock.release()
        return deleted, errors

    # --- 解锁 / 建库 / 重置 --------------------------------------------------
    def _unlock_locked(self, secret: str) -> UnlockResult:
        """解密验证主密码并缓存加密器。调用方必须已持有锁。"""
        from cryptography.fernet import Fernet

        try:
            meta = self._read_meta()
            params = self._read_params()
            salt = base64.b64decode(meta["salt"])
            expected = base64.b64decode(meta["verifier"])
        except Exception:  # noqa: BLE001
            return UnlockResult.ERROR

        dk = _derive(secret, salt, params)
        try:
            if not hmac.compare_digest(_verifier(dk), expected):
                return UnlockResult.WRONG_PASSWORD
            self._fernet = Fernet(_fernet_key(dk))
        finally:
            dk[:] = b"\x00" * len(dk)
        self._params = params
        self.status, self.status_detail = SecretsStatus.OK, ""
        return UnlockResult.OK

    def unlock_with_secret(self, secret: str) -> UnlockResult:
        """用主密码解锁。**会跑 100–300ms 的 KDF，调用方必须放后台线程。**"""
        if not secret:
            return UnlockResult.ERROR
        with self._lock:      # 阻塞抢锁：本来就要几百毫秒，没必要装快
            if not self._path().exists():
                return UnlockResult.ERROR
            return self._unlock_locked(secret)

    def create(self, secret: str) -> tuple[bool, str]:
        """建库并设主密码。库已存在时失败（不覆盖任何东西）。"""
        path = self._path()
        with self._lock:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
                os.close(fd)
            except FileExistsError:
                return False, tr("a vault already exists")
            except OSError as exc:
                return False, f"{type(exc).__name__}: {exc}"

            try:
                conn = sqlite3.connect(str(path), check_same_thread=False)
                conn.execute("PRAGMA secure_delete = ON")
                conn.execute("PRAGMA user_version = %d" % VAULT_VERSION)
                conn.execute("CREATE TABLE meta(key TEXT PRIMARY KEY, "
                             "value TEXT NOT NULL) WITHOUT ROWID")
                conn.execute("CREATE TABLE entries(screen_id TEXT PRIMARY KEY, "
                             "token BLOB NOT NULL, updated REAL NOT NULL) WITHOUT ROWID")
                salt = os.urandom(16)
                params = dict(KDF_DEFAULTS)
                dk = _derive(secret, salt, params)
                try:
                    meta_rows = {key: str(value) for key, value in params.items()}
                    meta_rows["salt"] = base64.b64encode(salt).decode("ascii")
                    meta_rows["verifier"] = base64.b64encode(_verifier(dk)).decode("ascii")
                    meta_rows["created"] = str(time.time())
                finally:
                    dk[:] = b"\x00" * len(dk)
                conn.executemany("INSERT INTO meta(key, value) VALUES(?, ?)",
                                 list(meta_rows.items()))
                conn.commit()
                self._conn = conn
            except Exception as exc:  # noqa: BLE001 - 建库失败不能留下半个文件
                self._conn = None
                self._remove_files()
                return False, f"{type(exc).__name__}: {exc}"

            result = self._unlock_locked(secret)
            if result is not UnlockResult.OK:
                self._conn = None
                self._remove_files()
                return False, tr("could not unlock the newly created vault")
            return True, ""

    def reset(self) -> None:
        """删库。**数据不可恢复** —— 调用方必须已经过反复确认/验证码。"""
        with self._lock:
            self._fernet = None
            self._conn = None
            self._remove_files()
            self.status, self.status_detail = SecretsStatus.NO_VAULT, ""

    def change_secret(self, old: str, new: str) -> tuple[bool, str]:
        """改主密码：先验旧的，再换盐、校验值，并**把所有条目重新加密**。"""
        with self._lock:
            if not self._path().exists():
                return False, tr("there is no vault")
            if self._unlock_locked(old) is not UnlockResult.OK:
                return False, tr("wrong master password")
            try:
                rows = self._connect().execute(
                    "SELECT screen_id, token FROM entries").fetchall()
            except sqlite3.Error as exc:
                return False, f"{type(exc).__name__}: {exc}"
            plain = []
            for screen_id, token in rows:
                password = self._decrypt(token, screen_id)
                if password is None:
                    # 解不开的条目说明密文被改过/库损坏 —— 这时候换密码会把这条
                    # 永久锁死，所以宁可整个操作失败，什么都不改。
                    return False, tr("some entries could not be decrypted; "
                                     "nothing was changed")
                plain.append((screen_id, password))

            from cryptography.fernet import Fernet

            salt = os.urandom(16)
            params = dict(KDF_DEFAULTS)
            dk = _derive(new, salt, params)
            try:
                meta_rows = {key: str(value) for key, value in params.items()}
                meta_rows["salt"] = base64.b64encode(salt).decode("ascii")
                meta_rows["verifier"] = base64.b64encode(_verifier(dk)).decode("ascii")
                meta_rows["created"] = str(time.time())
                new_fernet = Fernet(_fernet_key(dk))
            finally:
                dk[:] = b"\x00" * len(dk)

            try:
                conn = self._connect()
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("DELETE FROM meta")
                conn.executemany("INSERT INTO meta(key, value) VALUES(?, ?)",
                                 list(meta_rows.items()))
                for screen_id, password in plain:
                    token = new_fernet.encrypt(
                        screen_id.encode("utf-8") + _SEPARATOR + password.encode("utf-8"))
                    conn.execute("UPDATE entries SET token = ?, updated = ? "
                                 "WHERE screen_id = ?", (token, time.time(), screen_id))
                conn.commit()
            except sqlite3.Error as exc:
                self._conn.rollback()
                return False, f"{type(exc).__name__}: {exc}"

            self._fernet = new_fernet
            self.status, self.status_detail = SecretsStatus.OK, ""
            return True, ""

    def _remove_files(self) -> None:
        for path in [self._path(), *self._sidecars()]:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    def close(self) -> None:
        self._fernet = None
        if self._conn is not None:
            try:
                self._conn.close()
            except sqlite3.Error:
                pass
            self._conn = None

    def try_unlock(self) -> bool:
        # 内置库没有系统提示框可调；解锁要主密码，走 unlock_with_secret
        return self._fernet is not None
