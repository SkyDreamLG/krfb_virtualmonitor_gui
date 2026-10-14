"""多后端逻辑自检：选择规则、迁移、清除范围。

不碰任何真实密码库（除了内置库那个用临时目录建的一次）。
配置与数据写到 `/tmp/krfb-virtualmonitor-gui-backend-test`，可用 KRBFTEST_DIR 改。

    .venv/bin/python tests/test_backends.py
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def isolate_config(base_dir: str | None = None) -> Path:
    base = Path(base_dir or os.environ.get("KRBFTEST_DIR")
                or Path(tempfile.gettempdir()) / "krfb-virtualmonitor-gui-backend-test")
    os.environ["XDG_CONFIG_HOME"] = str(base / "config")
    os.environ["XDG_STATE_HOME"] = str(base / "state")
    os.environ["XDG_DATA_HOME"] = str(base / "data")
    return base


class FakeBackend:
    """内存里的假后端，用来驱动迁移逻辑（协议与真后端一致）。"""

    key = "fake"

    def __init__(self, entries: dict | None = None, *, fail_write: set | None = None,
                 lie_on_write: set | None = None) -> None:
        self.entries = dict(entries or {})
        self.fail_write = fail_write or set()      # 这些 id 写入返回 False
        self.lie_on_write = lie_on_write or set()  # 这些 id 写入"成功"但没落盘
        self.wipe_calls: list[list[str]] = []

    def get(self, screen_id: str):
        return self.entries.get(screen_id)

    def set(self, screen_id: str, password: str) -> bool:
        if screen_id in self.fail_write:
            return False
        if screen_id in self.lie_on_write:
            return True          # 声称成功，其实没写 —— 迁移里的"读回比对"要抓到
        self.entries[screen_id] = password
        return True

    def wipe(self, ids: Sequence[str]):
        self.wipe_calls.append(list(ids))
        deleted = 0
        for screen_id in ids:
            if self.entries.pop(screen_id, None) is not None:
                deleted += 1
        return deleted, []


def check_selection_rules() -> bool:
    """`select_backend()` 的真值表 —— 尤其是 UNKNOWN 的**否决权**。"""
    from krfb_gui.secrets import Occupancy, SecretsStatus, SelectionReason, select_backend

    OK, LOCKED, UNAVAILABLE = SecretsStatus.OK, SecretsStatus.LOCKED, SecretsStatus.UNAVAILABLE
    EMPTY, HAS, UNK = Occupancy.EMPTY, Occupancy.HAS_DATA, Occupancy.UNKNOWN

    cases = [
        # 有数据的赢
        ([("kwallet", OK, EMPTY), ("secretservice", OK, HAS), ("builtin", OK, EMPTY)],
         "secretservice", SelectionReason.HOLDS_DATA),
        # 都有数据时按 KDE 优先
        ([("kwallet", OK, HAS), ("secretservice", OK, HAS), ("builtin", OK, EMPTY)],
         "kwallet", SelectionReason.HOLDS_DATA),
        # **锁着但可能有数据**的后端有否决权：不能被静默跳过
        ([("kwallet", LOCKED, UNK), ("secretservice", OK, EMPTY), ("builtin", OK, EMPTY)],
         "kwallet", SelectionReason.LOCKED_UNKNOWN),
        # 前面确定没数据，才轮到后面的 UNKNOWN
        ([("kwallet", OK, EMPTY), ("secretservice", LOCKED, UNK), ("builtin", OK, EMPTY)],
         "secretservice", SelectionReason.LOCKED_UNKNOWN),
        # 谁都没数据 → KDE 优先
        ([("kwallet", OK, EMPTY), ("secretservice", OK, EMPTY), ("builtin", OK, EMPTY)],
         "kwallet", SelectionReason.AVAILABLE),
        # KDE 不可用 → 系统密钥环
        ([("kwallet", UNAVAILABLE, UNK), ("secretservice", OK, EMPTY), ("builtin", OK, EMPTY)],
         "secretservice", SelectionReason.AVAILABLE),
        # 系统库都不行 → 内置库（还没建库也算可用，可以现建）
        ([("kwallet", UNAVAILABLE, UNK), ("secretservice", UNAVAILABLE, EMPTY),
          ("builtin", SecretsStatus.NO_VAULT, EMPTY)],
         "builtin", SelectionReason.AVAILABLE),
        # 连内置库都不可用（比如库文件坏了）→ 仍然指向它，附"永远可用"的原因，
        # 让界面把真实状态显示出来，而不是挑一个根本用不了的系统库
        ([("kwallet", UNAVAILABLE, UNK), ("secretservice", UNAVAILABLE, EMPTY),
          ("builtin", UNAVAILABLE, EMPTY)],
         "builtin", SelectionReason.ALWAYS),
    ]

    for candidates, want_key, want_reason in cases:
        key, reason = select_backend(candidates)
        if key != want_key or reason is not want_reason:
            print(f"  ✗ {candidates} → ({key}, {reason.name})"
                  f"，期望 ({want_key}, {want_reason.name})")
            return False
    print(f"  ✓ {len(cases)} 条选择规则全部符合预期（含 UNKNOWN 否决权）")
    return True


def check_status_usability() -> bool:
    """哪些状态算"能用这个后端"（决定它能不能进候选、能不能建库）。"""
    from krfb_gui.secrets import SecretsStatus

    usable = {SecretsStatus.OK, SecretsStatus.LOCKED, SecretsStatus.NEEDS_PASSWORD,
              SecretsStatus.NO_VAULT}
    for status in SecretsStatus:
        if status.usable != (status in usable):
            print(f"  ✗ {status.name}.usable = {status.usable}，期望 {status in usable}")
            return False
        if status.needs_attention == (status is SecretsStatus.OK):
            print(f"  ✗ {status.name}.needs_attention 不对")
            return False
    print("  ✓ 可用性判定正确（锁定/待输密码/未建库都算可用，超时不算）")
    return True


def check_timeout_is_not_unavailable() -> bool:
    """超时必须是**独立**状态：它的文案与"不可用"不同，且仍然算需要处理。"""
    from krfb_gui.secrets import SecretsStatus

    timeout, unavailable = SecretsStatus.TIMEOUT, SecretsStatus.UNAVAILABLE
    if not timeout.needs_attention or not unavailable.needs_attention:
        print("  ✗ 超时/不可用都应该算「需要处理」")
        return False
    if timeout.label == unavailable.label or timeout.detail == unavailable.detail:
        print("  ✗ 超时和不可用的文案不该一样")
        return False
    # 超时是可恢复的：它不算 usable（也就不会被当成"有数据的后端"），
    # 但复检成功后 probe() 会把它拉回 OK —— 这条在 test_vault 的门面检查里覆盖不到，
    # 这里只锁住"它是个独立的、需要处理的、非可用的状态"这三点。
    if timeout.usable:
        print("  ✗ 超时不应该是 usable（此时读不到密码）")
        return False
    print("  ✓ 超时是独立状态：有自己的文案、需要处理、但不等于不可用")
    return True


def check_migration() -> bool:
    """迁移：跳过空条目、识别写失败与"谎报成功"、逐条读回比对。"""
    from krfb_gui.secrets import migrate

    src = FakeBackend({"a": "pass-a", "b": "pass-b", "c": "pass-c"})
    dst = FakeBackend(fail_write={"b"}, lie_on_write={"c"})
    progress: list[tuple[int, int]] = []

    copied, failed = migrate(src, dst, ["a", "b", "c", "d"],
                             on_progress=lambda done, total: progress.append((done, total)))

    if copied != ["a"]:
        print(f"  ✗ 成功列表 {copied}，期望 ['a']")
        return False
    if set(failed) != {"b", "c"}:
        print(f"  ✗ 失败列表 {sorted(failed)}，期望 ['b', 'c']")
        return False
    if dst.entries.get("a") != "pass-a":
        print("  ✗ 目标库里没有搬过去的密码")
        return False
    if progress and progress[-1][1] != 4:
        print(f"  ✗ 进度回调不对：{progress}")
        return False
    print("  ✓ 迁移：空条目跳过、写失败与谎报成功都能识别、读回比对有效")
    return True


def check_wipe_scope() -> bool:
    """清除只删给定的 id —— 库里别人的东西绝不能碰（用真的内置库验）。"""
    from krfb_gui import constants as C
    from krfb_gui.secrets.builtin import BuiltinVaultBackend

    for path in [C.VAULT_FILE, *[C.VAULT_FILE.with_name(C.VAULT_FILE.name + s)
                                 for s in ("-journal", "-wal", "-shm")]]:
        path.unlink(missing_ok=True)

    backend = BuiltinVaultBackend(timeout=5.0)
    backend.create("wipe test master")
    for name in ("keep-1", "drop-1", "keep-2"):
        backend.set(name, f"pw-{name}")

    deleted, errors = backend.wipe(["drop-1"])
    if errors or deleted != 1:
        print(f"  ✗ wipe 返回 ({deleted}, {errors})，期望 (1, [])")
        return False
    if backend.get("drop-1") is not None:
        print("  ✗ 该删的没删掉")
        return False
    if backend.get("keep-1") != "pw-keep-1" or backend.get("keep-2") != "pw-keep-2":
        print("  ✗ 把不该删的删掉了")
        return False
    print("  ✓ 清除只删指定 id，其余条目原样保留")
    return True


def check_last_modified_branches() -> bool:
    """时间戳：内置库有（用来显示"那批老数据是啥时候的"），KDE 钱包没有。"""
    from krfb_gui import constants as C
    from krfb_gui.secrets.builtin import BuiltinVaultBackend
    from krfb_gui.secrets.kwallet import KWalletBackend

    if KWalletBackend(timeout=1.0).last_modified() is not None:
        print("  ✗ KDE 钱包不提供条目时间戳，应该返回 None")
        return False

    for path in [C.VAULT_FILE, *[C.VAULT_FILE.with_name(C.VAULT_FILE.name + s)
                                 for s in ("-journal", "-wal", "-shm")]]:
        path.unlink(missing_ok=True)
    backend = BuiltinVaultBackend(timeout=5.0)
    if backend.last_modified() is not None:
        print("  ✗ 空库不该有时间戳")
        return False
    backend.create("time test master")
    backend.set("a", "pw")
    stamp = backend.last_modified()
    if stamp is None or stamp <= 0:
        print(f"  ✗ 有数据时时间戳不对：{stamp}")
        return False
    print("  ✓ 时间戳：内置库有、KDE 钱包返回 None")
    return True


def check_merge_plan() -> bool:
    """合并计划：只算不写、冲突单独列出、读不出来不当作新增。"""
    from krfb_gui.secrets.base import migrate, plan_merge

    src = FakeBackend({"a": "111", "b": "222", "c": "333"})
    dst = FakeBackend({"b": "222", "c": "999", "d": "444"})
    plan = plan_merge(src, dst, ["a", "b", "c", "d", "e"])

    if plan.add != ["a"] or plan.same != ["b"] or plan.conflicts != ["c"]:
        print(f"  ✗ 分类不对：add={plan.add} same={plan.same} "
              f"conflicts={plan.conflicts}（期望 ['a']/['b']/['c']）")
        return False
    if "d" in plan.ids_to_copy(True) or "e" in plan.ids_to_copy(True):
        print("  ✗ 目标独有 / 两边都没有的条目不该进写入列表")
        return False
    if plan.ids_to_copy(True) != ["a", "c"] or plan.ids_to_copy(False) != ["a"]:
        print(f"  ✗ 写入列表不对：听新数据={plan.ids_to_copy(True)}、"
              f"听目标={plan.ids_to_copy(False)}")
        return False
    if src.entries != {"a": "111", "b": "222", "c": "333"} or \
            dst.entries != {"b": "222", "c": "999", "d": "444"}:
        print("  ✗ 算计划不该改任何一边的数据")
        return False

    class Locked(FakeBackend):
        def get(self, screen_id):       # 锁着的库读出来就是 None
            return None

    locked = plan_merge(Locked(), dst, ["a", "b"])
    if locked.add or "a" not in locked.unreadable:
        # "b" 目标里有、源库读不出来：无从比对，但**不写**就是安全的选择
        print(f"  ✗ 读不出来被当成了新增：add={locked.add} "
              f"unreadable={locked.unreadable}")
        return False
    if "b" in locked.ids_to_copy(True):
        print("  ✗ 源库读不出来时不能拿目标的值去写")
        return False

    # 真合并一遍：把 ids_to_copy 交给 migrate()，目标变成两边的并集
    dst2 = FakeBackend({"c": "999"})
    plan2 = plan_merge(src, dst2, ["a", "b", "c"])
    copied, failed = migrate(src, dst2, plan2.ids_to_copy(True))
    if failed or sorted(copied) != ["a", "b", "c"]:
        print(f"  ✗ 合并写入失败：copied={copied} failed={failed}")
        return False
    if dst2.entries != {"a": "111", "b": "222", "c": "333"}:
        print(f"  ✗ 合并结果不对：{dst2.entries}")
        return False

    print("  ✓ 合并：只算不写、冲突单列、读不出来不算新增、能落成真正的并集")
    return True


def check_backend_combo() -> bool:
    """设置里的下拉：只有三个具体库、没有「自动」；不可用的当前项仍可选。

    这里守的是两条修过的 bug：
      * 钱包关掉再打开之后那一项被置灰、再也选不回去；
      * 旧版「自动」是个策略而不是后端，选它绕过了合并/清除提示（已整个删掉）。
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from krfb_gui import prefs
    from krfb_gui.secrets import Secrets
    from krfb_gui.secrets.base import SelectionReason
    from krfb_gui.ui.dialogs import SettingsDialog
    from krfb_gui.ui.theme import detect_palette

    app = QApplication.instance() or QApplication([])
    palette = detect_palette(app)

    if "auto" in prefs.BACKENDS or prefs.password_backend() not in prefs.BACKENDS:
        print(f"  ✗ 偏好不该再有 auto，且必须有具体默认值：{prefs.BACKENDS} / "
              f"{prefs.password_backend()}")
        return False

    secrets = Secrets()
    # 钱包被关掉之后的样子：两个系统库都不可用
    secrets.availability = {"kwallet": False, "secretservice": False, "builtin": True}
    secrets.backend_key = "builtin"
    secrets.selection_reason = SelectionReason.ALWAYS

    def build(preference):
        prefs.set_password_backend(preference)
        return SettingsDialog(palette, lambda: [], secrets, "0",
                              on_unlock=lambda: None,
                              on_backend_selected=lambda key: True,
                              on_recheck=lambda: None,
                              on_vault_action=lambda action: None)

    for preference in (prefs.BACKEND_KWALLET, prefs.BACKEND_SECRET_SERVICE):
        dialog = build(preference)
        combo = dialog._backend_combo
        items = [combo.itemData(i) for i in range(combo.count())]
        if preference not in items:
            print(f"  ✗ {preference}：不可用也得留在列表里，实际 {items}")
            return False
        model = combo.model()
        item = model.item(combo.findData(preference)) if model is not None else None
        if item is not None and not item.isEnabled():
            print(f"  ✗ {preference}：被置灰了 —— 这正是用户没法再选回去的原因")
            return False
        if combo.currentData() != preference:
            print(f"  ✗ {preference}：当前项应为它自己，实际 {combo.currentData()}")
            return False
        if "builtin" not in items:
            print(f"  ✗ 内置库永远该在列表里：{items}")
            return False
        if "auto" in items:
            print(f"  ✗ 「自动」这一项已经删掉了：{items}")
            return False
        dialog.deleteLater()

    # 钱包回来之后：可用集变了要能通知出去，那一项重新可用
    secrets.availability = {"kwallet": True, "secretservice": False, "builtin": True}
    dialog = build(prefs.BACKEND_KWALLET)
    items = [dialog._backend_combo.itemData(i)
             for i in range(dialog._backend_combo.count())]
    if items[:2] != [prefs.BACKEND_KWALLET, prefs.BACKEND_BUILTIN]:
        print(f"  ✗ 钱包恢复后应列出「KDE 钱包」与「内置加密库」：{items}")
        return False
    dialog.deleteLater()
    app.processEvents()

    # 旧配置里存过 "auto" → 读到就当 KDE 钱包（"自动"的定义本来就是"优先 KDE"）
    prefs.set_value("password_backend", "auto")
    if prefs.password_backend() != prefs.BACKEND_KWALLET:
        print(f"  ✗ 旧值 auto 该改写成 KDE 钱包，实际 {prefs.password_backend()}")
        return False
    prefs.set_value("password_backend", "garbage")
    if prefs.password_backend() != prefs.BACKEND_KWALLET:
        print(f"  ✗ 垃圾值该落到 KDE 钱包，实际 {prefs.password_backend()}")
        return False

    print("  ✓ 下拉：只有三个具体库、不可用的当前项仍可选、钱包回来那一项即恢复、"
          "旧配置的 auto 归到 KDE 钱包")
    return True


