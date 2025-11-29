import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_cpu_info_normal():
    from src.system.system_collector import SystemCollector

    cpu_times = SimpleNamespace(user=10, system=5, idle=85)
    freq = SimpleNamespace(current=2400)
    with patch("src.system.system_collector.psutil.cpu_count", return_value=4), patch(
        "src.system.system_collector.psutil.cpu_percent", return_value=12.5
    ), patch(
        "src.system.system_collector.psutil.cpu_times", return_value=cpu_times
    ), patch(
        "src.system.system_collector.psutil.cpu_freq", return_value=freq
    ):
        sc = SystemCollector()
        info = sc.get_cpu_info()
        assert info.get("cores") == 4 and info.get("usage_percent") is not None


def test_memory_info_normal():
    from src.system.system_collector import SystemCollector

    vm = SimpleNamespace(total=1000, available=600, used=400, percent=40)
    sm = SimpleNamespace(total=500, used=200, free=300, percent=40)
    with patch(
        "src.system.system_collector.psutil.virtual_memory", return_value=vm
    ), patch("src.system.system_collector.psutil.swap_memory", return_value=sm):
        sc = SystemCollector()
        info = sc.get_memory_info()
        assert info.get("total") == 1000 and info.get("swap_total") == 500


def test_disk_info_multiple_partitions():
    from src.system.system_collector import SystemCollector

    parts = [
        SimpleNamespace(device="d1", mountpoint="/d1", fstype="fs1"),
        SimpleNamespace(device="d2", mountpoint="/d2", fstype="fs2"),
    ]
    usage1 = SimpleNamespace(total=100, used=50, free=50, percent=50)
    usage2 = SimpleNamespace(total=200, used=100, free=100, percent=50)
    io = SimpleNamespace(
        read_bytes=10,
        write_bytes=20,
        read_count=1,
        write_count=2,
        read_time=3,
        write_time=4,
    )
    with patch(
        "src.system.system_collector.psutil.disk_partitions", return_value=parts
    ), patch(
        "src.system.system_collector.psutil.disk_usage", side_effect=[usage1, usage2]
    ), patch(
        "src.system.system_collector.psutil.disk_io_counters", return_value=io
    ):
        sc = SystemCollector()
        info = sc.get_disk_info()
        assert info.get("total") == 300 and info.get("used") == 150
