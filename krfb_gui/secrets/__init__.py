"""密码存储门面：内存缓存 + 可切换的多个后端。

对外 API 与拆分前完全一致（`Secrets` / `SecretsStatus` / `compose_detail` /
`generate_password` / `effective_length` / `SecretTimeout`），其余模块不用改。

三个后端见 `kwallet.py` / `secret_service.py` / `builtin.py`；选择规则见
`base.select_backend()`。这里只负责：

  * 记住"当前用哪个后端"（整个会话粘住，不在轮询里重算）；
  * 内存缓存与"锁定期间的待写队列"（`_dirty`）；
  * 建库 / 解锁 / 迁移 / 清除这些编排动作。

**本模块必须保持 Qt-free 且 import 廉价**：`cryptography` / `secretstorage`
只在真正构造对应后端时才 import（`_make_backend`）。
"""

from __future__ import annotations

import secrets as _secrets
import threading
from typing import Callable, Sequence

from .. import constants as C
from .. import prefs
from .base import (  # noqa: F401 - 对外重导出
    Backend,
    MergePlan,
    SelectionReason,
    backend_label,
    Occupancy,
    SecretTimeout,
    SecretsStatus,
    UnlockKind,
    UnlockResult,
    compose_detail,
    migrate,
    occupancy_of,
    plan_merge,
    select_backend,
)
from .builtin import BuiltinVaultBackend
from .kwallet import KWalletBackend
from .secret_service import SecretServiceBackend

# 后端顺序 = 回落顺序：KDE 钱包（默认）→ 系统密钥环 → 内置库
_BACKEND_ORDER = (prefs.BACKEND_KWALLET, prefs.BACKEND_SECRET_SERVICE,
                  prefs.BACKEND_BUILTIN)
_BACKEND_CLASSES = {
    prefs.BACKEND_KWALLET: KWalletBackend,
    prefs.BACKEND_SECRET_SERVICE: SecretServiceBackend,
    prefs.BACKEND_BUILTIN: BuiltinVaultBackend,
}


def generate_password(length: int = C.VNC_PASSWORD_LEN) -> str:
    """生成随机密码。

    默认只生成 8 位，因为 VNC 的 DES 认证**只使用前 8 个字符** ——
    更长的密码不会增加任何熵，只会让用户误以为自己更安全。
    """
    alphabet = C.PASSWORD_ALPHABET
    return "".join(_secrets.choice(alphabet) for _ in range(length))


def effective_length(password: str) -> int:
    """VNC 实际会用到的字符数（上限 8）。"""
    return min(len(password), C.VNC_PASSWORD_LEN)


