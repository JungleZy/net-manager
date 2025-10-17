#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SNMP持续轮询器 - 定期获取交换机设备信息
优化版本：支持100+设备的高效轮询
"""

import asyncio
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Tuple
from collections import deque
from datetime import datetime

from src.database.managers.switch_manager import SwitchManager
from src.snmp.manager import SNMPManager
from src.core.logger import logger


class SNMPContinuousPoller:
    """
    SNMP持续轮询器

    定期从数据库中获取所有交换机配置信息，
    然后通过SNMP协议获取每个交换机的设备信息。
    """

    def __init__(
        self,
        switch_manager: SwitchManager,
        poll_interval: int = 60,
        max_workers: int = 20,  # 提升并发数以应对100个设备
        device_timeout: int = 5,  # 降低单设备超时时间，快速失败
        batch_size: int = 50,  # 批量处理大小
        enable_cache: bool = True,  # 启用结果缓存
        cache_ttl: int = 300,  # 缓存生存时间（秒）
    ):
        """
        初始化SNMP持续轮询器（优化版）

        Args:
            switch_manager: 交换机管理器实例
            poll_interval: 轮询间隔（秒），默认60秒
            max_workers: 最大并发工作数，默认20（适配100+设备）
            device_timeout: 单个设备超时时间（秒），默认5秒（快速失败）
            batch_size: 批量处理大小，默认50（分批处理减少内存峰值）
            enable_cache: 是否启用结果缓存，默认True
            cache_ttl: 缓存生存时间（秒），默认300秒
        """
        self.switch_manager = switch_manager
        self.poll_interval = poll_interval
        self.max_workers = max_workers
        self.device_timeout = device_timeout
        self.batch_size = batch_size
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl

        self.snmp_manager = SNMPManager()
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        # 性能优化：设备状态缓存
        self._device_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._cache_lock = threading.Lock()

        # 性能统计
        self._stats: Dict[str, float] = {
            "total_polls": 0.0,
            "success_count": 0.0,
            "error_count": 0.0,
            "avg_poll_time": 0.0,
            "last_poll_duration": 0.0,
        }
        self._stats_lock = threading.Lock()

        # 失败设备跟踪（连续失败则降低轮询频率）
        self._failure_tracker: Dict[str, int] = {}
        self._failure_lock = threading.Lock()

    def start(self):
        """启动轮询器"""
        if self._running:
            logger.warning("SNMP轮询器已在运行中")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_poller, daemon=True)
        self._thread.start()
        logger.info(f"SNMP轮询器已启动，轮询间隔: {self.poll_interval}秒")

    def stop(self):
        """停止轮询器"""
        if not self._running:
            return

        logger.info("正在停止SNMP轮询器...")
        self._running = False

        if self._loop and self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)

        if self._thread:
            self._thread.join(timeout=5)

        logger.info("SNMP轮询器已停止")

    def _run_poller(self):
        """在独立线程中运行轮询器"""
        # 创建新的事件循环
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(self._polling_loop())
        except Exception as e:
            logger.error(f"SNMP轮询器运行出错: {e}")
        finally:
            self._loop.close()

    async def _polling_loop(self):
        """异步轮询循环（优化版）"""
        logger.info(
            f"SNMP轮询循环已启动，并发数: {self.max_workers}, 批量大小: {self.batch_size}"
        )

        while self._running:
            poll_start = time.time()
            try:
                # 执行一次轮询
                await self._poll_all_switches()

                poll_duration = time.time() - poll_start
                with self._stats_lock:
                    self._stats["last_poll_duration"] = poll_duration

                logger.info(f"本轮轮询耗时: {poll_duration:.2f}秒")

                # 等待下一次轮询（可中断）
                for _ in range(self.poll_interval):
                    if not self._running:
                        break
                    await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"轮询过程中出错: {e}", exc_info=True)
                # 发生错误后等待一段时间再继续
                await asyncio.sleep(5)

        logger.info("SNMP轮询循环已退出")

    async def _poll_all_switches(self):
        """轮询所有交换机（分批优化版）"""
        try:
            # 从数据库获取所有交换机配置
            switches = self.switch_manager.get_all_switches()

            if not switches:
                logger.debug("数据库中没有交换机配置")
                return

            total_switches = len(switches)
            logger.info(f"开始轮询 {total_switches} 个交换机设备")

            # 分批处理，避免内存峰值
            all_results = []
            for i in range(0, len(switches), self.batch_size):
                batch = switches[i : i + self.batch_size]
                batch_num = i // self.batch_size + 1
                total_batches = (len(switches) + self.batch_size - 1) // self.batch_size

                logger.debug(
                    f"处理批次 {batch_num}/{total_batches}，设备数: {len(batch)}"
                )

                # 并发执行当前批次
                batch_results = await self._poll_batch(batch)
                all_results.extend(batch_results)

                # 批次间短暂休息，避免网络拥塞
                if i + self.batch_size < len(switches):
                    await asyncio.sleep(0.1)

            # 统计结果
            success_count = sum(
                1
                for r in all_results
                if isinstance(r, dict) and r.get("type") == "success"
            )
            error_count = len(all_results) - success_count

            # 更新统计信息
            with self._stats_lock:
                self._stats["total_polls"] += float(len(all_results))
                self._stats["success_count"] += float(success_count)
                self._stats["error_count"] += float(error_count)

            # logger.info(
            #     f"轮询完成: 成功 {success_count}/{len(all_results)} 个, 失败 {error_count} 个"
            # )

            # 一次性发送所有结果（成功+失败）
            if all_results:
                self._send_poll_results(all_results)

            # 定期清理过期缓存
            self._cleanup_cache()

        except Exception as e:
            logger.error(f"轮询所有交换机时出错: {e}", exc_info=True)

    async def _poll_batch(self, switches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """并发轮询一批交换机"""
        semaphore = asyncio.Semaphore(self.max_workers)

        async def limited_poll(switch_config):
            async with semaphore:
                return await self._poll_single_switch(switch_config)

        results = await asyncio.gather(
            *[limited_poll(sw) for sw in switches], return_exceptions=True
        )

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"轮询设备异常: {switches[i].get('ip')}, {result}")
                processed_results.append(
                    {
                        "type": "error",
                        "ip": switches[i].get("ip"),
                        "switch_id": switches[i].get("id"),
                        "error": str(result),
                        "poll_time": time.time(),
                    }
                )
            else:
                processed_results.append(result)

        return processed_results

    def _filter_switches_by_failure(
        self, switches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """根据失败次数过滤设备（智能跳过策略）"""
        filtered = []
        with self._failure_lock:
            for switch in switches:
                ip = switch.get("ip")
                if not ip:
                    continue

                failure_count = self._failure_tracker.get(ip, 0)

                # 连续失败5次以上，每5轮才轮询一次
                if failure_count >= 5:
                    if int(self._stats["total_polls"]) % 5 == 0:
                        filtered.append(switch)
                    # else: 跳过本轮
                else:
                    filtered.append(switch)

        return filtered

    async def _poll_single_switch(
        self, switch_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        轮询单个交换机（带超时控制和缓存优化）

        Args:
            switch_config: 交换机配置字典

        Returns:
            包含设备信息的字典
        """
        ip = switch_config.get("ip", "")
        switch_id = switch_config.get("id")

        # 检查缓存
        if self.enable_cache:
            cached_result = self._get_from_cache(ip)
            if cached_result is not None:
                logger.debug(f"使用缓存数据: IP={ip}")
                # 缓存数据直接返回，由轮询完成后统一发送
                return cached_result

        try:
            # 使用asyncio.wait_for加入超时控制
            result = await asyncio.wait_for(
                self._do_poll_switch(switch_config), timeout=self.device_timeout
            )

            # 更新失败跟踪
            if result.get("type") == "success":
                self._update_failure_tracker(ip, success=True)
                # 缓存成功结果
                if self.enable_cache:
                    self._save_to_cache(ip, result)
            else:
                self._update_failure_tracker(ip, success=False)

            return result

        except asyncio.TimeoutError:
            # 超时处理
            self._update_failure_tracker(ip, success=False)
            timeout_result = {
                "type": "error",
                "ip": ip,
                "switch_id": switch_id,
                "error": f"轮询超时({self.device_timeout}秒)",
                "poll_time": time.time(),
            }
            return timeout_result
        except Exception as e:
            self._update_failure_tracker(ip, success=False)
            logger.debug(f"轮询交换机失败: IP={ip}, 错误={str(e)}")
            exception_result = {
                "type": "error",
                "ip": ip,
                "switch_id": switch_id,
                "error": str(e),
                "poll_time": time.time(),
            }
            return exception_result

    async def _do_poll_switch(self, switch_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行实际的设备轮询（不含超时控制）

        Args:
            switch_config: 交换机配置字典

        Returns:
            包含设备信息的字典
        """
        ip = switch_config.get("ip", "")
        snmp_version = switch_config.get("snmp_version", "v2c")
        switch_id = switch_config.get("id")

        # 准备SNMP认证参数
        kwargs = self._prepare_snmp_kwargs(switch_config)

        # 获取设备信息
        device_info = await self.snmp_manager.monitor.get_device_info(
            ip, snmp_version, **kwargs
        )

        # 检查是否成功获取到设备信息
        if not device_info or not any(device_info.values()):
            # 设备信息为空，表示连接失败
            error_result = {
                "type": "error",
                "ip": ip,
                "switch_id": switch_id,
                "error": "SNMP连接超时或配置错误",
                "poll_time": time.time(),
            }
            return error_result

        # 组合完整的设备信息
        result = {
            "type": "success",
            "ip": ip,
            "switch_id": switch_id,
            "snmp_version": snmp_version,
            "device_info": device_info,
            "poll_time": time.time(),
        }

        return result

    def _prepare_snmp_kwargs(self, switch_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备SNMP认证参数

        Args:
            switch_config: 交换机配置字典

        Returns:
            SNMP认证参数字典
        """
        snmp_version = switch_config.get("snmp_version", "v2c")
        kwargs = {}

        if snmp_version in ["v1", "v2c", "2c"]:
            # v1和v2c版本使用community
            kwargs["community"] = switch_config.get("community", "public")
        elif snmp_version == "v3":
            # v3版本使用用户认证
            kwargs["user"] = switch_config.get("user", "")

            # 可选的认证参数
            if switch_config.get("auth_key"):
                kwargs["auth_key"] = switch_config.get("auth_key")

            if switch_config.get("auth_protocol"):
                kwargs["auth_protocol"] = switch_config.get("auth_protocol", "md5")

            # 可选的加密参数
            if switch_config.get("priv_key"):
                kwargs["priv_key"] = switch_config.get("priv_key")

            if switch_config.get("priv_protocol"):
                kwargs["priv_protocol"] = switch_config.get("priv_protocol", "des")

        return kwargs

    def _get_from_cache(self, ip: str) -> Optional[Dict[str, Any]]:
        """从缓存获取设备信息"""
        with self._cache_lock:
            if ip in self._device_cache:
                cached_data, cache_time = self._device_cache[ip]
                if time.time() - cache_time < self.cache_ttl:
                    return cached_data
                else:
                    # 缓存过期，删除
                    del self._device_cache[ip]
        return None

    def _save_to_cache(self, ip: str, data: Dict[str, Any]):
        """保存设备信息到缓存"""
        with self._cache_lock:
            self._device_cache[ip] = (data, time.time())

    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        with self._cache_lock:
            expired_keys = [
                ip
                for ip, (_, cache_time) in self._device_cache.items()
                if current_time - cache_time >= self.cache_ttl
            ]
            for ip in expired_keys:
                del self._device_cache[ip]

            if expired_keys:
                logger.debug(f"清理 {len(expired_keys)} 个过期缓存项")

    def _update_failure_tracker(self, ip: str, success: bool):
        """更新设备失败跟踪"""
        with self._failure_lock:
            if success:
                # 成功则重置失败计数
                self._failure_tracker[ip] = 0
            else:
                # 失败则累加
                self._failure_tracker[ip] = self._failure_tracker.get(ip, 0) + 1

    def _send_poll_results(self, results: List[Dict[str, Any]]):
        """
        发送轮询结果（成功+失败合并为一条消息）

        Args:
            results: 轮询结果列表
        """
        from src.core.state_manager import state_manager

        try:
            # 统计成功和失败数量
            success_results = [r for r in results if r.get("type") == "success"]
            error_results = [r for r in results if r.get("type") == "error"]

            # 一次性发送所有结果
            state_manager.broadcast_message(
                {
                    "type": "snmpDeviceBatch",
                    "data": results,
                    "summary": {
                        "total": len(results),
                        "success": len(success_results),
                        "error": len(error_results),
                    },
                    "poll_time": time.time(),
                }
            )

            logger.info(
                f"WebSocket发送轮询结果: 总数={len(results)}, "
                f"成功={len(success_results)}, 失败={len(error_results)}"
            )

        except Exception as e:
            logger.error(f"发送轮询结果失败: {e}")

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
            stats["cached_devices"] = len(self._device_cache)

        return stats

    @property
    def is_running(self) -> bool:
        """检查轮询器是否正在运行"""
        return self._running


# 全局轮询器实例
_global_poller: Optional[SNMPContinuousPoller] = None


def start_snmp_poller(
    switch_manager: SwitchManager,
    poll_interval: int = 60,
    max_workers: int = 10,
    device_timeout: int = 10,  # 单个设备超时
) -> SNMPContinuousPoller:
    """
    启动全局SNMP轮询器

    Args:
        switch_manager: 交换机管理器实例
        poll_interval: 轮询间隔（秒）
        max_workers: 最大并发工作数
        device_timeout: 单个设备超时时间（秒）

    Returns:
        轮询器实例
    """
    global _global_poller

    if _global_poller is not None and _global_poller.is_running:
        logger.warning("SNMP轮询器已在运行中")
        return _global_poller

    _global_poller = SNMPContinuousPoller(
        switch_manager=switch_manager,
        poll_interval=poll_interval,
        max_workers=max_workers,
        device_timeout=device_timeout,  # 传递超时参数
    )
    _global_poller.start()

    return _global_poller


def stop_snmp_poller():
    """停止全局SNMP轮询器"""
    global _global_poller

    if _global_poller is not None:
        _global_poller.stop()
        _global_poller = None


def get_snmp_poller() -> Optional[SNMPContinuousPoller]:
    """获取全局SNMP轮询器实例"""
    return _global_poller


# 导出公共接口
__all__ = [
    "SNMPContinuousPoller",
    "start_snmp_poller",
    "stop_snmp_poller",
    "get_snmp_poller",
]
