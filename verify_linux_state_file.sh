#!/bin/bash

# Linux 环境下验证状态文件创建功能
# 此脚本用于快速验证打包后的程序是否能正常创建 client_state.json 文件

set -e  # 遇到错误立即退出

echo "========================================"
echo "验证 Linux 打包程序状态文件创建功能"
echo "========================================"

# 检查是否在 Linux 系统
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ 此脚本仅支持 Linux 系统"
    exit 1
fi

# 查找打包后的可执行文件
CLIENT_BIN=""
if [ -f "dist/client/net-manager-client" ]; then
    CLIENT_BIN="dist/client/net-manager-client"
elif [ -f "./net-manager-client" ]; then
    CLIENT_BIN="./net-manager-client"
else
    echo "❌ 未找到客户端可执行文件"
    echo "   请确保已完成打包或在正确的目录下运行此脚本"
    exit 1
fi

echo "✓ 找到客户端程序: $CLIENT_BIN"

# 检查可执行权限
if [ ! -x "$CLIENT_BIN" ]; then
    echo "⚠ 可执行文件没有执行权限，正在设置..."
    chmod +x "$CLIENT_BIN"
    echo "✓ 已设置执行权限"
fi

# 获取程序所在目录
PROGRAM_DIR=$(dirname "$CLIENT_BIN")
echo ""
echo "程序目录: $PROGRAM_DIR"

# 检查目录权限
echo ""
echo "检查目录权限..."
ls -ld "$PROGRAM_DIR"

# 检查目录是否可写
if [ ! -w "$PROGRAM_DIR" ]; then
    echo "❌ 目录不可写，请设置正确的权限"
    echo "   运行: chmod 755 $PROGRAM_DIR"
    exit 1
fi
echo "✓ 目录可写"

# 备份已存在的状态文件（如果有）
STATE_FILE="$PROGRAM_DIR/client_state.json"
if [ -f "$STATE_FILE" ]; then
    echo ""
    echo "⚠ 发现已存在的状态文件，将备份为 client_state.json.bak"
    cp "$STATE_FILE" "$STATE_FILE.bak"
    rm "$STATE_FILE"
fi

# 运行程序（5秒后自动终止）
echo ""
echo "运行客户端程序（5秒后自动停止）..."
timeout 5 "$CLIENT_BIN" &
PID=$!

# 等待程序初始化
sleep 2

# 检查程序是否还在运行
if ! kill -0 $PID 2>/dev/null; then
    echo "⚠ 程序已退出，请检查日志"
fi

# 等待程序完全停止
wait $PID 2>/dev/null || true

echo ""
echo "========================================"
echo "验证结果"
echo "========================================"

# 检查状态文件是否创建
if [ -f "$STATE_FILE" ]; then
    echo "✓ 状态文件创建成功: $STATE_FILE"
    
    # 检查文件权限
    echo ""
    echo "文件权限信息:"
    ls -l "$STATE_FILE"
    
    # 检查文件内容
    echo ""
    echo "文件内容:"
    cat "$STATE_FILE"
    
    # 检查文件权限值
    PERMS=$(stat -c "%a" "$STATE_FILE")
    if [ "$PERMS" = "644" ]; then
        echo ""
        echo "✓ 文件权限设置正确: $PERMS"
    else
        echo ""
        echo "⚠ 文件权限为 $PERMS，期望为 644"
    fi
    
    echo ""
    echo "========================================"
    echo "✓ 所有检查通过！"
    echo "========================================"
    
    exit 0
else
    echo "❌ 状态文件未创建"
    echo ""
    echo "请检查:"
    echo "1. 程序日志输出中的错误信息"
    echo "2. 目录权限是否正确"
    echo "3. 是否有足够的磁盘空间"
    echo ""
    echo "查看日志文件:"
    if [ -f "$PROGRAM_DIR/logs/net_manager.log" ]; then
        echo "  cat $PROGRAM_DIR/logs/net_manager.log"
    fi
    
    echo ""
    echo "========================================"
    echo "❌ 验证失败"
    echo "========================================"
    
    exit 1
fi
