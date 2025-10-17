# 日志按天切分说明

## 功能概述

服务器端日志已配置为按天自动切分，每天午夜（00:00）会自动创建新的日志文件。

## 配置详情

### 日志文件命名规则

- **当前日志文件**: `logs/net_manager_server`
- **历史日志文件**: `logs/net_manager_server.YYYY-MM-DD.log`

### 示例

```
logs/
├── net_manager_server              # 当前正在写入的日志
├── net_manager_server.2025-10-17.log  # 2025年10月17日的日志
├── net_manager_server.2025-10-16.log  # 2025年10月16日的日志
└── net_manager_server.2025-10-15.log  # 2025年10月15日的日志
```

## 日志保留策略

- **切分时间**: 每天午夜（00:00）
- **切分间隔**: 1天
- **保留天数**: 30天
- **自动清理**: 超过30天的旧日志会被自动删除

## 技术实现

使用Python的 `logging.handlers.TimedRotatingFileHandler` 实现：

```python
file_handler = TimedRotatingFileHandler(
    filename=str(log_file),
    when='midnight',      # 在午夜时切分
    interval=1,           # 每1天切分一次
    backupCount=30,       # 保留最近30天的日志
    encoding=file_encoding
)
file_handler.suffix = '%Y-%m-%d.log'  # 日志文件名后缀格式
```

## 优势

1. **自动管理**: 无需手动管理日志文件
2. **磁盘优化**: 自动清理旧日志，避免磁盘空间耗尽
3. **便于追踪**: 按日期组织，方便查找特定时间的日志
4. **性能优化**: 避免单个日志文件过大影响读写性能

## 查看日志

### 查看当前日志
```bash
# Linux/Mac
tail -f logs/net_manager_server

# Windows (PowerShell)
Get-Content logs/net_manager_server -Wait
```

### 查看历史日志
```bash
# 查看某一天的日志
cat logs/net_manager_server.2025-10-17.log

# 搜索特定内容
grep "ERROR" logs/net_manager_server.2025-10-17.log
```

## 注意事项

1. 日志切分在**服务器运行时**自动进行
2. 如果服务器在午夜时未运行，下次启动时会自动处理
3. 修改 `backupCount` 参数可调整保留天数
4. 日志文件编码自动适配系统（Windows使用GBK，Linux/Mac使用UTF-8）
