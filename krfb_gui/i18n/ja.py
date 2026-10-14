"""日文词条表。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的日文。
`{named}` 占位符集合必须与键完全一致；引号写进词条本身（日文用「」），
命令名与程序原样输出不译。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "システムに合わせる",
    ", ": "、",  # join_list() 的列表分隔符
    "Cancel": "キャンセル",
    "Close": "閉じる",
    "Delete": "削除",
    "Log": "ログ",
    "Notes": "メモ",
    "Password": "パスワード",
    "Port": "ポート",
    "Random": "ランダム",
    "Settings": "設定",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Krfb 仮想ディスプレイマネージャー",
    "3:2 Tablet": "3:2 タブレット",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "krfb-virtualmonitor の仮想ディスプレイをグラフィカルに管理",

    # --- models -------------------------------------------------------------
    "Running": "実行中",
    "Stopped": "停止",
    "Exited unexpectedly": "異常終了",
    "Starting": "起動中",
    "Failed to start": "起動失敗",
    "Unmanaged": "未管理",
    "Unnamed": "名前なし",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "キーリングの準備完了",
    "Keyring locked": "キーリングがロック中",
    "No keyring service found": "キーリングサービスが見つかりません",
    "Keyring unavailable": "キーリングを利用できません",
    "Keyring not responding": "キーリングが応答しません",
    "Keyring error": "キーリングエラー",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "KDE ウォレットが閉じられています。パスワードは今回のセッションの間だけメモリに保持されます",
    "kwalletd is not running on the session bus":
        "セッションバスに kwalletd がありません",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "設定ファイルを解析できません: {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "設定のバージョン {found} が想定された {expected} と一致しません。"
        "できる範囲で読み込みました",
    "Unrecognized config format: {path}":
        "設定形式を認識できません: {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "krfb-virtualmonitor が見つかりません（{path} に存在するはずです）",
    "No password available": "利用できるパスワードがありません",
    "Port {port} is already in use": "ポート {port} はすでに使用されています",
    "Failed to start: {error}": "起動に失敗: {error}",
    "The process vanished immediately after starting":
        "起動直後にプロセスが消えました",
    "The name \"{name}\" is already taken by a managed screen":
        "名前「{name}」は管理対象の仮想ディスプレイで既に使われています",
    "Port {port} is already taken by a managed screen":
        "ポート {port} は管理対象の仮想ディスプレイで既に使われています",
    "Imported from an externally started process":
        "外部で起動されたプロセスからインポートしました",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "krfb-virtualmonitor が見つかりません。krfb がインストールされているか"
        "確認してください（{path} に存在するはずです）。",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "kscreen-doctor が見つからないため、仮想ディスプレイの実際の"
        "解像度と拡大率を読み戻せません。起動確認はポートのチェックのみに"
        "縮退します。",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor は存在しますが何も出力しません（パッケージ版では"
        "同梱の Qt6 に汚染されて abort したことがあります）。仮想ディスプレイの"
        "実際の解像度と拡大率を読み戻せないため、起動確認はポートの"
        "チェックのみに縮退します。",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Wayland セッションですが WAYLAND_DISPLAY が設定されていないため、"
        "krfb は仮想ディスプレイを作成できません。デスクトップランチャーか"
        "端末から本プログラムを起動してください。",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Wayland セッションではありません。krfb の仮想ディスプレイには "
        "Wayland（および KWin）が必要で、X11 では必ず失敗します。",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} が指すソケットが存在しません（{path}）。"
        "krfb は「Virtual Monitors are only supported on Wayland」で失敗します。",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "systemd ユニット {unit} から起動されています。その "
        "KillMode=control-group と ExitType=main により、このプログラムを"
        "終了するとすべての仮想ディスプレイも一緒に終了します。"
        "代わりにデスクトップランチャーから起動するか、そのユニットに "
        "ExitType=cgroup を追加してください。",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "ログイン時に「実行を希望」とマークされた仮想ディスプレイを復元する",
    "Cannot write {path}: {error}": "{path} に書き込めません: {error}",
    "Cannot delete {path}: {error}": "{path} を削除できません: {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "起動時にトレイへ最小化（自動起動で使用）",
    "Config warning": "設定の警告",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor":
        "krfb-virtualmonitor のグラフィカルマネージャー",
    "New virtual screen": "新規仮想ディスプレイ",
    "Start all": "すべて開始",
    "Stop all": "すべて停止",
    "Scan for and adopt krfb processes started outside this app":
        "このアプリの外部で起動された krfb プロセスをスキャンして引き継ぐ",
    "Refresh now": "今すぐ更新",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "メインウィンドウを表示",
    "Quit": "終了",
    "Restart": "再起動",
    "View": "表示",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "ウィンドウを閉じますか、それともトレイに最小化しますか？",
    "Minimize to tray": "トレイに最小化",
    "Quit the program": "プログラムを終了",
    "Remember my choice": "選択を記憶する",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "仮想ディスプレイ {count} 台",
    "{count} running": "{count} 台が実行中",
    "{count} need attention": "{count} 台が要対応",
    "{count} environment problems": "環境問題 {count} 件",
    "{count} environment problems detected": "環境問題を {count} 件検出しました",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "「{name}」が終了しました。クラッシュしたか、強制終了された可能性があります",
    "{count} virtual screens have exited ({names}…)":
        "{count} 台の仮想ディスプレイが終了しました（{names}…）",
    "The process exited immediately after starting":
        "起動直後にプロセスが終了しました",
    " (the port is listening, but no virtual display was created)":
        "（ポートは待ち受けていますが、仮想ディスプレイは作成されていません）",
    " (the port isn't listening either)": "（ポートも待ち受けていません）",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "{seconds} 秒待ちましたが、KWin に Virtual-{name} 出力が"
        "まだ現れません{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "この仮想ディスプレイには保存されたパスワードがありません"
        "（古い設定から引き継がれた可能性があります）。ここで入力してください。",
    "Cannot read the password from the keyring: {reason}":
        "キーリングからパスワードを読み取れません: {reason}",
    "Keyring": "キーリング",
    "Unlocked. Passwords will be saved to the keyring.":
        "ロックを解除しました。パスワードはキーリングに保存されます。",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "ロック解除に失敗したか、タイムアウトしました。パスワードは"
        "今回のセッションでは引き続き使用できますが、終了後に再入力が必要です。",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "再起動が必要",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "「{name}」は実行中です。解像度、拡大率、ポートの変更は"
        "すでに作成されたディスプレイには反映されません。"
        "反映するには仮想ディスプレイを再起動する必要があります。",
    "Restart it now?": "今すぐ再起動しますか？",
    "Restart now": "今すぐ再起動",
    "Later": "後で",
    "Delete virtual screen": "仮想ディスプレイを削除",
    "Delete \"{name}\"?": "「{name}」を削除しますか？",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "この仮想ディスプレイは現在実行中です。削除すると先に停止されます。",
    "This action cannot be undone.": "この操作は元に戻せません。",
    "The saved password is removed from the keyring too.":
        "保存されたパスワードもキーリングから削除されます。",
    "No unmanaged krfb processes found":
        "管理対象外の krfb プロセスは見つかりませんでした",
    "{name}: {error}": "{name}: {error}",
    "Some could not be imported": "一部はインポートできませんでした",
    "Start failed": "起動失敗",
    "\"{name}\" failed to start": "「{name}」の起動に失敗しました",
    "View full log": "完全なログを表示",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "トレイに最小化しました。仮想ディスプレイは動作を続け、"
        "このアプリを終了しても停止しません。",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left":
        "左側から仮想ディスプレイを選択してください",
    "or click \"New\" in the top right": "または右上の「新規」をクリックしてください",
    "Requested": "要求値",
    "Actual": "実際値",
    "Address": "アドレス",
    "Status": "状態",
    "Copy the VNC address": "VNC アドレスをコピー",
    "Copy the connection password": "接続パスワードをコピー",
    "Copied": "コピーしました",
    "Start": "開始",
    "Stop": "停止",
    "Edit": "編集",
    "{actual}  ⚠ differs from the requested value": "{actual}  ⚠ 要求値と異なります",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "パスワードはここで非表示になっているだけです。"
        "krfb には平文で渡されます",
    "Running, PID {pid}": "実行中、PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "プロセスは消えていますが「実行を希望」とマークされています",
    "It may have crashed, been killed, or the machine was rebooted":
        "クラッシュしたか、強制終了されたか、マシンが再起動された可能性があります",
    "Creating, waiting for the KWin output…": "作成中、KWin の出力を待機しています…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "実行中に解像度や拡大率を変更しても、作成済みのディスプレイには"
        "反映されません。仮想ディスプレイの再起動が必要です",
    "Edit parameters": "パラメーターを編集",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · ポート {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "仮想ディスプレイはまだありません\n"
        "右上の「新規」をクリックして作成してください",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "仮想ディスプレイを編集",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "例: Tablet（KWin の出力「Virtual-<name>」になります）",
    "Custom…": "カスタム…",
    "Auto": "自動",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "使用中でも、他の仮想ディスプレイに割り当て済みでもないポートを選んでください",
    "Show / hide the password": "パスワードの表示 / 非表示",
    "Copy the password": "パスワードをコピー",
    "Optional, e.g. \"second screen for the iPad\"":
        "任意。例:「iPad 用のセカンドスクリーン」",
    "Start at login": "ログイン時に起動",
    "Save": "保存",
    "Name": "名前",
    "Resolution": "解像度",
    "Scale DPR": "拡大率 DPR",
    "Command that will be executed": "実行されるコマンド",
    "The name can't be empty": "名前を空にすることはできません",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "「{name}」はすでに使用されています"
        "（KWin の出力名 Virtual-{name} は一意でなければなりません）",
    "Port {port} is already used by another virtual screen":
        "ポート {port} は別の仮想ディスプレイで使用されています",
    "Port {port} is already taken by another program on the system":
        "ポート {port} はシステム上の他のプログラムで使用されています",
    "The password can't be empty": "パスワードを空にすることはできません",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "VNC 認証は最初の 8 文字のみを使用し、残りの {extra} 文字は"
        "効果がありません（実際に有効なパスワード: {effective}）",
    "VNC authentication uses all 8 characters":
        "VNC 認証は 8 文字すべてを使用します",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "パスワードが必要",
    "Enter the VNC password for this virtual screen":
        "この仮想ディスプレイの VNC パスワードを入力してください",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "パスワードは平文で krfb プロセスに渡されるため、同じマシンの"
        "他のユーザーが ps で見ることができます。また、VNC 認証は"
        "最初の 8 文字のみを使用します。",
    "Use": "使用",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found":
        "管理対象外の仮想ディスプレイが見つかりました",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "これらの krfb-virtualmonitor プロセスはこのアプリが起動したものでは"
        "ありません。インポートするとここで管理できます。",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · ポート {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "解像度不明",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ パッケージが更新されました。"
        "この仮想ディスプレイを再起動することをおすすめします</span>",
    "Import selected": "選択したものをインポート",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "言語",
    "Closing the window": "ウィンドウを閉じたとき",
    "Ask every time": "毎回確認",
    "Launch at login": "ログイン時に起動",
    "Start at login (tray mode)": "ログイン時に起動（トレイモード）",
    "Password storage": "パスワードの保存",
    "Environment": "環境",
    "About": "このアプリについて",
    "No problems found": "問題は見つかりませんでした",
    "not installed": "未インストール",
    "unknown": "不明",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "設定を保存できませんでした（{error}）。"
        "今回のセッションの間だけ有効です。",
    "Config:": "設定:",
    "Runtime state:": "実行状態:",
    "Logs:": "ログ:",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "検索…（Enter で次の一致へ移動）",
    "Auto-scroll": "自動スクロール",
    "Reload": "再読み込み",
    "Open containing folder": "格納フォルダーを開く",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "（まだ出力はありません）\n\n"
        "仮想ディスプレイを起動するまで、ここは空です。",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} 行   ·   {size} バイト",
    "No match for \"{needle}\"": "「{needle}」に一致するものはありません",
    "Refreshes every {seconds} s": "{seconds} 秒ごとに更新",

    # --- 密码库（多后端）----------------------------------------------------
    "KDE Wallet": "KDE ウォレット",
    "System keyring (Secret Service)": "システムキーリング（Secret Service）",
    "Built-in encrypted vault": "内蔵の暗号化保管庫",
    "Master password required": "マスターパスワードが必要",
    "No password vault yet": "パスワード保管庫はまだありません",
    "Enter the master password to unlock the built-in vault":
        "マスターパスワードを入力して内蔵の暗号化保管庫のロックを解除してください",
    "Set a master password to create the built-in vault":
        "マスターパスワードを設定すると内蔵の暗号化保管庫を作成できます",
    "The store is disabled or does not exist":
        "ストアが無効になっているか、存在しません",
    "The store did not respond in time; passwords are kept in memory "
    "for this session only":
        "ストアが時間内に応答しませんでした。パスワードは"
        "今回のセッションの間だけメモリに保持されます",
    "already holds saved passwords": "保存されたパスワードあり",
    "locked; may hold saved passwords": "ロック中、保存されたパスワードの可能性あり",
    "available": "利用可能",
    "always available": "常に利用可能",
    "selected in settings": "設定で選択中",
    "write failed": "書き込み失敗",
    "read-back mismatch": "読み戻しが一致しません",
    "store is locked": "ストアがロックされています",
    "store is busy": "ストアが使用中です（前回の呼び出しがまだ戻っていません）",
    "could not unlock the newly created vault":
        "新しく作成した保管庫のロックを解除できませんでした",
    "there is no vault": "保管庫がありません",
    "wrong master password": "マスターパスワードが正しくありません",
    "a vault already exists": "保管庫は既に存在します",
    "some entries could not be decrypted; nothing was changed":
        "一部のエントリを復号できませんでした。何も変更されていません",
    "(currently unavailable)": "（現在利用できません）",
    "Store:": "ストア:",
    "Detect again": "今すぐ再検出",
    "Using {backend}: the selected store is unavailable":
        "{backend} を使用中: 選択したストアを利用できません",
    "Master password": "マスターパスワード",
    "Current master password": "現在のマスターパスワード",
    "New master password": "新しいマスターパスワード",
    "Repeat the password": "パスワードをもう一度入力",
    "Create": "作成",
    "Change": "変更",
    "Unlock": "ロック解除",
    "Unlocked": "ロック解除済み",
    "Enter master password": "マスターパスワードを入力",
    "Set master password": "マスターパスワードを設定",
    "Change master password": "マスターパスワードを変更",
    "Create the built-in vault": "内蔵の暗号化保管庫を作成",
    "Unlock the built-in vault": "内蔵の暗号化保管庫のロックを解除",
    "Change the master password": "マスターパスワードを変更",
    "Use at least {count} characters": "{count} 文字以上で入力してください",
    "The two passwords do not match": "2 つのパスワードが一致しません",
    "Enter the current master password":
        "現在のマスターパスワードを入力してください",
    "The built-in vault stores passwords encrypted. There is no way "
    "to recover them if you forget the master password.":
        "内蔵の暗号化保管庫はパスワードを暗号化して保存します。"
        "マスターパスワードを忘れると、復元する方法はありません。",
    "Enter the master password for the built-in vault.":
        "内蔵の暗号化保管庫のマスターパスワードを入力してください。",
    "Changing the master password re-encrypts every password in the vault.":
        "マスターパスワードを変更すると、保管庫内のすべての"
        "パスワードが再暗号化されます。",
    "Wrong master password": "マスターパスワードが正しくありません",
    "Could not create the vault": "保管庫を作成できませんでした",
    "The master password has been changed.": "マスターパスワードを変更しました。",
    "Enter the master password to read saved passwords":
        "保存されたパスワードを読み取るにはマスターパスワードを入力してください",

    # --- 高危确认（验证码）--------------------------------------------------
    "Type the result here": "ここに答えを入力",
    "Confirm": "確認",
    "{a} + {b} = ?": "{a} + {b} = ?",
    "Wrong answer, here is another one": "答えが違います。別の問題を出します",
    "Too many wrong answers": "間違いが続いたため、キャンセルしました",

    # --- 密码库告警与切换 ---------------------------------------------------
    "Password store": "パスワードストア",
    "Password store unavailable": "パスワードストアを利用できません",
    "{store} holds {count} saved passwords but is unavailable right now.":
        "「{store}」に保存されたパスワードが {count} 件ありますが、"
        "現在利用できません。",
    "Enable it again in your system settings, or switch to another store — "
    "switching does not copy the old passwords over, and clearing the old "
    "store afterwards cannot be undone.":
        "システム設定で再度有効にするか、別のストアに切り替えてください — "
        "切り替えても古いパスワードは引き継がれず、"
        "その後に古いストアを消去すると元に戻せません。",
    "Open settings": "設定を開く",
    "{store} is not available right now.": "「{store}」は現在利用できません。",
    "The target store could not be unlocked.":
        "切り替え先のストアのロックを解除できませんでした。",
    "last updated {time}": "最終更新 {time}",
    "that store does not report timestamps":
        "そのストアはタイムスタンプを提供しません",
    "Moving saved passwords…": "保存されたパスワードを移動しています…",
    "{count} passwords could not be moved:":
        "{count} 件のパスワードを移動できませんでした:",
    "Retry the import before clearing the old store.":
        "古いストアを消去する前に、インポートを再試行してください。",
    "Now using {store}": "「{store}」に切り替えました",
    "Clear the old password store": "古いパスワードストアを消去",
    "Delete the {count} passwords from {store}?":
        "「{store}」から {count} 件のパスワードを削除しますか？",
    "They are now stored in the new store. Deleting them here cannot be "
    "undone — and any other application that uses that store will no "
    "longer find them either.":
        "これらは新しいストアに保存されています。"
        "ここで削除すると元に戻せません — "
        "また、そのストアを使う他のアプリからも見つからなくなります。",
    "Delete them": "削除する",
    "Deleted {count} passwords from the old store":
        "古いストアから {count} 件のパスワードを削除しました",

    # --- 内置库重置 ---------------------------------------------------------
    "Reset the built-in vault": "内蔵の暗号化保管庫をリセット",
    "This deletes every password stored in the built-in vault.":
        "内蔵の暗号化保管庫に保存されているすべてのパスワードが削除されます。",
    "They cannot be recovered — not even with the master password. "
    "Only do this if you no longer need them.":
        "元に戻せません — マスターパスワードがあっても復元できません。"
        "もう必要ない場合にのみ実行してください。",
    "Delete the vault": "保管庫を削除",
    "The built-in vault has been reset": "内蔵の暗号化保管庫をリセットしました",

    # --- 切り替え先に既存データがある場合：残す / 上書き / マージ -----------
    "{store} already holds {count} of this app's passwords ({when}).":
        "「{store}」には本アプリのパスワードがすでに {count} 件あります"
        "（{when}）。",
    "{source} holds {moving} for the same screens. Whichever side you "
    "drop is deleted for good.":
        "「{source}」にも同じ仮想ディスプレイのパスワードが "
        "{moving} 件あります。破棄した側は完全に削除され、"
        "元に戻せません。",
    "Keep the target's passwords": "切り替え先のパスワードを残す",
    "Overwrite with the new passwords": "新しいパスワードで上書き",
    "Merge…": "マージ…",
    "Merge": "マージ",
    "{adding} will be added, {identical} are identical and will be "
    "skipped, {conflicts} conflict.":
        "{adding} 件は追加され、{identical} 件は同一のためスキップされ、"
        "{conflicts} 件が競合します。",
    "Screens in conflict: {names}":
        "競合している仮想ディスプレイ: {names}",
    "Keep the target's version": "切り替え先のものを残す",
    "Use the new version": "新しいほうを使う",
    "{count} entries could not be read; they will be left as they are.":
        "エントリ {count} 件を読み取れませんでした。"
        "これらはそのまま残されます。",

    # --- 元のストアがロック中：1 件も移動できなかった場合 ---
    "The old store ({store}) is locked, so nothing was moved. "
    "Unlock it and switch again to bring the passwords over.":
        "古いストア「{store}」はロックされているため、"
        "1 件も移動できませんでした。"
        "ロックを解除してからもう一度切り替えると、"
        "パスワードを引き継げます。",
}
