#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Net Manager 开发环境设置脚本
"""

import os
import sys
import subprocess
import venv

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"警告: 当前Python版本为 {version.major}.{version.minor}.{version.micro}")
        print("建议使用Python 3.7或更高版本")
        return False
    return True

def create_virtual_environment():
    """创建虚拟环境"""
    venv_dir = "venv"
    if os.path.exists(venv_dir):
        print("虚拟环境已存在")
        return True
    
    print("正在创建虚拟环境...")
    try:
        venv.create(venv_dir, with_pip=True)
        print("虚拟环境创建成功")
        return True
    except Exception as e:
        print(f"创建虚拟环境失败: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    try:
        # 在虚拟环境中安装依赖
        if os.name == 'nt':  # Windows
            pip_path = os.path.join("venv", "Scripts", "pip")
        else:  # Unix/Linux/macOS
            pip_path = os.path.join("venv", "bin", "pip")
        
        result = subprocess.run([pip_path, "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("依赖安装成功")
            return True
        else:
            print(f"依赖安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"安装依赖时出错: {e}")
        return False

def main():
    """主函数"""
    print("Net Manager 开发环境设置")
    print("=" * 30)
    
    # 检查Python版本
    if not check_python_version():
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            return
    
    # 创建虚拟环境
    if not create_virtual_environment():
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    print("\n开发环境设置完成!")
    print("\n使用说明:")
    print("1. 激活虚拟环境:")
    if os.name == 'nt':  # Windows
        print("   .\\venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("2. 运行程序:")
    print("   python main.py")
    
    print("\n提示: 运行测试:")
    print("   python -m tests.test_system_collector")

if __name__ == "__main__":
    main()