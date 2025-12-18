#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import queue

class DevicePersistQueue:
    def __init__(self, db_manager, maxsize: int, flush_interval_ms: int, batch_size: int):
        self.db_manager = db_manager
        self.queue = queue.Queue(maxsize=maxsize)
        self.flush_interval_ms = flush_interval_ms
        self.batch_size = batch_size
        self.running = False
        self.worker = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()

    def stop(self):
        self.running = False
        if self.worker and self.worker.is_alive():
            self.worker.join(timeout=5)
        self.worker = None

    def enqueue(self, device_info) -> bool:
        try:
            self.queue.put_nowait(device_info)
            return True
        except queue.Full:
            return False

    def _drain_batch(self):
        batch = []
        while len(batch) < self.batch_size:
            try:
                item = self.queue.get_nowait()
                batch.append(item)
            except queue.Empty:
                break
        return batch

    def _run(self):
        interval = max(1, int(self.flush_interval_ms)) / 1000.0
        while self.running:
            try:
                time.sleep(interval)
                items = self._drain_batch()
                if not items:
                    continue
                try:
                    # 使用批量保存方法优化性能
                    self.db_manager.device_manager.save_device_info_batch(items)
                except Exception as e:
                    logger.exception(f"批量保存设备信息失败: {e}")
            except Exception as e:
                logger.exception(f"设备持久化队列运行出错: {e}")
