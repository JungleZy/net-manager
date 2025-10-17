# GitHub Actions Tag 触发配置说明

## 概述

已将 GitHub Actions 工作流 `test-then-build.yml` 的触发条件调整为**仅在推送 tag 时执行**，实现版本发布的自动化构建。

## 配置变更

### 1. 触发条件优化

#### 优化前

```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'client/**'
      - 'server/**'
      - 'requirements.txt'
      - '.github/workflows/test-then-build.yml'
  pull_request:
    branches: [main]
    paths:
      - 'client/**'
      - 'server/**'
      - 'requirements.txt'
      - '.github/workflows/test-then-build.yml'
  workflow_dispatch:
```

**问题**:

- ❌ 每次推送到 main/develop 分支都会触发
- ❌ 频繁执行构建，消耗 CI/CD 资源
- ❌ 不是每次提交都需要打包发布

#### 优化后

```yaml
on:
  push:
    tags:
      - 'v*' # 匹配所有以v开头的tag，例如 v1.0.0, v2.1.3
  workflow_dispatch: # 保留手动触发选项
```

**优势**:

- ✅ 仅在推送版本 tag 时触发
- ✅ 减少不必要的构建次数
- ✅ 节约 GitHub Actions 使用时间
- ✅ 保留手动触发选项（用于测试）

### 2. Release 步骤优化

#### 优化前

```yaml
release:
  if: github.ref == 'refs/heads/main'
  steps:
    - name: Create Release and Upload Assets
      with:
        tag_name: v${{ github.run_number }}
        name: Release v${{ github.run_number }}
```

**问题**:

- ❌ 使用 run_number 作为版本号，不直观
- ❌ 条件判断仍基于分支，不够精确

#### 优化后

```yaml
release:
  if: startsWith(github.ref, 'refs/tags/v') # 只在tag推送时执行
  steps:
    - name: Get tag name
      id: tag
      run: |
        echo "tag=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

    - name: Create Release and Upload Assets
      with:
        tag_name: ${{ steps.tag.outputs.tag }}
        name: Release ${{ steps.tag.outputs.tag }}
        body: |
          ## 自动构建版本 ${{ steps.tag.outputs.tag }}

          ### 包含平台
          - Windows (x86, x64, ARM)
          - Linux (x86, x64, ARM, ARM64)

          ### 下载说明
          请根据您的系统选择对应的可执行文件。
```

**优势**:

- ✅ 使用实际的 tag 名称作为版本号
- ✅ 更精确的条件判断
- ✅ 自动生成发布说明

## 使用方法

### 1. 创建并推送 Tag

#### 方法一：命令行创建 Tag

```bash
# 1. 确保代码已提交
git add .
git commit -m "准备发布 v1.0.0"

# 2. 创建带注释的tag
git tag -a v1.0.0 -m "发布版本 1.0.0"

# 3. 推送tag到远程仓库
git push origin v1.0.0
```

#### 方法二：GitHub 网页创建 Release

1. 进入仓库页面
2. 点击右侧 "Releases"
3. 点击 "Create a new release"
4. 填写 Tag version（例如：`v1.0.0`）
5. 填写 Release title 和描述
6. 点击 "Publish release"

**注意**: 通过网页创建 Release 会自动创建 tag 并触发工作流。

### 2. 监控构建进度

推送 tag 后：

1. 进入仓库的 "Actions" 页面
2. 可以看到 "Test Then Build" 工作流开始运行
3. 点击进入查看详细进度

### 3. 构建流程

```
推送 Tag (v1.0.0)
    ↓
触发 GitHub Actions
    ↓
┌─────────────────────────────────┐
│   并行测试 (Test Phase)          │
│  ┌─────────────┬──────────────┐ │
│  │ Windows测试 │  Linux测试    │ │
│  │  - x64      │  - x64       │ │
│  │  - x86      │  - x86       │ │
│  │  - ARM      │  - ARM       │ │
│  │             │  - ARM64     │ │
│  └─────────────┴──────────────┘ │
└─────────────────────────────────┘
    ↓ (测试通过)
┌─────────────────────────────────┐
│   并行构建 (Build Phase)         │
│  ┌─────────────┬──────────────┐ │
│  │ Windows构建 │  Linux构建    │ │
│  │  - x64      │  - x64       │ │
│  │  - x86      │  - x86       │ │
│  │  - ARM      │  - ARM       │ │
│  │             │  - ARM64     │ │
│  └─────────────┴──────────────┘ │
└─────────────────────────────────┘
    ↓ (构建完成)
┌─────────────────────────────────┐
│    创建 Release                  │
│  - 使用 tag 名称 (v1.0.0)       │
│  - 上传所有构建产物              │
│  - 生成发布说明                  │
└─────────────────────────────────┘
    ↓
✅ 发布完成
```

### 4. 下载构建产物

构建完成后：

1. 进入 "Releases" 页面
2. 找到对应版本的 Release（例如：v1.0.0）
3. 在 "Assets" 区域下载对应平台的可执行文件

## Tag 命名规范

### 推荐格式

遵循语义化版本规范（Semantic Versioning）：

```
v<主版本号>.<次版本号>.<修订号>[-预发布标识]
```

### 示例

| Tag             | 说明              | 适用场景             |
| --------------- | ----------------- | -------------------- |
| `v1.0.0`        | 正式版本 1.0.0    | 第一个稳定版本       |
| `v1.1.0`        | 次版本更新        | 新增功能，向后兼容   |
| `v1.1.1`        | 修订版本          | Bug 修复             |
| `v2.0.0`        | 主版本更新        | 重大变更，可能不兼容 |
| `v1.0.0-alpha`  | Alpha 版本        | 内部测试版本         |
| `v1.0.0-beta.1` | Beta 版本         | 公开测试版本         |
| `v1.0.0-rc.1`   | Release Candidate | 发布候选版本         |

