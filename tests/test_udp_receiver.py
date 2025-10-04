import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.udp_receiver import udp_receiver

if __name__ == "__main__":
    udp_receiver()