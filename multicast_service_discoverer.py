import socket
import struct
import time
import threading
from datetime import datetime


class MulticastServiceDiscoverer:
    def __init__(self, multicast_group="239.255.1.1", port=37020, timeout=10):
        self.multicast_group = multicast_group
        self.port = port
        self.timeout = timeout
        self.discovered_services = {}
        self.discovery_id = 0
        self.is_discovering = False

    def discover_services(self, service_type="ANY"):
        print(f"\n🔍 开始发现服务...")
        print(f"   目标类型: {service_type}")

        self.discovered_services.clear()
        self.is_discovering = True
        self.discovery_id += 1
        current_id = self.discovery_id

        # 启动监听线程
        listener_thread = threading.Thread(
            target=self._listen_for_responses, args=(current_id,)
        )
        listener_thread.daemon = True
        listener_thread.start()

        time.sleep(0.5)  # 给监听线程启动时间

        # 发送发现查询
        self._send_discovery_query(service_type, current_id)

        # 等待发现完成
        start_time = time.time()
        while time.time() - start_time < self.timeout and self.is_discovering:
            time.sleep(0.1)

        self.is_discovering = False
        time.sleep(0.5)

        services = list(self.discovered_services.values())

        print(f"\n📊 发现结果:")
        print(f"   找到服务数量: {len(services)}")
        for service in services:
            print(f"   ✅ {service['name']} ({service['type']}) @ {service['address']}")

        return services

    def _send_discovery_query(self, service_type, discovery_id):
        try:
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ttl = struct.pack("b", 32)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
            send_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

            query_msg = f"DISCOVER|{service_type}|{discovery_id}"
            send_socket.sendto(query_msg.encode(), (self.multicast_group, self.port))
            print(f"📤 发送查询: {query_msg}")

            send_socket.close()
            return True
        except Exception as e:
            print(f"❌ 发送查询失败: {e}")
            return False

    def _listen_for_responses(self, discovery_id):
        listen_socket = None
        try:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.bind(("", self.port))

            group = socket.inet_aton(self.multicast_group)
            mreq = struct.pack("4sL", group, socket.INADDR_ANY)
            listen_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            listen_socket.settimeout(1.0)
            print("👂 开始监听响应...")

            start_time = time.time()
            response_count = 0

            while self.is_discovering and (time.time() - start_time < self.timeout):
                try:
                    data, addr = listen_socket.recvfrom(1024)
                    response_count += 1

                    # 显示原始消息内容
                    raw_message = data.decode("utf-8", errors="replace")
                    print(
                        f"📥 收到原始响应 #{response_count} 来自 {addr}: {raw_message}"
                    )

                    # 尝试解析响应
                    if self._handle_service_response(data, addr, discovery_id):
                        print(f"   ✅ 成功解析为服务信息")
                    else:
                        print(f"   ❌ 无法解析为有效服务信息")

                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"❌ 接收响应错误: {e}")
                    break

            print(f"📨 总共收到 {response_count} 个响应")

        except Exception as e:
            print(f"❌ 监听线程错误: {e}")
        finally:
            if listen_socket:
                listen_socket.close()

    def _handle_service_response(self, data, service_addr, discovery_id):
        try:
            response = data.decode("utf-8")
            print(f"   正在解析响应: {response}")

            parts = response.split("|")
            print(f"   消息分割为 {len(parts)} 部分: {parts}")

            # 检查消息格式
            if len(parts) >= 4 and parts[0] == "RESPONSE":
                service_type = parts[1]
                service_name = parts[2]
                service_ip = parts[3]

                service_info = {
                    "name": service_name,
                    "type": service_type,
                    "address": f"{service_ip}:{service_addr[1]}",
                    "discovery_time": datetime.now().isoformat(),
                }

                service_key = f"{service_ip}:{service_addr[1]}"
                self.discovered_services[service_key] = service_info
                return True
            else:
                print(
                    f"   消息格式不匹配: 期望 'RESPONSE|type|name|ip'，实际收到 {parts[0] if parts else '空消息'}"
                )
                return False

        except Exception as e:
            print(f"❌ 处理响应失败: {e}")
            return False


def main():
    print("=" * 50)
    print("多播服务发现客户端")
    print("=" * 50)

    discoverer = MulticastServiceDiscoverer(
        multicast_group="239.255.1.1", port=37020, timeout=10
    )

    try:
        while True:
            print("\n" + "-" * 30)
            service_type = input(
                "请输入要发现的服务类型 (输入 'ANY' 发现所有服务, 输入 'quit' 退出): "
            ).strip()

            if service_type.lower() == "quit":
                break

            if not service_type:
                service_type = "ANY"

            services = discoverer.discover_services(service_type)

            if not services:
                print("\n❌ 未发现任何服务")

            continue_choice = input("\n是否继续发现? (y/n): ").strip().lower()
            if continue_choice != "y":
                break

    except KeyboardInterrupt:
        print("\n👋 客户端已退出")
    except Exception as e:
        print(f"\n❌ 客户端运行错误: {e}")


if __name__ == "__main__":
    main()
