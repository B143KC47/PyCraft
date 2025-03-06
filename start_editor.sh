#!/bin/bash
echo "正在启动 PyCraft 编辑器..."
python3 start_editor.py "$@"
if [ $? -ne 0 ]; then
    echo "启动失败，请检查错误信息。"
    read -p "按回车键继续..."
fi 