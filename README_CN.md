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
自带的命令行工具，可以在 KWin 上创建**虚拟显示器**——纯粹由软件模拟出来的
额外屏幕，适合无头远程访问、软件 KVM，或者把平板当成第二块屏幕来用。

它能力很强，但用起来很裸：每改一个参数就要重新敲一条带明文密码的长命令，
且没有任何手段能看到哪些屏幕正在运行。本项目把它封装成一个原生 Qt6 桌面程序，
并且守住两条不可妥协的底线：

> **一、关掉 GUI 不影响任何正在运行的虚拟屏。**
> **二、重新打开 GUI 一定能重新接管它们。**

## 功能特性

- **完整的生命周期管理** —— 左列表 + 右详情的界面，新建、编辑、启停、
  全部启动/全部停止、删除虚拟屏。
- **如实的状态跟踪** —— 只有进程真正存活**且** KWin 里确实出现了
  `Virtual-<名称>` 输出，才算「运行中」。状态划分明确：运行中、启动中、已停止、
  异常退出、启动失败、未托管。
- **GUI 重启后仍能继续管理** —— 虚拟屏被放进独立会话，GUI 按 `(名称, 端口)`
  重新识别身份，用 `pid + starttime` 双重校验存活（防 PID 复用，防僵尸误判）。
- **纳管外部进程** —— 你自己在终端敲命令启动的 `krfb-virtualmonitor`？
  「扫描」会从 `/proc` 里找到它并连密码一起接管。
- **密码进 KDE 钱包** —— 密码存在 KDE 钱包里，走 kwalletd 的原生
  `org.kde.KWallet` 接口，**不用**通用的 `org.freedesktop.secrets`：那个总线名
  是先到先得的，系统里只要装了别的实现（gnome-keyring 等）就会被抢走，密码会
  悄悄存进另一个后端（本机实测踩过）。密码绝不写入配置文件；钱包锁定或停用时，
  启动时会主动申请解锁，否则降级为仅本次会话内存并**在界面明确标注**，
  绝不卡死、绝不假装成功。
- **请求值与实际生效值分开显示** —— KWin 会覆写 `--scale` 请求值；界面同时显示
  「请求」和「实际」，不一致时标黄提醒。
- **实时日志窗口** —— 每个虚拟屏的 krfb 输出，按字节增量流式读取。
- **环境自检** —— 启动时检查 `krfb-virtualmonitor`、Wayland socket、
  `kscreen-doctor` 健康状况、systemd cgroup 语义，凡是会破坏上述两条底线的情况
  都会显式报告。
- **登录自启** —— 一个应用级 `.desktop`，在登录时恢复所有标记为「期望运行」的
  虚拟屏。明文密码始终不经手磁盘。
- **桌面原生体验** —— 系统托盘 + 单实例、跟随系统的明暗主题、新建对话框里实时
  预览「即将执行的完整命令行」。
- **11 种界面语言** —— 简体/繁体中文、English、日本語、한국어、Deutsch、Français、
  Español、Italiano、Português (Brasil)、Русский。默认跟随系统语言，也可以在
  「设置 → 语言」里即时切换（无需重启）。
- **关窗行为自己定** —— 标题栏的 X 可以是缩到托盘、退出程序，或每次都问一遍
  （弹窗里可勾选「记住我的选择」）。「设置」里也有对应选项。

## 运行要求

| 组件 | 要求 |
|---|---|
| 会话 | **Wayland + KWin**（KDE Plasma）。虚拟显示器是 KWin 独有的能力——GNOME 与 X11 都不行，程序启动时会直接说明原因。 |
| krfb | 提供 `/usr/bin/krfb-virtualmonitor`（Arch 与 Debian/Ubuntu 的包名都是 `krfb`）。 |
| kscreen | `kscreen-doctor`——强烈建议安装。用于回读**真实**分辨率/缩放，并修正被覆写的 `--scale`。 |
| kwallet | `kwalletd6`（KDE 钱包）——密码存储需要它。如果在系统设置里关掉了钱包子系统，程序会如实说明，并把密码降级为仅本次会话内存。 |
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

构建脚本产出 **onedir 目录**（可执行文件 + `_internal/`），拷到任何 Linux 机器
都能跑——不需要 Python，不需要虚拟环境，不需要任何依赖：

