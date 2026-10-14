"""核心需求验证：GUI 退出后虚拟屏仍在运行，且新进程能重新识别并接管。

分两个阶段在**两个独立的 Python 进程**里跑，这才是有意义的验证 ——
同一进程内验证无法证明"GUI 退出后还活着"。

    .venv/bin/python tests/test_persistence.py --phase a   # 启动后退出
    .venv/bin/python tests/test_persistence.py --phase b   # 全新进程重新发现

配置与状态写到临时目录（`/tmp/krfb-virtualmonitor-gui-test`，可用 KRBFTEST_DIR 改），
不碰用户的真实配置 —— 见 isolate_config()。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

TEST_NAME = "PersistTest"
TEST_PORT = 5923


def isolate_config(base_dir: str | None = None) -> Path:
    """把配置/运行态指到临时目录 —— 绝不能写进用户的真实配置。

    必须在 import krfb_gui **之前**调用：`constants.py` 在导入时就把 CONFIG_DIR /
    STATE_DIR 从环境变量里算好了，之后再改就没用了。

    为什么用固定路径而不是 mkdtemp：phase a 与 phase b 是两个独立进程，必须看到
    同一份文件。要换地方就设 KRBFTEST_DIR。
    """
    base = Path(base_dir or os.environ.get("KRBFTEST_DIR")
                or Path(tempfile.gettempdir()) / "krfb-virtualmonitor-gui-test")
    os.environ["XDG_CONFIG_HOME"] = str(base / "config")
    os.environ["XDG_STATE_HOME"] = str(base / "state")
    return base


def _make_manager():
    from krfb_gui.manager import Manager
    from krfb_gui.secrets import Secrets
    from krfb_gui.store import Store

    store = Store()
    store.load()
    return store, Manager(store, Secrets())


def phase_a() -> int:
    from krfb_gui.models import Screen

    store, manager = _make_manager()
    screen = Screen(name=TEST_NAME, width=1920, height=1080, scale=1.0, port=TEST_PORT)
    store.add(screen)
    print(f"  已登记: {screen.name} {screen.resolution} 端口 {screen.port}")

    result = manager.spawn(screen, "testpass1")
    print(f"  启动结果: ok={result.ok} pid={result.pid} error={result.error!r}")
    if not result.ok:
        return 1

    # 等待 KWin 出现 Virtual-<name> —— 这才是"虚拟屏真的建成了"的证据
    ready = False
    for _ in range(25):
        if manager.output_ready(screen):
            ready = True
            break
        time.sleep(0.4)
    print(f"  KWin 输出 Virtual-{TEST_NAME} 出现: {ready}")

    manager.apply_requested_scale(screen)
    runtime = store.runtime_for(screen.id)
    print(f"  回读实测值: {runtime.actual_resolution_display} @{runtime.actual_scale}")

    # 记录关键信息供阶段 B 比对
    payload = {"id": screen.id, "pid": result.pid, "starttime": result.starttime}
    Path(os.environ["KRBFTEST_INFO"]).write_text(json.dumps(payload))
    return 0


def phase_b() -> int:
    from krfb_gui.models import ScreenState

    info = json.loads(Path(os.environ["KRBFTEST_INFO"]).read_text())
    store, manager = _make_manager()

    screens = store.sorted_screens()
    print(f"  从磁盘读到 {len(screens)} 个虚拟屏")
    if len(screens) != 1:
        print(f"  ✗ 期望 1 个，实际 {len(screens)}")
        return 1

    screen = screens[0]
    runtime = store.runtime_for(screen.id, create=False)
    state = manager.state_of(screen)
    alive = manager.is_recorded_process_alive(runtime)

    print(f"  id 一致: {screen.id == info['id']}")
    print(f"  记录的 pid={runtime.pid} starttime={runtime.starttime}")
    print(f"  期望运行标志={screen.desired_running}")
    print(f"  身份校验（pid+starttime）通过={alive}")
    print(f"  状态判定: {state.name} ({state.label})")

    ok = True
    if screen.id != info["id"]:
        print("  ✗ id 不匹配")
        ok = False
    if runtime.pid != info["pid"] or runtime.starttime != info["starttime"]:
        print("  ✗ pid/starttime 与阶段 A 记录的不一致")
        ok = False
    if state is not ScreenState.RUNNING:
        print(f"  ✗ 期望 RUNNING，实际 {state.name}")
        ok = False

    # 已管理的进程不应出现在"未托管"列表里
    unmanaged = manager.unmanaged_processes()
    if any(p.pid == info["pid"] for p in unmanaged):
        print("  ✗ 已管理的进程被误判为未托管")
        ok = False
    print(f"  未托管进程数={len(unmanaged)}（已管理的已正确排除）")

    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["a", "b"], required=True)
    args = parser.parse_args()

    base = isolate_config()
    if args.phase == "a":
        # 每次都从干净状态开始，免得上一轮的残留让 phase b 读到两个屏
        for name in ("config", "state"):
            shutil.rmtree(base / name, ignore_errors=True)
        print(f"  配置目录: {base}（不碰你的真实配置）")
    return phase_a() if args.phase == "a" else phase_b()


if __name__ == "__main__":
    sys.exit(main())
