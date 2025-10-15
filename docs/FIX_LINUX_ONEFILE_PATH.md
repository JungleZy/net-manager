# 修复：Linux 下 Nuitka onefile 打包路径问题

## 问题描述

在 Linux 环境下运行 Nuitka `--onefile` 打包的客户端程序时，`client_state.json` 文件被创建在临时目录（如 `/tmp/onefile_xxxxx/`）下，而不是可执行文件所在的目录。

## 问题原因

### Nuitka onefile 模式的工作原理

Nuitka 的 `--onefile` 模式在不同操作系统上的行为有所不同：

**Windows:**
- 可执行文件直接运行
- `sys.executable` 指向实际的 `.exe` 文件路径
- 可以直接使用 `sys.executable` 获取程序所在目录

**Linux:**
- 可执行文件首先被解压到临时目录（通常在 `/tmp/` 下）
- 程序实际在临时目录中运行
- `sys.executable` 指向临时目录中的 Python 解释器，而不是原始可执行文件
- 临时目录在程序退出后会被清理

### 示例

```bash
# Linux 下运行 onefile 打包的程序
$ ./net-manager-client

# 程序内部 sys.executable 的值
# /tmp/onefile_12345_net-manager-client/python  # 临时目录！

# 实际的可执行文件路径
# /home/user/net-manager/net-manager-client
```

这导致如果使用 `sys.executable` 来确定配置文件路径，文件会被创建在临时目录中，程序退出后就会丢失。

## 解决方案

### 使用 `sys.argv[0]` 和 `os.path.realpath()`

在 Linux 环境下，应该使用 `sys.argv[0]` 配合 `os.path.realpath()` 来获取真实的可执行文件路径：

```python
def _get_application_path(self) -> Path:
    """获取应用程序路径，兼容开发环境和打包环境"""
    try:
        is_frozen = getattr(sys, "frozen", False)
        is_nuitka = "__compiled__" in globals()
        
        if is_frozen or is_nuitka:
            # 打包后的可执行文件路径
            if os.name != 'nt':
                # Linux/Unix系统：使用realpath解析符号链接，获取真实路径
                executable_path = os.path.realpath(sys.argv[0])
                application_path = Path(executable_path).parent
                logger.info(f"检测到Linux打包环境，使用argv[0]: {executable_path}")
            else:
                # Windows系统：sys.executable是可靠的
                application_path = Path(sys.executable).parent
                logger.info(f"检测到Windows打包环境，使用executable: {sys.executable}")
        else:
            # 开发环境
            application_path = Path(__file__).parent.parent.parent
            logger.info(f"检测到开发环境，应用路径: {application_path}")
        
        return application_path
```

### 关键点说明

1. **`sys.argv[0]`**：包含程序启动时的命令行参数，通常是可执行文件的路径
2. **`os.path.realpath()`**：解析符号链接，返回真实的绝对路径
3. **平台区分**：Windows 下 `sys.executable` 是可靠的，Linux 下需要使用 `sys.argv[0]`

## 验证修复

### 方法1：查看日志输出

运行程序后，查看日志中的路径信息：

```bash
$ ./net-manager-client

# 日志输出应该显示：
# 检测到Linux打包环境，使用argv[0]: /home/user/net-manager/net-manager-client
# 最终应用程序路径: /home/user/net-manager (可写: True)
```

### 方法2：检查文件位置

```bash
# 运行程序
$ ./net-manager-client &

# 等待几秒后，检查文件是否在正确位置
$ ls -la client_state.json
-rw-r--r-- 1 user user 123 Jan 01 12:00 client_state.json

# 文件应该和可执行文件在同一目录
$ ls -la
total XXX
drwxr-xr-x 2 user user 4096 Jan 01 12:00 .
drwxr-xr-x 3 user user 4096 Jan 01 11:59 ..
-rwxr-xr-x 1 user user XXXX Jan 01 11:59 net-manager-client
-rw-r--r-- 1 user user  123 Jan 01 12:00 client_state.json
```

### 方法3：使用验证脚本

```bash
$ chmod +x verify_linux_state_file.sh
$ ./verify_linux_state_file.sh
```

## 路径获取方法对比

