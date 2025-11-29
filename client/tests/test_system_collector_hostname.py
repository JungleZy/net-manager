import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_get_hostname_returns_string():
    from src.system.system_collector import SystemCollector
    sc = SystemCollector()
    h = sc.get_hostname()
    assert isinstance(h, str)
