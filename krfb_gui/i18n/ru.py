"""俄语词条表。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的俄语（西里尔字母）。
键顺序与 zh_cn.py 完全一致，按源文件分节，方便对照增删。

约定：
  * 值是整句，`{named}` 占位符集合必须与键完全一致（tests/test_i18n.py 会校验）；
  * 引号写进词条本身，俄语用 «»；
  * 不翻译：`krfb-virtualmonitor` / `kscreen-doctor` / `kwinoutputconfig.json` /
    `systemd` 这类专名，Wayland / KWin / X11，以及 HTML 片段里的标签；
  * 数量短语用“……：{count}”这种不随数变化的写法，词条表不支持复数形式。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "Как в системе",
    ", ": ", ",  # join_list() 的列表分隔符
    "Cancel": "Отмена",
    "Close": "Закрыть",
    "Delete": "Удалить",
    "Log": "Журнал",
    "Notes": "Заметки",
    "Password": "Пароль",
    "Port": "Порт",
    "Random": "Случайный",
    "Settings": "Настройки",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Менеджер виртуальных экранов Krfb",
    "3:2 Tablet": "Планшет 3:2",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "Управление виртуальными экранами krfb-virtualmonitor",

    # --- models -------------------------------------------------------------
    "Running": "Работает",
    "Stopped": "Остановлен",
    "Exited unexpectedly": "Неожиданно завершился",
    "Starting": "Запускается",
    "Failed to start": "Не удалось запустить",
    "Unmanaged": "Неуправляемый",
    "Unnamed": "Без имени",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "Связка ключей готова",
    "Keyring locked": "Связка ключей заблокирована",
    "No keyring service found": "Служба связки ключей не найдена",
    "Keyring unavailable": "Связка ключей недоступна",
    "Keyring not responding": "Связка ключей не отвечает",
    "Keyring error": "Ошибка связки ключей",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "Кошелёк KDE закрыт; пароли хранятся в памяти только до конца сеанса",
    "kwalletd is not running on the session bus":
        "В сеансовой шине не запущен kwalletd",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "Не удалось разобрать файл конфигурации: {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "Версия конфигурации {found} не совпадает с ожидаемой {expected}; "
        "файл загружен по возможности",
    "Unrecognized config format: {path}":
        "Неизвестный формат конфигурации: {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "krfb-virtualmonitor не найден (ожидается в {path})",
    "No password available": "Пароль недоступен",
    "Port {port} is already in use": "Порт {port} уже занят",
    "Failed to start: {error}": "Не удалось запустить: {error}",
    "The process vanished immediately after starting": "Процесс исчез сразу после запуска",
    "The name \"{name}\" is already taken by a managed screen":
        "Имя «{name}» уже занято управляемым экраном",
    "Port {port} is already taken by a managed screen":
        "Порт {port} уже занят управляемым экраном",
    "Imported from an externally started process": "Импортирован из процесса, запущенного извне",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "krfb-virtualmonitor не найден; убедитесь, что krfb установлен "
        "(ожидается в {path}).",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "kscreen-doctor не найден, поэтому реальное разрешение и масштаб "
        "виртуального экрана не удаётся прочитать; проверка запуска "
        "ограничивается контролем порта.",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor есть, но не выдаёт никаких данных (сборка в пакете "
        "однажды была испорчена собственным Qt6 и прерывалась), поэтому "
        "реальное разрешение и масштаб виртуального экрана не удаётся "
        "прочитать; проверка запуска ограничивается контролем порта.",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Это сеанс Wayland, но переменная WAYLAND_DISPLAY не задана, поэтому "
        "krfb не может создавать виртуальные мониторы. Запустите программу "
        "из меню рабочего стола или из терминала.",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Это не сеанс Wayland. Виртуальные мониторы krfb требуют Wayland "
        "(и KWin); в X11 они сразу отказывают.",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} указывает на несуществующий сокет "
        "({path}); krfb завершится с ошибкой "
        "«Virtual Monitors are only supported on Wayland».",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "Запущено модулем systemd {unit}, у которого KillMode=control-group и "
        "ExitType=main: выход из этой программы уничтожит вместе с ней и все "
        "виртуальные экраны. Запускайте её из меню рабочего стола или "
        "добавьте ExitType=cgroup в этот модуль.",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "При входе в систему восстанавливать виртуальные экраны, помеченные "
        "как «должны работать»",
    "Cannot write {path}: {error}": "Не удалось записать {path}: {error}",
    "Cannot delete {path}: {error}": "Не удалось удалить {path}: {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "Запускать свёрнутым в системный лоток (используется автозапуском)",
    "Config warning": "Предупреждение о конфигурации",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor": "Графический менеджер для krfb-virtualmonitor",
    "New virtual screen": "Новый виртуальный экран",
    "Start all": "Запустить все",
    "Stop all": "Остановить все",
    "Scan for and adopt krfb processes started outside this app":
        "Найти и принять под управление процессы krfb, запущенные вне этой программы",
    "Refresh now": "Обновить сейчас",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "Показать главное окно",
    "Quit": "Выход",
    "Restart": "Перезапустить",
    "View": "Просмотр",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "Закрыть окно или свернуть в лоток?",
    "Minimize to tray": "Свернуть в лоток",
    "Quit the program": "Выйти из программы",
    "Remember my choice": "Запомнить мой выбор",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "Виртуальных экранов: {count}",
    "{count} running": "Работают: {count}",
    "{count} need attention": "Требуют внимания: {count}",
    "{count} environment problems": "Проблем окружения: {count}",
    "{count} environment problems detected": "Обнаружено проблем окружения: {count}",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "«{name}» завершился — возможно, произошёл сбой или процесс был убит",
    "{count} virtual screens have exited ({names}…)":
        "Виртуальных экранов завершилось: {count} ({names}…)",
    "The process exited immediately after starting": "Процесс завершился сразу после запуска",
    " (the port is listening, but no virtual display was created)":
        " (порт прослушивается, но виртуальный дисплей не создан)",
    " (the port isn't listening either)": " (порт тоже не прослушивается)",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "Прошло {seconds} с, но вывод Virtual-{name} так и не появился "
        "в KWin{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "У этого виртуального экрана нет сохранённого пароля (возможно, он "
        "из старой конфигурации); введите его сейчас.",
    "Cannot read the password from the keyring: {reason}":
        "Не удалось прочитать пароль из связки ключей: {reason}",
    "Keyring": "Связка ключей",
    "Unlocked. Passwords will be saved to the keyring.":
        "Разблокировано. Пароли будут сохраняться в связке ключей.",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "Не удалось разблокировать или истекло время ожидания. Паролями ещё "
        "можно пользоваться до конца сеанса, но после выхода их придётся "
        "ввести заново.",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "Требуется перезапуск",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "«{name}» работает. Изменения разрешения, масштаба или порта не "
        "влияют на уже созданный экран; чтобы они вступили в силу, "
        "виртуальный экран нужно перезапустить.",
    "Restart it now?": "Перезапустить сейчас?",
    "Restart now": "Перезапустить",
    "Later": "Позже",
    "Delete virtual screen": "Удаление виртуального экрана",
    "Delete \"{name}\"?": "Удалить «{name}»?",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "Этот виртуальный экран сейчас работает; перед удалением он будет остановлен.",
    "This action cannot be undone.": "Это действие нельзя отменить.",
    "The saved password is removed from the keyring too.":
        "Сохранённый пароль тоже будет удалён из связки ключей.",
    "No unmanaged krfb processes found": "Неуправляемые процессы krfb не найдены",
    "{name}: {error}": "{name}: {error}",
    "Some could not be imported": "Некоторые не удалось импортировать",
    "Start failed": "Ошибка запуска",
    "\"{name}\" failed to start": "Не удалось запустить «{name}»",
    "View full log": "Открыть полный журнал",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "Свёрнуто в лоток. Виртуальные экраны продолжат работать и не будут "
        "остановлены при выходе из программы.",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left": "Выберите виртуальный экран слева",
    "or click \"New\" in the top right":
        "или нажмите «Новый виртуальный экран» в правом верхнем углу",
    "Requested": "Запрошено",
    "Actual": "Фактически",
    "Address": "Адрес",
    "Status": "Состояние",
    "Copy the VNC address": "Копировать адрес VNC",
    "Copy the connection password": "Копировать пароль подключения",
    "Copied": "Скопировано",
    "Start": "Запустить",
    "Stop": "Остановить",
    "Edit": "Изменить",
    "{actual}  ⚠ differs from the requested value":
        "{actual}  ⚠ отличается от запрошенного значения",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "Пароль скрыт только в интерфейсе; в krfb он передаётся открытым текстом",
    "Running, PID {pid}": "Работает, PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "Процесс исчез, но помечен как «должен работать»",
    "It may have crashed, been killed, or the machine was rebooted":
        "Возможно, произошёл сбой, процесс был убит или компьютер перезагружался",
    "Creating, waiting for the KWin output…": "Создание, ожидание вывода KWin…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "Изменение разрешения или масштаба на работающем экране не влияет на "
        "уже созданный; виртуальный экран нужно перезапустить",
    "Edit parameters": "Изменить параметры",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · Порт {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "Виртуальных экранов пока нет\n"
        "Нажмите «Новый виртуальный экран», чтобы создать первый",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "Изменение виртуального экрана",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "напр. Tablet (станет выводом KWin «Virtual-<name>»)",
    "Custom…": "Другой…",
    "Auto": "Авто",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "Выберите порт, который не занят и не назначен другому виртуальному экрану",
    "Show / hide the password": "Показать / скрыть пароль",
    "Copy the password": "Копировать пароль",
    "Optional, e.g. \"second screen for the iPad\"":
        "Необязательно, напр. «второй экран для iPad»",
    "Start at login": "Запускать при входе",
    "Save": "Сохранить",
    "Name": "Имя",
    "Resolution": "Разрешение",
    "Scale DPR": "Масштаб DPR",
    "Command that will be executed": "Команда, которая будет выполнена",
    "The name can't be empty": "Имя не может быть пустым",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "Имя «{name}» уже используется (имя вывода KWin Virtual-{name} "
        "должно быть уникальным)",
    "Port {port} is already used by another virtual screen":
        "Порт {port} уже используется другим виртуальным экраном",
    "Port {port} is already taken by another program on the system":
        "Порт {port} уже занят другой программой в системе",
    "The password can't be empty": "Пароль не может быть пустым",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "Аутентификация VNC использует только первые 8 символов; остальные "
        "{extra} ни на что не влияют (действующий пароль: {effective})",
    "VNC authentication uses all 8 characters": "Аутентификация VNC использует все 8 символов",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "Требуется пароль",
    "Enter the VNC password for this virtual screen":
        "Введите пароль VNC для этого виртуального экрана",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "Пароль передаётся процессу krfb открытым текстом, поэтому другие "
        "локальные пользователи могут увидеть его через ps; аутентификация "
        "VNC использует только первые 8 символов.",
    "Use": "Использовать",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found": "Найдены неуправляемые виртуальные экраны",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "Эти процессы krfb-virtualmonitor запущены не этой программой. "
        "Импортируйте их, чтобы управлять ими отсюда.",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · Порт {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "разрешение неизвестно",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ Пакет был обновлён; "
        "рекомендуется перезапустить этот виртуальный экран</span>",
    "Import selected": "Импортировать выбранные",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "Язык",
    "Closing the window": "При закрытии окна",
    "Ask every time": "Спрашивать каждый раз",
    "Launch at login": "Автозапуск при входе",
    "Start at login (tray mode)": "Запускать при входе (режим лотка)",
    "Password storage": "Хранение паролей",
    "Environment": "Окружение",
    "About": "О программе",
    "No problems found": "Проблем не обнаружено",
    "not installed": "не установлен",
    "unknown": "неизвестно",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "Не удалось сохранить настройку ({error}); "
        "она действует только до конца сеанса.",
    "Config:": "Конфигурация:",
    "Runtime state:": "Состояние:",
    "Logs:": "Журналы:",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "Поиск… (Enter — следующее совпадение)",
    "Auto-scroll": "Автопрокрутка",
    "Reload": "Перезагрузить",
    "Open containing folder": "Открыть содержащую папку",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "(Вывода пока нет)\n\nЗдесь пусто, пока виртуальный экран не запущен.",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} строк   ·   {size} байт",
    "No match for \"{needle}\"": "Совпадений для «{needle}» не найдено",
    "Refreshes every {seconds} s": "Обновляется каждые {seconds} с",

    # --- 密码库（多后端）----------------------------------------------------
    "KDE Wallet": "KDE Wallet",
    "System keyring (Secret Service)": "Системная связка ключей (Secret Service)",
    "Built-in encrypted vault": "Встроенное зашифрованное хранилище",
    "Master password required": "Требуется главный пароль",
    "No password vault yet": "Хранилища пока нет",
    "Enter the master password to unlock the built-in vault":
        "Введите главный пароль, чтобы разблокировать встроенное хранилище",
    "Set a master password to create the built-in vault":
        "Задайте главный пароль, чтобы создать встроенное хранилище",
    "The store is disabled or does not exist":
        "Хранилище паролей отключено или не существует",
    "The store did not respond in time; passwords are kept in memory "
    "for this session only":
        "Хранилище паролей не ответило вовремя; пароли хранятся в памяти "
        "только до конца сеанса",
    "already holds saved passwords": "уже содержит сохранённые пароли",
    "locked; may hold saved passwords":
        "заблокировано; может содержать сохранённые пароли",
    "available": "доступно",
    "always available": "всегда доступно",
    "selected in settings": "выбрано в настройках",
    "write failed": "ошибка записи",
    "read-back mismatch": "несовпадение при обратном чтении",
    "store is locked": "хранилище паролей заблокировано",
    "store is busy": "хранилище паролей занято",
    "could not unlock the newly created vault":
        "не удалось разблокировать только что созданное хранилище",
    "there is no vault": "хранилища нет",
    "wrong master password": "неверный главный пароль",
    "a vault already exists": "хранилище уже существует",
    "some entries could not be decrypted; nothing was changed":
        "некоторые записи не удалось расшифровать; ничего не изменено",
    "(currently unavailable)": "(сейчас недоступно)",
    "Store:": "Хранилище:",
    "Detect again": "Определить заново",
    "Using {backend}: the selected store is unavailable":
        "Используется {backend}: выбранное хранилище паролей недоступно",
    "Master password": "Главный пароль",
    "Current master password": "Текущий главный пароль",
    "New master password": "Новый главный пароль",
    "Repeat the password": "Повторите пароль",
    "Create": "Создать",
    "Change": "Сменить",
    "Unlock": "Разблокировать",
    "Unlocked": "Разблокировано",
    "Enter master password": "Введите главный пароль",
    "Set master password": "Задать главный пароль",
    "Change master password": "Сменить главный пароль",
    "Create the built-in vault": "Создать встроенное хранилище",
    "Unlock the built-in vault": "Разблокировать встроенное хранилище",
    "Change the master password": "Сменить главный пароль",
    "Use at least {count} characters": "Используйте не менее {count} символов",
    "The two passwords do not match": "Пароли не совпадают",
    "Enter the current master password": "Введите текущий главный пароль",
    "The built-in vault stores passwords encrypted. There is no way "
    "to recover them if you forget the master password.":
        "Встроенное хранилище хранит пароли в зашифрованном виде. Если вы "
        "забудете главный пароль, восстановить их не получится.",
    "Enter the master password for the built-in vault.":
        "Введите главный пароль для встроенного хранилища.",
    "Changing the master password re-encrypts every password in the vault.":
        "Смена главного пароля заново шифрует все пароли в хранилище.",
    "Wrong master password": "Неверный главный пароль",
    "Could not create the vault": "Не удалось создать хранилище",
    "The master password has been changed.": "Главный пароль изменён.",
    "Enter the master password to read saved passwords":
        "Введите главный пароль, чтобы прочитать сохранённые пароли",

    # --- 高危确认（验证码）--------------------------------------------------
    "Type the result here": "Введите результат здесь",
    "Confirm": "Подтвердить",
    "{a} + {b} = ?": "{a} + {b} = ?",
    "Wrong answer, here is another one": "Неверный ответ, вот другой пример",
    "Too many wrong answers": "Слишком много неверных ответов",

    # --- 密码库告警与切换 ---------------------------------------------------
    "Password store": "Хранилище паролей",
    "Password store unavailable": "Хранилище паролей недоступно",
    "{store} holds {count} saved passwords but is unavailable right now.":
        "В «{store}» сохранено паролей: {count}, но сейчас оно недоступно.",
    "Enable it again in your system settings, or switch to another store — "
    "switching does not copy the old passwords over, and clearing the old "
    "store afterwards cannot be undone.":
        "Включите его снова в системных настройках или перейдите на другое "
        "хранилище паролей — при переходе старые пароли не переносятся, а "
        "последующая очистка старого хранилища необратима.",
    "Open settings": "Открыть настройки",
    "{store} is not available right now.": "«{store}» сейчас недоступно.",
    "The target store could not be unlocked.":
        "Не удалось разблокировать целевое хранилище.",
    "last updated {time}": "последнее обновление: {time}",
    "that store does not report timestamps":
        "это хранилище не сообщает метки времени",
    "Moving saved passwords…": "Перенос сохранённых паролей…",
    "{count} passwords could not be moved:":
        "Не удалось перенести паролей: {count}",
    "Retry the import before clearing the old store.":
        "Повторите импорт, прежде чем очищать старое хранилище.",
    "Now using {store}": "Теперь используется «{store}»",
    "Clear the old password store": "Очистить старое хранилище паролей",
    "Delete the {count} passwords from {store}?":
        "Удалить пароли из «{store}» (всего: {count})?",
    "They are now stored in the new store. Deleting them here cannot be "
    "undone — and any other application that uses that store will no "
    "longer find them either.":
        "Теперь они хранятся в новом хранилище. Удаление здесь необратимо — "
        "и другие приложения, использующие это хранилище, тоже больше их не "
        "найдут.",
    "Delete them": "Удалить их",
    "Deleted {count} passwords from the old store":
        "Из старого хранилища удалено паролей: {count}",

    # --- 内置库重置 ---------------------------------------------------------
    "Reset the built-in vault": "Сбросить встроенное хранилище",
    "This deletes every password stored in the built-in vault.":
        "Это удалит все пароли, хранящиеся во встроенном хранилище.",
    "They cannot be recovered — not even with the master password. "
    "Only do this if you no longer need them.":
        "Их нельзя будет восстановить — даже с главным паролем. Делайте "
        "это, только если они больше не нужны.",
    "Delete the vault": "Удалить хранилище",
    "The built-in vault has been reset": "Встроенное хранилище сброшено",

    # --- Данные в целевом хранилище: оставить / перезаписать / объединить ---
    "{store} already holds {count} of this app's passwords ({when}).":
        "В «{store}» уже сохранено паролей этого приложения: {count} "
        "({when}).",
    "{source} holds {moving} for the same screens. Whichever side you "
    "drop is deleted for good.":
        "В «{source}» для тех же экранов сохранено паролей: {moving}. "
        "Отброшенная сторона удаляется безвозвратно.",
    "Keep the target's passwords": "Оставить пароли из целевого хранилища",
    "Overwrite with the new passwords": "Перезаписать новыми паролями",
    "Merge…": "Объединить…",
    "Merge": "Объединить",
    "{adding} will be added, {identical} are identical and will be "
    "skipped, {conflicts} conflict.":
        "Будет добавлено: {adding}, пропущено как идентичные: "
        "{identical}, конфликтов: {conflicts}.",
    "Screens in conflict: {names}": "Конфликтующие экраны: {names}",
    "Keep the target's version": "Оставить версию из целевого хранилища",
    "Use the new version": "Использовать новую версию",
    "{count} entries could not be read; they will be left as they are.":
        "Не удалось прочитать записей: {count}; "
        "они останутся без изменений.",

    # --- Старое хранилище заблокировано: ничего не перенесено ---
    "The old store ({store}) is locked, so nothing was moved. "
    "Unlock it and switch again to bring the passwords over.":
        "Старое хранилище ({store}) заблокировано, поэтому ничего не "
        "перенесено. Разблокируйте его и повторите переключение, чтобы "
        "перенести пароли.",
}
