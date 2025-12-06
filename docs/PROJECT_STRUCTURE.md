# Net Manager 项目结构

## 目录结构概览

```
net-manager/
├── agent/                      # 预构建客户端二进制（供前端下载）
├── client/                     # 客户端程序
│   ├── src/
│   │   ├── config_module/      # 配置读取
│   │   ├── core/               # 应用控制器与状态管理
│   │   ├── exceptions/         # 异常类型
│   │   ├── network/            # TCP/UDP 客户端
│   │   ├── system/             # 开机自启与系统信息采集
│   │   └── utils/              # 日志、平台工具、单例、唯一ID
│   ├── tests/                  # 客户端测试集
│   └── main.py                 # 客户端入口
├── server/                     # 服务端程序
│   ├── migrations/             # 数据库迁移脚本
│   ├── src/
│   │   ├── core/               # 配置、日志、单例、状态管理
│   │   ├── database/           # 连接池、管理器、异常
│   │   ├── models/             # 设备/交换机/拓扑模型
│   │   ├── monitor/            # 服务器性能监控
│   │   ├── network/
│   │   │   ├── api/            # Tornado HTTP API 与 WebSocket
│   │   │   ├── tcp/            # TCP 服务器
│   │   │   └── udp/            # UDP 广播与服务
│   │   ├── snmp/               # SNMP 管理、OID 分类、统一轮询
│   │   └── utils/              # 平台工具
│   ├── tests/                  # 服务端测试集
│   └── main.py                 # 服务端入口
├── dashboard/                  # 前端控制面板（Vue3 + Vite + Ant Design Vue）
│   ├── src/                    # 组件/视图/拓扑/API 封装
│   ├── public/docs/            # 面向用户的说明文档
│   ├── package.json            # 依赖配置
│   └── vite.config.js          # 开发端口 8001
├── docs/                       # 项目文档与专题
│   ├── 00-文档目录.md          # 文档索引
│   ├── BUILD.md                # 构建说明
│   ├── PROJECT_STRUCTURE.md    # 项目结构说明
│   └── ...                     # 其他模块与 API 文档
├── .github/workflows/          # CI/CD 工作流
├── build.py                    # 打包脚本（自动集成 Dashboard）
├── requirements.txt            # Python 统一依赖
├── pyproject.toml              # 项目配置
└── README.md                   # 项目总览
```

## 客户端模块说明

- `client/src/core/app_controller.py`：应用主控制器，处理发现、连接、上报、重试等流程
- `client/src/core/state_manager.py`：状态持久化与客户端唯一 ID 管理
- `client/src/network/tcp_client.py`：TCP 连接、断线重连、消息收发
- `client/src/network/udp_client.py`：UDP 广播与服务发现
- `client/src/system/system_collector.py`：CPU/内存/磁盘/网络接口等系统信息采集
- `client/src/system/autostart.py`：跨平台开机自启管理
- `client/src/utils/logger.py`：日志初始化与 idempotent 设置
- `client/src/utils/platform_utils.py`：跨平台路径、信号、可执行检测
- `client/src/utils/singleton_manager.py`：跨平台进程/文件锁单例
- `client/src/utils/unique_id.py`：唯一 ID 生成与加载

## 服务端模块说明

- `server/src/network/api/api_server.py`：Tornado HTTP 服务入口与路由
- `server/src/network/api/handlers/*`：设备/交换机/拓扑/性能等 RESTful API
- `server/src/network/websocket_handler.py`：WebSocket 实时消息推送
- `server/src/network/tcp/tcp_server.py`：接收客户端上报
- `server/src/network/udp/udp_server.py` 与 `broadcast_server.py`：广播与发现
- `server/src/snmp/*`：SNMP 管理器、统一轮询、OID 分类
- `server/src/monitor/server_monitor.py`：服务器性能采集与上报
- `server/src/database/*`：连接池与各资源管理器（设备/拓扑/交换机等）
- `server/src/core/*`：配置、日志、状态、单例

## 数据流概览

```
[客户端系统采集] → [TCP 上报] → [服务端 API/数据库] → [WebSocket 推送] → [Dashboard 展示]
                          ↘ [UDP 广播/发现] ↗
```

## 运行与构建

- 安装依赖：`pip install -r requirements.txt`
- 开发运行：
  - 后端：`cd server && python main.py`（API: `http://localhost:8000/api`）
  - 前端：`cd dashboard && npm run dev`（`http://localhost:8001`）
  - 客户端：`cd client && python main.py`
- 打包：
  - 服务端（含前端）：`python build.py --server`
  - 客户端：`python build.py --client`

## CI/CD

- 采用 Tag 触发的“先测试后构建”流程：`.github/workflows/test-then-build.yml`
- 自动发布 Release 并上传各平台构建产物

## 备注

- `server/static` 为构建时生成目录，由打包脚本从 `dashboard/dist` 复制
- `agent/` 内的二进制文件会被复制到 `server/static/agent`，供前端页面下载
