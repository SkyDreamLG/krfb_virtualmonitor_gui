<img src="packaging/krfb-virtualmonitor-gui.svg" width="72" align="right" alt="">

# Krfb 虚拟屏管理器

**把 `krfb-virtualmonitor` 图形化——不敲命令行，创建、管理、监控 KDE 虚拟显示器。**

[![License: GPL-3.0-or-later](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6%20%28Qt6%29-41cd52.svg)](https://doc.qt.io/qtforpython/)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%C2%B7%20Wayland%20%C2%B7%20KWin-informational.svg)](#运行要求)

[English](README.md)

---

## 项目简介

`krfb-virtualmonitor` 是 KDE 的 VNC 服务器 [krfb](https://invent.kde.org/network/krfb)
自带的命令行工具，用于在 KWin 上创建**虚拟显示器**：由软件模拟的额外屏幕，可用于
无头远程访问、软件 KVM，以及将平板电脑作为第二块屏幕。

该工具能力完整，但不保存任何状态：每次修改参数都要重新输入一条包含明文密码的完整
命令，且没有任何方式查看哪些屏幕正在运行。本项目为它提供一个原生 Qt6 前端，并保证
两条不变式：

> **一、关闭 GUI 不影响任何正在运行的虚拟屏。**
> **二、重新打开 GUI 一定重新接管它们。**

## 功能特性

- **完整的生命周期管理** —— 在列表/详情界面中新建、编辑、启动、停止与删除虚拟屏，
  可单条操作也可批量操作。
- **经校验的状态判定** —— 只有进程确实存活**且** KWin 已生成
  `Virtual-<名称>` 输出，才判定为「运行中」。状态划分明确：运行中、启动中、已停止、
  异常退出、启动失败、未托管。
- **GUI 重启后继续管理** —— 虚拟屏置于独立会话中；GUI 按 `(名称, 端口)` 重新识别，
  并以 `pid + starttime` 校验存活，可防止 PID 复用与僵尸进程造成的误判。
- **纳管外部进程** —— 手动启动的 `krfb-virtualmonitor` 可由「扫描」从 `/proc` 中
  找到并纳入管理，包括其密码。
- **三种密码库** —— **KDE 钱包**（使用 kwalletd 的原生 `org.kde.KWallet` 接口，
  而非通用的 `org.freedesktop.secrets` 总线名——后者先到先得，任何已安装的实现都
  可能抢占）、**系统密钥环**（Secret Service），以及**内置加密库**（SQLite，
  每个值用由用户设定的主密码派生的密钥加密，`scrypt` → Fernet）。默认为 KDE 钱包。
  密码库在设置中选择，列表中只显示当前可用的项目；选定项不可用时，程序按
  KDE 钱包 → 系统密钥环 → 内置加密库的顺序回落，并在状态行说明实际使用的是哪一个。
  回落不改写偏好，选定项恢复可用后即重新投入使用。换库时可选择迁移密码；若目标库中
  已存在本程序的密码，可选择保留目标库中的密码、用当前密码覆盖，或合并——合并会先
  比对两边内容，列出存在冲突的虚拟屏并询问以哪一边为准。清除原库是独立的、需单独
  确认的步骤。密码不会写入任何配置文件。锁定的库在启动时按需申请解锁；持有密码的库
  变为不可用时会弹出警告，而不会表现为「没有保存密码」。
- **请求值与实际生效值分别显示** —— KWin 可能覆写 `--scale` 请求值；界面同时显示
  请求值与实际生效值，不一致时标出。
- **实时日志窗口** —— 每个虚拟屏的 krfb 输出，按增量流式读取。
- **环境自检** —— 启动时检查 `krfb-virtualmonitor`、Wayland socket、
  `kscreen-doctor` 状态与 systemd cgroup 语义，并报告任何会破坏上述两条不变式的
  条件。
- **登录自启** —— 单个应用级 `.desktop` 条目，登录时恢复所有标记为「期望运行」的
  虚拟屏。
- **桌面集成** —— 系统托盘与单实例处理、跟随系统调色板的明暗主题，以及在对话框中
  实时预览即将执行的完整命令行。
- **11 种界面语言** —— 简体中文、繁體中文、English、日本語、한국어、Deutsch、
  Français、Español、Italiano、Português (Brasil)、Русский。默认跟随系统语言，
  也可在「设置 → 语言」中即时切换，无需重启。
- **可配置的关闭行为** —— 标题栏关闭按钮可设为最小化到托盘、退出程序，或每次询问
  （询问时提供「记住我的选择」选项）。「设置 → 关闭窗口时」也提供相同选项。

## 运行要求

| 组件 | 要求 |
|---|---|
| 会话 | **Wayland + KWin**（KDE Plasma）。虚拟显示器是 KWin 独有的能力；在不受支持的会话中，程序会在启动时说明原因。 |
| krfb | 提供 `/usr/bin/krfb-virtualmonitor`（Arch 与 Debian/Ubuntu 的包名均为 `krfb`）。 |
| kscreen | `kscreen-doctor`——强烈建议安装。用于回读实际分辨率与缩放，并修正被覆写的 `--scale` 值。 |
| kwallet | `kwalletd6`（KDE 钱包）——默认密码库。若在系统设置中关闭了钱包子系统，程序将回落到系统密钥环或内置加密库。 |
| Python | 3.11+（仅源码运行需要；打包版无需任何预装环境）。 |
| 工具 | [uv](https://docs.astral.sh/uv/) 管理依赖。 |

## 快速开始

```bash
# 1. 按 uv.lock 安装依赖到 .venv
uv sync

# 2. 启动
./run.sh              # 正常启动
./run.sh --tray       # 启动后直接缩到托盘
```

也可以直接调用入口：

```bash
.venv/bin/python main.py [--tray] [--version]
```

## 打包成独立可执行程序

`packaging/build.sh` 产出**单个文件**，可在任何 Linux 机器上运行，不需要 Python、
虚拟环境或任何已安装的依赖：

```bash
packaging/build.sh            # → dist/krfb-virtualmonitor-gui   （66 MB）
./dist/krfb-virtualmonitor-gui
```

该文件**每次启动**都会把约 170MB 解压到 `$TMPDIR`（参考机器上实测 0.79 秒，已解压的
目录版为 0.21 秒）。目录版可避免重复解压：

```bash
packaging/build.sh --onedir   # → dist/onedir/krfb-virtualmonitor-gui/
```

需要在机器之间拷贝单个产物时使用单文件版；长期安装（尤其是绑定了开机自启，每个会话
都要付解压成本）时使用 `--onedir`。两种产物可在 `dist/` 中共存。

AppImage 经过评估后未采用：它需要 `appimagetool` 与 libfuse2，而 Ubuntu 24.04 及
更高版本默认不再提供 libfuse2；没有 FUSE 时它同样会在启动时解压整个包，与单文件版
行为一致。

将程序加入 KDE 应用菜单与 `~/.local/bin`：

```bash
packaging/install-desktop.sh              # 安装
packaging/install-desktop.sh --uninstall  # 卸载
```

桌面启动器优先使用打包版；若尚未构建，则回退到通过 `.venv` 的源码运行。

## 使用说明

1. **新建虚拟屏** —— 点「新建」，指定名称、分辨率（预设或自定义）、缩放与端口。
   对话框中显示将要执行的完整命令行。
2. **启动** —— 程序启动 `krfb-virtualmonitor`，随后最多等待 8 秒，直到 KWin 中确实
   出现 `Virtual-<名称>` 输出，此时才判定为「运行中」。若 KWin 覆写了请求的缩放值，
   程序会通过 `kscreen-doctor` 显式修正，并将实际生效值回读进详情面板。
3. **连接** —— 任何 VNC 客户端连接 `localhost:<端口>`，使用对话框中生成（或输入）的
   密码，详情面板可随时查看。
4. **关闭 GUI** —— 虚拟屏继续运行；再次打开程序时全部重新纳管，日志保留。
5. **纳管未托管的进程** —— 在终端手动启动的 krfb 可由「扫描」导入为完全可管理的
   虚拟屏，密码一并接管。

登录自启是「设置」中的一个开关：开启后，登录时 GUI 以托盘模式启动，并恢复所有标记为
「期望运行」的虚拟屏。它只写入**一个应用级自启条目**，而不是为每个虚拟屏写一个
`.desktop` 文件：后者需要把 `--password` 明文写入权限为 `0644` 的桌面文件，从而使
密钥环加密失去意义。改为启动 GUI 自身后，密码始终不会以明文形式落盘。

## 架构

```
main.py                     入口：单实例守卫、主题、依赖组装
krfb_gui/
  constants.py              XDG 路径、krfb 参数约束、子进程环境白名单
  models.py                 Screen（配置）/ Runtime（运行态）/ ProcInfo
  store.py                  原子 JSON 持久化（临时文件 + fsync + rename）
  proctools.py              纯 /proc 读取：starttime、僵尸、端口、argv 解析
  envtools.py               清洗过的子进程环境——启动外部命令的唯一入口
  kscreen.py                解析 kscreen-doctor；回读实际输出状态
  manager.py                生命周期：启停/状态判定/纳管认领/环境自检
  secrets/                  密码存储：KDE 钱包 / 系统密钥环 / 内置加密库三个后端，
                            共用一层门面；带硬超时与非阻塞回落
  prefs.py                  界面偏好（语言、关窗行为、选定的密码库）
  i18n/                     11 种语言的词条表
  autostart.py              单个应用级 .desktop 开机自启
  ui/                       主窗口、列表、详情面板、对话框、日志窗口、
                            主题、内嵌 SVG 图标、矢量绘制
tests/
  test_persistence.py       两进程验证「GUI 退出后虚拟屏仍在且能重新接管」
  test_i18n.py              词条完整性（11 种语言）与源码漏译扫描
  test_vault.py             内置加密库：KDF/持久化/篡改/重置语义
  test_backends.py          密码库选择、回落链、迁移与合并逻辑
  test_child_env.py         打包版子进程环境回归
  test_process_state.py     僵尸进程存活判定回归
```

两条贯穿全局的设计规则：

**配置与运行态分文件存放。** `Screen` 表示用户意图，仅在修改设置时写盘；`Runtime`
表示观察结果（pid、实际生效值），每次进程事件都会更新。两者混存会导致每次轮询都重写
配置文件，并允许两个 GUI 实例互相覆盖更新。

**数据模块不 import Qt。** `manager`、`store`、`proctools`、`kscreen`、`envtools`、
`secrets`、`autostart` 均为纯 Python，可独立测试；只有 `ui/` 依赖 PySide6。

## 存储位置

| 内容 | 路径 | 权限 |
|---|---|---|
| 虚拟屏配置（不含密码） | `~/.config/krfb-virtualmonitor-gui/screens.json` | `0600` |
| 运行态（pid、实际生效值） | `~/.local/state/krfb-virtualmonitor-gui/runtime.json` | `0600` |
| 每个虚拟屏的日志 | `~/.local/state/krfb-virtualmonitor-gui/logs/<id>.log` | `0600` |
| 密码 | KDE 钱包 / 系统密钥环 / 内置加密库（在设置中选择） | — |
| 内置加密库（仅选用时存在） | `~/.local/share/krfb-virtualmonitor-gui/vault.db` | `0600` |
| 自启项 | `~/.config/autostart/krfb-virtualmonitor-gui.desktop` | `0644` |

在每种密码库中，密码都以虚拟屏的稳定 UUID 为键——这也是身份判定从不依赖 pid 的原因。
在 KDE 钱包中它们存放于标准的「Passwords」文件夹；在内置加密库中每个值单独加密，
明文为 `id + 分隔符 + 密码`，因此把一行的密文复制到另一行会被拒绝。主密码本身不落盘，
只保存用派生密钥另一部分算出的校验值。忘记主密码后数据无法恢复：重置会删除库中全部
内容，且必须先通过一道算术验证确认。从旧版本升级的安装，可在「设置 → 密码存储」中
迁移仍由原先密码库保存的数据；除非明确要求，不会删除任何内容。

## 测试

```bash
# 核心需求 · 阶段 A：启动一个虚拟屏，然后退出
.venv/bin/python tests/test_persistence.py --phase a

# 阶段 B：全新进程重新发现并接管它
.venv/bin/python tests/test_persistence.py --phase b
```

两个阶段运行在**两个独立的 Python 进程**中，这是唯一能够验证「虚拟屏在 GUI 退出后
仍然存在，且能被新进程接管」的方式。测试状态写入
`/tmp/krfb-virtualmonitor-gui-test`（可用 `KRBFTEST_DIR` 修改），不会触碰真实配置。

其余测试套件不需要显示环境，也不需要构建：

```bash
.venv/bin/python tests/test_i18n.py          # 词条完整性与一致性
.venv/bin/python tests/test_vault.py         # 内置加密库 KDF/持久化/重置
.venv/bin/python tests/test_backends.py      # 密码库选择、迁移与合并
.venv/bin/python tests/test_child_env.py     # 打包版子进程环境
.venv/bin/python tests/test_process_state.py # 僵尸进程不能算「运行中」
```

`test_i18n.py` 解析源码中每一处 `tr()` 调用，校验其字面量在全部词条表中存在且占位符
一致。`test_vault.py` 固定 KDF 参数，并跨进程验证持久化、篡改拒绝与重置语义。
`test_backends.py` 用内存后端覆盖密码库选择、回落链、迁移与合并计划。
`test_child_env.py` 模拟 PyInstaller 注入的 `LD_LIBRARY_PATH`，断言
`kscreen-doctor` 与 `krfb --version` 仍能正常工作，并扫描源码中任何绕过环境清洗的
`subprocess` 调用。`test_process_state.py` 启动真实僵尸进程，并据此断言存活判定规则。

## 技术说明

以下约束均在实际环境中验证确认，实现中都有对应处理，多数配有回归测试。

### 僵尸进程会被判定为「运行中」

krfb 收到 `SIGTERM` 后约 1 秒内退出，KWin 约 3 秒后移除虚拟输出，但已退出而未回收的
进程会变为僵尸：`/proc/<pid>/stat` 仍然存在，`starttime` 不变，因此身份校验仍会通过。
由于 krfb 是 GUI 的子进程，它只会在下一次创建子进程时被顺带回收。

*处理方式：* 存活判定额外排除状态字符 `Z`；同时「停止」这一用户意图在身份校验之前
记录。僵尸进程的 `/proc/<pid>/exe` 不可读，身份校验必然失败，但用户意图仍须被尊重，
否则界面会弹出错误的崩溃提示。

### `--scale` 会被 KWin 持久化的输出配置覆盖

KWin 在 `kwinoutputconfig.json` 中持久化每个输出的配置，而每个新建的虚拟显示器都会
获得同一个 UUID，该 UUID 上的旧配置优先于命令行请求值，因此请求 1.25 或 1.5 的缩放
实际生效值均为 1.75。

*处理方式：* 输出出现后，使用
`kscreen-doctor output.<连接名>.scale.<值>` 显式设置缩放，随后回读实际生效值。界面将
请求值与实际生效值分别显示，并标出不一致的情况。

### `kwalletd` 的解锁调用可能永不返回

`open()` 会使 kwalletd 显示自身的密码提示框，而 D-Bus 调用本身没有超时。若提示框无法
显示（无头会话、systemd unit 启动、提示程序异常），该调用将永久挂起。

*处理方式：* 探测只使用不会触发提示的调用（`isEnabled`、`isOpen`）；所有钱包调用都在
daemon 线程中执行并带 2 秒超时；任何可能触发提示的操作都限定在显式解锁路径中，绝不
进入轮询路径。钱包始终未解锁时，程序使用「功能特性」一节所述的回落链。启动路径不依赖
钱包调用成功。此处使用 daemon 线程而非 `ThreadPoolExecutor`：后者会在解释器退出时
join 工作线程，被阻塞的线程会拖住整个程序，正是需要避免的情形。

### VNC 认证仅使用 8 个字符

krfb 链接 libvncserver，采用经典 VNC DES 认证：只使用密码的前 8 个字符。

*处理方式：* 密码生成器固定生成 8 个字符，界面明确说明这一上限。更长的密码不会带来
额外熵。

### 密码可经 `/proc/<pid>/cmdline` 被其他本机用户读取

密码通过 `--password` 传递，而 `/proc/<pid>/cmdline` 的权限为 `0444`（任何用户可读）。
krfb 既不提供 stdin/环境变量传参方式，也不提供仅绑定 loopback 的选项，因此无法在
该工具层面消除。

*处理方式：* 界面如实披露这一暴露面，不做其他暗示。

### 启动成功不等于虚拟输出已创建

krfb 可能在报告 portal 错误的同时仍然监听端口。判定成功的唯一可靠依据是 KWin 中确实
出现了 `Virtual-<名称>` 输出。

*处理方式：* 当 `kscreen-doctor` 不可用或状态异常时，判定退化为检查端口监听——这是较弱
但如实的信号，选择它是为了确保正常工作的虚拟屏不会被误报为失败。

### 打包版会将其捆绑库路径传给子进程

PyInstaller 的 Linux 启动器会向程序自身环境注入
`LD_LIBRARY_PATH=<包内 _internal>:...`，以便加载捆绑的 Qt6。每个子进程都会继承它，
而本程序调用的所有外部命令（`krfb-virtualmonitor`、`kscreen-doctor`、`systemctl`）
都是*系统* Qt 程序，加载到版本不匹配的 libQt6 后会以 `SIGABRT` 中止。后果严重：
`list_outputs()` 持续返回空，启动校验在 8 秒后超时，运行记录被丢弃，进程成为孤儿。

*处理方式：* 通过严格的环境变量白名单（`constants.py` 中的 `ENV_PASSTHROUGH`）剥离
`LD_LIBRARY_PATH`、`PYTHONPATH`、`QT_*` 等变量，且所有外部命令统一经由
`envtools.run_helper()` 执行。`tests/test_child_env.py` 中的静态检查会在出现裸
`subprocess` 调用时使测试失败。相关兜底：`kscreen-doctor` 完全不可用时，启动校验退化
为端口检查；校验失败但进程实际仍存活时，不会清除进程身份。

### systemd cgroup 清理会连带终止所有虚拟屏

`setsid()` 可以抵御 `SIGHUP`，但无法抵御 cgroup 级别的清理。若 GUI 由配置了
`KillMode=control-group` 与 `ExitType=main` 的 unit 启动，GUI 退出时 systemd 会向整个
cgroup 发送 `SIGTERM`，所有虚拟屏随之终止。

*处理方式：* 启动时检测该情形，并报告解决办法（改用 `ExitType=cgroup`，或照常从桌面
启动器启动）。

## 已知限制

- **仅支持 Wayland + KWin。** 虚拟显示器需要合成器支持，目前只有 KWin 实现了该能力。
- **密码可经 `/proc/<pid>/cmdline` 被其他本机用户读取**（krfb 的固有限制，界面已如实
  标注）。
- **VNC 认证只使用 8 个字符**，与密码长度无关。
- **在打包版中**，日志窗口的「打开所在目录」按钮经由 `QDesktopServices` →
  `xdg-open` 执行，后者是 Qt 内部 fork 的子进程，无法接收清洗过的环境，因此仍会携带
  包内的 `LD_LIBRARY_PATH`，文件管理器可能无法启动。影响范围为该按钮。
- **切换运行方式后需要重新开关一次自启动**：自启条目记录的是写入它的那个启动器的
  路径，从源码版切换到打包版（或反向）后，需在设置中关闭再开启才会改写。

## 许可证

Copyright (C) 2026 SkyDreamLG。

本程序是自由软件：你可以按照**GNU 通用公共许可证**（由自由软件基金会发布）的条款
重新发布和/或修改它，条款为第 3 版或（由你选择）任何更新的版本。

本程序的发布是希望它有用，但**不提供任何担保**，甚至不提供可商用性或特定用途
适用性的默示担保。详见 [GNU 通用公共许可证](LICENSE)。
