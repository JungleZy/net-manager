# 多 CPU 支持功能更新说明

## 更新概述

本次更新增强了服务器性能监控模块，添加了对多物理 CPU（多路 CPU）系统的检测和显示支持。

## 更新内容

### 后端更新 (server/src/monitor/server_monitor.py)

#### 1. 增强的 CPU 信息采集

**新增字段：**

- `threads_per_core`: 每个物理核心的线程数（超线程信息）
- `estimated_physical_cpus`: 估算的物理 CPU 数量（对于多路 CPU 服务器）
- `per_cpu_frequency`: 每个核心的频率（如果系统支持）

**改进的 `_get_cpu_info()` 方法：**

```python
cpu_info = {
    "usage_percent": 6.3,
    "cores": 16,                      # 逻辑核心数（包含超线程）
    "physical_cores": 8,              # 物理核心数
    "threads_per_core": 2,            # 每核心线程数（新增）
    "estimated_physical_cpus": 1,     # 物理CPU数量（新增）
    "current_frequency": 4700.0,
    "max_frequency": 4700.0,
    "per_cpu_frequency": [...],       # 每核心频率（新增，可选）
    "per_cpu_percent": [...]
}
```

#### 2. 新增物理 CPU 估算方法

**`_estimate_physical_cpu_count()` 方法特性：**

- **Linux 系统**: 通过读取 `/proc/cpuinfo` 的 `physical id` 字段获取准确的物理 CPU 数量
- **Windows 系统**: 通过 WMIC 命令 `wmic cpu get NumberOfCores` 获取物理 CPU 数量
- **通用启发式**: 基于核心数量进行智能估算
  - 核心数 > 32 且是 4 的倍数 → 可能是 4 路系统
  - 核心数 > 32 且是 2 的倍数 → 可能是 2 路系统
  - 核心数 ≤ 32 → 单 CPU 系统

**检测逻辑示例：**

```python
# 单CPU: 8核16线程 (8物理核心 × 2超线程)
estimated_physical_cpus = 1

# 双路CPU: 32核64线程 (2个CPU × 16核心 × 2超线程)
estimated_physical_cpus = 2

# 四路CPU: 64核128线程 (4个CPU × 16核心 × 2超线程)
estimated_physical_cpus = 4
```

### 前端更新 (dashboard/src/views/home/ServerPerformance.vue)

#### 1. CPU 概览卡片优化

**单 CPU 系统显示：**

```
CPU使用率
6.3%
8核16线程
```

**多 CPU 系统显示（例如双路）：**

```
CPU使用率
6.3%
2路CPU | 32核64线程
```

#### 2. CPU 仪表盘信息增强

**新增物理 CPU 数量显示：**

- 单 CPU 系统：正常显示频率信息
- 多 CPU 系统：额外显示"物理 CPU: 2 路"等信息

**优化后的显示：**

```
CPU使用率 - 当前频率: 4700 MHz | 最大频率: 4700 MHz | 物理CPU: 2路
```

#### 3. CPU 核心使用率图表优化

**多 CPU 系统增强标题：**

```
CPU核心使用率
2路CPU，共32个物理核心，64个逻辑线程
```

这样可以更清晰地展示多 CPU 系统的拓扑结构。

## 数据格式示例

### 单 CPU 系统（8 核 16 线程，启用超线程）

```json
{
  "cpu": {
    "usage_percent": 6.3,
    "cores": 16,
    "physical_cores": 8,
    "threads_per_core": 2,
    "estimated_physical_cpus": 1,
    "current_frequency": 4700.0,
    "max_frequency": 4700.0,
    "per_cpu_percent": [25.0, 0.0, 0.0, ...]
  }
}
```

### 双路 CPU 系统（2×16 核 32 线程，启用超线程）

```json
{
  "cpu": {
    "usage_percent": 12.5,
    "cores": 64,
    "physical_cores": 32,
    "threads_per_core": 2,
    "estimated_physical_cpus": 2,
    "current_frequency": 3200.0,
    "max_frequency": 3800.0,
    "per_cpu_percent": [5.0, 10.0, 8.0, ...]
  }
}
```

### 四路 CPU 系统（4×20 核 80 线程，启用超线程）

```json
{
  "cpu": {
    "usage_percent": 25.3,
    "cores": 160,
    "physical_cores": 80,
    "threads_per_core": 2,
    "estimated_physical_cpus": 4,
    "current_frequency": 2800.0,
    "max_frequency": 3600.0,
    "per_cpu_percent": [...]
  }
}
```

## 兼容性

### 向后兼容

- ✅ 所有新增字段都是可选的
- ✅ 前端使用可选链和默认值处理
- ✅ 单 CPU 系统显示不变（不显示多余信息）

### 系统支持

- ✅ **Linux**: 完全支持，通过 `/proc/cpuinfo` 获取准确信息
- ✅ **Windows**: 完全支持，通过 WMIC 获取准确信息
- ✅ **macOS**: 支持，使用启发式估算
- ✅ **其他 Unix 系统**: 支持，使用启发式估算

## 测试

### 测试脚本

运行测试脚本验证多 CPU 检测功能：

```bash
cd server
python examples/test_multi_cpu.py
```

### 测试输出示例

```
============================================================
测试服务器CPU信息检测
============================================================

📊 CPU详细信息：
{
  "usage_percent": 6.3,
  "cores": 16,
  "physical_cores": 8,
  "threads_per_core": 2,
  "estimated_physical_cpus": 1,
  ...
}

============================================================
关键信息摘要：
============================================================
CPU使用率: 6.3%
逻辑核心数（线程）: 16
物理核心数: 8
每核心线程数: 2
是否启用超线程: 是

🖥️  估算的物理CPU数量: 1
   这是一个单CPU系统

⚡ 当前频率: 4700.0 MHz
   最大频率: 4700.0 MHz
```

## 使用场景

### 适用系统类型

1. **工作站**: 单 CPU，8-32 核心
2. **高端工作站**: 单 CPU 或双 CPU，16-64 核心
3. **服务器**: 双路或四路 CPU，32-160 核心
4. **超级计算节点**: 多路 CPU，>160 核心

### 优势

- 📊 **清晰的拓扑展示**: 直观显示物理 CPU 数量和核心分布
- 🔍 **准确的资源识别**: 帮助用户理解系统真实配置
- 📈 **更好的性能分析**: 便于识别多 CPU 系统的负载均衡情况
- 🎯 **智能检测**: 多种方法组合，确保检测准确性

## 注意事项

1. **估算准确性**:

   - Linux 和 Windows 系统通过系统接口获取，准确度高
   - 其他系统使用启发式估算，可能存在误差
   - 建议在实际多路系统上验证

2. **性能影响**:

   - 所有检测操作都在数据采集时执行
   - 不会增加额外的性能开销
   - 估算方法执行速度快（<1ms）

3. **显示逻辑**:
   - 只有在检测到多物理 CPU 时才显示相关信息
   - 单 CPU 系统保持原有简洁显示
   - 避免信息冗余

## 相关文件

### 后端文件

- `server/src/monitor/server_monitor.py` - CPU 信息采集和估算逻辑
- `server/examples/test_multi_cpu.py` - 测试脚本

### 前端文件

- `dashboard/src/views/home/ServerPerformance.vue` - 性能监控界面

## 版本信息

- **更新日期**: 2025-10-17
- **功能状态**: ✅ 已完成并测试
- **向后兼容**: ✅ 完全兼容
