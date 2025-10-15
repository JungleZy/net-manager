#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NetManager客户端主程序入口
负责初始化应用、启动核心组件和处理程序退出
"""

import sys
import os
import signal
from typing import Optional

# 第三方库导入
# 无

# 本地应用/库导入


def get_app_path() -> str:
    """
    获取应用路径

    Returns:
        str: 应用路径
    """
    is_frozen = getattr(sys, "frozen", False)
    is_nuitka = "__compiled__" in globals()
    if is_frozen or is_nuitka:
        # 如果是打包后的可执行文件
        # Linux下使用argv[0]避免Nuitka onefile的临时目录问题
        if os.name != "nt":
            app_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        else:
            app_path = os.path.dirname(sys.executable)
    else:
        # 如果是Python脚本
        app_path = os.path.dirname(os.path.abspath(__file__))
    return app_path


def main() -> int:
    """
    主程序入口

    Returns:
        int: 程序退出码，0表示正常退出，非0表示异常退出
    """

    # 在任何其他初始化之前，首先尝试获取锁
    try:
        from src.utils.singleton_manager import get_client_singleton_manager

        singleton_manager = get_client_singleton_manager()
        if not singleton_manager.acquire_lock():
            print("NetManager客户端已在运行中，请勿重复启动")
            print("如果您确定没有其他实例在运行，请手动删除锁文件或重启系统")
            return 1
    except Exception as e:
        print(f"获取客户端锁时发生错误: {e}")
        print("请检查系统权限或依赖库是否正确安装")
        return 1

    # 初始化状态管理器
    try:
        from src.core.state_manager import get_state_manager

        state_manager = get_state_manager()
        state_manager.get_client_id()
    except Exception as e:
        print(f"状态控制器初始化失败: {e}")
        return 1

    # 添加项目根目录到Python路径
    app_path = get_app_path()
    if app_path not in sys.path:
        sys.path.insert(0, app_path)

    # 获取日志记录器
    from src.utils.logger import get_logger

    logger = get_logger()
    logger.info("NetManager客户端启动")

    try:
        # 获取应用控制器实例
        from src.core.app_controller import get_app_controller

        app_controller = get_app_controller()

        # 注册信号处理器
        def signal_handler(signum, frame):
            logger.info(f"收到信号 {signum}，准备退出...")
            app_controller.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 启动应用
        logger.info("启动应用控制器...")
        app_controller.start()

        # 等待应用结束，但允许响应中断信号
        try:
            app_controller.wait()
        except KeyboardInterrupt:
            logger.info("用户中断程序")
            app_controller.stop()

        logger.info("NetManager客户端正常退出")
        return 0

    except KeyboardInterrupt:
        logger.info("用户中断程序")
        return 0
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
