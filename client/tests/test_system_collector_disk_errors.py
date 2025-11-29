import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_disk_info_permission_error_and_other():
    from src.system.system_collector import SystemCollector
    usage = SimpleNamespace(total=1000, used=400, free=600, percent=40.0)
    with patch("src.system.system_collector.psutil.disk_partitions", return_value=[SimpleNamespace(device="d", mountpoint="/d", fstype="x")]), \
         patch("src.system.system_collector.psutil.disk_usage", return_value=usage), \
         patch("src.system.system_collector.psutil.disk_io_counters", side_effect=PermissionError("perm")):
        sc = SystemCollector()
        info = sc.get_disk_info()
        assert info.get("total") == 1000
    with patch("src.system.system_collector.psutil.disk_partitions", side_effect=Exception("boom")):
        sc = SystemCollector()
        info = sc.get_disk_info()
        assert isinstance(info, dict)
