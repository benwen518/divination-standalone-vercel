#!/bin/bash

echo "启动AI算卦服务..."
echo

# 检查是否设置了API密钥
if [ -z "$SILICONFLOW_API_KEY" ]; then
    echo "警告：未设置SILICONFLOW_API_KEY环境变量"
    echo "请先设置API密钥："
    echo "export SILICONFLOW_API_KEY=your-api-key-here"
    echo
    exit 1
fi

# 启动服务
python app.py