# Dashboard 与 Server 集成验证清单

## 快速验证

使用此清单验证 Dashboard 与 Server 的集成是否正确配置。

## 1. 文件检查

### Dashboard 配置

- [ ] `dashboard/package.json` 存在
- [ ] `dashboard/vite.config.js` 存在
- [ ] `dashboard/vite.config.js` 包含 `transformBindType` 插件
- [ ] 构建脚本存在：`package.json` 中有 `"build": "vite build"`

### Server 配置

- [ ] `server/src/network/api/api_server.py` 已导入 `os` 和 `sys`
- [ ] `api_server.py` 中包含静态文件路径配置
- [ ] `api_server.py` 中根路径配置为 `RedirectHandler`
- [ ] Tornado Application 配置中包含 `static_path` 和 `static_url_prefix`

### 构建脚本

- [ ] `build.py` 中定义了 `DASHBOARD_DIR` 变量
- [ ] `build.py` 中包含 `build_dashboard()` 函数
- [ ] `build_server()` 函数在打包前调用 `build_dashboard()`
- [ ] `_build_application()` 函数在打包 server 时包含 `--include-data-dir` 参数

## 2. 功能测试

### 开发环境测试

#### 方式一：分离运行

```bash
# 终端 1
cd server
python main.py
# 预期：服务器启动，监听 8000 端口

# 终端 2
cd dashboard
npm run dev
# 预期：开发服务器启动，监听 8001 端口
```

- [ ] 访问 `http://localhost:8001` 可以看到前端页面
- [ ] 前端可以正常调用 `http://localhost:8000/api` 接口
- [ ] 浏览器控制台无 CORS 错误

#### 方式二：集成运行

```bash
# 构建前端
cd dashboard
npm run build
# 预期：生成 dist 目录

# 启动后端
cd ../server
python main.py
# 预期：服务器启动，输出 "静态文件目录: ..."
```

- [ ] 访问 `http://localhost:8000/` 自动跳转到 `/static/index.html`
- [ ] 前端页面正常显示
- [ ] API 请求正常工作
- [ ] 浏览器控制台无 404 错误

### 生产环境测试（打包）

```bash
# 清理旧的构建
rm -rf dist/server  # Linux
# 或
rmdir /s /q dist\server  # Windows

# 执行构建
python build.py --server
```

**预期输出**：

```
==================================================
步骤1: 打包前端控制面板
==================================================
开始打包前端控制面板...
✓ 找到包管理器: pnpm
正在构建前端项目...
✓ 前端构建完成
✓ 前端构建产物已复制到server/static目录

==================================================
步骤2: 打包服务端
==================================================
开始打包server...
✓ 包含静态文件目录: .../server/static
...
✓ server打包成功
```

检查项：

- [ ] `dashboard/dist` 目录已创建
- [ ] `server/static` 目录已创建并包含前端文件
- [ ] `server/static/index.html` 存在
- [ ] `dist/server/net-manager-server` (或 `.exe`) 已创建
- [ ] 打包过程输出 "✓ 包含静态文件目录"

运行打包后的程序：

```bash
cd dist/server
./net-manager-server  # Linux
# 或
net-manager-server.exe  # Windows
```

- [ ] 程序正常启动
- [ ] 日志输出 "静态文件目录: ..."
- [ ] 访问 `http://localhost:8000/` 可以看到前端页面
- [ ] API 接口正常工作

## 3. 代码审查

### api_server.py

检查以下代码片段是否存在：

```python
import os
import sys
import tornado.web
```

```python
# 获取静态文件目录
if getattr(sys, 'frozen', False):
    static_path = os.path.join(os.path.dirname(sys.executable), 'static')
else:
    static_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'static')
```

```python
# 主页重定向
(r"/", tornado.web.RedirectHandler, {"url": "/static/index.html"}),
```

```python
# 静态文件配置
if static_exists:
    settings["static_path"] = static_path
    settings["static_url_prefix"] = "/static/"
```

- [ ] 所有代码片段都存在
- [ ] 缩进正确
- [ ] 逻辑流程正确

### build.py

检查以下函数是否存在：

```python
def build_dashboard():
    """打包前端控制面板"""
    # ... 实现
```

```python
def build_server():
    """打包服务端"""
    # 在打包server之前先打包dashboard
    if not build_dashboard():
        return False
    # ...
```

