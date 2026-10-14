"""意大利语词条表。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的意大利语。
键顺序与 zh_cn.py 完全一致，按源文件分节，方便对照增删。

约定：
  * 值是整句，`{named}` 占位符集合必须与键完全一致（tests/test_i18n.py 会校验）；
  * 引号写进词条本身，意大利语用 «»；
  * 不翻译：`krfb-virtualmonitor` / `kscreen-doctor` / `kwinoutputconfig.json` /
    `systemd` 这类专名，Wayland / KWin / X11，以及 HTML 片段里的标签。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "Segui il sistema",
    ", ": ", ",  # join_list() 的列表分隔符
    "Cancel": "Annulla",
    "Close": "Chiudi",
    "Delete": "Elimina",
    "Log": "Registro",
    "Notes": "Note",
    "Password": "Password",
    "Port": "Porta",
    "Random": "Casuale",
    "Settings": "Impostazioni",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Gestore schermi virtuali Krfb",
    "3:2 Tablet": "Tablet 3:2",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "Gestisci gli schermi virtuali di krfb-virtualmonitor",

    # --- models -------------------------------------------------------------
    "Running": "In esecuzione",
    "Stopped": "Arrestato",
    "Exited unexpectedly": "Terminato inaspettatamente",
    "Starting": "Avvio in corso",
    "Failed to start": "Avvio non riuscito",
    "Unmanaged": "Non gestito",
    "Unnamed": "Senza nome",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "Portachiavi pronto",
    "Keyring locked": "Portachiavi bloccato",
    "No keyring service found": "Nessun servizio portachiavi trovato",
    "Keyring unavailable": "Portachiavi non disponibile",
    "Keyring not responding": "Il portachiavi non risponde",
    "Keyring error": "Errore del portachiavi",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "Il portafoglio KDE è chiuso; le password restano in memoria solo per questa sessione",
    "kwalletd is not running on the session bus":
        "kwalletd non è in esecuzione sul bus della sessione",
    "The KDE wallet subsystem is disabled, or no wallet exists":
        "Il sottosistema del portafoglio KDE è disattivato o non esiste alcun portafoglio",
    "The wallet did not respond in time; passwords are kept in "
    "memory for this session only":
        "Il portafoglio non ha risposto in tempo; le password restano in memoria solo per questa sessione",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "Impossibile analizzare il file di configurazione: {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "La versione della configurazione {found} non corrisponde a quella "
        "prevista {expected}; caricata come meglio possibile",
    "Unrecognized config format: {path}":
        "Formato di configurazione non riconosciuto: {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "krfb-virtualmonitor non trovato (atteso in {path})",
    "No password available": "Nessuna password disponibile",
    "Port {port} is already in use": "La porta {port} è già in uso",
    "Failed to start: {error}": "Avvio non riuscito: {error}",
    "The process vanished immediately after starting": "Il processo è sparito subito dopo l'avvio",
    "The name \"{name}\" is already taken by a managed screen":
        "Il nome «{name}» è già usato da uno schermo gestito",
    "Port {port} is already taken by a managed screen":
        "La porta {port} è già usata da uno schermo gestito",
    "Imported from an externally started process": "Importato da un processo avviato dall'esterno",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "krfb-virtualmonitor non trovato; assicurarsi che krfb sia installato "
        "(atteso in {path}).",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "kscreen-doctor non trovato, quindi la risoluzione e la scala reali di "
        "uno schermo virtuale non possono essere rilette; la verifica "
        "dell'avvio si limita a controllare la porta.",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor esiste ma non restituisce alcun output (la build "
        "pacchettizzata era stata compromessa dal suo Qt6 incluso e si "
        "interrompeva), quindi la risoluzione e la scala reali di uno schermo "
        "virtuale non possono essere rilette; la verifica dell'avvio si limita "
        "a controllare la porta.",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Questa è una sessione Wayland ma WAYLAND_DISPLAY non è impostata, "
        "quindi krfb non può creare monitor virtuali. Avviare il programma "
        "dal menu delle applicazioni o da un terminale.",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Questa non è una sessione Wayland. I monitor virtuali di krfb "
        "richiedono Wayland (e KWin); con X11 non funzionano affatto.",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} punta a un socket inesistente ({path}); "
        "krfb fallirà con «Virtual Monitors are only supported on Wayland».",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "Avviato dall'unità systemd {unit}, in cui KillMode=control-group ed "
        "ExitType=main fanno sì che chiudere questo programma termini anche "
        "tutti gli schermi virtuali. Avviarlo invece dal menu delle "
        "applicazioni, oppure aggiungere ExitType=cgroup a quell'unità.",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "All'accesso, ripristina gli schermi virtuali contrassegnati come "
        "«da tenere in esecuzione»",
    "Cannot write {path}: {error}": "Impossibile scrivere {path}: {error}",
    "Cannot delete {path}: {error}": "Impossibile eliminare {path}: {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "Avvia ridotto a icona nel vassoio di sistema (usato dall'avvio automatico)",
    "Config warning": "Avviso di configurazione",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor": "Gestore grafico per krfb-virtualmonitor",
    "New virtual screen": "Nuovo schermo virtuale",
    "Start all": "Avvia tutti",
    "Stop all": "Arresta tutti",
    "Scan for and adopt krfb processes started outside this app":
        "Cerca e adotta i processi krfb avviati al di fuori di questa applicazione",
    "Refresh now": "Aggiorna ora",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "Mostra finestra principale",
    "Quit": "Esci",
    "Restart": "Riavvia",
    "View": "Visualizza",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "Chiudere la finestra o ridurre a icona nel vassoio?",
    "Minimize to tray": "Riduci nel vassoio",
    "Quit the program": "Esci dal programma",
    "Remember my choice": "Ricorda la mia scelta",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "{count} schermi virtuali",
    "{count} running": "{count} in esecuzione",
    "{count} need attention": "{count} richiedono attenzione",
    "{count} environment problems": "{count} problemi dell'ambiente",
    "{count} environment problems detected": "Rilevati {count} problemi dell'ambiente",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "«{name}» è terminato: possibile crash o interruzione forzata",
    "{count} virtual screens have exited ({names}…)":
        "{count} schermi virtuali sono terminati ({names}…)",
    "The process exited immediately after starting": "Il processo è terminato subito dopo l'avvio",
    " (the port is listening, but no virtual display was created)":
        " (la porta è in ascolto, ma nessun display virtuale è stato creato)",
    " (the port isn't listening either)": " (neanche la porta è in ascolto)",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "Dopo {seconds} secondi l'output Virtual-{name} non è ancora "
        "apparso in KWin{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "Questo schermo virtuale non ha una password salvata (potrebbe venire "
        "da una vecchia configurazione); inserirne una ora.",
    "Cannot read the password from the keyring: {reason}":
        "Impossibile leggere la password dal portachiavi: {reason}",
    "Keyring": "Portachiavi",
    "Unlocked. Passwords will be saved to the keyring.":
        "Sbloccato. Le password verranno salvate nel portachiavi.",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "Sblocco non riuscito o scaduto. Le password restano utilizzabili per "
        "questa sessione, ma andranno reinserite dopo la chiusura.",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "Riavvio necessario",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "«{name}» è in esecuzione. Le modifiche a risoluzione, scala o porta "
        "non hanno effetto su uno schermo già creato; lo schermo virtuale "
        "deve essere riavviato perché abbiano effetto.",
    "Restart it now?": "Riavviarlo adesso?",
    "Restart now": "Riavvia ora",
    "Later": "Più tardi",
    "Delete virtual screen": "Elimina schermo virtuale",
    "Delete \"{name}\"?": "Eliminare «{name}»?",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "Questo schermo virtuale è in esecuzione; eliminandolo verrà prima arrestato.",
    "This action cannot be undone.": "Questa azione non può essere annullata.",
    "The saved password is removed from the keyring too.":
        "Anche la password salvata verrà rimossa dal portachiavi.",
    "No unmanaged krfb processes found": "Nessun processo krfb non gestito trovato",
    "{name}: {error}": "{name}: {error}",
    "Some could not be imported": "Alcuni non sono stati importati",
    "Start failed": "Avvio non riuscito",
    "\"{name}\" failed to start": "Avvio di «{name}» non riuscito",
    "View full log": "Mostra registro completo",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "Ridotto a icona nel vassoio. Gli schermi virtuali continuano a "
        "funzionare e non vengono arrestati quando si esce dall'applicazione.",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left": "Seleziona uno schermo virtuale a sinistra",
    "or click \"New\" in the top right": "oppure fai clic su «Nuovo» in alto a destra",
    "Requested": "Richiesto",
    "Actual": "Effettivo",
    "Address": "Indirizzo",
    "Status": "Stato",
    "Copy the VNC address": "Copia l'indirizzo VNC",
    "Copy the connection password": "Copia la password di connessione",
    "Copied": "Copiato",
    "Start": "Avvia",
    "Stop": "Arresta",
    "Edit": "Modifica",
    "{actual}  ⚠ differs from the requested value": "{actual}  ⚠ diverso dal valore richiesto",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "La password è nascosta solo nell'interfaccia; a krfb viene passata in chiaro",
    "Running, PID {pid}": "In esecuzione, PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "Il processo non c'è più ma è contrassegnato come «da tenere in esecuzione»",
    "It may have crashed, been killed, or the machine was rebooted":
        "Potrebbe essersi bloccato, essere stato terminato o il computer è stato riavviato",
    "Creating, waiting for the KWin output…": "Creazione in corso, in attesa dell'output di KWin…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "Modificare risoluzione o scala mentre è in esecuzione non ha effetto "
        "sullo schermo già creato; lo schermo virtuale deve essere riavviato",
    "Edit parameters": "Modifica parametri",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · Porta {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "Nessuno schermo virtuale\nFai clic su «Nuovo» per crearne uno",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "Modifica schermo virtuale",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "es. Tablet (diventa l'output «Virtual-<name>» di KWin)",
    "Custom…": "Personalizzato…",
    "Auto": "Auto",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "Scegli una porta non in uso e non assegnata a un altro schermo virtuale",
    "Show / hide the password": "Mostra / nascondi la password",
    "Copy the password": "Copia la password",
    "Optional, e.g. \"second screen for the iPad\"":
        "Facoltativo, ad es. «secondo schermo per l'iPad»",
    "Start at login": "Avvia all'accesso",
    "Save": "Salva",
    "Name": "Nome",
    "Resolution": "Risoluzione",
    "Scale DPR": "Scala DPR",
    "Command that will be executed": "Comando che verrà eseguito",
    "The name can't be empty": "Il nome non può essere vuoto",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "«{name}» è già in uso (il nome dell'output KWin Virtual-{name} "
        "deve essere univoco)",
    "Port {port} is already used by another virtual screen":
        "La porta {port} è già usata da un altro schermo virtuale",
    "Port {port} is already taken by another program on the system":
        "La porta {port} è già occupata da un altro programma del sistema",
    "The password can't be empty": "La password non può essere vuota",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "L'autenticazione VNC usa solo i primi 8 caratteri; gli altri {extra} "
        "non hanno alcun effetto (password effettiva: {effective})",
    "VNC authentication uses all 8 characters": "L'autenticazione VNC usa tutti gli 8 caratteri",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "Password richiesta",
    "Enter the VNC password for this virtual screen":
        "Inserisci la password VNC per questo schermo virtuale",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "La password viene passata al processo krfb in chiaro, quindi altri "
        "utenti locali possono vederla con ps; l'autenticazione VNC usa solo "
        "i primi 8 caratteri.",
    "Use": "Usa",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found": "Trovati schermi virtuali non gestiti",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "Questi processi krfb-virtualmonitor non sono stati avviati da questa "
        "applicazione. Importali per gestirli da qui.",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · Porta {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "risoluzione sconosciuta",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ Il pacchetto è stato aggiornato; "
        "si consiglia di riavviare questo schermo virtuale</span>",
    "Import selected": "Importa selezionati",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "Lingua",
    "Closing the window": "Alla chiusura della finestra",
    "Ask every time": "Chiedi ogni volta",
    "Launch at login": "Avvio automatico",
    "Start at login (tray mode)": "Avvia all'accesso (modalità vassoio)",
    "Password storage": "Archiviazione delle password",
    "Unlock keyring": "Sblocca portachiavi",
    "Environment": "Ambiente",
    "About": "Informazioni",
    "No problems found": "Nessun problema rilevato",
    "not installed": "non installato",
    "unknown": "sconosciuto",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "Impossibile salvare la preferenza ({error}); "
        "resta attiva solo per questa sessione.",
    "Config:": "Configurazione:",
    "Runtime state:": "Stato di esecuzione:",
    "Logs:": "Registri:",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "Cerca… (premi Invio per la corrispondenza successiva)",
    "Auto-scroll": "Scorrimento automatico",
    "Reload": "Ricarica",
    "Open containing folder": "Apri la cartella contenitrice",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "(Ancora nessun output)\n\nRimane vuoto finché lo schermo virtuale non viene avviato.",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} righe   ·   {size} byte",
    "No match for \"{needle}\"": "Nessuna corrispondenza per «{needle}»",
    "Refreshes every {seconds} s": "Aggiornamento ogni {seconds} s",
}
