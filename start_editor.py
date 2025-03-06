#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器快速启动脚本
"""

import sys
import os
import subprocess
import platform

def check_dependencies():
    """检查依赖项是否已安装"""
    try:
        import PyQt5
        import OpenGL
        import numpy
        import pybullet
        import pygame
        return True
    except ImportError as e:
        print(f"错误: 缺少依赖项 - {e}")
        return False

def install_dependencies():
    """安装依赖项"""
    print("正在安装依赖项...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖项安装成功！")
        return True
    except subprocess.CalledProcessError:
        print("依赖项安装失败，请手动安装。")
        return False

def main():
    """主函数"""
    print("正在启动 PyCraft 编辑器...")
    
    # 检查依赖项
    if not check_dependencies():
        print("是否要自动安装依赖项？(y/n)")
        choice = input().lower()
        if choice == 'y':
            if not install_dependencies():
                return 1
        else:
            print("请手动安装依赖项后再启动编辑器。")
            return 1
    
    # 构建命令行参数
    args = [sys.executable, "main.py", "--editor"]
    
    # 添加调试模式
    if "--debug" in sys.argv:
        args.append("--debug")
    
    # 添加分辨率
    for arg in sys.argv:
        if arg.startswith("--resolution="):
            args.append(arg)
            break
    
    # 启动编辑器
    try:
        if platform.system() == "Windows":
            # 在Windows上使用subprocess.CREATE_NO_WINDOW标志隐藏控制台窗口
            return subprocess.call(args, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            return subprocess.call(args)
    except Exception as e:
        print(f"启动编辑器时出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 