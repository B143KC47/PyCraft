"""
UI画布类，UI元素的容器
"""

import pygame
from OpenGL.GL import *
import numpy as np

from engine.ui.components.ui_component import UIComponent


class UICanvas(UIComponent):
    """UI画布类，UI元素的容器"""
    
    def __init__(self, name, width, height):
        """
        初始化UI画布
        
        Args:
            name (str): 画布名称
            width (float): 宽度
            height (float): 高度
        """
        super().__init__(0, 0, width, height)
        self.name = name
        self.background_color = (0, 0, 0, 0)  # 透明背景
        self.border_width = 0  # 无边框
        self.widgets = []  # 控件列表
    
    def create_widget(self, widget_type, *args, **kwargs):
        """
        创建UI控件
        
        Args:
            widget_type: 控件类型
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            widget: 创建的控件
        """
        widget = widget_type(*args, **kwargs)
        self.add_widget(widget)
        return widget
    
    def add_widget(self, widget):
        """
        添加UI控件
        
        Args:
            widget: 要添加的控件
            
        Returns:
            widget: 添加的控件
        """
        self.widgets.append(widget)
        self.add_child(widget)
        return widget
    
    def remove_widget(self, widget):
        """
        移除UI控件
        
        Args:
            widget: 要移除的控件
            
        Returns:
            bool: 是否成功移除
        """
        if widget in self.widgets:
            self.widgets.remove(widget)
            self.remove_child(widget)
            return True
        
        return False
    
    def get_widget_by_name(self, name):
        """
        通过名称获取控件
        
        Args:
            name (str): 控件名称
            
        Returns:
            widget: 控件实例，如果不存在则返回None
        """
        for widget in self.widgets:
            if hasattr(widget, 'name') and widget.name == name:
                return widget
        
        return None
    
    def clear(self):
        """清空画布"""
        self.widgets.clear()
        self.children.clear()
    
    def update(self, delta_time):
        """
        更新画布
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        super().update(delta_time)
    
    def render(self):
        """渲染画布"""
        if not self.visible:
            return
        
        # 渲染子组件
        for child in self.children:
            child.render()
    
    def process_event(self, event):
        """
        处理事件
        
        Args:
            event: Pygame事件
            
        Returns:
            bool: 事件是否被处理
        """
        return super().process_event(event)
    
    def __str__(self):
        """字符串表示"""
        return f"UICanvas(name={self.name}, widgets={len(self.widgets)})" 