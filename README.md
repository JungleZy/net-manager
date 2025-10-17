# Net Manager

Net Manager 是一个全栈网络设备管理系统，集成了客户端探测、服务端管理和Web控制面板三大核心模块，支持设备自动发现、网络拓扑可视化、SNMP设备监控等功能。

## 核心特性

✅ **设备自动发现** - 客户端自动上报系统信息，无需手动配置  
✅ **网络拓扑可视化** - 基于 LogicFlow 的可视化拓扑图编辑器  
✅ **SNMP 设备监控** - 支持 SNMPv1/v2c/v3 协议，实时监控交换机状态  
✅ **跨平台支持** - Windows/Linux/macOS 全平台客户端和服务端  
✅ **现代化 UI** - Vue 3 + Ant Design Vue 构建的响应式界面  
✅ **RESTful API** - 完整的 REST API 接口，支持二次开发  
✅ **单文件部署** - 使用 Nuitka 打包为单一可执行文件

## 项目结构

```
net-manager/
├── client/                    # 客户端程序
│   ├── src/                   # 客户端源代码
│   └── requirements.txt       # 客户端依赖
├── server/                    # 服务器程序
│   ├── src/                   # 服务器源代码
│   │   ├── core/              # 核心模块
│   │   ├── database/          # 数据库模块（已重构）
│   │   ├── models/            # 数据模型
│   │   ├── network/           # 网络通信模块
│   │   ├── snmp/              # SNMP监控模块
│   │   └── utils/             # 工具模块
│   ├── static/                # 前端静态文件（构建时生成）
│   ├── tests/                 # 测试代码
│   └── requirements.txt       # 服务器依赖
├── dashboard/                 # 前端控制面板
│   ├── src/                   # 前端源代码
│   ├── dist/                  # 构建产物（构建后生成）
│   └── package.json           # 前端依赖
├── dist/                      # 最终打包产物
│   ├── server/                # 服务端可执行文件
│   └── client/                # 客户端可执行文件
├── docs/                      # 文档
├── .github/workflows/         # GitHub Actions 工作流
├── build.py                   # 构建脚本
├── BUILD.md                   # 构建说明
└── README.md                  # 项目说明
```

## 数据库模块重构说明

数据库模块已从单一的`database_manager.py`文件重构为多个专门的管理器类，以提高代码的可维护性和可扩展性：

- **BaseDatabaseManager**: 提供基础的数据库连接和线程安全访问
- **DeviceManager**: 专门处理设备信息管理
- **SwitchManager**: 专门处理交换机配置管理
- **DatabaseManager**: 统一接口，保持向后兼容性

详细说明请参见 [数据库模块README](server/src/database/README.md)

开发者迁移指南请参见 [数据库迁移指南](docs/DATABASE_MIGRATION_GUIDE.md)

## 功能特性

### 前端控制面板（Dashboard）
- 🎨 基于 **Vue 3** + **Vite** + **Ant Design Vue** 构建
- 📊 **设备管理**：增删改查、设备类型管理、别名设置
- 🗺️ **网络拓扑图**：基于 LogicFlow 的可视化编辑器，支持拖拽、连线、分组
- 🔍 **SNMP 设备扫描**：自动发现网络设备，支持批量添加
- 📡 **实时数据监控**：WebSocket 实时推送设备状态
- 📱 **响应式设计**：支持桌面端和移动端访问

### 服务器端（Server）
- 🌐 **Tornado Web 框架**：高性能异步 HTTP 服务器
- 🔌 **TCP 服务器**：接收客户端设备信息上报
- 📢 **UDP 服务器**：接收广播消息，支持设备自动发现
- 🗄️ **SQLite 数据库**：存储设备信息、交换机配置、拓扑数据
- 📊 **SNMP 监控**：支持 SNMPv1/v2c/v3，监控交换机端口状态、流量等
- 🔗 **WebSocket 服务**：实时推送设备状态变更
- 📁 **静态文件服务**：集成前端控制面板，单一服务即可访问
- 🔧 **RESTful API**：完整的设备、交换机、拓扑管理接口

### 客户端（Client）
- 📊 **系统信息收集**：CPU、内存、磁盘、网络接口、网关等
- 🚀 **自动上报**：定期通过 TCP 协议发送信息到服务器
- 📡 **UDP 广播**：定期发送广播消息，便于服务端自动发现
- 🔄 **自动重连**：网络断开自动重连机制
- 💻 **跨平台支持**：Windows/Linux/macOS 全平台支持
- 🎯 **轻量级设计**：低资源占用，可后台运行

