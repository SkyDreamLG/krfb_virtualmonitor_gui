#!/usr/bin/env bash
# 构建独立可执行程序（onedir）。
#
#   packaging/build.sh
#
# 产物在 dist/krfb-virtualmonitor-gui/ —— 整个目录拷到别处也能跑，
# 不需要 .venv，也不需要目标机器装 Python。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APP="krfb-virtualmonitor-gui"
PY="$ROOT/.venv/bin/python"

if [[ ! -x "$PY" ]]; then
    echo "找不到 $PY" >&2
    echo "先在项目根目录建好虚拟环境：uv sync" >&2
    exit 1
fi

# PyInstaller 只是构建工具，不属于运行时依赖（pyproject 里放在 dev 组）
if ! "$PY" -c "import PyInstaller" 2>/dev/null; then
    echo "==> .venv 里没有 PyInstaller，先装上"
    if command -v uv >/dev/null 2>&1; then
        uv pip install --python "$PY" pyinstaller
    else
        "$PY" -m pip install pyinstaller
    fi
fi

echo "==> 清理旧的 build/ 与 dist/$APP"
rm -rf "$ROOT/build" "$ROOT/dist/$APP"

echo "==> 开始构建（首次约需 1~2 分钟）"
# 显式用 .venv 的 python 跑 PyInstaller：保证被分析的就是这套依赖，
# 而不是 PATH 上碰巧存在的另一个 Python 环境。
"$PY" -m PyInstaller --noconfirm --clean "$ROOT/packaging/$APP.spec"

echo
echo "==> 完成"
du -sh "$ROOT/dist/$APP"
echo
echo "运行：        ./dist/$APP/$APP"
echo "也可直接敲：  ./dist/$APP/$APP --tray    # 直接缩到托盘"
echo
echo "想让它出现在应用菜单和 ~/.local/bin 里：packaging/install-desktop.sh"
