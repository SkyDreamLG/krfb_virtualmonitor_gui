"""繁體中文（台灣）詞條表。

鍵是**英文原文**（`i18n.tr()` 的 key），值是要顯示的繁體中文。
按源文件分節，與 zh_cn.py 的鍵完全一致、順序相同，方便對照。

用語依台灣習慣：設定／螢幕／連接埠／行程／系統匣／金鑰圈／儲存／匯入。
約定：
  * 值是整句，`{named}` 佔位符集合必須與鍵完全一致（tests/test_i18n.py 會校驗）；
  * 引號寫進詞條本身 —— 中文用「」，英文原文用直引號；
  * 不收錄：命令列預覽、`vnc://host:port`、KWin 輸出名、引用的 krfb 英文原樣輸出。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "跟隨系統",
    ", ": "、",  # join_list() 的列表分隔符
    "Cancel": "取消",
    "Close": "關閉",
    "Delete": "刪除",
    "Log": "日誌",
    "Notes": "備註",
    "Password": "密碼",
    "Port": "連接埠",
    "Random": "隨機",
    "Settings": "設定",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Krfb 虛擬螢幕管理員",
    "3:2 Tablet": "3:2 平板",
    # 應用程式選單項目的描述，由 packaging/install-desktop.sh 寫進 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "圖形化管理 krfb-virtualmonitor 虛擬顯示器",

    # --- models -------------------------------------------------------------
    "Running": "執行中",
    "Stopped": "已停止",
    "Exited unexpectedly": "異常結束",
    "Starting": "啟動中",
    "Failed to start": "啟動失敗",
    "Unmanaged": "未受管理",
    "Unnamed": "未命名",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "金鑰圈已就緒",
    "Keyring locked": "金鑰圈已鎖定",
    "No keyring service found": "找不到金鑰圈服務",
    "Keyring unavailable": "金鑰圈無法使用",
    "Keyring not responding": "金鑰圈沒有回應",
    "Keyring error": "金鑰圈發生錯誤",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "KDE 錢包未解鎖，密碼僅暫存於本次工作階段的記憶體",
    "kwalletd is not running on the session bus":
        "工作階段匯流排上沒有 kwalletd",
    "The KDE wallet subsystem is disabled, or no wallet exists":
        "KDE 錢包子系統已關閉，或沒有可用的錢包",
    "The wallet did not respond in time; passwords are kept in "
    "memory for this session only":
        "錢包沒有回應，密碼僅暫存於本次工作階段的記憶體",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "無法解析設定檔：{path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "設定版本 {found} 與程式預期的 {expected} 不一致，已盡力讀取",
    "Unrecognized config format: {path}":
        "無法辨識設定檔格式：{path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "找不到 krfb-virtualmonitor（預期路徑 {path}）",
    "No password available": "沒有可用的密碼",
    "Port {port} is already in use": "連接埠 {port} 已被佔用",
    "Failed to start: {error}": "啟動失敗：{error}",
    "The process vanished immediately after starting": "行程啟動後立刻消失",
    "The name \"{name}\" is already taken by a managed screen":
        "名稱「{name}」已被受管理的螢幕佔用",
    "Port {port} is already taken by a managed screen":
        "連接埠 {port} 已被受管理的螢幕佔用",
    "Imported from an externally started process": "由外部命令列啟動，已匯入管理",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "找不到 krfb-virtualmonitor，請確認已安裝 krfb（預期路徑 {path}）。",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "找不到 kscreen-doctor，無法讀回虛擬螢幕的真實解析度與縮放，"
        "啟動成功判定會退化為只檢查連接埠。",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor 存在但讀不到任何輸出（打包版曾因內附的 Qt6 汙染而"
        "直接 abort），無法讀回虛擬螢幕的真實解析度與縮放，"
        "啟動成功判定會退化為只檢查連接埠。",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "目前是 Wayland 工作階段但沒有 WAYLAND_DISPLAY 環境變數，"
        "krfb 無法建立虛擬顯示器。請從桌面啟動器或終端機執行本程式。",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "目前不是 Wayland 工作階段。krfb 的虛擬顯示器僅支援 Wayland"
        "（且需要 KWin），在 X11 下會直接失敗。",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} 指向的 socket 不存在（{path}），"
        "krfb 會以「Virtual Monitors are only supported on Wayland」失敗。",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "目前由 systemd 單元 {unit} 啟動，其 KillMode=control-group 且 "
        "ExitType=main —— 結束本程式會連帶終止所有虛擬螢幕。"
        "請改從桌面啟動器執行，或為該單元加上 ExitType=cgroup。",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "登入時自動還原標記為「期望執行」的虛擬螢幕",
    "Cannot write {path}: {error}": "無法寫入 {path}：{error}",
    "Cannot delete {path}: {error}": "無法刪除 {path}：{error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "啟動後直接最小化到系統匣（供開機自動啟動使用）",
    "Config warning": "設定讀取警告",

    # --- ui/main_window: 標題列與工具列 --------------------------------------
    "Graphical manager for krfb-virtualmonitor": "krfb-virtualmonitor 圖形化管理員",
    "New virtual screen": "新增虛擬螢幕",
    "Start all": "全部啟動",
    "Stop all": "全部停止",
    "Scan for and adopt krfb processes started outside this app":
        "掃描並接管由本程式之外啟動的 krfb 行程",
    "Refresh now": "立即重新整理",

    # --- ui/main_window: 系統匣選單與通知列 ----------------------------------
    "Show main window": "顯示主視窗",
    "Quit": "結束",
    "Restart": "重新啟動",
    "View": "檢視",

    # --- ui/main_window: 關閉視窗時的詢問視窗 --------------------------------
    "Close the window or minimize to the tray?":
        "要關閉視窗，還是最小化到系統匣？",
    "Minimize to tray": "最小化到系統匣",
    "Quit the program": "結束程式",
    "Remember my choice": "記住我的選擇",

    # --- ui/main_window: 狀態列 ---------------------------------------------
    "{count} virtual screens": "共 {count} 個虛擬螢幕",
    "{count} running": "{count} 個執行中",
    "{count} need attention": "{count} 個需要處理",
    "{count} environment problems": "{count} 項環境問題",
    "{count} environment problems detected": "偵測到 {count} 項環境問題",

    # --- ui/main_window: 異常結束橫幅與啟動校驗 ------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "「{name}」已結束，可能當掉或被手動結束",
    "{count} virtual screens have exited ({names}…)":
        "{count} 個虛擬螢幕已結束（{names}…）",
    "The process exited immediately after starting": "行程啟動後立即結束",
    " (the port is listening, but no virtual display was created)":
        "（連接埠已監聽，但虛擬顯示器未建立）",
    " (the port isn't listening either)": "（連接埠也未監聽）",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "等待 {seconds} 秒後仍未在 KWin 中出現 Virtual-{name} 輸出{detail}",

    # --- ui/main_window: 密碼與金鑰圈 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "這個虛擬螢幕還沒有儲存密碼（可能是從舊設定匯入的），請補登一次。",
    "Cannot read the password from the keyring: {reason}":
        "無法從金鑰圈讀取密碼：{reason}",
    "Keyring": "金鑰圈",
    "Unlocked. Passwords will be saved to the keyring.":
        "已解鎖，密碼將儲存到金鑰圈。",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "解鎖失敗或逾時。密碼仍可在本次工作階段中使用，但結束後需要重新輸入。",

    # --- ui/main_window: 編輯 / 刪除 / 日誌 ----------------------------------
    "Restart required": "需要重新啟動",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "「{name}」正在執行。解析度、縮放或連接埠的變更"
        "不會影響已經建立好的螢幕，需要重新啟動該虛擬螢幕才能生效。",
    "Restart it now?": "要現在重新啟動嗎？",
    "Restart now": "立即重新啟動",
    "Later": "稍後",
    "Delete virtual screen": "刪除虛擬螢幕",
    "Delete \"{name}\"?": "確定要刪除「{name}」嗎？",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "這個虛擬螢幕目前正在執行，刪除會先停止它。",
    "This action cannot be undone.": "此操作無法復原。",
    "The saved password is removed from the keyring too.":
        "已儲存的密碼也會一併從金鑰圈移除。",
    "No unmanaged krfb processes found": "沒有發現未受管理的 krfb 行程",
    "{name}: {error}": "{name}：{error}",
    "Some could not be imported": "部分項目無法匯入",
    "Start failed": "啟動失敗",
    "\"{name}\" failed to start": "「{name}」啟動失敗",
    "View full log": "檢視完整日誌",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "已最小化到系統匣。虛擬螢幕會繼續執行，結束本程式也不會停止它們。",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left": "從左側選擇一個虛擬螢幕",
    "or click \"New\" in the top right": "或點擊右上角「新增」建立",
    "Requested": "要求",
    "Actual": "實際生效",
    "Address": "連線位址",
    "Status": "狀態",
    "Copy the VNC address": "複製 VNC 連線位址",
    "Copy the connection password": "複製連線密碼",
    "Copied": "已複製",
    "Start": "啟動",
    "Stop": "停止",
    "Edit": "編輯",
    "{actual}  ⚠ differs from the requested value": "{actual}  ⚠ 與要求值不符",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "密碼只在這裡隱藏顯示；實際以明文傳給 krfb 行程",
    "Running, PID {pid}": "執行中，PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "行程已消失，但標記為「期望執行」",
    "It may have crashed, been killed, or the machine was rebooted":
        "可能當掉、被手動終止，或電腦曾重新開機",
    "Creating, waiting for the KWin output…": "正在建立，等待 KWin 輸出…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "執行中變更解析度或縮放不會影響已建立的螢幕，需要重新啟動該虛擬螢幕",
    "Edit parameters": "編輯參數",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · 連接埠 {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "還沒有虛擬螢幕\n點擊右上角「新增」建立第一個",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "編輯虛擬螢幕",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "例如 Tablet（會成為 KWin 的 Virtual-<名稱> 輸出）",
    "Custom…": "自訂…",
    "Auto": "自動",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "找一個未被佔用、也沒被其他虛擬螢幕使用的連接埠",
    "Show / hide the password": "顯示 / 隱藏密碼",
    "Copy the password": "複製密碼",
    "Optional, e.g. \"second screen for the iPad\"":
        "選填，例如「給 iPad 當副螢幕」",
    "Start at login": "登入時自動啟動",
    "Save": "儲存",
    "Name": "名稱",
    "Resolution": "解析度",
    "Scale DPR": "縮放 DPR",
    "Command that will be executed": "將要執行的命令",
    "The name can't be empty": "名稱不能為空",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "「{name}」已被使用（KWin 輸出名稱 Virtual-{name} 必須唯一）",
    "Port {port} is already used by another virtual screen":
        "連接埠 {port} 已被另一個虛擬螢幕使用",
    "Port {port} is already taken by another program on the system":
        "連接埠 {port} 已被系統中的其他程式佔用",
    "The password can't be empty": "密碼不能為空",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "VNC 驗證只使用前 8 個字元，後 {extra} 個字元不產生任何作用"
        "（實際生效：{effective}）",
    "VNC authentication uses all 8 characters": "VNC 驗證使用全部 8 個字元",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "需要密碼",
    "Enter the VNC password for this virtual screen":
        "輸入這個虛擬螢幕的 VNC 連線密碼",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "密碼會以明文傳給 krfb 行程，因此本機其他使用者可透過 ps 看到；"
        "且 VNC 驗證只使用前 8 個字元。",
    "Use": "使用",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found": "發現未受管理的虛擬螢幕",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "以下 krfb-virtualmonitor 行程不是由本程式啟動的，匯入後即可在這裡統一管理。",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · 連接埠 {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "未知解析度",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ 程式套件已升級，"
        "建議改為重新啟動此虛擬螢幕</span>",
    "Import selected": "匯入選取的",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "語言",
    "Closing the window": "關閉視窗時",
    "Ask every time": "每次都詢問",
    "Launch at login": "開機自動啟動",
    "Start at login (tray mode)": "登入時自動啟動（系統匣模式）",
    "Password storage": "密碼儲存",
    "Unlock keyring": "解鎖金鑰圈",
    "Environment": "環境檢查",
    "About": "關於",
    "No problems found": "未發現問題",
    "not installed": "未安裝",
    "unknown": "未知",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "偏好設定儲存失敗（{error}）；本次工作階段內仍然生效。",
    "Config:": "設定：",
    "Runtime state:": "執行狀態：",
    "Logs:": "日誌：",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "搜尋…（按 Enter 跳至下一個相符項）",
    "Auto-scroll": "自動捲動",
    "Reload": "重新載入",
    "Open containing folder": "開啟所在資料夾",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "（尚無輸出）\n\n虛擬螢幕還沒啟動前，這裡會是空的。",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} 行   ·   {size} 位元組",
    "No match for \"{needle}\"": "找不到「{needle}」",
    "Refreshes every {seconds} s": "每 {seconds} 秒重新整理一次",
}
