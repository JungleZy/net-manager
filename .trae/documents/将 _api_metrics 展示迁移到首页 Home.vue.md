## 目标
- 纠正指标展示位置，将之前添加在 SNMPDevicesTab.vue 的指标概览迁移到首页 Home.vue 中，统一平台状态总览入口。
- 保持现有首页统计卡片与设备/交换机列表不变，新增轻量指标区块。

## 变更范围
- 移除：`dashboard/src/views/devices/SNMPDevicesTab.vue` 中的指标展示区块与相关逻辑（metrics 变量、定时器、MetricsApi 引入）。
- 新增：在 `dashboard/src/views/home/Home.vue` 顶部（`<ServerPerformance />` 之后）增加指标概览区块；在脚本中引入 `MetricsApi`、定义 `metrics` 状态与定时拉取逻辑。
- 说明：后端 `/api/metrics` 已存在；轮询默认参数已改为从配置读取（`server/src/snmp/manager.py`）。

## 实施步骤
1) Home.vue 模板新增指标区块
- 在首页卡片前插入 `a-descriptions` 展示：
  - `db_health` → 正常/异常标签
  - `tcp_client_count`、`tcp_client_map_size`
  - `snmp_device_stats.queue_size`、`snmp_interface_stats.queue_size`
  - `snmp_device_stats.p95_response_time`、`snmp_interface_stats.p95_response_time`
  - 丢弃项合计：`dropped_items`
  - 广播统计：`broadcast_errors`/`message_count`

2) Home.vue 逻辑增加指标拉取
- 引入 `MetricsApi`（若未存在则新增 `dashboard/src/common/api/metrics.js`）。
- 在 `setup` 中：
  - 定义 `const metrics = ref({})`
  - 实现 `fetchMetrics()` 调用 `/api/metrics`，将 `resp?.data?.data` 赋值到 `metrics`。
  - 在 `onMounted` 中：首次调用 `fetchMetrics()`；启动 `setInterval(fetchMetrics, 5000)`；在 `onUnmounted` 中清理定时器。

3) SNMPDevicesTab.vue 清理
- 删除顶部 `a-descriptions` 指标展示区块（原错误位置）。
- 删除 `MetricsApi` 引入、`metrics` 状态与 `metricsTimer` 定时器逻辑。

## 验证
- 启动前端后，首页 Home 显示指标概览，各字段更新；设备页不再显示指标。
- 后端 `/api/metrics` 返回包含对应字段（已就绪）；首页成功拉取并不影响其他交互。

## 兼容与风险
- 纯前端调整，不影响后端协议；指标区块为只读展示。
- 指标拉取失败时记录到控制台，页面保持正常（无硬错误）。

## 备注
- 轮询默认参数已从 `server/src/core/config.py` 自动应用到 `SNMPManager.start_pollers`，无需额外改动。
- 若后续需要，将指标区块抽象为独立组件便于复用。