```python
def _build_application(...):
    # ...
    if app_type == "server":
        static_dir = app_dir / "static"
        if static_dir.exists():
            cmd.append(f"--include-data-dir={static_dir}=static")
```

- [ ] 所有函数都存在
- [ ] 函数调用顺序正确
- [ ] 路径处理正确

## 4. 路由测试

启动服务器后，测试以下路由：

| 路由 | 预期结果 | 状态 |
|------|----------|------|
| `GET /` | 302 重定向到 `/static/index.html` | [ ] |
| `GET /static/index.html` | 200 返回 HTML | [ ] |
| `GET /static/assets/js/...` | 200 返回 JS 文件 | [ ] |
| `GET /static/assets/css/...` | 200 返回 CSS 文件 | [ ] |
| `GET /api/devices` | 200 返回 JSON | [ ] |
| `GET /api/switches` | 200 返回 JSON | [ ] |
| `GET /health` | 200 返回 JSON | [ ] |
| `GET /ws` | 101 WebSocket 连接 | [ ] |

## 5. 浏览器测试

打开 `http://localhost:8000/`，检查：

- [ ] 页面正常加载，无白屏
- [ ] 控制台无 404 错误
- [ ] 控制台无 CORS 错误
- [ ] 网络面板显示静态文件从 `/static/` 加载
- [ ] API 请求返回正常数据
- [ ] WebSocket 连接成功（如有）
- [ ] 页面功能正常（设备管理、拓扑图等）

## 6. 常见问题检查

### 问题 1: 访问 `/` 返回 404

检查：
- [ ] `server/static` 目录是否存在
- [ ] `server/static/index.html` 是否存在
- [ ] 服务器日志是否输出 "静态文件目录不存在"

解决方案：
```bash
cd dashboard && npm run build
```

### 问题 2: 静态文件 404

检查：
- [ ] Tornado Application 是否配置了 `static_path`
- [ ] `static_url_prefix` 是否为 `/static/`
- [ ] 静态文件路径是否正确

### 问题 3: 打包后静态文件无法访问

检查：
- [ ] Nuitka 命令是否包含 `--include-data-dir` 参数
- [ ] `server/static` 目录在打包前是否存在

### 问题 4: 前端 API 请求失败

检查：
- [ ] 前端 API 基础 URL 配置是否正确
- [ ] 开发/生产环境的 `bindType` 是否正确
- [ ] 服务器 CORS 配置是否正确

## 7. 性能检查

- [ ] 前端资源是否启用了 gzip 压缩
- [ ] 静态文件是否设置了缓存头
- [ ] 首次加载时间是否可接受（< 3 秒）
- [ ] API 响应时间是否正常（< 500ms）

## 8. 安全检查

- [ ] 生产环境是否禁用了 `debug` 模式
- [ ] CORS 配置是否限制了允许的源
- [ ] 静态文件路径是否防止了目录遍历攻击
- [ ] API 是否有适当的错误处理

## 9. 文档检查

- [ ] `BUILD.md` 文档是否完整
- [ ] `README.md` 是否包含集成说明
- [ ] `INTEGRATION_SUMMARY.md` 是否准确
- [ ] 代码注释是否清晰

## 10. 版本控制

- [ ] `.gitignore` 包含 `dashboard/dist/`
- [ ] `.gitignore` 包含 `server/static/`（如果不想提交）
- [ ] `.gitignore` 包含 `dist/`
- [ ] 所有重要文件已提交

## 完成标准

当所有检查项都通过时，集成即为成功：

✅ 文件配置正确  
✅ 开发环境运行正常  
✅ 生产打包成功  
✅ 路由测试通过  
✅ 浏览器测试通过  
✅ 文档完整  

## 快速测试命令

```bash
# 1. 测试开发环境
cd server && python main.py &
cd dashboard && npm run dev

# 2. 测试集成构建
python build.py --server

# 3. 测试打包产物
cd dist/server && ./net-manager-server

# 4. 验证配置
python test_static_config.py
```

## 需要帮助？

如果遇到问题，请检查：

1. [BUILD.md](BUILD.md) - 构建详细说明
2. [INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md) - 集成架构说明
3. [README.md](README.md) - 项目总览
4. 服务器日志输出
5. 浏览器控制台错误信息
