"""法语词条表（Français）。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的法语；分节与顺序与 zh_cn.py 一致。
`{named}` 占位符集合必须与键完全一致（tests/test_i18n.py 会校验）；
引号写进词条本身 —— 法语用 «  »，命令名、路径、环境变量一律保留原文。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "Suivre le système",
    ", ": ", ",  # join_list() 的列表分隔符
    "Cancel": "Annuler",
    "Close": "Fermer",
    "Delete": "Supprimer",
    "Log": "Journal",
    "Notes": "Notes",
    "Password": "Mot de passe",
    "Port": "Port",
    "Random": "Aléatoire",
    "Settings": "Paramètres",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Gestionnaire d'écrans virtuels Krfb",
    "3:2 Tablet": "Tablette 3:2",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "Gérer les écrans virtuels de krfb-virtualmonitor",

    # --- models -------------------------------------------------------------
    "Running": "En cours d'exécution",
    "Stopped": "Arrêté",
    "Exited unexpectedly": "Arrêt inattendu",
    "Starting": "Démarrage",
    "Failed to start": "Échec du démarrage",
    "Unmanaged": "Non géré",
    "Unnamed": "Sans nom",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "Trousseau prêt",
    "Keyring locked": "Trousseau verrouillé",
    "No keyring service found": "Aucun service de trousseau trouvé",
    "Keyring unavailable": "Trousseau indisponible",
    "Keyring not responding": "Le trousseau ne répond pas",
    "Keyring error": "Erreur du trousseau",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "Le portefeuille KDE est fermé ; les mots de passe sont conservés en mémoire pour cette session uniquement",
    "kwalletd is not running on the session bus":
        "kwalletd n'est pas lancé sur le bus de session",
    "The KDE wallet subsystem is disabled, or no wallet exists":
        "Le sous-système de portefeuille KDE est désactivé ou aucun portefeuille n'existe",
    "The wallet did not respond in time; passwords are kept in "
    "memory for this session only":
        "Le portefeuille n'a pas répondu à temps ; les mots de passe sont conservés en mémoire pour cette session uniquement",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "Impossible d'analyser le fichier de configuration : {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "La version de configuration {found} ne correspond pas à la version "
        "attendue {expected} ; chargement effectué au mieux",
    "Unrecognized config format: {path}":
        "Format de configuration non reconnu : {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "krfb-virtualmonitor introuvable (attendu dans {path})",
    "No password available": "Aucun mot de passe disponible",
    "Port {port} is already in use": "Le port {port} est déjà utilisé",
    "Failed to start: {error}": "Échec du démarrage : {error}",
    "The process vanished immediately after starting":
        "Le processus a disparu immédiatement après son démarrage",
    "The name \"{name}\" is already taken by a managed screen":
        "Le nom « {name} » est déjà utilisé par un écran géré",
    "Port {port} is already taken by a managed screen":
        "Le port {port} est déjà utilisé par un écran géré",
    "Imported from an externally started process":
        "Importé depuis un processus lancé en externe",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "krfb-virtualmonitor introuvable ; vérifier que krfb est installé "
        "(attendu dans {path}).",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "kscreen-doctor est introuvable, la résolution et l'échelle réelles "
        "d'un écran virtuel ne peuvent donc pas être relues ; la vérification "
        "du démarrage se limite au contrôle du port.",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor existe mais ne renvoie aucune sortie (la version "
        "empaquetée a déjà été perturbée par son Qt6 intégré et a avorté), la "
        "résolution et l'échelle réelles d'un écran virtuel ne peuvent donc pas "
        "être relues ; la vérification du démarrage se limite au contrôle du port.",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Il s'agit d'une session Wayland mais WAYLAND_DISPLAY n'est pas "
        "défini, krfb ne peut donc pas créer de moniteurs virtuels. "
        "Lancer ce programme depuis le lanceur du bureau ou un terminal.",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Ce n'est pas une session Wayland. Les moniteurs virtuels de krfb "
        "nécessitent Wayland (et KWin) ; sous X11, ils échouent d'emblée.",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} pointe vers une socket qui n'existe pas "
        "({path}) ; krfb échouera avec "
        "« Virtual Monitors are only supported on Wayland ».",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "Démarré par l'unité systemd {unit}, dont KillMode=control-group et "
        "ExitType=main font que quitter ce programme arrête tous les écrans "
        "virtuels avec lui. Le lancer plutôt depuis le lanceur du bureau, ou "
        "ajouter ExitType=cgroup à cette unité.",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "Restaurer à la connexion les écrans virtuels marqués "
        "« doit être en cours d'exécution »",
    "Cannot write {path}: {error}":
        "Impossible d'écrire {path} : {error}",
    "Cannot delete {path}: {error}":
        "Impossible de supprimer {path} : {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "Démarrer réduit dans la zone de notification "
        "(utilisé par le démarrage automatique)",
    "Config warning": "Avertissement de configuration",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor":
        "Gestionnaire graphique pour krfb-virtualmonitor",
    "New virtual screen": "Nouvel écran virtuel",
    "Start all": "Tout démarrer",
    "Stop all": "Tout arrêter",
    "Scan for and adopt krfb processes started outside this app":
        "Rechercher et adopter les processus krfb lancés hors de cette "
        "application",
    "Refresh now": "Actualiser maintenant",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "Afficher la fenêtre principale",
    "Quit": "Quitter",
    "Restart": "Redémarrer",
    "View": "Afficher",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "Fermer la fenêtre ou réduire dans la zone de notification ?",
    "Minimize to tray": "Réduire dans la zone de notification",
    "Quit the program": "Quitter le programme",
    "Remember my choice": "Se souvenir de mon choix",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "{count} écrans virtuels",
    "{count} running": "{count} en cours d'exécution",
    "{count} need attention": "{count} nécessitent une intervention",
    "{count} environment problems": "{count} problèmes d'environnement",
    "{count} environment problems detected":
        "{count} problèmes d'environnement détectés",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "« {name} » s'est arrêté — il a peut-être planté ou été tué",
    "{count} virtual screens have exited ({names}…)":
        "{count} écrans virtuels se sont arrêtés ({names}…)",
    "The process exited immediately after starting":
        "Le processus s'est arrêté immédiatement après son démarrage",
    " (the port is listening, but no virtual display was created)":
        " (le port est en écoute, mais aucun écran virtuel n'a été créé)",
    " (the port isn't listening either)":
        " (le port n'est pas non plus en écoute)",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "{seconds} secondes d'attente et la sortie Virtual-{name} n'est "
        "toujours pas apparue dans KWin{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "Cet écran virtuel n'a pas de mot de passe enregistré (il provient "
        "peut-être d'une ancienne configuration) ; en saisir un maintenant.",
    "Cannot read the password from the keyring: {reason}":
        "Impossible de lire le mot de passe depuis le trousseau : {reason}",
    "Keyring": "Trousseau",
    "Unlocked. Passwords will be saved to the keyring.":
        "Déverrouillé. Les mots de passe seront enregistrés dans le trousseau.",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "Le déverrouillage a échoué ou a expiré. Les mots de passe restent "
        "utilisables pour cette session, mais devront être saisis à nouveau "
        "après avoir quitté.",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "Redémarrage nécessaire",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "« {name} » est en cours d'exécution. Les modifications de résolution, "
        "d'échelle ou de port n'affectent pas un écran déjà créé ; l'écran "
        "virtuel doit être redémarré pour qu'elles prennent effet.",
    "Restart it now?": "Le redémarrer maintenant ?",
    "Restart now": "Redémarrer maintenant",
    "Later": "Plus tard",
    "Delete virtual screen": "Supprimer l'écran virtuel",
    "Delete \"{name}\"?": "Supprimer « {name} » ?",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "Cet écran virtuel est en cours d'exécution ; le supprimer "
        "l'arrêtera d'abord.",
    "This action cannot be undone.": "Cette action est irréversible.",
    "The saved password is removed from the keyring too.":
        "Le mot de passe enregistré est également supprimé du trousseau.",
    "No unmanaged krfb processes found":
        "Aucun processus krfb non géré trouvé",
    "{name}: {error}": "{name} : {error}",
    "Some could not be imported": "Certains n'ont pas pu être importés",
    "Start failed": "Échec du démarrage",
    "\"{name}\" failed to start": "« {name} » n'a pas pu démarrer",
    "View full log": "Afficher le journal complet",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "Réduit dans la zone de notification. Les écrans virtuels continuent "
        "de fonctionner et ne sont pas arrêtés en quittant cette application.",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left":
        "Sélectionner un écran virtuel à gauche",
    "or click \"New\" in the top right":
        "ou cliquer sur « Nouveau » en haut à droite",
    "Requested": "Demandé",
    "Actual": "Réel",
    "Address": "Adresse",
    "Status": "État",
    "Copy the VNC address": "Copier l'adresse VNC",
    "Copy the connection password": "Copier le mot de passe de connexion",
    "Copied": "Copié",
    "Start": "Démarrer",
    "Stop": "Arrêter",
    "Edit": "Modifier",
    "{actual}  ⚠ differs from the requested value":
        "{actual}  ⚠ diffère de la valeur demandée",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "Le mot de passe n'est masqué que dans l'interface ; "
        "il est transmis à krfb en clair",
    "Running, PID {pid}": "En cours d'exécution, PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "Le processus a disparu mais est marqué "
        "« doit être en cours d'exécution »",
    "It may have crashed, been killed, or the machine was rebooted":
        "Il a peut-être planté, été tué, ou la machine a été redémarrée",
    "Creating, waiting for the KWin output…":
        "Création en cours, en attente de la sortie KWin…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "Modifier la résolution ou l'échelle en cours d'exécution n'a aucun "
        "effet sur l'écran déjà créé ; l'écran virtuel doit être redémarré",
    "Edit parameters": "Modifier les paramètres",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · Port {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "Aucun écran virtuel pour l'instant\n"
        "Cliquer sur « Nouveau » pour en créer un",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "Modifier l'écran virtuel",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "ex. Tablette (devient la sortie KWin « Virtual-<name> »)",
    "Custom…": "Personnalisé…",
    "Auto": "Automatique",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "Choisir un port qui n'est ni utilisé "
        "ni attribué à un autre écran virtuel",
    "Show / hide the password": "Afficher / masquer le mot de passe",
    "Copy the password": "Copier le mot de passe",
    "Optional, e.g. \"second screen for the iPad\"":
        "Facultatif, ex. « second écran pour l'iPad »",
    "Start at login": "Démarrer à la connexion",
    "Save": "Enregistrer",
    "Name": "Nom",
    "Resolution": "Résolution",
    "Scale DPR": "Échelle DPR",
    "Command that will be executed": "Commande qui sera exécutée",
    "The name can't be empty": "Le nom ne peut pas être vide",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "« {name} » est déjà utilisé "
        "(le nom de sortie KWin Virtual-{name} doit être unique)",
    "Port {port} is already used by another virtual screen":
        "Le port {port} est déjà utilisé par un autre écran virtuel",
    "Port {port} is already taken by another program on the system":
        "Le port {port} est déjà utilisé par un autre programme du système",
    "The password can't be empty": "Le mot de passe ne peut pas être vide",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "L'authentification VNC n'utilise que les 8 premiers caractères ; "
        "les {extra} restants n'ont aucun effet "
        "(mot de passe effectif : {effective})",
    "VNC authentication uses all 8 characters":
        "L'authentification VNC utilise les 8 caractères",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "Mot de passe requis",
    "Enter the VNC password for this virtual screen":
        "Saisir le mot de passe VNC de cet écran virtuel",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "Le mot de passe est transmis au processus krfb en clair, les autres "
        "utilisateurs locaux peuvent donc le voir via ps ; l'authentification "
        "VNC n'utilise que les 8 premiers caractères.",
    "Use": "Utiliser",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found": "Écrans virtuels non gérés détectés",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "Ces processus krfb-virtualmonitor n'ont pas été lancés par cette "
        "application. Les importer pour les gérer ici.",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · Port {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "résolution inconnue",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ Le paquet a été mis à jour ; "
        "il est recommandé de redémarrer cet écran virtuel</span>",
    "Import selected": "Importer la sélection",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "Langue",
    "Closing the window": "Fermeture de la fenêtre",
    "Ask every time": "Demander à chaque fois",
    "Launch at login": "Lancer à la connexion",
    "Start at login (tray mode)":
        "Démarrer à la connexion (mode zone de notification)",
    "Password storage": "Stockage des mots de passe",
    "Unlock keyring": "Déverrouiller le trousseau",
    "Environment": "Environnement",
    "About": "À propos",
    "No problems found": "Aucun problème détecté",
    "not installed": "non installé",
    "unknown": "inconnu",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "Impossible d'enregistrer la préférence ({error}) ; "
        "elle reste effective pour cette session uniquement.",
    "Config:": "Configuration :",
    "Runtime state:": "État d'exécution :",
    "Logs:": "Journaux :",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "Rechercher… (appuyer sur Entrée pour le résultat suivant)",
    "Auto-scroll": "Défilement automatique",
    "Reload": "Recharger",
    "Open containing folder": "Ouvrir le dossier contenant",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "(Aucune sortie pour l'instant)\n\n"
        "Cette zone reste vide tant que l'écran virtuel n'est pas démarré.",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} lignes   ·   {size} octets",
    "No match for \"{needle}\"": "Aucun résultat pour « {needle} »",
    "Refreshes every {seconds} s": "Actualisation toutes les {seconds} s",
}
