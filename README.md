# Net Manager

Net Manager 是一个网络信息收集和监控工具，可以收集系统的主机名、IP地址、MAC地址和服务信息，并将这些信息保存到SQLite数据库中，同时通过UDP协议发送到指定的服务器。

## 功能特性

- 收集系统信息（主机名、IP地址、MAC地址、服务列表）
- 将收集的信息保存到SQLite数据库
- 通过UDP协议将信息发送到指定服务器
- 完善的日志记录功能
- 支持优雅关闭（处理SIGINT和SIGTERM信号）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

配置文件位于 `config.py`，可以修改以下参数：

- `UDP_HOST`: UDP服务器地址
- `UDP_PORT`: UDP服务器端口
- `DB_PATH`: SQLite数据库路径
- `COLLECT_INTERVAL`: 数据收集间隔（秒）
- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `LOG_FILE`: 日志文件路径

## 使用方法

### UDP广播模式
程序现在使用UDP广播模式发送数据到端口12306，无需配置特定的接收端地址。任何在同一网络中的UDP服务端都可以接收这些广播数据。

### 运行程序

```bash
# 运行Net Manager客户端
python main.py

# 运行UDP服务端（在另一个终端中运行）
python udp_server.py
```

UDP服务端将监听12306端口，接收来自Net Manager客户端的系统信息数据，并在控制台显示以下信息：
- 发送方的IP地址和端口号
- 主机名
- IP地址
- MAC地址
- 时间戳
- 服务数量和前5个服务的详细信息

## 项目结构

- `main.py`: 主程序入口
- `src/system_collector.py`: 系统信息收集模块
- `src/models.py`: 数据模型和数据库操作
- `src/udp_sender.py`: UDP发送模块
- `src/logger.py`: 日志模块
- `src/config.py`: 配置文件
- `udp_server.py`: UDP服务端（监听12306端口接收数据）
- `requirements.txt`: 项目依赖
- `logs/`: 日志文件目录
- `net_manager.db`: SQLite数据库文件（运行后自动生成）

## 信号处理

程序支持以下信号进行优雅关闭：

- `SIGINT` (Ctrl+C)
- `SIGTERM`

接收到这些信号时，程序会确保UDP连接被正确关闭后再退出。