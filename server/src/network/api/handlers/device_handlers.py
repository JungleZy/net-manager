#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设备管理处理器
"""

import json
import tornado.escape
from .base_handler import BaseHandler

class DeviceCreateHandler(BaseHandler):
    """设备创建处理器 - 新增设备"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            required_fields = ['mac_address', 'hostname', 'ip_address']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write({
                        "status": "error",
                        "message": f"缺少必需的字段: {field}"
                    })
                    return
            
            # 创建设备
            success, message = self.db_manager.create_device(data)
            
            if success:
                self.write({
                    "status": "success",
                    "message": message
                })
            else:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": message
                })
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })


class DeviceUpdateHandler(BaseHandler):
    """设备更新处理器 - 修改设备"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            required_fields = ['mac_address', 'hostname', 'ip_address']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write({
                        "status": "error",
                        "message": f"缺少必需的字段: {field}"
                    })
                    return
            
            # 更新设备
            success, message = self.db_manager.update_device(data)
            
            if success:
                self.write({
                    "status": "success",
                    "message": message
                })
            else:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": message
                })
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })


class DeviceDeleteHandler(BaseHandler):
    """设备删除处理器 - 删除设备"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            mac_address = data.get('mac_address')
            if not mac_address:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": "缺少必需的字段: mac_address"
                })
                return
            
            # 删除设备
            success, message = self.db_manager.delete_device(mac_address)
            
            if success:
                self.write({
                    "status": "success",
                    "message": message
                })
            else:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": message
                })
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })