# Net Manager

Net Manager 是一个功能完整的网络信息收集和监控系统，可以收集客户端系统信息并通过TCP协议发送到服务端，服务端将信息存储到SQLite数据库并提供RESTful API接口和Web仪表板。

## 🚀 功能特性

### 核心功能
- **系统信息收集**: 自动收集主机名、IP地址、MAC地址、网关、子网掩码、服务列表、进程信息
- **网络通信**: 使用UDP广播进行服务发现，TCP协议进行可靠数据传输
- **数据存储**: 使用SQLite数据库存储所有客户端系统信息
- **RESTful API**: 提供完整的API接口用于查询和管理设备信息
- **Web仪表板**: 现代化的Vue.js前端界面，实时显示设备状态
- **跨平台支持**: 完全支持Windows和Linux双平台
- **单例运行**: 基于命名互斥体的单例运行机制，确保应用只能运行一个实例

### 高级功能
- **开机自启动**: 支持Windows和Linux平台的自动启动配置
- **守护进程**: 自动监控和重启客户端程序
- **智能更新**: 只在系统信息发生变化时才发送数据，减少网络流量
- **在线状态检测**: 实时检测客户端在线/离线状态
- **优雅关闭**: 完善的信号处理机制，支持SIGINT和SIGTERM信号

## 📋 系统架构

```
客户端 (Client)                    服务端 (Server)
┌─────────────────┐               ┌─────────────────┐
│  SystemCollector│──────┐        │  UDPServer      │
│  (系统信息收集)  │      │        │  (服务发现)      │
└─────────────────┘      │        └─────────────────┘
                         │        ┌─────────────────┐
┌─────────────────┐      │        │  TCPServer      │
│  TCPClient      │──────┼───────▶│  (数据接收)      │
│  (数据传输)      │      │        └─────────────────┘
└─────────────────┘      │        ┌─────────────────┐
                         │        │  APIServer      │
┌─────────────────┐      │        │  (RESTful API)  │
│  StateManager   │──────┘        └─────────────────┘
│  (状态管理)      │                      │
└─────────────────┘                      │
                                         ▼
                                  ┌─────────────────┐
                                  │  SQLite DB      │
                                  │  (数据存储)      │
                                  └─────────────────┘
                                         │
                                         ▼
                                  ┌─────────────────┐
                                  │  Web Dashboard  │
                                  │  (Vue.js前端)   │
                                  └─────────────────┘
```

## 🛠️ 安装与配置

### 快速开始

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 设置开发环境（推荐）
```bash
python setup_dev_env.py
```

#### 3. 启动服务端
```bash
cd server
python main.py
```

#### 4. 启动客户端
```bash
cd client
python main.py
```

#### 5. 启动Web仪表板（可选）
```bash
cd dashboard
npm install
npm run dev
```

### 详细配置

#### 客户端配置 (`client/src/config.py`)
```python
UDP_HOST = "<broadcast>"      # UDP广播地址
UDP_PORT = 12345             # UDP端口（服务发现）
TCP_PORT = 12346             # TCP端口（数据传输）
COLLECT_INTERVAL = 30        # 数据收集间隔（秒）
LOG_LEVEL = "INFO"           # 日志级别
```

#### 服务端配置 (`server/src/config.py`)
```python
UDP_HOST = "0.0.0.0"         # UDP监听地址
UDP_PORT = 12345             # UDP监听端口
TCP_PORT = 12346             # TCP监听端口
API_PORT = 12344             # API监听端口
VERSION = "1.0.0"            # 版本信息
```

## 📦 打包与部署

### 使用自动化打包脚本（推荐）
```bash
# 打包客户端和服务端
python build.py

# 仅打包客户端
python build.py --client

# 仅打包服务端
python build.py --server

# 清理并重新打包
python build.py --clean
```

### 手动打包
```bash
# 安装Nuitka
pip install nuitka

# 打包客户端
python -m nuitka --standalone --onefile --enable-plugin=multiprocessing client/main.py

# 打包服务端
python -m nuitka --standalone --onefile --enable-plugin=multiprocessing server/main.py
```

### 打包版本运行
```bash
# 运行客户端
client/main.exe

# 运行服务端
server/main.exe

# 使用批处理脚本
client/run_client.bat
server/run_server.bat
```

## 🌐 API接口文档

### 基础信息
- **基础URL**: `http://localhost:12344`
- **数据格式**: JSON
- **编码**: UTF-8

### 可用端点

#### 1. 获取API信息
```http
GET /
```
返回API服务器的基本信息和可用端点列表。

**响应示例**:
```json
{
  "message": "Net Manager API Server",
  "version": "1.0.0",
  "endpoints": {
    "GET /api/systems": "获取所有系统信息",
    "GET /api/systems/{mac_address}": "根据MAC地址获取特定系统信息",
    "GET /health": "健康检查"
  }
}
```

#### 2. 健康检查
```http
GET /health
GET /healthz
```
检查API服务器的健康状态。

**响应示例**:
```json
{
  "status": "healthy",
  "service": "Net Manager API Server"
}
```

#### 3. 获取所有设备信息
```http
GET /api/systems
```
获取所有已连接客户端的系统信息概要，包含在线状态。

**响应示例**:
```json
{
  "status": "success",
  "data": [
    {
      "mac_address": "f0-2f-74-db-87-1f",
      "hostname": "DESKTOP-ABC123",
      "ip_address": "192.168.1.100",
      "services_count": 15,
      "processes_count": 87,
      "online": true,
      "timestamp": "2025-10-05 14:54:59"
    }
  ],
  "count": 1
}
```

#### 4. 获取特定设备信息
```http
GET /api/systems/{mac_address}
```
根据MAC地址获取特定客户端的完整系统信息。

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "mac_address": "f0-2f-74-db-87-1f",
    "hostname": "DESKTOP-ABC123",
    "ip_address": "192.168.1.100",
    "gateway": "192.168.1.1",
    "netmask": "255.255.255.0",
    "services": [...],
    "processes": [...],
    "online": true,
    "timestamp": "2025-10-05 14:54:59"
  }
}
```

**错误响应**:
```json
{
  "status": "error",
  "message": "未找到MAC地址为 f0-2f-74-db-87-1f 的系统信息"
}
```

### 数据结构说明

#### 系统信息(System Info) - 概要信息

| 字段名 | 类型 | 描述 |
|--------|------|------|
| mac_address | string | 客户端MAC地址 |
| hostname | string | 客户端主机名 |
| ip_address | string | 客户端IP地址 |
| services_count | integer | 客户端运行的服务数量 |
| processes_count | integer | 客户端运行的进程数量 |
| online | boolean | 客户端在线状态 |
| timestamp | string | 信息收集时间 |

#### 系统信息(System Info) - 详细信息

| 字段名 | 类型 | 描述 |
|--------|------|------|
| mac_address | string | 客户端MAC地址 |
| hostname | string | 客户端主机名 |
| ip_address | string | 客户端IP地址 |
| gateway | string | 客户端网关地址 |
| netmask | string | 客户端子网掩码 |
| services | array | 客户端运行的服务列表 |
| processes | array | 客户端运行的进程列表 |
| online | boolean | 客户端在线状态 |
| timestamp | string | 信息收集时间 |

#### 服务信息(Service)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| name | string | 服务名称 |
| status | string | 服务状态 |
| pid | integer | 进程ID |

#### 进程信息(Process)

| 字段名 | 类型 | 描述 |
|--------|------|------|
| name | string | 进程名称 |
| status | string | 进程状态 |
| pid | integer | 进程ID |
| cpu_percent | float | CPU使用率 |
| memory_percent | float | 内存使用率 |

### 错误处理

API使用标准HTTP状态码来表示请求结果：

- `200` - 请求成功
- `404` - 请求的资源未找到
- `500` - 服务器内部错误

### 使用示例

#### 使用curl

```bash
# 获取所有系统信息
curl http://localhost:12344/api/systems

# 根据MAC地址获取特定系统信息
curl http://localhost:12344/api/systems/f0-2f-74-db-87-1f
```

#### 使用Python requests

```python
import requests

# 获取所有系统信息
response = requests.get('http://localhost:12344/api/systems')
data = response.json()