```bash
packaging/build.sh
./dist/krfb-virtualmonitor-gui/krfb-virtualmonitor-gui
```

选 onedir 是刻意的：PyInstaller 的单文件模式每次启动都要把上百 MB 解压到 `/tmp`，
对一个常驻托盘的 GUI 程序不划算。

想让它出现在 KDE 应用菜单和 `~/.local/bin` 里：

```bash
packaging/install-desktop.sh              # 安装
packaging/install-desktop.sh --uninstall  # 卸载
```

桌面启动器**优先指向打包版**，没构建过才回退到 `.venv` 源码运行。

## 使用说明

1. **新建虚拟屏** —— 点「新建」，填名称、分辨率（预设或自定义）、缩放、端口。
   对话框底部实时显示将要执行的完整命令行。
2. **启动** —— 程序拉起 `krfb-virtualmonitor`，然后最多等 8 秒，直到 KWin 里
   真的出现 `Virtual-<名称>` 输出，才算「运行中」。若 KWin 覆写了请求的 scale，
   程序会通过 `kscreen-doctor` 修正一遍，并把实际生效值回读进详情面板。
3. **连接** —— 任何 VNC 客户端连 `localhost:<端口>`，密码就是对话框里生成
   （或你填写）的那个，详情面板可随时查看。
4. **随时离开** —— 关窗口甚至退出整个 GUI，虚拟屏继续跑；之后再打开，全部重新
   纳管，日志也还在。
5. **纳管散落的进程** —— 如果你在终端亲手启动过 krfb，「扫描」会把它导入为
   完全可管理的虚拟屏，密码一并接管。

登录自启是设置里的一个开关：打开后，登录时 GUI 以托盘模式启动，并恢复所有
标记为「期望运行」的虚拟屏。它刻意只写**一个应用级自启项**，而不是每个虚拟屏
一个 `.desktop`——后者需要把 `--password` 明文写进 0644（任何人可读）的桌面文件，
等于白做密钥环加密。改为启动 GUI 自身，密码就始终不经手磁盘明文。
（KDE 的自启动生成器从该条目派生的 unit 恰好是 `ExitType=cgroup`，属于安全情况——
见下面的 cgroup 说明。）

## 架构

```
main.py                     入口：单实例守卫、主题、依赖组装
krfb_gui/
  constants.py              XDG 路径、krfb 参数约束、子进程环境白名单
  models.py                 Screen（配置）/ Runtime（运行态）/ ProcInfo
  store.py                  原子 JSON 持久化（临时文件 + fsync + rename）
  proctools.py              纯 /proc 读取：starttime、僵尸、端口、argv 解析
  envtools.py               清洗过的子进程环境——起外部命令的唯一入口
  kscreen.py                解析 kscreen-doctor；回读真实输出状态
  manager.py                生命周期：启停/状态判定/纳管认领/环境自检
  secrets.py                KDE 钱包客户端；带硬超时，降级为仅会话内存，绝不阻塞
  autostart.py              单个应用级 .desktop 开机自启
  ui/                       主窗口、列表、详情面板、对话框、日志窗口、
                            主题、内嵌 SVG 图标、矢量绘制
tests/
  test_persistence.py       两进程验证「GUI 退出后虚拟屏仍在且能重新接管」
  test_child_env.py         打包版子进程环境回归
  test_process_state.py     僵尸进程存活判定回归
```

两条贯穿全局的设计规则：

**配置与运行态分文件存放。** `Screen` 是用户意图，只在改设置时写盘；`Runtime`
是观察结果（pid、实测分辨率），每次进程事件都会变。混在一起会让每次轮询都重写
配置文件，两个 GUI 实例还会互相覆盖对方的更新。

**数据模块一律不 import Qt。** `manager`、`store`、`proctools`、`kscreen`、
`envtools`、`secrets`、`autostart` 是纯 Python，可单独测试；只有 `ui/` 依赖 PySide6。

## 存储位置

