#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SNMP扫描处理器
"""

import json
import tornado.escape
import tornado.web
from src.network.api.handlers.base_handler import BaseHandler
from src.snmp.manager import SNMPManager
import asyncio
from tornado.platform.asyncio import AnyThreadEventLoopPolicy

class SNMPScanHandler(BaseHandler):
    """SNMP扫描处理器 - 扫描网络中的SNMP设备"""
    
    def initialize(self, db_manager):
        self.db_manager = db_manager
        self.snmp_manager = SNMPManager()
    
    async def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 获取扫描参数
            network = data.get('network', '192.168.1.0/24')
            version = data.get('version', 'v2c')
            
            # 根据SNMP版本获取相应的认证参数
            if version in ['v1', 'v2c']:
                community = data.get('communities', ['public'])[0]
                print(community, network, version)
                # 调用扫描方法
                snmp_devices = await self.snmp_manager.scan_network_devices(network, version, community)
            elif version == 'v3':
                # SNMPv3参数
                user = data.get('user')
                auth_key = data.get('auth_key')
                auth_protocol = data.get('auth_protocol', 'md5')
                priv_key = data.get('priv_key')
                priv_protocol = data.get('priv_protocol', 'des')
                
                # 对于SNMPv3，传递完整的认证参数
                snmp_devices = await self.snmp_manager.scan_network_devices(
                    network, version, user=user, auth_key=auth_key, 
                    auth_protocol=auth_protocol, priv_key=priv_key, 
                    priv_protocol=priv_protocol
                )
            else:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": f"不支持的SNMP版本: {version}"
                })
                return
            
            self.write({
                "status": "success",
                "data": snmp_devices,
                "count": len(snmp_devices)
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

class SNMPScanHandlerSimple(BaseHandler):
    """SNMP扫描处理器 - 扫描网络中的SNMP设备"""
    
    def initialize(self, db_manager):
        self.db_manager = db_manager
        self.snmp_manager = SNMPManager()
    
    def post(self):
        try:
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 获取扫描参数
            network = data.get('network', '192.168.1.0/24')
            # 调用扫描方法
            snmp_devices = self.snmp_manager.scan_snmp_devices(network)
            
            
            self.write({
                "status": "success",
                "data": snmp_devices,
                "count": len(snmp_devices)
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
