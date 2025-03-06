#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器应用程序类
"""

import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
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
        
        # 显示启动画面
        self._show_splash_screen()
        
        # 创建主窗口
        self.main_window = MainWindow(width, height)
        
        if debug:
            print("编辑器启动于调试模式")
        
        # 显示欢迎信息
        QTimer.singleShot(1000, self._show_welcome_message)
    
    def _show_splash_screen(self):
        """显示启动画面"""
        # 创建一个纯色的启动画面
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.darkBlue)
        
        # 创建启动画面
        splash = QSplashScreen(pixmap)
        
        # 设置字体
        font = QFont("Arial", 14)
        splash.setFont(font)
        
        # 显示消息
        splash.showMessage(
            "正在启动 PyCraft 编辑器...",
            Qt.AlignCenter | Qt.AlignBottom,
            Qt.white
        )
        
        # 显示启动画面
        splash.show()
        
        # 处理事件，确保启动画面显示
        self.app.processEvents()
        
        # 延迟关闭启动画面
        QTimer.singleShot(1500, splash.close)
    
    def _show_welcome_message(self):
        """显示欢迎信息"""
        if not self.debug:  # 在调试模式下不显示欢迎信息
            QMessageBox.information(
                self.main_window,
                "欢迎使用 PyCraft 编辑器",
                "欢迎使用 PyCraft 编辑器！\n\n"
                "已创建一个初始的3D场景，您可以使用以下控制方式浏览场景：\n"
                "- WASD 键：前后左右移动\n"
                "- 空格键：上升\n"
                "- Ctrl 键：下降\n\n"
                "请点击场景视图以获取焦点，然后开始操作。"
            )
    
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