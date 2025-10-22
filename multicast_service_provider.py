import socket
import struct
import time
import threading
from datetime import datetime


class MulticastServiceProvider:
    def __init__(
        self,
        service_name,
        service_type,
        multicast_group="239.255.1.1",
        port=37020,
        ttl=32,
    ):
        self.service_name = service_name
        self.service_type = service_type
        self.multicast_group = multicast_group
        self.port = port
        self.ttl = ttl
        self.running = False

        # 获取本机IP
        self.local_ip = self._get_local_ip()
        print(f"🔧 本机IP地址: {self.local_ip}")

    def _get_local_ip(self):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start_providing(self):
        try:
            # 创建发送socket（用于发送响应）
            self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ttl_binary = struct.pack("b", self.ttl)
            self.send_socket.setsockopt(
                socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_binary
            )
            self.send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

            self.running = True
            print(f"🚀 服务启动: {self.service_name} ({self.service_type})")
            print(f"   多播组: {self.multicast_group}:{self.port}")
            print(f"   本机IP: {self.local_ip}")

            # 启动响应线程
            response_thread = threading.Thread(target=self._response_worker)
            response_thread.daemon = True
            response_thread.start()

            return True
        except Exception as e:
            print(f"❌ 启动服务失败: {e}")
            return False

    def _response_worker(self):
        listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.bind(("", self.port))

            group = socket.inet_aton(self.multicast_group)
            mreq = struct.pack("4sL", group, socket.INADDR_ANY)
            listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            listen_socket.settimeout(1.0)
            print("✅ 服务已就绪，等待查询...")

            while self.running:
                try:
                    data, addr = listen_socket.recvfrom(1024)
                    message = data.decode("utf-8")
                    print(f"📥 收到查询: {message} 来自 {addr}")

                    if data.startswith(b"DISCOVER"):
                        self._handle_discover_query(data, addr)

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ 接收数据错误: {e}")

        except Exception as e:
            print(f"❌ 监听线程错误: {e}")
        finally:
            listen_socket.close()

    def _handle_discover_query(self, data, client_addr):
        try:
            query = data.decode("utf-8")
            parts = query.split("|")

            if len(parts) >= 2:
                requested_type = parts[1]

                # 检查服务类型是否匹配
                if (
                    requested_type.upper() == "ANY"
                    or requested_type == self.service_type
                ):
                    # 关键修改：通过多播发送响应，而不是单播
                    response = f"RESPONSE|{self.service_type}|{self.service_name}|{self.local_ip}"

                    # 发送到多播组，所有客户端都能收到
                    self.send_socket.sendto(
                        response.encode(), (self.multicast_group, self.port)
                    )
                    print(f"📤 通过多播发送响应: {response}")

        except Exception as e:
            print(f"❌ 处理查询失败: {e}")

    def stop_providing(self):
        self.running = False
        if hasattr(self, "send_socket"):
            self.send_socket.close()
        print("🛑 服务已停止")


if __name__ == "__main__":
    provider = MulticastServiceProvider(
        service_name="测试服务",
        service_type="test_service",
        multicast_group="239.255.1.1",
        port=37020,
    )

    try:
        if provider.start_providing():
            print("按 Ctrl+C 停止服务")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n停止服务")
    finally:
        provider.stop_providing()
