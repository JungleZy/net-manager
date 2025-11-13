## 目标
- 按照内网需求，移除 TCP 消息长度上限检查，避免因载荷较大而被拒绝。
- 保留接收超时与现有协议逻辑，确保异常客户端不会无限阻塞线程。

## 范围与文件
- `server/src/network/tcp/tcp_server.py`
- `server/src/core/config.py`（保留参数但本次不使用）

## 具体改动
- 在握手与常规消息路径移除 `message_length > TCP_MAX_MESSAGE_SIZE` 的判断与早退，保留原有接收流程：
  - 握手长度检查删除：`server/src/network/tcp/tcp_server.py:59`
  - 常规消息长度检查删除：`server/src/network/tcp/tcp_server.py:96`
- 保留 `TCP_RECV_TIMEOUT` 超时设置与超时处理。
- 配置中的 `TCP_MAX_MESSAGE_SIZE` 保留（不删除），方便后续需要时再启用，但当前不在代码中使用。

## 验证
- 基于现有日志与逻辑路径验证：握手与消息接收在超时生效的前提下不再因长度被拒绝。
- 不改动协议与广播行为；无破坏性变更。