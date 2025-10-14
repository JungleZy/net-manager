import sqlite3
import os

def check_database_tables():
    db_path = r"e:\workspace\project\net-manager\server\net_manager_server.db"
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
            
        # 检查switch_info表结构
        if any(table[0] == 'switch_info' for table in tables):
            print("\nswitch_info表结构:")
            cursor.execute("PRAGMA table_info(switch_info);")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        else:
            print("\nswitch_info表不存在")
            
        # 检查device_info表结构
        if any(table[0] == 'device_info' for table in tables):
            print("\ndevice_info表结构:")
            cursor.execute("PRAGMA table_info(device_info);")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column[1]} ({column[2]})")
        else:
            print("\ndevice_info表不存在")
            
        # 检查switch_info表中的数据
        if any(table[0] == 'switch_info' for table in tables):
            print("\nswitch_info表中的数据:")
            cursor.execute("SELECT COUNT(*) FROM switch_info;")
            count = cursor.fetchone()[0]
            print(f"  总记录数: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM switch_info LIMIT 5;")
                rows = cursor.fetchall()
                print("  前5条记录:")
                for row in rows:
                    print(f"    {row}")
            else:
                print("  表为空")
                
        conn.close()
        
    except Exception as e:
        print(f"检查数据库时出错: {e}")

if __name__ == "__main__":
    check_database_tables()