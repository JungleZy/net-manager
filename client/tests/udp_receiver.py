import socket
import json
from client.src.config import UDP_PORT

def udp_receiver():
    """UDP接收器，用于测试数据接收"""
    # 创建UDP套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 绑定端口
    server_address = ('localhost', UDP_PORT)
    print(f"UDP接收器启动，监听端口 {UDP_PORT}...")
    sock.bind(server_address)
    
    try:
        while True:
            # 接收数据
            data, address = sock.recvfrom(4096)
            print(f"收到来自 {address} 的数据:")
            
            try:
                # 解析JSON数据
                info = json.loads(data.decode('utf-8'))
                print(f"  主机名: {info.get('hostname', 'N/A')}")
                print(f"  IP地址: {info.get('ip_address', 'N/A')}")
                print(f"  MAC地址: {info.get('mac_address', 'N/A')}")
                print(f"  时间戳: {info.get('timestamp', 'N/A')}")
                print(f"  服务数量: {len(json.loads(info.get('services', '[]')))}")
                print("-" * 40)
            except json.JSONDecodeError:
                print(f"  无法解析的数据: {data.decode('utf-8')}")
                
    except KeyboardInterrupt:
        print("\nUDP接收器已停止")
    finally:
        sock.close()

if __name__ == "__main__":
    udp_receiver()