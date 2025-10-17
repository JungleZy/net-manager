#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
网络管理工具构建脚本
支持客户端和服务端的打包构建
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
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
DIST_DIR = PROJECT_ROOT / "dist"
VENV_DIR = PROJECT_ROOT / "venv"

# Nuitka构建选项常量
NUITKA_STATIC_LIBPYTHON_NO = "--static-libpython=no"  # 不静态链接Python库
NUITKA_ASSUME_YES_FOR_DOWNLOADS = "--assume-yes-for-downloads"  # 自动下载必要的依赖
NUITKA_ENABLE_PLUGIN_MULTIPROCESSING = (
    "--enable-plugin=multiprocessing"  # 启用多进程插件
)
NUITKA_FOLLOW_IMPORTS = "--follow-imports"  # 跟踪导入
NUITKA_WINDOWS_UAC_ADMIN = "--windows-uac-admin"  # 请求管理员权限
NUITKA_INCLUDE_PACKAGE = "--include-package=src"  # 包含src包
NUITKA_FOLLOW_STDLIB = "--follow-stdlib"  # 优化标准库的处理
NUITKA_PYTHON_FLAG_O = "--python-flag=-O"  # Python优化模式
NUITKA_LTO_YES = "--lto=yes"  # 链接时优化
NUITKA_NOINCLUDE_UNITTEST_MODE_ALLOW = "--noinclude-unittest-mode=allow"
NUITKA_DISABLE_CCACHE = "--disable-ccache"  # 禁用编译缓存确保全新编译
NUITKA_NO_PYI_FILE = "--no-pyi-file"  # 不生成pyi文件
NUITKA_REMOVE_OUTPUT = "--remove-output"  # 构建完成后清理临时文件


def check_compiler():
    """检查可用的C编译器并返回推荐的编译器选项"""
    if os.name == "nt":  # Windows系统使用默认编译器
        return None

    # 检查clang是否可用
    clang_available = False
    try:
        result = subprocess.run(["clang", "--version"], capture_output=True, check=True)
        clang_available = True
        print("✓ clang 编译器可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # 检查gcc是否可用
    gcc_available = False
    try:
        result = subprocess.run(["gcc", "--version"], capture_output=True, check=True)
        gcc_available = True
        print("✓ gcc 编译器可用")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    if not gcc_available and not clang_available:
        print("\n" + "=" * 60)
        print("✗ 错误: 未找到可用的C编译器")
        print("=" * 60)
        print("在Linux下使用Nuitka需要安装C编译器。")
        print("\n请根据您的Linux发行版执行以下命令安装：")
        print("\n  Ubuntu/Debian系统:")
        print("    sudo apt update")
        print("    sudo apt install gcc clang")
        print("\n  CentOS/RHEL/Fedora系统:")
        print("    sudo dnf install gcc clang")
        print("\n  Arch Linux:")
        print("    sudo pacman -S gcc clang")
        print("=" * 60 + "\n")
        return False

    # 优先推荐使用clang（更稳定，较少崩溃）
    if clang_available:
        print("ℹ 将使用 clang 编译器（推荐，更稳定）")
        return "--clang"
    else:
        print("ℹ 将使用 gcc 编译器")
        print("  提示：如果遇到编译器崩溃问题，建议安装clang编译器")
        return None


def check_patchelf():
    """检查Linux系统是否安装了patchelf"""
    if os.name == "nt":  # Windows系统不需要patchelf
        return True

    try:
        subprocess.run(["patchelf", "--version"], capture_output=True, check=True)
        print("✓ patchelf 已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n" + "=" * 60)
        print("✗ 错误: 未安装 patchelf")
        print("=" * 60)
        print("在Linux下使用Nuitka standalone模式需要安装patchelf工具。")
        print("\n请根据您的Linux发行版执行以下命令安装：")
        print("\n  Ubuntu/Debian系统:")
        print("    sudo apt update")
        print("    sudo apt install patchelf")
        print("\n  CentOS/RHEL/Fedora系统:")
        print("    sudo dnf install patchelf")
        print("    或")
        print("    sudo yum install patchelf")
        print("\n  Arch Linux:")
        print("    sudo pacman -S patchelf")
        print("=" * 60 + "\n")
        return False


def check_nuitka():
    """检查Nuitka是否已安装"""
    # 首先检查虚拟环境中的Nuitka
    if VENV_DIR.exists():
        try:
            if os.name == "nt":  # Windows
                nuitka_path = VENV_DIR / "Scripts" / "python.exe"
            else:  # Unix/Linux/macOS
                nuitka_path = VENV_DIR / "bin" / "python"

            if nuitka_path.exists():
                subprocess.run(
                    [str(nuitka_path), "-m", "nuitka", "--version"],
                    capture_output=True,
                    check=True,
                )
                print("✓ 虚拟环境中Nuitka已安装")
                return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # 然后尝试使用sys.executable
    try:
        subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            check=True,
        )
        print("✓ Nuitka 已安装")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            # 在Windows上尝试使用py命令
            subprocess.run(
                ["py", "-m", "nuitka", "--version"], capture_output=True, check=True
            )
            print("✓ Nuitka 已安装")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Nuitka 未安装，请先安装：pip install nuitka")
            return False