| 方法 | Windows | Linux (onefile) | 开发环境 | 推荐 |
|------|---------|-----------------|----------|------|
| `sys.executable` | ✅ 正确 | ❌ 临时目录 | ✅ 正确 | Windows 打包 |
| `sys.argv[0]` | ✅ 正确 | ✅ 正确 | ✅ 正确 | Linux 打包 |
| `__file__` | ❌ 打包后不可用 | ❌ 打包后不可用 | ✅ 正确 | 仅开发环境 |
| `os.path.realpath(sys.argv[0])` | ✅ 正确 | ✅ 正确 | ✅ 正确 | **推荐** |

## 相关技术细节

### sys.argv[0] 的可能值

```python
# 直接运行
$ ./net-manager-client
sys.argv[0] = './net-manager-client'

# 使用绝对路径
$ /home/user/net-manager/net-manager-client
sys.argv[0] = '/home/user/net-manager/net-manager-client'

# 通过符号链接运行
$ ln -s /opt/net-manager/net-manager-client ~/my-client
$ ~/my-client
sys.argv[0] = '/home/user/my-client'
os.path.realpath(sys.argv[0]) = '/opt/net-manager/net-manager-client'
```

### 为什么需要 realpath()

- 解析符号链接，获取真实路径
- 转换相对路径为绝对路径
- 处理路径中的 `.` 和 `..`

```python
# 示例
import os

# 相对路径
print(os.path.realpath('./net-manager-client'))
# 输出: /home/user/net-manager/net-manager-client

# 符号链接
print(os.path.realpath('/home/user/my-client'))
# 输出: /opt/net-manager/net-manager-client (实际文件位置)
```

## 其他受影响的模块

如果项目中其他模块也需要获取程序路径，建议统一使用这个方法：

### singleton_manager.py

```python
def _acquire_lock_unix(self) -> bool:
    """Unix/Linux平台获取文件锁"""
    try:
        is_frozen = getattr(sys, 'frozen', False)
        is_nuitka = '__compiled__' in globals()
        
        if is_frozen or is_nuitka:
            if os.name != 'nt':
                # Linux: 使用 argv[0]
                executable_path = os.path.realpath(sys.argv[0])
                application_path = os.path.dirname(executable_path)
            else:
                # Windows: 使用 sys.executable
                application_path = os.path.dirname(sys.executable)
        else:
            # 开发环境
            application_path = os.path.dirname(os.path.abspath(__file__))
```

### logger.py

如果日志文件也需要保存在程序目录：

```python
def setup_logger() -> logging.Logger:
    """设置日志记录器"""
    # 获取程序目录
    is_frozen = getattr(sys, 'frozen', False)
    is_nuitka = '__compiled__' in globals()
    
    if is_frozen or is_nuitka:
        if os.name != 'nt':
            app_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
        else:
            app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    log_file = os.path.join(app_dir, 'logs', 'net_manager.log')
```

## 最佳实践

1. **统一路径获取方法**
   - 创建一个工具函数，统一处理路径获取
   - 避免在不同模块中重复实现

2. **充分的日志记录**
   - 记录检测到的环境类型
   - 记录使用的路径获取方法
   - 记录最终的路径和权限状态

3. **跨平台测试**
   - Windows 和 Linux 都要测试
   - 测试不同的启动方式（相对路径、绝对路径、符号链接）

4. **错误处理**
   - 处理路径无效的情况
   - 处理权限不足的情况
   - 提供清晰的错误信息

## 参考资料

- [Nuitka User Manual - Standalone Mode](https://nuitka.net/doc/user-manual.html#onefile-finding-files)
- [Python sys.argv 文档](https://docs.python.org/3/library/sys.html#sys.argv)
- [Python os.path.realpath 文档](https://docs.python.org/3/library/os.path.html#os.path.realpath)
- [Stack Overflow: Getting the path of the executable in Python](https://stackoverflow.com/questions/404744/)

## 相关文件

- `client/src/core/state_manager.py` - 状态管理器（已修复）
- `docs/LINUX_FILE_PERMISSIONS_FIX.md` - Linux 文件权限修复文档
- `verify_linux_state_file.sh` - Linux 验证脚本
