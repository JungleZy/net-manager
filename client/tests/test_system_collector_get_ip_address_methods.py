import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_ip_address_method2():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    with patch("src.system.system_collector.socket.socket", side_effect=Exception("m1")), \
         patch.object(SystemCollector, "_get_ip_via_psutil", return_value="192.168.88.1"):
        ip = sc.get_ip_address()
        assert ip == "192.168.88.1"

def test_get_ip_address_method3():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    with patch("src.system.system_collector.socket.socket", side_effect=Exception("m1")), \
         patch.object(SystemCollector, "_get_ip_via_psutil", return_value="unknown"), \
         patch.object(SystemCollector, "_get_ip_via_gateway", return_value="192.168.0.2"):
        ip = sc.get_ip_address()
        assert ip == "192.168.0.2"

def test_get_ip_address_method4():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    with patch("src.system.system_collector.socket.socket", side_effect=Exception("m1")), \
         patch.object(SystemCollector, "_get_ip_via_psutil", return_value="unknown"), \
         patch.object(SystemCollector, "_get_ip_via_gateway", return_value="unknown"), \
         patch("src.system.system_collector.socket.gethostbyname", return_value="10.0.0.5"):
        ip = sc.get_ip_address()
        assert ip == "10.0.0.5"
