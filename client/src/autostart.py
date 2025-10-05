#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开机自启动和守护进程功能模块
支持Windows和Linux双平台
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from src.logger import logger


def get_platform():
    """获取当前操作系统平台"""
    return platform.system().lower()


def is_windows():
    """检查是否为Windows系统"""
    return get_platform() == 'windows'


def is_linux():
    """检查是否为Linux系统"""
    return get_platform() == 'linux'


def get_executable_path():
    """获取可执行文件路径"""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_client_executable_path():
    """获取客户端可执行文件路径"""
    # 如果是打包后的exe文件，返回exe文件路径
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件路径
        return sys.executable
    else:
        # 开发环境下的脚本路径
        return os.path.abspath(sys.argv[0])


def enable_autostart():
    """启用开机自启动"""
    try:
        if is_windows():
            return _enable_autostart_windows()
        elif is_linux():
            return _enable_autostart_linux()
        else:
            logger.error(f"不支持的操作系统平台: {get_platform()}")
            return False
    except Exception as e:
        logger.error(f"启用开机自启动时出错: {e}")
        return False


def disable_autostart():
    """禁用开机自启动"""
    try:
        if is_windows():
            return _disable_autostart_windows()
        elif is_linux():
            return _disable_autostart_linux()
        else:
            logger.error(f"不支持的操作系统平台: {get_platform()}")
            return False
    except Exception as e:
        logger.error(f"禁用开机自启动时出错: {e}")
        return False


def is_autostart_enabled():
    """检查是否已启用开机自启动"""
    try:
        if is_windows():
            return _is_autostart_enabled_windows()
        elif is_linux():
            return _is_autostart_enabled_linux()
        else:
            logger.error(f"不支持的操作系统平台: {get_platform()}")
            return False
    except Exception as e:
        logger.error(f"检查开机自启动状态时出错: {e}")
        return False


def _enable_autostart_windows():
    """Windows平台启用开机自启动"""
    try:
        # 使用启动文件夹方式实现开机自启动
        import winreg
        
        # 获取当前用户的启动文件夹路径
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        
        # 确保启动文件夹存在
        startup_folder.mkdir(parents=True, exist_ok=True)
        
        # 获取客户端可执行文件路径
        client_exe_path = get_client_executable_path()
        
        # 如果是打包后的exe文件，创建快捷方式
        # 只在打包环境下执行开机自启动和守护进程功能
        # 检查是否处于打包环境（Nuitka或PyInstaller）
        is_frozen = hasattr(sys, 'frozen') and sys.frozen
        is_nuitka = '__compiled__' in globals()
        
        if is_frozen or is_nuitka:
            # 创建快捷方式
            try:
                import win32com.client
                shortcut_path = startup_folder / "NetManager.lnk"
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))
                shortcut.Targetpath = client_exe_path
                shortcut.WorkingDirectory = os.path.dirname(client_exe_path)
                shortcut.WindowStyle = 1  # 正常窗口
                shortcut.save()
                
                logger.info(f"已创建开机启动快捷方式: {shortcut_path}")
            except ImportError:
                # 如果没有安装pywin32，则回退到创建批处理文件
                bat_path = startup_folder / "start_net_manager.bat"
                with open(bat_path, 'w', encoding='utf-8') as f:
                    f.write("@echo off\n")
                    f.write("cd /d %~dp0\n")
                    f.write(f'"{client_exe_path}"\n')
                
                logger.info(f"已创建开机启动批处理文件: {bat_path}")
        else:
            # 开发环境下，创建Python脚本启动文件
            bat_path = startup_folder / "start_net_manager.bat"
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write("@echo off\n")
                f.write("cd /d %~dp0\n")
                f.write(f'python "{client_exe_path}"\n')
            
            logger.info(f"已创建开机启动批处理文件: {bat_path}")
        
        return True
    except Exception as e:
        logger.error(f"Windows平台启用开机自启动时出错: {e}")
        return False


def _disable_autostart_windows():
    """Windows平台禁用开机自启动"""
    try:
        # 获取当前用户的启动文件夹路径
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        
        # 删除快捷方式文件
        shortcut_path = startup_folder / "NetManager.lnk"
        if shortcut_path.exists():
            shortcut_path.unlink()
            logger.info(f"已删除开机启动快捷方式: {shortcut_path}")
        
        # 删除批处理文件（兼容旧版本）
        bat_path = startup_folder / "start_net_manager.bat"
        if bat_path.exists():
            bat_path.unlink()
            logger.info(f"已删除开机启动批处理文件: {bat_path}")
        
        return True
    except Exception as e:
        logger.error(f"Windows平台禁用开机自启动时出错: {e}")
        return False


def _is_autostart_enabled_windows():
    """Windows平台检查是否已启用开机自启动"""
    try:
        # 获取当前用户的启动文件夹路径
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        
        # 检查快捷方式是否存在
        shortcut_path = startup_folder / "NetManager.lnk"
        if shortcut_path.exists():
            return True
        
        # 如果快捷方式不存在，检查批处理文件是否存在（兼容旧版本）
        bat_path = startup_folder / "start_net_manager.bat"
        return bat_path.exists()
    except Exception as e:
        logger.error(f"Windows平台检查开机自启动状态时出错: {e}")
        return False


