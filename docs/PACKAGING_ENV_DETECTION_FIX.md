# 打包环境检测修复

## 问题描述

在代码审查中发现，项目中存在**打包环境检测方式不一致**的问题，这可能导致在某些情况下无法正确识别打包环境，进而影响路径获取等功能。

## 发现的问题

### 1. 检测方式不一致

**问题代码：**
```python
# ❌ 错误方式1 - 可能抛出 AttributeError
is_frozen = hasattr(sys, 'frozen') and sys.frozen

# ❌ 错误方式2 - 重复检测
is_frozen = hasattr(sys, 'frozen') and sys.frozen
is_nuitka = '__compiled__' in globals()
if is_frozen or is_nuitka:
    # ...
elif '__compiled__' in globals():  # 重复检测
    # ...
```

**问题分析：**
- `hasattr(sys, 'frozen') and sys.frozen` 在某些情况下可能抛出 `AttributeError`
- `sys.frozen` 可能不是布尔值，而是其他值（如字符串）
- 重复检测 `'__compiled__' in globals()` 导致逻辑冗余

**正确方式：**
```python
# ✅ 正确方式 - 使用 getattr 提供默认值
is_frozen = getattr(sys, 'frozen', False)
is_nuitka = '__compiled__' in globals()

if is_frozen or is_nuitka:
    # 打包环境
else:
    # 开发环境
```

### 2. 路径获取方式不一致

**问题代码：**
```python
# ❌ 在 Linux 下会指向临时目录
if is_frozen or is_nuitka:
    app_path = os.path.dirname(sys.executable)
```

**正确方式：**
```python
# ✅ 跨平台兼容
if is_frozen or is_nuitka:
    if os.name != 'nt':
        # Linux: 使用 argv[0] 避免 Nuitka onefile 临时目录问题
        app_path = os.path.dirname(os.path.realpath(sys.argv[0]))
    else:
        # Windows: sys.executable 是可靠的
        app_path = os.path.dirname(sys.executable)
```

## 修复的文件

### 客户端

1. **`client/main.py`**
   ```python
   def get_app_path() -> str:
       is_frozen = getattr(sys, 'frozen', False)  # ✅ 修复
       is_nuitka = '__compiled__' in globals()
       if is_frozen or is_nuitka:
           if os.name != 'nt':  # ✅ 新增
               app_path = os.path.dirname(os.path.realpath(sys.argv[0]))
           else:
               app_path = os.path.dirname(sys.executable)
       else:
           app_path = os.path.dirname(os.path.abspath(__file__))
       return app_path
   ```

2. **`client/src/core/app_controller.py`**
   ```python
   # 处理开机自启动设置
   is_frozen = getattr(sys, 'frozen', False)  # ✅ 修复
   is_nuitka = '__compiled__' in globals()
   if is_frozen or is_nuitka:
       self._handle_autostart()
   ```

3. **`client/src/core/state_manager.py`**
   - ✅ 已经使用正确方式
   - ✅ 已经正确处理 Linux 路径

### 服务端

4. **`server/src/core/singleton_manager.py`**
   ```python
   def _acquire_lock_unix(self) -> bool:
       is_frozen = getattr(sys, 'frozen', False)  # ✅ 修复
       is_nuitka = '__compiled__' in globals()
       
       if is_frozen or is_nuitka:
           if os.name != 'nt':  # ✅ 新增
               application_path = os.path.dirname(os.path.realpath(sys.argv[0]))
           else:
               application_path = os.path.dirname(sys.executable)
       else:
           application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   ```

## 标准化的检测模式

### 推荐模式

```python
import os
import sys
from pathlib import Path

def get_application_path() -> Path:
    """
    获取应用程序路径（标准化模式）
    
    Returns:
        Path: 应用程序路径
    """
    # 检测打包环境
    is_frozen = getattr(sys, 'frozen', False)
    is_nuitka = '__compiled__' in globals()
    
    if is_frozen or is_nuitka:
        # 打包环境
        if os.name != 'nt':
            # Linux/Unix: 使用 argv[0] 避免 Nuitka onefile 临时目录
            executable_path = os.path.realpath(sys.argv[0])
            app_path = Path(executable_path).parent
        else:
            # Windows: sys.executable 可靠
            app_path = Path(sys.executable).parent
    else:
        # 开发环境
        app_path = Path(__file__).parent
    
    return app_path
```

### 使用场景

**场景1：获取程序所在目录**
```python
app_dir = get_application_path()
config_file = app_dir / "config.json"
```

**场景2：获取锁文件路径**
```python
app_dir = get_application_path()
lock_file = app_dir / "app.lock"
```

