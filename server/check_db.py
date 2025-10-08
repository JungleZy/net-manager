import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'net_manager_server.db')
print(f"数据库路径: {db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 查询所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('数据库中的表:')
for table in tables:
    print(f"  - {table[0]}")

# 查询switches表结构
print('\nswitches表结构:')
cursor.execute('PRAGMA table_info(switches)')
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col}")

# 查询system_info表结构
print('\nsystem_info表结构:')
cursor.execute('PRAGMA table_info(system_info)')
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col}")

conn.close()
print('\n检查完成')