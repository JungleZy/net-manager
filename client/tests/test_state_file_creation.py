#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试状态文件创建功能
特别是Linux环境下的文件权限问题
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))


def test_state_file_creation_with_permissions():
    """测试状态文件创建时的权限设置"""
    print("=" * 60)
    print("测试：状态文件创建及权限设置")
    print("=" * 60)

    # 创建临时目录用于测试
    test_dir = Path(tempfile.mkdtemp(prefix="net_manager_test_"))
    print(f"\n临时测试目录: {test_dir}")

    # 保存原始值
    original_executable = sys.executable

    try:
        # 模拟打包环境
        original_executable = sys.executable
        sys.executable = str(test_dir / "test_executable")

        # 设置__compiled__标志模拟Nuitka打包环境
        globals()["__compiled__"] = True

        # 导入状态管理器
        from src.core.state_manager import StateManager

        # 创建状态管理器实例
        print("\n创建状态管理器实例...")
        state_manager = StateManager()

        # 检查状态文件路径
        print(f"\n状态文件路径: {state_manager.state_file}")
        print(f"状态文件存在: {state_manager.state_file.exists()}")

        # 测试获取client_id（会触发文件创建）
        print("\n获取客户端ID...")
        client_id = state_manager.get_client_id()
        print(f"客户端ID: {client_id}")

        # 验证文件是否创建成功
        assert state_manager.state_file.exists(), "状态文件未创建"
        print("✓ 状态文件创建成功")

        # 检查文件权限（仅Linux系统）
        if os.name != "nt":
            file_stat = os.stat(state_manager.state_file)
            file_mode = oct(file_stat.st_mode)[-3:]
            print(f"\n文件权限: {file_mode}")

            dir_stat = os.stat(state_manager.state_file.parent)
            dir_mode = oct(dir_stat.st_mode)[-3:]
            print(f"目录权限: {dir_mode}")

            # 验证权限设置是否正确
            assert file_mode == "644", f"文件权限不正确，期望644，实际{file_mode}"
            print("✓ 文件权限设置正确")

        # 测试读取状态文件
        print("\n测试读取状态...")
        saved_client_id = state_manager.get_state("client_id")
        assert saved_client_id == client_id, "读取的客户端ID不匹配"
        print("✓ 状态读取成功")

        # 测试更新状态
        print("\n测试更新状态...")
        test_value = "test_value_123"
        assert state_manager.set_state("test_key", test_value), "设置状态失败"
        assert state_manager.get_state("test_key") == test_value, "读取的状态值不匹配"
        print("✓ 状态更新成功")

        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # 清理临时目录
        sys.executable = original_executable
        if "__compiled__" in globals():
            del globals()["__compiled__"]

        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"\n已清理临时目录: {test_dir}")

    return True


def test_permission_error_handling():
    """测试权限错误处理"""
    print("\n" + "=" * 60)
    print("测试：权限错误处理")
    print("=" * 60)

    # 仅在Linux系统测试
    if os.name == "nt":
        print("Windows系统跳过此测试")
        return True

    # 创建只读临时目录
    test_dir = Path(tempfile.mkdtemp(prefix="net_manager_readonly_"))
    print(f"\n临时测试目录: {test_dir}")

    # 保存原始值
    original_executable = sys.executable

    try:
        # 设置目录为只读
        os.chmod(test_dir, 0o444)
        print(f"目录权限设为只读: {oct(os.stat(test_dir).st_mode)[-3:]}")

        # 模拟打包环境
        original_executable = sys.executable
        sys.executable = str(test_dir / "test_executable")
        globals()["__compiled__"] = True

        # 尝试创建状态管理器（应该捕获权限错误）
        from src.core.state_manager import StateManager, StateManagerError

        print("\n尝试在只读目录创建状态管理器...")
        try:
            state_manager = StateManager()
            # 如果没有抛出异常，说明权限处理有问题
            print("✗ 应该抛出权限错误，但没有")
            return False
        except StateManagerError as e:
            print(f"✓ 正确捕获权限错误: {e}")
            return True

    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # 清理
        sys.executable = original_executable
        if "__compiled__" in globals():
            del globals()["__compiled__"]

        # 恢复目录权限后删除
        if test_dir.exists():
            os.chmod(test_dir, 0o755)
            shutil.rmtree(test_dir)
            print(f"\n已清理临时目录: {test_dir}")


def main():
    """主测试函数"""
    print("开始测试状态文件创建和权限设置...\n")

    # 运行测试
    test1_passed = test_state_file_creation_with_permissions()
    test2_passed = test_permission_error_handling()

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"状态文件创建测试: {'✓ 通过' if test1_passed else '✗ 失败'}")
    print(f"权限错误处理测试: {'✓ 通过' if test2_passed else '✗ 失败'}")
    print("=" * 60)

    return test1_passed and test2_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