| 内容 | 路径 | 权限 |
|---|---|---|
| 虚拟屏配置（不含密码） | `~/.config/krfb-virtualmonitor-gui/screens.json` | `0600` |
| 运行态（pid、实测值） | `~/.local/state/krfb-virtualmonitor-gui/runtime.json` | `0600` |
| 每个虚拟屏的日志 | `~/.local/state/krfb-virtualmonitor-gui/logs/<id>.log` | `0600` |
| 密码 | KDE 钱包（`kdewallet`，走 `org.kde.KWallet`） | — |
| 自启项 | `~/.config/autostart/krfb-virtualmonitor-gui.desktop` | `0644` |

密码存在 KDE 钱包标准的「Passwords」文件夹里，键是虚拟屏的稳定 UUID——这也正是
身份判定从不依赖 pid 的原因。（从旧版本升级：首次读取时会顺手把还留在
freedesktop Secret Service 里的密码搬进钱包，**只读不删**。）

## 测试

```bash
# 核心需求 · 阶段 A：启动一个虚拟屏，然后退出
.venv/bin/python tests/test_persistence.py --phase a

# 阶段 B：全新进程重新发现并接管它
.venv/bin/python tests/test_persistence.py --phase b
```

两个阶段跑在**两个独立的 Python 进程**里——这正是重点：只有这样才能真正验证
「GUI 退出后虚拟屏还在，且能被新进程重新接管」。测试配置写在
`/tmp/krfb-virtualmonitor-gui-test`（可用 `KRBFTEST_DIR` 改），不碰你的真实配置。

另有两条不需要构建、不弹窗口、不依赖显示环境的回归测试：

```bash
.venv/bin/python tests/test_child_env.py      # 打包版子进程环境
.venv/bin/python tests/test_process_state.py  # 僵尸进程不能算「运行中」
```

`test_child_env.py` 模拟 PyInstaller 注入的 `LD_LIBRARY_PATH`，断言
`kscreen-doctor` / `krfb --version` 仍能正常出结果，并扫描源码中任何绕过清洗的
裸 `subprocess` 调用；`test_process_state.py` 用真正的僵尸子进程断言存活判定规则。

## 工程笔记

这个项目真正有意思的地方，是它必须直面的那些失败模式。下面每一条都在真机上实测
复现过，都有对应的修复，能补回归测试的都补了。

### 僵尸进程会一直被当成「运行中」

krfb 收到 `SIGTERM` 后 ~1 秒内就退出，KWin 那边 ~3 秒就摘掉虚拟屏——而界面却
显示「运行中」超过一分钟。原因：krfb 是本程序的子进程，而父进程从不 `waitpid`，
退出后它变成**僵尸**——`/proc/<pid>/stat` 还在、starttime 也不变，身份校验照样
通过。真正的回收只发生在下一次创建子进程时（`subprocess` 顺手做 `_cleanup()`）。
对策：存活判定额外排除状态字符 `Z`；并且「停止」这个用户意图**先记**再做身份
校验——僵尸的 `/proc/<pid>/exe` 已经读不到，身份校验必然失败，但「用户不要它
跑了」这件事不能丢，否则界面会把它当异常退出、弹出误导性的崩溃横幅。

### `--scale` 参数基本是无效的

实测请求 `--scale 1.25` 和 `1.5`，KWin 一律给 **1.75**。原因：KWin 在
`kwinoutputconfig.json` 里为虚拟输出持久化了一份配置，而**每个新建的虚拟显示器
都会拿到同一个 UUID**——于是那份陈旧配置永远压过命令行请求值。对策：建成之后再用
`kscreen-doctor output.<连接名>.scale.<值>` 显式设置一遍，然后回读真实值。
界面上的「请求」与「实际生效」分开显示，不一致时标黄——只显示请求值就是在骗人。

### 打开钱包这一步可能永远不返回

kwalletd 的 `open()` 会弹钱包密码框，而 **D-Bus 调用本身没有任何超时**。如果
提示框弹不出来（无显示环境、从 systemd unit 启动、prompter 异常），这个调用就
永远挂着。对策：探测只用不可能弹框的方法（`isEnabled` / `isOpen`），所有钱包调用
丢进 daemon 线程并带 2 秒超时，**可能弹框的操作（open）只允许出现在显式的解锁
路径里，绝不进轮询/刷新路径**。钱包始终没解开就降级为「仅本次会话内存」并在界面
明确标注。**启动路径永远不依赖钱包成功。**
（用 `threading.Thread` 而不是 `ThreadPoolExecutor`——后者会在解释器退出时 join
工作线程，被阻塞的线程会把整个程序拖住，正好是要避免的失败模式。）

