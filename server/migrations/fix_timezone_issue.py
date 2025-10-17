#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移脚本 - 修复时区问题
将现有表的时间戳默认值从UTC改为本地时间
"""

import sqlite3
import sys
from pathlib import Path
import logging

# 设置简单的logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent


def fix_timezone_for_device_info(db_path: str):
    """
    修复 device_info 表的时区问题

    注意：SQLite 不支持直接修改列的默认值，需要重建表
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("开始修复 device_info 表的时区问题...")

        # 1. 创建临时表（使用本地时间）
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS device_info_new (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                hostname TEXT,
                os_name TEXT,
                os_version TEXT,
                os_architecture TEXT,
                machine_type TEXT,
                services TEXT,
                processes TEXT,
                networks TEXT,
                cpu_info TEXT,
                memory_info TEXT,
                disk_info TEXT,
                type TEXT,
                alias TEXT DEFAULT '',
                timestamp DATETIME DEFAULT (datetime('now', 'localtime')),
                created_at DATETIME DEFAULT (datetime('now', 'localtime'))
            )
        """
        )

        # 2. 检查旧表是否存在
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='device_info'"
        )
        if cursor.fetchone():
            # 3. 复制数据
            logger.info("  正在复制数据...")
            cursor.execute(
                """
                INSERT INTO device_info_new 
                SELECT id, client_id, hostname, os_name, os_version, os_architecture, 
                       machine_type, services, processes, networks, cpu_info, memory_info, 
                       disk_info, type, alias, timestamp, created_at
                FROM device_info
            """
            )

            # 4. 删除旧表
            cursor.execute("DROP TABLE device_info")
            logger.info("  已删除旧表")

        # 5. 重命名新表
        cursor.execute("ALTER TABLE device_info_new RENAME TO device_info")

        # 6. 重建索引
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_device_info_client_id 
            ON device_info(client_id)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_device_info_timestamp 
            ON device_info(timestamp)
        """
        )

        conn.commit()
        logger.info("✓ device_info 表时区修复成功")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ 修复 device_info 表失败: {e}")
        raise
    finally:
        if conn:
            conn.close()


def fix_timezone_for_switch_info(db_path: str):
    """
    修复 switch_info 表的时区问题
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        logger.info("开始修复 switch_info 表的时区问题...")

        # 1. 创建临时表（使用本地时间）
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS switch_info_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT NOT NULL UNIQUE,
                snmp_version TEXT NOT NULL,
                community TEXT,
                user TEXT,
                auth_key TEXT,
                auth_protocol TEXT,
                priv_key TEXT,
                priv_protocol TEXT,
                description TEXT,
                device_name TEXT,
                device_type TEXT,
                alias TEXT DEFAULT '',
                created_at DATETIME DEFAULT (datetime('now', 'localtime')),
                updated_at DATETIME DEFAULT (datetime('now', 'localtime'))
            )
        """
        )

        # 2. 检查旧表是否存在
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='switch_info'"
        )
        if cursor.fetchone():
            # 3. 复制数据
            logger.info("  正在复制数据...")
            cursor.execute(
                """
                INSERT INTO switch_info_new 
                SELECT id, ip, snmp_version, community, user, auth_key, auth_protocol,
                       priv_key, priv_protocol, description, device_name, device_type, 
                       alias, created_at, updated_at
                FROM switch_info
            """
            )

            # 4. 删除旧表
            cursor.execute("DROP TABLE switch_info")
            logger.info("  已删除旧表")

        # 5. 重命名新表
        cursor.execute("ALTER TABLE switch_info_new RENAME TO switch_info")

        # 6. 重建索引
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_switch_info_ip 
            ON switch_info(ip)
        """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_switch_info_created_at 
            ON switch_info(created_at)
        """
        )

        conn.commit()
        logger.info("✓ switch_info 表时区修复成功")

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"✗ 修复 switch_info 表失败: {e}")
        raise
    finally:
        if conn:
            conn.close()


def fix_timezone_issue(db_path: str = "net_manager_server.db"):
    """
    修复数据库时区问题

    Args:
        db_path: 数据库文件路径
    """
    logger.info("=" * 60)
    logger.info("开始修复数据库时区问题")
    logger.info(f"数据库路径: {db_path}")
    logger.info("=" * 60)

    try:
        # 修复 device_info 表
        fix_timezone_for_device_info(db_path)

        # 修复 switch_info 表
        fix_timezone_for_switch_info(db_path)

        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 时区问题修复完成！")
        logger.info("=" * 60)
        logger.info("")
        logger.info("说明：")
        logger.info("  - 所有时间字段现在使用本地时间")
        logger.info(
            "  - timestamp/created_at/updated_at 默认值已修改为 datetime('now', 'localtime')"
        )
        logger.info("  - 原有数据已保留，不受影响")
        logger.info("")

    except Exception as e:
        logger.error(f"时区问题修复失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # 默认使用项目根目录下的数据库文件
    db_path = project_root / "net_manager_server.db"
    fix_timezone_issue(str(db_path))
