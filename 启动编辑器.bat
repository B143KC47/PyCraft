@echo off
echo 正在启动 PyCraft 编辑器...
python start_editor.py %*
if errorlevel 1 (
    echo 启动失败，请检查错误信息。
    pause
) 