import os
import sys
from unittest.mock import patch

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_services_error_returns_empty_list():
    from src.system.system_collector import SystemCollector
    with patch("src.system.system_collector.psutil.net_connections", side_effect=Exception("boom")):
        sc = SystemCollector()
        assert sc.get_services() == []
