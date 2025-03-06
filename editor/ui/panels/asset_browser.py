#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源浏览器面板类
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QFileSystemModel,
    QMenu, QAction
)
from PyQt5.QtCore import QDir, Qt


class AssetBrowser(QWidget):
    """资源浏览器面板类"""
    
    def __init__(self):
        """初始化资源浏览器"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建文件系统模型
        self.model = QFileSystemModel()
        self.model.setReadOnly(False)
        
        # 设置过滤器
        self.model.setNameFilters([
            "*.png", "*.jpg", "*.jpeg",  # 图片
            "*.obj", "*.fbx", "*.gltf",  # 3D模型
            "*.wav", "*.mp3", "*.ogg",   # 音频
            "*.scene"                     # 场景文件
        ])
        self.model.setNameFilterDisables(False)
        
        # 创建树形视图
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        
        # 隐藏不需要的列
        self.tree_view.setColumnHidden(1, True)  # 大小
        self.tree_view.setColumnHidden(2, True)  # 类型
        self.tree_view.setColumnHidden(3, True)  # 修改日期
        
        layout.addWidget(self.tree_view)
    
    def set_root_path(self, path):
        """设置根路径
        
        Args:
            path (str): 资源根路径
        """
        if os.path.exists(path):
            # 设置根路径
            self.model.setRootPath(path)
            # 设置视图的根索引
            self.tree_view.setRootIndex(self.model.index(path))
    
    def _show_context_menu(self, position):
        """显示上下文菜单
        
        Args:
            position: 鼠标位置
        """
        menu = QMenu()
        
        # 添加新建文件夹动作
        new_folder_action = QAction("新建文件夹", self)
        new_folder_action.triggered.connect(self._create_new_folder)
        menu.addAction(new_folder_action)
        
        # 添加导入资源动作
        import_action = QAction("导入资源", self)
        import_action.triggered.connect(self._import_asset)
        menu.addAction(import_action)
        
        # 显示菜单
        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def _create_new_folder(self):
        """创建新文件夹"""
        # TODO: 实现创建新文件夹功能
        pass
    
    def _import_asset(self):
        """导入资源"""
        # TODO: 实现资源导入功能
        pass 