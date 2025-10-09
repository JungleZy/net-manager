#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统类型处理器
"""

import json
import tornado.escape
from .base_handler import BaseHandler


class SystemTypeHandler(BaseHandler):
    """系统类型处理器 - 设置设备类型"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def put(self, mac_address):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            device_type = data.get('type')
            
            # 检查type字段是否存在
            if device_type is None:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": "缺少必需的字段: type"
                })
                return
            
            # 更新数据库中的设备类型
            success = self.db_manager.update_system_type(mac_address, device_type)
            
            if success:
                self.write({
                    "status": "success",
                    "message": "设备类型更新成功"
                })
            else:
                self.set_status(404)
                self.write({
                    "status": "error",
                    "message": f"未找到MAC地址为 {mac_address} 的系统信息"
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