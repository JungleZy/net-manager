import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_virtual_and_loopback_detection():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    assert sc._is_virtual_or_loopback_interface("lo")
    assert sc._is_virtual_or_loopback_interface("Loopback")
    assert sc._is_virtual_or_loopback_interface("vmnet0")
    assert sc._is_virtual_or_loopback_interface("VirtualBox Host-Only")
    assert sc._is_virtual_or_loopback_interface("wan miniport")
