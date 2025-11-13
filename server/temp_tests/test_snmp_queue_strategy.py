import asyncio


def test_drop_new_strategy(monkeypatch):
    from src.snmp.unified_poller import SNMPPoller
    from src.database.managers.switch_manager import SwitchManager
    from src.core import config

    # 配置为 drop_new，队列最大为 3
    monkeypatch.setattr(config, "SNMP_QUEUE_STRATEGY", "drop_new")
    monkeypatch.setattr(config, "SNMP_QUEUE_MAXSIZE", 3)

    # 伪造 SwitchManager 返回多个设备
    class FakeSM:
        def get_all_switches(self):
            return [{"ip": f"10.0.0.{i}"} for i in range(1, 8)]

    poller = SNMPPoller(switch_manager=FakeSM(), poll_interval=1)

    # 启动一个简化的轮询循环，只运行enqueue逻辑一次
    async def once_enqueue():
        poller._task_queue = asyncio.Queue(maxsize=config.SNMP_QUEUE_MAXSIZE)
        poller._active_lock = asyncio.Lock()
        await poller._enqueue_devices()

    # 运行一次入队（由于poll_interval循环，这里会立即返回）
    poller._running = True
    def runner():
        async def _run():
            task = asyncio.create_task(once_enqueue())
            await asyncio.sleep(0.2)
            poller._running = False
            await task
        asyncio.run(_run())

    runner()

    # 队列大小不超过最大，且存在丢弃统计
    assert poller._task_queue.qsize() <= config.SNMP_QUEUE_MAXSIZE
    assert poller.get_statistics().get("dropped_items", 0) >= 1
