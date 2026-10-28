"""密码库后端的公共约定：状态枚举、能力枚举、选择规则、超时工具。

三个后端（KDE 钱包 / 系统密钥环 / 内置加密库）都实现这里的 `Backend` 协议。

**契约**（每一条都是踩过坑写下来的，实现时必须遵守）：

  * 探测类方法（`probe` / `occupancy` / `get` / `set` / `delete` / `iter_ids` /
    `last_modified`）**绝不允许触发任何用户可见的弹框** —— 它们会被 2 秒一次的
    轮询路径调用，弹框等于把界面变成随机弹窗生成器；
  * 只有 `try_unlock()` / `unlock_with_secret()` 允许弹框或长时间阻塞，
    而且调用方必须把它们放进后台线程；
  * 底层调用一律用 `_call_with_timeout()` 包住（D-Bus / 系统提示框都可能永远不返回）；
  * 探测路径**非阻塞抢锁**（`_try_lock`）：上一次调用可能正卡在提示框里握着锁，
    UI 线程绝不能去等它，抢不到就跳过这一轮；
  * `wipe()` 只删调用方给的那几个 id，**绝不整库清空** —— 库里还有别的程序的东西。
"""

from __future__ import annotations

import threading
from enum import Enum
from typing import Callable, Iterable, NamedTuple, Sequence

from .. import prefs
from ..i18n import tr


class SecretsStatus(Enum):
    """一个密码库后端的当前状态。"""

    OK = "ok"                    # 可用且已解锁
    LOCKED = "locked"            # 在，但锁着（解锁会弹系统提示框）
    NEEDS_PASSWORD = "needs_password"  # 内置库：在，但要用户输入主密码
    NO_VAULT = "no_vault"        # 内置库：还没建
    NO_SERVICE = "no_service"    # 会话总线上没有这个服务
    UNAVAILABLE = "unavailable"  # 服务被关掉 / 后端不可用
    TIMEOUT = "timeout"          # 调用超时 —— **是可恢复的，不等于不可用**
    ERROR = "error"

    @property
    def label(self) -> str:
        return tr({
            SecretsStatus.OK: "Keyring ready",
            SecretsStatus.LOCKED: "Keyring locked",
            SecretsStatus.NEEDS_PASSWORD: "Master password required",
            SecretsStatus.NO_VAULT: "No password vault yet",
            SecretsStatus.NO_SERVICE: "No keyring service found",
            SecretsStatus.UNAVAILABLE: "Keyring unavailable",
            SecretsStatus.TIMEOUT: "Keyring not responding",
            SecretsStatus.ERROR: "Keyring error",
        }[self])

    @property
    def detail(self) -> str:
        """逐状态的人类可读说明（可翻译）。原始异常文本不放这里 ——
        那是 `Backend.status_detail`，语言无关的技术信息。"""
        return tr({
            SecretsStatus.OK: "",
            SecretsStatus.LOCKED: "The KDE wallet is closed; "
                                   "passwords are kept in memory for this session only",
            SecretsStatus.NEEDS_PASSWORD: "Enter the master password to unlock "
                                          "the built-in vault",
            SecretsStatus.NO_VAULT: "Set a master password to create the built-in vault",
            SecretsStatus.NO_SERVICE: "kwalletd is not running on the session bus",
            SecretsStatus.UNAVAILABLE: "The store is disabled or does not exist",
            SecretsStatus.TIMEOUT: "The store did not respond in time; "
                                   "passwords are kept in memory for this session only",
            SecretsStatus.ERROR: "",
        }[self])

    @property
    def needs_attention(self) -> bool:
        return self is not SecretsStatus.OK

    @property
    def usable(self) -> bool:
        """能不能在这个后端上干活（解锁或建库之后）。"""
        return self in (SecretsStatus.OK, SecretsStatus.LOCKED,
                        SecretsStatus.NEEDS_PASSWORD, SecretsStatus.NO_VAULT)


class Occupancy(Enum):
    """后端里有没有**本程序的**数据。

    锁着的后端枚举条目会弹框，而探测路径禁止弹框 —— 所以"锁着"只能算 UNKNOWN，
    不能当成 EMPTY：把 UNKNOWN 当空会让程序静默跳过用户真正的密码库。
    """

    EMPTY = "empty"        # 确定没有
    HAS_DATA = "has_data"  # 确定有
    UNKNOWN = "unknown"    # 问不到（锁着/超时）—— 可能有


class UnlockKind(Enum):
    """解锁这个后端需要什么。"""

    NONE = "none"                  # 已经 OK，或者本来就没什么可解的
    SYSTEM_PROMPT = "system_prompt"  # 调 unlock()，系统自己弹框（KDE 钱包 / 密钥环）
    APP_SECRET = "app_secret"      # 需要用户输入一个"应用级秘密"（内置库的主密码）


class UnlockResult(Enum):
    OK = "ok"
    WRONG_PASSWORD = "wrong_password"
    ERROR = "error"


