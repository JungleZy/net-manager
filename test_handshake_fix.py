#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试握手消息修复
验证服务端能否正确处理带长度前缀的握手消息
"""

import socket
import json
import struct
import threading
import time
from datetime import datetime


def send_handshake_message(client_socket, client_id):
    """发送带长度前缀的握手消息"""
    # 构造握手消息
    handshake_message = {
        "type": "handshake",
        "client_id": client_id,
        "timestamp": datetime.now().isoformat(),
    }

    # 序列化消息
    message_bytes = json.dumps(handshake_message, ensure_ascii=False).encode("utf-8")

    # 添加长度前缀
    length_prefix = struct.pack("!I", len(message_bytes))  # 网络字节序

    # 发送消息
    client_socket.sendall(length_prefix + message_bytes)
    print(f"已发送握手消息: {handshake_message}")


def test_handshake():
    """测试握手消息处理"""
    # 创建服务端socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("127.0.0.1", 12345))
    server_socket.listen(1)

    print("服务端启动，监听端口 12345")

    def server_thread():
        """服务端线程"""
        try:
            client_socket, address = server_socket.accept()
            print(f"客户端 {address} 已连接")

            # 接收数据长度（4字节）
            raw_length = b""
            while len(raw_length) < 4:
                packet = client_socket.recv(4 - len(raw_length))
                if not packet:
                    return
                raw_length += packet

            # 解析数据长度
            message_length = struct.unpack("!I", raw_length)[0]
            print(f"接收到消息长度: {message_length}")

            # 接收指定长度的数据
            data = b""
            while len(data) < message_length:
                packet = client_socket.recv(message_length - len(data))
                if not packet:
                    return
                data += packet

            # 解析握手消息
            handshake_info = json.loads(data.decode("utf-8"))
            print(f"接收到握手消息: {handshake_info}")

            if handshake_info.get("type") == "handshake":
                client_id = handshake_info.get("client_id", "unknown")
                print(f"握手成功，client_id: {client_id}")

                # 发送确认消息
                response = {"status": "ok", "message": "握手成功"}
                response_bytes = json.dumps(response, ensure_ascii=False).encode(
                    "utf-8"
                )
                client_socket.sendall(response_bytes)
            else:
                print("不是握手消息")

            client_socket.close()
        except Exception as e:
            print(f"服务端处理出错: {e}")
        finally:
            server_socket.close()

    # 启动服务端线程
    server_t = threading.Thread(target=server_thread)
    server_t.start()

    # 等待服务端启动
    time.sleep(1)

    # 创建客户端socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 12345))

    # 发送握手消息
    send_handshake_message(client_socket, "test-client-123")

    # 接收服务端响应
    try:
        response_data = client_socket.recv(1024)
        if response_data:
            response = json.loads(response_data.decode("utf-8"))
            print(f"服务端响应: {response}")
    except Exception as e:
        print(f"接收服务端响应出错: {e}")

    client_socket.close()
    server_t.join()

    print("测试完成")


if __name__ == "__main__":
    test_handshake()
