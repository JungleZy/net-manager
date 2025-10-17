# SNMP轮询器快速参考卡片

## 🎯 快速启动

### 设备信息轮询器
```python
from src.snmp.continuous_poller import start_snmp_poller

poller = start_snmp_poller(
    switch_manager,
    poll_interval=10,        # 10秒轮询
    min_workers=5,           # 最小5并发
    max_workers=20,          # 最大20并发
    device_timeout=30,       # 30秒超时
    dynamic_adjustment=True, # 动态调整
)
```

### 接口信息轮询器
```python
from src.snmp.interface_poller import start_interface_poller

poller = start_interface_poller(
    switch_manager,
    poll_interval=30,        # 30秒轮询
    min_workers=5,           # 最小5并发
    max_workers=30,          # 最大30并发
    device_timeout=60,       # 60秒超时
    dynamic_adjustment=True, # 动态调整
)
```

## 📊 获取统计

```python
stats = poller.get_statistics()

# 关键指标
print(f"成功率: {stats['success_count'] / stats['total_polls'] * 100:.1f}%")
print(f"当前并发: {stats['current_concurrency']}")
print(f"队列大小: {stats['queue_size']}")
print(f"平均响应: {stats['avg_response_time']:.2f}秒")
print(f"P95响应: {stats['p95_response_time']:.2f}秒")
```

## 📡 WebSocket消息

### 设备信息更新
```javascript
ws.on('snmpDeviceUpdate', (data) => {
    const device = data.data;
    console.log(`设备 ${device.ip} 更新:`, device.device_info);
});
```

### 接口信息更新
```javascript
ws.on('snmpInterfaceUpdate', (data) => {
    const interfaces = data.data;
    console.log(`设备 ${interfaces.ip} 接口:`, interfaces.interface_info);
});
```

## ⚙️ 配置推荐

### 小规模（<10设备）
```python
min_workers=3, max_workers=10
```

### 中规模（10-50设备）
```python
min_workers=5, max_workers=20
```

### 大规模（50-100设备）
```python
min_workers=10, max_workers=30
```

### 超大规模（100+设备）
```python
min_workers=15, max_workers=50
```

## 🔧 常用操作

### 停止轮询器
```python
from src.snmp.continuous_poller import stop_snmp_poller
from src.snmp.interface_poller import stop_interface_poller

stop_snmp_poller()
stop_interface_poller()
```

### 获取轮询器实例
```python
from src.snmp.continuous_poller import get_snmp_poller
from src.snmp.interface_poller import get_interface_poller

device_poller = get_snmp_poller()
interface_poller = get_interface_poller()
```

### 检查运行状态
```python
if poller.is_running:
    print("轮询器正在运行")
```

## 📈 健康检查

### 正常状态
```python
✅ 成功率 >90%
✅ 平均响应 <2秒
✅ P95响应 <4秒
✅ 队列积压 <20
✅ 失败设备 <5%
```

### 异常状态处理

#### 成功率低 (<70%)
```python
# 检查：
1. 网络连通性
2. SNMP配置是否正确
3. 设备是否在线
4. 查看 failed_devices 列表
```

#### 响应慢 (P95>5秒)
```python
# 调整：
1. 降低 max_workers
2. 增加 device_timeout
3. 检查网络延迟
4. 查看 highly_failed_devices
```

#### 队列积压 (>50)
```python
# 优化：
1. 增加 max_workers
2. 减少 poll_interval
3. 启用缓存
4. 检查设备数量
```

## 🎨 动态调整策略

### 自动增加并发
```
条件: 队列>20 且 P95响应<2.5秒
动作: 并发+5（最多到max_workers）
```

### 自动降低并发
```
条件: P95响应>4秒 且 成功率<70%
动作: 并发-3（最少到min_workers）
```

### 资源优化
```
条件: 队列<5 且 活跃工作<30%
动作: 并发-2（最少到min_workers）
```

## 🐛 故障排查

### 问题1: 轮询器无法启动
```python
# 检查：
1. 数据库连接是否正常
2. SwitchManager 是否初始化
3. 端口是否被占用
4. 查看日志错误信息
```

### 问题2: 并发数不调整
```python
# 检查：
1. dynamic_adjustment=True
2. 数据样本是否足够（>10次）
3. 是否满足调整条件
4. 查看调整日志
```

### 问题3: 消息未推送
```python
# 检查：
1. WebSocket连接是否正常
2. state_manager 是否初始化
3. 网络是否畅通
4. 查看发送错误日志
```

### 问题4: 内存持续增长
```python
# 优化：
1. 降低 cache_ttl
2. 减少 max_workers
3. 检查是否有内存泄漏
4. 重启轮询器
```

## 📝 日志级别

### DEBUG
```
设备入队、工作协程、缓存命中
```

### INFO
```
启动/停止、并发调整、批次处理
```

### WARNING
```
重复启动、高失败率设备
```

### ERROR
```
轮询失败、发送失败、异常错误
```

## 🔗 相关文件

### 核心代码
- `continuous_poller.py` - 设备信息轮询器
- `interface_poller.py` - 接口信息轮询器

### 文档
- `UNIFIED_REFACTOR_SUMMARY.md` - 完整重构总结
- `REFACTOR_COMPARISON.md` - 新旧架构对比
- `interface_poller_queue_architecture.md` - 架构详解

### 示例
- `examples/interface_poller_queue_example.py` - 使用示例
- `tests/test_interface_poller_refactor.py` - 功能验证

## 💡 最佳实践

### 1. 合理配置并发
```python
# 根据设备数量选择合适的并发范围
# 总并发不超过100
# min_workers 约为设备数的5%
# max_workers 约为设备数的30%
```

### 2. 启用缓存
```python
enable_cache=True   # 减少重复请求
cache_ttl=300       # 5分钟TTL
```

### 3. 设置合理超时
```python
# 设备信息: 30秒（数据较少）
# 接口信息: 60秒（数据较多）
```

### 4. 监控关键指标
```python
# 定期检查：
- 成功率
- 响应时间
- 队列大小
- 失败设备
```

### 5. 分层轮询频率
```python
# 设备信息: 10秒（重要且快速）
# 接口信息: 30秒（数据量大）
```

## 🎯 性能调优

### 优化响应速度
```python
min_workers=10      # 提高最小并发
poll_interval=5     # 缩短轮询间隔
enable_cache=True   # 启用缓存
```

### 优化资源占用
```python
max_workers=20      # 限制最大并发
cache_ttl=600       # 延长缓存时间
device_timeout=10   # 快速失败
```

### 平衡性能和资源
```python
min_workers=5       # 适中最小并发
max_workers=30      # 适中最大并发
dynamic_adjustment=True  # 自动调整
```

---

**版本**: 2.0（队列模式）  
**更新时间**: 2025-10-17  
**状态**: ✅ 生产就绪
