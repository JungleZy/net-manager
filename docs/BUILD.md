# 项目构建说明

## 构建流程

本项目支持客户端（Client）和服务端（Server）的打包构建。服务端打包时会自动打包前端控制面板（Dashboard）。

### 构建顺序

1. **前端控制面板（Dashboard）** - 使用 Vite 构建
2. **服务端（Server）** - 使用 Nuitka 打包，包含 Dashboard 的静态文件
3. **客户端（Client）** - 使用 Nuitka 打包

## 前端控制面板构建

### 自动构建（推荐）

当执行服务端打包时，会自动触发 Dashboard 的构建：

```bash
python build.py --server
```

### 手动构建

如果需要单独构建 Dashboard：

```bash
cd dashboard
npm install  # 或 pnpm install / yarn install
npm run build
```

构建产物会生成在 `dashboard/dist` 目录下。

## 服务端构建

### 完整流程

执行以下命令会自动完成：
1. 构建 Dashboard
2. 将 Dashboard 构建产物复制到 `server/static` 目录
3. 打包 Server

```bash
python build.py --server
```

### 构建产物

- 可执行文件：`dist/server/net-manager-server.exe`（Windows）或 `dist/server/net-manager-server`（Linux）
- 静态文件：打包进可执行文件中的 `static` 目录

### 访问控制面板

启动服务端后，可以通过以下方式访问控制面板：

- 浏览器访问：`http://localhost:8000/`（自动重定向到 `/static/index.html`）
- 直接访问：`http://localhost:8000/static/index.html`

## 客户端构建

```bash
python build.py --client
```

## 完整构建

同时构建客户端和服务端：

```bash
python build.py
```

## 前置要求

### Dashboard 构建要求

- Node.js >= 16
- npm / pnpm / yarn（任选其一）

### Server/Client 打包要求

- Python 3.8+
- Nuitka
- C 编译器：
  - Windows: MSVC 或 MinGW
  - Linux: gcc 或 clang（推荐 clang）
- Linux 还需要：patchelf

## 构建配置

### Dashboard 配置

`dashboard/vite.config.js` 中的构建配置：

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

### Server 静态文件服务

服务端通过 Tornado 提供静态文件服务：

```python
# 主页重定向
(r"/", tornado.web.RedirectHandler, {"url": "/static/index.html"})

# 静态文件配置
settings = {
    "static_path": static_path,
    "static_url_prefix": "/static/"
}
```

## 开发模式

### 前端开发

```bash
cd dashboard
npm run dev
```

访问：`http://localhost:8001`

### 后端开发

```bash
cd server
python main.py
```

API 访问：`http://localhost:8000/api`

## 目录结构

```
project/
├── dashboard/          # 前端控制面板
│   ├── src/           # 源代码
│   ├── dist/          # 构建产物（构建后生成）
│   └── package.json
├── server/            # 服务端
│   ├── src/           # 源代码
│   ├── static/        # 前端静态文件（构建时复制）
│   └── main.py
├── client/            # 客户端
│   ├── src/           # 源代码
│   └── main.py
├── dist/              # 最终打包产物
│   ├── server/        # 服务端可执行文件
│   └── client/        # 客户端可执行文件
└── build.py           # 构建脚本
```

## 常见问题

### 1. Dashboard 构建失败

**问题**：找不到 npm/pnpm/yarn

**解决**：确保已安装 Node.js 和包管理器：
```bash
node --version
npm --version
```

### 2. 静态文件无法访问

**问题**：启动服务端后，访问 `/` 返回 404

**原因**：
- Dashboard 未构建
- `server/static` 目录不存在

**解决**：重新执行服务端构建：
```bash
python build.py --server
```

### 3. 打包后静态文件路径错误

**问题**：打包后的可执行文件无法找到静态文件

**原因**：Nuitka 打包时需要特殊处理静态文件

**解决**：确保 `server/static` 目录存在于打包时，Nuitka 会自动包含相对于主程序的目录。

## 部署建议

### 生产环境部署

1. 构建完整的服务端（包含 Dashboard）：
   ```bash
   python build.py --server
   ```

2. 部署 `dist/server` 目录中的所有文件

3. 启动服务端：
   ```bash
   ./net-manager-server  # Linux
   net-manager-server.exe  # Windows
   ```

4. 访问控制面板：`http://your-server-ip:8000/`

### 开发环境部署

1. 前端开发服务器：
   ```bash
   cd dashboard && npm run dev
   ```

2. 后端开发服务器：
   ```bash
   cd server && python main.py
   ```

3. 前端访问：`http://localhost:8001`
4. 后端 API：`http://localhost:8000/api`
