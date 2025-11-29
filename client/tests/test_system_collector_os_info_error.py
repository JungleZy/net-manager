import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_os_info_architecture_error():
    from src.system.system_collector import SystemCollector
    with patch("src.system.system_collector.platform.system", return_value="Windows"), \
         patch("src.system.system_collector.platform.version", return_value="10"), \
         patch("src.system.system_collector.platform.machine", return_value="x64"), \
         patch("src.system.system_collector.platform.architecture", side_effect=Exception("x")):
        sc = SystemCollector()
        os_name, os_version, os_arch, machine_type = sc.get_os_info()
        assert os_name == "Windows" and os_version == "10" and machine_type == "x64" and os_arch == "unknown"
