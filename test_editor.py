#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器测试脚本
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

def main():
    """主函数"""
    # 创建Qt应用程序
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("PyCraft Editor Test")
    window.resize(800, 600)
    
    # 创建标签
    label = QLabel("PyCraft 编辑器测试窗口")
    label.setStyleSheet("font-size: 24px; color: #333;")
    window.setCentralWidget(label)
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 