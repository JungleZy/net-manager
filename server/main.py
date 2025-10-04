#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Net Manager Server - UDP服务端主程序
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from udp_server import udp_server

if __name__ == "__main__":
    udp_server()