class SecretTimeout(Exception):
    """后端调用超时。阻塞的线程无法取消，只能丢弃。

    消息面向开发者（调用方拿到超时后会丢弃它、改用状态说明），不需要翻译。
    """


def compose_detail(status: SecretsStatus, raw: str) -> str:
    """界面可用的完整说明：状态解释 + 原始异常文本（如果有）。"""
    return " · ".join(part for part in (status.detail, raw) if part)


def call_with_timeout(func, timeout: float):
    """在 daemon 线程里执行 func，超时就抛 SecretTimeout。

    刻意不用 ThreadPoolExecutor：它会注册 atexit 钩子 join 工作线程，一旦线程被
    永久阻塞，解释器退出时就会被拖住 —— 正是我们要规避的失败模式。
    """
    box: dict[str, object] = {}
    done = threading.Event()

    def runner() -> None:
        try:
            box["value"] = func()
        except BaseException as exc:  # noqa: BLE001 - 要把异常原样带回调用方
            box["error"] = exc
        finally:
            done.set()

    thread = threading.Thread(target=runner, daemon=True, name="secrets-call")
    thread.start()
    if not done.wait(timeout):
        raise SecretTimeout(f"backend call did not return within {timeout:.1f}s")
    if "error" in box:
        raise box["error"]  # type: ignore[misc]
    return box.get("value")


class Backend:
    """后端基类：状态字段 + 一把串行化的锁 + 非阻塞抢锁的辅助。"""

    key: str = ""
    unlock_kind: UnlockKind = UnlockKind.NONE

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        self.status = SecretsStatus.UNAVAILABLE
        self.status_detail = ""
        self._lock = threading.Lock()   # 底层连接/句柄不是线程安全的

    # --- 抢锁 ---------------------------------------------------------------
    def _try_lock(self) -> bool:
        """非阻塞抢锁。探测路径专用：抢不到说明**已经有调用在跑**（多半正卡在
        系统提示框上），这时保持现状、跳过这一轮，绝不让 UI 线程去等。"""
        return self._lock.acquire(blocking=False)

    # --- 探测（不弹框、不长时间阻塞）---------------------------------------
    def probe(self) -> SecretsStatus:
        raise NotImplementedError

    def present_ids(self, candidates: Sequence[str]) -> list[str] | None:
        """candidates 里哪些 id 在本库中（不读密码本身）。

        **锁着/问不到时返回 None，而不是空列表** —— 调用方要靠它区分
        "确定没有"和"问不到"，混淆这两者会让程序静默跳过用户真正的密码库。
        """
        raise NotImplementedError

    def get(self, screen_id: str) -> str | None:
        raise NotImplementedError

    def set(self, screen_id: str, password: str) -> bool:
        raise NotImplementedError

    def delete(self, screen_id: str) -> None:
        raise NotImplementedError

    def last_modified(self) -> float | None:
        """库里数据的最后修改时间（unix 秒）。后端不提供时间戳时返回 None。"""
        raise NotImplementedError

    def wipe(self, ids: Sequence[str]) -> tuple[int, list[str]]:
        """删掉给定 id 的条目，返回 (删掉几条, 错误列表)。**只删给定的 id。**"""
        raise NotImplementedError

    # --- 解锁（允许弹框，调用方必须放后台线程）------------------------------
    def try_unlock(self) -> bool:
        return self.status is SecretsStatus.OK

    def unlock_with_secret(self, secret: str) -> UnlockResult:
        return UnlockResult.ERROR

    def close(self) -> None:
        """丢弃密钥材料 / 连接。"""


def occupancy_of(present: "list[str] | None") -> Occupancy:
    """把 `present_ids()` 的返回值翻译成占用状态。"""
    if present is None:
        return Occupancy.UNKNOWN
    return Occupancy.HAS_DATA if present else Occupancy.EMPTY


class SelectionReason(Enum):
    """`select_backend()` 为什么挑了这个后端。值是内部标识，不显示。"""

    HOLDS_DATA = "holds"
    LOCKED_UNKNOWN = "locked_unknown"
    AVAILABLE = "available"
    ALWAYS = "always"
    SELECTED = "selected"

    @property
    def label(self) -> str:
        return tr({
            SelectionReason.HOLDS_DATA: "already holds saved passwords",
            SelectionReason.LOCKED_UNKNOWN: "locked; may hold saved passwords",
            SelectionReason.AVAILABLE: "available",
            SelectionReason.ALWAYS: "always available",
            SelectionReason.SELECTED: "selected in settings",
        }[self])


def backend_label(key: str) -> str:
    """后端的显示名。字典的键用常量而不是字面量 —— 字面量只留显示文案，
    静态扫描才只会把这些文案当成词条（键是标识符，不是要翻译的东西）。"""
    return tr({
        prefs.BACKEND_KWALLET: "KDE Wallet",
        prefs.BACKEND_SECRET_SERVICE: "System keyring (Secret Service)",
        prefs.BACKEND_BUILTIN: "Built-in encrypted vault",
    }.get(key, ""))


