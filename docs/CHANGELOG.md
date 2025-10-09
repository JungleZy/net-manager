# 变更日志 (Changelog)

## [1.0.0] - 2025-10-09

### 重构
- 数据库模块重构，将单一的database_manager.py拆分为多个专门的管理器类
  - BaseDatabaseManager: 基础数据库管理器
  - DeviceManager: 设备信息管理器
  - SwitchManager: 交换机信息管理器
  - DatabaseManager: 组合管理器，提供统一接口

### 新增
- 提供向后兼容的使用方式，现有代码可无缝迁移
- 提供新的推荐使用方式，支持更细粒度的数据库操作

### 修改
- 更新所有相关文件的导入路径，从`src.database.database_manager`改为`src.database`
- 更新SystemInfo和SwitchInfo模型的使用示例，修复参数不匹配的问题

### 文档
- 添加数据库迁移指南 (DATABASE_MIGRATION_GUIDE.md)
- 更新数据库模块说明文档

### 测试
- 所有数据库相关测试通过
- 所有示例代码运行正常
- 主程序可以正常启动