def check_availability_refresh() -> bool:
    """轮询里的可用性复检：只改"哪些库可用"，不动当前选择。

    另外要守住一条：抢不到锁（TIMEOUT）时结论不可信，**不能**把后端标成不可用
    —— 那会让下拉里的后端凭空消失。
    """
    from krfb_gui.secrets import Secrets
    from krfb_gui.secrets.base import SecretsStatus

    class Stub:
        def __init__(self, status):
            self.status = status

        def probe(self):
            return self.status

    secrets = Secrets()
    secrets.availability = {"kwallet": False, "secretservice": False, "builtin": True}
    secrets.backend_key = "builtin"
    secrets._backends = {
        "kwallet": Stub(SecretsStatus.TIMEOUT),      # 抢不到锁 → 别下结论
        "secretservice": Stub(SecretsStatus.OK),
        "builtin": Stub(SecretsStatus.OK),
    }

    changed = secrets.refresh_availability()
    if secrets.availability["kwallet"] is not False:
        print("  ✗ 超时不该被当成不可用（结论不可信，保持原样）")
        return False
    if secrets.availability["secretservice"] is not True:
        print("  ✗ 可用后端没被标回可用")
        return False
    if secrets.backend_key != "builtin":
        print(f"  ✗ 复检动了当前选择：{secrets.backend_key}")
        return False

    # 钱包回来了（这次探测正常）→ 可用性翻回来
    secrets._backends["kwallet"] = Stub(SecretsStatus.OK)
    if not secrets.refresh_availability():
        print("  ✗ 可用性变了却没报告变化（界面就不会刷新）")
        return False
    if not secrets.availability["kwallet"]:
        print("  ✗ 钱包回来后没被标成可用")
        return False
    if secrets.backend_key != "builtin":
        print("  ✗ 复检不该顺手把库也切了（会话内保持粘住）")
        return False

    print("  ✓ 可用性复检：只改可用集、不动选择、超时不误判为不可用")
    return True