# --- 挑一个能用的后端（选定项不可用时的回落）------------------------------------


def select_backend(candidates: Sequence[tuple[str, SecretsStatus, Occupancy]],
                   ) -> tuple[str, SelectionReason]:
    """从探测结果里挑一个后端，返回 (key, 原因)。

    规则（顺序即优先级：KDE 钱包 → 系统密钥环 → 内置库）：
      1. 有确定数据的 → 第一个；
      2. 否则有 UNKNOWN 的 → 第一个。**否决权**：锁着但可能存着密码的后端，
         绝不能被静默跳过 —— 否则用户看到的是"密码全没了"；
      3. 否则有可用的 → 第一个（KDE 优先）；
      4. 都没有 → 内置库（它永远可用）。
    """
    ready = [c for c in candidates if c[1].usable]
    if not ready:
        return candidates[-1][0], SelectionReason.ALWAYS

    holders = [c for c in ready if c[2] is Occupancy.HAS_DATA]
    if holders:
        return holders[0][0], SelectionReason.HOLDS_DATA

    unknown = [c for c in ready if c[2] is Occupancy.UNKNOWN]
    if unknown:
        return unknown[0][0], SelectionReason.LOCKED_UNKNOWN

    return ready[0][0], SelectionReason.AVAILABLE


# --- 合并 ---------------------------------------------------------------------
class MergePlan(NamedTuple):
    """目标已有数据时，"合并"这一步该怎么走（只算不写）。"""

    add: list[str]           # 目标里没有、源里有 → 直接补进去
    same: list[str]          # 两边一模一样 → 跳过（省一次无谓的写）
    conflicts: list[str]     # 两边都有但密码不同 → 得由用户定哪边赢
    unreadable: list[str]    # 至少一边读不出来（例如源库锁着）→ 不碰

    @property
    def total(self) -> int:
        return len(self.add) + len(self.same) + len(self.conflicts) + len(self.unreadable)

    def ids_to_copy(self, prefer_source: bool) -> list[str]:
        """要写进目标的 id。`prefer_source` 决定冲突的那些听谁的。"""
        return self.add + (self.conflicts if prefer_source else [])


def plan_merge(src: Backend, dst: Backend, ids: Sequence[str]) -> MergePlan:
    """算一遍合并计划。**只读**，不写任何东西，可以在弹方案前随便调。

    读不出来的一律进 `unreadable` 而不是当空值处理 —— 锁着的库和"确实没有"
    是两回事，当成空值会把对方的数据当成"新增"再覆盖一遍。
    """
    add: list[str] = []
    same: list[str] = []
    conflicts: list[str] = []
    unreadable: list[str] = []

    for screen_id in ids:
        try:
            mine = src.get(screen_id)
            theirs = dst.get(screen_id)
        except Exception:  # noqa: BLE001
            unreadable.append(screen_id)
            continue
        if mine is None:
            # 源里没有这条 → 目标里有没有都保持原样，不用写
            if theirs is None:
                unreadable.append(screen_id)   # 两边都没有：多半是读不出来
            continue
        if theirs is None:
            add.append(screen_id)
        elif theirs == mine:
            same.append(screen_id)
        else:
            conflicts.append(screen_id)

    return MergePlan(add, same, conflicts, unreadable)


# --- 迁移 ---------------------------------------------------------------------
def migrate(src: Backend, dst: Backend, ids: Sequence[str],
            on_progress: Callable[[int, int], None] | None = None,
            ) -> tuple[list[str], dict[str, str]]:
    """把 ids 里的密码从 src 搬到 dst：读 → 写 → **读回比对**。

    返回 (成功搬过去的 id, {失败的 id: 原因})。
    迁移前调用方必须确保 dst 已解锁 —— 往锁着的库里写只会静默失败。
    """
    copied: list[str] = []
    failed: dict[str, str] = {}
    total = len(ids)

    for index, screen_id in enumerate(ids, start=1):
        try:
            value = src.get(screen_id)
        except Exception as exc:  # noqa: BLE001 - 一条失败不该拖垮整轮迁移
            failed[screen_id] = f"{type(exc).__name__}: {exc}"
            continue
        if not value:
            continue  # 源库里本来就没有这条
        try:
            if not dst.set(screen_id, value):
                failed[screen_id] = tr("write failed")
                continue
            if dst.get(screen_id) != value:
                # 读回比对：写接口返回成功但实际没落盘的情况是存在的
                failed[screen_id] = tr("read-back mismatch")
                continue
        except Exception as exc:  # noqa: BLE001
            failed[screen_id] = f"{type(exc).__name__}: {exc}"
            continue
        copied.append(screen_id)
        if on_progress is not None:
            on_progress(index, total)

    return copied, failed
