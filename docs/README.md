# 文档总览与导航

> 📚 文档入口：[文档目录](00-文档目录.md) | [快速参考](QUICK_REFERENCE.md)

## 概述

Net Manager 是一个全栈网络设备管理系统，包含客户端探测、服务端管理与 Web 控制面板。此目录下汇聚了架构、API、指南、构建与故障排查等文档。

## 推荐阅读路径

- 入门：`README.md`（项目总览） → `00-文档目录.md`（索引） → `QUICK_REFERENCE.md`
- 架构：`PROJECT_STRUCTURE.md` → `MODULE_DESIGN.md` → `INTERFACE_SPEC.md`
- API：`API_DOCUMENTATION.md` → `SWITCH_API.md` → `TOPOLOGY_API.md` → `API-Performance.md`
- 前端：`DASHBOARD_README.md` → `Network-Topology-Monitor.md`
- 构建：`BUILD.md` → `PACKAGING.md` → `GitHub-Actions-Tag-Trigger.md`
- 故障：`TROUBLESHOOTING_404.md`

## 模块一览

- 客户端：系统采集、TCP/UDP 通信、开机自启、重连与状态管理
- 服务端：Tornado HTTP API、WebSocket 推送、TCP/UDP 服务、SNMP 管理、数据库管理
- 前端：Vue3 + Vite + Ant Design Vue，拓扑可视化（LogicFlow）、性能图表（ECharts）

## 重要说明

- 构建服务端时会自动构建并集成前端静态资源至 `server/static`
- `agent/` 中的二进制在构建后复制至 `server/static/agent`，可通过前端页面下载

## 变更记录

- 2025-12-06：更新为文档总览形式，替换旧 SNMP 专题说明至对应专题文档：`SNMP_README.md`、`ROUTER_CONFIG_GUIDE.md`、`SHA_AUTH_SUPPORT.md`
