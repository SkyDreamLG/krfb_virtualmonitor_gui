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

    # --- 密码库（多后端）----------------------------------------------------
    "KDE Wallet": "KDE Wallet",
    "System keyring (Secret Service)": "Llavero del sistema (Secret Service)",
    "Built-in encrypted vault": "Caja fuerte cifrada integrada",
    "Master password required": "Se requiere la contraseña maestra",
    "No password vault yet": "Todavía no hay caja fuerte",
    "Enter the master password to unlock the built-in vault":
        "Introducir la contraseña maestra para desbloquear la caja fuerte "
        "integrada",
    "Set a master password to create the built-in vault":
        "Definir una contraseña maestra para crear la caja fuerte integrada",
    "The store is disabled or does not exist":
        "El almacenamiento está desactivado o no existe",
    "The store did not respond in time; passwords are kept in memory "
    "for this session only":
        "El almacenamiento no respondió a tiempo; las contraseñas solo se "
        "conservan en memoria durante esta sesión",
    "already holds saved passwords": "ya contiene contraseñas guardadas",
    "locked; may hold saved passwords":
        "bloqueado; puede contener contraseñas guardadas",
    "available": "disponible",
    "always available": "siempre disponible",
    "selected in settings": "seleccionado en los ajustes",
    "write failed": "fallo de escritura",
    "read-back mismatch": "discrepancia en la relectura",
    "store is locked": "El almacenamiento está bloqueado",
    "store is busy":
        "El almacenamiento está ocupado (la llamada anterior aún no ha "
        "terminado)",
    "could not unlock the newly created vault":
        "No se pudo desbloquear la caja fuerte recién creada",
    "there is no vault": "Todavía no existe ninguna caja fuerte",
    "wrong master password": "Contraseña maestra incorrecta",
    "a vault already exists": "Ya existe una caja fuerte",
    "some entries could not be decrypted; nothing was changed":
        "Algunas entradas no se pudieron descifrar; no se cambió nada",
    "(currently unavailable)": "(actualmente no disponible)",
    "Store:": "Almacenamiento:",
    "Detect again": "Detectar de nuevo",
    "Using {backend}: the selected store is unavailable":
        "Se usa {backend}: el almacenamiento seleccionado no está disponible",
    "Master password": "Contraseña maestra",
    "Current master password": "Contraseña maestra actual",
    "New master password": "Nueva contraseña maestra",
    "Repeat the password": "Repetir la contraseña",
    "Create": "Crear",
    "Change": "Cambiar",
    "Unlock": "Desbloquear",
    "Unlocked": "Desbloqueado",
    "Enter master password": "Introducir la contraseña maestra",
    "Set master password": "Definir la contraseña maestra",
    "Change master password": "Cambiar la contraseña maestra",
    "Create the built-in vault": "Crear la caja fuerte integrada",
    "Unlock the built-in vault": "Desbloquear la caja fuerte integrada",
    "Change the master password": "Cambiar la contraseña maestra",
    "Use at least {count} characters": "Usar al menos {count} caracteres",
    "The two passwords do not match": "Las dos contraseñas no coinciden",
    "Enter the current master password":
        "Introducir la contraseña maestra actual",
    "The built-in vault stores passwords encrypted. There is no way to "
    "recover them if you forget the master password.":
        "La caja fuerte integrada guarda las contraseñas cifradas. Si se olvida "
        "la contraseña maestra, no hay forma de recuperarlas.",
    "Enter the master password for the built-in vault.":
        "Introducir la contraseña maestra de la caja fuerte integrada.",
    "Changing the master password re-encrypts every password in the "
    "vault.":
        "Cambiar la contraseña maestra vuelve a cifrar todas las contraseñas de "
        "la caja fuerte.",
    "Wrong master password": "Contraseña maestra incorrecta",
    "Could not create the vault": "No se pudo crear la caja fuerte",
    "The master password has been changed.":
        "La contraseña maestra se ha cambiado.",
    "Enter the master password to read saved passwords":
        "Introducir la contraseña maestra para leer las contraseñas guardadas",

    # --- 高危确认（验证码）--------------------------------------------------
    "Type the result here": "Escribir el resultado aquí",
    "Confirm": "Confirmar",
    "{a} + {b} = ?": "{a} + {b} = ?",
    "Wrong answer, here is another one": "Respuesta incorrecta, aquí hay otra",
    "Too many wrong answers": "Demasiadas respuestas incorrectas",

    # --- 密码库告警与切换----------------------------------------------------
    "Password store": "Almacenamiento de contraseñas",
    "Password store unavailable":
        "Almacenamiento de contraseñas no disponible",
    "{store} holds {count} saved passwords but is unavailable right "
    "now.":
        "«{store}» contiene {count} contraseñas guardadas, pero ahora mismo no "
        "está disponible.",
    "Enable it again in your system settings, or switch to another "
    "store — switching does not copy the old passwords over, and "
    "clearing the old store afterwards cannot be undone.":
        "Volver a activarlo en los ajustes del sistema o cambiar a otro "
        "almacenamiento — el cambio no copia las contraseñas antiguas, y borrar "
        "después el almacenamiento antiguo no se puede deshacer.",
    "Open settings": "Abrir los ajustes",
    "{store} is not available right now.":
        "«{store}» no está disponible ahora mismo.",
    "The target store could not be unlocked.":
        "No se pudo desbloquear el almacenamiento de destino.",
    "last updated {time}": "última actualización {time}",
    "that store does not report timestamps":
        "ese almacenamiento no proporciona marcas de tiempo",
    "Moving saved passwords…": "Moviendo las contraseñas guardadas…",
    "{count} passwords could not be moved:":
        "No se pudieron mover {count} contraseñas:",
    "Retry the import before clearing the old store.":
        "Reintentar la importación antes de borrar el almacenamiento antiguo.",
    "Now using {store}": "Ahora se usa {store}",
    "Clear the old password store":
        "Borrar el almacenamiento de contraseñas antiguo",
    "Delete the {count} passwords from {store}?":
        "¿Eliminar las {count} contraseñas de «{store}»?",
    "They are now stored in the new store. Deleting them here cannot be "
    "undone — and any other application that uses that store will no "
    "longer find them either.":
        "Ahora están guardadas en el nuevo almacenamiento. Eliminarlas aquí no "
        "se puede deshacer — y cualquier otra aplicación que use ese "
        "almacenamiento tampoco volverá a encontrarlas.",
    "Delete them": "Eliminarlas",
    "Deleted {count} passwords from the old store":
        "Se eliminaron {count} contraseñas del almacenamiento antiguo",

    # --- 内置库重置----------------------------------------------------------
    "Reset the built-in vault": "Restablecer la caja fuerte integrada",
    "This deletes every password stored in the built-in vault.":
        "Esto elimina todas las contraseñas guardadas en la caja fuerte "
        "integrada.",
    "They cannot be recovered — not even with the master password. Only "
    "do this if you no longer need them.":
        "No se pueden recuperar — ni siquiera con la contraseña maestra. Hazlo "
        "solo si ya no las necesitas.",
    "Delete the vault": "Eliminar la caja fuerte",
    "The built-in vault has been reset":
        "Se ha restablecido la caja fuerte integrada",

    # --- 换库时目标已有数据：保留 / 覆盖 / 合并-----------------------------------------
    "{store} already holds {count} of this app's passwords ({when}).":
        "«{store}» ya contiene {count} contraseñas de esta aplicación "
        "({when}).",
    "{source} holds {moving} for the same screens. Whichever side you "
    "drop is deleted for good.":
        "«{source}» contiene {moving} para las mismas pantallas. El lado que "
        "descartes se eliminará para siempre.",
    "Keep the target's passwords": "Mantener las contraseñas de destino",
    "Overwrite with the new passwords":
        "Sobrescribir con las contraseñas nuevas",
    "Merge…": "Combinar…",
    "Merge": "Combinar",
    "{adding} will be added, {identical} are identical and will be "
    "skipped, {conflicts} conflict.":
        "Se añadirán {adding}, {identical} son idénticas y se omitirán, "
        "{conflicts} están en conflicto.",
    "Screens in conflict: {names}": "Pantallas en conflicto: {names}",
    "Keep the target's version": "Mantener la versión de destino",
    "Use the new version": "Usar la versión nueva",
    "{count} entries could not be read; they will be left as they are.":
        "No se pudieron leer {count} entradas; se dejarán tal como están.",

    # --- 换库时源库锁着：一条都没搬，要说清楚 ---
    "The old store ({store}) is locked, so nothing was moved. "
    "Unlock it and switch again to bring the passwords over.":
        "El almacenamiento antiguo ({store}) está bloqueado, así que no "
        "se movió nada. Desbloquéalo y vuelve a cambiar para traer las "
        "contraseñas.",
}
