import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_cpu_load_oserror_sets_unsupported():
    from src.system.system_collector import SystemCollector

    with patch("src.system.system_collector.psutil.getloadavg", side_effect=OSError()):
        sc = SystemCollector()
        info = sc.get_cpu_info()
        assert info.get("load_average") == "unknown"
