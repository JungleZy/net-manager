# Net Manager 项目结构

## 目录结构

```
net-manager/
├── README.md                  # 项目说明文档
├── PROJECT_STRUCTURE.md       # 项目结构说明
├── requirements.txt           # 项目依赖
├── net_manager.db            # SQLite数据库文件
├── logs/                     # 日志目录
│   └── net_manager.log       # 日志文件
├── client/                   # 客户端代码
│   ├── main.py               # 客户端主程序入口
│   ├── main.exe              # 客户端打包后的可执行文件
│   ├── run_client.bat        # 客户端运行脚本
│   ├── src/                  # 客户端源代码
│   │   ├── __init__.py       # Python包标识文件
│   │   ├── autostart.py      # 开机自启动功能
│   │   ├── config.py         # 客户端配置文件
│   │   ├── logger.py         # 日志模块
│   │   ├── models.py         # 数据模型
│   │   ├── platform_utils.py # 跨平台工具函数
│   │   ├── singleton_manager.py  # 跨平台单例管理器（命名互斥体实现）
│   │   ├── system_collector.py   # 系统信息收集器
│   │   ├── start_net_manager.py  # 启动脚本
│   │   ├── tcp_client.py     # TCP客户端
│   │   └── setup_dev_env.py  # 开发环境设置脚本
│   ├── tests/                # 客户端测试目录
│   │   ├── __init__.py       # Python包标识文件
│   │   ├── test_cross_platform.py  # 跨平台测试
│   │   ├── test_system_collector.py  # 系统信息收集器测试
│   │   ├── test_tcp_connection.py    # TCP连接测试
│   │   ├── test_udp_receiver.py      # UDP接收器测试脚本
│   │   └── udp_receiver.py   # UDP接收器(用于测试)
│   ├── test_autostart.py     # 开机自启动测试脚本
│   └── test_singleton.py     # 跨平台单例功能测试脚本
├── server/                   # 服务端代码
│   ├── main.py               # 服务端主程序入口
│   ├── server.lock           # 服务端单例锁文件（已废弃，改用命名互斥体）
│   ├── src/                  # 服务端源代码
│   │   ├── __init__.py       # Python包标识文件
│   │   ├── config.py         # 服务端配置文件
│   │   ├── logger.py         # 日志模块
│   │   ├── platform_utils.py # 跨平台工具函数
│   │   ├── singleton_manager.py  # 跨平台单例管理器（命名互斥体实现）
│   │   ├── tcp_server.py     # TCP服务端
│   │   └── udp_server.py     # UDP服务端（监听12306端口接收数据）
│   └── test_singleton.py     # 跨平台单例功能测试脚本
├── setup_dev_env.py          # 开发环境设置脚本
├── build.py                  # 打包脚本
├── PACKAGING.md              # 打包说明
└── SUMMARY.md                # 项目摘要
```

## 模块说明

### 客户端主要模块

1. **client/src/system_collector.py** - 系统信息收集器
   - `SystemCollector`类
   - 获取主机名、IP地址、MAC地址
   - 获取运行的服务和端口信息

2. **client/src/models.py** - 数据模型和数据库操作
   - `SystemInfo`类 - 系统信息数据模型
   - `DatabaseManager`类 - 数据库管理器
   - SQLite数据库操作

3. **client/src/udp_sender.py** - UDP发送器
   - `UDPSender`类
   - 通过UDP协议发送系统信息

### 4. **client/src/logger.py** - 日志模块
   - 日志配置和记录
   - 文件和控制台输出

### 5. **client/src/config.py** - 客户端配置文件
   - UDP配置
   - 数据库配置
   - 收集间隔配置
   - 日志配置

### 6. **client/src/platform_utils.py** - 平台兼容性工具模块
   - 跨平台路径处理
   - 信号处理兼容性
   - 系统编码识别 服务端主要模块

1. **server/udp_server.py** - UDP服务端
   - 监听12306端口接收数据
   - 解析并显示接收到的系统信息

2. **server/src/config.py** - 服务端配置文件
   - UDP端口配置

### 主程序

- **client/main.py** - 客户端主程序入口
  - 初始化各组件
  - 循环收集系统信息
  - 保存到数据库
  - 通过UDP发送
  - 信号处理

- **server/main.py** - 服务端主程序入口
  - 启动UDP服务端

### 测试模块

- **client/tests/test_system_collector.py** - 系统信息收集器单元测试
- **client/tests/udp_receiver.py** - UDP接收器(用于测试UDP发送功能)
- **client/tests/test_udp_receiver.py** - UDP接收器测试脚本
- **client/test_udp_config.py** - UDP配置测试

### 辅助脚本

- **client/src/start_net_manager.py** - 启动脚本
- **client/src/setup_dev_env.py** - 开发环境设置脚本

## 数据流

```
[系统信息收集] --> [数据库存储] --> [UDP发送]
     ^              ^              ^
     |              |              |
SystemCollector  DatabaseManager  UDPSender
```

## 配置说明

### 客户端配置文件 `client/src/config.py` 包含以下配置项：

- `UDP_HOST` - UDP服务器地址
- `UDP_PORT` - UDP服务器端口
- `DB_PATH` - SQLite数据库路径
- `COLLECT_INTERVAL` - 数据收集间隔(秒)
- `LOG_LEVEL` - 日志级别
- `LOG_FILE` - 日志文件路径

### 服务端配置文件 `server/src/config.py` 包含以下配置项：

- `UDP_PORT` - UDP监听端口

## 使用说明

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **运行客户端**:
   
   ### 方法1：源码方式运行
   ```bash
   cd client
   python main.py
   ```
   
   ### 方法2：打包版本运行（推荐）
   ```bash
   cd client
   main.exe
   
   # 或者使用批处理脚本
   run_client.bat
   ```

3. **运行服务端**:
   ```bash
   cd server
   python main.py
   ```

4. **运行测试**:
   ```bash
   cd client
   python -m tests.test_system_collector
   ```

5. **设置开发环境**:
   ```bash
   cd client
   python src/setup_dev_env.py
   ```