def check_availability_poll_wiring() -> bool:
    """轮询里那条线要接上：每 ~6 秒后台复检一次，变了才通知界面。

    这是用户报的那个 bug 的另一半 —— 光有 refresh_availability() 没人调，
    「自动」在钱包回来后照样回不来。
    """
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import threading
    import time as _time

    from PySide6.QtWidgets import QApplication

    from krfb_gui.secrets import Secrets
    from krfb_gui.secrets.base import SecretsStatus
    from krfb_gui.ui.main_window import MainWindow
    from krfb_gui.ui.theme import detect_palette

    class Stub:
        def __init__(self, status):
            self.status = status

        def probe(self):
            return self.status

        def present_ids(self, candidates):     # 启动扫描会问一遍
            return []

    class StubManager:
        def environment_warnings(self):
            return []

        def __getattr__(self, name):
            return lambda *a, **k: None

    app = QApplication.instance() or QApplication([])

    class Quiet(MainWindow):          # 别让轮询去碰真的虚拟屏
        def _request_unlock(self, *, automatic):   # 跳过启动扫描，专测轮询这一条线
            pass

        def _refresh(self):
            pass

        def _verify_pending(self):
            pass

    secrets = Secrets()
    secrets.availability = {"kwallet": False, "secretservice": False, "builtin": True}
    secrets.backend_key = "builtin"
    secrets._backends = {"kwallet": Stub(SecretsStatus.OK),      # 钱包已经回来了
                         "secretservice": Stub(SecretsStatus.NO_SERVICE),
                         "builtin": Stub(SecretsStatus.OK)}
    window = Quiet(detect_palette(app), __import__("krfb_gui.store", fromlist=["Store"]).Store(),
                   secrets, StubManager())
    fired: list[int] = []
    window.availability_changed.connect(lambda: fired.append(1))

    window._ticks = 2
    window._recheck_secrets()         # 没到 3 的倍数 → 什么都不做
    if fired or secrets.availability["kwallet"]:
        print("  ✗ 不该每轮都复检")
        return False

    window._ticks = 3
    window._recheck_secrets()
    deadline = _time.monotonic() + 5
    while _time.monotonic() < deadline and not fired:
        app.processEvents()
        _time.sleep(0.02)
    ok = bool(fired) and secrets.availability["kwallet"] is True
    if not ok:
        print(f"  ✗ 钱包回来后没通知界面：fired={fired} "
              f"availability={secrets.availability}")
        return False
    if secrets.backend_key != "builtin":
        print("  ✗ 复检不该顺手换库")
        return False
    window._timer.stop()
    window._avail_running = False
    window.hide()
    print("  ✓ 轮询：每 6 秒后台复检、有变化才通知界面、不动当前选择")
    return True