**场景3：获取日志目录**
```python
app_dir = get_application_path()
log_dir = app_dir / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
```

## 环境检测说明

### sys.frozen

| 环境 | sys.frozen 值 | 说明 |
|-----|--------------|------|
| 开发环境 | 不存在 | 普通 Python 脚本 |
| PyInstaller | True | PyInstaller 打包 |
| cx_Freeze | True | cx_Freeze 打包 |
| py2exe | True | py2exe 打包 |
| Nuitka | 不存在 | Nuitka 使用不同机制 |

### __compiled__

| 环境 | __compiled__ | 说明 |
|-----|-------------|------|
| 开发环境 | 不存在 | 普通 Python 脚本 |
| Nuitka | 存在 | Nuitka 编译后的代码 |
| PyInstaller | 不存在 | 使用 sys.frozen |

### sys.executable vs sys.argv[0]

| 平台 | 打包工具 | sys.executable | sys.argv[0] | 推荐 |
|-----|---------|---------------|-------------|------|
| Windows | Nuitka onefile | ✅ 正确路径 | ✅ 正确路径 | sys.executable |
| Linux | Nuitka onefile | ❌ 临时目录 | ✅ 正确路径 | sys.argv[0] |
| Windows | PyInstaller | ✅ 正确路径 | ✅ 正确路径 | sys.executable |
| Linux | PyInstaller | ✅ 正确路径 | ✅ 正确路径 | 都可以 |

## 最佳实践

### 1. 统一检测方式

✅ **推荐：**
```python
is_frozen = getattr(sys, 'frozen', False)
is_nuitka = '__compiled__' in globals()
```

❌ **避免：**
```python
is_frozen = hasattr(sys, 'frozen') and sys.frozen
```

### 2. 跨平台路径获取

✅ **推荐：**
```python
if is_frozen or is_nuitka:
    if os.name != 'nt':
        path = os.path.realpath(sys.argv[0])
    else:
        path = sys.executable
```

❌ **避免：**
```python
if is_frozen or is_nuitka:
    path = sys.executable  # Linux 下会出问题
```

### 3. 使用 pathlib

✅ **推荐：**
```python
from pathlib import Path

app_path = Path(executable).parent
config_file = app_path / "config.json"
```

❌ **避免：**
```python
import os

app_path = os.path.dirname(executable)
config_file = os.path.join(app_path, "config.json")
```

### 4. 详细日志记录

✅ **推荐：**
```python
logger.info(f"检测到打包环境: frozen={is_frozen}, nuitka={is_nuitka}")
logger.info(f"使用路径获取方式: {'argv[0]' if os.name != 'nt' else 'executable'}")
logger.info(f"应用程序路径: {app_path}")
```

## 验证方法

### 1. 开发环境测试

```bash
# 直接运行 Python 脚本
python client/main.py

# 检查日志输出
# 应该显示: "检测到开发环境"
```

### 2. Windows 打包测试

```bash
# 打包
python build.py --client

# 运行
dist/client/net-manager-client.exe

# 检查日志输出
# 应该显示: "检测到Windows打包环境"
# 配置文件应在 exe 同目录
```

### 3. Linux 打包测试

```bash
# 打包
python build.py --client

# 运行
dist/client/net-manager-client

# 检查日志输出
# 应该显示: "检测到Linux打包环境，使用argv[0]"
# 配置文件应在可执行文件同目录，不在 /tmp
```

### 4. 符号链接测试（Linux）

```bash
# 创建符号链接
ln -s /opt/net-manager/net-manager-client ~/my-client

# 运行符号链接
~/my-client

# 检查配置文件位置
# 应该在 /opt/net-manager/ 下，而不是 ~/ 下
```

## 相关文档

- [`docs/FIX_LINUX_ONEFILE_PATH.md`](FIX_LINUX_ONEFILE_PATH.md) - Nuitka onefile 路径问题详解
- [`docs/LINUX_FILE_PERMISSIONS_FIX.md`](LINUX_FILE_PERMISSIONS_FIX.md) - Linux 文件权限处理

## 总结

通过统一打包环境检测方式和路径获取逻辑，确保了：

✅ **一致性**：所有模块使用相同的检测和路径获取方式  
✅ **可靠性**：使用 `getattr` 避免 `AttributeError`  
✅ **跨平台**：正确处理 Windows 和 Linux 的差异  
✅ **Nuitka 兼容**：解决 onefile 模式下的临时目录问题  
✅ **可维护性**：代码清晰，易于理解和维护  

这些修复确保了程序在各种环境下都能正确识别打包状态并获取正确的路径。
