import sys
import os
from typing import Optional

def get_application_path():
    """获取应用程序路径，兼容开发环境和打包环境"""
    is_frozen = hasattr(sys, 'frozen') and sys.frozen
    is_nuitka = '__compiled__' in globals()
    
    if is_frozen or is_nuitka:
        # 打包后的可执行文件路径
        application_path = os.path.dirname(sys.executable)
    elif '__compiled__' in globals():
        # Nuitka打包环境
        application_path = os.path.dirname(os.path.abspath(__file__))
    else:
        # 开发环境
        application_path = os.path.dirname(os.path.abspath(__file__))

    
    return application_path

# 添加项目根目录到Python路径
parent_dir = get_application_path()
sys.path.insert(0, parent_dir)

from src.utils.logger import logger
from src.core.app_controller import get_app_controller


def main():
    """主程序入口"""
    try:
        # 获取应用程序控制器实例
        app_controller = get_app_controller()
        
        # 初始化应用程序控制器
        if not app_controller.initialize():
            logger.error("应用程序初始化失败")
            # 添加延迟以便观察输出
            import time
            time.sleep(5)
            sys.exit(1)
        
        # 运行应用程序主循环
        app_controller.run()
        
    except KeyboardInterrupt:
        logger.info("接收到键盘中断信号")
    except Exception as e:
        logger.error(f"程序运行时发生未处理的异常: {e}")
    finally:
        logger.info("程序退出")

if __name__ == "__main__":
    main()