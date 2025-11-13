import logging

def test_notify_event_exception_logging(caplog):
    from src.core.state_manager import state_manager

    caplog.set_level(logging.ERROR)

    def bad_cb(data):
        raise RuntimeError("boom")

    state_manager.subscribe_event("test_event", bad_cb)
    state_manager._notify_event("test_event", {"k": "v"})

    assert any("事件回调执行失败" in r.message for r in caplog.records)
