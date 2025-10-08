#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开发环境设置脚本
用于检查和安装项目所需的依赖项
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 虚拟环境目录
VENV_DIR = PROJECT_ROOT / "venv"

# requirements.txt文件路径
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

# Python版本要求
REQUIRED_PYTHON_VERSION = (3, 8)


def check_python_version():
    """检查Python版本是否满足要求"""
    current_version = sys.version_info[:2]
    if current_version < REQUIRED_PYTHON_VERSION:
        print(f"错误: 需要Python {REQUIRED_PYTHON_VERSION[0]}.{REQUIRED_PYTHON_VERSION[1]}或更高版本")
        print(f"当前Python版本: {current_version[0]}.{current_version[1]}")
        return False
    return True


def get_venv_python_path():
    """获取虚拟环境中的Python解释器路径"""
    system = platform.system().lower()
    if system == "windows":
        return VENV_DIR / "Scripts" / "python.exe"
    else:  # Unix/Linux
        return VENV_DIR / "bin" / "python"


def get_venv_pip_path():
    """获取虚拟环境中的pip路径"""
    system = platform.system().lower()
    if system == "windows":
        return VENV_DIR / "Scripts" / "pip.exe"
    else:  # Unix/Linux
        return VENV_DIR / "bin" / "pip"


def create_virtual_environment():
    """创建虚拟环境"""
    print("正在创建虚拟环境...")
    try:
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
        print("虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError:
        print("虚拟环境创建失败")
        return False


def install_requirements():
    """在虚拟环境中安装依赖项"""
    print("正在安装依赖项...")
    pip_path = get_venv_pip_path()
    
    try:
        subprocess.run([str(pip_path), "install", "-r", str(REQUIREMENTS_FILE)], check=True)
        print("依赖项安装成功")
        return True
    except subprocess.CalledProcessError:
        print("依赖项安装失败")
        return False


def main():
    """主函数"""
    print("开始设置开发环境...")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建虚拟环境
    if not create_virtual_environment():
        sys.exit(1)
    
    # 安装依赖项
    if not install_requirements():
        sys.exit(1)
    
    print("开发环境设置完成!")
    print(f"虚拟环境位置: {VENV_DIR}")
    print("激活虚拟环境:")
    system = platform.system().lower()
    if system == "windows":
        print(f"  {VENV_DIR}\\Scripts\\activate")
    else:  # Unix/Linux
        print(f"  source {VENV_DIR}/bin/activate")


if __name__ == "__main__":
    main()