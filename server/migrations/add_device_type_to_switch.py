#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移脚本 - 为 switch_info 表添加 device_type 字段
"""

import sqlite3
import os
from pathlib import Path


def migrate():
    """执行数据库迁移"""
    # 获取数据库文件路径
    db_path = Path(__file__).parent.parent / "net_manager_server.db"

    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(switch_info)")
        columns = [column[1] for column in cursor.fetchall()]

        if "device_type" in columns:
            print("字段 device_type 已存在，跳过迁移")
            conn.close()
            return True

        # 添加 device_type 字段
        print("正在添加 device_type 字段到 switch_info 表...")
        cursor.execute(
            """
            ALTER TABLE switch_info ADD COLUMN device_type TEXT DEFAULT ''
        """
        )

        conn.commit()
        print("✓ 迁移成功：已添加 device_type 字段")

        # 验证字段是否添加成功
        cursor.execute("PRAGMA table_info(switch_info)")
        columns = [column[1] for column in cursor.fetchall()]

        if "device_type" in columns:
            print("✓ 验证成功：device_type 字段已成功添加")
        else:
            print("✗ 验证失败：device_type 字段未添加")
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"✗ 迁移失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("数据库迁移：为 switch_info 表添加 device_type 字段")
    print("=" * 60)

    success = migrate()

    if success:
        print("\n迁移完成！")
    else:
        print("\n迁移失败，请检查错误信息。")

    print("=" * 60)
