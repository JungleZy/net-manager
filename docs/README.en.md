# Documentation Overview & Navigation

> Index: 00-Document-Index.en.md | Quick Reference: QUICK_REFERENCE.md

## Overview

Net Manager is a full-stack network device management system with client probing, server management and a web dashboard. This folder contains architecture, API, guides, build and troubleshooting docs.

## Recommended Path

- Getting started: README.md → 00-Document-Index.en.md → QUICK_REFERENCE.md
- Architecture: PROJECT_STRUCTURE.en.md → MODULE_DESIGN.md → INTERFACE_SPEC.md
- API: API_DOCUMENTATION.en.md → SWITCH_API.md → TOPOLOGY_API.md → API-Performance.md
- Frontend: DASHBOARD_README.md → Network-Topology-Monitor.md
- Build: BUILD.en.md → PACKAGING.md → GitHub-Actions-Tag-Trigger.md
- Troubleshooting: TROUBLESHOOTING_404.md

## Modules

- Client: system collector, TCP/UDP, autostart, reconnect and state management
- Server: Tornado HTTP API, WebSocket push, TCP/UDP servers, SNMP manager, database managers
- Dashboard: Vue3 + Vite + Ant Design Vue, topology (LogicFlow), performance charts (ECharts)

## Notes

- Server build auto-integrates frontend static assets into `server/static`
- `agent/` binaries will be copied to `server/static/agent` for dashboard download

## Changelog

- 2025-12-06: Added English overview and index links
