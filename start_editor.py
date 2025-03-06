#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器快速启动脚本
"""

import sys
import os
import subprocess
import platform
import time

def check_dependencies():
    """检查依赖项是否已安装"""
    required_packages = ["PyQt5", "OpenGL", "numpy", "pybullet", "pygame"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"错误: 缺少以下依赖项: {', '.join(missing_packages)}")
        return False
    return True

def install_dependencies():
    """安装依赖项"""
    print("正在安装依赖项...")
    try:
        print("=" * 50)
        print("开始安装必要的Python包，这可能需要一些时间...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("=" * 50)
        print("依赖项安装成功！")
        # 给用户一些时间阅读信息
        time.sleep(1)
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 50)
        print(f"依赖项安装失败: {str(e)}")
        print("请尝试手动运行: pip install -r requirements.txt")
        print("=" * 50)
        time.sleep(3)
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("正在启动 PyCraft 编辑器...")
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: PyCraft 需要 Python 3.6 或更高版本")
        return 1
    
    # 检查依赖项
    if not check_dependencies():
        print("是否要自动安装依赖项？(y/n)")
        choice = input().lower().strip()
        if choice == 'y':
            if not install_dependencies():
                return 1
            # 重新检查，确保依赖项已正确安装
            if not check_dependencies():
                print("依赖项安装后仍有问题，请检查Python环境。")
                return 1
        else:
            print("请手动安装依赖项后再启动编辑器。")
            return 1
    
    # 构建命令行参数
    args = [sys.executable, "editor_main.py"]
    
    # 传递所有额外的命令行参数
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    print(f"启动命令: {' '.join(args)}")
    print("=" * 50)
    
    # 启动编辑器
    try:
        if platform.system() == "Windows":
            # 在Windows上使用subprocess.CREATE_NO_WINDOW标志隐藏控制台窗口
            return subprocess.call(args, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            return subprocess.call(args)
    except Exception as e:
        print(f"启动编辑器时出错: {e}")
        print("请确保文件 editor_main.py 存在并且可执行。")
        input("按Enter键退出...")
        return 1

if __name__ == "__main__":
    sys.exit(main())