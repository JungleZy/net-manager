# Net Manager Project Structure

## Overview

```
net-manager/
├── agent/                      # Prebuilt client binaries (for dashboard downloads)
├── client/
│   ├── src/
│   │   ├── config_module/      # Config loading
│   │   ├── core/               # App controller & state
│   │   ├── exceptions/         # Exception types
│   │   ├── network/            # TCP/UDP clients
│   │   ├── system/             # Autostart & system collector
│   │   └── utils/              # Logger, platform utils, singleton, unique ID
│   ├── tests/                  # Client tests
│   └── main.py                 # Client entry
├── server/
│   ├── migrations/             # Database migrations
│   ├── src/
│   │   ├── core/               # Config, logger, state, singleton
│   │   ├── database/           # Pool, managers, exceptions
│   │   ├── models/             # Device/switch/topology models
│   │   ├── monitor/            # Server performance monitor
│   │   ├── network/
│   │   │   ├── api/            # Tornado HTTP API & WebSocket
│   │   │   ├── tcp/            # TCP server
│   │   │   └── udp/            # UDP
│   │   ├── snmp/               # SNMP manager, OID classifier, unified poller
│   │   └── utils/              # Platform utils
│   ├── tests/                  # Server tests
│   └── main.py                 # Server entry
├── dashboard/                  # Vue3 + Vite + Ant Design Vue
│   ├── src/                    # Components/views/topology/API wrappers
│   ├── public/docs/            # User-facing docs
│   ├── package.json            # Dependencies
│   └── vite.config.js          # Dev port 8001
├── docs/                       # Project docs & guides
│   ├── 00-Document-Index.en.md # English doc index
│   ├── PROJECT_STRUCTURE.en.md # Project structure (this file)
│   ├── BUILD.en.md             # Build guide
│   └── API_DOCUMENTATION.en.md # API docs
├── .github/workflows/          # CI/CD workflows
├── build.py                    # Packaging (integrates dashboard)
├── requirements.txt            # Python deps
├── pyproject.toml              # Project config
└── README.md                   # Overview
```

## Client Modules

- `client/src/core/app_controller.py`: discovery, connect/report, retry
- `client/src/core/state_manager.py`: persistence & unique ID
- `client/src/network/tcp_client.py`: TCP connection & reconnect
- `client/src/network/udp_client.py`: UDP broadcast & discovery
- `client/src/system/system_collector.py`: CPU/memory/disk/network
- `client/src/system/autostart.py`: cross-platform autostart
- `client/src/utils/*`: logging, platform utilities, singleton, unique ID

## Server Modules

- `server/src/network/api/api_server.py`: Tornado app & routes
- `server/src/network/api/handlers/*`: devices/switches/topology/performance
- `server/src/network/websocket_handler.py`: WebSocket push
- `server/src/network/tcp/tcp_server.py`: client reporting
- `server/src/network/udp/*`: broadcast/discovery
- `server/src/snmp/*`: manager, unified poller, OID classifier
- `server/src/monitor/server_monitor.py`: server metrics
- `server/src/database/*`: connection pool & managers
- `server/src/core/*`: config, logger, state, singleton

## Data Flow

```
Client → TCP report → API/DB → WebSocket → Dashboard
           ↘ UDP broadcast/discovery ↗
```

## Run & Build

- Install deps: `pip install -r requirements.txt`
- Dev:
  - Backend: `cd server && python main.py` (`http://localhost:8000/api`)
  - Frontend: `cd dashboard && npm run dev` (`http://localhost:8001`)
  - Client: `cd client && python main.py`
- Package:
  - Server (with dashboard): `python build.py --server`
  - Client: `python build.py --client`
