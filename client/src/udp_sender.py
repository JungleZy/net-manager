import socket
import json
from src.config import UDP_HOST, UDP_PORT
from src.logger import logger

class UDPSender:
    """UDP发送器"""
    
    def __init__(self):
        self.udp_host = UDP_HOST
        self.udp_port = UDP_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 启用广播模式
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        logger.info(f"UDP发送器初始化完成，使用广播模式发送数据到端口: {self.udp_port}")
    
    def send_system_info(self, system_info):
        """通过UDP广播发送系统信息"""
        try:
            # 将系统信息对象转换为字典
            info_dict = {
                "hostname": system_info.hostname,
                "ip_address": system_info.ip_address,
                "mac_address": system_info.mac_address,
                "services": system_info.services,  # 这已经是JSON格式的字符串
                "timestamp": system_info.timestamp
            }
            
            # 将字典转换为JSON字符串
            message = json.dumps(info_dict, ensure_ascii=False)
            
            # 通过广播发送数据
            self.socket.sendto(message.encode('utf-8'), (self.udp_host, self.udp_port))
            logger.info(f"数据已通过广播发送到端口 {self.udp_port}")
            return True
        except Exception as e:
            logger.error(f"发送数据失败: {e}")
            return False
    
    def close(self):
        """关闭UDP套接字"""
        try:
            self.socket.close()
            logger.info("UDP套接字已关闭")
        except Exception as e:
            logger.error(f"关闭UDP套接字时出错: {e}")