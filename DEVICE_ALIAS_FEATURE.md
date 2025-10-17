# 设备别名功能实现文档

## 功能概述

为 `device_info` 和 `switch_info` 表添加设备别名（alias）字段，该字段只能通过各自的 UpdateHandler 修改。

## 实现内容

### 1. 数据库变更

#### 新增字段
- **device_info.alias**: TEXT类型，默认值为空字符串
- **switch_info.alias**: TEXT类型，默认值为空字符串

#### 迁移脚本
- 文件: `server/migrations/add_alias_field.py`
- 功能: 自动为两个表添加alias字段（如果不存在）
- 使用方法:
  ```bash
  cd server
  python migrations/add_alias_field.py
  ```

### 2. 模型更新

#### DeviceInfo 模型
文件: `server/src/models/device_info.py`

**变更内容:**
- 添加 `alias` 参数到构造函数
- 在 `to_dict()` 方法中包含 alias 字段
- 在 `from_dict()` 方法中解析 alias 字段

```python
def __init__(
    self,
    # ... 其他参数
    alias: Optional[str] = None,
    **kwargs
):
    # ... 
    self.alias = alias if alias is not None else ""
```

#### SwitchInfo 模型
文件: `server/src/models/switch_info.py`

**变更内容:**
- 添加 `alias` 参数到构造函数（默认为空字符串）
- 在 `to_dict()` 方法中包含 alias 字段
- 在 `from_dict()` 方法中解析 alias 字段
- 更新 `__str__()` 方法包含 alias 信息

```python
def __init__(
    self,
    # ... 其他参数
    alias: str = "",
    # ...
):
    self.alias = alias
```

### 3. 数据库管理器更新

#### DeviceManager
文件: `server/src/database/managers/device_manager.py`

**变更内容:**

1. **init_tables()** - 表初始化
   - 在CREATE TABLE语句中添加 `alias TEXT DEFAULT ''`

2. **save_device_info()** - 保存设备信息
   - 在INSERT OR REPLACE语句中保留alias字段（使用COALESCE保持现有值）
   - 通过TCP更新时不会修改alias字段

3. **get_all_device_info()** - 获取所有设备
   - SELECT语句包含alias字段
   - 返回结果包含alias信息

4. **get_device_info_by_id()** - 根据ID查询
   - SELECT语句包含alias字段
   - 返回结果包含alias信息

5. **get_device_info_by_client_id()** - 根据client_id查询
   - SELECT语句包含alias字段
   - 返回结果包含alias信息

6. **create_device()** - 创建设备
   - INSERT语句包含alias字段（默认为空）

7. **update_device()** - 更新设备
   - UPDATE语句包含alias字段
   - **只能通过此方法修改alias**

#### SwitchManager
文件: `server/src/database/managers/switch_manager.py`

**变更内容:**

1. **init_tables()** - 表初始化
   - 在CREATE TABLE语句中添加 `alias TEXT DEFAULT ''`

2. **add_switch()** - 添加交换机
   - INSERT语句包含alias字段（默认为空）

3. **update_switch()** - 更新交换机
   - UPDATE语句包含alias字段
   - **只能通过此方法修改alias**

4. **get_switch_by_id()** - 根据ID查询
   - SELECT语句包含alias字段
   - 返回结果包含alias信息

5. **get_switch_by_ip()** - 根据IP查询
   - SELECT语句包含alias字段
   - 返回结果包含alias信息

6. **get_all_switches()** - 获取所有交换机
   - SELECT语句包含alias字段
   - 返回结果包含alias信息

### 4. API Handler更新

#### DeviceUpdateHandler
文件: `server/src/network/api/handlers/devices_handlers.py`

**变更内容:**
- 支持从请求数据中读取alias字段
- 通过 `db_manager.update_device()` 更新alias
- 添加注释说明alias字段可以在UpdateHandler中修改

```python
def post(self):
    try:
        data = tornado.escape.json_decode(self.request.body)
        # alias字段可以在UpdateHandler中修改
        success, message = self.db_manager.update_device(data)
```

#### SwitchCreateHandler
文件: `server/src/network/api/handlers/switches_handlers.py`

**变更内容:**
- 创建交换机时，alias设置为空字符串
- 不从请求中读取alias（创建时固定为空）

```python
switch_info = SwitchInfo(
    # ... 其他字段
    alias="",  # 创建时alias为空
)
```

