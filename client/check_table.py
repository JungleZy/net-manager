import sqlite3

# 连接到数据库
conn = sqlite3.connect('net_manager.db')
cursor = conn.cursor()

# 查询表结构
cursor.execute("PRAGMA table_info(system_info)")

columns = cursor.fetchall()
print("当前system_info表结构:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

conn.close()