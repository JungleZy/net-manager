#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
接口流量速率查询处理器
提供通过SNMP查询设备接口上传/下载速率的HTTP接口
"""

import tornado.web
from src.network.api.handlers.base_handler import BaseHandler
from src.snmp.manager import SNMPManager


class InterfaceTrafficHandler(BaseHandler):
    """接口速率查询处理器"""

    def initialize(self, db_manager):
        self.db_manager = db_manager
        self.snmp_manager = SNMPManager(db_manager=self.db_manager)

    async def get(self):
        """
        查询接口速率
        查询参数:
          - ip: 设备IP地址 (必填)
          - version: SNMP版本 (可选，默认 v2c)
          - 对于v1/v2c: community (可选，默认 public)
          - 对于v3: user, auth_key, auth_protocol, priv_key, priv_protocol, level
        返回: 列表，每项包含 index/description/in/out octets 以及 upload/download bps/readable
        """
        try:
            ip = self.get_argument("ip", None)
            version = self.get_argument("version", "v2c")
            if not ip:
                self.set_status(400)
                self.write({"code": 400, "message": "缺少必需参数: ip", "data": None})
                return

            kwargs = {}
            if version in ("v1", "v2c"):
                kwargs["community"] = self.get_argument("community", "public")
            elif version == "v3":
                # 兼容不同命名：username/user, authKey/auth_key, privKey/priv_key
                kwargs["user"] = self.get_argument("user", self.get_argument("username", None))
                kwargs["auth_key"] = self.get_argument("auth_key", self.get_argument("authKey", None))
                kwargs["auth_protocol"] = self.get_argument("auth_protocol", "md5")
                kwargs["priv_key"] = self.get_argument("priv_key", self.get_argument("privKey", None))
                kwargs["priv_protocol"] = self.get_argument("priv_protocol", "des")
                kwargs["level"] = self.get_argument("level", "noAuthNoPriv")

            # 获取带速率的接口统计
            stats = await self.snmp_manager.get_interface_statistics(ip, version, **kwargs)

            self.write({"code": 0, "message": "success", "data": stats})
        except Exception as e:
            self.set_status(500)
            self.write({"code": 500, "message": f"查询接口速率失败: {str(e)}", "data": None})