#### SwitchUpdateHandler
文件: `server/src/network/api/handlers/switches_handlers.py`

**变更内容:**
- 支持从请求数据中读取alias字段
- 通过 `db_manager.update_switch()` 更新alias
- 添加注释说明alias字段只能通过UpdateHandler修改

```python
switch_info = SwitchInfo(
    # ... 其他字段
    alias=data.get("alias", ""),  # alias只能通过UpdateHandler修改
)
```

## 使用说明

### 1. 数据库迁移

首次部署或更新时，运行迁移脚本：

```bash
cd server
python migrations/add_alias_field.py
```

或使用验证脚本：

```bash
cd server
python verify_alias_migration.py
```

### 2. API使用示例

#### 更新设备别名

**请求:**
```http
POST /api/devices/update
Content-Type: application/json

{
  "id": "device-001",
  "hostname": "MyComputer",
  "alias": "办公室主机A"
}
```

**响应:**
```json
{
  "status": "success",
  "message": "设备更新成功"
}
```

#### 更新交换机别名

**请求:**
```http
POST /api/switches/update
Content-Type: application/json

{
  "id": 1,
  "ip": "192.168.1.100",
  "snmp_version": "2c",
  "alias": "机房A-核心交换机"
}
```

**响应:**
```json
{
  "status": "success",
  "message": "交换机配置更新成功"
}
```

#### 查询设备（包含别名）

**请求:**
```http
GET /api/devices/device-001
```

**响应:**
```json
{
  "status": "success",
  "data": {
    "id": "device-001",
    "hostname": "MyComputer",
    "alias": "办公室主机A",
    ...
  }
}
```

## 重要约束

### 1. alias字段修改规则

- ✅ **可以修改**: 通过 `DeviceUpdateHandler` 或 `SwitchUpdateHandler`
- ❌ **不能修改**: 
  - 通过TCP客户端上报数据（`save_device_info()`）
  - 通过创建Handler（`DeviceCreateHandler`、`SwitchCreateHandler`）

### 2. 默认值

- 创建设备/交换机时，alias默认为空字符串 `""`
- 通过TCP更新设备信息时，alias保持原值不变

### 3. 数据类型

- 字段类型: TEXT
- 允许空值: 是（默认为空字符串）
- 长度限制: 无（由SQLite TEXT类型决定）

## 测试验证

运行验证脚本确认迁移成功：

```bash
cd server
python verify_alias_migration.py
```

预期输出:
```
============================================================
验证设备别名字段迁移
============================================================

1. 运行数据库迁移...
   ✓ 迁移成功

2. 验证device_info表结构...
   ✓ device_info表包含alias字段 (类型: TEXT)

3. 验证switch_info表结构...
   ✓ switch_info表包含alias字段 (类型: TEXT)

============================================================
🎉 所有验证通过！别名字段已成功添加到数据库
============================================================
```

## 文件清单

### 新增文件
- `server/migrations/add_alias_field.py` - 数据库迁移脚本
- `server/verify_alias_migration.py` - 迁移验证脚本
- `server/test_alias_feature.py` - 功能测试脚本（需要完整依赖）
- `DEVICE_ALIAS_FEATURE.md` - 本文档

### 修改文件
- `server/src/models/device_info.py` - 设备信息模型
- `server/src/models/switch_info.py` - 交换机信息模型
- `server/src/database/managers/device_manager.py` - 设备数据库管理器
- `server/src/database/managers/switch_manager.py` - 交换机数据库管理器
- `server/src/network/api/handlers/devices_handlers.py` - 设备API处理器
- `server/src/network/api/handlers/switches_handlers.py` - 交换机API处理器

## 注意事项

1. **向后兼容**: 迁移脚本会检查字段是否已存在，可以安全地重复运行
2. **数据迁移**: 现有数据的alias字段将自动设置为空字符串
3. **客户端更新**: 通过TCP客户端上报的数据不会影响alias字段
4. **前端集成**: 前端需要在设备/交换机编辑界面添加alias字段输入框

## 后续建议

1. **前端界面**: 在设备管理和交换机管理页面添加别名字段
2. **搜索功能**: 考虑在搜索功能中包含别名字段
3. **显示优先级**: 在列表显示时可以优先显示别名（如果存在）
4. **验证规则**: 可以考虑添加别名长度限制或格式验证
