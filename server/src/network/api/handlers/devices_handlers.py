#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备管理处理器
"""

import json
import tornado.escape
import sqlite3
from src.network.api.handlers.base_handler import BaseHandler


class DeviceCreateHandler(BaseHandler):
    """设备创建处理器 - 新增设备"""

    def initialize(self, db_manager):
        self.db_manager = db_manager

    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            required_fields = ["id", "hostname"]
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write(
                        {"status": "error", "message": f"缺少必需的字段: {field}"}
                    )
                    return

            # 创建设备
            success, message = self.db_manager.device_manager.create_device(data)

            if success:
                self.write({"status": "success", "message": message})
            else:
                self.set_status(400)
                self.write({"status": "error", "message": message})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class DeviceUpdateHandler(BaseHandler):
    """设备更新处理器 - 修改设备"""

    def initialize(self, db_manager):
        self.db_manager = db_manager

    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            required_fields = ["id"]
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write(
                        {"status": "error", "message": f"缺少必需的字段: {field}"}
                    )
                    return

            # alias字段可以在UpdateHandler中修改
            # 其他字段正常处理

            # 更新设备
            success, message = self.db_manager.device_manager.update_device(data)

            if success:
                self.write({"status": "success", "message": message})
            else:
                self.set_status(400)
                self.write({"status": "error", "message": message})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class DeviceDeleteHandler(BaseHandler):
    """设备删除处理器 - 删除设备"""

    def initialize(self, db_manager):
        self.db_manager = db_manager

    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)

            # 检查必需字段
            device_id = data.get("id")
            if not device_id:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: id"})
                return

            # 删除设备
            success, message = self.db_manager.device_manager.delete_device(device_id)

            if success:
                self.write({"status": "success", "message": message})
            else:
                self.set_status(400)
                self.write({"status": "error", "message": message})
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class DeviceHandler(BaseHandler):
    """单个系统信息处理器 - 根据设备ID获取系统信息"""

    def initialize(self, db_manager, get_tcp_server_func=None):
        self.db_manager = db_manager
        self.get_tcp_server_func = get_tcp_server_func

    def get_online_status(self, device_id):
        """根据client_id判断客户端是否在线"""
        # 首先通过设备ID获取client_id
        try:
            conn = sqlite3.connect(self.db_manager.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT client_id FROM devices_info WHERE id = ? ORDER BY timestamp DESC LIMIT 1
            """,
                (device_id,),
            )
            row = cursor.fetchone()
            conn.close()

            if not row or not row[0]:
                return False

            client_id = row[0]
        except Exception:
            return False

        # 然后通过TCP服务器检查client_id是否在线
        if not self.get_tcp_server_func:
            return False

        tcp_server = self.get_tcp_server_func()
        if not tcp_server:
            return False

        # 检查client_id是否在在线客户端映射中
        with tcp_server.clients_lock:
            return client_id in tcp_server.client_id_map

    def get(self, device_id):
        try:
            device = self.db_manager.device_manager.get_device_info_by_id(device_id)
            if device:
                # 添加在线状态字段
                device["online"] = self.get_online_status(device_id)
                self.write({"status": "success", "data": device})
            else:
                self.set_status(404)
                self.write(
                    {"status": "error", "message": f"未找到ID为 {device_id} 的系统信息"}
                )
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class DeviceTypeHandler(BaseHandler):
    """系统类型处理器 - 设置设备类型"""

    def initialize(self, db_manager):
        self.db_manager = db_manager

    def put(self, device_id):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            device_type = data.get("type")

            # 检查type字段是否存在
            if device_type is None:
                self.set_status(400)
                self.write({"status": "error", "message": "缺少必需的字段: type"})
                return

            # 更新数据库中的设备类型
            success = self.db_manager.device_manager.update_device_type(
                device_id, device_type
            )

            if success:
                self.write({"status": "success", "message": "设备类型更新成功"})
            else:
                self.set_status(404)
                self.write(
                    {"status": "error", "message": f"未找到ID为 {device_id} 的系统信息"}
                )
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "无效的JSON格式"})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})


class DevicesHandler(BaseHandler):
    """系统信息处理器 - 获取所有系统信息"""

    def initialize(self, db_manager, get_tcp_server_func=None):
        self.db_manager = db_manager
        self.get_tcp_server_func = get_tcp_server_func

    def get_online_status(self, client_id):
        """根据client_id判断客户端是否在线"""
        # 通过TCP服务器检查client_id是否在线
        if not self.get_tcp_server_func:
            return False

        tcp_server = self.get_tcp_server_func()
        if not tcp_server:
            return False

        # 检查client_id是否在在线客户端映射中
        with tcp_server.clients_lock:
            return client_id in tcp_server.client_id_map

    def get(self):
        try:
            devices = self.db_manager.device_manager.get_all_device_info()

            # 处理返回数据：只返回services和processes的数量，并添加在线状态和操作系统信息
            processed_devices = []
            for device in devices:
                networks = device["networks"] if device["networks"] else []

                # 提取所有网络接口的IP地址
                ips = []
                for network in networks:
                    if isinstance(network, dict) and "ip_address" in network:
                        ip = network["ip_address"]
                        if ip:  # 只添加非空的IP地址
                            ips.append(f"{network['name']}: {ip}")

                processed_device = {
                    "id": device["id"],
                    "alias": device["alias"],
                    "hostname": device["hostname"],
                    "services_count": len(device["services"]),
                    "processes_count": len(device["processes"]),
                    "networks_count": len(networks),
                    "ips": ips,  # 添加IP地址列表字段
                    "cpu_info": device["cpu_info"],
                    "memory_info": device["memory_info"],
                    "disk_info": device["disk_info"],
                    "online": self.get_online_status(device["client_id"]),
                    "os_name": device["os_name"],
                    "os_version": device["os_version"],
                    "os_architecture": device["os_architecture"],
                    "machine_type": device["machine_type"],
                    "type": device["type"],
                    "client_id": device["client_id"],
                    "timestamp": device["timestamp"],
                    "created_at": device["created_at"],
                }
                processed_devices.append(processed_device)

            self.write(
                {
                    "status": "success",
                    "data": processed_devices,
                    "count": len(processed_devices),
                }
            )
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": f"内部服务器错误: {str(e)}"})
