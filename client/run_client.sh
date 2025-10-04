#!/bin/bash

# Net Manager客户端Linux运行脚本
# 作者: Assistant
# 日期: 2024

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3环境"
    echo "请先安装Python3.7或更高版本"
    exit 1
fi

# 检查虚拟环境
VENV_PATH="$PROJECT_DIR/venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "警告: 未找到虚拟环境，将使用系统Python环境"
else
    # 激活虚拟环境
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
        echo "已激活虚拟环境"
    else
        echo "警告: 虚拟环境激活脚本不存在"
    fi
fi

# 检查依赖
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    # 这里可以添加依赖检查逻辑，但为了简化运行流程，我们假设依赖已安装
    echo "项目依赖文件存在: $REQUIREMENTS_FILE"
else
    echo "警告: 未找到依赖文件 $REQUIREMENTS_FILE"
fi

# 进入项目目录并运行客户端
cd "$PROJECT_DIR"
echo "正在启动Net Manager客户端..."
echo "按 Ctrl+C 可以优雅关闭程序"

# 运行客户端主程序
python3 client/main.py

# 检查程序退出状态
if [ $? -eq 0 ]; then
    echo "Net Manager客户端正常退出"
else
    echo "Net Manager客户端异常退出"
    exit 1
fi