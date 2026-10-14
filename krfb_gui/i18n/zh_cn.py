"""简体中文词条表。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的中文。
按源文件分节，尽量与源码顺序一致，方便对照增删。

约定：
  * 值是整句，`{named}` 占位符集合必须与键完全一致（tests/test_i18n.py 会校验）；
  * 引号写进词条本身 —— 中文用「」，英文原文用直引号；
  * 不收录：命令行预览、`vnc://host:port`、KWin 输出名、引用的 krfb 英文原样输出。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "跟随系统",
    ", ": "、",  # join_list() 的列表分隔符
    "Cancel": "取消",
    "Close": "关闭",
    "Delete": "删除",
    "Log": "日志",
    "Notes": "备注",
    "Password": "密码",
    "Port": "端口",
    "Random": "随机",
    "Settings": "设置",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Krfb 虚拟屏管理器",
    "3:2 Tablet": "3:2 平板",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "图形化管理 krfb-virtualmonitor 虚拟显示器",

    # --- models -------------------------------------------------------------
    "Running": "运行中",
    "Stopped": "已停止",
    "Exited unexpectedly": "异常退出",
    "Starting": "启动中",
    "Failed to start": "启动失败",
    "Unmanaged": "未托管",
    "Unnamed": "未命名",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "密钥环已就绪",
    "Keyring locked": "密钥环已锁定",
    "No keyring service found": "未找到密钥环服务",
    "Keyring unavailable": "密钥环不可用",
    "Keyring not responding": "密钥环无响应",
    "Keyring error": "密钥环出错",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "KDE 钱包未解锁，密码暂存本次会话内存",
    "kwalletd is not running on the session bus":
        "会话总线上没有 kwalletd",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "配置文件无法解析：{path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "配置版本 {found} 与程序预期的 {expected} 不一致，已尽力读取",
    "Unrecognized config format: {path}":
        "配置格式无法识别：{path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "找不到 krfb-virtualmonitor（期望路径 {path}）",
    "No password available": "没有可用的密码",
    "Port {port} is already in use": "端口 {port} 已被占用",
    "Failed to start: {error}": "启动失败：{error}",
    "The process vanished immediately after starting": "进程启动后立刻消失",
    "The name \"{name}\" is already taken by a managed screen":
        "名称「{name}」已被管理的虚拟屏占用",
    "Port {port} is already taken by a managed screen":
        "端口 {port} 已被管理的虚拟屏占用",
    "Imported from an externally started process": "由外部命令行启动，已导入管理",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "找不到 krfb-virtualmonitor，请确认已安装 krfb（期望路径 {path}）。",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "找不到 kscreen-doctor，无法回读虚拟屏的真实分辨率与缩放，"
        "启动成功判定会退化为只检查端口。",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor 存在但读不到任何输出（打包版里曾被包内 Qt6 污染而"
        "直接 abort），无法回读虚拟屏的真实分辨率与缩放，"
        "启动成功判定会退化为只检查端口。",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "当前是 Wayland 会话但没有 WAYLAND_DISPLAY 环境变量，"
        "krfb 无法创建虚拟显示器。请从桌面启动器或终端运行本程序。",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "当前不是 Wayland 会话。krfb 的虚拟显示器仅支持 Wayland"
        "（且需要 KWin），在 X11 下会直接失败。",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} 指向的 socket 不存在（{path}），"
        "krfb 会以「Virtual Monitors are only supported on Wayland」失败。",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "当前由 systemd 单元 {unit} 启动，其 KillMode=control-group 且 "
        "ExitType=main —— 退出本程序会连带杀掉所有虚拟屏。"
        "请改从桌面启动器运行，或给该单元加上 ExitType=cgroup。",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "登录时自动恢复标记为「期望运行」的虚拟屏",
    "Cannot write {path}: {error}": "无法写入 {path}：{error}",
    "Cannot delete {path}: {error}": "无法删除 {path}：{error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "启动后直接最小化到托盘（供开机自启使用）",
    "Config warning": "配置读取警告",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor": "krfb-virtualmonitor 图形化管理器",
    "New virtual screen": "新建虚拟屏",
    "Start all": "全部启动",
    "Stop all": "全部停止",
    "Scan for and adopt krfb processes started outside this app":
        "扫描并认领外部启动的 krfb 进程",
    "Refresh now": "立即刷新状态",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "显示主窗口",
    "Quit": "退出",
    "Restart": "重启",
    "View": "查看",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "关闭窗口，还是最小化到托盘？",
    "Minimize to tray": "最小化到托盘",
    "Quit the program": "退出程序",
    "Remember my choice": "记住我的选择",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "共 {count} 个虚拟屏",
    "{count} running": "{count} 个运行中",
    "{count} need attention": "{count} 个需要处理",
    "{count} environment problems": "{count} 项环境问题",
    "{count} environment problems detected": "检测到 {count} 项环境问题",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "「{name}」已退出，可能崩溃或被手动结束",
    "{count} virtual screens have exited ({names}…)":
        "{count} 个虚拟屏已退出（{names}…）",
    "The process exited immediately after starting": "进程启动后立即退出",
    " (the port is listening, but no virtual display was created)":
        "（端口已监听，但虚拟显示器未创建）",
    " (the port isn't listening either)": "（端口也未监听）",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "等待 {seconds} 秒仍未在 KWin 中出现 Virtual-{name} 输出{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "该虚拟屏还没有保存密码（可能是从旧配置导入的），请补录一次。",
    "Cannot read the password from the keyring: {reason}":
        "无法从密钥环读取密码：{reason}",
    "Keyring": "密钥环",
    "Unlocked. Passwords will be saved to the keyring.":
        "已解锁，密码将保存到密钥环。",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "解锁失败或超时。密码仍可在本次会话中使用，但退出后需要重新输入。",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "需要重启",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "「{name}」正在运行。分辨率、缩放或端口的改动"
        "不会影响已经创建好的屏幕，需要重启该虚拟屏才能生效。",
    "Restart it now?": "现在重启吗？",
    "Restart now": "立即重启",
    "Later": "稍后",
    "Delete virtual screen": "删除虚拟屏",
    "Delete \"{name}\"?": "确定要删除「{name}」吗？",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "该虚拟屏当前正在运行，删除会先停止它。",
    "This action cannot be undone.": "此操作不可撤销。",
    "The saved password is removed from the keyring too.":
        "保存的密码也会一并从密钥环中移除。",
    "No unmanaged krfb processes found": "没有发现未托管的 krfb 进程",
    "{name}: {error}": "{name}：{error}",
    "Some could not be imported": "部分未能导入",
    "Start failed": "启动失败",
    "\"{name}\" failed to start": "「{name}」启动失败",
    "View full log": "查看完整日志",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "已最小化到托盘。虚拟屏继续运行，退出本程序也不会停止它们。",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left": "从左侧选择一个虚拟屏",
    "or click \"New\" in the top right": "或点击右上角「新建」创建",
    "Requested": "请求",
    "Actual": "实际生效",
    "Address": "连接地址",
    "Status": "状态",
    "Copy the VNC address": "复制 VNC 连接地址",
    "Copy the connection password": "复制连接密码",
    "Copied": "已复制",
    "Start": "启动",
    "Stop": "停止",
    "Edit": "编辑",
    "{actual}  ⚠ differs from the requested value": "{actual}  ⚠ 与请求值不符",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "密码只在这里隐藏显示；实际以明文传给 krfb 进程",
    "Running, PID {pid}": "运行中，PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "进程已消失，但标记为「期望运行」",
    "It may have crashed, been killed, or the machine was rebooted":
        "可能崩溃、被手动杀掉，或机器重启过",
    "Creating, waiting for the KWin output…": "正在创建，等待 KWin 输出…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "运行中修改分辨率或缩放不会影响已创建的屏幕，需要重启该虚拟屏",
    "Edit parameters": "编辑参数",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · 端口 {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "还没有虚拟屏\n点击右上角「新建」创建第一个",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "编辑虚拟屏",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "例如 Tablet（会成为 KWin 的 Virtual-<名称> 输出）",
    "Custom…": "自定义…",
    "Auto": "自动",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "找一个未被占用、也没被其他虚拟屏使用的端口",
    "Show / hide the password": "显示 / 隐藏密码",
    "Copy the password": "复制密码",
    "Optional, e.g. \"second screen for the iPad\"":
        "可选，例如「给 iPad 当副屏」",
    "Start at login": "登录时自动启动",
    "Save": "保存",
    "Name": "名称",
    "Resolution": "分辨率",
    "Scale DPR": "缩放 DPR",
    "Command that will be executed": "将要执行的命令",
    "The name can't be empty": "名称不能为空",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "「{name}」已被使用（KWin 输出名 Virtual-{name} 必须唯一）",
    "Port {port} is already used by another virtual screen":
        "端口 {port} 已被另一个虚拟屏使用",
    "Port {port} is already taken by another program on the system":
        "端口 {port} 已被系统中的其他程序占用",
    "The password can't be empty": "密码不能为空",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "VNC 认证只使用前 8 个字符，后 {extra} 位不产生任何作用"
        "（实际生效：{effective}）",
    "VNC authentication uses all 8 characters": "VNC 认证使用全部 8 个字符",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "需要密码",
    "Enter the VNC password for this virtual screen":
        "输入该虚拟屏的 VNC 连接密码",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "密码会以明文传给 krfb 进程，因此本机其他用户可通过 ps 看到；"
        "且 VNC 认证只使用前 8 个字符。",
    "Use": "使用",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found": "发现未托管的虚拟屏",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "以下 krfb-virtualmonitor 进程不是本程序启动的，导入后即可在这里统一管理。",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · 端口 {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "未知分辨率",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ 程序包已升级，"
        "建议改为重启此虚拟屏</span>",
    "Import selected": "导入选中的",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "语言",
    "Closing the window": "关闭窗口时",
    "Ask every time": "每次询问",
    "Launch at login": "开机自启",
    "Start at login (tray mode)": "登录时自动启动（托盘模式）",
    "Password storage": "密码存储",
    "Environment": "环境检查",
    "About": "关于",
    "No problems found": "未发现问题",
    "not installed": "未安装",
    "unknown": "未知",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "偏好保存失败（{error}）；本次会话内仍然生效。",
    "Config:": "配置：",
    "Runtime state:": "运行态：",
    "Logs:": "日志：",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "搜索…（回车跳转下一个匹配）",
    "Auto-scroll": "自动滚动",
    "Reload": "重新载入",
    "Open containing folder": "打开所在目录",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "（暂无输出）\n\n如果虚拟屏还没启动，这里会是空的。",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} 行   ·   {size} 字节",
    "No match for \"{needle}\"": "未找到「{needle}」",
    "Refreshes every {seconds} s": "每 {seconds} 秒刷新一次",

    # --- 密码库（多后端）----------------------------------------------------
    "KDE Wallet": "KDE 钱包",
    "System keyring (Secret Service)": "系统密钥环（Secret Service）",
    "Built-in encrypted vault": "内置加密库",
    "Master password required": "需要主密码",
    "No password vault yet": "还没有密码库",
    "Enter the master password to unlock the built-in vault":
        "输入主密码以解锁内置加密库",
    "Set a master password to create the built-in vault":
        "设置主密码即可创建内置加密库",
    "The store is disabled or does not exist": "该密码库已停用或不存在",
    "The store did not respond in time; passwords are kept in memory "
    "for this session only":
        "密码库无响应，密码暂存本次会话内存",
    "already holds saved passwords": "已有保存的密码",
    "locked; may hold saved passwords": "已锁定，可能存有密码",
    "available": "可用",
    "always available": "永远可用",
    "selected in settings": "在设置里选定的",
    "write failed": "写入失败",
    "read-back mismatch": "读回校验不一致",
    "store is locked": "密码库已锁定",
    "store is busy": "密码库忙（上一次调用还没返回）",
    "could not unlock the newly created vault": "新建的密码库无法解锁",
    "there is no vault": "还没有密码库",
    "wrong master password": "主密码不正确",
    "a vault already exists": "密码库已存在",
    "some entries could not be decrypted; nothing was changed":
        "有条目无法解密，未做任何改动",
    "(currently unavailable)": "（当前不可用）",
    "Store:": "密码库：",
    "Detect again": "立即重新检测",
    "Using {backend}: the selected store is unavailable":
        "正在使用 {backend}：选定的密码库不可用",
    "Master password": "主密码",
    "Current master password": "当前主密码",
    "New master password": "新主密码",
    "Repeat the password": "再输一次",
    "Create": "创建",
    "Change": "修改",
    "Unlock": "解锁",
    "Unlocked": "已解锁",
    "Enter master password": "输入主密码",
    "Set master password": "设置主密码",
    "Change master password": "修改主密码",
    "Create the built-in vault": "创建内置加密库",
    "Unlock the built-in vault": "解锁内置加密库",
    "Change the master password": "修改主密码",
    "Use at least {count} characters": "至少 {count} 个字符",
    "The two passwords do not match": "两次输入不一致",
    "Enter the current master password": "请输入当前主密码",
    "The built-in vault stores passwords encrypted. There is no way "
    "to recover them if you forget the master password.":
        "内置加密库把密码加密保存。忘记主密码就没有任何办法找回它们。",
    "Enter the master password for the built-in vault.":
        "输入内置加密库的主密码。",
    "Changing the master password re-encrypts every password in the vault.":
        "修改主密码会重新加密库里的每一条密码。",
    "Wrong master password": "主密码不正确",
    "Could not create the vault": "无法创建密码库",
    "The master password has been changed.": "主密码已修改。",
    "Enter the master password to read saved passwords":
        "输入主密码才能读取已保存的密码",

    # --- 高危确认（验证码）--------------------------------------------------
    "Type the result here": "在这里输入结果",
    "Confirm": "确认",
    "{a} + {b} = ?": "{a} + {b} = ?",
    "Wrong answer, here is another one": "答案不对，换一道题",
    "Too many wrong answers": "连续答错，已取消",

    # --- 密码库告警与切换 ---------------------------------------------------
    "Password store": "密码库",
    "Password store unavailable": "密码库不可用",
    "{store} holds {count} saved passwords but is unavailable right now.":
        "「{store}」里存着 {count} 条密码，但现在不可用。",
    "Enable it again in your system settings, or switch to another store — "
    "switching does not copy the old passwords over, and clearing the old "
    "store afterwards cannot be undone.":
        "请在系统设置里重新启用它，或者换一个密码库 —— 换库不会把这些密码带过去，"
        "之后若选择清除原数据则无法恢复。",
    "Open settings": "打开设置",
    "{store} is not available right now.": "「{store}」当前不可用。",
    "The target store could not be unlocked.": "目标密码库无法解锁。",
    "last updated {time}": "最近更新于 {time}",
    "that store does not report timestamps": "该密码库不提供时间戳",
    "Moving saved passwords…": "正在迁移已保存的密码…",
    "{count} passwords could not be moved:":
        "有 {count} 条密码没能迁移：",
    "Retry the import before clearing the old store.":
        "请先重试导入，再清除原密码库。",
    "Now using {store}": "已切换到「{store}」",
    "Clear the old password store": "清除原密码库的数据",
    "Delete the {count} passwords from {store}?":
        "要从「{store}」里删除这 {count} 条密码吗？",
    "They are now stored in the new store. Deleting them here cannot be "
    "undone — and any other application that uses that store will no "
    "longer find them either.":
        "它们现在已经在新密码库里了。在这里删除无法恢复 —— 而且其他使用该密码库的"
        "程序也会找不到它们。",
    "Delete them": "删除它们",
    "Deleted {count} passwords from the old store":
        "已从原密码库删除 {count} 条密码",

    # --- 内置库重置 ---------------------------------------------------------
    "Reset the built-in vault": "重置内置加密库",
    "This deletes every password stored in the built-in vault.":
        "这会删除内置加密库里保存的所有密码。",
    "They cannot be recovered — not even with the master password. "
    "Only do this if you no longer need them.":
        "它们无法恢复 —— 有主密码也救不回来。只有确定不再需要时才这么做。",
    "Delete the vault": "删除密码库",
    "The built-in vault has been reset": "内置加密库已重置",

    # --- 换库时目标已有数据：保留 / 覆盖 / 合并 ---
    "{store} already holds {count} of this app's passwords ({when}).": "「{store}」里已经有本程序的 {count} 条密码（{when}）。",
    "{source} holds {moving} for the same screens. Whichever side you "
    "drop is deleted for good.": "「{source}」里有同一批虚拟屏的 {moving} 条。被放弃的那一边会被永久删除。",
    "Keep the target's passwords": "保留目标里的密码",
    "Overwrite with the new passwords": "用新密码覆盖",
    "Merge…": "合并…",
    "Merge": "合并",
    "{adding} will be added, {identical} are identical and will be "
    "skipped, {conflicts} conflict.": "将新增 {adding} 条、{identical} 条完全相同会跳过、{conflicts} 条有冲突。",
    "Screens in conflict: {names}": "冲突的虚拟屏：{names}",
    "Keep the target's version": "冲突时保留目标里的",
    "Use the new version": "冲突时用新的",
    "{count} entries could not be read; they will be left as they are.": "有 {count} 条读不出来，将保持原样。",

    # --- 换库时源库锁着：一条都没搬，要说清楚 ---
    "The old store ({store}) is locked, so nothing was moved. "
    "Unlock it and switch again to bring the passwords over.":
        "原密码库「{store}」锁着，一条都没能搬过来。解锁它之后重新切换一次即可带走密码。",
}
