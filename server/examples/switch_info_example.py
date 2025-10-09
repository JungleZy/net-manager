#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SwitchInfo模型使用示例

这个示例演示了如何使用SwitchInfo模型和数据库管理器来管理交换机配置信息。
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.models.switch_info import SwitchInfo
from src.database import DatabaseManager

def main():
    """主函数 - 演示SwitchInfo的使用"""
    print("SwitchInfo模型使用示例")
    print("=" * 30)
    
    # 创建数据库管理器实例
    db_manager = DatabaseManager("example_net_manager.db")
    
    # 1. 创建SwitchInfo对象
    print("\n1. 创建SwitchInfo对象")
    switch1 = SwitchInfo(
        ip="192.168.1.100",
        snmp_version="2c",
        community="public",
        description="Core Switch"
    )
    
    switch2 = SwitchInfo(
        ip="192.168.1.101",
        snmp_version="3",
        user="admin",
        auth_key="mysecretpassword",
        auth_protocol="SHA",
        priv_key="myprivatekey",
        priv_protocol="AES",
        description="Distribution Switch"
    )
    
    print(f"创建了交换机1: {switch1}")
    print(f"创建了交换机2: {switch2}")
    
    # 2. 添加交换机到数据库
    print("\n2. 添加交换机到数据库")
    try:
        success, message = db_manager.add_switch(switch1)
        print(f"添加交换机1结果: {success}, {message}")
    except Exception as e:
        print(f"添加交换机1失败: {e}")
    
    try:
        success, message = db_manager.add_switch(switch2)
        print(f"添加交换机2结果: {success}, {message}")
    except Exception as e:
        print(f"添加交换机2失败: {e}")
    
    # 3. 获取所有交换机
    print("\n3. 获取所有交换机")
    try:
        switches = db_manager.get_all_switches()
        print(f"数据库中共有 {len(switches)} 个交换机:")
        for switch in switches:
            print(f"  - ID: {switch['id']}, IP: {switch['ip']}, 版本: {switch['snmp_version']}, 描述: {switch['description']}")
    except Exception as e:
        print(f"获取交换机列表失败: {e}")
    
    # 4. 根据IP获取交换机
    print("\n4. 根据IP获取交换机")
    try:
        switch = db_manager.get_switch_by_ip("192.168.1.100")
        if switch:
            print(f"找到交换机: IP={switch['ip']}, 版本={switch['snmp_version']}, 描述={switch['description']}")
        else:
            print("未找到IP为192.168.1.100的交换机")
    except Exception as e:
        print(f"根据IP获取交换机失败: {e}")
    
    # 5. 更新交换机
    print("\n5. 更新交换机")
    if switches:
        # 获取第一个交换机并更新它
        first_switch_data = switches[0]
        updated_switch = SwitchInfo(
            id=first_switch_data['id'],
            ip=first_switch_data['ip'],
            snmp_version="3",
            user="newadmin",
            auth_key="newpassword",
            auth_protocol="MD5",
            priv_key="newprivatekey",
            priv_protocol="DES",
            description="Updated Core Switch"
        )
        
        try:
            success, message = db_manager.update_switch(updated_switch)
            print(f"更新交换机结果: {success}, {message}")
        except Exception as e:
            print(f"更新交换机失败: {e}")
    
    # 6. 再次获取所有交换机以验证更新
    print("\n6. 验证更新结果")
    try:
        switches = db_manager.get_all_switches()
        print(f"更新后的交换机列表:")
        for switch in switches:
            print(f"  - ID: {switch['id']}, IP: {switch['ip']}, 版本: {switch['snmp_version']}, 描述: {switch['description']}")
    except Exception as e:
        print(f"获取交换机列表失败: {e}")
    
    # 7. 删除交换机
    print("\n7. 删除交换机")
    if switches:
        # 删除第一个交换机
        switch_id_to_delete = switches[0]['id']
        try:
            success, message = db_manager.delete_switch(switch_id_to_delete)
            print(f"删除交换机(ID={switch_id_to_delete})结果: {success}, {message}")
        except Exception as e:
            print(f"删除交换机失败: {e}")
    
    # 8. 最终获取所有交换机
    print("\n8. 最终交换机列表")
    try:
        switches = db_manager.get_all_switches()
        print(f"最终数据库中共有 {len(switches)} 个交换机:")
        for switch in switches:
            print(f"  - ID: {switch['id']}, IP: {switch['ip']}, 版本: {switch['snmp_version']}, 描述: {switch['description']}")
    except Exception as e:
        print(f"获取交换机列表失败: {e}")
    
    # 清理示例数据库文件
    print("\n9. 清理示例数据库文件")
    if os.path.exists("example_net_manager.db"):
        os.remove("example_net_manager.db")
        print("已删除示例数据库文件")
    
    print("\n示例执行完成!")

if __name__ == "__main__":
    main()