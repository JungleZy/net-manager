#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
异步TCP服务端 - 用于与Net Manager客户端建立长连接并接收数据
基于asyncio实现，支持单线程处理数千个并发连接
"""

import asyncio
import json
import struct
import time
import uuid
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from src.core.config import (
    TCP_PORT,
    TCP_RECV_TIMEOUT,
    TCP_MAX_MESSAGE_SIZE,
    TCP_MAX_CLIENTS,
    DEVICE_PERSIST_QUEUE_MAXSIZE,
    DEVICE_PERSIST_FLUSH_INTERVAL_MS,
    DEVICE_PERSIST_BATCH_SIZE,
)
from src.core.logger import logger
from src.database import DatabaseManager
from src.models.device_info import DeviceInfo
from src.core.state_manager import state_manager
from src.network.tcp.persist_queue import DevicePersistQueue


class AsyncTCPServer:
    """异步TCP服务端，用于与Net Manager客户端建立长连接并处理设备数据

    主要功能：
    - 接收客户端连接并进行握手认证
    - 处理客户端发送的设备信息数据
    - 将设备数据保存到数据库
    - 通过WebSocket广播设备状态变化
    - 管理客户端连接生命周期
    """

    def __init__(self, db_manager=None, max_workers=10):
        """初始化异步TCP服务器

        Args:
            db_manager: 数据库管理器实例，用于数据存储
            max_workers: 线程池最大工作线程数（用于CPU密集型任务）
        """
        self.tcp_port = TCP_PORT  # TCP服务监听端口
        self.clients = set()  # 存储当前连接的客户端（reader, writer, address）元组集合
        self.client_id_map = {}  # 映射client_id到客户端地址
        self.client_device_map = {}  # 映射client_id到设备信息（包含id、alias、grouping和type字段）
        self._client_last_active = {}  # 客户端最后活跃时间
        
        # 细粒度锁，替代原来的单个clients_lock，减少锁竞争
        self.clients_lock = threading.RLock()  # 保护clients集合和client_id_map的锁
        self.device_map_lock = threading.RLock()  # 保护client_device_map的锁
        self.active_time_lock = threading.RLock()  # 保护_client_last_active的锁
        
        self.running = False  # 服务器运行状态标志
        self.server = None  # 异步服务器实例

        # 复用或创建数据库管理器实例
        self.db_manager = db_manager if db_manager else DatabaseManager()

        # 使用线程池处理CPU密集型任务
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.persist_queue = DevicePersistQueue(
            db_manager=self.db_manager,
            maxsize=DEVICE_PERSIST_QUEUE_MAXSIZE,
            flush_interval_ms=DEVICE_PERSIST_FLUSH_INTERVAL_MS,
            batch_size=DEVICE_PERSIST_BATCH_SIZE,
        )

    async def start(self):
        """启动异步TCP服务器"""
        logger.info(f"异步TCP服务端启动，监听端口 {self.tcp_port}")
        self.running = True

        # 启动持久化队列
        try:
            self.persist_queue.start()
        except Exception:
            logger.exception("无法启动持久化队列")

        # 加载设备缓存
        await self.load_device_cache()

        try:
            # 创建异步服务器
            self.server = await asyncio.start_server(
                self.handle_client,
                '0.0.0.0',
                self.tcp_port,
                backlog=1024
            )

            # 启动服务器
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError:
            logger.info("异步TCP服务端被取消")
        except Exception as e:
            logger.exception(f"异步TCP服务端运行出错: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """停止异步TCP服务器"""
        if not self.running:
            return

        logger.info("异步TCP服务端正在停止...")
        self.running = False

        # 关闭服务器
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # 清理客户端连接
        with self.clients_lock:
            for reader, writer, address in list(self.clients):
                try:
                    writer.close()
                    await writer.wait_closed()
                except Exception as e:
                    logger.warning(f"关闭客户端 {address} 连接时出错: {e}")
            self.clients.clear()
            self.client_id_map.clear()
        
        # 清理客户端活跃时间记录
        with self.active_time_lock:
            self._client_last_active.clear()
        
        # 清理设备映射缓存
        with self.device_map_lock:
            self.client_device_map.clear()

        # 关闭线程池
        self.executor.shutdown(wait=True)

        # 停止持久化队列
        try:
            self.persist_queue.stop()
        except Exception:
            logger.exception("无法停止持久化队列")

        logger.info("异步TCP服务端已停止")

    async def load_device_cache(self):
        """从数据库加载所有设备信息到缓存"""
        try:
            # 使用线程池执行阻塞的数据库操作
            devices = await asyncio.get_event_loop().run_in_executor(
                self.executor,
                self.db_manager.device_manager.get_all_device_info
            )
            if devices:
                with self.device_map_lock:
                    for device in devices:
                        client_id = device.get('client_id')
                        if client_id:
                            self.client_device_map[client_id] = {
                                'id': device.get('id'),
                                'alias': device.get('alias', ''),
                                'grouping': device.get('grouping', ''),
                                'type': device.get('type', '')
                            }
                logger.info(f"设备缓存加载完成，共 {len(devices)} 个设备")
        except Exception as e:
            logger.exception(f"加载设备缓存时出错: {e}")

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理单个客户端连接的完整生命周期

        Args:
            reader: 异步流读取器
            writer: 异步流写入器
        """
        address = writer.get_extra_info('peername')
        logger.debug(f"客户端 {address} 已连接")

        # 检查最大客户端连接数
        with self.clients_lock:
            current_clients = len(self.clients)
        if current_clients >= TCP_MAX_CLIENTS:
            logger.warning(f"客户端连接数已达上限 {TCP_MAX_CLIENTS}，拒绝连接: {address}")
            writer.close()
            await writer.wait_closed()
            return

        # 将客户端添加到连接集合
        with self.clients_lock:
            self.clients.add((reader, writer, address))
        with self.active_time_lock:
            self._client_last_active[(reader, writer)] = time.time()

        client_id = None
        try:
            # 1. 接收客户端握手消息（带4字节长度前缀）
            # 接收4字节长度前缀
            raw_length = await asyncio.wait_for(
                reader.read(4),
                timeout=TCP_RECV_TIMEOUT
            )
            if not raw_length:
                logger.warning(f"客户端 {address} 握手超时")
                return

            # 解析消息长度（大端序）
            message_length = struct.unpack("!I", raw_length)[0]

            # 检查消息长度是否超限
            if message_length > TCP_MAX_MESSAGE_SIZE:
                logger.warning(
                    f"客户端 {address} 握手消息长度超限: {message_length}"
                )
                return

            # 接收完整的握手数据
            handshake_data = await asyncio.wait_for(
                reader.read(message_length),
                timeout=TCP_RECV_TIMEOUT
            )
            if not handshake_data:
                logger.warning(f"客户端 {address} 握手数据接收超时")
                return

            # 解析握手JSON数据
            handshake_info = json.loads(handshake_data.decode("utf-8"))

            if handshake_info.get("type") == "handshake":
                # 握手成功，获取client_id
                client_id = handshake_info.get("client_id", "unknown")
                logger.info(
                    f"客户端 {address} 握手成功，client_id: {client_id}"
                )

                # 存储client_id与客户端地址的映射
                with self.clients_lock:
                    self.client_id_map[client_id] = address
                with self.active_time_lock:
                    self._client_last_active[(reader, writer)] = time.time()

                # 广播设备在线状态
                try:
                    state_manager.broadcast_message(
                        {
                            "type": "deviceStatus",
                            "data": {
                                "client_id": client_id,
                                "status": "online",
                            },
                        }
                    )
                except Exception:
                    logger.debug(f"无法广播客户端 {client_id} 在线状态")
            else:
                logger.warning(f"客户端 {address} 发送的不是握手消息")
                return

            # 2. 持续接收客户端数据
            while self.running:
                # 接收消息长度前缀
                try:
                    raw_length = await asyncio.wait_for(
                        reader.read(4),
                        timeout=TCP_RECV_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    # 接收超时，更新活跃时间后继续
                    with self.active_time_lock:
                        self._client_last_active[(reader, writer)] = time.time()
                    continue

                if not raw_length:
                    break  # 连接关闭

                # 解析消息长度
                message_length = struct.unpack("!I", raw_length)[0]
                if message_length > TCP_MAX_MESSAGE_SIZE:
                    logger.warning(f"客户端 {address} 消息长度超限: {message_length}")
                    break

                # 接收完整消息数据
                try:
                    data = await asyncio.wait_for(
                        reader.read(message_length),
                        timeout=TCP_RECV_TIMEOUT
                    )
                except asyncio.TimeoutError:
                    # 接收超时，更新活跃时间后继续
                    with self.active_time_lock:
                        self._client_last_active[(reader, writer)] = time.time()
                    continue

                if not data:
                    break  # 连接关闭

                # 更新客户端最后活跃时间
                with self.active_time_lock:
                    self._client_last_active[(reader, writer)] = time.time()

                # 3. 异步处理客户端数据，避免阻塞事件循环
                asyncio.create_task(
                    self._process_client_data(data, address, client_id)
                )

        except ConnectionResetError:
            logger.info(f"客户端 {address} 断开连接")
        except asyncio.CancelledError:
            logger.debug(f"客户端 {address} 处理被取消")
        except Exception as e:
            logger.exception(f"处理客户端 {address} 数据时出错: {e}")
        finally:
            # 4. 连接关闭清理
            # 广播设备离线状态
            try:
                if client_id:
                    state_manager.broadcast_message(
                        {
                            "type": "deviceStatus",
                            "data": {"client_id": client_id, "status": "offline"},
                        }
                    )
            except Exception:
                logger.debug(f"无法广播客户端 {client_id} 离线状态")

            # 清理客户端连接资源
            await self._cleanup_client_connection(reader, writer, address, client_id)

    async def _process_client_data(self, data, address, client_id=None):
        """异步处理来自客户端的设备数据"""
        if not data:
            logger.debug(f"收到来自 {address} 的空数据包，忽略")
            return

        logger.debug(f"收到来自 {address} 的数据，长度: {len(data)} 字节")

        json_str = None
        try:
            # 1. 解码并清理数据
            json_str = data.decode("utf-8").strip()

            if not json_str:
                logger.warning(f"收到来自 {address} 的空JSON字符串，忽略")
                return

            # 2. 解析JSON数据
            info = json.loads(json_str)

            # 3. 处理设备ID
            client_id = info.get("client_id")
            if client_id:
                # 尝试从缓存获取设备信息
                cached_device = None
                with self.device_map_lock:
                    cached_device = self.client_device_map.get(client_id)

                if cached_device:
                    # 使用缓存的设备ID
                    info["id"] = cached_device['id']
                else:
                    # 尝试从数据库获取现有设备
                    existing_device = None
                    try:
                        existing_device = await asyncio.get_event_loop().run_in_executor(
                            self.executor,
                            self.db_manager.device_manager.get_device_info_by_client_id,
                            client_id
                        )
                    except Exception:
                        logger.exception(f"无法从数据库获取设备信息: {client_id}")
                        existing_device = None

                    if existing_device:
                        # 使用现有设备ID
                        info["id"] = existing_device["id"]
                        # 更新缓存
                        with self.device_map_lock:
                            self.client_device_map[client_id] = {
                                'id': existing_device["id"],
                                'alias': existing_device.get('alias', ''),
                                'grouping': existing_device.get('grouping', ''),
                                'type': existing_device.get('type', '')
                            }
                    else:
                        # 创建新设备ID和默认类型
                        info["id"] = str(uuid.uuid4())
                        info["type"] = "台式机"  # 默认设备类型
                        # 更新缓存
                        with self.device_map_lock:
                            self.client_device_map[client_id] = {
                                'id': info["id"],
                                'alias': '',
                                'grouping': '',
                                'type': info["type"]
                            }
            else:
                # 缺少client_id，忽略数据
                logger.warning(
                    f"收到来自 {address} 的信息，设备信息缺少 client_id，忽略"
                )
                return

            # 4. 创建设备信息对象
            device_info = self._create_device_info_with_id(info)
            
            # 5. 将设备信息放入持久化队列
            try:
                self.persist_queue.enqueue(device_info)
            except Exception:
                logger.exception(f"无法将设备信息放入持久化队列: {client_id}")

            # 6. 确保设备ID映射正确
            try:
                with self.device_map_lock:
                    # 更新缓存的设备ID
                    if client_id in self.client_device_map:
                        self.client_device_map[client_id]['id'] = device_info.id
                    else:
                        self.client_device_map[client_id] = {
                            'id': device_info.id,
                            'alias': '',
                            'grouping': '',
                            'type': ''
                        }
            except Exception:
                logger.exception(f"无法更新设备缓存: {client_id}")

            # 7. 广播设备信息
            try:
                with self.device_map_lock:
                    device_info.alias = self.client_device_map[client_id]['alias']
                    device_info.grouping = self.client_device_map[client_id]['grouping']
                    device_info.type = self.client_device_map[client_id]['type']
                state_manager.broadcast_message(
                    {"type": "deviceInfo", "data": device_info.to_dict()}
                )
            except Exception:
                logger.debug(f"无法广播设备信息: {client_id}")

            logger.debug(f"设备 {client_id} 的信息已处理完成")

        except json.JSONDecodeError as e:
            # 记录JSON解析错误详情
            error_msg = f"无法解析的JSON数据: {e}"
            if json_str:
                # 记录数据预览（前200字符）
                data_preview = json_str[:200] + ("..." if len(json_str) > 200 else "")
                logger.warning(f"{error_msg}。数据预览: {data_preview}")
            else:
                logger.warning(f"{error_msg}。无法解码数据")
        except Exception as e:
            logger.exception(f"处理客户端 {address} 数据时出错: {e}")

    async def _cleanup_client_connection(self, reader, writer, address, client_id=None):
        """清理客户端连接资源"""
        # 移除客户端连接记录和client_id映射
        with self.clients_lock:
            self.clients.discard((reader, writer, address))
            # 移除client_id映射
            if client_id and client_id in self.client_id_map:
                del self.client_id_map[client_id]
        # 移除客户端活跃时间记录
        with self.active_time_lock:
            self._client_last_active.pop((reader, writer), None)

        # 关闭连接
        try:
            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logger.warning(f"关闭客户端 {address} 套接字时出错: {e}")
        
        logger.info(f"客户端 {address} 连接已关闭")

    def _create_device_info_with_id(self, info):
        """创建带有指定ID的设备信息对象"""
        return DeviceInfo(
            id=info["id"],  # 使用指定的设备ID
            client_id=info.get("client_id", ""),  # 客户端标识符
            hostname=info.get("hostname", "N/A"),  # 主机名
            os_name=info.get("os_name", "N/A"),  # 操作系统名称
            os_version=info.get("os_version", "N/A"),  # 操作系统版本
            os_architecture=info.get("os_architecture", "N/A"),  # 操作系统架构
            machine_type=info.get("machine_type", "N/A"),  # 机器类型
            services=info.get("services", "[]"),  # 服务信息（JSON字符串）
            processes=info.get("processes", "[]"),  # 进程信息（JSON字符串）
            networks=info.get("networks", "[]"),  # 网络信息（JSON字符串）
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 当前时间戳
            cpu_info=info.get("cpu_info", ""),  # CPU信息
            memory_info=info.get("memory_info", ""),  # 内存信息
            disk_info=info.get("disk_info", ""),  # 磁盘信息
            type="",  # 显式设置type为空，避免通过TCP更新设备类型
            alias="",  # 设备别名
            grouping="",  # 设备分组
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 创建时间
        )

    def get_client_address(self, client_id):
        """根据client_id获取客户端地址"""
        # 注意：这个方法是同步的，使用线程锁保护访问
        with self.clients_lock:
            return self.client_id_map.get(client_id)

    def get_online_devices_count(self):
        """获取在线设备数量"""
        # 注意：这个方法是同步的，使用线程锁保护访问
        with self.clients_lock:
            return len(self.client_id_map)
