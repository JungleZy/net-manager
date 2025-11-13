#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from typing import Dict, Any

from src.network.api.handlers.base_handler import BaseHandler
from src.core.config import METRICS_ENABLED
from src.core.logger import logger


class MetricsHandler(BaseHandler):
    """轻量指标端点"""

    def initialize(self, db_manager, get_tcp_server_func=None):
        self.db_manager = db_manager
        self.get_tcp_server_func = get_tcp_server_func

    def get(self):
        if not METRICS_ENABLED:
            self.set_status(404)
            self.write({"status": "error", "message": "metrics disabled"})
            return

        metrics: Dict[str, Any] = {
            "ts": time.time(),
            "db_health": False,
            "tcp_client_count": 0,
            "tcp_client_map_size": 0,
            "snmp_device_stats": {},
            "snmp_interface_stats": {},
            "broadcast_errors": 0,
            "message_count": 0,
        }

        try:
            metrics["db_health"] = self.db_manager.health_check()
        except Exception as e:
            logger.debug(f"DB健康检查错误: {e}")

        try:
            tcp_server = (
                self.get_tcp_server_func() if self.get_tcp_server_func else None
            )
            if tcp_server:
                with tcp_server.clients_lock:
                    metrics["tcp_client_count"] = len(tcp_server.clients)
                    metrics["tcp_client_map_size"] = len(tcp_server.client_id_map)
        except Exception as e:
            logger.debug(f"TCP指标收集错误: {e}")

        try:
            from src.snmp.unified_poller import (
                get_device_poller,
                get_interface_poller,
            )

            device_poller = get_device_poller()
            interface_poller = get_interface_poller()
            if device_poller:
                metrics["snmp_device_stats"] = device_poller.get_statistics()
            if interface_poller:
                metrics["snmp_interface_stats"] = interface_poller.get_statistics()
        except Exception as e:
            logger.debug(f"SNMP指标收集错误: {e}")

        try:
            from src.core.state_manager import state_manager

            metrics["broadcast_errors"] = getattr(
                state_manager, "_broadcast_errors", 0
            )
            metrics["message_count"] = getattr(state_manager, "_message_count", 0)
        except Exception as e:
            logger.debug(f"StateManager指标收集错误: {e}")

        self.write({"status": "success", "data": metrics})

