#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
属性面板类
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFormLayout


class PropertyPanel(QWidget):
    """属性面板类"""
    
    def __init__(self):
        """初始化属性面板"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建滚动区域
        scroll = QScrollArea()
        layout.addWidget(scroll)
        
        # 创建内容窗口部件
        content = QWidget()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        
        # 创建表单布局
        self.form_layout = QFormLayout()
        content.setLayout(self.form_layout)
    
    def update_properties(self, entity):
        """更新属性显示
        
        Args:
            entity: 要显示属性的实体
        """
        # 清除现有的属性
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not entity:
            return
        
        # TODO: 根据实体的组件添加属性控件 