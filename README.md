# Net Manager

Net Manager是一个网络设备管理系统，包含服务器和客户端两部分。

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
│   ├── tests/                 # 测试代码
│   └── requirements.txt       # 服务器依赖
├── docs/                      # 文档
├── .github/workflows/         # GitHub Actions 工作流
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

### 服务器端
- TCP服务器接收客户端信息
- UDP服务器接收广播消息
- RESTful API提供设备管理接口
- 数据库存储设备信息
- SNMP交换机监控功能

### 客户端
- 收集系统信息
- 通过TCP协议发送信息到服务器
- 定期发送UDP广播消息
- 跨平台支持（Windows/Linux/macOS）

## 安装和运行

### 服务器端
```bash
cd server
pip install -r requirements.txt
python src/main.py
```

### 客户端
```bash
cd client
pip install -r requirements.txt
python src/main.py
```

## 跨平台打包

本项目支持使用 GitHub Actions 进行跨平台打包，采用"先测试后构建"的策略，可生成以下平台的可执行文件：

- Windows x86
- Windows x64
- Linux x86
- Linux x64

详细说明请参见 [GitHub Actions 打包指南](docs/GITHUB_ACTIONS_PACKAGING.md)

## 自动化测试

本项目使用 GitHub Actions 进行跨平台自动化测试，确保在不同操作系统上的兼容性：

- Windows (x64)
- Linux (x64)

测试工作流会在每次推送代码到 `main` 或 `develop` 分支时自动运行，也会在创建 Pull Request 时触发。

所有测试均已通过修复，确保在不同平台上都能正常运行。

## API接口

### 设备管理
- `GET /api/devices` - 获取所有设备信息
- `GET /api/devices/{mac}` - 获取特定设备信息
- `POST /api/devices` - 创建新设备
- `PUT /api/devices/{mac}` - 更新设备信息
- `DELETE /api/devices/{mac}` - 删除设备
- `PUT /api/devices/{mac}/type` - 更新设备类型

### 健康检查
- `GET /api/health` - 服务器健康检查

### 交换机管理
- `GET /api/switches` - 获取所有交换机配置
- `GET /api/switches/{id}` - 获取特定交换机配置
- `POST /api/switches/create` - 添加交换机配置
- `POST /api/switches/update` - 更新交换机配置
- `POST /api/switches/delete` - 删除交换机配置

详细API文档请参见 [交换机API文档](docs/SWITCH_API.md)

## 技术栈

- Python 3.7+
- SQLite（数据库）
- Socket编程（TCP/UDP通信）
- Flask（Web API）
- pysnmp（SNMP监控）
- threading（并发处理）

## 文档

- [项目结构说明](docs/PROJECT_STRUCTURE.md)
- [模块设计](docs/MODULE_DESIGN.md)
- [接口规范](docs/INTERFACE_SPEC.md)
- [开发计划](docs/开发计划.md)
- [数据库模块重构说明](docs/DATABASE_MIGRATION_GUIDE.md)
- [变更日志](docs/CHANGELOG.md)
- [API文档](docs/API_DOCUMENTATION.md)
- [交换机API文档](docs/SWITCH_API.md)
- [仪表盘说明](docs/DASHBOARD_README.md)
- [SHA认证支持](docs/SHA_AUTH_SUPPORT.md)
- [状态管理器](docs/STATE_MANAGER.md)
- [路由器配置指南](docs/ROUTER_CONFIG_GUIDE.md)
- [打包说明](docs/PACKAGING.md)
- [GitHub Actions 打包指南](docs/GITHUB_ACTIONS_PACKAGING.md)

## 许可证

MIT License