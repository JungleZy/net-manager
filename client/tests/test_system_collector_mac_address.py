import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_mac_address_priority_and_unknown():
    from src.system.system_collector import SystemCollector
    import psutil
    addrs = {
        "lo": [SimpleNamespace(family=psutil.AF_LINK, address="00:00:00:00:00:00")],
        "Wi-Fi": [SimpleNamespace(family=psutil.AF_LINK, address="aa:aa:aa:aa:aa:aa")],
        "Ethernet": [SimpleNamespace(family=psutil.AF_LINK, address="bb:bb:bb:bb:bb:bb")],
    }
    with patch("src.system.system_collector.psutil.net_if_addrs", return_value=addrs):
        sc = SystemCollector()
        mac = sc.get_mac_address()
        assert mac in ("bb:bb:bb:bb:bb:bb", "aa:aa:aa:aa:aa:aa")
    # all invalid -> unknown
    bad = {"lo": [SimpleNamespace(family=psutil.AF_LINK, address="ff:ff:ff:ff:ff:ff")]} 
    with patch("src.system.system_collector.psutil.net_if_addrs", return_value=bad):
        sc = SystemCollector()
        assert sc.get_mac_address() == "unknown"