## 安装和运行

### 快速开始

#### 1. 服务器端（包含前端控制面板）

**开发环境：**

```bash
# 安装Python依赖
cd server
pip install -r requirements.txt

# 启动服务器
python main.py

# 另开终端，启动前端开发服务器
cd dashboard
npm install  # 或 pnpm install / yarn install
npm run dev
```

访问：
- 后端 API: `http://localhost:8000/api`
- 前端控制面板: `http://localhost:8001`

**生产环境（打包后）：**

```bash
# 构建服务端（自动构建前端并集成）
python build.py --server

# 运行
cd dist/server
./net-manager-server  # Linux
net-manager-server.exe  # Windows
```

访问: `http://localhost:8000/` （自动重定向到控制面板）

#### 2. 客户端

**开发环境：**

```bash
cd client
pip install -r requirements.txt
python main.py
```

**生产环境（打包后）：**

```bash
# 构建客户端
python build.py --client

# 运行
cd dist/client
./net-manager-client  # Linux
net-manager-client.exe  # Windows
```

### Linux环境运行注意事项

在Linux环境下运行打包后的客户端时，请注意以下几点：

1. **文件权限**：确保可执行文件有执行权限
   ```bash
   chmod +x net-manager-client
   ```

2. **写入权限**：客户端需要在程序所在目录创建配置文件（如 `client_state.json`），请确保：
   - 程序所在目录具有写入权限
   - 或者以适当的用户权限运行程序
   
   如果遇到权限问题，可以：
   ```bash
   # 检查目录权限
   ls -la
   
   # 设置目录写入权限
   chmod 755 /path/to/program/directory
   ```

3. **推荐运行方式**：
   - 普通用户权限运行（推荐）
   - 避免使用root权限，除非必要
   - 确保程序目录归属当前用户

## 跨平台打包

本项目支持使用 GitHub Actions 进行跨平台打包，采用“先测试后构建”的策略，可生成以下平台的可执行文件：

- Windows x86
- Windows x64
- Linux x86
- Linux x64

### 本地打包

使用 `build.py` 脚本可以在本地进行打包：

```bash
python build.py          # 打包客户端和服务端
python build.py --client # 仅打包客户端
python build.py --server # 仅打包服务端（自动构建前端）
```

**打包流程（服务端）：**

1. 构建前端控制面板（Dashboard）
   - 检测并安装 npm/pnpm/yarn
   - 执行 `npm run build`
   - 生成 `dashboard/dist` 目录

2. 复制前端产物
   - 将 `dashboard/dist` 复制到 `server/static`

3. 打包服务端
   - 使用 Nuitka 打包 server
   - 自动包含 `server/static` 目录
   - 生成单一可执行文件

**前置要求：**

**Dashboard 构建要求：**
- Node.js >= 16
- npm / pnpm / yarn（任选其一）

**Server/Client 打包要求：**
- Python 3.8+
- Nuitka
- C 编译器：
  - Windows: MSVC 或 MinGW
  - Linux: gcc 或 clang（推荐 clang）
- Linux 还需要：patchelf

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install patchelf gcc clang

# CentOS/RHEL/Fedora
sudo dnf install patchelf gcc clang
# 或
sudo yum install patchelf gcc clang

# Arch Linux
sudo pacman -S patchelf gcc clang
```

**关于编译器的说明：**

- 打包脚本会自动检测可用的C编译器
- 如果安装了clang，脚本会优先使用clang（更稳定，较少崩溃）
- 如果只有gcc可用，会使用gcc
- 如果遇到gcc编译器崩溃问题（segfault），建议：
  - 安装并使用clang编译器
  - 或升级gcc到最新版本

如果未安装必要的工具，打包过程会自动检测并给出安装提示。

详细说明请参见 [GitHub Actions 打包指南](docs/GITHUB_ACTIONS_PACKAGING.md)

## 自动化测试

本项目使用 GitHub Actions 进行跨平台自动化测试，确保在不同操作系统上的兼容性：

- Windows (x64)
- Linux (x64)

测试工作流会在每次推送代码到 `main` 或 `develop` 分支时自动运行，也会在创建 Pull Request 时触发。

所有测试均已通过修复，确保在不同平台上都能正常运行。

## API 接口

### 设备管理 API
| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/devices` | 获取所有设备信息 |
| `GET` | `/api/devices/{device_id}` | 获取特定设备信息 |
| `POST` | `/api/devices/create` | 创建新设备 |
| `POST` | `/api/devices/update` | 更新设备信息 |
| `POST` | `/api/devices/delete` | 删除设备 |
| `PUT` | `/api/devices/{device_id}/type` | 更新设备类型 |

