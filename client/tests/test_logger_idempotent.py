import os
import sys
import logging
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_setup_logger_idempotent_handlers_not_duplicate():
    import src.utils.logger as lg

    with patch("src.utils.logger._logger", None, create=True), patch(
        "src.config_module.config.config",
        type("C", (), {"get": staticmethod(lambda *a, **k: "INFO")}),
    ):
        l1 = lg.setup_logger()
        l2 = lg.setup_logger()
        assert l1 is l2
        # file handler may be absent in INFO-only config; ensure no duplicate stream handlers
        streams = [h for h in l1.handlers if type(h) is logging.StreamHandler]
        assert len(streams) <= 1
