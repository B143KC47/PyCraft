#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
场景面板类
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QOpenGLWidget
from PyQt5.QtCore import Qt


class ScenePanel(QWidget):
    """场景面板类"""
    
    def __init__(self):
        """初始化场景面板"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建OpenGL窗口部件
        self.gl_widget = QOpenGLWidget()
        layout.addWidget(self.gl_widget)
        
        # 设置焦点策略
        self.setFocusPolicy(Qt.StrongFocus)
    
    def load_scene(self, scene_path):
        """加载场景
        
        Args:
            scene_path (str): 场景文件路径
        """
        # TODO: 实现场景加载功能
        pass 