def check_default_fallback_chain() -> bool:
    """默认 KDE 钱包；它不可用时按 系统密钥环 → 内置库 回落，且**不改偏好**。

    这是"把自动删掉、直接默认 KDE"之后的行为：用户没得选"自动"，
    但钱包不可用时不能让程序变成"没有密码库"。
    """
    from krfb_gui import prefs
    from krfb_gui.secrets import Secrets
    from krfb_gui.secrets.base import SecretsStatus

    class Stub:
        def __init__(self, status, ids=()):
            self.status = status
            self.ids = list(ids)

        def probe(self):
            return self.status

        def present_ids(self, candidates):
            return [c for c in candidates if c in self.ids]

    def scan_with(kwallet, keyring, seen_pref=prefs.BACKEND_KWALLET):
        secrets = Secrets()
        secrets._backends = {
            "kwallet": Stub(kwallet),
            "secretservice": Stub(keyring),
            "builtin": Stub(SecretsStatus.NO_VAULT),
        }
        prefs.set_password_backend(seen_pref)
        chosen = secrets.scan(["a", "b"])
        return secrets, chosen

    # ① 钱包可用 → 就是钱包
    secrets, chosen = scan_with(SecretsStatus.OK, SecretsStatus.OK)
    if chosen != prefs.BACKEND_KWALLET or secrets.fallback_from:
        print(f"  ✗ 钱包可用时应直接用钱包：{chosen} fallback={secrets.fallback_from}")
        return False

    # ② 钱包不可用、密钥环可用 → 回落到密钥环，偏好不动
    secrets, chosen = scan_with(SecretsStatus.NO_SERVICE, SecretsStatus.OK)
    if chosen != prefs.BACKEND_SECRET_SERVICE:
        print(f"  ✗ 钱包没了应回落到系统密钥环，实际 {chosen}")
        return False
    if secrets.fallback_from != prefs.BACKEND_KWALLET:
        print(f"  ✗ 回落后要说明原选的是谁：{secrets.fallback_from}")
        return False
    if prefs.password_backend() != prefs.BACKEND_KWALLET:
        print(f"  ✗ 回落不该改偏好（钱包回来要能自动用回去）："
              f"{prefs.password_backend()}")
        return False

    # ③ 两个系统库都不可用 → 落到内置库（永远可用）
    secrets, chosen = scan_with(SecretsStatus.NO_SERVICE, SecretsStatus.NO_SERVICE)
    if chosen != prefs.BACKEND_BUILTIN:
        print(f"  ✗ 系统库都没了应落到内置库，实际 {chosen}")
        return False

    # ④ 钱包锁着（可用）→ 仍然用钱包，优先于"有数据的密钥环"
    secrets, chosen = scan_with(SecretsStatus.LOCKED, SecretsStatus.OK)
    if chosen != prefs.BACKEND_KWALLET:
        print(f"  ✗ 锁着的钱包也算可用，应继续用它：{chosen}")
        return False

    print("  ✓ 默认 KDE 钱包；不可用时按 系统密钥环 → 内置库 回落，且不改偏好")
    return True


def main() -> int:
    base = isolate_config()
    shutil.rmtree(base, ignore_errors=True)

    checks = (
        ("后端选择规则", check_selection_rules),
        ("状态可用性判定", check_status_usability),
        ("超时 ≠ 不可用", check_timeout_is_not_unavailable),
        ("迁移（含部分失败）", check_migration),
        ("清除范围", check_wipe_scope),
        ("时间戳来源", check_last_modified_branches),
        ("默认回落链", check_default_fallback_chain),
        ("合并计划", check_merge_plan),
        ("密码库下拉", check_backend_combo),
        ("可用性复检", check_availability_refresh),
        ("轮询接线", check_availability_poll_wiring),
    )

    failed = 0
    for title, check in checks:
        print(f"{title}:")
        try:
            ok = check()
        except Exception as exc:
            print(f"  ✗ 抛异常：{type(exc).__name__}: {exc}")
            ok = False
        failed += 0 if ok else 1

    print(f"\n失败 {failed} 项")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
