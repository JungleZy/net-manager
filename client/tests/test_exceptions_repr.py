import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

def test_exceptions_str_and_repr():
    from src.exceptions.exceptions import NetManagerError, NetworkDiscoveryError, ConfigurationError
    e = NetManagerError("msg", error_code=123, details={"a":1})
    assert str(e) == "[123] msg"
    r = repr(e)
    assert "NetManagerError" in r and "error_code=123" in r
    e2 = NetworkDiscoveryError("x")
    assert "x" in str(e2)
    e3 = ConfigurationError()
    assert "配置错误" in str(e3)
