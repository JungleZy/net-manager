# Net Manager

Net Manager 是一个网络信息收集和监控工具，可以收集系统的主机名、IP地址、MAC地址和服务信息，并通过UDP协议发送到指定的服务器。

## 功能特性

- 收集系统信息（主机名、IP地址、MAC地址、服务列表）
- 通过UDP协议将信息发送到指定服务器
- 完善的日志记录功能
- 支持优雅关闭（处理SIGINT和SIGTERM信号）
- 基于命名互斥体的单例运行机制（确保应用只能运行一个实例）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 安装Nuitka（用于打包）

```bash
pip install nuitka
```

## 配置

配置文件位于 `config.py`，可以修改以下参数：

- `UDP_HOST`: UDP服务器地址
- `UDP_PORT`: UDP服务器端口
- `COLLECT_INTERVAL`: 数据收集间隔（秒）
- `LOG_LEVEL`: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `LOG_FILE`: 日志文件路径

## 使用方法

### UDP广播模式
程序现在使用UDP广播模式发送数据到端口12345，无需配置特定的接收端地址。任何在同一网络中的UDP服务端都可以接收这些广播数据。

### 运行程序

#### 方法1：源码方式运行
```bash
# 运行Net Manager客户端
cd client
python main.py

# 运行UDP服务端（在另一个终端中运行）
cd server
python main.py
```

#### 方法2：打包版本运行（推荐）
项目可以使用Nuitka打包成独立的可执行文件，可以直接运行：

##### 使用预打包版本：
```bash
# 运行Net Manager客户端（打包版本）
client\main.exe

# 或者使用提供的批处理脚本
client\run_client.bat

# 运行UDP服务端（在另一个终端中运行）
server\main.py
```

##### 使用自动化打包脚本：
项目提供了自动化打包脚本 `build.py`，可以分别对客户端和服务端进行打包：

```bash
# 打包客户端和服务端
python build.py

# 仅打包客户端
python build.py --client

# 仅打包服务端
python build.py --server

# 清理之前的构建并重新打包
python build.py --clean
```

打包版本的优势：
- 不需要安装Python环境
- 不需要安装依赖包
- 启动速度更快
- 更便于分发和部署

UDP服务端将监听12345端口，接收来自Net Manager客户端的系统信息数据，并在控制台显示以下信息：
- 发送方的IP地址和端口号
- 主机名
- IP地址
- MAC地址
- 时间戳
- 服务数量和前5个服务的详细信息

## 跨平台兼容性

Net Manager客户端现已支持Windows和Linux双平台运行：

### Windows平台
- 可直接运行打包版本 `client\main.exe`
- 或使用批处理脚本 `client\run_client.bat`
- 支持Windows 7及以上版本

### Linux平台
- 需要Python 3.7+环境
- 安装依赖：`pip install -r requirements.txt`
- 运行：`python client/main.py`

### 平台兼容性特性
- 统一的路径处理机制，自动适配不同系统的路径分隔符
- 跨平台信号处理，支持优雅关闭
- 自动识别系统编码，确保日志文件正确显示中文
- 统一的配置文件管理

## 项目结构

### 客户端 (client/)
- `main.py`: 客户端主程序入口
- `src/system_collector.py`: 系统信息收集模块
- `src/tcp_client.py`: TCP客户端模块
- `src/logger.py`: 日志模块
- `src/config.py`: 配置文件
- `src/platform_utils.py`: 平台兼容性工具模块

### 服务端 (server/)
- `main.py`: 服务端主程序入口
- `src/udp_server.py`: UDP服务发现服务器
- `src/tcp_server.py`: TCP数据接收服务器

### 其他
- `requirements.txt`: 项目依赖
- `logs/`: 日志文件目录

## 信号处理

程序支持以下信号进行优雅关闭：

- `SIGINT` (Ctrl+C)
- `SIGTERM` (Linux/Unix)

接收到这些信号时，程序会确保UDP连接被正确关闭后再退出。