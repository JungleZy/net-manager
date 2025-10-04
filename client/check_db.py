import sqlite3
import json

# 连接到数据库
conn = sqlite3.connect('net_manager.db')
cursor = conn.cursor()

# 查询最新的系统信息
cursor.execute('''
    SELECT hostname, ip_address, mac_address, services, processes, timestamp
    FROM system_info
    ORDER BY timestamp DESC
    LIMIT 1
''')

result = cursor.fetchone()
if result:
    hostname, ip_address, mac_address, services, processes, timestamp = result
    print(f"主机名: {hostname}")
    print(f"IP地址: {ip_address}")
    print(f"MAC地址: {mac_address}")
    print(f"时间戳: {timestamp}")
    
    # 解析服务信息
    services_data = json.loads(services)
    print(f"服务数量: {len(services_data)}")
    
    # 解析进程信息
    try:
        if processes:
            processes_data = json.loads(processes)
            print(f"进程数量: {len(processes_data)}")
            
            # 显示前5个进程
            print("\n前5个进程:")
            for i, process in enumerate(processes_data[:5]):
                print(f"  {i+1}. PID: {process['pid']}, 名称: {process['name']}, 状态: {process['status']}")
        else:
            print("进程信息为空")
    except (json.JSONDecodeError, TypeError):
        print("进程信息为空或格式不正确")
else:
    print("数据库中没有系统信息记录")

conn.close()