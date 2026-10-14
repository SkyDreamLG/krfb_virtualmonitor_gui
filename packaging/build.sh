#!/usr/bin/env bash
# 构建独立可执行程序。
#
#   packaging/build.sh             单文件（默认）→ dist/krfb-virtualmonitor-gui
#   packaging/build.sh --onedir    目录版      → dist/onedir/krfb-virtualmonitor-gui/
#
# 两种产物都拷到别的 Linux 机器就能跑，不需要 .venv，也不需要目标机器装 Python。
#
# 为什么两种都留着：
#   * 单文件（onefile）—— 就一个 66MB 的文件，方便拷来拷去。代价是**每次启动**
#     都要把 170MB 解压到 $TMPDIR（本机 /tmp 是 tmpfs，等于写进内存），
#     实测启动 0.79s，而目录版 0.21s；
#   * 目录版（onedir）—— 启动快、不重复解压，适合长期装在机器上（尤其开机自启）。
#
# 两者可以共存：单文件占 dist/krfb-virtualmonitor-gui（文件），
# 目录版占 dist/onedir/krfb-virtualmonitor-gui/（目录），互不冲突。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

APP="krfb-virtualmonitor-gui"
PY="$ROOT/.venv/bin/python"
MODE="onefile"

for arg in "$@"; do
    case "$arg" in
        --onedir) MODE="onedir" ;;
        -h|--help)
            sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *)
            echo "未知参数：$arg（可用：--onedir）" >&2
            exit 2 ;;
    esac
done

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

if [[ "$MODE" == "onedir" ]]; then
    SPEC="$ROOT/packaging/$APP.spec"
    OUTPUT="$ROOT/dist/onedir/$APP"
    echo "==> 清理旧的 build/ 与 dist/onedir/$APP"
    rm -rf "$ROOT/build" "$ROOT/dist/onedir"
    DISTPATH="$ROOT/dist/onedir"
else
    SPEC="$ROOT/packaging/$APP-onefile.spec"
    OUTPUT="$ROOT/dist/$APP"
    echo "==> 清理旧的 build/ 与 dist/$APP"
    rm -rf "$ROOT/build" "$ROOT/dist/$APP"
    DISTPATH="$ROOT/dist"
fi

echo "==> 开始构建（$MODE，首次约需 1~2 分钟）"
# 显式用 .venv 的 python 跑 PyInstaller：保证被分析的就是这套依赖，
# 而不是 PATH 上碰巧存在的另一个 Python 环境。
"$PY" -m PyInstaller --noconfirm --clean --distpath "$DISTPATH" "$SPEC"

echo
echo "==> 完成"
du -sh "$OUTPUT"
echo
if [[ "$MODE" == "onedir" ]]; then
    echo "运行：        ./dist/onedir/$APP/$APP"
    echo "也可直接敲：  ./dist/onedir/$APP/$APP --tray    # 直接缩到托盘"
else
    echo "运行：        ./dist/$APP"
    echo "也可直接敲：  ./dist/$APP --tray    # 直接缩到托盘"
    echo
    echo "提示：单文件每次启动要解压约 170MB（实测 0.79s）。想更快就用 --onedir。"
fi
echo
echo "想让它出现在应用菜单和 ~/.local/bin 里：packaging/install-desktop.sh"
