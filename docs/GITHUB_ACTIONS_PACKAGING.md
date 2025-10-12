# GitHub Actions 跨平台打包指南

本文档介绍了如何使用 GitHub Actions 对 NetManager 客户端进行跨平台打包。

## 支持的平台

- Windows x86
- Windows x64
- Linux x86
- Linux ARM

## 工作流触发条件

1. 推送到 `main` 或 `develop` 分支，且修改了以下文件：
   - `client/**`
   - `requirements.txt`
   - `.github/workflows/build-client.yml`

2. 在 `main` 分支上创建 Pull Request，且修改了上述文件

3. 手动触发（workflow_dispatch）

## 构建流程

### Windows 构建
- 运行环境：`windows-latest`
- 架构：x86, x64
- 使用 Nuitka 进行打包
- 生成独立的单文件可执行程序

### Linux 构建
- 运行环境：`ubuntu-latest`
- 架构：x86, arm
- 使用 Nuitka 进行打包
- 生成独立的单文件可执行程序

## 发布流程

当推送到 `main` 分支时，会自动创建 Release 并上传所有平台的构建产物。

## 本地测试工作流

可以使用 [act](https://github.com/nektos/act) 工具在本地测试 GitHub Actions 工作流：

```bash
# 安装 act
# 在 Windows 上使用 Chocolatey:
choco install act-cli

# 在 macOS 上使用 Homebrew:
brew install act

# 运行工作流
act push -j build-windows
act push -j build-linux
```

## 自定义构建选项

如果需要修改构建选项，可以在 `.github/workflows/build-client.yml` 文件中进行调整：

1. 修改 Python 版本：
   ```yaml
   - name: Setup Python
     uses: actions/setup-python@v5
     with:
       python-version: '3.9'  # 修改为你需要的版本
   ```

2. 修改 Nuitka 构建参数：
   ```yaml
   python -m nuitka \
     --standalone \
     --onefile \
     # 添加或修改其他参数
   ```

## 故障排除

### 构建失败
1. 检查依赖安装是否正确
2. 确认 Nuitka 版本是否兼容
3. 查看构建日志中的具体错误信息

### 构建产物未生成
1. 确认 Nuitka 命令是否正确执行
2. 检查输出路径是否正确
3. 验证文件权限设置

## 注意事项

1. 构建过程中会自动安装 `requirements.txt` 中列出的所有依赖
2. 构建产物会作为 artifacts 上传，可以在 GitHub Actions 页面下载
3. 只有推送到 `main` 分支才会自动创建 Release