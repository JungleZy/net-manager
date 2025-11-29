import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_cpu_info_fallback_on_exception():
    from src.system.system_collector import SystemCollector

    with patch(
        "src.system.system_collector.psutil.cpu_count", side_effect=Exception("err")
    ):
        sc = SystemCollector()
        info = sc.get_cpu_info()
        assert info.get("cores") == "unknown"


def test_memory_info_virtual_and_swap_fail():
    from src.system.system_collector import SystemCollector

    with patch(
        "src.system.system_collector.psutil.virtual_memory", side_effect=Exception("vm")
    ), patch(
        "src.system.system_collector.psutil.swap_memory", side_effect=Exception("swap")
    ):
        sc = SystemCollector()
        info = sc.get_memory_info()
        assert info.get("total") == "unknown"
        assert info.get("swap_total") == "unknown"


def test_disk_info_partitions_and_io():
    from src.system.system_collector import SystemCollector

    partitions = [SimpleNamespace(device="d1", mountpoint="/mnt/d1", fstype="fs1")]
    usage = SimpleNamespace(total=1000, used=400, free=600, percent=40.0)
    io = SimpleNamespace(
        read_bytes=10,
        write_bytes=20,
        read_count=1,
        write_count=2,
        read_time=3,
        write_time=4,
    )
    with patch(
        "src.system.system_collector.psutil.disk_partitions", return_value=partitions
    ), patch(
        "src.system.system_collector.psutil.disk_usage", return_value=usage
    ), patch(
        "src.system.system_collector.psutil.disk_io_counters", return_value=io
    ):
        sc = SystemCollector()
        info = sc.get_disk_info()
        assert info.get("total") == 1000
        assert info.get("used") == 400
        assert info.get("read_bytes") == 10


def test_get_processes_default_current_added():
    from src.system.system_collector import SystemCollector

    with patch("src.system.system_collector.psutil.process_iter", return_value=[]):
        sc = SystemCollector()
        processes = sc.get_processes()
        assert len(processes) >= 1
