# -*- coding: utf-8 -*-
"""
Network module package initialization.

This package contains network functionality for the network management server,
including UDP, TCP, and API servers.
"""

# Import network components for easier access
from src.network.udp_server import udp_server, stop_udp_server
from src.network.tcp_server import TCPServer
from src.network.api_server import APIServer

__all__ = [
    'udp_server',
    'stop_udp_server',
    'TCPServer',
    'APIServer'
]

__version__ = '1.0.0'