def _build_application(
    app_type, app_dir, output_dir, console_mode, compiler_option=None
):
    """通用构建函数

    Args:
        app_type: 应用类型 ('client' 或 'server')
        app_dir: 应用目录
        output_dir: 输出目录
        console_mode: 控制台模式 ('hide' 或 'force')
        compiler_option: 编译器选项 (如 '--clang')
    """
    print(f"开始打包{app_type}...")

    # 切换到应用目录
    os.chdir(app_dir)

    # 确定输出文件名和产品名称
    output_filename = f"net-manager-{app_type}"
    product_name = f"net-manager-{app_type}"

    # 获取项目版本
    version = "1.0.0"  # 默认版本

    # 使用虚拟环境中的Python
    python_path = sys.executable  # 默认使用系统Python

    if VENV_DIR.exists():
        if os.name == "nt":  # Windows
            venv_python = VENV_DIR / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            venv_python = VENV_DIR / "bin" / "python"

        if venv_python.exists():
            python_path = str(venv_python)

    cmd = [
        python_path,
        "-m",
        "nuitka",
        f"--output-filename={output_filename}",  # 设置输出文件名
        f"--windows-product-name={product_name}",
        f"--product-version={version}",  # 产品版本
        f"--file-version={version}",  # 文件版本
        f"--output-dir={output_dir}",  # 输出目录
        f"--windows-console-mode={console_mode}",  # 控制台模式
        "--standalone",  # 独立模式
        "--onefile",  # 单文件
        NUITKA_STATIC_LIBPYTHON_NO,  # 不静态链接Python库
        NUITKA_ASSUME_YES_FOR_DOWNLOADS,  # 自动下载必要的依赖
        NUITKA_ENABLE_PLUGIN_MULTIPROCESSING,  # 启用多进程插件
        NUITKA_FOLLOW_IMPORTS,  # 跟踪导入
        NUITKA_WINDOWS_UAC_ADMIN,  # 请求管理员权限
        NUITKA_INCLUDE_PACKAGE,  # 包含src包
        NUITKA_FOLLOW_STDLIB,  # 优化标准库的处理
        NUITKA_PYTHON_FLAG_O,  # Python优化模式
        NUITKA_LTO_YES,  # 链接时优化
        NUITKA_NOINCLUDE_UNITTEST_MODE_ALLOW,
        NUITKA_DISABLE_CCACHE,  # 禁用编译缓存确保全新编译
        NUITKA_NO_PYI_FILE,  # 不生成pyi文件
        NUITKA_REMOVE_OUTPUT,  # 构建完成后清理临时文件
    ]

    # 如果是server，需要包含static目录
    if app_type == "server":
        static_dir = app_dir / "static"
        if static_dir.exists():
            cmd.append(f"--include-data-dir={static_dir}=static")
            print(f"✓ 包含静态文件目录: {static_dir}")
        else:
            print(f"⚠ 警告: 静态文件目录不存在: {static_dir}")

    # 如果指定了编译器选项，添加到命令中
    if compiler_option:
        cmd.append(compiler_option)

    # 添加入口文件
    cmd.append("main.py")

    # 如果sys.executable不可用，尝试使用py命令（Windows）
    if sys.executable == "" or not os.path.exists(sys.executable):
        cmd[0] = "py"

    print(f"执行命令: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {app_type}打包成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {app_type}打包失败: {e}")
        print(f"错误详情: {e.stderr}")
        return False


# 全局变量存储编译器选项
_compiler_option = None


def build_client():
    """打包客户端"""
    return _build_application(
        app_type="client",
        app_dir=CLIENT_DIR,
        output_dir=str(DIST_DIR / "client"),
        console_mode="hide",
        compiler_option=_compiler_option,
    )


