#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试TCP连接逻辑修改
验证在发起UDP发现前先查询配置文件是否存在tcp_ip的功能
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.state_manager import get_state_manager
from src.core.app_controller import AppController

def test_tcp_ip_from_config():
    state_manager = get_state_manager()
    test_ip = "192.168.1.100"
    test_port = 12346
    state_manager.set_state("tcp_ip", test_ip)
    state_manager.set_state("tcp_port", test_port)
    app_controller = AppController()
    server_address = app_controller._get_server_address_from_config()
    if server_address:
        ip, port = server_address
        assert ip == test_ip
        assert port == test_port
    else:
        assert False
    state_manager.set_state("tcp_ip", "")
    server_address = app_controller._get_server_address_from_config()
    assert server_address is None

def test_connection_logic():
    state_manager = get_state_manager()
    test_ip = "192.168.1.200"
    test_port = 12346
    state_manager.set_state("tcp_ip", test_ip)
    state_manager.set_state("tcp_port", test_port)
    app_controller = AppController()
    server_address = app_controller._get_server_address_from_config()
    if server_address:
        ip, port = server_address
        pass
    else:
        assert False
    state_manager.set_state("tcp_ip", "")
    server_address = app_controller._get_server_address_from_config()
    assert server_address is None

def main():
    os.chdir(Path(__file__).parent)
    test_tcp_ip_from_config()
    test_connection_logic()

if __name__ == "__main__":
    main()