def _enable_autostart_linux():
    """Linux平台启用开机自启动"""
    try:
        # 使用systemd服务方式实现开机自启动
        service_name = "net-manager-client.service"
        service_file_path = f"/etc/systemd/system/{service_name}"
        
        # 获取客户端可执行文件路径
        client_exe_path = get_client_executable_path()
        
        # 创建systemd服务文件内容
        service_content = f"""[Unit]
Description=Net Manager Client
After=network.target

[Service]
Type=simple
ExecStart={client_exe_path}
WorkingDirectory={get_executable_path()}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        # 由于需要root权限，我们先创建临时文件
        temp_service_file = "/tmp/net-manager-client.service"
        with open(temp_service_file, 'w') as f:
            f.write(service_content)
        
        # 使用sudo命令复制服务文件到系统目录
        try:
            subprocess.run(['sudo', 'cp', temp_service_file, service_file_path], check=True)
            subprocess.run(['sudo', 'chmod', '644', service_file_path], check=True)
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            subprocess.run(['sudo', 'systemctl', 'enable', service_name], check=True)
            logger.info(f"已创建并启用systemd服务: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Linux平台启用开机自启动时出错: {e}")
            return False
    except Exception as e:
        logger.error(f"Linux平台启用开机自启动时出错: {e}")
        return False


def _disable_autostart_linux():
    """Linux平台禁用开机自启动"""
    try:
        service_name = "net-manager-client.service"
        service_file_path = f"/etc/systemd/system/{service_name}"
        
        # 禁用并删除服务
        try:
            subprocess.run(['sudo', 'systemctl', 'disable', service_name], check=True)
            subprocess.run(['sudo', 'rm', '-f', service_file_path], check=True)
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            logger.info(f"已禁用并删除systemd服务: {service_name}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Linux平台禁用开机自启动时出错: {e}")
            return False
    except Exception as e:
        logger.error(f"Linux平台禁用开机自启动时出错: {e}")
        return False


def _is_autostart_enabled_linux():
    """Linux平台检查是否已启用开机自启动"""
    try:
        service_name = "net-manager-client.service"
        # 检查服务是否已启用
        result = subprocess.run(['systemctl', 'is-enabled', service_name], 
                               capture_output=True, text=True)
        return result.returncode == 0 and 'enabled' in result.stdout
    except Exception as e:
        logger.error(f"Linux平台检查开机自启动状态时出错: {e}")
        return False


def create_daemon_script():
    """创建守护进程脚本"""
    try:
        if is_windows():
            return _create_daemon_script_windows()
        elif is_linux():
            return _create_daemon_script_linux()
        else:
            logger.error(f"不支持的操作系统平台: {get_platform()}")
            return False
    except Exception as e:
        logger.error(f"创建守护进程脚本时出错: {e}")
        return False


def _create_daemon_script_windows():
    """Windows平台创建守护进程脚本"""
    try:
        # 创建守护进程批处理脚本
        script_path = Path(get_executable_path()) / "net_manager_daemon.bat"
        client_exe_path = get_client_executable_path()
        
        script_content = f"""@echo off
REM Net Manager 守护进程脚本

:loop
tasklist | find /i "{os.path.basename(client_exe_path)}" >nul
if %errorlevel%==1 (
    echo Net Manager 客户端未运行，正在启动...
    start "" "{client_exe_path}"
) else (
    echo Net Manager 客户端正在运行
)

REM 等待60秒后再次检查
timeout /t 60 /nobreak >nul
goto loop
"""
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"已创建Windows守护进程脚本: {script_path}")
        return True
    except Exception as e:
        logger.error(f"Windows平台创建守护进程脚本时出错: {e}")
        return False


def _create_daemon_script_linux():
    """Linux平台创建守护进程脚本"""
    try:
        # 创建守护进程shell脚本
        script_path = Path(get_executable_path()) / "net_manager_daemon.sh"
        client_exe_path = get_client_executable_path()
        
        script_content = f"""#!/bin/bash
# Net Manager 守护进程脚本

while true; do
    if ! pgrep -f "{os.path.basename(client_exe_path)}" > /dev/null; then
        echo "Net Manager 客户端未运行，正在启动..."
        nohup {client_exe_path} > /dev/null 2>&1 &
    else
        echo "Net Manager 客户端正在运行"
    fi
    
    # 等待60秒后再次检查
    sleep 60
done
"""
        
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # 添加执行权限
        os.chmod(script_path, 0o755)
        
        logger.info(f"已创建Linux守护进程脚本: {script_path}")
        return True
    except Exception as e:
        logger.error(f"Linux平台创建守护进程脚本时出错: {e}")
        return False


if __name__ == "__main__":
    # 测试代码
    print("当前平台:", get_platform())
    print("是否为Windows:", is_windows())
    print("是否为Linux:", is_linux())
    print("客户端可执行文件路径:", get_client_executable_path())