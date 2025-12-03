## 目标

* 不再基于接口流量判断边状态；只要两端节点在线，边标记为“数据传输状态”。

* 去除动态效果，统一将连线颜色改为 `#1890ff`（蓝色）。

## 变更文件

* `dashboard/src/views/network/Network.vue`

## 具体改动

1. 统一边颜色为蓝色

* 在 LogicFlow 初始化的样式配置中：

  * 将 `style.edge.stroke`、`style.edgeHover.stroke`、`style.edgeSelected.stroke` 全部改为 `#1890ff`。

1. 新增按在线状态更新边的统一方法

* 添加 `updateEdgesByOnlineStatus()`：

  * 读取当前图数据 `lf.getGraphData()`。

  * 遍历每条边，查找源/目标节点的在线状态（`node.properties.status`）。

  * 若两端在线：

    * 设置边属性 `properties.hasData = true`（便于已有自定义边使用；但不启用动画）。

  * 否则：

    * 设置 `properties.hasData = false`。

  * 关闭任何可能存在的边动画（调用 `lf.closeEdgeAnimation(edge.id)`）。

1. 重构 `handleSnmpDeviceUpdate` 与 `handleDeviceInfoUpdate`

* 移除对接口流量（`interface_info` / `networks`）的检查逻辑。

* 在更新节点在线状态与列表后，调用 `updateEdgesByOnlineStatus()`。

* 不再调用 `updateEdgeDataStatus` 基于流量开启动画；如有保留，可改为仅设置属性，不开动画。

1. 保留其他功能不变

* 节点点击、搜索、全屏、居中等逻辑保持现有行为。

## 验收

* 任意两端节点在线时，该边变为蓝色；两端任一离线时，边仍为蓝色但 `hasData=false`（用于区分，未来可扩展样式）。

* 页面无动态动效；边颜色统一为 `#1890ff`。

* 不依赖接口速率数据，也不需要后端字段改变。

