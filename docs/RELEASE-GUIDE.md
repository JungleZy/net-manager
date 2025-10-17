# 版本发布快速指南

## 一键发布流程

### 准备工作

1. 确保代码已提交并推送到 `main` 分支
2. 确定版本号（遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范）

### 发布步骤

#### 方法一：命令行发布（推荐）

```bash
# 1. 切换到主分支并更新
git checkout main
git pull origin main

# 2. 创建版本 tag
git tag -a v1.0.0 -m "发布版本 1.0.0 - 添加了XXX功能"

# 3. 推送 tag（自动触发构建和发布）
git push origin v1.0.0

# ✅ 完成！等待约 40-60 分钟自动构建完成
```

#### 方法二：GitHub 网页发布

1. 访问：`https://github.com/your-username/net-manager/releases/new`
2. 填写：
   - **Tag version**: `v1.0.0`
   - **Release title**: `Release v1.0.0`
   - **Description**: 描述此版本的更新内容
3. 点击 **Publish release**
4. ✅ 自动触发构建

## 版本号规范

### 格式

```
v<主版本号>.<次版本号>.<修订号>
```

### 示例

- `v1.0.0` - 首个正式版本
- `v1.1.0` - 新增功能（向后兼容）
- `v1.1.1` - Bug 修复
- `v2.0.0` - 重大更新（可能不兼容旧版本）

### 预发布版本

- `v1.0.0-alpha` - 内部测试版
- `v1.0.0-beta.1` - 公开测试版
- `v1.0.0-rc.1` - 发布候选版

## 发布后检查

### 1. 查看构建进度

```
GitHub 仓库 → Actions → Test Then Build
```

### 2. 构建流程

```
测试 (5-8分钟)
  ↓
构建 (15-30分钟)
  ↓
发布 (2-5分钟)
  ↓
完成 ✅
```

### 3. 下载发布文件

```
GitHub 仓库 → Releases → 选择版本 → Assets
```

## 常见操作

### 删除错误的 Tag

```bash
# 删除本地 tag
git tag -d v1.0.0

# 删除远程 tag
git push origin :refs/tags/v1.0.0
```

### 查看所有 Tag

```bash
git tag -l
```

### 查看 Tag 详情

```bash
git show v1.0.0
```

## 故障排查

### Tag 推送后没有触发？

1. 检查 tag 名称是否以 `v` 开头
2. 访问 Actions 页面查看是否有错误

### 构建失败？

1. 进入 Actions 页面查看日志
2. 修复问题后删除旧 tag 重新发布

### 无法推送 Tag？

```bash
# 确保有推送权限
git remote -v

# 确保本地 tag 存在
git tag -l
```

## 发布检查清单

- [ ] 代码已提交到 main 分支
- [ ] 版本号符合规范（v 开头）
- [ ] Tag 注释清晰描述了更新内容
- [ ] 已在本地测试过
- [ ] CHANGELOG.md 已更新（可选）
- [ ] README.md 版本号已更新（可选）

## 自动生成的产物

每次发布会自动生成以下文件：

### Windows

- `net-manager-client-win-x86.exe` (32 位)
- `net-manager-client-win-x64.exe` (64 位)

### Linux

- `net-manager-client-linux-x86` (32 位)
- `net-manager-client-linux-x64` (64 位)
- `net-manager-client-linux-arm` (ARM 32 位)
- `net-manager-client-linux-arm64` (ARM 64 位)

## 更多信息

详细文档请参考：[GitHub-Actions-Tag-Trigger.md](./GitHub-Actions-Tag-Trigger.md)