### 交换机管理 API
| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/switches` | 获取所有交换机配置 |
| `GET` | `/api/switches/{id}` | 获取特定交换机配置 |
| `POST` | `/api/switches/create` | 添加交换机配置 |
| `POST` | `/api/switches/update` | 更新交换机配置 |
| `POST` | `/api/switches/delete` | 删除交换机配置 |
| `POST` | `/api/switches/scan` | SNMP 扫描设备 |
| `POST` | `/api/switches/scan/simple` | 简单 SNMP 扫描 |

### 拓扑管理 API
| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/topologies` | 获取所有拓扑图 |
| `GET` | `/api/topologies/latest` | 获取最新拓扑图 |
| `GET` | `/api/topologies/{topology_id}` | 获取特定拓扑图 |
| `POST` | `/api/topologies/create` | 创建拓扑图 |
| `POST` | `/api/topologies/update` | 更新拓扑图 |
| `POST` | `/api/topologies/delete` | 删除拓扑图 |

### 系统 API
| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/health` | 服务器健康检查 |
| `GET` | `/healthz` | Kubernetes 健康检查端点 |
| `WS` | `/ws` | WebSocket 连接(实时数据推送) |

> 详细 API 文档请参见 [API 文档](docs/API_DOCUMENTATION.md) 和 [交换机 API 文档](docs/SWITCH_API.md)

## 技术栈

### 后端
- **Python 3.8+**
- **Tornado** - 异步 Web 框架
- **SQLite** - 轻量级嵌入式数据库
- **pysnmp** - SNMP 协议支持（v1/v2c/v3）
- **psutil** - 系统信息采集
- **Socket** - TCP/UDP 网络通信

### 前端
- **Vue 3** - 渐进式 JavaScript 框架
- **Vite** - 极速构建工具（使用 Rolldown）
- **Ant Design Vue** - 企业级 UI 组件库
- **LogicFlow** - 流程图编辑框架（用于拓扑图）
- **Axios** - HTTP 客户端
- **Tailwind CSS** - 实用优先的 CSS 框架
- **VueRouter** - 路由管理

### 打包工具
- **Nuitka** - Python 到 C/C++ 编译器，生成独立可执行文件
- **Node.js** - 前端构建环境

## 快速导航

### 📚 核心文档
- **[构建说明](BUILD.md)** - 前端和后端构建流程详解
- [数据库模块重构说明](docs/DATABASE_MIGRATION_GUIDE.md) - 数据库架构迁移指南
- [数据库模块 README](server/src/database/README.md) - 数据库模块使用说明

### 🔧 开发文档
- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [模块设计](docs/MODULE_DESIGN.md)
- [接口规范](docs/INTERFACE_SPEC.md)
- [状态管理器](docs/STATE_MANAGER.md)

### 📖 API 文档
- [API 文档](docs/API_DOCUMENTATION.md) - 完整 API 接口说明
- [交换机 API 文档](docs/SWITCH_API.md) - 交换机管理 API

### 🎨 前端文档
- [仪表盘说明](docs/DASHBOARD_README.md)

### 🔐 安全与配置
- [SHA 认证支持](docs/SHA_AUTH_SUPPORT.md) - SNMP v3 SHA 认证配置
- [路由器配置指南](docs/ROUTER_CONFIG_GUIDE.md)

### 📦 部署文档
- [打包说明](docs/PACKAGING.md)
- [GitHub Actions 打包指南](docs/GITHUB_ACTIONS_PACKAGING.md)

### 📝 其他
- [开发计划](docs/开发计划.md)
- [变更日志](docs/CHANGELOG.md)

## 开发团队

如有问题或建议，欢迎提交 Issue 或 Pull Request。

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

MIT License

## Star History

如果这个项目对您有帮助，请给我们一个 ⭐️！