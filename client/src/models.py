import sqlite3
import os
from pathlib import Path
from src.config import DB_PATH
from src.logger import logger

class SystemInfo:
    """系统信息模型"""
    def __init__(self, hostname, ip_address, mac_address, services, processes, timestamp):
        self.hostname = hostname
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.services = services  # 存储为JSON字符串
        self.processes = processes  # 存储为JSON字符串
        self.timestamp = timestamp

class DatabaseManager:
    """数据库管理器"""
    def __init__(self):
        # 确保db_path是Path对象
        self.db_path = DB_PATH if isinstance(DB_PATH, Path) else Path(DB_PATH)
        self.init_db()
        self.migrate_database()

    def migrate_database(self):
        """迁移数据库结构"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否存在processes字段
            cursor.execute("PRAGMA table_info(system_info)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'processes' not in columns:
                # 添加processes字段
                cursor.execute("ALTER TABLE system_info ADD COLUMN processes TEXT")
                conn.commit()
                logger.info("数据库迁移成功：添加了processes字段")
            else:
                logger.info("数据库已包含processes字段，无需迁移")
            
            conn.close()
        except Exception as e:
            logger.error(f"数据库迁移失败: {e}")
            raise
    
    def init_db(self):
        """初始化数据库表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建系统信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hostname TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    mac_address TEXT NOT NULL,
                    services TEXT NOT NULL,
                    processes TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def save_system_info(self, system_info):
        """保存系统信息到数据库，并只保留最新的5条记录"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_info (hostname, ip_address, mac_address, services, processes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (system_info.hostname, system_info.ip_address, system_info.mac_address, 
                  system_info.services, system_info.processes, system_info.timestamp))
            
            # 先获取应该保留的记录ID，然后删除不在这个列表中的记录
            cursor.execute('SELECT id FROM system_info ORDER BY id DESC LIMIT 5')
            keep_ids = [str(row[0]) for row in cursor.fetchall()]
            
            if keep_ids:
                placeholders = ','.join('?' * len(keep_ids))
                cursor.execute(f'DELETE FROM system_info WHERE id NOT IN ({placeholders})', keep_ids)
            else:
                cursor.execute('DELETE FROM system_info')
            
            conn.commit()
            conn.close()
            logger.info("系统信息保存成功，已清理旧数据，只保留最新的5条记录")
        except Exception as e:
            logger.error(f"保存系统信息失败: {e}")
            raise
    
    def get_latest_system_info(self):
        """获取最新的系统信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT hostname, ip_address, mac_address, services, processes, timestamp
                FROM system_info
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                logger.info("成功获取最新系统信息")
                return SystemInfo(*result)
            logger.info("数据库中无系统信息记录")
            return None
        except Exception as e:
            logger.error(f"获取最新系统信息失败: {e}")
            return None
    
    def get_all_system_info(self):
        """获取所有系统信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT hostname, ip_address, mac_address, services, processes, timestamp
                FROM system_info
                ORDER BY timestamp DESC
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            logger.info(f"成功获取所有系统信息，共 {len(results)} 条记录")
            return [SystemInfo(*row) for row in results]
        except Exception as e:
            logger.error(f"获取所有系统信息失败: {e}")
            return []