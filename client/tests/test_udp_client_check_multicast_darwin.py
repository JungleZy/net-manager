import os
import sys
from unittest.mock import patch, MagicMock

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_check_interface_multicast_darwin_true():
    from src.network.udp_client import UDPClient
    u = UDPClient()
    with patch("src.network.udp_client.platform.system", return_value="Darwin"), \
         patch("subprocess.run", return_value=MagicMock(returncode=0, stdout="... MULTICAST ...")):
        assert u._check_interface_multicast_capability("en0") is True
