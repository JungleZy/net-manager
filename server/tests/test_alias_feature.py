#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试设备别名功能
"""

import sys
from pathlib import Path
import tempfile

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.database.managers.device_manager import DeviceManager
from src.database.managers.switch_manager import SwitchManager
from src.models.device_info import DeviceInfo
from src.models.switch_info import SwitchInfo
from src.core.logger import logger


def test_device_alias():
    """测试设备别名功能"""
    print("\n=== 测试设备别名功能 ===")

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    device_manager = DeviceManager(db_path=tmp.name)

    # 创建测试设备
    test_device_data = {
        "id": "test-device-001",
        "client_id": "client-001",
        "hostname": "test-hostname",
        "os_name": "Windows",
        "os_version": "10",
        "os_architecture": "x64",
        "machine_type": "Desktop",
        "type": "台式机",
    }

    print("\n1. 创建设备（alias应为空）...")
    success, message = device_manager.create_device(test_device_data)
    print(f"   结果: {message}")

    # 查询设备
    device = device_manager.get_device_info_by_id("test-device-001")
    assert device is not None, "设备应该存在"
    print(f"   设备信息: alias='{device['alias']}'")
    assert device["alias"] == "", "创建时alias应为空"

    # 通过UpdateHandler更新alias
    print("\n2. 更新设备别名...")
    test_device_data["alias"] = "办公室主机A"
    success, message = device_manager.update_device(test_device_data)
    print(f"   结果: {message}")

    # 查询更新后的设备
    device = device_manager.get_device_info_by_id("test-device-001")
    assert device is not None, "设备应该存在"
    print(f"   更新后的设备信息: alias='{device['alias']}'")
    assert device["alias"] == "办公室主机A", "更新后alias应为'办公室主机A'"

    # 测试通过save_device_info不会修改alias
    print("\n3. 测试通过save_device_info不会修改alias...")
    device_info = DeviceInfo(
        id="test-device-001",
        client_id="client-001",
        hostname="test-hostname-updated",
        os_name="Windows",
        os_version="11",
        os_architecture="x64",
        machine_type="Desktop",
    )
    device_manager.save_device_info(device_info)

    device = device_manager.get_device_info_by_id("test-device-001")
    assert device is not None, "设备应该存在"
    print(
        f"   保存后的设备信息: hostname='{device['hostname']}', alias='{device['alias']}'"
    )
    assert device["hostname"] == "test-hostname-updated", "hostname应该被更新"
    assert device["alias"] == "办公室主机A", "alias不应该被save_device_info修改"

    print("\n✅ 设备别名功能测试通过！")


def test_switch_alias():
    """测试交换机别名功能"""
    print("\n=== 测试交换机别名功能 ===")

    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    switch_manager = SwitchManager(db_path=tmp.name)

    # 创建测试交换机
    print("\n1. 创建交换机（alias应为空）...")
    switch_info = SwitchInfo(
        ip="192.168.1.100",
        snmp_version="2c",
        community="public",
        device_name="核心交换机",
        device_type="交换机",
    )
    success, message = switch_manager.add_switch(switch_info)
    print(f"   结果: {message}")

    # 查询交换机
    switch = switch_manager.get_switch_by_ip("192.168.1.100")
    assert switch is not None, "交换机应该存在"
    print(f"   交换机信息: id={switch['id']}, alias='{switch['alias']}'")
    assert switch["alias"] == "", "创建时alias应为空"

    # 通过UpdateHandler更新alias
    print("\n2. 更新交换机别名...")
    switch_info_update = SwitchInfo(
        id=switch["id"],
        ip="192.168.1.100",
        snmp_version="2c",
        community="public",
        device_name="核心交换机",
        device_type="交换机",
        alias="机房A-核心交换机",
    )
    success, message = switch_manager.update_switch(switch_info_update)
    print(f"   结果: {message}")

    # 查询更新后的交换机
    switch = switch_manager.get_switch_by_ip("192.168.1.100")
    assert switch is not None, "交换机应该存在"
    print(f"   更新后的交换机信息: alias='{switch['alias']}'")
    assert switch["alias"] == "机房A-核心交换机", "更新后alias应为'机房A-核心交换机'"

    print("\n✅ 交换机别名功能测试通过！")


if __name__ == "__main__":
    try:
        # 运行迁移脚本
        print("运行数据库迁移...")
        from migrations.add_alias_field import add_alias_field

        add_alias_field("test_alias.db")

        # 测试设备别名
        test_device_alias()

        # 测试交换机别名
        test_switch_alias()

        print("\n" + "=" * 50)
        print("🎉 所有测试通过！")
        print("=" * 50)

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        # 清理测试数据库
        import os

        if os.path.exists("test_alias.db"):
            os.remove("test_alias.db")
            print("\n清理测试数据库完成")
