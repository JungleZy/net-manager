# 数据库迁移说明

## 迁移脚本：添加 device_type 字段到 switch_info 表

### 背景
为了支持更精确的设备分类和拓扑图展示，需要为交换机表添加 `device_type` 字段，用于存储设备类型（如：交换机、路由器、防火墙等）。

### 迁移内容
- **表名**: `switch_info`
- **新增字段**: `device_type TEXT DEFAULT ''`
- **默认值**: 空字符串

### 运行迁移

#### 方法1：直接运行Python脚本
```bash
cd server
python migrations/add_device_type_to_switch.py
```

#### 方法2：从项目根目录运行
```bash
python server/migrations/add_device_type_to_switch.py
```

### 迁移验证
迁移脚本会自动验证字段是否添加成功，输出信息如下：

**成功示例**:
```
============================================================
数据库迁移：为 switch_info 表添加 device_type 字段
============================================================
正在添加 device_type 字段到 switch_info 表...
✓ 迁移成功：已添加 device_type 字段
✓ 验证成功：device_type 字段已成功添加

迁移完成！
============================================================
```

**已迁移**:
```
============================================================
数据库迁移：为 switch_info 表添加 device_type 字段
============================================================
字段 device_type 已存在，跳过迁移

迁移完成！
============================================================
```

### 影响范围

#### 后端变更
1. **模型层** (`src/models/switch_info.py`)
   - 添加 `device_type` 字段到 `SwitchInfo` 类
   - 更新 `to_dict()` 和 `from_dict()` 方法

2. **数据库层** (`src/database/managers/switch_manager.py`)
   - 更新表结构定义
   - 更新所有 CRUD 操作的 SQL 语句
   - 更新查询结果映射

#### 前端变更
1. **组件** (`src/components/devices/SwitchAddModal.vue`)
   - 添加设备类型选择器
   - 支持的类型：交换机、路由器、防火墙、服务器、其他

2. **视图** (`src/views/devices/SNMPDevicesTab.vue`)
   - 表格增加"设备类型"列
   - 初始化数据包含 `device_type` 字段

3. **拓扑图** (`src/views/topology/Topology.vue`)
   - 根据 `device_type` 自动选择对应的图标和节点类型
   - 支持动态显示不同类型的设备

### 支持的设备类型
- 交换机 (默认)
- 路由器
- 防火墙
- 服务器
- 打印机
- 笔记本
- 电脑
- 其他

### 回滚方案
如果需要回滚此迁移，可以执行以下SQL（注意：SQLite不支持DROP COLUMN，需要重建表）：

```sql
-- 备份数据
CREATE TABLE switch_info_backup AS SELECT * FROM switch_info;

-- 删除原表
DROP TABLE switch_info;

-- 创建不含device_type的新表
CREATE TABLE switch_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL UNIQUE,
    snmp_version TEXT NOT NULL,
    community TEXT,
    user TEXT,
    auth_key TEXT,
    auth_protocol TEXT,
    priv_key TEXT,
    priv_protocol TEXT,
    description TEXT,
    device_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 恢复数据（不包含device_type）
INSERT INTO switch_info (id, ip, snmp_version, community, user, auth_key, auth_protocol, priv_key, priv_protocol, description, device_name, created_at, updated_at)
SELECT id, ip, snmp_version, community, user, auth_key, auth_protocol, priv_key, priv_protocol, description, device_name, created_at, updated_at
FROM switch_info_backup;

-- 删除备份表
DROP TABLE switch_info_backup;
```

### 注意事项
1. 迁移前建议备份数据库文件
2. 迁移脚本是幂等的，可以多次运行
3. 现有数据的 `device_type` 默认为空字符串
4. 前端会根据空的 `device_type` 自动使用默认值"交换机"
