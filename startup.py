#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 运行测试脚本
"""

import sys
import os
import subprocess
import platform

def test_editor_startup():
    """测试编辑器启动功能"""
    print("正在测试PyCraft编辑器启动...")
    
    # 获取Python解释器路径
    python_executable = sys.executable
    
    # 构建启动命令 (使用start_editor.py，它会检查依赖并启动编辑器)
    cmd = [python_executable, "start_editor.py", "--debug"]
    
    try:
        # 在Windows上隐藏控制台窗口
        if platform.system() == "Windows":
            try:
                result = subprocess.call(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            except AttributeError:
                # 如果CREATE_NO_WINDOW不可用，使用另一种方法
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.call(cmd, startupinfo=startupinfo)
        else:
            result = subprocess.call(cmd)
        
        # 检查返回值
        if result == 0:
            print("测试成功：编辑器正常启动并退出")
            return True
        else:
            print(f"测试失败：编辑器返回错误代码 {result}")
            return False
            
    except Exception as e:
        print(f"测试异常：{e}")
        return False

def check_dependencies():
    """检查必要的依赖项是否已安装"""
    print("检查依赖项...")
    required_packages = ["PyQt5", "OpenGL", "numpy", "pybullet", "pygame"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n缺少以下依赖项，请先安装：")
        print(", ".join(missing_packages))
        print("可以使用以下命令安装：")
        print(f"{sys.executable} -m pip install -r requirements.txt")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("PyCraft 编辑器测试脚本")
    print("=" * 50)
    
    if not check_dependencies():
        sys.exit(1)
    
    print("\n开始运行编辑器启动测试...")
    if test_editor_startup():
        print("\n所有测试通过！PyCraft编辑器已准备就绪。")
        sys.exit(0)
    else:
        print("\n测试失败！请查看日志文件了解详情。")
        sys.exit(1)