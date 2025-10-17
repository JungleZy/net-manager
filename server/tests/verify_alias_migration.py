#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证别名字段迁移
"""

import sqlite3
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from migrations.add_alias_field import add_alias_field


def verify_alias_migration(db_path: str = "net_manager_server.db"):
    """验证别名字段迁移"""

    print("=" * 60)
    print("验证设备别名字段迁移")
    print("=" * 60)

    # 运行迁移
    print("\n1. 运行数据库迁移...")
    try:
        add_alias_field(db_path)
        print("   ✓ 迁移成功")
    except Exception as e:
        print(f"   ✗ 迁移失败: {e}")
        return False

    # 验证device_info表
    print("\n2. 验证device_info表结构...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(device_info)")
        columns = {column[1]: column[2] for column in cursor.fetchall()}

        if "alias" in columns:
            print(f"   ✓ device_info表包含alias字段 (类型: {columns['alias']})")
        else:
            print("   ✗ device_info表不包含alias字段")
            conn.close()
            return False

        conn.close()
    except Exception as e:
        print(f"   ✗ 验证失败: {e}")
        return False

    # 验证switch_info表
    print("\n3. 验证switch_info表结构...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(switch_info)")
        columns = {column[1]: column[2] for column in cursor.fetchall()}

        if "alias" in columns:
            print(f"   ✓ switch_info表包含alias字段 (类型: {columns['alias']})")
        else:
            print("   ✗ switch_info表不包含alias字段")
            conn.close()
            return False

        conn.close()
    except Exception as e:
        print(f"   ✗ 验证失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("🎉 所有验证通过！别名字段已成功添加到数据库")
    print("=" * 60)
    print("\n说明：")
    print("  - device_info.alias: 设备别名字段")
    print("  - switch_info.alias: 交换机别名字段")
    print("  - alias字段只能通过各自的UpdateHandler修改")
    print("  - 创建设备/交换机时，alias默认为空字符串")
    print("\n")

    return True


if __name__ == "__main__":
    # 默认使用项目根目录下的数据库文件
    db_path = project_root / "net_manager_server.db"

    success = verify_alias_migration(str(db_path))

    if not success:
        sys.exit(1)
