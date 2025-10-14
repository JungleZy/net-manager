# 拓扑图信息管理模块 (Topology Info Management)

本模块提供拓扑图信息的数据库存储和管理功能。

## 功能特性

- ✅ 拓扑图信息的增删改查操作
- ✅ 自动时间戳记录
- ✅ 线程安全的数据库操作
- ✅ 连接池管理
- ✅ 完善的异常处理

## 数据库表结构

### topology_info 表

| 字段名     | 类型     | 说明                      |
| ---------- | -------- | ------------------------- |
| id         | INTEGER  | 主键，自增                |
| content    | TEXT     | 拓扑图内容（JSON 字符串） |
| created_at | DATETIME | 创建时间，默认当前时间    |

## 使用方法

### 1. 导入模块

```python
from src.database.managers.topology_manager import TopologyManager
from src.models.topology_info import TopologyInfo
import json
```

### 2. 创建管理器实例

```python
topology_manager = TopologyManager(db_path="net_manager_server.db")
```

### 3. 保存拓扑图

```python
# 创建拓扑图数据
topology_data = {
    "nodes": [
        {"id": "1", "type": "router", "label": "核心路由器", "x": 100, "y": 100},
        {"id": "2", "type": "switch", "label": "交换机1", "x": 200, "y": 200},
    ],
    "edges": [
        {"source": "1", "target": "2"}
    ]
}

# 转换为JSON字符串
content = json.dumps(topology_data, ensure_ascii=False)

# 创建TopologyInfo对象
topology_info = TopologyInfo(content=content)

# 保存到数据库
topology_id = topology_manager.save_topology(topology_info)
print(f"保存成功，ID: {topology_id}")
```

### 4. 查询拓扑图

```python
# 根据ID查询
topology = topology_manager.get_topology_by_id(topology_id)
if topology:
    print(f"ID: {topology['id']}")
    print(f"内容: {topology['content']}")
    print(f"创建时间: {topology['created_at']}")

# 查询最新的拓扑图
latest_topology = topology_manager.get_latest_topology()

# 查询所有拓扑图
all_topologies = topology_manager.get_all_topologies()
```

### 5. 更新拓扑图

```python
# 更新拓扑图内容
updated_data = {
    "nodes": [
        {"id": "1", "type": "router", "label": "核心路由器", "x": 100, "y": 100},
        {"id": "2", "type": "switch", "label": "交换机1", "x": 200, "y": 200},
        {"id": "3", "type": "pc", "label": "电脑1", "x": 300, "y": 300},
    ],
    "edges": [
        {"source": "1", "target": "2"},
        {"source": "2", "target": "3"}
    ]
}

updated_content = json.dumps(updated_data, ensure_ascii=False)
success = topology_manager.update_topology(topology_id, updated_content)
print(f"更新{'成功' if success else '失败'}")
```

### 6. 删除拓扑图

```python
success = topology_manager.delete_topology(topology_id)
print(f"删除{'成功' if success else '失败'}")
```

### 7. 统计信息

```python
# 获取拓扑图总数
count = topology_manager.get_topology_count()
print(f"拓扑图总数: {count}")
```

## API 方法说明

### TopologyManager 类方法

| 方法名                | 参数                             | 返回值           | 说明                      |
| --------------------- | -------------------------------- | ---------------- | ------------------------- |
| `save_topology`       | `topology_info: TopologyInfo`    | `int`            | 保存拓扑图，返回新记录 ID |
| `get_topology_by_id`  | `topology_id: int`               | `Optional[Dict]` | 根据 ID 查询拓扑图        |
| `get_latest_topology` | 无                               | `Optional[Dict]` | 获取最新的拓扑图          |
| `get_all_topologies`  | 无                               | `List[Dict]`     | 获取所有拓扑图            |
| `update_topology`     | `topology_id: int, content: str` | `bool`           | 更新拓扑图内容            |
| `delete_topology`     | `topology_id: int`               | `bool`           | 删除拓扑图                |
| `get_topology_count`  | 无                               | `int`            | 获取拓扑图总数            |

### TopologyInfo 模型

| 属性         | 类型  | 说明                      |
| ------------ | ----- | ------------------------- |
| `id`         | `str` | 拓扑图 ID                 |
| `content`    | `str` | 拓扑图内容（JSON 字符串） |
| `created_at` | `str` | 创建时间                  |

| 方法              | 说明           |
| ----------------- | -------------- |
| `to_dict()`       | 转换为字典     |
| `from_dict(data)` | 从字典创建实例 |

## 示例程序

运行示例程序来了解完整使用流程：

```bash
# 在server目录下运行
cd server
$env:PYTHONPATH="."; python examples\topology_usage_example.py
```

## 异常处理

模块使用以下异常类型：

- `DatabaseError` - 通用数据库错误
- `DatabaseQueryError` - 数据库查询错误
- `DatabaseConnectionError` - 数据库连接错误

示例：

```python
from src.database.db_exceptions import DatabaseQueryError

try:
    topology = topology_manager.get_topology_by_id(1)
except DatabaseQueryError as e:
    print(f"查询失败: {e}")
```

## 最佳实践

1. **使用连接池**：管理器已内置连接池，无需手动管理连接
2. **异常处理**：始终捕获并处理可能的数据库异常
3. **JSON 格式**：确保 content 字段存储有效的 JSON 字符串
4. **线程安全**：管理器内部已实现线程安全，可在多线程环境中使用

## 文件位置

- 模型文件：`server/src/models/topology_info.py`
- 管理器文件：`server/src/database/managers/topology_manager.py`
- 示例文件：`server/examples/topology_usage_example.py`
- 本文档：`server/src/database/managers/TOPOLOGY_README.md`
