# Net Manager 项目结构

## 目录结构

```
net-manager/
├── README.md                  # 项目说明文档
├── PROJECT_STRUCTURE.md       # 项目结构说明
├── requirements.txt           # 项目依赖
├── main.py                   # 主程序入口
├── net_manager.db            # SQLite数据库文件
├── logs/                     # 日志目录
│   └── net_manager.log       # 日志文件
├── src/                      # 源代码目录
│   ├── __init__.py           # Python包标识文件
│   ├── config.py             # 配置文件
│   ├── logger.py             # 日志模块
│   ├── system_collector.py   # 系统信息收集器
│   ├── models.py             # 数据模型
│   ├── udp_sender.py         # UDP发送器
│   ├── start_net_manager.py  # 启动脚本
│   └── setup_dev_env.py      # 开发环境设置脚本
├── tests/                    # 测试目录
│   ├── __init__.py           # Python包标识文件
│   ├── test_system_collector.py  # 系统信息收集器测试
│   ├── test_udp_receiver.py      # UDP接收器测试脚本
│   └── udp_receiver.py           # UDP接收器(用于测试)
└── venv/                     # 虚拟环境目录
    ├── Scripts/              # Windows下的可执行文件
    ├── Lib/                  # 第三方库
    └── Include/              # 头文件
```

## 模块说明

### 主要模块

1. **src/system_collector.py** - 系统信息收集器
   - `SystemCollector`类
   - 获取主机名、IP地址、MAC地址
   - 获取运行的服务和端口信息

2. **src/models.py** - 数据模型和数据库操作
   - `SystemInfo`类 - 系统信息数据模型
   - `DatabaseManager`类 - 数据库管理器
   - SQLite数据库操作

3. **src/udp_sender.py** - UDP发送器
   - `UDPSender`类
   - 通过UDP协议发送系统信息

4. **src/logger.py** - 日志模块
   - 日志配置和记录
   - 文件和控制台输出

5. **src/config.py** - 配置文件
   - UDP配置
   - 数据库配置
   - 收集间隔配置
   - 日志配置

### 主程序

- **main.py** - 主程序入口
  - 初始化各组件
  - 循环收集系统信息
  - 保存到数据库
  - 通过UDP发送
  - 信号处理

### 测试模块

- **tests/test_system_collector.py** - 系统信息收集器单元测试
- **tests/udp_receiver.py** - UDP接收器(用于测试UDP发送功能)
- **tests/test_udp_receiver.py** - UDP接收器测试脚本

### 辅助脚本

- **src/start_net_manager.py** - 启动脚本
- **src/setup_dev_env.py** - 开发环境设置脚本
- **udp_server.py** - UDP服务端（监听12306端口接收数据）

## 数据流

```
[系统信息收集] --> [数据库存储] --> [UDP发送]
     ^              ^              ^
     |              |              |
SystemCollector  DatabaseManager  UDPSender
```

## 配置说明

配置文件 `config.py` 包含以下配置项：

- `UDP_HOST` - UDP服务器地址
- `UDP_PORT` - UDP服务器端口
- `DB_PATH` - SQLite数据库路径
- `COLLECT_INTERVAL` - 数据收集间隔(秒)
- `LOG_LEVEL` - 日志级别
- `LOG_FILE` - 日志文件路径

## 使用说明

1. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

2. **运行程序**:
   ```bash
   python main.py
   ```

3. **运行测试**:
   ```bash
   python -m tests.test_system_collector
   ```

4. **设置开发环境**:
   ```bash
   python setup_dev_env.py
   ```