### VNC 密码只有前 8 个字符有效

krfb 链接的是 libvncserver，用的是经典 VNC DES 认证——**只取密码前 8 个字符**。
所以密码生成器只生成 8 位，界面也如实说明。给你一个 32 位密码却只有 8 位有效，
那是虚假的安全感。

### 密码对本机其他用户可见

密码是通过 `--password` 传的，而 `/proc/<pid>/cmdline` 是 `0444`（任何人可读）。
krfb 没有 stdin/env 传参方式，也没有只绑 loopback 的选项——这是它的固有限制，
本程序无法在命令行层面消除，只能在界面上如实告知。

### 启动「成功」不等于虚拟屏建成了

krfb 会报 portal 错误却仍然监听端口。判定成功的唯一可靠证据是 KWin 里真的出现了
`Virtual-<名称>` 输出。当 `kscreen-doctor` 缺失或不可用时，判定退化为「端口在
监听」——这是更弱但诚实的信号，宁可判得弱一点，也不能在虚拟屏明明起来了的情况下
误报失败。

### 打包版会毒化子进程环境

PyInstaller 的 Linux 启动器会往 GUI **自己**的环境里注入
`LD_LIBRARY_PATH=<包内 _internal>:...`，好让它加载包内的 Qt6。这个变量会**继承给
每一个子进程**——而本程序要调用的外部命令（`krfb-virtualmonitor`、
`kscreen-doctor`、`systemctl`）全是*系统* Qt 程序，继承过去就会绑到错误的
libQt6 上直接 abort（SIGABRT、stdout 全空）。后果很严重：`list_outputs()` 永远
返回空，启动判定永久失败，8 秒后**误报超时**，还会把运行记录抹掉、进程变成孤儿。

对策：严格的环境变量白名单（`constants.py` 的 `ENV_PASSTHROUGH`）剥掉
`LD_LIBRARY_PATH` / `PYTHONPATH` / `QT_*` 等，且**所有**外部命令统一走
`envtools.run_helper()`。`tests/test_child_env.py` 里有一条静态规则守着「不许再
出现裸的 `subprocess` 调用」。另外两条相关的兜底：`kscreen-doctor` 完全用不了时，
启动判定按环境自检承诺过的行为退化为只检查端口；校验失败时若进程其实还活着，
只记错误、**不清**进程身份。

### systemd cgroup 会连带杀掉所有虚拟屏

`setsid()` 能防 `SIGHUP`，防不住 cgroup 级的清理。若 GUI 由
`KillMode=control-group` + `ExitType=main` 的 unit 启动，GUI 一退出，systemd 就会
SIGTERM 整个 cgroup——所有虚拟屏陪葬。程序启动时会检测这种情况并说明改法
（改用 `ExitType=cgroup`，或照常从桌面启动器启动）。

## 已知限制

- **仅限 Wayland + KWin。** 虚拟显示器需要合成器支持，目前只有 KWin 实现了。
- **密码对本机其他用户可见**（经 `/proc/<pid>/cmdline`，krfb 的固有限制，
  界面已如实标注）。
- **VNC 认证只使用 8 个字符**，密码再长也一样。
- **打包版里**日志窗口的「打开所在目录」走 `QDesktopServices` → `xdg-open`，
  是 Qt 自己 fork 的子进程，拿不到清洗过的环境，仍会带着包内 `LD_LIBRARY_PATH`
  去起文件管理器（可能起不来）。影响面就这一个按钮。
- **切换运行方式要重新开关一次自启动**：自启项里写的是当时那个启动器的路径，
  从源码版切到打包版（或反过来）后，需要在设置里关掉再打开才会改写。

## 许可证

Copyright (C) 2026 SkyDreamLG。

本程序是自由软件：你可以按照**GNU 通用公共许可证**（由自由软件基金会发布）的条款
重新发布和/或修改它，条款为第 3 版或（由你选择）任何更新的版本。

本程序的发布是希望它有用，但**不提供任何担保**，甚至不提供可商用性或特定用途
适用性的默示担保。详见 [GNU 通用公共许可证](LICENSE)。
