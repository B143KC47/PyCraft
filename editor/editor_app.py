#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器应用程序类
"""

import sys
from PyQt5.QtWidgets import QApplication
from editor.ui.main_window import MainWindow


class EditorApp:
    """编辑器应用程序类"""
    
    def __init__(self, width=1920, height=1080, debug=False):
        """初始化编辑器应用程序
        
        Args:
            width (int): 窗口宽度
            height (int): 窗口高度
            debug (bool): 是否启用调试模式
        """
        self.width = width
        self.height = height
        self.debug = debug
        
        # 创建Qt应用程序
        self.app = QApplication(sys.argv)
        
        # 创建主窗口
        self.main_window = MainWindow(width, height)
        
        if debug:
            print("编辑器启动于调试模式")
    
    def open_project(self, project_path):
        """打开项目
        
        Args:
            project_path (str): 项目路径
        """
        if self.debug:
            print(f"打开项目: {project_path}")
        self.main_window.open_project(project_path)
    
    def load_scene(self, scene_path):
        """加载场景
        
        Args:
            scene_path (str): 场景文件路径
        """
        if self.debug:
            print(f"加载场景: {scene_path}")
        self.main_window.load_scene(scene_path)
    
    def run(self):
        """运行编辑器"""
        # 显示主窗口
        self.main_window.show()
        
        # 运行Qt应用程序
        return self.app.exec_() 