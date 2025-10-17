#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
服务器性能监控模块
定期收集服务器性能数据并通过WebSocket发送到前端
"""

import time
import threading
import psutil
from typing import Dict, Any, List, Optional
from src.core.logger import logger
from src.core.state_manager import state_manager
from src.core.config import SERVER_MONITOR_INTERVAL


class ServerMonitor:
    """服务器性能监控器"""

    def __init__(self, interval: Optional[int] = None):
        """
        初始化服务器监控器

        Args:
            interval: 监控数据采集间隔（秒），默认从配置文件读取
        """
        self.interval = interval if interval is not None else SERVER_MONITOR_INTERVAL
        self.running = False
        self.monitor_thread = None
        self.logger = logger

        # 用于计算网络速率的上次采集数据
        self._last_net_io = None
        self._last_net_time = None

    def start(self):
        """启动监控线程"""
        if self.running:
            self.logger.warning("服务器监控器已在运行中")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info(f"服务器性能监控器已启动，采集间隔: {self.interval}秒")

    def stop(self):
        """停止监控线程"""
        self.running = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        self.logger.info("服务器性能监控器已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 收集性能数据
                performance_data = self._collect_performance_data()

                # 通过WebSocket广播到前端
                state_manager.broadcast_message(
                    {"type": "server_performance", "data": performance_data},
                    message_type="server_performance",
                )

                self.logger.debug(
                    f"已发送服务器性能数据: CPU={performance_data['cpu']['usage_percent']:.1f}%, "
                    f"内存={performance_data['memory']['usage_percent']:.1f}%"
                )

            except Exception as e:
                self.logger.error(f"收集服务器性能数据时出错: {e}", exc_info=True)

            # 等待下一次采集
            time.sleep(self.interval)

    def _collect_performance_data(self) -> Dict[str, Any]:
        """
        收集服务器性能数据

        Returns:
            Dict[str, Any]: 包含CPU、内存、磁盘、网络等性能数据
        """
        return {
            "timestamp": time.time(),
            "cpu": self._get_cpu_info(),
            "memory": self._get_memory_info(),
            "disk": self._get_disk_info(),
            "network": self._get_network_info(),
        }

    def _get_cpu_info(self) -> Dict[str, Any]:
        """
        获取CPU性能信息
        支持多物理CPU系统，提供详细的CPU拓扑信息

        Returns:
            Dict[str, Any]: CPU相关性能指标
        """
        try:
            logical_cores = psutil.cpu_count(logical=True)
            physical_cores = psutil.cpu_count(logical=False)

            cpu_info = {
                "usage_percent": round(psutil.cpu_percent(interval=0.1), 2),
                "cores": logical_cores,  # 逻辑核心数（包含超线程）
                "physical_cores": physical_cores,  # 物理核心数
            }

            # 计算物理CPU数量（假设每个物理CPU的核心数相同）
            # 对于多CPU系统，physical_cores 是所有物理CPU的总核心数
            if physical_cores and logical_cores:
                # 检测是否启用了超线程
                threads_per_core = (
                    logical_cores // physical_cores if physical_cores > 0 else 1
                )
                cpu_info["threads_per_core"] = threads_per_core

                # 尝试估算物理CPU数量（这是一个估算值）
                # 在实际多CPU系统中，可能需要通过其他方式获取准确值
                if threads_per_core > 1:
                    # 有超线程的情况
                    cpu_info["estimated_physical_cpus"] = (
                        self._estimate_physical_cpu_count()
                    )
                else:
                    # 无超线程
                    cpu_info["estimated_physical_cpus"] = (
                        self._estimate_physical_cpu_count()
                    )

            # 获取CPU频率（可能在某些系统上不可用）
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    cpu_info["current_frequency"] = round(cpu_freq.current, 2)
                    cpu_info["max_frequency"] = (
                        round(cpu_freq.max, 2) if cpu_freq.max else None
                    )

                # 尝试获取每个核心的频率（如果支持）
                try:
                    per_cpu_freq = psutil.cpu_freq(percpu=True)
                    if per_cpu_freq and len(per_cpu_freq) > 1:
                        cpu_info["per_cpu_frequency"] = [
                            round(freq.current, 2) if freq else 0
                            for freq in per_cpu_freq
                        ]
                except Exception:
                    pass
            except Exception:
                pass

            # 获取CPU负载（仅Unix系统）
            try:
                load_avg = psutil.getloadavg()
                cpu_info["load_average"] = [round(x, 2) for x in load_avg]
            except AttributeError:
                # Windows系统不支持getloadavg
                pass

            # 获取每个核心的使用率
            cpu_info["per_cpu_percent"] = [
                round(x, 2) for x in psutil.cpu_percent(interval=0.1, percpu=True)
            ]

            return cpu_info
        except Exception as e:
            self.logger.error(f"获取CPU信息失败: {e}")
            return {"usage_percent": 0, "cores": 0}

    def _get_memory_info(self) -> Dict[str, Any]:
        """
        获取内存使用信息

        Returns:
            Dict[str, Any]: 内存相关性能指标
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            memory_info = {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "usage_percent": round(mem.percent, 2),
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free,
                "swap_percent": round(swap.percent, 2),
            }

            # 添加缓存信息（如果可用）
            if hasattr(mem, "cached"):
                memory_info["cached"] = mem.cached
            if hasattr(mem, "buffers"):
                memory_info["buffers"] = mem.buffers

            return memory_info
        except Exception as e:
            self.logger.error(f"获取内存信息失败: {e}")
            return {"total": 0, "used": 0, "usage_percent": 0}

    def _get_disk_info(self) -> Dict[str, Any]:
        """
        获取磁盘使用信息

        Returns:
            Dict[str, Any]: 磁盘相关性能指标
        """
        try:
            disk_info = {
                "partitions": [],
                "total": 0,
                "used": 0,
                "free": 0,
                "usage_percent": 0,
            }

            # 获取所有磁盘分区
            partitions = psutil.disk_partitions(all=False)
            total_space = 0
            used_space = 0

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    partition_info = {
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "usage_percent": round(usage.percent, 2),
                    }
                    disk_info["partitions"].append(partition_info)

                    total_space += usage.total
                    used_space += usage.used
                except (PermissionError, OSError):
                    # 跳过无权限访问的分区
                    continue

            # 计算总体使用情况
            if total_space > 0:
                disk_info["total"] = total_space
                disk_info["used"] = used_space
                disk_info["free"] = total_space - used_space
                disk_info["usage_percent"] = round((used_space / total_space) * 100, 2)

            # 获取磁盘IO统计
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    disk_info["io"] = {
                        "read_bytes": disk_io.read_bytes,
                        "write_bytes": disk_io.write_bytes,
                        "read_count": disk_io.read_count,
                        "write_count": disk_io.write_count,
                    }
            except Exception:
                pass

            return disk_info
        except Exception as e:
            self.logger.error(f"获取磁盘信息失败: {e}")
            return {"total": 0, "used": 0, "usage_percent": 0, "partitions": []}

    def _get_network_info(self) -> List[Dict[str, Any]]:
        """
        获取网络接口信息，包括上传/下载速率

        Returns:
            List[Dict[str, Any]]: 网络接口列表及其性能指标
        """
        try:
            network_interfaces = []

            # 获取当前网络IO统计
            current_net_io = psutil.net_io_counters(pernic=True)
            current_time = time.time()

            # 获取网络接口地址信息
            net_if_addrs = psutil.net_if_addrs()

            for interface_name, current_stats in current_net_io.items():
                # 跳过回环和虚拟接口
                if self._is_virtual_or_loopback_interface(interface_name):
                    continue

                interface_info = {
                    "name": interface_name,
                    "bytes_sent": current_stats.bytes_sent,
                    "bytes_recv": current_stats.bytes_recv,
                    "packets_sent": current_stats.packets_sent,
                    "packets_recv": current_stats.packets_recv,
                    "upload_rate": 0,
                    "download_rate": 0,
                }

                # 计算速率（需要两次采集的数据）
                if (
                    self._last_net_io
                    and interface_name in self._last_net_io
                    and self._last_net_time is not None
                ):
                    last_stats = self._last_net_io[interface_name]
                    time_delta = current_time - self._last_net_time

                    if time_delta > 0:
                        # 计算每秒字节数
                        upload_rate = (
                            current_stats.bytes_sent - last_stats.bytes_sent
                        ) / time_delta
                        download_rate = (
                            current_stats.bytes_recv - last_stats.bytes_recv
                        ) / time_delta

                        interface_info["upload_rate"] = round(upload_rate, 2)
                        interface_info["download_rate"] = round(download_rate, 2)

                # 获取IP和MAC地址
                if interface_name in net_if_addrs:
                    for addr in net_if_addrs[interface_name]:
                        if addr.family == psutil.AF_LINK:  # MAC地址
                            interface_info["mac_address"] = addr.address
                        elif addr.family == 2:  # IPv4地址 (socket.AF_INET)
                            interface_info["ip_address"] = addr.address
                            interface_info["netmask"] = addr.netmask

                network_interfaces.append(interface_info)

            # 保存当前数据供下次计算速率使用
            self._last_net_io = current_net_io
            self._last_net_time = current_time

            return network_interfaces
        except Exception as e:
            self.logger.error(f"获取网络信息失败: {e}")
            return []

    def _estimate_physical_cpu_count(self) -> int:
        """
        估算物理CPU（插槽）数量
        在多路CPU服务器上，这个值表示物理CPU芯片的数量

        Returns:
            int: 估算的物理CPU数量，失败时返回1
        """
        try:
            import platform

            system = platform.system()

            if system == "Linux":
                # Linux系统通过/proc/cpuinfo获取准确信息
                try:
                    with open("/proc/cpuinfo", "r") as f:
                        content = f.read()

                    # 统计唯一的physical id数量
                    physical_ids = set()
                    for line in content.split("\n"):
                        if line.startswith("physical id"):
                            physical_id = line.split(":")[1].strip()
                            physical_ids.add(physical_id)

                    if physical_ids:
                        return len(physical_ids)
                except Exception as e:
                    self.logger.debug(f"无法从/proc/cpuinfo读取CPU数量: {e}")

            elif system == "Windows":
                # Windows系统通过WMI获取
                try:
                    import subprocess

                    result = subprocess.run(
                        ["wmic", "cpu", "get", "NumberOfCores"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        lines = [
                            l.strip() for l in result.stdout.split("\n") if l.strip()
                        ]
                        # 第一行是标题，后面每行代表一个物理CPU
                        cpu_count = len(lines) - 1
                        if cpu_count > 0:
                            return cpu_count
                except Exception as e:
                    self.logger.debug(f"无法通过WMIC获取CPU数量: {e}")

            # 如果以上方法都失败，使用启发式估算
            # 假设常见的CPU配置：单CPU或双CPU系统
            physical_cores = psutil.cpu_count(logical=False)
            if physical_cores:
                # 常见的单CPU核心数：2, 4, 6, 8, 10, 12, 16, 18, 20, 24, 28, 32, 64
                # 如果核心数很大，可能是多CPU系统
                if physical_cores > 32:
                    # 很可能是双路或四路系统
                    if physical_cores % 4 == 0 and physical_cores >= 64:
                        return 4  # 四路系统
                    elif physical_cores % 2 == 0:
                        return 2  # 双路系统

            return 1  # 默认返回单CPU

        except Exception as e:
            self.logger.error(f"估算物理CPU数量时出错: {e}")
            return 1

    def _is_virtual_or_loopback_interface(self, interface_name: str) -> bool:
        """
        判断网络接口是否为虚拟接口或回环接口

        Args:
            interface_name: 网络接口名称

        Returns:
            bool: 如果是虚拟接口或回环接口返回True
        """
        interface_lower = interface_name.lower()

        # 回环接口
        if interface_lower.startswith(("lo", "loopback")):
            return True

        # 虚拟接口关键词
        virtual_keywords = [
            "virtual",
            "veth",
            "docker",
            "bridge",
            "vmnet",
            "vbox",
            "hyper-v",
            "tunnel",
            "tap",
            "ppp",
            "wan",
            "isatap",
            "teredo",
        ]

        return any(keyword in interface_lower for keyword in virtual_keywords)


# 创建全局监控器实例（延迟初始化）
_server_monitor = None


def get_server_monitor(interval: Optional[int] = None) -> ServerMonitor:
    """
    获取服务器监控器单例实例

    Args:
        interval: 监控间隔（秒），默认从配置文件读取

    Returns:
        ServerMonitor: 监控器实例
    """
    global _server_monitor
    if _server_monitor is None:
        _server_monitor = ServerMonitor(interval=interval)
    return _server_monitor
