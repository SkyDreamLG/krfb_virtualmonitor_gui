"""巴西葡萄牙语词条表。

键是**英文原文**（`i18n.tr()` 的 key），值是要显示的巴西葡萄牙语。
键顺序与 zh_cn.py 完全一致，按源文件分节，方便对照增删。

约定：
  * 值是整句，`{named}` 占位符集合必须与键完全一致（tests/test_i18n.py 会校验）；
  * 引号写进词条本身，巴西葡语用 “”；
  * 不翻译：`krfb-virtualmonitor` / `kscreen-doctor` / `kwinoutputconfig.json` /
    `systemd` 这类专名，Wayland / KWin / X11，以及 HTML 片段里的标签。
"""

CATALOG: dict[str, str] = {
    # --- 通用 ---------------------------------------------------------------
    "Follow system": "Seguir o sistema",
    ", ": ", ",  # join_list() 的列表分隔符
    "Cancel": "Cancelar",
    "Close": "Fechar",
    "Delete": "Excluir",
    "Log": "Registro",
    "Notes": "Observações",
    "Password": "Senha",
    "Port": "Porta",
    "Random": "Aleatória",
    "Settings": "Configurações",

    # --- constants ----------------------------------------------------------
    "Krfb Virtual Screen Manager": "Gerenciador de telas virtuais do Krfb",
    "3:2 Tablet": "Tablet 3:2",
    # 应用菜单项的描述，由 packaging/install-desktop.sh 写进 .desktop
    "Manage krfb-virtualmonitor virtual screens":
        "Gerencie telas virtuais do krfb-virtualmonitor",

    # --- models -------------------------------------------------------------
    "Running": "Em execução",
    "Stopped": "Parada",
    "Exited unexpectedly": "Fechou inesperadamente",
    "Starting": "Iniciando",
    "Failed to start": "Falha ao iniciar",
    "Unmanaged": "Não gerenciada",
    "Unnamed": "Sem nome",

    # --- secrets ------------------------------------------------------------
    "Keyring ready": "Chaveiro pronto",
    "Keyring locked": "Chaveiro bloqueado",
    "No keyring service found": "Nenhum serviço de chaveiro encontrado",
    "Keyring unavailable": "Chaveiro indisponível",
    "Keyring not responding": "O chaveiro não está respondendo",
    "Keyring error": "Erro no chaveiro",
    "The KDE wallet is closed; passwords are kept in memory for "
    "this session only":
        "A carteira do KDE está fechada; as senhas ficam na memória apenas nesta sessão",
    "kwalletd is not running on the session bus":
        "kwalletd não está em execução no barramento da sessão",

    # --- store --------------------------------------------------------------
    "Cannot parse the config file: {path}":
        "Não foi possível analisar o arquivo de configuração: {path}",
    "Config version {found} doesn't match the expected {expected}; "
    "loaded on a best-effort basis":
        "A versão da configuração {found} não corresponde à esperada "
        "{expected}; carregada da melhor forma possível",
    "Unrecognized config format: {path}":
        "Formato de configuração não reconhecido: {path}",

    # --- manager ------------------------------------------------------------
    "krfb-virtualmonitor not found (expected at {path})":
        "krfb-virtualmonitor não encontrado (esperado em {path})",
    "No password available": "Nenhuma senha disponível",
    "Port {port} is already in use": "A porta {port} já está em uso",
    "Failed to start: {error}": "Falha ao iniciar: {error}",
    "The process vanished immediately after starting": "O processo desapareceu logo após iniciar",
    "The name \"{name}\" is already taken by a managed screen":
        "O nome “{name}” já está em uso por uma tela gerenciada",
    "Port {port} is already taken by a managed screen":
        "A porta {port} já está em uso por uma tela gerenciada",
    "Imported from an externally started process": "Importada de um processo iniciado externamente",
    "krfb-virtualmonitor not found; make sure krfb is installed "
    "(expected at {path}).":
        "krfb-virtualmonitor não encontrado; verifique se o krfb está "
        "instalado (esperado em {path}).",
    "kscreen-doctor not found, so the real resolution and scale of a "
    "virtual screen can't be read back; startup verification falls "
    "back to checking the port only.":
        "kscreen-doctor não encontrado, então a resolução e a escala reais de "
        "uma tela virtual não podem ser lidas de volta; a verificação de "
        "inicialização passa a checar apenas a porta.",
    "kscreen-doctor exists but returns no output (the packaged build "
    "was once poisoned by its bundled Qt6 and aborted), so the real "
    "resolution and scale of a virtual screen can't be read back; "
    "startup verification falls back to checking the port only.":
        "kscreen-doctor existe, mas não retorna saída alguma (a build "
        "empacotada já foi uma vez corrompida pelo Qt6 que ela mesma inclui e "
        "abortava), então a resolução e a escala reais de uma tela virtual não "
        "podem ser lidas de volta; a verificação de inicialização passa a "
        "checar apenas a porta.",
    "This is a Wayland session but WAYLAND_DISPLAY is not set, so "
    "krfb cannot create virtual monitors. Start this program from the "
    "desktop launcher or a terminal.":
        "Esta é uma sessão Wayland, mas WAYLAND_DISPLAY não está definida, "
        "então o krfb não pode criar monitores virtuais. Inicie este programa "
        "pelo menu de aplicativos ou por um terminal.",
    "This is not a Wayland session. krfb's virtual monitors require "
    "Wayland (and KWin); under X11 they fail outright.":
        "Esta não é uma sessão Wayland. Os monitores virtuais do krfb exigem "
        "Wayland (e o KWin); no X11 eles falham de imediato.",
    "WAYLAND_DISPLAY={display} points to a socket that does not exist "
    "({path}); krfb will fail with "
    "\"Virtual Monitors are only supported on Wayland\".":
        "WAYLAND_DISPLAY={display} aponta para um socket que não existe "
        "({path}); o krfb vai falhar com “Virtual Monitors are only supported "
        "on Wayland”.",
    "Started by systemd unit {unit}, whose KillMode=control-group and "
    "ExitType=main mean that quitting this program kills every virtual "
    "screen along with it. Run it from the desktop launcher instead, or "
    "add ExitType=cgroup to that unit.":
        "Iniciado pela unidade systemd {unit}, cujos KillMode=control-group e "
        "ExitType=main fazem com que sair deste programa encerre junto todas "
        "as telas virtuais. Inicie-o pelo menu de aplicativos ou adicione "
        "ExitType=cgroup a essa unidade.",

    # --- autostart ----------------------------------------------------------
    "Restore virtual screens marked as \"desired running\" at login":
        "Ao entrar, restaure as telas virtuais marcadas como "
        "“deveriam estar em execução”",
    "Cannot write {path}: {error}": "Não foi possível gravar {path}: {error}",
    "Cannot delete {path}: {error}": "Não foi possível excluir {path}: {error}",

    # --- main.py ------------------------------------------------------------
    "Start minimized to the tray (used by autostart)":
        "Iniciar minimizado na bandeja (usado pela inicialização automática)",
    "Config warning": "Aviso de configuração",

    # --- ui/main_window: 标题栏与工具栏 --------------------------------------
    "Graphical manager for krfb-virtualmonitor": "Gerenciador gráfico para o krfb-virtualmonitor",
    "New virtual screen": "Nova tela virtual",
    "Start all": "Iniciar todas",
    "Stop all": "Parar todas",
    "Scan for and adopt krfb processes started outside this app":
        "Procurar e adotar processos krfb iniciados fora deste aplicativo",
    "Refresh now": "Atualizar agora",

    # --- ui/main_window: 托盘菜单与通知条 ------------------------------------
    "Show main window": "Mostrar janela principal",
    "Quit": "Sair",
    "Restart": "Reiniciar",
    "View": "Ver",

    # --- ui/main_window: 关闭窗口时的询问弹窗 --------------------------------
    "Close the window or minimize to the tray?":
        "Fechar a janela ou minimizar para a bandeja?",
    "Minimize to tray": "Minimizar para a bandeja",
    "Quit the program": "Sair do programa",
    "Remember my choice": "Lembrar minha escolha",

    # --- ui/main_window: 状态栏 ---------------------------------------------
    "{count} virtual screens": "{count} telas virtuais",
    "{count} running": "{count} em execução",
    "{count} need attention": "{count} precisam de atenção",
    "{count} environment problems": "{count} problemas de ambiente",
    "{count} environment problems detected": "{count} problemas de ambiente detectados",

    # --- ui/main_window: 崩溃横幅与启动校验 ----------------------------------
    "\"{name}\" has exited — it may have crashed or been killed":
        "“{name}” foi encerrada — pode ter travado ou sido finalizada",
    "{count} virtual screens have exited ({names}…)":
        "{count} telas virtuais foram encerradas ({names}…)",
    "The process exited immediately after starting": "O processo encerrou logo após iniciar",
    " (the port is listening, but no virtual display was created)":
        " (a porta está escutando, mas nenhum monitor virtual foi criado)",
    " (the port isn't listening either)": " (a porta também não está escutando)",
    "Waited {seconds} seconds and the Virtual-{name} output still "
    "hasn't appeared in KWin{detail}":
        "Esperamos {seconds} segundos e a saída Virtual-{name} ainda não "
        "apareceu no KWin{detail}",

    # --- ui/main_window: 密码与密钥环 ----------------------------------------
    "This virtual screen has no saved password (it may come "
    "from an old config); enter one now.":
        "Esta tela virtual não tem senha salva (pode vir de uma configuração "
        "antiga); informe uma agora.",
    "Cannot read the password from the keyring: {reason}":
        "Não foi possível ler a senha do chaveiro: {reason}",
    "Keyring": "Chaveiro",
    "Unlocked. Passwords will be saved to the keyring.":
        "Desbloqueado. As senhas serão salvas no chaveiro.",
    "Unlock failed or timed out. Passwords can still be used for "
    "this session, but must be re-entered after quitting.":
        "O desbloqueio falhou ou expirou. As senhas ainda podem ser usadas "
        "nesta sessão, mas precisarão ser digitadas novamente depois de sair.",

    # --- ui/main_window: 编辑 / 删除 / 日志 ----------------------------------
    "Restart required": "É preciso reiniciar",
    "\"{name}\" is running. Changes to the resolution, scale or port "
    "do not affect a screen that has already been created; the "
    "virtual screen must be restarted for them to take effect.":
        "“{name}” está em execução. Alterações na resolução, escala ou porta "
        "não afetam uma tela já criada; a tela virtual precisa ser reiniciada "
        "para que entrem em vigor.",
    "Restart it now?": "Reiniciar agora?",
    "Restart now": "Reiniciar agora",
    "Later": "Mais tarde",
    "Delete virtual screen": "Excluir tela virtual",
    "Delete \"{name}\"?": "Excluir “{name}”?",
    "This virtual screen is currently running; deleting it will "
    "stop it first.":
        "Esta tela virtual está em execução; excluí-la vai pará-la primeiro.",
    "This action cannot be undone.": "Esta ação não pode ser desfeita.",
    "The saved password is removed from the keyring too.":
        "A senha salva também será removida do chaveiro.",
    "No unmanaged krfb processes found": "Nenhum processo krfb não gerenciado encontrado",
    "{name}: {error}": "{name}: {error}",
    "Some could not be imported": "Algumas não puderam ser importadas",
    "Start failed": "Falha ao iniciar",
    "\"{name}\" failed to start": "Falha ao iniciar “{name}”",
    "View full log": "Ver o registro completo",
    "Minimized to the tray. Virtual screens keep running and "
    "are not stopped when you quit this app.":
        "Minimizado para a bandeja. As telas virtuais continuam em execução e "
        "não são paradas quando você sai deste aplicativo.",

    # --- ui/detail_pane -----------------------------------------------------
    "Select a virtual screen on the left": "Selecione uma tela virtual à esquerda",
    "or click \"New\" in the top right": "ou clique em “Nova” no canto superior direito",
    "Requested": "Solicitado",
    "Actual": "Efetivo",
    "Address": "Endereço",
    "Status": "Status",
    "Copy the VNC address": "Copiar o endereço VNC",
    "Copy the connection password": "Copiar a senha de conexão",
    "Copied": "Copiado",
    "Start": "Iniciar",
    "Stop": "Parar",
    "Edit": "Editar",
    "{actual}  ⚠ differs from the requested value": "{actual}  ⚠ difere do valor solicitado",
    "The password is only hidden in the UI; "
    "it is passed to krfb in plain text":
        "A senha só fica oculta na interface; ela é passada ao krfb em texto puro",
    "Running, PID {pid}": "Em execução, PID {pid}",
    "Process is gone but marked as \"desired running\"":
        "O processo desapareceu, mas está marcado como “deveria estar em execução”",
    "It may have crashed, been killed, or the machine was rebooted":
        "Pode ter travado, sido finalizado ou a máquina foi reiniciada",
    "Creating, waiting for the KWin output…": "Criando, aguardando a saída do KWin…",
    "Changing resolution or scale while running has no effect on the "
    "created screen; the virtual screen must be restarted":
        "Alterar a resolução ou a escala com a tela em execução não tem efeito "
        "sobre a tela já criada; a tela virtual precisa ser reiniciada",
    "Edit parameters": "Editar parâmetros",

    # --- ui/screen_list -----------------------------------------------------
    "{name}\n{resolution} · Port {port}": "{name}\n{resolution} · Porta {port}",
    "No virtual screens yet\n"
    "Click \"New\" to create one":
        "Nenhuma tela virtual ainda\nClique em “Nova” para criar uma",

    # --- ui/screen_dialog ---------------------------------------------------
    "Edit virtual screen": "Editar tela virtual",
    "e.g. Tablet (it becomes the KWin output \"Virtual-<name>\")":
        "ex.: Tablet (vira a saída “Virtual-<name>” do KWin)",
    "Custom…": "Personalizado…",
    "Auto": "Automático",
    "Pick a port that is neither in use "
    "nor assigned to another virtual screen":
        "Escolha uma porta que não esteja em uso nem atribuída a outra tela virtual",
    "Show / hide the password": "Mostrar / ocultar a senha",
    "Copy the password": "Copiar a senha",
    "Optional, e.g. \"second screen for the iPad\"":
        "Opcional, ex.: “segunda tela para o iPad”",
    "Start at login": "Iniciar ao entrar",
    "Save": "Salvar",
    "Name": "Nome",
    "Resolution": "Resolução",
    "Scale DPR": "Escala DPR",
    "Command that will be executed": "Comando que será executado",
    "The name can't be empty": "O nome não pode ficar vazio",
    "\"{name}\" is already in use "
    "(the KWin output name Virtual-{name} must be unique)":
        "“{name}” já está em uso (o nome de saída do KWin Virtual-{name} "
        "precisa ser único)",
    "Port {port} is already used by another virtual screen":
        "A porta {port} já é usada por outra tela virtual",
    "Port {port} is already taken by another program on the system":
        "A porta {port} já está ocupada por outro programa do sistema",
    "The password can't be empty": "A senha não pode ficar vazia",
    "VNC authentication only uses the first 8 characters; "
    "the remaining {extra} have no effect "
    "(effective password: {effective})":
        "A autenticação VNC usa apenas os 8 primeiros caracteres; os {extra} "
        "restantes não têm efeito algum (senha efetiva: {effective})",
    "VNC authentication uses all 8 characters": "A autenticação VNC usa todos os 8 caracteres",

    # --- ui/dialogs: PasswordPrompt -----------------------------------------
    "Password required": "Senha obrigatória",
    "Enter the VNC password for this virtual screen":
        "Digite a senha VNC desta tela virtual",
    "The password is passed to the krfb process in plain text, so other "
    "local users can see it via ps; VNC authentication only uses the "
    "first 8 characters.":
        "A senha é passada ao processo krfb em texto puro, então outros "
        "usuários locais podem vê-la com ps; a autenticação VNC usa apenas os "
        "8 primeiros caracteres.",
    "Use": "Usar",

    # --- ui/dialogs: AdoptDialog --------------------------------------------
    "Unmanaged virtual screens found": "Telas virtuais não gerenciadas encontradas",
    "These krfb-virtualmonitor processes were not started by this app. "
    "Import them to manage them here.":
        "Estes processos krfb-virtualmonitor não foram iniciados por este "
        "aplicativo. Importe-os para gerenciá-los aqui.",
    "<b>{name}</b> · {resolution} · Port {port}<br>"
    "<span style='font-size:11px'>PID {pid}</span>":
        "<b>{name}</b> · {resolution} · Porta {port}<br>"
        "<span style='font-size:11px'>PID {pid}</span>",
    "unknown resolution": "resolução desconhecida",
    "<br><span style='font-size:11px'>⚠ The package was upgraded; "
    "restarting this virtual screen is recommended</span>":
        "<br><span style='font-size:11px'>⚠ O pacote foi atualizado; "
        "recomenda-se reiniciar esta tela virtual</span>",
    "Import selected": "Importar selecionadas",

    # --- ui/dialogs: SettingsDialog -----------------------------------------
    "Language": "Idioma",
    "Closing the window": "Ao fechar a janela",
    "Ask every time": "Perguntar sempre",
    "Launch at login": "Inicialização automática",
    "Start at login (tray mode)": "Iniciar ao entrar (modo bandeja)",
    "Password storage": "Armazenamento de senhas",
    "Environment": "Ambiente",
    "About": "Sobre",
    "No problems found": "Nenhum problema encontrado",
    "not installed": "não instalado",
    "unknown": "desconhecido",
    "Couldn't save the preference ({error}); "
    "it stays in effect for this session only.":
        "Não foi possível salvar a preferência ({error}); "
        "ela vale apenas nesta sessão.",
    "Config:": "Configuração:",
    "Runtime state:": "Estado de execução:",
    "Logs:": "Registros:",

    # --- ui/log_viewer ------------------------------------------------------
    "Search… (press Enter for the next match)":
        "Pesquisar… (pressione Enter para a próxima ocorrência)",
    "Auto-scroll": "Rolagem automática",
    "Reload": "Recarregar",
    "Open containing folder": "Abrir a pasta do arquivo",
    "(No output yet)\n\nThis is empty until the virtual screen is started.":
        "(Nenhuma saída ainda)\n\nFica vazio até a tela virtual ser iniciada.",
    "{path}   ·   {lines} lines   ·   {size} bytes":
        "{path}   ·   {lines} linhas   ·   {size} bytes",
    "No match for \"{needle}\"": "Nenhuma ocorrência de “{needle}”",
    "Refreshes every {seconds} s": "Atualiza a cada {seconds} s",

    # --- 密码库（多后端）----------------------------------------------------
    "KDE Wallet": "KDE Wallet",
    "System keyring (Secret Service)": "Chaveiro do sistema (Secret Service)",
    "Built-in encrypted vault": "Cofre criptografado integrado",
    "Master password required": "Senha mestra obrigatória",
    "No password vault yet": "Nenhum cofre de senhas ainda",
    "Enter the master password to unlock the built-in vault":
        "Digite a senha mestra para desbloquear o cofre integrado",
    "Set a master password to create the built-in vault":
        "Defina uma senha mestra para criar o cofre integrado",
    "The store is disabled or does not exist":
        "O armazenamento está desativado ou não existe",
    "The store did not respond in time; passwords are kept in memory "
    "for this session only":
        "O armazenamento não respondeu a tempo; as senhas ficam na memória "
        "apenas nesta sessão",
    "already holds saved passwords": "já contém senhas salvas",
    "locked; may hold saved passwords": "bloqueado; pode conter senhas salvas",
    "available": "disponível",
    "always available": "sempre disponível",
    "selected in settings": "selecionado nas configurações",
    "write failed": "falha ao gravar",
    "read-back mismatch": "leitura de volta divergente",
    "store is locked": "o armazenamento está bloqueado",
    "store is busy": "o armazenamento está ocupado",
    "could not unlock the newly created vault":
        "não foi possível desbloquear o cofre recém-criado",
    "there is no vault": "não existe nenhum cofre",
    "wrong master password": "senha mestra incorreta",
    "a vault already exists": "já existe um cofre",
    "some entries could not be decrypted; nothing was changed":
        "algumas entradas não puderam ser descriptografadas; nada foi alterado",
    "(currently unavailable)": "(indisponível no momento)",
    "Store:": "Armazenamento:",
    "Detect again": "Detectar novamente",
    "Using {backend}: the selected store is unavailable":
        "Usando {backend}: o armazenamento selecionado está indisponível",
    "Master password": "Senha mestra",
    "Current master password": "Senha mestra atual",
    "New master password": "Nova senha mestra",
    "Repeat the password": "Repita a senha",
    "Create": "Criar",
    "Change": "Alterar",
    "Unlock": "Desbloquear",
    "Unlocked": "Desbloqueado",
    "Enter master password": "Digite a senha mestra",
    "Set master password": "Definir a senha mestra",
    "Change master password": "Alterar a senha mestra",
    "Create the built-in vault": "Criar o cofre integrado",
    "Unlock the built-in vault": "Desbloquear o cofre integrado",
    "Change the master password": "Alterar a senha mestra",
    "Use at least {count} characters": "Use pelo menos {count} caracteres",
    "The two passwords do not match": "As duas senhas não coincidem",
    "Enter the current master password": "Digite a senha mestra atual",
    "The built-in vault stores passwords encrypted. There is no way "
    "to recover them if you forget the master password.":
        "O cofre integrado armazena as senhas criptografadas. Não há como "
        "recuperá-las se você esquecer a senha mestra.",
    "Enter the master password for the built-in vault.":
        "Digite a senha mestra do cofre integrado.",
    "Changing the master password re-encrypts every password in the vault.":
        "Alterar a senha mestra criptografa de novo todas as senhas do cofre.",
    "Wrong master password": "Senha mestra incorreta",
    "Could not create the vault": "Não foi possível criar o cofre",
    "The master password has been changed.": "A senha mestra foi alterada.",
    "Enter the master password to read saved passwords":
        "Digite a senha mestra para ler as senhas salvas",

    # --- 高危确认（验证码）--------------------------------------------------
    "Type the result here": "Digite o resultado aqui",
    "Confirm": "Confirmar",
    "{a} + {b} = ?": "{a} + {b} = ?",
    "Wrong answer, here is another one": "Resposta errada, aqui está outra",
    "Too many wrong answers": "Muitas respostas erradas",

    # --- 密码库告警与切换 ---------------------------------------------------
    "Password store": "Armazenamento de senhas",
    "Password store unavailable": "Armazenamento de senhas indisponível",
    "{store} holds {count} saved passwords but is unavailable right now.":
        "“{store}” contém {count} senhas salvas, mas está indisponível no "
        "momento.",
    "Enable it again in your system settings, or switch to another store — "
    "switching does not copy the old passwords over, and clearing the old "
    "store afterwards cannot be undone.":
        "Reative-o nas configurações do sistema ou mude para outro "
        "armazenamento — a troca não copia as senhas antigas, e limpar o "
        "armazenamento antigo depois disso não pode ser desfeito.",
    "Open settings": "Abrir configurações",
    "{store} is not available right now.":
        "“{store}” não está disponível no momento.",
    "The target store could not be unlocked.":
        "Não foi possível desbloquear o armazenamento de destino.",
    "last updated {time}": "atualizado pela última vez em {time}",
    "that store does not report timestamps":
        "esse armazenamento não informa data e hora",
    "Moving saved passwords…": "Movendo as senhas salvas…",
    "{count} passwords could not be moved:":
        "Não foi possível mover {count} senhas:",
    "Retry the import before clearing the old store.":
        "Tente importar novamente antes de limpar o armazenamento antigo.",
    "Now using {store}": "Agora usando “{store}”",
    "Clear the old password store":
        "Limpar os dados do armazenamento antigo",
    "Delete the {count} passwords from {store}?":
        "Excluir as {count} senhas de “{store}”?",
    "They are now stored in the new store. Deleting them here cannot be "
    "undone — and any other application that uses that store will no "
    "longer find them either.":
        "Elas agora estão no novo armazenamento. Excluí-las aqui não pode ser "
        "desfeito — e qualquer outro aplicativo que use esse armazenamento "
        "também não as encontrará mais.",
    "Delete them": "Excluí-las",
    "Deleted {count} passwords from the old store":
        "Excluídas {count} senhas do armazenamento antigo",

    # --- 内置库重置 ---------------------------------------------------------
    "Reset the built-in vault": "Redefinir o cofre integrado",
    "This deletes every password stored in the built-in vault.":
        "Isto exclui todas as senhas armazenadas no cofre integrado.",
    "They cannot be recovered — not even with the master password. "
    "Only do this if you no longer need them.":
        "Não será possível recuperá-las — nem mesmo com a senha mestra. Só "
        "faça isso se não precisar mais delas.",
    "Delete the vault": "Excluir o cofre",
    "The built-in vault has been reset": "O cofre integrado foi redefinido",

    # --- 换库时目标已有数据：保留 / 覆盖 / 合并 ----------------------------------------
    "{store} already holds {count} of this app's passwords ({when}).":
        "“{store}” já contém {count} senhas deste aplicativo ({when}).",
    "{source} holds {moving} for the same screens. Whichever side you "
    "drop is deleted for good.":
        "“{source}” contém {moving} para as mesmas telas. O lado que você "
        "descartar será excluído em definitivo.",
    "Keep the target's passwords": "Manter as senhas de destino",
    "Overwrite with the new passwords":
        "Substituir pelas senhas novas",
    "Merge…": "Mesclar…",
    "Merge": "Mesclar",
    "{adding} will be added, {identical} are identical and will be "
    "skipped, {conflicts} conflict.":
        "{adding} serão adicionadas, {identical} são idênticas e serão "
        "ignoradas, {conflicts} estão em conflito.",
    "Screens in conflict: {names}": "Telas em conflito: {names}",
    "Keep the target's version": "Manter a versão de destino",
    "Use the new version": "Usar a versão nova",
    "{count} entries could not be read; they will be left as they are.":
        "Não foi possível ler {count} entradas; elas permanecerão como "
        "estão.",

    # --- 换库时源库锁着：一条都没搬，要说清楚 ---
    "The old store ({store}) is locked, so nothing was moved. "
    "Unlock it and switch again to bring the passwords over.":
        "O armazenamento antigo ({store}) está bloqueado, então nada foi "
        "movido. Desbloqueie-o e faça a troca novamente para trazer as "
        "senhas.",
}
