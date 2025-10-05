#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Net Manager 自动化打包脚本
支持分别对客户端和服务端进行Nuitka打包
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.resolve()
CLIENT_DIR = PROJECT_ROOT / "client"
SERVER_DIR = PROJECT_ROOT / "server"
DIST_DIR = PROJECT_ROOT / "dist"
VENV_DIR = PROJECT_ROOT / "venv"

def check_nuitka():
    """检查Nuitka是否已安装"""
    # 首先检查虚拟环境中的Nuitka
    if VENV_DIR.exists():
        try:
            if os.name == 'nt':  # Windows
                nuitka_path = VENV_DIR / "Scripts" / "python.exe"
            else:  # Unix/Linux/macOS
                nuitka_path = VENV_DIR / "bin" / "python"
            
            if nuitka_path.exists():
                subprocess.run([str(nuitka_path), "-m", "nuitka", "--version"], 
                              capture_output=True, check=True)
                print("✓ 虚拟环境中Nuitka已安装")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    
    # 然后尝试使用sys.executable
    try:
        subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                      capture_output=True, check=True)
        print("✓ Nuitka 已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # 在Windows上尝试使用py命令
            subprocess.run(["py", "-m", "nuitka", "--version"], 
                          capture_output=True, check=True)
            print("✓ Nuitka 已安装")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Nuitka 未安装，请先安装：pip install nuitka")
            return False

def _build_application(app_type, app_dir, output_dir, console_mode):
    """通用构建函数
    
    Args:
        app_type: 应用类型 ('client' 或 'server')
        app_dir: 应用目录
        output_dir: 输出目录
        console_mode: 控制台模式 ('hide' 或 'force')
    """
    print(f"开始打包{app_type}...")
    
    # 切换到应用目录
    os.chdir(app_dir)
    
    # 确定输出文件名和产品名称
    output_filename = f"net-manager-{app_type}"
    product_name = f"net-manager-{app_type}"
    
    # 获取项目版本
    version = "1.0.0"  # 默认版本
    
    # 构建命令
    # 首先尝试使用虚拟环境中的Python
    if VENV_DIR.exists():
        if os.name == 'nt':  # Windows
            python_path = VENV_DIR / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            python_path = VENV_DIR / "bin" / "python"
        
        if python_path.exists():
            cmd = [
                str(python_path), "-m", "nuitka",
                f"--output-filename={output_filename}", # 设置输出文件名
                f"--windows-product-name={product_name}",
                f"--product-version={version}",  # 产品版本
                f"--file-version={version}",    # 文件版本
                "--standalone",           # 独立模式
                "--onefile",              # 单文件
                "--static-libpython=no",  # 不静态链接Python库
                "--assume-yes-for-downloads",  # 自动下载必要的依赖
                "--enable-plugin=multiprocessing",  # 启用多进程插件
                "--follow-imports",       # 跟踪导入
                f"--output-dir={output_dir}",  # 输出目录
                f"--windows-console-mode={console_mode}",  # 控制台模式
                "--windows-uac-admin",  # 请求管理员权限
                "--include-package=src",   # 包含src包
                "--follow-imports",  # 跟踪导入的模块
                "--follow-stdlib",  # 优化标准库的处理
                "--python-flag=-O",  # Python优化模式
                "--lto=yes",  # 链接时优化
                "--noinclude-unittest-mode=allow",
                "--disable-ccache",  # 禁用编译缓存确保全新编译
                "--no-pyi-file",  # 不生成pyi文件
                "--remove-output",  # 构建完成后清理临时文件
                "main.py"                 # 入口文件
            ]
        else:
            # 如果虚拟环境中的Python不存在，回退到sys.executable
            cmd = [
                sys.executable, "-m", "nuitka",
                f"--output-filename={output_filename}", # 设置输出文件名
                f"--windows-product-name={product_name}",
                f"--product-version={version}",  # 产品版本
                f"--file-version={version}",    # 文件版本
                "--standalone",           # 独立模式
                "--onefile",              # 单文件
                "--static-libpython=no",  # 不静态链接Python库
                "--assume-yes-for-downloads",  # 自动下载必要的依赖
                "--enable-plugin=multiprocessing",  # 启用多进程插件
                "--follow-imports",       # 跟踪导入
                f"--output-dir={output_dir}",  # 输出目录
                f"--windows-console-mode={console_mode}",  # 控制台模式
                "--windows-uac-admin",  # 请求管理员权限
                "--include-package=src",   # 包含src包
                "--follow-imports",  # 跟踪导入的模块
                "--follow-stdlib",  # 优化标准库的处理
                "--python-flag=-O",  # Python优化模式
                "--lto=yes",  # 链接时优化
                "--noinclude-unittest-mode=allow",
                "--disable-ccache",  # 禁用编译缓存确保全新编译
                "--no-pyi-file",  # 不生成pyi文件
                "--remove-output",  # 构建完成后清理临时文件
                "main.py"                 # 入口文件
            ]
    else:
        # 如果没有虚拟环境，使用sys.executable
        cmd = [
            sys.executable, "-m", "nuitka",
            f"--output-filename={output_filename}", # 设置输出文件名
            f"--windows-product-name={product_name}",
            f"--product-version={version}",  # 产品版本
            f"--file-version={version}",    # 文件版本
            "--standalone",           # 独立模式
            "--onefile",              # 单文件
            "--static-libpython=no",  # 不静态链接Python库
            "--assume-yes-for-downloads",  # 自动下载必要的依赖
            "--enable-plugin=multiprocessing",  # 启用多进程插件
            "--follow-imports",       # 跟踪导入
            f"--output-dir={output_dir}",  # 输出目录
            f"--windows-console-mode={console_mode}",  # 控制台模式
            "--windows-uac-admin",  # 请求管理员权限
            "--include-package=src",   # 包含src包
            "--follow-imports",  # 跟踪导入的模块
            "--follow-stdlib",  # 优化标准库的处理
            "--python-flag=-O",  # Python优化模式
            "--lto=yes",  # 链接时优化
            "--noinclude-unittest-mode=allow",
            "--disable-ccache",  # 禁用编译缓存确保全新编译
            "--no-pyi-file",  # 不生成pyi文件
            "--remove-output",  # 构建完成后清理临时文件
            "main.py"                 # 入口文件
        ]
    
    # 如果sys.executable不可用，尝试使用py命令（Windows）
    if sys.executable == "" or not os.path.exists(sys.executable):
        cmd[0] = "py"
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {app_type}打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {app_type}打包失败: {e}")
        print(f"错误详情: {e.stderr}")
        return False

def build_client():
    """打包客户端"""
    return _build_application(
        app_type="client",
        app_dir=CLIENT_DIR,
        output_dir=str(DIST_DIR / "client"),
        console_mode="hide"
    )

def build_server():
    """打包服务端"""
    return _build_application(
        app_type="server",
        app_dir=SERVER_DIR,
        output_dir=str(DIST_DIR / "server"),
        console_mode="force"
    )

def copy_additional_files():
    """复制额外需要的文件"""
    print("复制额外文件...")
    
    # 创建日志目录
    client_log_dir = DIST_DIR / "client" / "logs"
    server_log_dir = DIST_DIR / "server" / "logs"
    client_log_dir.mkdir(parents=True, exist_ok=True)
    server_log_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制README等说明文件
    readme_files = ["README.md", "PACKAGING.md"]
    for readme in readme_files:
        src = PROJECT_ROOT / readme
        if src.exists():
            shutil.copy2(src, DIST_DIR / "client" / readme)
            shutil.copy2(src, DIST_DIR / "server" / readme)
    
    print("✓ 额外文件复制完成")

def ensure_virtual_environment():
    """确保虚拟环境存在并已安装必要的依赖"""
    if not VENV_DIR.exists():
        print("虚拟环境不存在，正在创建...")
        try:
            import venv
            venv.create(VENV_DIR, with_pip=True)
            print("✓ 虚拟环境创建成功")
        except Exception as e:
            print(f"✗ 创建虚拟环境时出错: {e}")
            return False
    
    # 检查是否已安装依赖
    try:
        if os.name == 'nt':  # Windows
            pip_path = VENV_DIR / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            pip_path = VENV_DIR / "bin" / "pip"
        
        if pip_path.exists():
            # 检查是否已安装Nuitka
            result = subprocess.run([str(pip_path), "show", "nuitka"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("正在安装Nuitka...")
                subprocess.run([str(pip_path), "install", "nuitka"], check=True)
                print("✓ Nuitka安装成功")
            
            # 检查是否已安装项目依赖
            result = subprocess.run([str(pip_path), "show", "psutil"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("正在安装项目依赖...")
                subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
                print("✓ 项目依赖安装成功")
            
            return True
        else:
            print("✗ 虚拟环境中的pip不存在")
            return False
    except Exception as e:
        print(f"✗ 检查或安装依赖时出错: {e}")
        return False

def create_run_scripts():
    """创建运行脚本"""
    print("创建运行脚本...")
    
    # 客户端运行脚本
    client_bat = DIST_DIR / "client" / "run_client.bat"
    with open(client_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %~dp0\n")
        f.write("main.exe\n")
        f.write("pause\n")
    
    # 服务端运行脚本
    server_bat = DIST_DIR / "server" / "run_server.bat"
    with open(server_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %~dp0\n")
        f.write("main.exe\n")
        f.write("pause\n")
    
    print("✓ 运行脚本创建完成")

def clean_build():
    """清理之前的构建"""
    print("清理之前的构建...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
        print("✓ 清理完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Net Manager 打包脚本")
    parser.add_argument("--client", action="store_true", help="仅打包客户端")
    parser.add_argument("--server", action="store_true", help="仅打包服务端")
    parser.add_argument("--clean", action="store_true", help="清理之前的构建")
    parser.add_argument("--no-venv", action="store_true", help="不使用虚拟环境")
    
    args = parser.parse_args()
    
    # 如果不是指定不使用虚拟环境，则确保虚拟环境存在
    if not args.no_venv:
        print("检查虚拟环境...")
        if not ensure_virtual_environment():
            print("✗ 虚拟环境准备失败")
            sys.exit(1)
    
    # 检查Nuitka
    if not check_nuitka():
        sys.exit(1)
    
    # 清理之前的构建
    if args.clean:
        clean_build()
    
    # 创建输出目录
    DIST_DIR.mkdir(exist_ok=True)
    
    # 确定要打包的目标
    build_client_flag = args.client or (not args.client and not args.server)
    build_server_flag = args.server or (not args.client and not args.server)
    
    success = True
    
    # 打包客户端
    if build_client_flag:
        if not build_client():
            success = False
    
    # 打包服务端
    if build_server_flag:
        if not build_server():
            success = False
    
    if success:
        # 复制额外文件
        copy_additional_files()
        
        # 创建运行脚本
        create_run_scripts()
        
        print("\n" + "="*50)
        print("打包完成!")
        print("="*50)
        print(f"客户端输出目录: {DIST_DIR / 'client'}")
        print(f"服务端输出目录: {DIST_DIR / 'server'}")
        print("\n使用说明:")
        print("1. 客户端运行:")
        print(f"   cd {DIST_DIR / 'client'}")
        print("   run_client.bat 或 main.exe")
        print("\n2. 服务端运行:")
        print(f"   cd {DIST_DIR / 'server'}")
        print("   run_server.bat 或 main.exe")
    else:
        print("\n打包过程中出现错误，请检查上面的错误信息。")
        sys.exit(1)

if __name__ == "__main__":
    main()