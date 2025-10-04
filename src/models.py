import sqlite3
import os
from src.config import DB_PATH
from src.logger import logger

class SystemInfo:
    """系统信息模型"""
    def __init__(self, hostname, ip_address, mac_address, services, timestamp):
        self.hostname = hostname
        self.ip_address = ip_address
        self.mac_address = mac_address
        self.services = services  # 存储为JSON字符串
        self.timestamp = timestamp

class DatabaseManager:
    """数据库管理器"""
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()
    
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
        """保存系统信息到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO system_info (hostname, ip_address, mac_address, services, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (system_info.hostname, system_info.ip_address, system_info.mac_address, 
                  system_info.services, system_info.timestamp))
            
            conn.commit()
            conn.close()
            logger.info("系统信息保存成功")
        except Exception as e:
            logger.error(f"保存系统信息失败: {e}")
            raise
    
    def get_latest_system_info(self):
        """获取最新的系统信息"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT hostname, ip_address, mac_address, services, timestamp
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
                SELECT hostname, ip_address, mac_address, services, timestamp
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