# Build Guide

## Flow

1. Build Dashboard (Vite)
2. Package Server (Nuitka), include dashboard static files
3. Package Client (Nuitka)

## Server Build (auto integrates dashboard)

```bash
python build.py --server
```

Artifacts:
- Executable: `dist/server/net-manager-server(.exe)`
- Static: bundled `static` directory

Access:
- `http://localhost:8000/` (redirects to dashboard)
- API: `http://localhost:8000/api`

## Client Build

```bash
python build.py --client
```

## Full Build

```bash
python build.py
```

## Requirements

- Dashboard: Node.js ≥ 16, npm/pnpm/yarn
- Server/Client: Python 3.8+, Nuitka, C compiler
  - Windows: MSVC or MinGW
  - Linux: gcc or clang (recommended), patchelf

## Dev Mode

- Frontend: `cd dashboard && npm run dev` → `http://localhost:8001`
- Backend: `cd server && python main.py` → API `http://localhost:8000/api`

## Troubleshooting

- Missing npm: install Node.js and ensure PATH is set
- 404 at `/`: build dashboard or check `server/static` exists
