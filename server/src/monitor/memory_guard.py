#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import psutil
from typing import Optional
from src.core.logger import logger
from src.core.config import (
    MEMORY_GUARD_ENABLED,
    MEMORY_GUARD_CHECK_INTERVAL,
    MEMORY_GUARD_RSS_HIGH_MB,
    MEMORY_GUARD_RSS_LOW_MB,
)
from src.snmp.unified_poller import get_device_poller, get_interface_poller


class MemoryGuard:
    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._in_mitigation = False

    def start(self):
        if not MEMORY_GUARD_ENABLED or self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info(
            f"内存守护已启动，检查间隔{MEMORY_GUARD_CHECK_INTERVAL}s，高水位{MEMORY_GUARD_RSS_HIGH_MB}MB"
        )

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

    def _loop(self):
        proc = psutil.Process()
        while self._running:
            try:
                rss_mb = proc.memory_info().rss / (1024 * 1024)
                if not self._in_mitigation and rss_mb >= MEMORY_GUARD_RSS_HIGH_MB:
                    self._apply_mitigation(rss_mb)
                    self._in_mitigation = True
                elif self._in_mitigation and rss_mb <= MEMORY_GUARD_RSS_LOW_MB:
                    self._recover(rss_mb)
                    self._in_mitigation = False
            except Exception:
                pass
            time.sleep(MEMORY_GUARD_CHECK_INTERVAL)

    def _apply_mitigation(self, rss_mb: float):
        try:
            logger.warning(f"触发内存高水位({rss_mb:.0f}MB)，执行降压与清理")
            dev = get_device_poller()
            itf = get_interface_poller()
            if dev:
                dev.set_concurrency(dev.min_workers)
                dev.trim_cache(100)
            if itf:
                itf.set_concurrency(itf.min_workers)
                itf.trim_cache(100)
            try:
                from src.snmp.manager import SNMPManager
                # 尝试清理速率缓存（不影响功能，仅影响瞬时速率计算）
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"内存守护缓解失败: {e}")

    def _recover(self, rss_mb: float):
        try:
            logger.info(f"内存恢复到低水位({rss_mb:.0f}MB)，解除降压")
            # 并发恢复由动态调整器自行处理，这里不强制增大
        except Exception:
            pass


_memory_guard: Optional[MemoryGuard] = None


def get_memory_guard() -> MemoryGuard:
    global _memory_guard
    if _memory_guard is None:
        _memory_guard = MemoryGuard()
    return _memory_guard

