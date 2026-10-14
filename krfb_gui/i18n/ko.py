"""韩文词条表。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的韩文。
`{named}` 占位符集合必须与键完全一致；引号写进词条本身（韩文用 ' '），
命令名与程序原样输出不译。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "시스템 따르기",
    ", ": ", ",  # join_list() 的列表分隔符
    "Cancel": "취소",
    "Close": "닫기",
    "Delete": "삭제",
    "Log": "로그",
    "Notes": "메모",
    "Password": "비밀번호",
    "Port": "포트",
    "Random": "무작위",
    "Settings": "설정",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Krfb 가상 디스플레이 관리자",
    "3:2 Tablet": "3:2 태블릿",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "krfb-virtualmonitor 가상 디스플레이를 그래픽으로 관리",

    # --- models -------------------------------------------------------------
    "Running": "실행 중",
    "Stopped": "중지됨",
    "Exited unexpectedly": "예기치 않게 종료됨",
    "Starting": "시작 중",
    "Failed to start": "시작 실패",
    "Unmanaged": "관리되지 않음",
    "Unnamed": "이름 없음",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "키링 준비됨",
    "Keyring locked": "키링 잠김",
    "No keyring service found": "키링 서비스를 찾을 수 없음",
    "Keyring unavailable": "키링을 사용할 수 없음",
    "Keyring not responding": "키링이 응답하지 않음",
    "Keyring error": "키링 오류",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "KDE 지갑이 닫혀 있습니다. 비밀번호는 이번 세션 동안에만 메모리에 보관됩니다",
    "kwalletd is not running on the session bus":
        "세션 버스에 kwalletd가 없습니다",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "설정 파일을 분석할 수 없습니다: {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "설정 버전 {found}이(가) 예상한 {expected}과(와) 일치하지 않습니다. "
        "최선을 다해 읽어 들였습니다",
    "Unrecognized config format: {path}":
        "설정 형식을 인식할 수 없습니다: {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "krfb-virtualmonitor를 찾을 수 없습니다 ({path}에 있어야 합니다)",
    "No password available": "사용할 수 있는 비밀번호가 없습니다",
    "Port {port} is already in use": "포트 {port}이(가) 이미 사용 중입니다",
    "Failed to start: {error}": "시작 실패: {error}",
    "The process vanished immediately after starting":
        "시작 직후 프로세스가 사라졌습니다",
    "The name \"{name}\" is already taken by a managed screen":
        "이름 '{name}'은(는) 관리 중인 가상 디스플레이에서 이미 사용 중입니다",
    "Port {port} is already taken by a managed screen":
        "포트 {port}은(는) 관리 중인 가상 디스플레이에서 이미 사용 중입니다",
    "Imported from an externally started process":
        "외부에서 시작된 프로세스에서 가져왔습니다",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "krfb-virtualmonitor를 찾을 수 없습니다. krfb가 설치되어 있는지 "
        "확인하세요 ({path}에 있어야 합니다).",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "kscreen-doctor를 찾을 수 없어 가상 디스플레이의 실제 해상도와 "
        "배율을 다시 읽을 수 없습니다. 시작 확인은 포트 검사만으로 "
        "대체됩니다.",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor가 있지만 아무것도 출력하지 않습니다 (패키지 빌드가 "
        "번들 Qt6에 오염되어 abort된 적이 있습니다). 가상 디스플레이의 "
        "실제 해상도와 배율을 다시 읽을 수 없어 시작 확인은 포트 검사만으로 "
        "대체됩니다.",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Wayland 세션이지만 WAYLAND_DISPLAY가 설정되어 있지 않아 krfb가 "
        "가상 디스플레이를 만들 수 없습니다. 데스크톱 실행기나 터미널에서 "
        "이 프로그램을 시작하세요.",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Wayland 세션이 아닙니다. krfb의 가상 디스플레이에는 Wayland(와 "
        "KWin)가 필요하며, X11에서는 무조건 실패합니다.",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display}이(가) 가리키는 소켓이 없습니다 ({path}). "
        "krfb는 'Virtual Monitors are only supported on Wayland' 메시지와 "
        "함께 실패합니다.",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "systemd 유닛 {unit}(으)로 시작되었습니다. 이 유닛의 "
        "KillMode=control-group과 ExitType=main 때문에 이 프로그램을 "
        "종료하면 모든 가상 디스플레이도 함께 종료됩니다. 대신 데스크톱 "
        "실행기에서 실행하거나, 해당 유닛에 ExitType=cgroup을 추가하세요.",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "로그인할 때 '실행 원함'으로 표시된 가상 디스플레이 복원",
    "Cannot write {path}: {error}": "{path}에 쓸 수 없습니다: {error}",
    "Cannot delete {path}: {error}": "{path}을(를) 삭제할 수 없습니다: {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "시작할 때 트레이로 최소화 (자동 시작에서 사용)",
    "Config warning": "설정 경고",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor":
        "krfb-virtualmonitor 그래픽 관리자",
    "New virtual screen": "새 가상 디스플레이",
    "Start all": "모두 시작",
    "Stop all": "모두 중지",
    "Scan for and adopt krfb processes started outside this app":
        "이 앱 밖에서 시작된 krfb 프로세스를 검색해 가져오기",
    "Refresh now": "지금 새로 고침",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "기본 창 표시",
    "Quit": "종료",
    "Restart": "다시 시작",
    "View": "보기",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "창을 닫을까요, 트레이로 최소화할까요?",
    "Minimize to tray": "트레이로 최소화",
    "Quit the program": "프로그램 종료",
    "Remember my choice": "선택 기억하기",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "가상 디스플레이 {count}개",
    "{count} running": "{count}개 실행 중",
    "{count} need attention": "{count}개 확인 필요",
    "{count} environment problems": "환경 문제 {count}개",
    "{count} environment problems detected": "환경 문제 {count}개 발견",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "'{name}'이(가) 종료되었습니다. 충돌했거나 강제 종료되었을 수 있습니다",
    "{count} virtual screens have exited ({names}…)":
        "가상 디스플레이 {count}개가 종료되었습니다 ({names}…)",
    "The process exited immediately after starting":
        "시작 직후 프로세스가 종료되었습니다",
    " (the port is listening, but no virtual display was created)":
        " (포트는 수신 중이지만 가상 디스플레이가 만들어지지 않았습니다)",
    " (the port isn't listening either)": " (포트도 수신 중이 아닙니다)",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "{seconds}초를 기다렸지만 KWin에 Virtual-{name} 출력이 "
        "아직 나타나지 않았습니다{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "이 가상 디스플레이에는 저장된 비밀번호가 없습니다 "
        "(예전 설정에서 가져온 것일 수 있습니다). 지금 입력하세요.",
    "Cannot read the password from the keyring: {reason}":
        "키링에서 비밀번호를 읽을 수 없습니다: {reason}",
    "Keyring": "키링",
    "Unlocked. Passwords will be saved to the keyring.":
        "잠금을 해제했습니다. 비밀번호가 키링에 저장됩니다.",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "잠금 해제에 실패했거나 시간이 초과되었습니다. 비밀번호는 "
        "이번 세션에서는 계속 사용할 수 있지만, 종료 후에는 다시 "
        "입력해야 합니다.",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "다시 시작 필요",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "'{name}'이(가) 실행 중입니다. 해상도, 배율, 포트를 변경해도 "
        "이미 만들어진 화면에는 영향을 주지 않습니다. 적용하려면 "
        "가상 디스플레이를 다시 시작해야 합니다.",
    "Restart it now?": "지금 다시 시작할까요?",
    "Restart now": "지금 다시 시작",
    "Later": "나중에",
    "Delete virtual screen": "가상 디스플레이 삭제",
    "Delete \"{name}\"?": "'{name}'을(를) 삭제할까요?",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "이 가상 디스플레이는 현재 실행 중입니다. 삭제하면 먼저 중지됩니다.",
    "This action cannot be undone.": "이 작업은 되돌릴 수 없습니다.",
    "The saved password is removed from the keyring too.":
        "저장된 비밀번호도 키링에서 삭제됩니다.",
    "No unmanaged krfb processes found":
        "관리되지 않는 krfb 프로세스를 찾지 못했습니다",
    "{name}: {error}": "{name}: {error}",
    "Some could not be imported": "일부를 가져오지 못했습니다",
    "Start failed": "시작 실패",
    "\"{name}\" failed to start": "'{name}'을(를) 시작하지 못했습니다",
    "View full log": "전체 로그 보기",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "트레이로 최소화했습니다. 가상 디스플레이는 계속 실행되며, "
        "이 앱을 종료해도 중지되지 않습니다.",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left":
        "왼쪽에서 가상 디스플레이를 선택하세요",
    "or click \"New\" in the top right":
        "또는 오른쪽 위의 '새로 만들기'를 클릭하세요",
    "Requested": "요청값",
    "Actual": "실제값",
    "Address": "주소",
    "Status": "상태",
    "Copy the VNC address": "VNC 주소 복사",
    "Copy the connection password": "연결 비밀번호 복사",
    "Copied": "복사됨",
    "Start": "시작",
    "Stop": "중지",
    "Edit": "편집",
    "{actual}  ⚠ differs from the requested value":
        "{actual}  ⚠ 요청한 값과 다릅니다",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "비밀번호는 여기서 숨겨져 있을 뿐이며, krfb에는 평문으로 전달됩니다",
    "Running, PID {pid}": "실행 중, PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "프로세스는 사라졌지만 '실행 원함'으로 표시되어 있습니다",
    "It may have crashed, been killed, or the machine was rebooted":
        "충돌했거나 강제 종료되었거나, 시스템이 다시 시작되었을 수 있습니다",
    "Creating, waiting for the KWin output…":
        "만드는 중, KWin 출력을 기다리는 중…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "실행 중에 해상도나 배율을 변경해도 만들어진 화면에는 영향을 "
        "주지 않습니다. 가상 디스플레이를 다시 시작해야 합니다",
    "Edit parameters": "매개변수 편집",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · 포트 {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "아직 가상 디스플레이가 없습니다\n"
        "오른쪽 위의 '새로 만들기'를 클릭해 만드세요",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "가상 디스플레이 편집",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "예: Tablet (KWin 출력 'Virtual-<name>'이(가) 됩니다)",
    "Custom…": "사용자 지정…",
    "Auto": "자동",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "사용 중이 아니고 다른 가상 디스플레이에 할당되지도 않은 포트를 고르세요",
    "Show / hide the password": "비밀번호 표시 / 숨기기",
    "Copy the password": "비밀번호 복사",
    "Optional, e.g. \"second screen for the iPad\"":
        "선택 사항, 예: 'iPad용 보조 화면'",
    "Start at login": "로그인 시 시작",
    "Save": "저장",
    "Name": "이름",
    "Resolution": "해상도",
    "Scale DPR": "배율 DPR",
    "Command that will be executed": "실행될 명령",
    "The name can't be empty": "이름은 비워 둘 수 없습니다",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "'{name}'은(는) 이미 사용 중입니다 "
        "(KWin 출력 이름 Virtual-{name}은(는) 고유해야 합니다)",
    "Port {port} is already used by another virtual screen":
        "포트 {port}은(는) 다른 가상 디스플레이에서 사용 중입니다",
    "Port {port} is already taken by another program on the system":
        "포트 {port}은(는) 시스템의 다른 프로그램에서 사용 중입니다",
    "The password can't be empty": "비밀번호는 비워 둘 수 없습니다",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "VNC 인증은 처음 8자만 사용하므로 나머지 {extra}자는 "
        "아무 효과가 없습니다 (실제 비밀번호: {effective})",
    "VNC authentication uses all 8 characters":
        "VNC 인증은 8자를 모두 사용합니다",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "비밀번호 필요",
    "Enter the VNC password for this virtual screen":
        "이 가상 디스플레이의 VNC 비밀번호를 입력하세요",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "비밀번호는 평문으로 krfb 프로세스에 전달되므로 같은 시스템의 "
        "다른 사용자가 ps로 볼 수 있습니다. 또한 VNC 인증은 처음 8자만 "
        "사용합니다.",
    "Use": "사용",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found":
        "관리되지 않는 가상 디스플레이 발견",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "이 krfb-virtualmonitor 프로세스는 이 앱이 시작한 것이 아닙니다. "
        "가져오면 여기서 관리할 수 있습니다.",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · 포트 {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "알 수 없는 해상도",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ 패키지가 업그레이드되었습니다. "
        "이 가상 디스플레이를 다시 시작하는 것이 좋습니다</span>",
    "Import selected": "선택 항목 가져오기",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "언어",
    "Closing the window": "창을 닫을 때",
    "Ask every time": "매번 묻기",
    "Launch at login": "로그인 시 실행",
    "Start at login (tray mode)": "로그인 시 시작 (트레이 모드)",
    "Password storage": "비밀번호 저장",
    "Environment": "환경",
    "About": "정보",
    "No problems found": "문제를 찾지 못했습니다",
    "not installed": "설치되지 않음",
    "unknown": "알 수 없음",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "설정을 저장하지 못했습니다 ({error}). "
        "이번 세션 동안에만 적용됩니다.",
    "Config:": "설정:",
    "Runtime state:": "실행 상태:",
    "Logs:": "로그:",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "검색… (Enter 키로 다음 일치 항목)",
    "Auto-scroll": "자동 스크롤",
    "Reload": "다시 불러오기",
    "Open containing folder": "포함된 폴더 열기",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "(아직 출력 없음)\n\n"
        "가상 디스플레이를 시작할 때까지 여기는 비어 있습니다.",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines}줄   ·   {size}바이트",
    "No match for \"{needle}\"": "'{needle}'에 대한 일치 항목이 없습니다",
    "Refreshes every {seconds} s": "{seconds}초마다 새로 고침",

    # --- 密码库（多后端）----------------------------------------------------
    "KDE Wallet": "KDE 지갑",
    "System keyring (Secret Service)": "시스템 키링 (Secret Service)",
    "Built-in encrypted vault": "내장 암호화 금고",
    "Master password required": "마스터 비밀번호 필요",
    "No password vault yet": "아직 비밀번호 금고가 없습니다",
    "Enter the master password to unlock the built-in vault":
        "내장 암호화 금고의 잠금을 해제하려면 마스터 비밀번호를 입력하세요",
    "Set a master password to create the built-in vault":
        "마스터 비밀번호를 설정하면 내장 암호화 금고가 만들어집니다",
    "The store is disabled or does not exist":
        "저장소가 비활성화되었거나 존재하지 않습니다",
    "The store did not respond in time; passwords are kept in memory "
    "for this session only":
        "저장소가 제때 응답하지 않았습니다. 비밀번호는 "
        "이번 세션 동안에만 메모리에 보관됩니다",
    "already holds saved passwords": "저장된 비밀번호 있음",
    "locked; may hold saved passwords": "잠김, 저장된 비밀번호가 있을 수 있음",
    "available": "사용 가능",
    "always available": "항상 사용 가능",
    "selected in settings": "설정에서 선택됨",
    "write failed": "쓰기 실패",
    "read-back mismatch": "다시 읽은 값 불일치",
    "store is locked": "저장소가 잠겨 있습니다",
    "store is busy": "저장소가 사용 중입니다 (이전 호출이 아직 반환되지 않음)",
    "could not unlock the newly created vault":
        "새로 만든 금고의 잠금을 해제할 수 없습니다",
    "there is no vault": "금고가 없습니다",
    "wrong master password": "마스터 비밀번호가 올바르지 않습니다",
    "a vault already exists": "금고가 이미 존재합니다",
    "some entries could not be decrypted; nothing was changed":
        "일부 항목의 암호를 풀 수 없습니다. 아무것도 변경되지 않았습니다",
    "(currently unavailable)": "(현재 사용할 수 없음)",
    "Store:": "저장소:",
    "Detect again": "지금 다시 감지",
    "Using {backend}: the selected store is unavailable":
        "{backend} 사용 중: 선택한 저장소를 사용할 수 없습니다",
    "Master password": "마스터 비밀번호",
    "Current master password": "현재 마스터 비밀번호",
    "New master password": "새 마스터 비밀번호",
    "Repeat the password": "비밀번호 다시 입력",
    "Create": "만들기",
    "Change": "변경",
    "Unlock": "잠금 해제",
    "Unlocked": "잠금 해제됨",
    "Enter master password": "마스터 비밀번호 입력",
    "Set master password": "마스터 비밀번호 설정",
    "Change master password": "마스터 비밀번호 변경",
    "Create the built-in vault": "내장 암호화 금고 만들기",
    "Unlock the built-in vault": "내장 암호화 금고 잠금 해제",
    "Change the master password": "마스터 비밀번호 변경",
    "Use at least {count} characters": "{count}자 이상 사용하세요",
    "The two passwords do not match": "두 비밀번호가 일치하지 않습니다",
    "Enter the current master password":
        "현재 마스터 비밀번호를 입력하세요",
    "The built-in vault stores passwords encrypted. There is no way "
    "to recover them if you forget the master password.":
        "내장 암호화 금고는 비밀번호를 암호화하여 저장합니다. "
        "마스터 비밀번호를 잊으면 되찾을 방법이 없습니다.",
    "Enter the master password for the built-in vault.":
        "내장 암호화 금고의 마스터 비밀번호를 입력하세요.",
    "Changing the master password re-encrypts every password in the vault.":
        "마스터 비밀번호를 변경하면 금고에 있는 모든 비밀번호가 "
        "다시 암호화됩니다.",
    "Wrong master password": "마스터 비밀번호가 올바르지 않습니다",
    "Could not create the vault": "금고를 만들 수 없습니다",
    "The master password has been changed.": "마스터 비밀번호를 변경했습니다.",
    "Enter the master password to read saved passwords":
        "저장된 비밀번호를 읽으려면 마스터 비밀번호를 입력하세요",

    # --- 高危确认（验证码）--------------------------------------------------
    "Type the result here": "여기에 결과를 입력하세요",
    "Confirm": "확인",
    "{a} + {b} = ?": "{a} + {b} = ?",
    "Wrong answer, here is another one": "답이 틀렸습니다. 다른 문제를 냅니다",
    "Too many wrong answers": "틀린 답이 너무 많습니다",

    # --- 密码库告警与切换 ---------------------------------------------------
    "Password store": "비밀번호 저장소",
    "Password store unavailable": "비밀번호 저장소를 사용할 수 없음",
    "{store} holds {count} saved passwords but is unavailable right now.":
        "'{store}'에 저장된 비밀번호가 {count}개 있지만 "
        "지금은 사용할 수 없습니다.",
    "Enable it again in your system settings, or switch to another store — "
    "switching does not copy the old passwords over, and clearing the old "
    "store afterwards cannot be undone.":
        "시스템 설정에서 다시 활성화하거나 다른 저장소로 전환하세요 — "
        "전환해도 기존 비밀번호가 함께 복사되지 않으며, "
        "그 후 기존 저장소를 지우면 되돌릴 수 없습니다.",
    "Open settings": "설정 열기",
    "{store} is not available right now.":
        "'{store}'을(를) 지금 사용할 수 없습니다.",
    "The target store could not be unlocked.":
        "대상 저장소의 잠금을 해제할 수 없습니다.",
    "last updated {time}": "마지막 업데이트 {time}",
    "that store does not report timestamps":
        "그 저장소는 타임스탬프를 제공하지 않습니다",
    "Moving saved passwords…": "저장된 비밀번호를 옮기는 중…",
    "{count} passwords could not be moved:":
        "{count}개의 비밀번호를 옮기지 못했습니다:",
    "Retry the import before clearing the old store.":
        "기존 저장소를 지우기 전에 가져오기를 다시 시도하세요.",
    "Now using {store}": "'{store}'(으)로 전환했습니다",
    "Clear the old password store": "기존 비밀번호 저장소 지우기",
    "Delete the {count} passwords from {store}?":
        "'{store}'에서 비밀번호 {count}개를 삭제할까요?",
    "They are now stored in the new store. Deleting them here cannot be "
    "undone — and any other application that uses that store will no "
    "longer find them either.":
        "이제 새 저장소에 저장되어 있습니다. "
        "여기서 삭제하면 되돌릴 수 없으며, "
        "그 저장소를 사용하는 다른 프로그램에서도 찾을 수 없게 됩니다.",
    "Delete them": "삭제",
    "Deleted {count} passwords from the old store":
        "기존 저장소에서 비밀번호 {count}개를 삭제했습니다",

    # --- 内置库重置 ---------------------------------------------------------
    "Reset the built-in vault": "내장 암호화 금고 초기화",
    "This deletes every password stored in the built-in vault.":
        "내장 암호화 금고에 저장된 모든 비밀번호가 삭제됩니다.",
    "They cannot be recovered — not even with the master password. "
    "Only do this if you no longer need them.":
        "되돌릴 수 없습니다 — 마스터 비밀번호가 있어도 복구할 수 없습니다. "
        "더 이상 필요하지 않을 때만 실행하세요.",
    "Delete the vault": "금고 삭제",
    "The built-in vault has been reset": "내장 암호화 금고를 초기화했습니다",

    # --- 대상 저장소에 기존 데이터가 있을 때: 유지 / 덮어쓰기 / 병합 --------
    "{store} already holds {count} of this app's passwords ({when}).":
        "'{store}'에 이미 이 프로그램의 비밀번호가 {count}개 있습니다 "
        "({when}).",
    "{source} holds {moving} for the same screens. Whichever side you "
    "drop is deleted for good.":
        "'{source}'에도 같은 가상 디스플레이의 비밀번호가 {moving}개 "
        "있습니다. 어느 쪽을 버리든 그 쪽은 영구적으로 삭제됩니다.",
    "Keep the target's passwords": "대상 저장소의 비밀번호 유지",
    "Overwrite with the new passwords": "새 비밀번호로 덮어쓰기",
    "Merge…": "병합…",
    "Merge": "병합",
    "{adding} will be added, {identical} are identical and will be "
    "skipped, {conflicts} conflict.":
        "{adding}개는 추가되고, {identical}개는 동일하여 건너뛰고, "
        "{conflicts}개는 충돌합니다.",
    "Screens in conflict: {names}": "충돌하는 가상 디스플레이: {names}",
    "Keep the target's version": "대상 저장소의 버전 유지",
    "Use the new version": "새 버전 사용",
    "{count} entries could not be read; they will be left as they are.":
        "{count}개의 항목을 읽을 수 없습니다. "
        "해당 항목은 그대로 유지됩니다.",

    # --- 기존 저장소가 잠겨 있을 때: 하나도 옮기지 못한 경우 ---
    "The old store ({store}) is locked, so nothing was moved. "
    "Unlock it and switch again to bring the passwords over.":
        "기존 저장소('{store}')가 잠겨 있어 하나도 옮기지 못했습니다. "
        "잠금을 해제한 뒤 다시 전환하면 비밀번호를 가져올 수 있습니다.",
}
