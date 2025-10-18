#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SNMP统一轮询器 - 支持设备信息和接口信息轮询
快进快出队列模式：为每个设备建立独立轮询，根据性能动态调整并发数
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Tuple, Set, Literal, TYPE_CHECKING
from collections import deque
from datetime import datetime
import statistics

from src.database.managers.switch_manager import SwitchManager
from src.core.logger import logger

if TYPE_CHECKING:
    from src.snmp.manager import SNMPManager

PollType = Literal["device", "interface"]


class SNMPPoller:
    """
    SNMP统一轮询器（快进快出队列模式）

    支持设备信息和接口信息两种轮询类型。
    每个设备独立轮询，通过队列快速调度，根据性能动态调整并发数。
    """

    def __init__(
        self,
        switch_manager: SwitchManager,
        poll_type: PollType = "device",
        poll_interval: int = 60,
        min_workers: int = 5,
        max_workers: int = 50,
        device_timeout: int = 5,
        enable_cache: bool = True,
        cache_ttl: int = 300,
        dynamic_adjustment: bool = True,
    ):
        """
        初始化SNMP统一轮询器

        Args:
            switch_manager: 交换机管理器实例
            poll_type: 轮询类型 ("device": 设备信息, "interface": 接口信息)
            poll_interval: 轮询间隔（秒），默认60秒
            min_workers: 最小并发数，默认5
            max_workers: 最大并发数，默认50
            device_timeout: 单个设备超时时间（秒），默认5秒
            enable_cache: 是否启用结果缓存，默认True
            cache_ttl: 缓存生存时间（秒），默认300秒
            dynamic_adjustment: 是否启用动态并发调整，默认True
        """
        self.switch_manager = switch_manager
        self.poll_type = poll_type
        self.poll_interval = poll_interval
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = min_workers
        self.device_timeout = device_timeout
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        self.dynamic_adjustment = dynamic_adjustment

        self.snmp_manager: Optional["SNMPManager"] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # 快进快出队列
        self._task_queue: Optional[asyncio.Queue] = None
        self._active_tasks: Set[str] = set()
        self._active_lock: Optional[asyncio.Lock] = None

        # 用于跟踪所有运行中的任务
        self._worker_tasks: List[asyncio.Task] = []
        self._enqueue_task: Optional[asyncio.Task] = None
        self._adjustment_task: Optional[asyncio.Task] = None

        # 缓存
        self._cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._cache_lock = threading.Lock()

        # 性能统计
        self._stats: Dict[str, Any] = {
            "total_polls": 0,
            "success_count": 0,
            "error_count": 0,
            "avg_response_time": 0.0,
            "last_poll_duration": 0.0,
            "queue_size": 0,
            "active_workers": 0,
            "current_concurrency": min_workers,
        }
        self._stats_lock = threading.Lock()

        # 响应时间历史
        self._response_times: deque = deque(maxlen=100)
        self._response_lock = threading.Lock()

        # 失败设备跟踪
        self._failure_tracker: Dict[str, int] = {}
        self._failure_lock = threading.Lock()

        # 动态调整参数
        self._last_adjustment_time = 0
        self._adjustment_interval = 30

        # 根据轮询类型设置名称
        self._type_name = "设备" if poll_type == "device" else "接口"

    def start(self):
        """启动轮询器"""
        if self._running:
            logger.warning(f"SNMP{self._type_name}轮询器已在运行中")
            return

        # 延迟导入并初始化SNMPManager，避免循环导入
        if self.snmp_manager is None:
            from src.snmp.manager import SNMPManager

            self.snmp_manager = SNMPManager()

        self._running = True
        self._thread = threading.Thread(target=self._run_poller, daemon=True)
        self._thread.start()
        logger.info(
            f"SNMP{self._type_name}轮询器已启动，轮询间隔: {self.poll_interval}秒, "
            f"并发范围: {self.min_workers}-{self.max_workers}"
        )

    def stop(self):
        """停止轮询器"""
        if not self._running:
            return

        logger.info(f"正在停止SNMP{self._type_name}轮询器...")
        self._running = False

        # 优雅地停止异步任务
        if self._loop and not self._loop.is_closed():
            # 在事件循环中调度清理任务
            future = asyncio.run_coroutine_threadsafe(self._cleanup_tasks(), self._loop)
            try:
                # 等待清理完成，最多10秒
                future.result(timeout=10)
            except Exception as e:
                logger.warning(f"清理任务时出错: {e}")

        # 等待线程结束
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        logger.info(f"SNMP{self._type_name}轮询器已停止")

    def _run_poller(self):
        """在独立线程中运行轮询器"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._polling_loop())
        except Exception as e:
            logger.error(f"SNMP{self._type_name}轮询器运行出错: {e}")
        finally:
            try:
                # 取消所有剩余任务
                pending = asyncio.all_tasks(self._loop)
                for task in pending:
                    task.cancel()
                # 等待所有任务完成取消
                if pending:
                    self._loop.run_until_complete(
                        asyncio.gather(*pending, return_exceptions=True)
                    )
            except Exception as e:
                logger.debug(f"清理剩余任务时出错: {e}")
            finally:
                self._loop.close()

    async def _polling_loop(self):
        """异步轮询循环（快进快出队列模式）"""
        self._task_queue = asyncio.Queue()
        self._active_lock = asyncio.Lock()

        logger.info(
            f"SNMP{self._type_name}轮询循环已启动（队列模式），初始并发数: {self.current_workers}"
        )

        # 启动工作协程池
        self._worker_tasks = [
            asyncio.create_task(self._worker(i)) for i in range(self.current_workers)
        ]

        # 启动设备入队协程
        self._enqueue_task = asyncio.create_task(self._enqueue_devices())

        # 启动动态调整协程
        if self.dynamic_adjustment:
            self._adjustment_task = asyncio.create_task(self._dynamic_adjust_workers())

        try:
            # 等待所有任务完成
            all_tasks = [self._enqueue_task] + self._worker_tasks
            if self._adjustment_task:
                all_tasks.append(self._adjustment_task)
            await asyncio.gather(*all_tasks, return_exceptions=True)
        except asyncio.CancelledError:
            logger.debug(f"SNMP{self._type_name}轮询循环被取消")
        except Exception as e:
            logger.error(f"轮询循环出错: {e}", exc_info=True)

        logger.info(f"SNMP{self._type_name}轮询循环已退出")

    async def _enqueue_devices(self):
        """持续将设备加入轮询队列"""
        assert self._task_queue is not None
        assert self._active_lock is not None

        while self._running:
            try:
                switches = self.switch_manager.get_all_switches()

                if not switches:
                    logger.debug("数据库中没有交换机配置")
                    await asyncio.sleep(self.poll_interval)
                    continue

                enqueued = 0
                for switch in switches:
                    ip = switch.get("ip")
                    if not ip:
                        continue

                    async with self._active_lock:
                        if ip in self._active_tasks:
                            continue

                    await self._task_queue.put(switch)
                    enqueued += 1

                with self._stats_lock:
                    self._stats["queue_size"] = self._task_queue.qsize()

                logger.debug(f"已将 {enqueued} 个设备加入{self._type_name}轮询队列")

                for _ in range(self.poll_interval):
                    if not self._running:
                        break
                    await asyncio.sleep(1)

                self._cleanup_cache()

            except asyncio.CancelledError:
                logger.debug(f"设备入队协程被取消")
                break
            except Exception as e:
                logger.error(f"设备入队过程出错: {e}", exc_info=True)
                await asyncio.sleep(5)

    async def _worker(self, worker_id: int):
        """工作协程，从队列中取设备并执行轮询"""
        assert self._task_queue is not None
        assert self._active_lock is not None

        logger.debug(f"工作协程 {worker_id} 已启动")

        while self._running:
            try:
                try:
                    switch_config = await asyncio.wait_for(
                        self._task_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                ip = switch_config.get("ip")
                if not ip:
                    self._task_queue.task_done()
                    continue

                async with self._active_lock:
                    self._active_tasks.add(ip)
                    active_count = len(self._active_tasks)

                with self._stats_lock:
                    self._stats["active_workers"] = active_count

                start_time = time.time()
                result = await self._poll_single_switch(switch_config)
                response_time = time.time() - start_time

                with self._response_lock:
                    self._response_times.append(response_time)

                self._send_single_result(result)

                async with self._active_lock:
                    self._active_tasks.discard(ip)

                self._task_queue.task_done()

            except asyncio.CancelledError:
                logger.debug(f"工作协程 {worker_id} 被取消")
                break
            except Exception as e:
                logger.error(f"工作协程 {worker_id} 出错: {e}", exc_info=True)
                await asyncio.sleep(1)

        logger.debug(f"工作协程 {worker_id} 已退出")

    async def _poll_single_switch(
        self, switch_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """轮询单个交换机（带超时控制和缓存优化）"""
        ip = switch_config.get("ip", "")
        switch_id = switch_config.get("id")

        if self.enable_cache:
            cached_result = self._get_from_cache(ip)
            if cached_result is not None:
                logger.debug(f"使用缓存{self._type_name}数据: IP={ip}")
                with self._stats_lock:
                    self._stats["success_count"] += 1
                    self._stats["total_polls"] += 1
                return cached_result

        try:
            result = await asyncio.wait_for(
                self._do_poll_switch(switch_config), timeout=self.device_timeout
            )

            with self._stats_lock:
                self._stats["total_polls"] += 1
                if result.get("type") == "success":
                    self._stats["success_count"] += 1
                    self._update_failure_tracker(ip, success=True)
                    if self.enable_cache:
                        self._save_to_cache(ip, result)
                else:
                    self._stats["error_count"] += 1
                    self._update_failure_tracker(ip, success=False)

            return result

        except asyncio.TimeoutError:
            self._update_failure_tracker(ip, success=False)
            with self._stats_lock:
                self._stats["error_count"] += 1
                self._stats["total_polls"] += 1
            return {
                "type": "error",
                "ip": ip,
                "switch_id": switch_id,
                "error": f"{self._type_name}轮询超时({self.device_timeout}秒)",
                "poll_time": time.time(),
            }
        except Exception as e:
            self._update_failure_tracker(ip, success=False)
            with self._stats_lock:
                self._stats["error_count"] += 1
                self._stats["total_polls"] += 1
            logger.debug(f"轮询交换机{self._type_name}失败: IP={ip}, 错误={str(e)}")
            return {
                "type": "error",
                "ip": ip,
                "switch_id": switch_id,
                "error": str(e),
                "poll_time": time.time(),
            }

    async def _do_poll_switch(self, switch_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行实际的轮询（不含超时控制）"""
        assert self.snmp_manager is not None, "SNMP Manager未初始化"

        ip = switch_config.get("ip", "")
        snmp_version = switch_config.get("snmp_version", "v2c")
        switch_id = switch_config.get("id")

        kwargs = self._prepare_snmp_kwargs(switch_config)

        # 根据轮询类型调用不同的方法
        if self.poll_type == "device":
            data = await self.snmp_manager.monitor.get_device_info(
                ip, snmp_version, **kwargs
            )

            if not data or not any(data.values()):
                return {
                    "type": "error",
                    "ip": ip,
                    "switch_id": switch_id,
                    "error": "SNMP连接超时或配置错误",
                    "poll_time": time.time(),
                }

            return {
                "type": "success",
                "ip": ip,
                "switch_id": switch_id,
                "snmp_version": snmp_version,
                "device_info": data,
                "poll_time": time.time(),
            }
        else:  # interface
            data = await self.snmp_manager.monitor.get_interface_info(
                ip, snmp_version, **kwargs
            )

            if not data:
                return {
                    "type": "error",
                    "ip": ip,
                    "switch_id": switch_id,
                    "error": "SNMP连接超时或配置错误",
                    "poll_time": time.time(),
                }

            return {
                "type": "success",
                "ip": ip,
                "switch_id": switch_id,
                "snmp_version": snmp_version,
                "interface_info": data,
                "interface_count": len(data),
                "poll_time": time.time(),
            }

    def _prepare_snmp_kwargs(self, switch_config: Dict[str, Any]) -> Dict[str, Any]:
        """准备SNMP认证参数"""
        snmp_version = switch_config.get("snmp_version", "v2c")
        kwargs = {}

        if snmp_version in ["v1", "v2c", "2c"]:
            kwargs["community"] = switch_config.get("community", "public")
        elif snmp_version == "v3":
            kwargs["user"] = switch_config.get("user", "")
            if switch_config.get("auth_key"):
                kwargs["auth_key"] = switch_config.get("auth_key")
            if switch_config.get("auth_protocol"):
                kwargs["auth_protocol"] = switch_config.get("auth_protocol", "md5")
            if switch_config.get("priv_key"):
                kwargs["priv_key"] = switch_config.get("priv_key")
            if switch_config.get("priv_protocol"):
                kwargs["priv_protocol"] = switch_config.get("priv_protocol", "des")

        return kwargs

    def _get_from_cache(self, ip: str) -> Optional[Dict[str, Any]]:
        """从缓存获取数据"""
        with self._cache_lock:
            if ip in self._cache:
                cached_data, cache_time = self._cache[ip]
                if time.time() - cache_time < self.cache_ttl:
                    return cached_data
                else:
                    del self._cache[ip]
        return None

    def _save_to_cache(self, ip: str, data: Dict[str, Any]):
        """保存数据到缓存"""
        with self._cache_lock:
            self._cache[ip] = (data, time.time())

    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        with self._cache_lock:
            expired_keys = [
                ip
                for ip, (_, cache_time) in self._cache.items()
                if current_time - cache_time >= self.cache_ttl
            ]
            for ip in expired_keys:
                del self._cache[ip]

            if expired_keys:
                logger.debug(f"清理 {len(expired_keys)} 个过期{self._type_name}缓存项")

    def _update_failure_tracker(self, ip: str, success: bool):
        """更新设备失败跟踪"""
        with self._failure_lock:
            if success:
                self._failure_tracker[ip] = 0
            else:
                self._failure_tracker[ip] = self._failure_tracker.get(ip, 0) + 1

    async def _dynamic_adjust_workers(self):
        """动态调整工作协程数量"""
        assert self._task_queue is not None

        while self._running:
            try:
                await asyncio.sleep(self._adjustment_interval)

                current_time = time.time()
                if (
                    current_time - self._last_adjustment_time
                    < self._adjustment_interval
                ):
                    continue

                self._last_adjustment_time = current_time

                with self._response_lock:
                    if len(self._response_times) < 10:
                        continue
                    avg_response = statistics.mean(self._response_times)
                    p95_response = statistics.quantiles(self._response_times, n=20)[18]

                queue_size = self._task_queue.qsize()
                with self._stats_lock:
                    active_workers = self._stats.get("active_workers", 0)
                    success_rate = (
                        self._stats["success_count"] / self._stats["total_polls"]
                        if self._stats["total_polls"] > 0
                        else 0
                    )

                new_workers = self.current_workers

                if queue_size > 20 and p95_response < self.device_timeout * 0.5:
                    new_workers = min(self.current_workers + 5, self.max_workers)
                    logger.info(
                        f"队列积压({queue_size})，响应良好(p95={p95_response:.2f}s)，增加并发至 {new_workers}"
                    )
                elif p95_response > self.device_timeout * 0.8 and success_rate < 0.7:
                    new_workers = max(self.current_workers - 3, self.min_workers)
                    logger.info(
                        f"响应缓慢(p95={p95_response:.2f}s)，成功率低({success_rate:.2%})，降低并发至 {new_workers}"
                    )
                elif queue_size < 5 and active_workers < self.current_workers * 0.3:
                    new_workers = max(self.current_workers - 2, self.min_workers)
                    logger.debug(f"队列空闲，降低并发至 {new_workers}")

                if new_workers != self.current_workers:
                    await self._adjust_worker_pool(new_workers)
                    with self._stats_lock:
                        self._stats["current_concurrency"] = new_workers
                        self._stats["avg_response_time"] = avg_response

            except asyncio.CancelledError:
                logger.debug(f"动态调整协程被取消")
                break
            except Exception as e:
                logger.error(f"动态调整并发数出错: {e}", exc_info=True)

    async def _adjust_worker_pool(self, target_workers: int):
        """调整工作协程池大小"""
        current = self.current_workers
        if target_workers > current:
            for i in range(current, target_workers):
                task = asyncio.create_task(self._worker(i))
                self._worker_tasks.append(task)
            logger.info(f"工作协程数增加: {current} -> {target_workers}")
        self.current_workers = target_workers

    async def _cleanup_tasks(self):
        """清理所有异步任务"""
        logger.debug(f"开始清理{self._type_name}轮询器任务...")

        # 取消所有任务
        tasks_to_cancel = []
        if self._adjustment_task and not self._adjustment_task.done():
            tasks_to_cancel.append(self._adjustment_task)
        if self._enqueue_task and not self._enqueue_task.done():
            tasks_to_cancel.append(self._enqueue_task)
        tasks_to_cancel.extend([t for t in self._worker_tasks if not t.done()])

        for task in tasks_to_cancel:
            task.cancel()

        # 等待所有任务完成取消
        if tasks_to_cancel:
            await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

        logger.debug(f"{self._type_name}轮询器任务清理完成")

    def _send_single_result(self, result: Dict[str, Any]):
        """立即发送单个轮询结果（快进快出）"""
        from src.core.state_manager import state_manager

        try:
            msg_type = (
                "snmpDeviceUpdate"
                if self.poll_type == "device"
                else "snmpInterfaceUpdate"
            )
            state_manager.broadcast_message(
                {
                    "type": msg_type,
                    "data": result,
                    "poll_time": time.time(),
                }
            )
        except Exception as e:
            logger.error(f"发送{self._type_name}轮询结果失败: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """获取轮询统计信息"""
        with self._stats_lock:
            stats = self._stats.copy()

        with self._failure_lock:
            stats["failed_devices"] = sum(
                1 for count in self._failure_tracker.values() if count > 0
            )
            stats["highly_failed_devices"] = sum(
                1 for count in self._failure_tracker.values() if count >= 5
            )

        with self._cache_lock:
            stats["cached_devices"] = len(self._cache)

        if self._task_queue:
            stats["queue_size"] = self._task_queue.qsize()

        with self._response_lock:
            if self._response_times:
                stats["avg_response_time"] = statistics.mean(self._response_times)
                stats["p95_response_time"] = (
                    statistics.quantiles(self._response_times, n=20)[18]
                    if len(self._response_times) >= 20
                    else max(self._response_times)
                )

        return stats

    @property
    def is_running(self) -> bool:
        """检查轮询器是否正在运行"""
        return self._running


# 全局轮询器实例
_device_poller: Optional[SNMPPoller] = None
_interface_poller: Optional[SNMPPoller] = None


def start_device_poller(
    switch_manager: SwitchManager,
    poll_interval: int = 10,
    min_workers: int = 5,
    max_workers: int = 20,
    device_timeout: int = 30,
    **kwargs,
) -> SNMPPoller:
    """启动设备信息轮询器"""
    global _device_poller

    if _device_poller is not None and _device_poller.is_running:
        logger.warning("SNMP设备轮询器已在运行中")
        return _device_poller

    _device_poller = SNMPPoller(
        switch_manager=switch_manager,
        poll_type="device",
        poll_interval=poll_interval,
        min_workers=min_workers,
        max_workers=max_workers,
        device_timeout=device_timeout,
        **kwargs,
    )
    _device_poller.start()
    return _device_poller


def start_interface_poller(
    switch_manager: SwitchManager,
    poll_interval: int = 30,
    min_workers: int = 5,
    max_workers: int = 30,
    device_timeout: int = 60,
    **kwargs,
) -> SNMPPoller:
    """启动接口信息轮询器"""
    global _interface_poller

    if _interface_poller is not None and _interface_poller.is_running:
        logger.warning("SNMP接口轮询器已在运行中")
        return _interface_poller

    _interface_poller = SNMPPoller(
        switch_manager=switch_manager,
        poll_type="interface",
        poll_interval=poll_interval,
        min_workers=min_workers,
        max_workers=max_workers,
        device_timeout=device_timeout,
        **kwargs,
    )
    _interface_poller.start()
    return _interface_poller


def stop_device_poller():
    """停止设备信息轮询器"""
    global _device_poller
    if _device_poller is not None:
        _device_poller.stop()
        _device_poller = None


def stop_interface_poller():
    """停止接口信息轮询器"""
    global _interface_poller
    if _interface_poller is not None:
        _interface_poller.stop()
        _interface_poller = None


def get_device_poller() -> Optional[SNMPPoller]:
    """获取设备信息轮询器实例"""
    return _device_poller


def get_interface_poller() -> Optional[SNMPPoller]:
    """获取接口信息轮询器实例"""
    return _interface_poller


__all__ = [
    "SNMPPoller",
    "start_device_poller",
    "start_interface_poller",
    "stop_device_poller",
    "stop_interface_poller",
    "get_device_poller",
    "get_interface_poller",
]
