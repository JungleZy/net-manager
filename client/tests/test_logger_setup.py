import os
import sys
import logging
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

parent_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, parent_dir)


def test_setup_logger_creates_file_handler():
    import src.utils.logger as lg

    tmp_dir = Path("./logs_test")
    log_path = tmp_dir / "nm_test.log"
    try:
        if tmp_dir.exists():
            for f in tmp_dir.iterdir():
                f.unlink()
            tmp_dir.rmdir()
        cfg = SimpleNamespace(
            get=lambda section, key, default: (
                str(log_path) if (section, key) == ("logging", "file") else "INFO"
            )
        )
        with patch("src.utils.logger._logger", None, create=True), patch(
            "src.utils.logger.logging.getLogger",
            return_value=logging.Logger("nm_test_logger"),
        ), patch(
            "src.utils.logger.get_appropriate_encoding", return_value="utf-8"
        ), patch(
            "src.utils.logger.normalize_path", side_effect=lambda p: str(p)
        ), patch(
            "src.config_module.config.config", cfg
        ):
            logger = lg.setup_logger()
            assert isinstance(logger, logging.Logger)
            logger.info("create file")
            assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    finally:
        logging.shutdown()
        if log_path.exists():
            log_path.unlink()
        if tmp_dir.exists():
            tmp_dir.rmdir()


def test_get_log_level_default_and_error():
    import src.utils.logger as lg

    # default path when config not set properly
    with patch(
        "src.config_module.config.config", SimpleNamespace(get=lambda *a, **k: "INFO")
    ):
        level = lg.get_log_level()
        assert level == logging.INFO
    # error path returns INFO
    with patch(
        "src.config_module.config.config",
        SimpleNamespace(get=lambda *a, **k: (_ for _ in ()).throw(Exception("boom"))),
    ):
        level = lg.get_log_level()
        assert level == logging.INFO


def test_file_handler_failure_warns_and_continues():
    import src.utils.logger as lg

    cfg = SimpleNamespace(
        get=lambda section, key, default: (
            "logs/nm_fail.log" if (section, key) == ("logging", "file") else "INFO"
        )
    )
    with patch("src.utils.logger._logger", None, create=True), patch(
        "src.utils.logger.get_appropriate_encoding", return_value="utf-8"
    ), patch("src.utils.logger.normalize_path", side_effect=lambda p: str(p)), patch(
        "src.config_module.config.config", cfg
    ), patch(
        "src.utils.logger.logging.FileHandler", side_effect=Exception("fail")
    ):
        logger = lg.setup_logger()
        assert isinstance(logger, logging.Logger)


def test_setup_logger_top_level_exception_fallback():
    import src.utils.logger as lg

    with patch("src.utils.logger._logger", None, create=True), patch(
        "src.utils.logger.get_log_level", side_effect=Exception("oops")
    ):
        logger = lg.setup_logger()
        assert isinstance(logger, logging.Logger)
