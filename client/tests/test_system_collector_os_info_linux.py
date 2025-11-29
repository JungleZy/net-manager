import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_get_os_info_linux():
    from src.system.system_collector import SystemCollector

    with patch(
        "src.system.system_collector.platform.system", return_value="Linux"
    ), patch("src.system.system_collector.platform.release", return_value="6.1"), patch(
        "src.system.system_collector.platform.machine", return_value="x86_64"
    ), patch(
        "src.system.system_collector.platform.architecture",
        return_value=("64bit", "ELF"),
    ):
        sc = SystemCollector()
        os_name, os_version, os_arch, machine_type = sc.get_os_info()
        assert os_name == "Linux" and os_arch == "64bit" and machine_type == "x86_64"
