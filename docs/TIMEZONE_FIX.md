# 时区问题修复文档

## 问题描述

在之前的实现中，时间处理存在不一致的问题：

1. **数据库层**：SQLite 使用 `CURRENT_TIMESTAMP` 或 `datetime('now')`，返回的是 **UTC 时间**
2. **Python 模型层**：使用 `datetime.now().isoformat()`，返回的是 **本地时间**（但没有时区标识）
3. **结果**：时间显示不准确，可能相差数小时（取决于时区）

## 解决方案

统一使用**本地时间**（因为这是一个局域网管理系统，使用本地时间更直观）。

### 修改内容

#### 1. SQLite 时间函数
将所有 `datetime('now')` 改为 `datetime('now', 'localtime')`

**修改位置：**
- 表结构的 DEFAULT 值
- INSERT 语句中的时间字段
- UPDATE 语句中的时间字段

#### 2. Python 时间格式
将 `datetime.now().isoformat()` 改为 `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`

**原因：**
- 保持与数据库格式一致
- 更易读的时间格式
- 与项目其他部分保持一致

## 修改的文件

### 模型层
- [`server/src/models/switch_info.py`](server/src/models/switch_info.py)
  - `created_at` 和 `updated_at` 使用本地时间格式

### 数据库管理器
- [`server/src/database/managers/device_manager.py`](server/src/database/managers/device_manager.py)
  - `init_tables()`: 表定义使用 `datetime('now', 'localtime')`
  - `create_device()`: INSERT 使用 `datetime('now', 'localtime')`

- [`server/src/database/managers/switch_manager.py`](server/src/database/managers/switch_manager.py)
  - `init_tables()`: 表定义使用 `datetime('now', 'localtime')`
  - `add_switch()`: INSERT 使用 `datetime('now', 'localtime')`
  - `update_switch()`: UPDATE 使用 `datetime('now', 'localtime')`

### 数据库迁移
- [`server/migrations/fix_timezone_issue.py`](server/migrations/fix_timezone_issue.py)
  - 修复已存在表的时区问题
  - 重建表结构以使用本地时间

## 使用方法

### 1. 对于新部署
新建的表会自动使用本地时间，无需额外操作。

### 2. 对于已有数据库
运行迁移脚本修复时区问题：

```bash
cd server
python migrations/fix_timezone_issue.py
```

**脚本功能：**
1. 创建新表结构（使用本地时间）
2. 复制旧数据到新表
3. 删除旧表
4. 重命名新表
5. 重建索引

**安全性：**
- 原有数据完全保留
- 使用事务确保数据一致性
- 如果失败会自动回滚

## 验证

### 验证时间是否正确

1. **创建新交换机**：
```python
from src.models.switch_info import SwitchInfo
switch = SwitchInfo(ip="192.168.1.1", snmp_version="2c")
print(switch.created_at)  # 应该显示当前本地时间
```

2. **查看数据库**：
```sql
-- 查看 device_info 表结构
PRAGMA table_info(device_info);

-- 查看 switch_info 表结构
PRAGMA table_info(switch_info);

-- 插入测试数据
INSERT INTO switch_info (ip, snmp_version) VALUES ('192.168.1.1', '2c');

-- 查看插入的时间
SELECT created_at, updated_at FROM switch_info ORDER BY id DESC LIMIT 1;
```

3. **对比时间**：
   - Python: `datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
   - SQLite: `SELECT datetime('now', 'localtime')`
   - 两者应该一致

## 时间格式说明

### 统一格式
```
2025-10-17 09:30:45
```

**格式**: `YYYY-MM-DD HH:MM:SS`

### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `created_at` | 创建时间（本地时间） | `2025-10-17 09:30:45` |
| `updated_at` | 更新时间（本地时间） | `2025-10-17 09:35:20` |
| `timestamp` | 时间戳（本地时间） | `2025-10-17 09:30:45` |

## 注意事项

### 1. 时区一致性
- 确保服务器系统时区设置正确
- 所有服务器应使用相同的时区
- 如果需要跨时区部署，考虑改用 UTC

### 2. 旧数据兼容性
- 迁移脚本会保留所有旧数据
- 旧数据的时间值不会改变
- 只是将来新插入的数据会使用本地时间

### 3. 数据库备份
运行迁移前建议备份数据库：
```bash
cp net_manager_server.db net_manager_server.db.backup
```

## SQLite 时间函数参考

### 常用函数
```sql
-- UTC 时间
SELECT datetime('now');                    -- 2025-10-17 01:30:45

-- 本地时间
SELECT datetime('now', 'localtime');       -- 2025-10-17 09:30:45

-- 格式化
SELECT strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime');
```

### 时间修饰符
```sql
-- 加减时间
SELECT datetime('now', 'localtime', '+1 day');
SELECT datetime('now', 'localtime', '-1 hour');
SELECT datetime('now', 'localtime', '+1 month');
```

## 相关资源

- [SQLite Date And Time Functions](https://www.sqlite.org/lang_datefunc.html)
- [Python datetime Documentation](https://docs.python.org/3/library/datetime.html)

## 总结

修复后的时间处理方案：
- ✅ **统一使用本地时间**
- ✅ **格式统一**: `YYYY-MM-DD HH:MM:SS`
- ✅ **数据库和 Python 代码一致**
- ✅ **易读易用**
- ✅ **适合局域网环境**

如果未来需要支持跨时区部署，建议：
1. 改用 UTC 时间存储
2. 在前端进行时区转换
3. 在 API 响应中包含时区信息
