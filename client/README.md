# NetManager Client

NetManager客户端负责收集系统信息并通过TCP连接发送到服务端。

## 目录结构

```
client/
├── src/
│   ├── config_module/     # 配置管理模块
│   ├── core/              # 核心模块
│   ├── exceptions/        # 异常处理模块
│   ├── network/           # 网络通信模块
│   ├── system/            # 系统信息收集模块
│   ├── utils/             # 工具模块
│   └── __init__.py
├── tests/                 # 测试文件
├── examples/              # 使用示例
└── main.py                # 主程序入口
```

## 网络模块说明

### TCP客户端 (src/network/tcp_client.py)

负责与服务端建立TCP连接并发送系统信息。

主要功能：
- 建立和维护TCP连接
- 发送系统信息到服务端
- 处理服务端命令
- 自动重连机制

### UDP客户端 (src/network/udp_client.py)

负责通过多播和广播方式发现服务端。

主要功能：
- 多播服务发现
- 广播服务发现
- 获取活跃网络接口列表

## 使用示例

### 服务发现和连接示例

```python
from src.network.udp_client import get_udp_client
from src.network.tcp_client import get_tcp_client

# 获取UDP客户端实例（用于服务发现）
udp_client = get_udp_client()

# 获取TCP客户端实例（用于数据传输）
tcp_client = get_tcp_client()

# 1. 使用多播方式发现服务端
server_address = udp_client.discover_server_multicast()

# 2. 如果多播方式失败，回退到广播方式
if server_address is None:
    server_address = udp_client.discover_server_broadcast()

# 3. 使用发现的服务端地址连接TCP客户端
if server_address and tcp_client.connect(server_address):
    # 4. 发送系统信息
    tcp_client.send_system_info()
    
    # 5. 断开连接
    tcp_client.disconnect()
```

详细示例请参考 [examples/service_discovery_example.py](examples/service_discovery_example.py)

## 测试

运行服务发现功能测试：

```bash
cd client
python -m tests.test_service_discovery
```