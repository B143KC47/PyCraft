@echo off
title PyCraft编辑器
echo ==================================================
echo             PyCraft编辑器 - 启动器
echo ==================================================
echo.

:: 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python。请安装Python 3.6或更高版本。
    echo 可以从 https://www.python.org/downloads/ 下载Python。
    echo.
    pause
    exit /b 1
)

:: 确保依赖项已安装
echo [信息] 检查依赖项...
python -c "import PyQt5, OpenGL, numpy, pybullet, pygame" >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 缺少必要的依赖项，尝试安装...
    echo.
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [错误] 依赖项安装失败。请尝试手动安装：
        echo python -m pip install -r requirements.txt
        echo.
        pause
        exit /b 1
    )
    echo [信息] 依赖项安装完成。
    echo.
)

:: 启动编辑器
echo [信息] 正在启动PyCraft编辑器...
echo.
python start_editor.py %*

:: 检查编辑器是否正常退出
if %errorlevel% neq 0 (
    echo.
    echo [错误] PyCraft编辑器异常退出，错误代码: %errorlevel%
    echo 请查看编辑器日志文件了解详情。
    echo.
    pause
    exit /b %errorlevel%
)

exit /b 0