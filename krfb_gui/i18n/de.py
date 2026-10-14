"""德语词条表（Deutsch）。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的德语；分节与顺序与 zh_cn.py 一致。
`{named}` 占位符集合必须与键完全一致（tests/test_i18n.py 会校验）；
引号写进词条本身 —— 德语用 „ “，命令名、路径、环境变量一律保留原文。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "Dem System folgen",
    ", ": ", ",  # join_list() 的列表分隔符
    "Cancel": "Abbrechen",
    "Close": "Schließen",
    "Delete": "Löschen",
    "Log": "Protokoll",
    "Notes": "Notizen",
    "Password": "Passwort",
    "Port": "Port",
    "Random": "Zufällig",
    "Settings": "Einstellungen",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Krfb-Verwaltung für virtuelle Bildschirme",
    "3:2 Tablet": "3:2-Tablet",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "Virtuelle Bildschirme mit krfb-virtualmonitor verwalten",

    # --- models -------------------------------------------------------------
    "Running": "Läuft",
    "Stopped": "Gestoppt",
    "Exited unexpectedly": "Unerwartet beendet",
    "Starting": "Wird gestartet",
    "Failed to start": "Start fehlgeschlagen",
    "Unmanaged": "Nicht verwaltet",
    "Unnamed": "Unbenannt",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "Schlüsselbund bereit",
    "Keyring locked": "Schlüsselbund gesperrt",
    "No keyring service found": "Kein Schlüsselbund-Dienst gefunden",
    "Keyring unavailable": "Schlüsselbund nicht verfügbar",
    "Keyring not responding": "Schlüsselbund reagiert nicht",
    "Keyring error": "Schlüsselbund-Fehler",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "Die KDE-Brieftasche ist geschlossen; Passwörter werden nur für diese Sitzung im Arbeitsspeicher gehalten",
    "kwalletd is not running on the session bus":
        "Auf dem Sitzungsbus läuft kein kwalletd",
    "The KDE wallet subsystem is disabled, or no wallet exists":
        "Das KDE-Brieftaschen-Subsystem ist deaktiviert oder es existiert keine Brieftasche",
    "The wallet did not respond in time; passwords are kept in "
    "memory for this session only":
        "Die Brieftasche hat nicht rechtzeitig geantwortet; Passwörter werden nur für diese Sitzung im Arbeitsspeicher gehalten",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "Die Konfigurationsdatei kann nicht gelesen werden: {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "Konfigurationsversion {found} stimmt nicht mit der erwarteten "
        "{expected} überein; soweit möglich wurde sie dennoch geladen",
    "Unrecognized config format: {path}":
        "Unbekanntes Konfigurationsformat: {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "krfb-virtualmonitor nicht gefunden (erwartet unter {path})",
    "No password available": "Kein Passwort verfügbar",
    "Port {port} is already in use": "Port {port} wird bereits verwendet",
    "Failed to start: {error}": "Start fehlgeschlagen: {error}",
    "The process vanished immediately after starting":
        "Der Prozess ist direkt nach dem Start verschwunden",
    "The name \"{name}\" is already taken by a managed screen":
        "Der Name „{name}“ wird bereits von einem verwalteten Bildschirm verwendet",
    "Port {port} is already taken by a managed screen":
        "Port {port} wird bereits von einem verwalteten Bildschirm verwendet",
    "Imported from an externally started process":
        "Aus einem extern gestarteten Prozess importiert",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "krfb-virtualmonitor nicht gefunden; bitte prüfen, ob krfb installiert "
        "ist (erwartet unter {path}).",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "kscreen-doctor wurde nicht gefunden, daher lassen sich die tatsächliche "
        "Auflösung und Skalierung eines virtuellen Bildschirms nicht auslesen; "
        "die Startprüfung beschränkt sich auf die Prüfung des Ports.",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor ist vorhanden, liefert aber keine Ausgabe (die gepackte "
        "Version wurde einmal durch ihr mitgeliefertes Qt6 gestört und brach "
        "ab), daher lassen sich die tatsächliche Auflösung und Skalierung eines "
        "virtuellen Bildschirms nicht auslesen; die Startprüfung beschränkt "
        "sich auf die Prüfung des Ports.",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Dies ist eine Wayland-Sitzung, aber WAYLAND_DISPLAY ist nicht gesetzt, "
        "daher kann krfb keine virtuellen Monitore erstellen. Bitte dieses "
        "Programm über den Desktop-Starter oder ein Terminal starten.",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Dies ist keine Wayland-Sitzung. Die virtuellen Monitore von krfb "
        "erfordern Wayland (und KWin); unter X11 schlagen sie direkt fehl.",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} verweist auf einen Socket, der nicht "
        "existiert ({path}); krfb wird mit "
        "„Virtual Monitors are only supported on Wayland“ fehlschlagen.",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "Gestartet durch systemd-Unit {unit}: Deren KillMode=control-group und "
        "ExitType=main führen dazu, dass beim Beenden dieses Programms alle "
        "virtuellen Bildschirme mit beendet werden. Bitte stattdessen über den "
        "Desktop-Starter starten oder der Unit ExitType=cgroup hinzufügen.",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "Virtuelle Bildschirme mit der Markierung „Soll laufen“ beim Anmelden "
        "wiederherstellen",
    "Cannot write {path}: {error}": "Kann {path} nicht schreiben: {error}",
    "Cannot delete {path}: {error}": "Kann {path} nicht löschen: {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "Minimiert im Systemabschnitt starten (für Autostart)",
    "Config warning": "Konfigurationswarnung",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor":
        "Grafische Verwaltung für krfb-virtualmonitor",
    "New virtual screen": "Neuer virtueller Bildschirm",
    "Start all": "Alle starten",
    "Stop all": "Alle stoppen",
    "Scan for and adopt krfb processes started outside this app":
        "Nach krfb-Prozessen suchen, die außerhalb dieser Anwendung gestartet "
        "wurden, und sie übernehmen",
    "Refresh now": "Jetzt aktualisieren",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "Hauptfenster anzeigen",
    "Quit": "Beenden",
    "Restart": "Neu starten",
    "View": "Anzeigen",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "Fenster schließen oder in den Systemabschnitt minimieren?",
    "Minimize to tray": "In den Systemabschnitt minimieren",
    "Quit the program": "Programm beenden",
    "Remember my choice": "Auswahl merken",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "{count} virtuelle Bildschirme",
    "{count} running": "{count} laufend",
    "{count} need attention": "{count} benötigen Aufmerksamkeit",
    "{count} environment problems": "{count} Umgebungsprobleme",
    "{count} environment problems detected":
        "{count} Umgebungsprobleme gefunden",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "„{name}“ wurde beendet — möglicherweise abgestürzt oder abgeschossen",
    "{count} virtual screens have exited ({names}…)":
        "{count} virtuelle Bildschirme wurden beendet ({names}…)",
    "The process exited immediately after starting":
        "Der Prozess wurde direkt nach dem Start beendet",
    " (the port is listening, but no virtual display was created)":
        " (der Port ist erreichbar, aber es wurde kein virtueller Bildschirm "
        "erstellt)",
    " (the port isn't listening either)":
        " (der Port ist ebenfalls nicht erreichbar)",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "{seconds} Sekunden gewartet, die Ausgabe Virtual-{name} ist "
        "aber noch nicht in KWin erschienen{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "Für diesen virtuellen Bildschirm ist kein Passwort gespeichert "
        "(er stammt möglicherweise aus einer alten Konfiguration); "
        "bitte jetzt eines eingeben.",
    "Cannot read the password from the keyring: {reason}":
        "Das Passwort kann nicht aus dem Schlüsselbund gelesen werden: {reason}",
    "Keyring": "Schlüsselbund",
    "Unlocked. Passwords will be saved to the keyring.":
        "Entsperrt. Passwörter werden im Schlüsselbund gespeichert.",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "Entsperren fehlgeschlagen oder Zeitüberschreitung. Die Passwörter "
        "können in dieser Sitzung weiterhin verwendet werden, müssen aber nach "
        "dem Beenden erneut eingegeben werden.",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "Neustart erforderlich",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "„{name}“ läuft. Änderungen an Auflösung, Skalierung oder Port wirken "
        "sich nicht auf einen bereits erstellten Bildschirm aus; der virtuelle "
        "Bildschirm muss neu gestartet werden, damit sie wirksam werden.",
    "Restart it now?": "Jetzt neu starten?",
    "Restart now": "Jetzt neu starten",
    "Later": "Später",
    "Delete virtual screen": "Virtuellen Bildschirm löschen",
    "Delete \"{name}\"?": "„{name}“ löschen?",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "Dieser virtuelle Bildschirm läuft gerade; beim Löschen wird er zuerst "
        "gestoppt.",
    "This action cannot be undone.":
        "Diese Aktion kann nicht rückgängig gemacht werden.",
    "The saved password is removed from the keyring too.":
        "Das gespeicherte Passwort wird ebenfalls aus dem Schlüsselbund entfernt.",
    "No unmanaged krfb processes found":
        "Keine nicht verwalteten krfb-Prozesse gefunden",
    "{name}: {error}": "{name}: {error}",
    "Some could not be imported": "Einige konnten nicht importiert werden",
    "Start failed": "Start fehlgeschlagen",
    "\"{name}\" failed to start": "„{name}“ konnte nicht gestartet werden",
    "View full log": "Vollständiges Protokoll anzeigen",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "In den Systemabschnitt minimiert. Die virtuellen Bildschirme laufen "
        "weiter und werden beim Beenden dieser Anwendung nicht gestoppt.",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left":
        "Links einen virtuellen Bildschirm auswählen",
    "or click \"New\" in the top right": "oder oben rechts auf „Neu“ klicken",
    "Requested": "Angefordert",
    "Actual": "Tatsächlich",
    "Address": "Adresse",
    "Status": "Status",
    "Copy the VNC address": "VNC-Adresse kopieren",
    "Copy the connection password": "Verbindungspasswort kopieren",
    "Copied": "Kopiert",
    "Start": "Starten",
    "Stop": "Stoppen",
    "Edit": "Bearbeiten",
    "{actual}  ⚠ differs from the requested value":
        "{actual}  ⚠ weicht vom angeforderten Wert ab",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "Das Passwort wird nur in der Oberfläche verborgen; "
        "es wird im Klartext an krfb übergeben",
    "Running, PID {pid}": "Läuft, PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "Prozess ist verschwunden, aber als „Soll laufen“ markiert",
    "It may have crashed, been killed, or the machine was rebooted":
        "Er ist möglicherweise abgestürzt, wurde abgeschossen, oder der Rechner "
        "wurde neu gestartet",
    "Creating, waiting for the KWin output…":
        "Wird erstellt, warte auf die KWin-Ausgabe…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "Das Ändern von Auflösung oder Skalierung im laufenden Betrieb hat "
        "keine Auswirkung auf den erstellten Bildschirm; der virtuelle "
        "Bildschirm muss neu gestartet werden",
    "Edit parameters": "Parameter bearbeiten",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · Port {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "Noch keine virtuellen Bildschirme\n"
        "Zum Erstellen auf „Neu“ klicken",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "Virtuellen Bildschirm bearbeiten",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "z. B. Tablet (wird zur KWin-Ausgabe „Virtual-<name>“)",
    "Custom…": "Benutzerdefiniert…",
    "Auto": "Automatisch",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "Einen Port auswählen, der weder belegt ist "
        "noch einem anderen virtuellen Bildschirm zugewiesen wurde",
    "Show / hide the password": "Passwort ein-/ausblenden",
    "Copy the password": "Passwort kopieren",
    "Optional, e.g. \"second screen for the iPad\"":
        "Optional, z. B. „zweiter Bildschirm für das iPad“",
    "Start at login": "Beim Anmelden starten",
    "Save": "Speichern",
    "Name": "Name",
    "Resolution": "Auflösung",
    "Scale DPR": "Skalierung DPR",
    "Command that will be executed": "Befehl, der ausgeführt wird",
    "The name can't be empty": "Der Name darf nicht leer sein",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "„{name}“ wird bereits verwendet "
        "(der KWin-Ausgabename Virtual-{name} muss eindeutig sein)",
    "Port {port} is already used by another virtual screen":
        "Port {port} wird bereits von einem anderen virtuellen Bildschirm "
        "verwendet",
    "Port {port} is already taken by another program on the system":
        "Port {port} wird bereits von einem anderen Programm im System verwendet",
    "The password can't be empty": "Das Passwort darf nicht leer sein",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "Die VNC-Authentifizierung verwendet nur die ersten 8 Zeichen; "
        "die restlichen {extra} haben keine Wirkung "
        "(wirksames Passwort: {effective})",
    "VNC authentication uses all 8 characters":
        "Die VNC-Authentifizierung verwendet alle 8 Zeichen",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "Passwort erforderlich",
    "Enter the VNC password for this virtual screen":
        "VNC-Passwort für diesen virtuellen Bildschirm eingeben",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "Das Passwort wird im Klartext an den krfb-Prozess übergeben und ist "
        "für andere lokale Benutzer über ps sichtbar; die "
        "VNC-Authentifizierung verwendet nur die ersten 8 Zeichen.",
    "Use": "Verwenden",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found":
        "Nicht verwaltete virtuelle Bildschirme gefunden",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "Diese krfb-virtualmonitor-Prozesse wurden nicht von dieser Anwendung "
        "gestartet. Importieren, um sie hier zu verwalten.",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · Port {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "unbekannte Auflösung",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ Das Paket wurde aktualisiert; "
        "es wird empfohlen, diesen virtuellen Bildschirm neu zu starten</span>",
    "Import selected": "Ausgewählte importieren",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "Sprache",
    "Closing the window": "Beim Schließen des Fensters",
    "Ask every time": "Jedes Mal fragen",
    "Launch at login": "Beim Anmelden starten",
    "Start at login (tray mode)":
        "Beim Anmelden starten (Systemabschnitt-Modus)",
    "Password storage": "Passwortspeicherung",
    "Unlock keyring": "Schlüsselbund entsperren",
    "Environment": "Umgebung",
    "About": "Über",
    "No problems found": "Keine Probleme gefunden",
    "not installed": "nicht installiert",
    "unknown": "unbekannt",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "Die Einstellung konnte nicht gespeichert werden ({error}); "
        "sie gilt nur für diese Sitzung.",
    "Config:": "Konfiguration:",
    "Runtime state:": "Laufzeitstatus:",
    "Logs:": "Protokolle:",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "Suchen… (Eingabetaste springt zum nächsten Treffer)",
    "Auto-scroll": "Automatisch scrollen",
    "Reload": "Neu laden",
    "Open containing folder": "Enthaltenden Ordner öffnen",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "(Noch keine Ausgabe)\n\n"
        "Hier steht erst etwas, wenn der virtuelle Bildschirm gestartet wurde.",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} Zeilen   ·   {size} Byte",
    "No match for \"{needle}\"": "Kein Treffer für „{needle}“",
    "Refreshes every {seconds} s": "Aktualisierung alle {seconds} s",
}
