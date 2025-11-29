import os
import sys
from types import SimpleNamespace

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_app_controller_hash_changes_on_field_update():
    from src.core.app_controller import AppController
    c = AppController()
    info1 = SimpleNamespace(
        hostname="h",
        ip_address="1.2.3.4",
        mac_address="aa:bb:cc:dd:ee:ff",
        gateway="g",
        netmask="255.255.255.0",
        os_name="Windows",
        os_version="11",
        os_architecture="x64",
        machine_type="pc",
    )
    h1 = c._calculate_system_info_hash(info1)
    info2 = SimpleNamespace(
        hostname="h",
        ip_address="1.2.3.4",
        mac_address="aa:bb:cc:dd:ee:ff",
        gateway="g",
        netmask="255.255.255.0",
        os_name="Windows",
        os_version="11",
        os_architecture="x64",
        machine_type="server",
    )
    h2 = c._calculate_system_info_hash(info2)
    assert h1 != h2
