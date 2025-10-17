#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移脚本 - 添加设备别名字段
为 device_info 和 switch_info 表添加 alias 字段
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


def add_alias_field(db_path: str = "net_manager_server.db"):
    """
    为 device_info 和 switch_info 表添加 alias 字段

    Args:
        db_path: 数据库文件路径
    """
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查 device_info 表中是否已存在 alias 字段
        cursor.execute("PRAGMA table_info(device_info)")
        columns = [column[1] for column in cursor.fetchall()]

        if "alias" not in columns:
            logger.info("正在为 device_info 表添加 alias 字段...")
            cursor.execute(
                """
                ALTER TABLE device_info ADD COLUMN alias TEXT DEFAULT ''
                """
            )
            logger.info("device_info 表的 alias 字段添加成功")
        else:
            logger.info("device_info 表已存在 alias 字段，跳过")

        # 检查 switch_info 表中是否已存在 alias 字段
        cursor.execute("PRAGMA table_info(switch_info)")
        columns = [column[1] for column in cursor.fetchall()]

        if "alias" not in columns:
            logger.info("正在为 switch_info 表添加 alias 字段...")
            cursor.execute(
                """
                ALTER TABLE switch_info ADD COLUMN alias TEXT DEFAULT ''
                """
            )
            logger.info("switch_info 表的 alias 字段添加成功")
        else:
            logger.info("switch_info 表已存在 alias 字段，跳过")

        conn.commit()
        logger.info("数据库迁移完成")

    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    # 默认使用项目根目录下的数据库文件
    db_path = project_root / "net_manager_server.db"
    add_alias_field(str(db_path))
