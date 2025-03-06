#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
层级面板类
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem


class HierarchyPanel(QWidget):
    """层级面板类"""
    
    def __init__(self):
        """初始化层级面板"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建树形视图
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("场景层级")
        layout.addWidget(self.tree_widget)
        
        # 连接信号
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _on_selection_changed(self):
        """选择改变时的处理函数"""
        # TODO: 实现选择改变的处理
        pass 