# 根据MAC地址获取特定系统信息
response = requests.get('http://localhost:12344/api/systems/f0-2f-74-db-87-1f')
data = response.json()
```

## 🖥️ Web仪表板

### 功能特性
- **实时设备监控**: 显示所有连接设备的在线状态和基本信息
- **设备统计**: 总设备数、在线设备、离线设备统计
- **设备管理**: 查看和管理所有网络设备
- **网络拓扑**: 可视化网络设备连接关系
- **响应式设计**: 支持桌面和移动设备
- **现代化UI**: 基于Tailwind CSS的现代化界面设计

### 技术栈
- **框架**: Vue.js 3 (Composition API)
- **路由**: Vue Router 4
- **UI库**: Tailwind CSS
- **构建工具**: Vite
- **HTTP客户端**: Axios
- **状态管理**: VueUse
- **网络拓扑**: LogicFlow
- **工具库**: Lodash-es, Day.js

### 页面结构
- **首页 (/home)**: 显示设备统计信息和设备列表
- **设备管理 (/devices)**: 设备详细信息管理页面
- **网络拓扑 (/topology)**: 网络设备连接关系可视化页面

### 运行方式
```bash
cd dashboard
npm install
npm run dev      # 开发模式
npm run build    # 生产构建
npm run preview  # 预览生产构建
```

### API配置
Web仪表板通过环境变量配置API地址：
- 开发环境: `http://127.0.0.1:12344`
- 生产环境: 当前页面的协议、主机名和端口

### 目录结构
```
dashboard/
├── src/
│   ├── views/              # 页面组件
│   │   ├── Index.vue       # 主页面布局
│   │   ├── home/Home.vue   # 首页
│   │   ├── devices/        # 设备管理页面
│   │   └── topology/       # 网络拓扑页面
│   ├── common/api/         # API接口封装
│   ├── config/             # 配置文件
│   │   ├── router/         # 路由配置
│   │   └── http/           # HTTP客户端配置
│   └── styles/             # 样式文件
└── package.json            # 项目依赖配置
```

## 🧪 测试

### 运行所有测试
```bash
# 系统信息收集器测试
python -m client.tests.test_system_collector

# TCP连接测试
python -m client.tests.test_tcp_connection

# 跨平台兼容性测试
python -m client.tests.test_cross_platform
```

### 数据库检查
```bash
# 查看数据库中的系统信息
cd server
python check_db.py
```

## 🔧 高级功能

### 开机自启动
- **Windows**: 创建启动文件夹快捷方式或批处理文件
- **Linux**: 创建systemd服务

### 守护进程
- 自动监控客户端进程状态
- 进程异常退出时自动重启
- 支持Windows和Linux平台

### 智能数据更新
- 计算系统信息哈希值
- 只在数据发生变化时发送
- 减少网络流量和服务器负载

## 📁 项目结构

```
net-manager/
├── README.md                  # 项目说明文档
├── requirements.txt           # 项目依赖
├── setup_dev_env.py          # 开发环境设置脚本
├── build.py                  # 自动化打包脚本
├── client/                   # 客户端代码
│   ├── main.py               # 客户端主程序入口
│   ├── src/                  # 客户端源代码
│   │   ├── system_collector.py   # 系统信息收集器
│   │   ├── tcp_client.py     # TCP客户端
│   │   ├── autostart.py      # 开机自启动功能
│   │   ├── singleton_manager.py  # 跨平台单例管理器
│   │   └── ...               # 其他模块
│   └── tests/                # 客户端测试
├── server/                   # 服务端代码
│   ├── main.py               # 服务端主程序入口
│   ├── check_db.py           # 数据库检查脚本
│   └── src/                  # 服务端源代码
│       ├── tcp_server.py     # TCP服务端
│       ├── udp_server.py     # UDP服务端
│       ├── api_server.py     # API服务端
│       └── ...               # 其他模块
├── dashboard/                # Web仪表板
│   ├── src/                  # Vue.js源代码
│   │   ├── views/            # 页面组件
│   │   ├── common/api/       # API接口
│   │   └── config/           # 配置文件
│   └── ...                   # 其他前端文件
└── docs/                     # 项目文档
    ├── API_DOCUMENTATION.md  # API文档
    ├── PACKAGING.md          # 打包说明
    └── ...                   # 其他文档
```

## 🛡️ 跨平台兼容性

### 支持的平台
- **Windows**: Windows 7及以上版本
- **Linux**: 主流Linux发行版

### 平台特性
- **路径处理**: 自动适配不同系统的路径分隔符
- **编码识别**: 自动识别系统编码（Windows: GBK，Linux: UTF-8）
- **信号处理**: 跨平台信号处理，支持优雅关闭
- **权限管理**: 适配不同平台的权限要求

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 🆘 支持

如遇到问题，请：
1. 查看项目文档
2. 检查日志文件
3. 运行测试验证功能
4. 提交Issue报告问题

---