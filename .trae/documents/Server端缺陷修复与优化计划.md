## 目标
- 精准记录与分类异常、避免吞异常、提升问题定位能力，同时不改变现有对外行为与返回格式。

## 范围与文件
- `main.py`：清理流程与全局保活循环
- `src/core/state_manager.py`：WebSocket广播与事件回调
- `src/snmp/snmp_monitor.py`：SNMP接口采集与遍历（含`try`块重构）
- `src/snmp/unified_poller.py`：设备/接口轮询器的worker异常路径
- `src/network/tcp/tcp_server.py`：消息接收处理的异常路径

## 具体改动
### main.py
- 将多个宽泛 `except Exception` 改为针对性异常捕获（如 `OSError`、`RuntimeError`、`asyncio.CancelledError`）并使用 `logger.exception` 保留堆栈（参考 73–75、81–83、90–98、106–108、115–117、120–122）。
- 抽取统一 `graceful_shutdown()`，集中关闭 API/TCP/UDP/轮询器与监控线程，使用 `try-except-finally` 保证各子系统独立关闭、互不影响（保留原有日志语义）。

### state_manager.py
- 在事件回调处（231–233）移除 `pass` 吞异常，改为 `logger.exception`；避免单个连接异常影响其他客户端，使用 per-client try/except 包裹并继续广播。
- 为广播方法增加可选 `on_error` 回调，记录失败客户端并清理其连接。

### snmp_monitor.py
- 针对大段单一 `try`（如 1098 附近），拆分为更小的阶段性 `try`：
  - 会话建立/验证阶段
  - OID 获取/批量遍历阶段
  - 结果归并/速率计算阶段
- 在每阶段捕获并分类异常（`TimeoutError`、`ValueError`、`pysnmp`特定异常），写入 `logger.exception`，并在返回结构加入非破坏性 `errors` 字段（仅内部使用，不改变当前外部 API 响应）。
- 保持现有功能：若部分 OID 失败，返回已有成功数据，并在日志中可定位失败源（设备/IP、OID、阶段）。

### unified_poller.py
- 在 worker 协程与线程桥接处，增加 per-task try/except，使用 `logger.exception` 记录失败任务，不使异常冒泡中断事件循环（35–118、198–205、319–435）。
- 在结果聚合处加入失败计数与最近错误摘要日志，仍保持对外广播的成功条目。

### tcp_server.py
- 在 `_process_client_data` 与 `_recv_all` 的异常路径中，区分 `ConnectionResetError`、`OSError`、`UnicodeDecodeError`、`ValueError` 等，统一 `logger.exception`，并优先关闭对应客户端套接字（130–212、300–308）。
- 保持现有协议与行为，不加入新的超时或大小限制（这些属于后续阶段）。

## 日志与分类规范
- 统一使用：`logger.exception("<模块>/<阶段> 失败", extra={"peer": ip, "device": id, "oid": x})`
- 分级：
  - `error`：影响当前任务但可继续运行
  - `warning`：非关键字段缺失或降级处理
  - `info`：阶段性成功与数量统计

## 测试用例（新增）
- main 清理流程：模拟子系统关闭抛出异常，断言未影响其他子系统关闭且日志包含堆栈。
- state_manager 广播：模拟某客户端回调抛错，断言其他客户端仍收到消息，日志记录异常而无崩溃。
- snmp_monitor 分阶段异常：
  - 模拟会话建立异常与 OID 遍历异常，断言成功部分返回且日志包含异常分类；不改变现有函数的返回类型与字段。
- unified_poller worker：模拟单任务失败，断言事件循环未中断，失败任务被记录。
- tcp_server 接收：模拟粘包/半包与异常数据，断言连接被关闭且异常分类正确记录。

## 验收标准
- 所有新增测试通过；原有测试不回归。
- 关键路径出现异常时，日志包含堆栈与分类信息，可定位到文件/函数/阶段。
- 对外接口的成功与失败语义保持现状，无破坏性变更。

## 风险与回滚
- 仅修改异常处理与日志，不改动业务协议；若出现问题，可通过分支开关恢复为原始捕获方式（保留一次性开关变量）。

## 交付物
- 以上文件的异常处理重构与日志增强
- 新增针对性测试文件与用例
- 简要运维说明：异常分类与常见定位步骤