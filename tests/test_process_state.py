"""僵尸进程回归测试：进程已退出但还没被回收时，绝不能判成"还在跑"。

背景（本机实测）：krfb 收到 SIGTERM 后 **1 秒内**就退出（KWin 也把虚拟屏摘了），
但它是本程序的子进程；父进程不 `waitpid` 的话它就变成僵尸 —— `/proc/<pid>/stat`
还在、starttime 也不变。于是"点停止"之后界面一直显示"运行中"，直到某个偶然事件
触发 Python 回收子进程（`subprocess` 只在下一次创建 Popen 时才顺手 `_cleanup()`），
实测能拖到一分钟以上，而系统那边 3 秒就已经看不到屏了。

    .venv/bin/python tests/test_process_state.py

修复前第 1/2/3 项失败，修复后全绿。不建虚拟屏、不碰真实配置、不需要显示环境。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SLEEP = shutil.which("sleep") or "/bin/sleep"


def _wait_for_state(pid: int, want: str, timeout: float = 5.0) -> str:
    """轮询 /proc 直到进程进入 want 状态（Z=僵尸 S=可中断睡眠），返回最终状态。

    刻意用轮询而不是固定 sleep：慢机器上给足时间，快机器上不浪费时间。
    """
    from krfb_gui import proctools

    deadline = time.time() + timeout
    state = ""
    while time.time() < deadline:
        state = proctools.read_state(pid) or "GONE"
        if state == want:
            return state
        time.sleep(0.05)
    return state


def _make_zombie() -> subprocess.Popen:
    """造一个**未被回收**的僵尸子进程。

    关键：必须持有 Popen 引用。一旦对象被回收，`Popen.__del__` 会把它塞进
    `subprocess._active`，之后任何一次创建 Popen 都会顺手把它 waitpid 掉 ——
    那要观察的僵尸就自己消失了。持有引用则 `__del__` 不跑，内核会一直留着它。
    """
    proc = subprocess.Popen([SLEEP, "0.05"])
    state = _wait_for_state(proc.pid, "Z")
    assert state == "Z", f"没能造出僵尸（状态 {state}）"
    return proc


def _manager(tmp: Path):
    from krfb_gui.manager import Manager
    from krfb_gui.secrets import Secrets
    from krfb_gui.store import Store

    store = Store(tmp / "screens.json", tmp / "runtime.json")
    return store, Manager(store, Secrets())


def check_zombie_is_visible_to_proc_but_not_alive() -> bool:
    """僵尸的 starttime 照样读得到 —— 这正是只比 starttime 会栽的地方。"""
    from krfb_gui import proctools

    proc = _make_zombie()
    try:
        starttime = proctools.read_starttime(proc.pid)
        if starttime is None:
            print("  ✗ 僵尸的 starttime 读不到（前提变了？）—— 本测试的假设不成立")
            return False
        if not proctools.is_zombie(proc.pid):
            print("  ✗ 状态明明是 Z，is_zombie() 却说不是")
            return False
    finally:
        proc.wait()

    print("  ✓ 僵尸：starttime 仍读得到（所以只比 starttime 不够），is_zombie() 认得出")
    return True


def check_zombie_not_counted_as_running() -> bool:
    """记录里的进程变成僵尸后，必须判成"不在跑"。"""
    from krfb_gui import proctools
    from krfb_gui.models import Screen, ScreenState

    with tempfile.TemporaryDirectory(prefix="krfbstate-") as tmp:
        store, manager = _manager(Path(tmp))
        screen = Screen(name="ZombieTest", width=1920, height=1080, scale=1.0, port=5991)
        store.add(screen)

        proc = _make_zombie()
        try:
            starttime = proctools.read_starttime(proc.pid)
            store.mark_started(screen.id, proc.pid, starttime)
            runtime = store.runtime_for(screen.id, create=False)

            alive = manager.is_recorded_process_alive(runtime)
            state = manager.state_of(screen)
        finally:
            proc.wait()

        if alive:
            print("  ✗ 僵尸被判成「还在跑」（界面会一直显示运行中）")
            return False
        if state is not ScreenState.STOPPED:
            print(f"  ✗ 期望 STOPPED（desired_running=False），实际 {state.name}")
            return False

    print("  ✓ 僵尸不再算运行中：state_of() 立刻回到已停止")
    return True


def check_terminate_still_records_intent_on_zombie() -> bool:
    """对僵尸发不出信号，但"用户要它停"必须记下来 —— 否则会误弹崩溃横幅。

    僵尸的 /proc/<pid>/exe 已经读不到，terminate() 的身份校验必然失败。
    """
    from krfb_gui import proctools
    from krfb_gui.models import Screen

    with tempfile.TemporaryDirectory(prefix="krfbstate-") as tmp:
        store, manager = _manager(Path(tmp))
        screen = Screen(name="ZombieStop", width=1920, height=1080, scale=1.0, port=5992)
        screen.desired_running = True
        store.add(screen)

        proc = _make_zombie()
        try:
            store.mark_started(screen.id, proc.pid, proctools.read_starttime(proc.pid))
            signalled = manager.terminate(screen)
            intent = screen.desired_running
        finally:
            proc.wait()

        if signalled:
            print("  ✗ 僵尸身上居然报告「信号发出去了」")
            return False
        if intent:
            print("  ✗ 停止意图没被记录：界面会把它当异常退出，弹出崩溃横幅")
            return False

    print("  ✓ 对僵尸：信号发不出去（返回 False）但停止意图已记录")
    return True


def check_live_process_still_running() -> bool:
    """正面对照：真正在跑的进程必须照样判成运行中（别修过头）。"""
    from krfb_gui import proctools
    from krfb_gui.models import Screen, ScreenState

    with tempfile.TemporaryDirectory(prefix="krfbstate-") as tmp:
        store, manager = _manager(Path(tmp))
        screen = Screen(name="AliveTest", width=1920, height=1080, scale=1.0, port=5993)
        screen.desired_running = True
        store.add(screen)

        proc = subprocess.Popen([SLEEP, "30"])
        try:
            _wait_for_state(proc.pid, "S")
            store.mark_started(screen.id, proc.pid, proctools.read_starttime(proc.pid))
            runtime = store.runtime_for(screen.id, create=False)
            alive = manager.is_recorded_process_alive(runtime)
            state = manager.state_of(screen)
        finally:
            proc.terminate()
            proc.wait()

        if not alive or state is not ScreenState.RUNNING:
            print(f"  ✗ 活着的进程被判成不在跑（alive={alive}, state={state.name}）")
            return False

    print("  ✓ 真正在跑的进程仍然判为运行中")
    return True


def main() -> int:
    checks = (
        ("僵尸对 /proc 仍是可见的（starttime 读得到）", check_zombie_is_visible_to_proc_but_not_alive),
        ("僵尸不算运行中", check_zombie_not_counted_as_running),
        ("对僵尸停止仍记录用户意图", check_terminate_still_records_intent_on_zombie),
        ("活着的进程仍算运行中（正面对照）", check_live_process_still_running),
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
