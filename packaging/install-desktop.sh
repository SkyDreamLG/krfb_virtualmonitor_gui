#!/usr/bin/env bash
# 把桌面项和图标装到用户目录，让程序出现在 KDE 应用菜单里。
#
# 顺带解决一个噪声：Qt 的 setDesktopFileName("krfb-virtualmonitor-gui") 需要一个
# 同名的 .desktop 才能注册到 portal，否则每次启动都会打印
# "Could not register app ID: App info not found"。
#
# 完全可逆：再跑一次带 --uninstall 即可移除。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_ID="krfb-virtualmonitor-gui"
BIN_DIR="${HOME}/.local/bin"
APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"

if [[ "${1:-}" == "--uninstall" ]]; then
    rm -f "$APP_DIR/$APP_ID.desktop" "$ICON_DIR/$APP_ID.svg" "$BIN_DIR/$APP_ID"
    echo "已移除桌面项、图标与 $BIN_DIR/$APP_ID"
    command -v update-desktop-database >/dev/null && update-desktop-database "$APP_DIR" 2>/dev/null || true
    exit 0
fi

mkdir -p "$APP_DIR" "$ICON_DIR" "$BIN_DIR"

# 一个稳定入口，避免 .desktop 里写死路径。
# 优先用 packaging/build.sh 产出的独立可执行程序；没构建过才回退到源码 + .venv。
BUNDLED="$ROOT/dist/$APP_ID/$APP_ID"
cat > "$BIN_DIR/$APP_ID" <<EOF
#!/usr/bin/env bash
if [[ -x "$BUNDLED" ]]; then
    exec "$BUNDLED" "\$@"
fi
exec "$ROOT/.venv/bin/python" "$ROOT/main.py" "\$@"
EOF
chmod +x "$BIN_DIR/$APP_ID"

install -m644 "$ROOT/packaging/$APP_ID.svg" "$ICON_DIR/$APP_ID.svg"

# 本地化键与 krfb_gui/i18n/ 的词条一一对应（默认键按规范用英文，
# 其余语言各一行，菜单里显示哪种由桌面环境按系统区域自己挑）。
# 改语言表时这两处要一起改 —— i18n/zh_cn.py 里有同一批键。
cat > "$APP_DIR/$APP_ID.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Krfb Virtual Screen Manager
Name[zh_CN]=Krfb 虚拟屏管理器
Name[zh_TW]=Krfb 虛擬螢幕管理員
Name[ja]=Krfb 仮想ディスプレイマネージャー
Name[ko]=Krfb 가상 디스플레이 관리자
Name[de]=Krfb-Verwaltung für virtuelle Bildschirme
Name[fr]=Gestionnaire d'écrans virtuels Krfb
Name[es]=Gestor de pantallas virtuales Krfb
Name[it]=Gestore schermi virtuali Krfb
Name[pt_BR]=Gerenciador de telas virtuais do Krfb
Name[ru]=Менеджер виртуальных экранов Krfb
Comment=Manage krfb-virtualmonitor virtual screens
Comment[zh_CN]=图形化管理 krfb-virtualmonitor 虚拟显示器
Comment[zh_TW]=圖形化管理 krfb-virtualmonitor 虛擬顯示器
Comment[ja]=krfb-virtualmonitor の仮想ディスプレイをグラフィカルに管理
Comment[ko]=krfb-virtualmonitor 가상 디스플레이를 그래픽으로 관리
Comment[de]=Virtuelle Bildschirme mit krfb-virtualmonitor verwalten
Comment[fr]=Gérer les écrans virtuels de krfb-virtualmonitor
Comment[es]=Gestionar las pantallas virtuales de krfb-virtualmonitor
Comment[it]=Gestisci gli schermi virtuali di krfb-virtualmonitor
Comment[pt_BR]=Gerencie telas virtuais do krfb-virtualmonitor
Comment[ru]=Управление виртуальными экранами krfb-virtualmonitor
Exec=$BIN_DIR/$APP_ID
Icon=$APP_ID
Terminal=false
Categories=System;RemoteAccess;Network;
Keywords=krfb;vnc;virtual;monitor;虚拟屏;远程;
StartupNotify=true
EOF

command -v update-desktop-database >/dev/null && update-desktop-database "$APP_DIR" 2>/dev/null || true
echo "已安装："
echo "  菜单项  $APP_DIR/$APP_ID.desktop"
echo "  图标    $ICON_DIR/$APP_ID.svg"
echo "  启动器  $BIN_DIR/$APP_ID"
echo
if [[ -x "$BUNDLED" ]]; then
    echo "入口指向：打包版（$BUNDLED）"
else
    echo "入口指向：源码版（$ROOT/.venv/bin/python main.py）"
    echo "  提示：跑一次 packaging/build.sh 构建独立可执行程序后重跑本脚本，入口会自动切过去。"
fi
echo
echo "现在可以从 KDE 应用菜单搜索「Krfb 虚拟屏管理器」启动了。"
echo "卸载：$0 --uninstall"
