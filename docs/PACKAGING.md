# Net Manager 打包说明

## 概述

本文档说明如何使用Nuitka将Net Manager客户端和服务端打包成独立的可执行文件，以便在没有Python环境的系统上运行。

项目提供了三种打包方式：
1. 手动命令行打包
2. 自动化打包脚本（推荐）
3. GitHub Actions 自动化打包（CI/CD）

## 打包工具

项目使用[Nuitka](https://nuitka.net/)作为打包工具，它是一个Python编译器，可以将Python代码编译成独立的可执行文件。

## 方法一：手动命令行打包

### 1. 安装Nuitka

在项目的虚拟环境中安装Nuitka：

```bash
# 激活虚拟环境
cd venv\Scripts
.\activate

# 安装Nuitka
pip install nuitka
```

### 2. 打包客户端程序

在项目根目录下运行以下命令：

```bash
# 激活虚拟环境
cd venv\Scripts
.\activate

# 切换到项目根目录
cd ..\..

# 使用Nuitka打包客户端程序
python -m nuitka --standalone --onefile --enable-plugin=multiprocessing client/main.py
```

参数说明：
- `--standalone`: 创建独立的可执行文件，包含所有依赖
- `--onefile`: 打包成单个可执行文件
- `--enable-plugin=multiprocessing`: 启用多进程插件支持

### 3. 移动生成的文件

打包完成后，会在项目根目录生成`main.exe`文件，将其移动到client目录：

```bash
move main.exe client\
```

## 方法二：使用自动化打包脚本（推荐）

项目提供了 `build.py` 自动化打包脚本，可以简化打包过程并支持分别打包客户端和服务端。

### 1. 使用方法

```bash
# 打包客户端和服务端
python build.py

# 仅打包客户端
python build.py --client

# 仅打包服务端
python build.py --server

# 清理之前的构建并重新打包
python build.py --clean
```

### 2. 输出目录

打包完成后，生成的文件将位于 `dist` 目录中：
- 客户端: `dist/client/`
- 服务端: `dist/server/`

每个目录都包含：
- `main.exe`: 打包后的可执行文件
- `run_client.bat` / `run_server.bat`: 运行脚本
- `logs/`: 日志目录
- 相关说明文档

## 方法三：GitHub Actions 自动化打包（CI/CD）

项目使用 GitHub Actions 实现自动化打包，采用"先测试后构建"的策略，确保代码质量和跨平台兼容性。

### 1. 工作流程

GitHub Actions 工作流程包含以下步骤：

1. **测试阶段**：
   - 在多个平台上运行跨平台兼容性测试
   - 确保所有测试通过后再进行构建

2. **构建阶段**：
   - 在不同操作系统和架构上并行构建客户端可执行文件
   - 支持 Windows (x86, x64) 和 Linux (x86, x64)

3. **发布阶段**：
   - 自动创建 GitHub Release 并上传构建产物

### 2. 触发条件

GitHub Actions 工作流程会在以下情况下自动触发：
- 推送代码到 `main` 或 `develop` 分支
- 创建指向 `main` 分支的 Pull Request
- 手动手动触发工作流程

### 3. 构建产物

构建完成后，会生成以下可执行文件：
- Windows:
  - `net-manager-client-win-x86.exe`
  - `net-manager-client-win-x64.exe`
- Linux:
  - `net-manager-client-linux-x86`
  - `net-manager-client-linux-x64`

### 4. 工作流程文件

相关的 GitHub Actions 工作流程定义在 `.github/workflows/` 目录中：
- `test-then-build.yml`: 主要工作流程，实现先测试后构建策略
- `build-client.yml`: 已弃用的旧工作流程
- `cross-platform-test.yml`: 已弃用的旧测试工作流程

## 打包结果

打包完成后，client目录中会包含以下文件：
- `main.exe`: 打包后的可执行文件
- `run_client.bat`: 运行脚本

## 运行打包版本

### 方法1：直接运行
```bash
cd client
main.exe
```

### 方法2：使用批处理脚本
```bash
cd client
run_client.bat
```

## 打包版本的优势

1. **无需Python环境**: 打包后的程序可以在没有安装Python的Windows系统上运行
2. **无需安装依赖**: 所有依赖都被打包进可执行文件中
3. **启动速度快**: 编译后的程序启动速度比源码方式更快
4. **便于分发**: 单个可执行文件便于分发和部署
5. **保护源码**: 可执行文件比源码更难被逆向工程

## 注意事项

1. 打包过程可能需要较长时间（几分钟），请耐心等待
2. 生成的可执行文件体积较大（约7-8MB），这是正常现象
3. 打包后的程序仍然需要与服务端配合使用
4. 如果修改了客户端代码，需要重新打包才能生效