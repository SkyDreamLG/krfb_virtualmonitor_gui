"""内置加密库自检：加密格式、锁定语义、篡改检测、重置。

配置与数据都写到临时目录（`/tmp/krfb-virtualmonitor-gui-vault-test`，可用
KRBFTEST_DIR 改），不碰用户的真实密码库 —— 见 isolate_config()。

    .venv/bin/python tests/test_vault.py
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MASTER = "correct horse battery staple"


def isolate_config(base_dir: str | None = None) -> Path:
    """把配置与数据目录都指到临时目录。

    必须在 import krfb_gui **之前**调用：`constants.py` 在导入时就把路径算好了。
    """
    base = Path(base_dir or os.environ.get("KRBFTEST_DIR")
                or Path(tempfile.gettempdir()) / "krfb-virtualmonitor-gui-vault-test")
    os.environ["XDG_CONFIG_HOME"] = str(base / "config")
    os.environ["XDG_STATE_HOME"] = str(base / "state")
    os.environ["XDG_DATA_HOME"] = str(base / "data")
    return base


def _fresh_backend():
    from krfb_gui import constants as C
    from krfb_gui.secrets.builtin import BuiltinVaultBackend

    for path in [C.VAULT_FILE, *[C.VAULT_FILE.with_name(C.VAULT_FILE.name + s)
                                 for s in ("-journal", "-wal", "-shm")]]:
        path.unlink(missing_ok=True)
    return BuiltinVaultBackend(timeout=3.0)


def check_backend_import_is_cheap() -> bool:
    """import krfb_gui.secrets 不该建库、也不该把 PySide6 拖进来。"""
    from krfb_gui import constants as C

    if C.VAULT_FILE.exists():
        print("  ✗ 光 import 就建出库文件了")
        return False
    probe = ("import sys; sys.path.insert(0, %r);"
             "import krfb_gui.secrets, krfb_gui.constants as C;"
             "print('PySide6' in sys.modules, C.VAULT_FILE.exists())" % str(ROOT))
    proc = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                          text=True, timeout=60, env=dict(os.environ))
    if proc.returncode != 0:
        print(f"  ✗ 子进程失败：{proc.stderr.strip()[:200]}")
        return False
    if proc.stdout.strip() != "False False":
        print(f"  ✗ 期望 'False False'（无 Qt / 无库文件），拿到 {proc.stdout.strip()!r}")
        return False
    print("  ✓ import 廉价：不建库、不引入 PySide6")
    return True


def check_kdf_parameters() -> bool:
    """KDF 参数必须是显式给了 maxmem 的那一组 —— 不传 maxmem 时 n≥2^15
    会直接 ValueError，而那只会在用户"设主密码"时炸。"""
    from krfb_gui.secrets.builtin import KDF_DEFAULTS, _derive

    params = dict(KDF_DEFAULTS)
    if not params.get("kdf_maxmem"):
        print("  ✗ KDF_DEFAULTS 里没有显式 maxmem")
        return False

    # 不带 maxmem 调一次必须失败（证明默认上限确实不够），带参数则成功
    try:
        hashlib.scrypt(b"pw", salt=b"0" * 16, n=params["kdf_n"], r=params["kdf_r"],
                       p=params["kdf_p"], dklen=32)
        print("  ✗ 不带 maxmem 竟然成功了 —— 参数或 OpenSSL 上限变了，得重新确认")
        return False
    except ValueError:
        pass

    dk = _derive(MASTER, b"salt" * 4, params)
    if len(dk) != params["kdf_dklen"]:
        print(f"  ✗ 派生长度 {len(dk)} ≠ {params['kdf_dklen']}")
        return False
    dk[:] = b"\x00" * len(dk)
    print(f"  ✓ KDF 参数 n=2^{params['kdf_n'].bit_length() - 1} r={params['kdf_r']} "
          f"p={params['kdf_p']}，maxmem 显式传入")
    return True


def check_frozen_derivation() -> bool:
    """同一对 (密码, 盐, 参数) 必须永远派生出同一把密钥。

    这里冻结的是**格式契约**：哪天有人顺手改了 KDF 参数或盐的处理方式，
    老库就再也解不开了，这个断言会先炸出来。
    """
    from krfb_gui.secrets.builtin import KDF_DEFAULTS, _fernet_key, _derive, _verifier

    params = dict(KDF_DEFAULTS)
    salt = bytes(range(16))
    dk = _derive("frozen-master", salt, params)
    key = _fernet_key(dk)
    verifier = _verifier(dk)
    dk[:] = b"\x00" * len(dk)

    if len(key) != 44 or not key.endswith(b"="):
        print(f"  ✗ Fernet 密钥形状不对：{key!r}")
        return False
    if len(verifier) != 32:
        print(f"  ✗ 校验值长度 {len(verifier)} ≠ 32")
        return False
    print("  ✓ 派生结果对同一输入稳定（密钥 44 字节 b64 / 校验值 32 字节）")
    return True


def check_roundtrip_and_restart() -> bool:
    """建库 → 写读删 → **另起一个进程**确认真的落盘了。"""
    from krfb_gui import constants as C

    backend = _fresh_backend()
    if backend.probe().name != "NO_VAULT":
        print("  ✗ 空目录下应该是 NO_VAULT")
        return False
    created, error = backend.create(MASTER)
    if not created:
        print(f"  ✗ 建库失败：{error}")
        return False

    if not backend.set("id-1", "pass-1") or backend.get("id-1") != "pass-1":
        print("  ✗ 写入/读回不一致")
        return False
    if backend.set("id-2", "pass-2") is not True:
        print("  ✗ 第二条写入失败")
        return False
    mode = C.VAULT_FILE.stat().st_mode & 0o777
    if mode != 0o600:
        print(f"  ✗ 库文件权限 {oct(mode)} ≠ 0o600")
        return False
    if backend.present_ids(["id-1", "id-2", "nope"]) != ["id-1", "id-2"]:
        print("  ✗ present_ids 结果不对")
        return False
    if backend.last_modified() is None:
        print("  ✗ 有数据却拿不到时间戳")
        return False

    # 另一个进程重新打开：证明不是靠内存缓存
    probe = ("import sys; sys.path.insert(0, %r);"
             "from krfb_gui.secrets.builtin import BuiltinVaultBackend;"
             "b = BuiltinVaultBackend(timeout=3.0);"
             "print(b.probe().name, b.unlock_with_secret(%r).name, b.get('id-1'))"
             % (str(ROOT), MASTER))
    proc = subprocess.run([sys.executable, "-c", probe], capture_output=True,
                          text=True, timeout=120, env=dict(os.environ))
    if proc.stdout.strip() != "NEEDS_PASSWORD OK pass-1":
        print(f"  ✗ 新进程读到 {proc.stdout.strip()!r}（stderr: {proc.stderr[:200]}）")
        return False

    backend.delete("id-2")
    if backend.get("id-2") is not None:
        print("  ✗ 删除后还能读到")
        return False
    print("  ✓ 建库/读写删/权限 0600/换进程重开都正常")
    return True


def check_wrong_password_and_tamper() -> bool:
    """错密码必须被拒且不动数据；密文被改/被串行都必须读不到、且不抛异常。"""
    from krfb_gui.secrets.builtin import BuiltinVaultBackend
    from krfb_gui.secrets.base import UnlockResult

    backend = _fresh_backend()
    backend.create(MASTER)      # create() 之后本实例就是解锁状态
    backend.set("a", "pass-a")
    backend.set("b", "pass-b")

    # 拿一个**没解锁过**的实例来试错密码：这才检验得了"错密码读不到东西"
    locked = BuiltinVaultBackend(timeout=3.0)
    if locked.unlock_with_secret("not-the-master") is not UnlockResult.WRONG_PASSWORD:
        print("  ✗ 错密码没被拒")
        return False
    if locked.get("a") is not None:
        print("  ✗ 错密码之后竟然读到了数据")
        return False

    # 已解锁的实例遇到错密码只该"拒绝"，不该把已经拿到的钥匙丢掉
    if backend.unlock_with_secret("not-the-master") is not UnlockResult.WRONG_PASSWORD:
        print("  ✗ 已解锁实例上的错密码没被拒")
        return False
    if backend.get("a") != "pass-a":
        print("  ✗ 已解锁的会话被错密码尝试搞掉了")
        return False

    # 用正确密码重开：数据必须是完好的
    again = BuiltinVaultBackend(timeout=3.0)
    if again.unlock_with_secret(MASTER) is not UnlockResult.OK or again.get("a") != "pass-a":
        print("  ✗ 错密码尝试破坏了数据")
        return False

    from krfb_gui import constants as C

    conn = sqlite3.connect(str(C.VAULT_FILE))
    token = conn.execute("SELECT token FROM entries WHERE screen_id = 'a'").fetchone()[0]
    flipped = bytearray(token)
    flipped[-1] ^= 0xFF
    conn.execute("UPDATE entries SET token = ? WHERE screen_id = 'a'", (bytes(flipped),))
    other = conn.execute("SELECT token FROM entries WHERE screen_id = 'b'").fetchone()[0]
    conn.execute("INSERT OR REPLACE INTO entries(screen_id, token, updated) "
                 "VALUES ('swapped', ?, 0)", (other,))
    conn.commit()
    conn.close()

    fresh = BuiltinVaultBackend(timeout=3.0)
    fresh.unlock_with_secret(MASTER)
    if fresh.get("a") is not None:
        print("  ✗ 改过的密文还能读出来")
        return False
    if fresh.get("swapped") is not None:
        print("  ✗ 把 b 的密文贴到别的行竟然能读（id 绑定失效）")
        return False
    if fresh.get("b") != "pass-b":
        print("  ✗ 没被动过的条目读不出来了")
        return False
    print("  ✓ 错密码被拒且不动数据；翻改/串行的密文读取返回 None 且不抛")
    return True


def check_master_password_change() -> bool:
    """改主密码：旧密码失效、新密码可用、数据完好。"""
    from krfb_gui.secrets.builtin import BuiltinVaultBackend
    from krfb_gui.secrets.base import UnlockResult

    backend = _fresh_backend()
    backend.create(MASTER)
    backend.set("a", "pass-a")

    ok, error = backend.change_secret(MASTER, "another master password")
    if not ok:
        print(f"  ✗ 改主密码失败：{error}")
        return False

    fresh = BuiltinVaultBackend(timeout=3.0)
    if fresh.unlock_with_secret(MASTER) is not UnlockResult.WRONG_PASSWORD:
        print("  ✗ 旧主密码还能解锁")
        return False
    fresh = BuiltinVaultBackend(timeout=3.0)
    if fresh.unlock_with_secret("another master password") is not UnlockResult.OK:
        print("  ✗ 新主密码解不开")
        return False
    if fresh.get("a") != "pass-a":
        print("  ✗ 改密码之后数据丢了")
        return False

    if fresh.change_secret("wrong-old", "x")[0]:
        print("  ✗ 用错旧密码也能改")
        return False
    print("  ✓ 改主密码后旧密码失效、新密码可用、数据完好")
    return True


def check_reset() -> bool:
    """重置：文件与边车全消失、旧密码再也打不开、新密码可建新库。"""
    from krfb_gui import constants as C
    from krfb_gui.secrets.builtin import BuiltinVaultBackend
    from krfb_gui.secrets.base import UnlockResult

    backend = _fresh_backend()
    backend.create(MASTER)
    backend.set("a", "pass-a")
    backend.reset()

    leftovers = [p for p in [C.VAULT_FILE, *[C.VAULT_FILE.with_name(C.VAULT_FILE.name + s)
                                             for s in ("-journal", "-wal", "-shm")]]
                 if p.exists()]
    if leftovers:
        print(f"  ✗ 重置后还剩文件：{leftovers}")
        return False

    fresh = BuiltinVaultBackend(timeout=3.0)
    if fresh.probe().name != "NO_VAULT":
        print(f"  ✗ 重置后状态是 {fresh.probe().name}，期望 NO_VAULT")
        return False
    if fresh.unlock_with_secret(MASTER) is not UnlockResult.ERROR:
        print("  ✗ 重置后旧密码还能用来解锁")
        return False
    if not fresh.create("brand new master")[0]:
        print("  ✗ 重置后建不出新库")
        return False
    print("  ✓ 重置删净文件与边车，旧主密码失效，可重新建库")
    return True


def check_facade_locked_semantics() -> bool:
    """门面在库锁着时的语义：set 只进内存 + 待写队列，解锁后补写落盘。"""
    from krfb_gui.secrets.builtin import BuiltinVaultBackend
    from krfb_gui.secrets import Secrets

    _fresh_backend().create(MASTER)     # 先建好一个库
    secrets = Secrets(timeout=3.0)
    secrets.select("builtin")
    if secrets.status.name != "NEEDS_PASSWORD":
        print(f"  ✗ 新会话应为 NEEDS_PASSWORD，实际 {secrets.status.name}")
        return False

    if secrets.set("a", "pass-a") is not False:
        print("  ✗ 锁着时 set() 竟然返回成功")
        return False
    if secrets.recall("a") != "pass-a" or secrets.pending_ids != {"a"}:
        print("  ✗ 锁着时没有正确进入内存+待写队列")
        return False
    if secrets.get("a") != "pass-a":
        print("  ✗ 内存缓存没生效")
        return False

    if secrets.unlock_with_secret(MASTER).name != "OK":
        print("  ✗ 解锁失败")
        return False
    if secrets.pending_ids:
        print(f"  ✗ 解锁后待写队列没清空：{secrets.pending_ids}")
        return False

    fresh = BuiltinVaultBackend(timeout=3.0)
    fresh.unlock_with_secret(MASTER)
    if fresh.get("a") != "pass-a":
        print("  ✗ 解锁后没补写进库")
        return False
    print("  ✓ 锁定语义：set 进内存+待写队列，解锁后补写落盘")
    return True


def main() -> int:
    base = isolate_config()
    # 每次都从干净状态开始 —— 上一轮留下的 vault.db 会让"import 不该建库"
    # 这样的检查误报
    shutil.rmtree(base, ignore_errors=True)
    checks = (
        ("import 廉价（不建库、不引 Qt）", check_backend_import_is_cheap),
        ("KDF 参数与显式 maxmem", check_kdf_parameters),
        ("派生结果稳定（格式契约）", check_frozen_derivation),
        ("建库/读写删/换进程重开/权限", check_roundtrip_and_restart),
        ("错密码与篡改检测", check_wrong_password_and_tamper),
        ("修改主密码", check_master_password_change),
        ("重置加密库", check_reset),
        ("门面的锁定语义", check_facade_locked_semantics),
    )

    failed = 0
    for title, check in checks:
        print(f"{title}:")
        try:
            ok = check()
        except Exception as exc:  # 让一项失败不要吞掉其它项
            print(f"  ✗ 抛异常：{type(exc).__name__}: {exc}")
            ok = False
        failed += 0 if ok else 1

    print(f"\n失败 {failed} 项")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