### 版本号规则

- **主版本号**（Major）：重大功能变更，可能不向后兼容
- **次版本号**（Minor）：新增功能，向后兼容
- **修订号**（Patch）：Bug 修复，向后兼容

## 手动触发

如果需要手动触发构建（用于测试）：

1. 进入仓库的 "Actions" 页面
2. 选择 "Test Then Build" 工作流
3. 点击右上角 "Run workflow" 按钮
4. 选择分支
5. 点击 "Run workflow" 确认

**注意**: 手动触发时不会创建 Release，仅执行测试和构建。

## 常见场景

### 场景一：发布正式版本

```bash
# 1. 更新版本号（例如在 README 或配置文件中）
# 2. 提交更改
git add .
git commit -m "Release v1.0.0"
git push origin main

# 3. 创建并推送 tag
git tag -a v1.0.0 -m "正式发布版本 1.0.0"
git push origin v1.0.0

# ✅ 自动触发构建和发布
```

### 场景二：发布测试版本

```bash
# 创建预发布 tag
git tag -a v1.1.0-beta.1 -m "Beta 测试版本"
git push origin v1.1.0-beta.1

# ✅ 自动构建，可在 Release 中标记为 pre-release
```

### 场景三：删除错误的 Tag

```bash
# 删除本地 tag
git tag -d v1.0.0

# 删除远程 tag
git push origin :refs/tags/v1.0.0

# ⚠️ 注意：删除 tag 不会删除已创建的 Release，需手动删除
```

### 场景四：重新发布相同版本

```bash
# 1. 先删除旧 tag（见场景三）
# 2. 重新创建 tag
git tag -a v1.0.0 -m "重新发布版本 1.0.0"
git push origin v1.0.0

# ✅ 重新触发构建
```

## 工作流执行时间估算

| 阶段         | 平台               | 预估时间          |
| ------------ | ------------------ | ----------------- |
| **测试阶段** | Windows            | ~5-8 分钟         |
|              | Linux              | ~5-8 分钟         |
| **构建阶段** | Windows (3 个架构) | ~15-25 分钟       |
|              | Linux (4 个架构)   | ~20-30 分钟       |
| **发布阶段** | 上传产物           | ~2-5 分钟         |
| **总计**     |                    | **约 40-60 分钟** |

**注意**: 由于测试和构建是并行执行的，实际时间不是简单相加。

## GitHub Actions 配额

### 免费额度（公开仓库）

- ✅ 无限制的构建时间
- ✅ 无限制的并发任务

### 免费额度（私有仓库）

- ⏱️ 每月 2000 分钟（Linux）
- ⏱️ Windows 构建消耗 2 倍 时间
- ⏱️ macOS 构建消耗 10 倍 时间

### 优化建议

1. **减少不必要的构建**

   - ✅ 仅在 tag 推送时构建（已实现）
   - ✅ 避免频繁推送测试 tag

2. **优化构建时间**

   - 使用缓存加速依赖安装
   - 减少不必要的构建架构
   - 合理使用并行构建

3. **监控使用情况**
   - 定期检查 Actions 使用时间
   - 设置使用警报

## 故障排查

### 问题一：Tag 推送后没有触发

**可能原因**:

1. Tag 名称不匹配 `v*` 格式
2. 工作流文件有语法错误
3. GitHub Actions 被禁用

**解决方法**:

```bash
# 检查 tag 名称
git tag -l

# 确认 tag 格式正确（必须以 v 开头）
git tag -a v1.0.0 -m "版本 1.0.0"
git push origin v1.0.0
```

### 问题二：构建失败

**查看日志**:

1. 进入 Actions 页面
2. 点击失败的工作流
3. 查看具体步骤的错误信息

**常见错误**:

- 依赖安装失败：检查 `requirements.txt`
- 测试失败：修复代码后重新推送 tag
- 构建超时：优化构建配置或升级 Actions 配额

### 问题三：Release 创建失败

**可能原因**:

1. 权限不足
2. Tag 已存在对应的 Release
3. 文件路径错误

**解决方法**:

- 检查仓库 Settings → Actions → General → Workflow permissions
- 确保选择 "Read and write permissions"

## 最佳实践

### 1. 版本管理

- ✅ 遵循语义化版本规范
- ✅ 在代码中更新版本号
- ✅ 维护 CHANGELOG.md 记录变更

### 2. 发布流程

```
开发 → 测试 → 合并到 main → 打 tag → 自动构建 → 自动发布
```

### 3. Tag 管理

- ✅ 使用带注释的 tag (`git tag -a`)
- ✅ Tag 消息说明版本内容
- ✅ 不要随意删除已发布的 tag

### 4. Release 说明

- ✅ 自动生成的 Release 包含构建信息
- ✅ 可手动编辑 Release 补充详细说明
- ✅ 标注 breaking changes

## 相关文件

- `.github/workflows/test-then-build.yml` - 工作流配置文件
- `requirements.txt` - Python 依赖
- `client/main.py` - 客户端入口文件

## 扩展阅读

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [语义化版本规范](https://semver.org/lang/zh-CN/)
- [Git Tag 使用指南](https://git-scm.com/book/zh/v2/Git-基础-打标签)

## 版本信息

- **配置更新日期**: 2025-10-17
- **工作流版本**: 2.0
- **触发方式**: Tag 推送 + 手动触发
- **支持平台**: Windows (x86/x64/ARM), Linux (x86/x64/ARM/ARM64)
