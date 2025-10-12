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
from src.core.state_manager import state_manager
import asyncio
import threading
from tornado.platform.asyncio import AnyThreadEventLoopPolicy

class SNMPScanHandler(BaseHandler):
    """SNMP扫描处理器 - 扫描网络中的SNMP设备"""
    
    def initialize(self, db_manager):
        self.db_manager = db_manager
        self.snmp_manager = SNMPManager()
    
    def post(self):
        try:
            if state_manager.scan_task_id is not None:
                self.set_status(400)
                self.write({
                    "status": "error",
                    "message": "当前有正在运行的扫描任务，请稍后重试"
                })
                self.finish()
                return
            # 解析请求体中的JSON数据
            data = tornado.escape.json_decode(self.request.body)
            
            # 获取扫描参数
            network = data.get('network', '192.168.1.0/24')
            version = data.get('version', 'v2c')
            
            # 创建扫描任务ID，用于跟踪扫描状态
            import uuid
            scan_task_id = str(uuid.uuid4())
            state_manager.scan_task_id = scan_task_id
            
            # 立即响应客户端，告知扫描已开始
            self.write({
                "status": "started",
                "task_id": scan_task_id,
                "message": "SNMP扫描已启动"
            })
            self.finish()
            
            # 在独立线程中运行扫描任务
            scan_thread = threading.Thread(
                target=self._run_scan_in_thread,
                args=(scan_task_id, network, version, data),
                daemon=True
            )
            scan_thread.start()
            
        except json.JSONDecodeError:
            state_manager.scan_task_id = None
            self.set_status(400)
            self.write({
                "status": "error",
                "message": "无效的JSON格式"
            })
        except Exception as e:
            state_manager.scan_task_id = None
            self.set_status(500)
            self.write({
                "status": "error",
                "message": f"内部服务器错误: {str(e)}"
            })
    
    def _run_scan_in_thread(self, task_id, network, version, data):
        """在独立线程中运行SNMP扫描"""
        try:
            # 通知开始扫描
            state_manager.broadcast_message({
                "type": "scanTask", 
                "data": {
                    "task_id": task_id,
                    "event": "scan_started",
                    "network": network,
                    "version": version 
                }
            })
            
            # 根据SNMP版本获取相应的认证参数并执行扫描
            snmp_devices = []
            if version in ['v1', 'v2c']:
                communities = data.get('communities', ['public'])
                # 在事件循环中运行异步扫描
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    snmp_devices = loop.run_until_complete(
                        self.snmp_manager.scan_network_devices(network, version, communities)
                    )
                finally:
                    loop.close()
            elif version == 'v3':
                # SNMPv3参数
                user = data.get('user')
                auth_key = data.get('auth_key')
                auth_protocol = data.get('auth_protocol', 'md5')
                priv_key = data.get('priv_key')
                priv_protocol = data.get('priv_protocol', 'des')
                
                # 在事件循环中运行异步扫描
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    snmp_devices = loop.run_until_complete(
                        self.snmp_manager.scan_network_devices(
                            network, version, user=user, auth_key=auth_key, 
                            auth_protocol=auth_protocol, priv_key=priv_key, 
                            priv_protocol=priv_protocol
                        )
                    )
                finally:
                    loop.close()
            else:
                # 广播错误信息
                state_manager.broadcast_message({
                    "type": "scanTask", 
                    "data": {
                        "task_id": None,
                        "event": "scan_error",
                        "message": f"不支持的SNMP版本: {version}"
                    }
                })
                return
            
            # 广播扫描结果
            print("广播扫描结果:", snmp_devices)
            # 重置扫描任务ID
            state_manager.scan_task_id = None
            
            state_manager.broadcast_message({
                "type": "scanTask", 
                "data": {
                    "task_id": None,
                    "event": "scan_completed",
                    "data": snmp_devices,
                    "count": len(snmp_devices)
                }
            })
            
        except Exception as e:
            # 重置扫描任务ID
            state_manager.scan_task_id = None
            # 广播错误信息
            state_manager.broadcast_message({
                "type": "scanTask", 
                "data": {
                    "task_id": None,
                    "event": "scan_error",
                    "message": f"扫描过程中发生错误: {str(e)}"
                }
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
