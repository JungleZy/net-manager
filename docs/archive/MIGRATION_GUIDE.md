# Net Manager Server 迁移指南

## 1. 概述

本文档旨在指导开发人员将现有代码迁移到新的模块化架构中，确保迁移过程平滑且不影响现有功能。

## 2. 迁移准备

### 2.1 环境准备
- 确保Python版本 >= 3.8
- 安装最新的依赖包
- 备份现有代码和数据库

### 2.2 测试环境搭建
- 配置测试数据库
- 准备测试数据
- 确保所有测试用例可运行

## 3. 迁移步骤

### 3.1 阶段1：核心模块迁移

#### 3.1.1 配置管理迁移
1. 将现有的`config.py`重构为`core/config_manager.py`
2. 保持原有配置项的兼容性
3. 添加环境变量支持
4. 实现配置变更通知机制

#### 3.1.2 依赖注入容器实现
1. 创建`core/di_container.py`
2. 实现基本的依赖注入功能
3. 注册核心服务

#### 3.1.3 日志模块迁移
1. 将`logger.py`重构为`utils/logger.py`
2. 实现新的日志接口
3. 保持原有日志格式兼容

### 3.2 阶段2：数据模型迁移

#### 3.2.1 系统信息模型
1. 将`system_info.py`重构为`models/system_info.py`
2. 添加数据验证功能
3. 实现序列化接口

#### 3.2.2 设备模型
1. 创建`models/device.py`
2. 实现设备相关数据结构
3. 添加设备状态管理

### 3.3 阶段3：数据库模块迁移

#### 3.3.1 数据库接口定义
1. 创建`database/interfaces/database_interface.py`
2. 定义所有数据库操作接口
3. 保持与现有方法的兼容性

#### 3.3.2 SQLite实现重构
1. 将`database_manager.py`重构为`database/implementations/sqlite_database.py`
2. 实现数据库接口
3. 添加异步操作支持

#### 3.3.3 数据库工厂实现
1. 创建`database/factories/database_factory.py`
2. 实现数据库实例创建逻辑
3. 支持配置驱动的数据库选择

### 3.4 阶段4：网络模块迁移

#### 3.4.1 TCP服务器重构
1. 将`tcp_server.py`重构为`network/tcp/tcp_server.py`
2. 实现网络服务接口
3. 保持现有功能不变

#### 3.4.2 UDP服务器重构
1. 将`udp_server.py`重构为`network/udp/udp_server.py`
2. 实现网络服务接口
3. 优化UDP处理逻辑

#### 3.4.3 API服务重构
1. 将`api_server.py`重构为`network/api/api_server.py`
2. 实现网络服务接口
3. 保持REST API接口兼容

#### 3.4.4 SNMP模块重构
1. 将`snmp/`目录结构保持不变
2. 优化模块导入方式
3. 添加异步支持

### 3.5 阶段5：服务层实现

#### 3.5.1 系统信息服务
1. 创建`services/system_service.py`
2. 实现系统信息服务接口
3. 协调数据模型和数据库操作

#### 3.5.2 设备管理服务
1. 创建`services/device_service.py`
2. 实现设备管理服务接口
3. 提供设备配置管理功能

### 3.6 阶段6：应用集成

#### 3.6.1 主入口重构
1. 重构`main.py`使用新的模块结构
2. 通过DI容器获取服务实例
3. 确保应用启动流程正确

#### 3.6.2 配置文件更新
1. 更新配置文件格式
2. 确保向后兼容性
3. 添加新配置项说明

## 4. 导入方式更新

### 4.1 从相对导入改为绝对导入
```python
# 旧方式（相对导入）
from .config import TCP_PORT

# 新方式（绝对导入）
from src.core.config_manager import ConfigManager
```

### 4.2 明确导入需要的对象
```python
# 旧方式
from src.database_manager import *

# 新方式
from src.database.interfaces.database_interface import DatabaseInterface
from src.database.factories.database_factory import DatabaseFactory
```

### 4.3 使用括号分组导入
```python
# 旧方式
from src.exceptions import DatabaseError, DatabaseConnectionError, DatabaseInitializationError

# 新方式
from src.exceptions import (
    DatabaseError, 
    DatabaseConnectionError, 
    DatabaseInitializationError
)
```

## 5. 测试验证

### 5.1 单元测试
- 为新接口编写单元测试
- 确保覆盖率不低于原有水平
- 验证异常处理逻辑

### 5.2 集成测试
- 验证模块间协作正常
- 测试配置管理功能
- 验证异步操作正确性

### 5.3 功能测试
- 运行所有现有测试用例
- 验证功能完整性和正确性
- 性能测试和对比

## 6. 回滚计划

### 6.1 回滚条件
- 关键功能无法正常工作
- 性能严重下降
- 数据一致性问题

### 6.2 回滚步骤
1. 恢复原有代码版本
2. 恢复原有数据库结构
3. 重新部署应用
4. 验证功能正常

## 7. 注意事项

### 7.1 兼容性保持
- 确保API接口向后兼容
- 保持数据库结构兼容
- 维持配置文件格式兼容

### 7.2 性能考虑
- 监控重构后的性能变化
- 优化关键路径代码
- 避免不必要的性能损耗

### 7.3 文档更新
- 及时更新相关文档
- 提供迁移示例代码
- 更新API文档