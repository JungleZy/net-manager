#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TCP服务端 - 用于与Net Manager客户端建立长连接并接收数据
"""

from math import log
import socket
import json
import threading
import time
import sys
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from src.core.config import (
    TCP_PORT,
    TCP_THREADPOOL_WORKERS,
    TCP_RECV_TIMEOUT,
    TCP_MAX_MESSAGE_SIZE,
    TCP_MAX_PENDING_TASKS,
    DEVICE_PERSIST_QUEUE_MAXSIZE,
    DEVICE_PERSIST_FLUSH_INTERVAL_MS,
    DEVICE_PERSIST_BATCH_SIZE,
    TCP_MAX_CLIENTS,
    TCP_ACCEPT_EMFILE_BACKOFF_MS,
    TCP_EMFILE_DROP_COUNT,
)
from src.core.logger import logger
from src.database import DatabaseManager
from src.models.device_info import DeviceInfo
from src.core.state_manager import state_manager
from src.network.tcp.persist_queue import DevicePersistQueue


# 添加项目根目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


class TCPServer:
    """TCP服务端，用于与Net Manager客户端建立长连接并处理设备数据

    主要功能：
    - 接收客户端连接并进行握手认证
    - 处理客户端发送的设备信息数据
    - 将设备数据保存到数据库
    - 通过WebSocket广播设备状态变化
    - 管理客户端连接生命周期
    """

    def __init__(self, db_manager=None, max_workers=TCP_THREADPOOL_WORKERS):
        """初始化TCP服务器

        Args:
            db_manager: 数据库管理器实例，用于数据存储
            max_workers: 线程池最大工作线程数
        """
        self.tcp_port = TCP_PORT  # TCP服务监听端口
        self.clients = set()  # 存储当前连接的客户端（socket, address）元组集合
        self.client_id_map = {}  # 映射client_id到客户端地址
        self.client_device_map = {}  # 映射client_id到设备信息（包含id、alias、type字段）
        self.clients_lock = threading.Lock()  # 保护客户端集合和映射的线程锁
        self.running = False  # 服务器运行状态标志
        self._client_last_active = {}

        # 复用或创建数据库管理器实例
        self.db_manager = db_manager if db_manager else DatabaseManager()

        # 使用线程池处理客户端连接，提高并发性能
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.persist_queue = DevicePersistQueue(
            db_manager=self.db_manager,
            maxsize=DEVICE_PERSIST_QUEUE_MAXSIZE,
            flush_interval_ms=DEVICE_PERSIST_FLUSH_INTERVAL_MS,
            batch_size=DEVICE_PERSIST_BATCH_SIZE,
        )

    def handle_client(self, client_socket, address):
        """处理单个客户端连接的完整生命周期

        包括：
        1. 客户端连接建立
        2. 握手认证
        3. 数据接收与处理
        4. 连接异常处理
        5. 连接关闭清理

        Args:
            client_socket: 客户端套接字对象
            address: 客户端地址元组 (ip, port)
        """
        logger.debug(f"客户端 {address} 已连接")

        # 将客户端添加到连接集合
        with self.clients_lock:
            self.clients.add((client_socket, address))

        client_id = None
        try:
            # 1. 接收客户端握手消息（带4字节长度前缀）
            import struct

            # 接收4字节长度前缀
            raw_length, timed_out = self._recv_all_status(client_socket, 4)
            if raw_length and not timed_out:
                # 解析消息长度（大端序）
                message_length = struct.unpack("!I", raw_length)[0]

                # 检查消息长度是否超限
                if message_length > TCP_MAX_MESSAGE_SIZE:
                    logger.warning(
                        f"客户端 {address} 握手消息长度超限: {message_length}"
                    )
                    return

                # 接收完整的握手数据
                handshake_data, data_timed_out = self._recv_all_status(
                    client_socket, message_length
                )

                if handshake_data and not data_timed_out:
                    try:
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
                    except json.JSONDecodeError:
                        logger.warning(f"客户端 {address} 发送的握手消息无法解析")

            # 2. 持续接收客户端数据
            while self.running:
                # 接收消息长度前缀
                raw_length, timed_out = self._recv_all_status(client_socket, 4)
                if timed_out:
                    time.sleep(0.05)  # 接收超时，短暂休眠后继续
                    continue
                if not raw_length:
                    break  # 连接关闭

                # 解析消息长度
                message_length = struct.unpack("!I", raw_length)[0]
                if message_length > TCP_MAX_MESSAGE_SIZE:
                    logger.warning(f"客户端 {address} 消息长度超限: {message_length}")
                    break

                # 接收完整消息数据
                data, data_timed_out = self._recv_all_status(
                    client_socket, message_length
                )
                if data_timed_out:
                    time.sleep(0.05)  # 接收超时，短暂休眠后继续
                    continue
                if not data:
                    break  # 连接关闭
                try:
                    with self.clients_lock:
                        self._client_last_active[client_socket] = time.time()
                except Exception:
                    pass

                # 3. 异步处理客户端数据，避免阻塞主线程
                try:
                    # 检查线程池队列长度，防止队列溢出
                    try:
                        qsize = getattr(self.executor, "_work_queue", None)
                        pending = qsize.qsize() if qsize is not None else 0
                    except Exception:
                        pending = 0

                    # 队列拥塞时丢弃数据
                    if pending > TCP_MAX_PENDING_TASKS:
                        logger.warning(f"服务器队列拥塞，丢弃来自 {address} 的数据")
                        continue

                    # 提交数据处理任务到线程池
                    self.executor.submit(
                        self._process_client_data, data, address, client_id
                    )
                except RuntimeError as e:
                    if "cannot schedule new futures after shutdown" in str(e):
                        logger.debug(f"服务器正在关闭，不再处理来自 {address} 的新数据")
                        break
                    else:
                        raise

        except ConnectionResetError:
            logger.info(f"客户端 {address} 断开连接")
        except Exception as e:
            logger.exception(f"处理客户端 {address} 数据时出错: {e}")
        finally:
            # 4. 连接关闭清理
            # 广播设备离线状态
            try:
                state_manager.broadcast_message(
                    {
                        "type": "deviceStatus",
                        "data": {"client_id": client_id, "status": "offline"},
                    }
                )
            except Exception:
                logger.debug(f"无法广播客户端 {client_id} 离线状态")

            # 清理客户端连接资源
            self._cleanup_client_connection(client_socket, address, client_id)

    def _process_client_data(self, data, address, client_id=None):
        """异步处理来自客户端的设备数据

        主要流程：
        1. 数据有效性检查
        2. JSON数据解析
        3. 设备ID管理（新建/复用）
        4. 创建设备信息对象
        5. 数据保存到数据库
        6. WebSocket广播设备信息

        Args:
            data: 原始二进制数据
            address: 客户端地址
            client_id: 客户端标识符
        """
        # 检查数据是否为空
        if not data:
            logger.debug(f"收到来自 {address} 的空数据包，忽略")
            return

        logger.debug(f"收到来自 {address} 的数据，长度: {len(data)} 字节")

        json_str = None  # 初始化JSON字符串变量，避免异常处理中未绑定
        try:
            # 1. 解码并清理数据
            json_str = data.decode("utf-8").strip()  # 去除首尾空白字符

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
                try:
                    cached_device = self.client_device_map.get(client_id)
                except Exception:
                    cached_device = None

                if cached_device:
                    # 使用缓存的设备ID
                    info["id"] = cached_device['id']
                else:
                    # 尝试从数据库获取现有设备
                    existing_device = None
                    try:
                        existing_device = (
                            self.db_manager.device_manager.get_device_info_by_client_id(
                                client_id
                            )
                        )
                    except Exception:
                        existing_device = None

                    if existing_device:
                        # 使用现有设备ID
                        info["id"] = existing_device["id"]
                        # 更新缓存
                        with self.clients_lock:
                            self.client_device_map[client_id] = {
                                'id': existing_device["id"],
                                'alias': existing_device.get('alias', ''),
                                'type': existing_device.get('type', '')
                            }
                    else:
                        # 创建新设备ID和默认类型
                        import uuid

                        info["id"] = str(uuid.uuid4())
                        info["type"] = "台式机"  # 默认设备类型
                        # 更新缓存
                        with self.clients_lock:
                            self.client_device_map[client_id] = {
                                'id': info["id"],
                                'alias': '',
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
            try:
                self.persist_queue.enqueue(device_info)
            except Exception:
                pass

            # 确保设备ID映射正确
            try:
                with self.clients_lock:
                    # 更新缓存的设备ID
                    if client_id in self.client_device_map:
                        self.client_device_map[client_id]['id'] = device_info.id
                    else:
                        self.client_device_map[client_id] = {
                            'id': device_info.id,
                            'alias': '',
                            'type': ''
                        }
            except Exception:
                pass
            device_info.alias = self.client_device_map[client_id]['alias']
            device_info.type = self.client_device_map[client_id]['type']
            state_manager.broadcast_message(
                {"type": "deviceInfo", "data": device_info.to_dict()}
            )

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

            # 记录原始数据的十六进制表示，便于调试编码问题
            hex_data = data.hex()[:200] + ("..." if len(data.hex()) > 200 else "")
            logger.debug(f"原始数据(十六进制): {hex_data}")
        except Exception as e:
            logger.exception(f"处理客户端 {address} 数据时出错: {e}")

    def _create_device_info(self, info):
        """创建新的设备信息对象（自动生成ID）

        Args:
            info: 设备信息字典

        Returns:
            DeviceInfo: 设备信息对象
        """
        import uuid

        return DeviceInfo(
            id=str(uuid.uuid4()),  # 生成新的唯一设备ID
            client_id=info.get("client_id", ""),  # 客户端标识符
            hostname=info.get("hostname", "N/A"),  # 主机名
            os_name=info.get("os_name", "N/A"),  # 操作系统名称
            os_version=info.get("os_version", "N/A"),  # 操作系统版本
            os_architecture=info.get("os_architecture", "N/A"),  # 操作系统架构
            machine_type=info.get("machine_type", "N/A"),  # 机器类型
            services=info.get("services", "[]"),  # 服务信息（JSON字符串）
            processes=info.get("processes", "[]"),  # 进程信息（JSON字符串）
            networks=info.get("networks", "[]"),  # 网络信息（JSON字符串）
            timestamp=info.get("timestamp", "N/A"),  # 时间戳
            cpu_info=info.get("cpu_info", ""),  # CPU信息
            memory_info=info.get("memory_info", ""),  # 内存信息
            disk_info=info.get("disk_info", ""),  # 磁盘信息
        )

    def _create_device_info_with_id(self, info):
        """创建带有指定ID的设备信息对象

        Args:
            info: 设备信息字典，必须包含id字段

        Returns:
            DeviceInfo: 设备信息对象
        """
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
            created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 创建时间
        )

    def _process_services_info(self, info):
        """处理设备服务信息

        Args:
            info: 包含服务信息的设备数据字典
        """
        services_data = info.get("services", "[]")
        try:
            # 兼容字符串和字典类型的服务数据
            if isinstance(services_data, str):
                services = json.loads(services_data)
            else:
                services = services_data
            logger.debug(f"  服务数量: {len(services)}")

        except json.JSONDecodeError:
            logger.warning(f"  服务信息无法解析: {services_data}")

    def _process_processes_info(self, info):
        """处理设备进程信息

        Args:
            info: 包含进程信息的设备数据字典
        """
        processes_data = info.get("processes", "[]")
        try:
            # 兼容字符串和字典类型的进程数据
            if isinstance(processes_data, str):
                processes = json.loads(processes_data)
            else:
                processes = processes_data
            logger.debug(f"  进程数量: {len(processes)}")

        except json.JSONDecodeError:
            logger.warning(f"  进程信息无法解析: {processes_data}")

    def load_device_cache(self):
        """从数据库加载所有设备信息到缓存
        
        缓存结构: self.client_device_map[client_id] = {
            'id': 设备ID,
            'alias': 设备别名,
            'type': 设备类型
        }
        """
        try:
            # 获取所有设备信息
            devices = self.db_manager.device_manager.get_all_device_info()
            if devices:
                with self.clients_lock:
                    for device in devices:
                        client_id = device.get('client_id')
                        if client_id:
                            self.client_device_map[client_id] = {
                                'id': device.get('id'),
                                'alias': device.get('alias', ''),
                                'type': device.get('type', '')
                            }
                logger.info(f"设备缓存加载完成，共 {len(devices)} 个设备")
        except Exception as e:
            logger.exception(f"加载设备缓存时出错: {e}")

    def get_client_address(self, client_id):
        """根据client_id获取客户端地址

        Args:
            client_id: 客户端标识符

        Returns:
            tuple: 客户端地址 (ip, port) 或 None
        """
        with self.clients_lock:
            return self.client_id_map.get(client_id)

    def _cleanup_client_connection(self, client_socket, address, client_id=None):
        """清理客户端连接资源

        Args:
            client_socket: 客户端套接字
            address: 客户端地址
            client_id: 客户端标识符
        """
        # 移除客户端连接记录
        with self.clients_lock:
            self.clients.discard((client_socket, address))
            # 移除client_id映射
            if client_id and client_id in self.client_id_map:
                del self.client_id_map[client_id]
            # 注意：client_device_map缓存不应被清理，因为设备信息需要在客户端离线后依然保留
            self._client_last_active.pop(client_socket, None)

        # 关闭套接字
        client_socket.close()
        logger.info(f"客户端 {address} 连接已关闭")

    def _recv_all(self, sock, length):
        """确保接收指定长度的数据

        Args:
            sock: 套接字对象
            length: 需要接收的数据长度

        Returns:
            bytes: 完整的数据或None（超时/错误）
        """
        data = b""
        while len(data) < length:
            try:
                # 接收剩余长度的数据
                packet = sock.recv(length - len(data))
            except socket.timeout:
                logger.warning("接收数据超时")
                return None
            except OSError:
                return None

            # 连接关闭
            if not packet:
                return None

            data += packet
        return data

    def _recv_all_status(self, sock, length):
        """确保接收指定长度的数据，并返回超时状态

        Args:
            sock: 套接字对象
            length: 需要接收的数据长度

        Returns:
            tuple: (data, timed_out)
                data: 完整的数据或None
                timed_out: 布尔值，表示是否超时
        """
        data = b""
        while len(data) < length:
            try:
                packet = sock.recv(length - len(data))
            except socket.timeout:
                return None, True  # 超时，返回True
            except OSError:
                return None, False  # 其他错误，返回False

            if not packet:
                return None, False  # 连接关闭，返回False

            data += packet
        return data, False  # 成功接收，返回False

    def start(self):
        """启动TCP服务器

        主要流程：
        1. 创建并配置TCP套接字
        2. 绑定地址和端口
        3. 开始监听连接
        4. 接受客户端连接并提交到线程池处理
        5. 优雅处理关闭信号
        6. 清理资源
        """
        # 创建TCP套接字（IPv4, TCP）
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # 设置套接字选项
        server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
        )  # 允许地址重用
        server_socket.setsockopt(
            socket.IPPROTO_TCP, socket.TCP_NODELAY, 1
        )  # 禁用Nagle算法，减少延迟

        server_address = ("0.0.0.0", self.tcp_port)  # 监听所有网络接口
        logger.info(f"TCP服务端启动，监听端口 {self.tcp_port}")

        try:
            # 绑定地址和端口
            server_socket.bind(server_address)

            # 设置监听队列大小，处理并发连接
            server_socket.listen(512)
            self.running = True
            try:
                self.persist_queue.start()
            except Exception:
                pass

            # 加载设备缓存
            self.load_device_cache()

            # 主循环，接受客户端连接
            while self.running:
                try:
                    # 设置accept超时，以便能够响应关闭信号
                    server_socket.settimeout(1.0)

                    # 接受客户端连接
                    client_socket, address = server_socket.accept()
                    client_socket.settimeout(TCP_RECV_TIMEOUT)  # 设置客户端套接字超时
                    with self.clients_lock:
                        current_clients = len(self.clients)
                    if current_clients >= TCP_MAX_CLIENTS:
                        try:
                            client_socket.close()
                        except:
                            pass
                        continue

                    # 将客户端连接提交到线程池处理
                    if self.running:
                        try:
                            self.executor.submit(
                                self.handle_client, client_socket, address
                            )
                        except RuntimeError as e:
                            if "cannot schedule new futures after shutdown" in str(e):
                                # 服务器正在关闭，不再接受新连接
                                logger.debug("服务器正在关闭，不再接受新连接")
                                client_socket.close()
                                break
                            else:
                                raise

                except socket.timeout:
                    # accept超时，继续循环检查running状态
                    continue
                except Exception as e:
                    if self.running:
                        try:
                            import errno as _errno

                            emfile = getattr(_errno, "EMFILE", 24)
                        except Exception:
                            emfile = 24
                        if (
                            isinstance(e, OSError)
                            and getattr(e, "errno", None) == emfile
                            or "Too many open files" in str(e)
                        ):
                            try:
                                self._handle_emfile()
                            except Exception:
                                pass
                            time.sleep(
                                max(0.001, TCP_ACCEPT_EMFILE_BACKOFF_MS / 1000.0)
                            )
                            continue
                        logger.exception(f"接受连接时出错: {e}")

        except KeyboardInterrupt:
            logger.info("TCP服务端正在停止...")
        except Exception as e:
            logger.exception(f"服务端运行出错: {e}")
        finally:
            # 清理资源
            self.running = False

            # 关闭所有客户端连接
            with self.clients_lock:
                for client_socket, address in self.clients:
                    try:
                        client_socket.close()
                    except Exception as e:
                        logger.warning(f"关闭客户端连接时出错: {e}")
                self.clients.clear()  # 清空客户端集合
                self.client_id_map.clear()  # 清空client_id映射

            # 关闭服务器套接字
            server_socket.close()

            # 关闭线程池
            self.executor.shutdown(wait=True)
            try:
                self.persist_queue.stop()
            except Exception:
                pass

            logger.info("TCP服务端已停止")

    def _handle_emfile(self):
        drops = TCP_EMFILE_DROP_COUNT
        to_close = []
        with self.clients_lock:
            if self._client_last_active:
                items = list(self._client_last_active.items())
                items.sort(key=lambda x: x[1])
                for sock, _ts in items[:drops]:
                    for s, addr in list(self.clients):
                        if s is sock:
                            to_close.append((s, addr))
                            break
            else:
                to_close = list(self.clients)[:drops]
        for s, addr in to_close:
            try:
                s.close()
            except:
                pass
            with self.clients_lock:
                self.clients.discard((s, addr))
        with self.clients_lock:
            for s, _ in to_close:
                self._client_last_active.pop(s, None)
