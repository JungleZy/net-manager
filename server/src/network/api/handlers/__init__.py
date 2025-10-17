#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API handlers package
"""

from src.network.api.handlers.base_handler import BaseHandler
from src.network.api.handlers.main_handler import MainHandler
from src.network.api.handlers.health_handler import HealthHandler
from src.network.api.handlers.devices_handlers import (
    DeviceCreateHandler,
    DeviceUpdateHandler,
    DeviceDeleteHandler,
    DeviceHandler,
    DeviceTypeHandler,
    DevicesHandler,
)
from src.network.api.handlers.switches_handlers import (
    SwitchCreateHandler,
    SwitchUpdateHandler,
    SwitchDeleteHandler,
    SwitchHandler,
    SwitchesHandler,
)
from src.network.api.handlers.topology_handlers import (
    TopologyCreateHandler,
    TopologyUpdateHandler,
    TopologyDeleteHandler,
    TopologyHandler,
    TopologiesHandler,
    TopologyLatestHandler,
)
from src.network.api.handlers.snmp_scan_handler import (
    SNMPScanHandler,
    SNMPScanHandlerSimple,
)
from src.network.api.handlers.performance_handler import PerformanceHandler

__all__ = [
    "BaseHandler",
    "MainHandler",
    "HealthHandler",
    "DeviceCreateHandler",
    "DeviceUpdateHandler",
    "DeviceDeleteHandler",
    "DeviceHandler",
    "DeviceTypeHandler",
    "DevicesHandler",
    "SwitchCreateHandler",
    "SwitchUpdateHandler",
    "SwitchDeleteHandler",
    "SwitchHandler",
    "SwitchesHandler",
    "TopologyCreateHandler",
    "TopologyUpdateHandler",
    "TopologyDeleteHandler",
    "TopologyHandler",
    "TopologiesHandler",
    "TopologyLatestHandler",
    "SNMPScanHandler",
    "SNMPScanHandlerSimple",
    "PerformanceHandler",
]
