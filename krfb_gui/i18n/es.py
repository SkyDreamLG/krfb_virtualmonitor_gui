"""西班牙语词条表（Español）。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的西班牙语；分节与顺序与 zh_cn.py 一致。
`{named}` 占位符集合必须与键完全一致（tests/test_i18n.py 会校验）；
引号写进词条本身 —— 西班牙语用 « »，命令名、路径、环境变量一律保留原文。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "Seguir el sistema",
    ", ": ", ",  # join_list() 的列表分隔符
    "Cancel": "Cancelar",
    "Close": "Cerrar",
    "Delete": "Eliminar",
    "Log": "Registro",
    "Notes": "Notas",
    "Password": "Contraseña",
    "Port": "Puerto",
    "Random": "Aleatoria",
    "Settings": "Ajustes",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Gestor de pantallas virtuales Krfb",
    "3:2 Tablet": "Tableta 3:2",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "Gestionar las pantallas virtuales de krfb-virtualmonitor",

    # --- models -------------------------------------------------------------
    "Running": "En ejecución",
    "Stopped": "Detenido",
    "Exited unexpectedly": "Finalizó inesperadamente",
    "Starting": "Iniciando",
    "Failed to start": "No se pudo iniciar",
    "Unmanaged": "Sin gestionar",
    "Unnamed": "Sin nombre",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "Llavero listo",
    "Keyring locked": "Llavero bloqueado",
    "No keyring service found": "No se encontró ningún servicio de llavero",
    "Keyring unavailable": "Llavero no disponible",
    "Keyring not responding": "El llavero no responde",
    "Keyring error": "Error del llavero",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "La cartera de KDE está cerrada; las contraseñas solo se conservan en memoria durante esta sesión",
    "kwalletd is not running on the session bus":
        "kwalletd no se está ejecutando en el bus de sesión",
    "The KDE wallet subsystem is disabled, or no wallet exists":
        "El subsistema de cartera de KDE está desactivado o no existe ninguna cartera",
    "The wallet did not respond in time; passwords are kept in "
    "memory for this session only":
        "La cartera no respondió a tiempo; las contraseñas solo se conservan en memoria durante esta sesión",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "No se puede analizar el archivo de configuración: {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "La versión de configuración {found} no coincide con la esperada "
        "{expected}; se cargó en la medida de lo posible",
    "Unrecognized config format: {path}":
        "Formato de configuración no reconocido: {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "No se encontró krfb-virtualmonitor (se esperaba en {path})",
    "No password available": "No hay ninguna contraseña disponible",
    "Port {port} is already in use": "El puerto {port} ya está en uso",
    "Failed to start: {error}": "No se pudo iniciar: {error}",
    "The process vanished immediately after starting":
        "El proceso desapareció inmediatamente después de iniciarse",
    "The name \"{name}\" is already taken by a managed screen":
        "El nombre «{name}» ya lo usa una pantalla gestionada",
    "Port {port} is already taken by a managed screen":
        "El puerto {port} ya lo usa una pantalla gestionada",
    "Imported from an externally started process":
        "Importada de un proceso iniciado externamente",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "No se encontró krfb-virtualmonitor; comprobar que krfb está "
        "instalado (se esperaba en {path}).",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "No se encontró kscreen-doctor, por lo que no se pueden leer la "
        "resolución y la escala reales de una pantalla virtual; la "
        "verificación del inicio se limita a comprobar el puerto.",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor existe pero no devuelve ninguna salida (la versión "
        "empaquetada se vio afectada una vez por su Qt6 incluido y se abortó), "
        "por lo que no se pueden leer la resolución y la escala reales de una "
        "pantalla virtual; la verificación del inicio se limita a comprobar "
        "el puerto.",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Esta es una sesión Wayland pero WAYLAND_DISPLAY no está definida, "
        "por lo que krfb no puede crear monitores virtuales. Iniciar este "
        "programa desde el lanzador del escritorio o un terminal.",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Esta no es una sesión Wayland. Los monitores virtuales de krfb "
        "requieren Wayland (y KWin); en X11 fallan directamente.",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} apunta a un socket que no existe "
        "({path}); krfb fallará con "
        "«Virtual Monitors are only supported on Wayland».",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "Iniciado por la unidad systemd {unit}, cuyos KillMode=control-group "
        "y ExitType=main hacen que al salir de este programa se cierren "
        "también todas las pantallas virtuales. Iniciarlo mejor desde el "
        "lanzador del escritorio, o añadir ExitType=cgroup a esa unidad.",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "Restaurar al iniciar sesión las pantallas virtuales marcadas como "
        "«debe estar en ejecución»",
    "Cannot write {path}: {error}": "No se puede escribir {path}: {error}",
    "Cannot delete {path}: {error}": "No se puede eliminar {path}: {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "Iniciar minimizado en la bandeja (usado por el inicio automático)",
    "Config warning": "Aviso de configuración",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor":
        "Gestor gráfico para krfb-virtualmonitor",
    "New virtual screen": "Nueva pantalla virtual",
    "Start all": "Iniciar todas",
    "Stop all": "Detener todas",
    "Scan for and adopt krfb processes started outside this app":
        "Buscar y adoptar los procesos krfb iniciados fuera de esta "
        "aplicación",
    "Refresh now": "Actualizar ahora",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "Mostrar la ventana principal",
    "Quit": "Salir",
    "Restart": "Reiniciar",
    "View": "Ver",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "¿Cerrar la ventana o minimizar a la bandeja?",
    "Minimize to tray": "Minimizar a la bandeja",
    "Quit the program": "Salir del programa",
    "Remember my choice": "Recordar mi elección",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "{count} pantallas virtuales",
    "{count} running": "{count} en ejecución",
    "{count} need attention": "{count} requieren atención",
    "{count} environment problems": "{count} problemas de entorno",
    "{count} environment problems detected":
        "Se detectaron {count} problemas de entorno",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "«{name}» ha finalizado — puede que se haya bloqueado o se haya matado",
    "{count} virtual screens have exited ({names}…)":
        "{count} pantallas virtuales han finalizado ({names}…)",
    "The process exited immediately after starting":
        "El proceso finalizó inmediatamente después de iniciarse",
    " (the port is listening, but no virtual display was created)":
        " (el puerto está escuchando, pero no se creó ninguna pantalla "
        "virtual)",
    " (the port isn't listening either)":
        " (el puerto tampoco está escuchando)",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "Se esperaron {seconds} segundos y la salida Virtual-{name} aún "
        "no ha aparecido en KWin{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "Esta pantalla virtual no tiene contraseña guardada (puede proceder "
        "de una configuración antigua); introducir una ahora.",
    "Cannot read the password from the keyring: {reason}":
        "No se puede leer la contraseña del llavero: {reason}",
    "Keyring": "Llavero",
    "Unlocked. Passwords will be saved to the keyring.":
        "Desbloqueado. Las contraseñas se guardarán en el llavero.",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "El desbloqueo falló o se agotó el tiempo. Las contraseñas aún pueden "
        "usarse durante esta sesión, pero deberán introducirse de nuevo al "
        "salir.",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "Es necesario reiniciar",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "«{name}» está en ejecución. Los cambios de resolución, escala o "
        "puerto no afectan a una pantalla ya creada; hay que reiniciar la "
        "pantalla virtual para que surtan efecto.",
    "Restart it now?": "¿Reiniciarla ahora?",
    "Restart now": "Reiniciar ahora",
    "Later": "Más tarde",
    "Delete virtual screen": "Eliminar pantalla virtual",
    "Delete \"{name}\"?": "¿Eliminar «{name}»?",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "Esta pantalla virtual está en ejecución; al eliminarla se detendrá "
        "primero.",
    "This action cannot be undone.": "Esta acción no se puede deshacer.",
    "The saved password is removed from the keyring too.":
        "La contraseña guardada también se elimina del llavero.",
    "No unmanaged krfb processes found":
        "No se encontraron procesos krfb sin gestionar",
    "{name}: {error}": "{name}: {error}",
    "Some could not be imported": "Algunos no se pudieron importar",
    "Start failed": "Error al iniciar",
    "\"{name}\" failed to start": "«{name}» no se pudo iniciar",
    "View full log": "Ver el registro completo",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "Minimizado a la bandeja. Las pantallas virtuales siguen "
        "ejecutándose y no se detienen al salir de esta aplicación.",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left":
        "Seleccionar una pantalla virtual a la izquierda",
    "or click \"New\" in the top right":
        "o hacer clic en «Nueva» arriba a la derecha",
    "Requested": "Solicitado",
    "Actual": "Real",
    "Address": "Dirección",
    "Status": "Estado",
    "Copy the VNC address": "Copiar la dirección VNC",
    "Copy the connection password": "Copiar la contraseña de conexión",
    "Copied": "Copiado",
    "Start": "Iniciar",
    "Stop": "Detener",
    "Edit": "Editar",
    "{actual}  ⚠ differs from the requested value":
        "{actual}  ⚠ difiere del valor solicitado",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "La contraseña solo se oculta en la interfaz; "
        "se pasa a krfb en texto sin cifrar",
    "Running, PID {pid}": "En ejecución, PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "El proceso ha desaparecido pero está marcado como "
        "«debe estar en ejecución»",
    "It may have crashed, been killed, or the machine was rebooted":
        "Puede que se haya bloqueado, se haya matado o se haya reiniciado "
        "el equipo",
    "Creating, waiting for the KWin output…":
        "Creando, esperando la salida de KWin…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "Cambiar la resolución o la escala en ejecución no afecta a la "
        "pantalla ya creada; hay que reiniciar la pantalla virtual",
    "Edit parameters": "Editar parámetros",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · Puerto {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "Aún no hay pantallas virtuales\n"
        "Hacer clic en «Nueva» para crear una",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "Editar pantalla virtual",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "p. ej. Tablet (se convierte en la salida de KWin «Virtual-<name>»)",
    "Custom…": "Personalizado…",
    "Auto": "Automático",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "Elegir un puerto que no esté en uso "
        "ni asignado a otra pantalla virtual",
    "Show / hide the password": "Mostrar / ocultar la contraseña",
    "Copy the password": "Copiar la contraseña",
    "Optional, e.g. \"second screen for the iPad\"":
        "Opcional; p. ej. «segunda pantalla para el iPad»",
    "Start at login": "Iniciar al iniciar sesión",
    "Save": "Guardar",
    "Name": "Nombre",
    "Resolution": "Resolución",
    "Scale DPR": "Escala DPR",
    "Command that will be executed": "Comando que se ejecutará",
    "The name can't be empty": "El nombre no puede estar vacío",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "«{name}» ya está en uso "
        "(el nombre de salida de KWin Virtual-{name} debe ser único)",
    "Port {port} is already used by another virtual screen":
        "El puerto {port} ya lo usa otra pantalla virtual",
    "Port {port} is already taken by another program on the system":
        "El puerto {port} ya lo usa otro programa del sistema",
    "The password can't be empty": "La contraseña no puede estar vacía",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "La autenticación VNC solo usa los 8 primeros caracteres; "
        "los {extra} restantes no tienen ningún efecto "
        "(contraseña efectiva: {effective})",
    "VNC authentication uses all 8 characters":
        "La autenticación VNC usa los 8 caracteres",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "Se requiere contraseña",
    "Enter the VNC password for this virtual screen":
        "Introducir la contraseña VNC de esta pantalla virtual",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "La contraseña se pasa al proceso krfb en texto sin cifrar, por lo "
        "que otros usuarios locales pueden verla con ps; además, la "
        "autenticación VNC solo usa los 8 primeros caracteres.",
    "Use": "Usar",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found":
        "Se encontraron pantallas virtuales sin gestionar",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "Estos procesos de krfb-virtualmonitor no los inició esta "
        "aplicación. Importarlos para gestionarlos aquí.",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · Puerto {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "resolución desconocida",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ El paquete se ha actualizado; "
        "se recomienda reiniciar esta pantalla virtual</span>",
    "Import selected": "Importar seleccionados",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "Idioma",
    "Closing the window": "Al cerrar la ventana",
    "Ask every time": "Preguntar cada vez",
    "Launch at login": "Iniciar al iniciar sesión",
    "Start at login (tray mode)":
        "Iniciar al iniciar sesión (modo bandeja)",
    "Password storage": "Almacenamiento de contraseñas",
    "Unlock keyring": "Desbloquear el llavero",
    "Environment": "Entorno",
    "About": "Acerca de",
    "No problems found": "No se encontraron problemas",
    "not installed": "no instalado",
    "unknown": "desconocido",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "No se pudo guardar la preferencia ({error}); "
        "sigue vigente solo durante esta sesión.",
    "Config:": "Configuración:",
    "Runtime state:": "Estado de ejecución:",
    "Logs:": "Registros:",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "Buscar… (pulsar Intro para el siguiente resultado)",
    "Auto-scroll": "Desplazamiento automático",
    "Reload": "Recargar",
    "Open containing folder": "Abrir la carpeta contenedora",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "(Aún no hay salida)\n\n"
        "Esto estará vacío hasta que se inicie la pantalla virtual.",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} líneas   ·   {size} bytes",
    "No match for \"{needle}\"": "No hay coincidencias para «{needle}»",
    "Refreshes every {seconds} s": "Se actualiza cada {seconds} s",
}
