import socket
import json
import threading
import time
from typing import Optional, Tuple
from src.config import UDP_HOST, UDP_PORT, TCP_PORT
from src.logger import logger

class TCPClient:
    """TCP客户端，用于与服务端建立长连接"""
    
    def __init__(self):
        self.tcp_port = TCP_PORT
        self.server_address: Optional[Tuple[str, int]] = None
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        self.lock = threading.Lock()  # 用于保护共享状态的锁
        
    def discover_server(self):
        """通过UDP发现服务端"""
        try:
            # 创建UDP套接字用于服务发现
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.settimeout(5.0)  # 5秒超时
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # 发送服务发现请求
            discovery_request = {
                'type': 'discovery',
                'timestamp': __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            request_data = json.dumps(discovery_request).encode('utf-8')
            
            # 发送到配置的地址
            udp_socket.sendto(request_data, (UDP_HOST, UDP_PORT))
            logger.info(f"发送服务发现请求到 {UDP_HOST}:{UDP_PORT}")
            
            # 接收服务端响应
            response_data, server_address = udp_socket.recvfrom(1024)
            response = json.loads(response_data.decode('utf-8'))
            
            # 检查响应类型
            if response.get('type') == 'discovery_response':
                self.server_address = (server_address[0], response.get('tcp_port', self.tcp_port))
                logger.info(f"发现服务端: {self.server_address[0]}:{self.server_address[1]}")
                return True
            else:
                logger.warning("收到无效的服务发现响应")
                return False
                
        except socket.timeout:
            logger.warning("服务发现超时")
            return False
        except Exception as e:
            logger.error(f"服务发现失败: {e}")
            return False
        finally:
            if 'udp_socket' in locals():
                udp_socket.close()
    
    def connect_to_server(self):
        """连接到服务端"""
        if not self.server_address:
            logger.error("未发现服务端地址")
            return False
            
        with self.lock:
            try:
                # 如果已有连接，先关闭
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                
                # 创建TCP套接字
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(10.0)  # 10秒连接超时
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)  # 启用TCP keepalive
                
                # 连接到服务端
                self.socket.connect(self.server_address)
                self.connected = True
                self.running = True
                logger.info(f"已连接到服务端 {self.server_address[0]}:{self.server_address[1]}")
                
                # 启动接收线程
                receive_thread = threading.Thread(target=self._receive_data)
                receive_thread.daemon = True
                receive_thread.start()
                
                return True
                
            except Exception as e:
                logger.error(f"连接服务端失败: {e}")
                self.connected = False
                self.running = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                return False
    
    def _receive_data(self):
        """接收服务端数据的线程函数"""
        try:
            while self.running and self.connected:
                try:
                    # 接收数据
                    data = self.socket.recv(65536)  # 64KB缓冲区
                    if not data:
                        logger.info("服务端关闭连接")
                        break
                        
                    # 处理接收到的数据
                    self._handle_received_data(data)
                    
                except socket.timeout:
                    # 超时继续循环
                    continue
                except ConnectionResetError:
                    logger.warning("连接被服务端重置")
                    break
                except Exception as e:
                    if self.running:
                        logger.error(f"接收数据时出错: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"接收线程出错: {e}")
        finally:
            with self.lock:
                self.connected = False
                self.running = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
            logger.info("与服务端的连接已断开")
    
    def _handle_received_data(self, data):
        """处理接收到的数据"""
        try:
            # 这里可以处理服务端发送的指令或响应
            message = json.loads(data.decode('utf-8'))
            logger.info(f"收到服务端消息: {message}")
        except Exception as e:
            logger.error(f"处理接收到的数据时出错: {e}")
    
    def send_system_info(self, system_info):
        """通过TCP发送系统信息"""
        with self.lock:
            if not self.connected:
                logger.error("未连接到服务端")
                return False
                
            try:
                # 将系统信息对象转换为字典
                info_dict = {
                    "hostname": system_info.hostname,
                    "ip_address": system_info.ip_address,
                    "mac_address": system_info.mac_address,
                    "services": system_info.services,  # 这已经是JSON格式的字符串
                    "processes": system_info.processes,  # 这已经是JSON格式的字符串
                    "timestamp": system_info.timestamp
                }
                
                # 将字典转换为JSON字符串
                message = json.dumps(info_dict, ensure_ascii=False)
                
                # 通过TCP发送数据
                self.socket.sendall(message.encode('utf-8'))
                logger.info("数据已通过TCP发送到服务端")
                return True
            except Exception as e:
                logger.error(f"发送数据失败: {e}")
                self.connected = False
                if self.socket:
                    try:
                        self.socket.close()
                    except:
                        pass
                    self.socket = None
                return False
    
    def disconnect(self):
        """断开与服务端的连接"""
        with self.lock:
            self.running = False
            self.connected = False
            
            if self.socket:
                try:
                    self.socket.close()
                    logger.info("TCP套接字已关闭")
                except Exception as e:
                    logger.error(f"关闭TCP套接字时出错: {e}")
                finally:
                    self.socket = None
    
    def is_connected(self):
        """检查是否已连接到服务端"""
        return self.connected