class Secrets:
    """密码读写门面。后端可切换，内存缓存与后端对调用方透明。"""

    def __init__(self, timeout: float = C.KEYRING_TIMEOUT_MS / 1000) -> None:
        self.timeout = timeout
        self._backends: dict[str, Backend] = {}
        self._backend: Backend | None = None
        self.backend_key = ""            # 实际在用的后端
        self.selection_reason: SelectionReason | None = None
        self.fallback_from = ""          # 显式选择不可用时的原选择（供 UI 说明）
        self.availability: dict[str, bool] = {}
        self._candidates: list[str] = []   # 最近一次 scan 用的 id 列表

        self._memory: dict[str, str] = {}
        self._dirty: set[str] = set()
        # _memory/_dirty 会被 UI 线程（轮询里的 get）和后台线程（解锁后补写）同时碰
        self._state_lock = threading.Lock()

    # --- 后端工厂 -----------------------------------------------------------
    def _make_backend(self, key: str) -> Backend:
        backend = self._backends.get(key)
        if backend is None:
            backend = _BACKEND_CLASSES[key](self.timeout)
            self._backends[key] = backend
        return backend

    @property
    def backend(self) -> Backend | None:
        return self._backend

    # --- 探测与选择 ---------------------------------------------------------
    def probe(self) -> SecretsStatus:
        """探测**当前**后端（UI 线程可调，代价与拆分前相同）。

        轮询路径会反复调它：别的程序解锁了密钥环之后，这里下一次就会把状态
        从"超时"拉回"已就绪"。
        """
        if self._backend is None:
            return SecretsStatus.UNAVAILABLE
        return self._backend.probe()

    def scan(self, candidates: Sequence[str]) -> str:
        """探测所有后端、解析出该用哪个。**必须在后台线程调用**（三个后端 × D-Bus
        同步跑会把窗口冻住几秒）。

        返回选中的后端 key。整个会话粘住：只有这里和 `select()` 会改当前后端。
        """
        self._candidates = list(candidates)
        results = []
        for key in _BACKEND_ORDER:
            backend = self._make_backend(key)
            status = backend.probe()
            sid_list = backend.present_ids(candidates)
            occupancy = occupancy_of(sid_list)
            results.append((key, status, occupancy))
            self.availability[key] = status.usable
            if sid_list:
                # 记住"这个库里有几条"，用于"曾用过的库突然不可用"的启动告警
                prefs.note_store_seen(key, len(sid_list))

        preference = prefs.password_backend()   # 永远是具体后端（prefs 已经归一化）
        chosen, reason = preference, SelectionReason.SELECTED
        status = dict((key, st) for key, st, _ in results)[preference]
        self.fallback_from = ""
        if not status.usable:
            # 选定的后端不可用 → 按 KDE 钱包 → 系统密钥环 → 内置的顺序回落，
            # 并让界面说清楚现在实际在用谁（**不改偏好**：钱包回来还能自动用回去）
            chosen, reason = select_backend(results)
            self.fallback_from = preference

        self._set_backend(chosen)
        self.selection_reason = reason
        return chosen

    def refresh_availability(self) -> bool:
        """重新探测"哪些后端可用"，**只更新 `availability`，绝不动当前选择**
        （选择在整个会话里是粘住的，见 §1）。返回是否有变化。

        轮询里的廉价复检用它：KDE 钱包被关掉再打开之后，下拉里那一项得自己
        回来 —— 光靠启动时扫那一次，它会一直标着"不可用"。
        **后台线程调用**（三个后端各一次 D-Bus 探测）。
        """
        changed = False
        for key in _BACKEND_ORDER:
            try:
                status = self._make_backend(key).probe()
            except Exception:  # noqa: BLE001 - 某个后端炸了不该影响其他后端
                continue
            if status is SecretsStatus.TIMEOUT:
                # 抢不到锁 / 没响应 → 结论不可信。这时把它标成"不可用"会让下拉
                # 里的后端凭空消失，宁可保持上一次的结论。
                continue
            usable = status.usable
            if self.availability.get(key) != usable:
                self.availability[key] = usable
                changed = True
        return changed

    def _set_backend(self, key: str) -> None:
        if self._backend is not None and self._backend.key == key:
            return
        if self._backend is not None:
            self._backend.close()
        with self._state_lock:
            self._memory.clear()   # 值属于旧后端，不能带到新后端
            # _dirty 保留：那些是"用户在这次会话里设过、但没写成"的密码，
            # 换后端后应该写进新后端，而不是丢掉。
        self._backend = self._make_backend(key)
        self.backend_key = key

    def select(self, key: str) -> None:
        """用户显式选定后端：写偏好 + 立刻切过去。"""
        if key not in prefs.BACKENDS:
            key = prefs.BACKEND_KWALLET
        prefs.set_password_backend(key)
        self._make_backend(key).probe()
        self._set_backend(key)
        self.availability.setdefault(key, True)
        self.selection_reason = SelectionReason.SELECTED
        self.fallback_from = ""

    # --- 状态 ---------------------------------------------------------------
    @property
    def status(self) -> SecretsStatus:
        return self._backend.status if self._backend is not None else SecretsStatus.UNAVAILABLE

    @property
    def status_detail(self) -> str:
        return self._backend.status_detail if self._backend is not None else ""

    @property
    def detail(self) -> str:
        """界面用的完整说明：状态解释 + 原始异常文本。每次访问都重新拼，
        语言切换后不会像缓存在控件里的字符串那样过期。"""
        return compose_detail(self.status, self.status_detail)

    @property
    def unlock_kind(self) -> UnlockKind:
        if self._backend is None:
            return UnlockKind.NONE
        if self._backend.status is SecretsStatus.OK:
            return UnlockKind.NONE
        if self._backend.status in (SecretsStatus.NO_SERVICE, SecretsStatus.UNAVAILABLE,
                                    SecretsStatus.NO_VAULT, SecretsStatus.ERROR):
            # 没得解锁（有些是可以去建库，但那不是"解锁"）
            return UnlockKind.NONE
        return self._backend.unlock_kind

    # --- 读 -----------------------------------------------------------------
    def get(self, screen_id: str) -> str | None:
        """先查内存（快且不会挂），再查后端。

        后端没解锁时**不去试** —— 那可能弹提示框，而这条路径会被轮询调用。
        """
        with self._state_lock:
            if screen_id in self._memory:
                return self._memory[screen_id]
        if self._backend is None or self._backend.status is not SecretsStatus.OK:
            return None

        value = self._backend.get(screen_id)
        if value is not None:
            with self._state_lock:
                self._memory[screen_id] = value
            # 记下"这个库里确实存着东西"：本次会话里刚写进去、还没来得及重新
            # 扫描的密码也要算数，否则库后来不可用时就告警不起来。
            if not prefs.store_seen().get(self.backend_key, 0):
                prefs.note_store_seen(self.backend_key, 1)
            return value
        return None

    def set(self, screen_id: str, password: str) -> bool:
        """写密码。内存一定成功；后端是否写成功由返回值表示。"""
        with self._state_lock:
            self._memory[screen_id] = password

        if self._backend is None or self._backend.status is not SecretsStatus.OK:
            with self._state_lock:
                self._dirty.add(screen_id)
            return False

        if not self._backend.set(screen_id, password):
            with self._state_lock:
                self._dirty.add(screen_id)
            return False
        with self._state_lock:
            self._dirty.discard(screen_id)
        return True

    def delete(self, screen_id: str) -> None:
        with self._state_lock:
            self._memory.pop(screen_id, None)
            self._dirty.discard(screen_id)
        if self._backend is not None:
            self._backend.delete(screen_id)   # 后端自己保证不抛

    # --- 仅内存的显式操作 ---------------------------------------------------
    def remember(self, screen_id: str, password: str) -> None:
        with self._state_lock:
            self._memory[screen_id] = password

    def recall(self, screen_id: str) -> str | None:
        with self._state_lock:
            return self._memory.get(screen_id)

    def forget(self, screen_id: str) -> None:
        with self._state_lock:
            self._memory.pop(screen_id, None)

    @property
    def pending_ids(self) -> set[str]:
        """只存在内存、没能写进后端的屏幕 id（退出后会丢）。"""
        with self._state_lock:
            return set(self._dirty)

    # --- 解锁 ---------------------------------------------------------------
    def try_unlock(self) -> bool:
        """解锁当前后端（KDE 钱包 / 系统密钥环走系统提示框）。**必须放后台线程。**"""
        backend = self._backend
        if backend is None:
            return False
        unlocked = backend.try_unlock()
        if unlocked:
            self._flush_dirty()
        return unlocked

    def unlock_with_secret(self, secret: str) -> UnlockResult:
        """用主密码解锁内置库。**必须放后台线程**（KDF 要 100–300ms）。"""
        backend = self._backend
        if backend is None or not hasattr(backend, "unlock_with_secret"):
            return UnlockResult.ERROR
        result = backend.unlock_with_secret(secret)
        if result is UnlockResult.OK:
            self._flush_dirty()
        return result

    def flush_pending(self) -> None:
        """把锁定期间只存在内存里的密码补写进后端（后端已解锁时才有意义）。"""
        if self._backend is not None and self._backend.status is SecretsStatus.OK:
            self._flush_dirty()

    def _flush_dirty(self) -> None:
        """把锁定期间只存在内存里的密码补写进后端。"""
        with self._state_lock:
            pending = [(sid, self._memory.get(sid)) for sid in list(self._dirty)]
        for screen_id, password in pending:
            if password is not None and self._backend is not None:
                if self._backend.set(screen_id, password):
                    with self._state_lock:
                        self._dirty.discard(screen_id)

    # --- 内置库专属动作 ------------------------------------------------------
    def create_vault(self, secret: str) -> tuple[bool, str]:
        backend = self._backends.get(prefs.BACKEND_BUILTIN)
        if backend is None:
            backend = self._make_backend(prefs.BACKEND_BUILTIN)
        created, error = backend.create(secret)  # type: ignore[attr-defined]
        if created:
            self._flush_dirty()
        return created, error

    def reset_vault(self) -> None:
        """删掉内置库。**数据不可恢复** —— 调用方必须已经过反复确认/验证码。"""
        backend = self._backends.get(prefs.BACKEND_BUILTIN)
        if backend is None:
            return
        backend.reset()  # type: ignore[attr-defined]
        with self._state_lock:
            # 重置后内存里的密码要重新落盘，否则这次会话设过的密码就丢了
            self._dirty.update(self._memory)

    def change_master_password(self, old: str, new: str) -> tuple[bool, str]:
        backend = self._backends.get(prefs.BACKEND_BUILTIN)
        if backend is None:
            return False, "no built-in vault"
        return backend.change_secret(old, new)  # type: ignore[attr-defined]

    # --- 迁移 / 清除 ---------------------------------------------------------
    def present_ids(self, key: str, candidates: Sequence[str]) -> list[str] | None:
        """某个后端里有候选 id 中的哪几条（None = 问不到，例如锁着）。"""
        backend = self._backends.get(key)
        if backend is None:
            backend = self._make_backend(key)
        return backend.present_ids(candidates)

    def probe_backend(self, key: str) -> SecretsStatus:
        """探测**指定**后端（迁移向导用；代价与 `probe()` 相同）。"""
        return self._make_backend(key).probe()

    def status_of(self, key: str) -> SecretsStatus:
        """指定后端的**当前**状态（不再探测）。"""
        backend = self._backends.get(key)
        return backend.status if backend is not None else SecretsStatus.UNAVAILABLE

    def unlock_backend(self, key: str) -> bool:
        """解锁指定后端（系统提示框那类）。**必须放后台线程。**"""
        return self._make_backend(key).try_unlock()

    def unlock_backend_with_secret(self, key: str, secret: str) -> UnlockResult:
        """用主密码解锁指定后端（内置库）。**必须放后台线程。**"""
        return self._make_backend(key).unlock_with_secret(secret)

    def migrate_between(self, source: str, target: str, ids: Sequence[str],
                        on_progress: Callable[[int, int], None] | None = None,
                        ) -> tuple[list[str], dict[str, str]]:
        """把 source 里的 ids 搬到 target（两个都可以不是当前后端）。"""
        src = self._make_backend(source)
        dst = self._make_backend(target)
        copied, failed = migrate(src, dst, ids, on_progress)
        for screen_id in copied:
            value = dst.get(screen_id)
            if value is not None:
                with self._state_lock:
                    self._memory[screen_id] = value
                    self._dirty.discard(screen_id)
        return copied, failed

    def plan_merge_between(self, source: str, target: str,
                           ids: Sequence[str]) -> MergePlan:
        """算目标已有数据时的合并计划（**只读**，不写任何东西）。

        两个后端都没解锁时读到的都是 None → 会落到 `unreadable`，不会误判成新增。
        """
        return plan_merge(self._make_backend(source), self._make_backend(target), ids)

    def last_modified(self, key: str) -> float | None:
        backend = self._backends.get(key)
        if backend is None:
            backend = self._make_backend(key)
        return backend.last_modified()

    def migrate_to(self, target: str, ids: Sequence[str],
                   on_progress: Callable[[int, int], None] | None = None,
                   ) -> tuple[list[str], dict[str, str]]:
        """把当前后端里的 ids 搬到 target。返回 (成功的, {失败: 原因})。"""
        source = self._backend
        destination = self._make_backend(target)
        if source is None:
            return [], {}
        copied, failed = migrate(source, destination, ids, on_progress)
        # 迁移进来的值放进内存，省得后续再读一遍；待写队列也能清了
        for screen_id in copied:
            value = destination.get(screen_id)
            if value is not None:
                with self._state_lock:
                    self._memory[screen_id] = value
                    self._dirty.discard(screen_id)
        return copied, failed

    def wipe_backend(self, key: str, ids: Sequence[str]) -> tuple[int, list[str]]:
        """清掉某个后端里给定的条目。**只删这些 id。**"""
        backend = self._backends.get(key)
        if backend is None:
            backend = self._make_backend(key)
        return backend.wipe(ids)
