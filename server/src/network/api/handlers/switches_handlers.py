#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
交换机管理处理器
"""

import json
import tornado.escape
from src.network.api.handlers.base_handler import BaseHandler
from src.models.switch_info import SwitchInfo


class SwitchCreateHandler(BaseHandler):
    """交换机创建处理器 - 新增交换机"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            required_fields = ['ip', 'snmp_version']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write({
                        "status": "error",
                        "message": f"缺少必需的字段: {field}"
                    })
                    return
            
            # 检查交换机是否已存在（基于IP地址和SNMP版本）
            ip = data['ip']
            snmp_version = data['snmp_version']
            if self.db_manager.switch_exists(ip, snmp_version):
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": f"具有相同IP地址({ip})和SNMP版本({snmp_version})的交换机已存在"
                })
                return
            
            # 创建SwitchInfo对象
            switch_info = SwitchInfo(
                ip=data['ip'],
                snmp_version=data['snmp_version'],
                community=data.get('community', ''),
                user=data.get('user', ''),
                auth_key=data.get('auth_key', ''),
                auth_protocol=data.get('auth_protocol', ''),
                priv_key=data.get('priv_key', ''),
                priv_protocol=data.get('priv_protocol', ''),
                description=data.get('description', ''),
                device_name=data.get('device_name', '')
            )
            
            # 添加交换机
            success, message = self.db_manager.add_switch(switch_info)
            
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


class SwitchUpdateHandler(BaseHandler):
    """交换机更新处理器 - 修改交换机"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            required_fields = ['id', 'ip', 'snmp_version']
            for field in required_fields:
                if field not in data or not data[field]:
                    self.set_status(400)
                    self.write({
                        "status": "error",
                        "message": f"缺少必需的字段: {field}"
                    })
                    return
            
            # 创建SwitchInfo对象
            switch_info = SwitchInfo(
                id=data['id'],
                ip=data['ip'],
                snmp_version=data['snmp_version'],
                community=data.get('community', ''),
                user=data.get('user', ''),
                auth_key=data.get('auth_key', ''),
                auth_protocol=data.get('auth_protocol', ''),
                priv_key=data.get('priv_key', ''),
                priv_protocol=data.get('priv_protocol', ''),
                description=data.get('description', ''),
                device_name=data.get('device_name', '')
            )
            
            # 更新交换机
            success, message = self.db_manager.update_switch(switch_info)
            
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


class SwitchDeleteHandler(BaseHandler):
    """交换机删除处理器 - 删除交换机"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 检查必需字段
            switch_id = data.get('id')
            if not switch_id:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": "缺少必需的字段: id"
                })
                return
            
            # 删除交换机
            success, message = self.db_manager.delete_switch(switch_id)
            
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


class SwitchHandler(BaseHandler):
    """单个交换机信息处理器 - 根据ID获取交换机信息"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def get(self, switch_id):
        try:
            switch = self.db_manager.get_switch_by_id(int(switch_id))
            if switch:
                self.write({
                    "status": "success",
                    "data": switch
                })
            else:
                self.set_status(404)
                self.write({
                    "status": "error",
                    "message": f"未找到ID为 {switch_id} 的交换机信息"
                })
        except ValueError:
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的交换机ID"
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })


class SwitchesHandler(BaseHandler):
    """交换机信息处理器 - 获取所有交换机信息"""
    def initialize(self, db_manager):
        self.db_manager = db_manager
    
    def get(self):
        try:
            switches = self.db_manager.get_all_switches()
            
            self.write({
                "status": "success",
                "data": switches,
                "count": len(switches)
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })