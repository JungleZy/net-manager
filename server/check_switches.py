import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'net_manager_server.db')
print(f"数据库路径: {db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询switches表中的数据
cursor.execute("SELECT * FROM switches")
rows = cursor.fetchall()

if rows:
    print(f"\n交换机配置数据 ({len(rows)} 条记录):")
    print("-" * 50)
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"IP: {row[1]}")
        print(f"SNMP版本: {row[2]}")
        print(f"Community: {row[3]}")
        print(f"User: {row[4]}")
        print(f"Auth Key: {row[5]}")
        print(f"Auth Protocol: {row[6]}")
        print(f"Priv Key: {row[7]}")
        print(f"Priv Protocol: {row[8]}")
        print(f"Description: {row[9]}")
        print(f"Created At: {row[10]}")
        print(f"Updated At: {row[11]}")
        print("-" * 50)
else:
    print("\n交换机配置数据: 无记录")

conn.close()
print('\n检查完成')