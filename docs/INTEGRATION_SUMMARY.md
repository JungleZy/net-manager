# Dashboard 与 Server 集成总结

## 概述

本文档总结了前端控制面板（Dashboard）与服务端（Server）的集成方案。

## 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   用户浏览器                          │
│                                                       │
│  http://localhost:8000/                              │
│         ↓ (自动重定向)                                │
│  http://localhost:8000/static/index.html            │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Server (Tornado 服务)                    │
│                                                       │
│  ┌──────────────┐         ┌──────────────┐          │
│  │  静态文件服务 │         │   API 服务   │          │
│  │  /static/*   │         │   /api/*     │          │
│  └──────────────┘         └──────────────┘          │
│         ↓                         ↓                  │
│  ┌──────────────┐         ┌──────────────┐          │
│  │ Dashboard    │         │  REST API    │          │
│  │ (HTML/JS/CSS)│         │  (JSON)      │          │
│  └──────────────┘         └──────────────┘          │
└─────────────────────────────────────────────────────┘
```

### 构建流程

```
┌─────────────┐
│ Dashboard   │
│ (Vue 3)     │
└──────┬──────┘
       │ npm run build
       ↓
┌─────────────┐
│ dist/       │
│ (静态文件)   │
└──────┬──────┘
       │ 复制
       ↓
┌─────────────┐
│ server/     │
│ static/     │
└──────┬──────┘
       │ Nuitka 打包
       ↓
┌─────────────┐
│ dist/server/│
│ 可执行文件   │
└─────────────┘
```

## 实现细节

### 1. Dashboard 构建配置

**位置**: `dashboard/vite.config.js`

```javascript
build: {
  rollupOptions: {
    output: {
      chunkFileNames: 'assets/js/[name]-[hash].js',
      entryFileNames: 'assets/js/[name]-[hash].js',
      assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
    }
  }
}
```

### 2. Server 静态文件服务

**位置**: `server/src/network/api/api_server.py`

**关键代码**:

```python
# 主页重定向到静态文件
(r"/", tornado.web.RedirectHandler, {"url": "/static/index.html"})

# 静态文件配置
settings = {
    "static_path": static_path,
    "static_url_prefix": "/static/"
}

tornado.web.Application(routes, **settings)
```

**静态文件路径处理**:

```python
# 开发环境
static_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'static')

# 打包后环境
static_path = os.path.join(os.path.dirname(sys.executable), 'static')
```

### 3. 构建脚本集成

**位置**: `build.py`

**关键函数**:

```python
def build_dashboard():
    """打包前端控制面板"""
    # 1. 检测包管理器 (pnpm/npm/yarn)
    # 2. 安装依赖 (如果需要)
    # 3. 执行构建 (npm run build)
    # 4. 复制产物到 server/static

def build_server():
    """打包服务端"""
    # 1. 先构建 Dashboard
    # 2. 打包 Server (自动包含 static 目录)
```

**Nuitka 打包选项**:

```python
# 如果是server，需要包含static目录
if app_type == "server":
    cmd.append(f"--include-data-dir={static_dir}=static")
```

## 使用方式

### 开发环境

**方式一：分离运行（推荐开发时使用）**

```bash
# 终端 1: 启动后端
cd server
python main.py

# 终端 2: 启动前端开发服务器
cd dashboard
npm run dev
```

访问：
- 前端：http://localhost:8001 (热重载)
- 后端 API：http://localhost:8000/api

**方式二：集成运行**

```bash
# 先构建前端
cd dashboard
npm run build

# 启动后端（提供静态文件服务）
cd ../server
python main.py
```

访问：http://localhost:8000/ (自动跳转到控制面板)

### 生产环境

```bash
# 构建服务端（自动构建并集成前端）
python build.py --server

# 运行
cd dist/server
./net-manager-server
```

访问：http://your-server-ip:8000/

## 目录结构

### 开发时

```
net-manager/
├── dashboard/
│   ├── src/                    # 前端源代码
│   ├── dist/                   # 构建产物（构建后生成）
│   └── package.json
├── server/
│   ├── src/
│   └── static/                 # 前端静态文件（构建时复制）
└── build.py
```

### 打包后

```
dist/
└── server/
    ├── net-manager-server      # 可执行文件
    └── static/                 # 内嵌在可执行文件中
        ├── index.html
        ├── assets/
        │   ├── js/
        │   └── css/
        └── ...
```

## 访问路径

### 静态文件

- `/` → 重定向到 `/static/index.html`
- `/static/*` → 静态文件服务

### API 接口

- `/api/devices` → 设备管理 API
- `/api/switches` → 交换机管理 API
- `/api/topologies` → 拓扑图管理 API
- `/ws` → WebSocket 连接
- `/health` → 健康检查

## 优势

1. **单一部署包**：一个可执行文件包含前端和后端
2. **无需额外 Web 服务器**：Tornado 直接提供静态文件服务
3. **开发友好**：支持前后端分离开发，前端热重载
4. **自动化构建**：一键构建，自动集成前端资源
5. **跨平台**：支持 Windows/Linux 打包

## 注意事项

### 1. 构建顺序

- **必须先构建 Dashboard**，再打包 Server
- `build.py --server` 已自动处理此顺序

### 2. 静态文件路径

- 开发环境：`server/static/`
- 打包后：内嵌在可执行文件中，通过 Nuitka 的 `--include-data-dir` 选项

### 3. 前端构建要求

- Node.js >= 16
- npm/pnpm/yarn（任选其一）

### 4. CORS 配置

- API 已配置 CORS，支持跨域访问
- 生产环境建议限制 `Access-Control-Allow-Origin`

## 故障排查

### 问题：访问 `/` 返回 404

**原因**：静态文件目录不存在

**解决**：
```bash
# 重新构建
python build.py --server
```

### 问题：前端页面显示但 API 请求失败

**原因**：前端 API 地址配置错误

**检查**：
- 开发环境：`dashboard/src/config/http/index.js`
- 确认 `bindType` 是否正确（dev/prod）

### 问题：打包后静态文件无法访问

**原因**：Nuitka 未包含 static 目录

**检查**：
```bash
# 确认 build.py 中有以下代码
if app_type == "server":
    cmd.append(f"--include-data-dir={static_dir}=static")
```

## 相关文档

- [BUILD.md](BUILD.md) - 详细构建说明
- [README.md](README.md) - 项目总览
- [dashboard/README.md](dashboard/README.md) - 前端文档（如有）
- [server/src/network/api/api_server.py](server/src/network/api/api_server.py) - API 服务器实现
