#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
唯一标识符生成和管理模块
用于为每个客户端生成并持久化一个唯一标识符
"""

import os
import uuid
import json
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 状态文件名
STATE_FILE = "client_state.json"

def generate_unique_id():
    """
    生成一个唯一的UUID作为客户端标识符
    
    Returns:
        str: 生成的唯一标识符字符串
    """
    unique_id = str(uuid.uuid4())
    logger.debug(f"生成新的唯一标识符: {unique_id}")
    return unique_id

def save_unique_id(unique_id, app_path):
    """
    将唯一标识符保存到状态文件中
    
    Args:
        unique_id (str): 要保存的唯一标识符
        app_path (str): 应用程序路径
        
    Returns:
        bool: 保存成功返回True，否则返回False
    """
    try:
        # 构建状态文件路径
        state_file_path = os.path.join(app_path, STATE_FILE)
        
        # 如果状态文件已存在，读取现有内容
        state_data = {}
        if os.path.exists(state_file_path):
            try:
                with open(state_file_path, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
            except Exception as e:
                logger.warning(f"读取现有状态文件时出错: {e}")
        
        # 更新客户端ID
        state_data['client_id'] = unique_id
        
        # 写入状态文件
        with open(state_file_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"唯一标识符已保存到状态文件: {state_file_path}")
        return True
    except Exception as e:
        logger.error(f"保存唯一标识符失败: {e}")
        return False

def load_unique_id(app_path):
    """
    从状态文件中加载唯一标识符
    
    Args:
        app_path (str): 应用程序路径
        
    Returns:
        str: 加载的唯一标识符，如果失败则返回None
    """
    try:
        # 构建状态文件路径
        state_file_path = os.path.join(app_path, STATE_FILE)
        
        # 检查状态文件是否存在
        if not os.path.exists(state_file_path):
            logger.debug(f"状态文件不存在: {state_file_path}")
            return None
            
        # 读取状态文件
        with open(state_file_path, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
            
        # 获取客户端ID
        unique_id = state_data.get('client_id')
        if not unique_id:
            logger.debug(f"状态文件中未找到客户端ID")
            return None
            
        # 验证UUID格式
        uuid.UUID(unique_id)  # 如果不是有效的UUID格式会抛出异常
        
        logger.debug(f"从状态文件加载唯一标识符: {unique_id}")
        return unique_id
    except Exception as e:
        logger.error(f"加载唯一标识符失败: {e}")
        return None

def get_or_create_unique_id(app_path):
    """
    获取或创建唯一标识符
    如果状态文件中存在则加载，否则生成新的并保存
    
    Args:
        app_path (str): 应用程序路径
        
    Returns:
        str: 唯一标识符
    """
    # 尝试从状态文件加载现有的唯一标识符
    unique_id = load_unique_id(app_path)
    
    # 如果加载失败，则生成新的
    if not unique_id:
        unique_id = generate_unique_id()
        # 保存新生成的唯一标识符到状态文件
        if not save_unique_id(unique_id, app_path):
            logger.warning("无法保存新生成的唯一标识符")
    
    return unique_id