def build_dashboard():
    """打包前端控制面板"""
    print("开始打包前端控制面板...")

    # 检查dashboard目录是否存在
    if not DASHBOARD_DIR.exists():
        print(f"✗ Dashboard目录不存在: {DASHBOARD_DIR}")
        return False

    # 检查package.json是否存在
    package_json = DASHBOARD_DIR / "package.json"
    if not package_json.exists():
        print(f"✗ package.json不存在: {package_json}")
        return False

    # 切换到dashboard目录
    original_dir = os.getcwd()
    os.chdir(DASHBOARD_DIR)

    try:
        # 检查node_modules是否存在，如果不存在则安装依赖
        node_modules = DASHBOARD_DIR / "node_modules"
        if not node_modules.exists():
            print("正在安装前端依赖...")
            # 检测npm或pnpm或yarn
            npm_cmd = None
            for cmd in ["pnpm", "npm", "yarn"]:
                try:
                    subprocess.run([cmd, "--version"], capture_output=True, check=True)
                    npm_cmd = cmd
                    print(f"✓ 找到包管理器: {cmd}")
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue

            if not npm_cmd:
                print("✗ 未找到npm/pnpm/yarn，请先安装Node.js和包管理器")
                return False

            # 安装依赖
            install_cmd = [npm_cmd, "install"]
            subprocess.run(install_cmd, check=True)
            print("✓ 前端依赖安装完成")

        # 执行构建
        print("正在构建前端项目...")
        npm_cmd = None
        for cmd in ["pnpm", "npm", "yarn"]:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, check=True)
                npm_cmd = cmd
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        build_cmd = [npm_cmd, "run", "build"]
        subprocess.run(build_cmd, check=True)
        print("✓ 前端构建完成")

        # 检查构建产物
        dist_dir = DASHBOARD_DIR / "dist"
        if not dist_dir.exists():
            print(f"✗ 构建产物不存在: {dist_dir}")
            return False

        # 移动构建产物到server/static目录
        server_static_dir = SERVER_DIR / "static"
        if server_static_dir.exists():
            print(f"清理旧的静态文件目录: {server_static_dir}")
            shutil.rmtree(server_static_dir)

        print(f"复制构建产物到: {server_static_dir}")
        shutil.copytree(dist_dir, server_static_dir)
        print("✓ 前端构建产物已复制到server/static目录")

        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ 前端打包失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 打包前端时发生错误: {e}")
        return False
    finally:
        # 恢复原始工作目录
        os.chdir(original_dir)


def build_server():
    """打包服务端"""
    # 在打包server之前先打包dashboard
    print("\n" + "=" * 50)
    print("步骤1: 打包前端控制面板")
    print("=" * 50)
    if not build_dashboard():
        print("✗ 前端打包失败，无法继续打包服务端")
        return False

    print("\n" + "=" * 50)
    print("步骤2: 打包服务端")
    print("=" * 50)
    return _build_application(
        app_type="server",
        app_dir=SERVER_DIR,
        output_dir=str(DIST_DIR / "server"),
        console_mode="force",
        compiler_option=_compiler_option,
    )


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
        if os.name == "nt":  # Windows
            pip_path = VENV_DIR / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            pip_path = VENV_DIR / "bin" / "pip"

        if pip_path.exists():
            # 检查是否已安装Nuitka
            result = subprocess.run(
                [str(pip_path), "show", "nuitka"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print("正在安装Nuitka...")
                subprocess.run([str(pip_path), "install", "nuitka"], check=True)
                print("✓ Nuitka安装成功")

            # 检查是否已安装项目依赖
            result = subprocess.run(
                [str(pip_path), "show", "psutil"], capture_output=True, text=True
            )
            if result.returncode != 0:
                print("正在安装项目依赖...")
                subprocess.run(
                    [str(pip_path), "install", "-r", "requirements.txt"], check=True
                )
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
        f.write("net-manager-client.exe\n")
        f.write("pause\n")

    # 客户端开机自启动脚本
    client_autostart_bat = DIST_DIR / "client" / "enable_autostart.bat"
    with open(client_autostart_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %~dp0\n")
        f.write("net-manager-client.exe --enable-autostart\n")
        f.write("pause\n")

    # 客户端禁用开机自启动脚本
    client_disable_autostart_bat = DIST_DIR / "client" / "disable_autostart.bat"
    with open(client_disable_autostart_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %~dp0\n")
        f.write("net-manager-client.exe --disable-autostart\n")
        f.write("pause\n")

    # 客户端守护进程脚本
    client_daemon_bat = DIST_DIR / "client" / "create_daemon.bat"
    with open(client_daemon_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %~dp0\n")
        f.write("net-manager-client.exe --create-daemon\n")
        f.write("pause\n")

    # 客户端禁用守护进程脚本
    client_disable_daemon_bat = DIST_DIR / "client" / "disable_daemon.bat"
    with open(client_disable_daemon_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %~dp0\n")
        f.write("net-manager-client.exe --disable-daemon\n")
        f.write("pause\n")

    # 服务端运行脚本
    server_bat = DIST_DIR / "server" / "run_server.bat"
    with open(server_bat, "w", encoding="utf-8") as f:
        f.write("@echo off\n")
        f.write("cd /d %~dp0\n")
        f.write("net-manager-server.exe\n")
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
    global _compiler_option

    parser = argparse.ArgumentParser(description="Net Manager 打包脚本")
    parser.add_argument("--client", action="store_true", help="仅打包客户端")
    parser.add_argument("--server", action="store_true", help="仅打包服务端")

    args = parser.parse_args()

    # 如果不是指定不使用虚拟环境，则确保虚拟环境存在
    print("检查虚拟环境...")
    if not ensure_virtual_environment():
        print("✗ 虚拟环境准备失败")
        sys.exit(1)

    # 检查Nuitka
    if not check_nuitka():
        sys.exit(1)

    # 检查patchelf (仅Linux系统需要)
    if not check_patchelf():
        sys.exit(1)

    # 检查编译器并获取推荐的编译器选项
    print("检查C编译器...")
    compiler_result = check_compiler()
    if compiler_result is False:
        sys.exit(1)
    _compiler_option = compiler_result

    # 清理之前的构建
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
        print("\n" + "=" * 50)
        print("打包完成!")
        print("=" * 50)
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
