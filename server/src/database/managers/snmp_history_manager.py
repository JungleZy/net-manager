#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Any, Dict, List, Optional, Tuple

from src.core.logger import logger
from src.database.db_exceptions import DatabaseError, DatabaseQueryError
from src.database.managers.base_manager import BaseDatabaseManager


class SNMPHistoryManager(BaseDatabaseManager):
    def __init__(
        self,
        db_path: str = "net_manager_server.db",
        max_connections: int = 10,
        cleanup_interval: int = 60,
        max_idle_time: int = 300,
        shared_pool=None,
    ):
        super().__init__(
            db_path, max_connections, cleanup_interval, max_idle_time, shared_pool
        )
        self.init_tables()

    def init_tables(self) -> None:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.execute("PRAGMA journal_mode = WAL")
                cursor.execute("PRAGMA synchronous = NORMAL")
                cursor.execute("PRAGMA cache_size = 10000")
                cursor.execute("PRAGMA temp_store = MEMORY")

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS snmp_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        switch_id INTEGER NOT NULL,
                        ip TEXT NOT NULL,
                        poll_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        interface_count INTEGER DEFAULT 0,
                        interface_info TEXT,
                        poll_time REAL,
                        created_at DATETIME DEFAULT (datetime('now', 'localtime')),
                        FOREIGN KEY (switch_id) REFERENCES switch_info(id) ON DELETE CASCADE
                    )
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_snmp_history_switch_time
                    ON snmp_history(switch_id, created_at DESC)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_snmp_history_type
                    ON snmp_history(poll_type)
                """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_snmp_history_switch_type_time
                    ON snmp_history(switch_id, poll_type, created_at)
                """
                )

                conn.commit()
        except Exception as e:
            logger.error(f"SNMP历史记录表初始化失败: {e}")
            raise DatabaseError(f"SNMP历史记录表初始化失败: {e}") from e

    async def insert_history_async(self, record: Dict[str, Any]) -> Tuple[bool, str]:
        try:
            interface_info_text = None
            info = record.get("interface_info")
            if info is not None:
                try:
                    interface_info_text = json.dumps(info, ensure_ascii=False)
                except Exception:
                    interface_info_text = str(info)

            latest_status = None
            if self.async_pool is None:
                with self.get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT status FROM snmp_history WHERE switch_id = ? AND poll_type = ? ORDER BY created_at DESC LIMIT 1",
                        (record.get("switch_id"), record.get("poll_type")),
                    )
                    row = cursor.fetchone()
                    latest_status = row[0] if row else None
                    if latest_status == record.get("status"):
                        return True, "状态未变化，跳过保存"
                    cursor.execute(
                        """
                        INSERT INTO snmp_history (
                            switch_id, ip, poll_type, status,
                            interface_count, interface_info, poll_time, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                    """,
                        (
                            record.get("switch_id"),
                            record.get("ip"),
                            record.get("poll_type"),
                            record.get("status"),
                            int(record.get("interface_count", 0)),
                            interface_info_text,
                            float(record.get("poll_time", 0.0)),
                        ),
                    )
                    conn.commit()
                    return True, "插入成功"
            else:
                async with self.get_async_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT status FROM snmp_history WHERE switch_id = ? AND poll_type = ? ORDER BY created_at DESC LIMIT 1",
                        (record.get("switch_id"), record.get("poll_type")),
                    )
                    row = cursor.fetchone()
                    latest_status = row[0] if row else None
                    if latest_status == record.get("status"):
                        return True, "状态未变化，跳过保存"
                    cursor.execute(
                        """
                        INSERT INTO snmp_history (
                            switch_id, ip, poll_type, status,
                            interface_count, interface_info, poll_time, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
                    """,
                        (
                            record.get("switch_id"),
                            record.get("ip"),
                            record.get("poll_type"),
                            record.get("status"),
                            int(record.get("interface_count", 0)),
                            interface_info_text,
                            float(record.get("poll_time", 0.0)),
                        ),
                    )
                    conn.commit()
                    return True, "插入成功"
        except Exception as e:
            logger.error(f"插入SNMP历史记录失败: {e}")
            raise DatabaseQueryError(f"插入SNMP历史记录失败: {e}") from e

    def query_history(
        self,
        switch_id: int,
        limit: int = 100,
        offset: int = 0,
        poll_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                if poll_type:
                    cursor.execute(
                        """
                        SELECT id, switch_id, ip, poll_type, status, interface_count,
                               interface_info, poll_time, created_at
                        FROM snmp_history
                        WHERE switch_id = ? AND poll_type = ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    """,
                        (switch_id, poll_type, limit, offset),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, switch_id, ip, poll_type, status, interface_count,
                               interface_info, poll_time, created_at
                        FROM snmp_history
                        WHERE switch_id = ?
                        ORDER BY created_at DESC
                        LIMIT ? OFFSET ?
                    """,
                        (switch_id, limit, offset),
                    )

                rows = cursor.fetchall()
                results: List[Dict[str, Any]] = []
                for r in rows:
                    interface_info = r[6]
                    try:
                        parsed = json.loads(interface_info) if interface_info else None
                    except Exception:
                        parsed = interface_info
                    results.append(
                        {
                            "id": r[0],
                            "switch_id": r[1],
                            "ip": r[2],
                            "poll_type": r[3],
                            "status": r[4],
                            "interface_count": r[5],
                            "interface_info": parsed,
                            "poll_time": r[7],
                            "created_at": r[8],
                        }
                    )
                return results
        except Exception as e:
            logger.error(f"查询SNMP历史记录失败: {e}")
            raise DatabaseQueryError(f"查询SNMP历史记录失败: {e}") from e

    def clear_history(self, switch_id: Optional[int] = None) -> Tuple[bool, str]:
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                if switch_id is None:
                    cursor.execute("DELETE FROM snmp_history")
                else:
                    cursor.execute(
                        "DELETE FROM snmp_history WHERE switch_id = ?",
                        (switch_id,),
                    )
                conn.commit()
                return True, "清空成功"
        except Exception as e:
            logger.error(f"清空SNMP历史记录失败: {e}")
            raise DatabaseQueryError(f"清空SNMP历史记录失败: {e}") from e
