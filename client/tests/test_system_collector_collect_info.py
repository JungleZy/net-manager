import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_collect_system_info_success():
    from src.system.system_collector import SystemCollector

    sc = SystemCollector()
    with patch.object(SystemCollector, "get_hostname", return_value="h"), patch.object(
        SystemCollector, "get_os_info", return_value=("Windows", "11", "x64", "pc")
    ), patch.object(
        SystemCollector, "get_cpu_info", return_value={"cores": 4}
    ), patch.object(
        SystemCollector, "get_memory_info", return_value={"total": 100}
    ), patch.object(
        SystemCollector, "get_disk_info", return_value={"total": 200}
    ), patch.object(
        SystemCollector, "get_network_interfaces", return_value=[{"name": "eth0"}]
    ), patch.object(
        SystemCollector, "get_processes", return_value=[{"pid": 1}]
    ), patch.object(
        SystemCollector, "get_services", return_value=[{"protocol": "TCP"}]
    ), patch(
        "src.core.state_manager.StateManager"
    ) as SM:
        SM.return_value.get_client_id.return_value = "abc"
        info = sc.collect_system_info()
        assert info.hostname == "h"
        assert info.client_id == "abc"
        assert (
            info.os_name == "Windows"
            and info.os_version == "11"
            and info.os_architecture == "x64"
            and info.machine_type == "pc"
        )
        assert isinstance(info.network_interfaces, list)


def test_collect_system_info_fallback_on_exception():
    from src.system.system_collector import SystemCollector

    sc = SystemCollector()
    with patch.object(SystemCollector, "get_hostname", side_effect=Exception("x")):
        info = sc.collect_system_info()
        assert info.hostname == "unknown"
