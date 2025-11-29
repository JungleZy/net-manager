import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_collect_system_info_integration():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    info = sc.collect_system_info()
    assert isinstance(info.hostname, str)
    assert isinstance(info.network_interfaces, list)
