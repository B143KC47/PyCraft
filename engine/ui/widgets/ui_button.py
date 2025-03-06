"""
UI按钮控件，用于处理点击事件
"""

import pygame
from OpenGL.GL import *
import numpy as np

from engine.ui.components.ui_component import UIComponent
from engine.ui.widgets.ui_label import UILabel


class UIButton(UIComponent):
    """UI按钮控件，用于处理点击事件"""
    
    def __init__(self, text="Button", x=0, y=0, width=100, height=30, font_size=16, font_name=None):
        """
        初始化UI按钮
        
        Args:
            text (str): 按钮文本
            x (float): X坐标
            y (float): Y坐标
            width (float): 宽度
            height (float): 高度
            font_size (int): 字体大小
            font_name (str): 字体名称，如果为None则使用默认字体
        """
        super().__init__(x, y, width, height)
        
        # 按钮状态
        self.pressed = False
        
        # 按钮颜色
        self.normal_color = (0.2, 0.2, 0.2, 0.8)  # 正常状态颜色
        self.hover_color = (0.3, 0.3, 0.3, 0.8)  # 悬停状态颜色
        self.pressed_color = (0.1, 0.1, 0.1, 0.8)  # 按下状态颜色
        self.disabled_color = (0.15, 0.15, 0.15, 0.5)  # 禁用状态颜色
        
        # 边框颜色
        self.normal_border_color = (0.5, 0.5, 0.5, 1.0)  # 正常状态边框颜色
        self.hover_border_color = (0.7, 0.7, 0.7, 1.0)  # 悬停状态边框颜色
        self.pressed_border_color = (0.3, 0.3, 0.3, 1.0)  # 按下状态边框颜色
        self.disabled_border_color = (0.3, 0.3, 0.3, 0.5)  # 禁用状态边框颜色
        
        # 文本颜色
        self.normal_text_color = (1.0, 1.0, 1.0, 1.0)  # 正常状态文本颜色
        self.hover_text_color = (1.0, 1.0, 1.0, 1.0)  # 悬停状态文本颜色
        self.pressed_text_color = (0.8, 0.8, 0.8, 1.0)  # 按下状态文本颜色
        self.disabled_text_color = (0.7, 0.7, 0.7, 0.5)  # 禁用状态文本颜色
        
        # 设置初始颜色
        self.background_color = self.normal_color
        self.border_color = self.normal_border_color
        self.text_color = self.normal_text_color
        
        # 创建标签
        self.label = UILabel(text, 0, 0, width, height, font_size, font_name)
        self.label.background_color = (0, 0, 0, 0)  # 透明背景
        self.label.border_width = 0  # 无边框
        self.label.text_color = self.text_color
        self.label.text_alignment = "center"  # 居中对齐
        self.add_child(self.label)
        
        # 点击事件回调
        self.on_click = None
    
    def set_text(self, text):
        """
        设置按钮文本
        
        Args:
            text (str): 按钮文本
        """
        self.label.set_text(text)
    
    def set_font(self, font_name=None, font_size=None):
        """
        设置字体
        
        Args:
            font_name (str): 字体名称，如果为None则使用当前字体
            font_size (int): 字体大小，如果为None则使用当前大小
        """
        self.label.set_font(font_name, font_size)
    
    def set_colors(self, normal_color=None, hover_color=None, pressed_color=None, disabled_color=None):
        """
        设置按钮颜色
        
        Args:
            normal_color (tuple): 正常状态颜色，RGBA格式，值范围0-1
            hover_color (tuple): 悬停状态颜色，RGBA格式，值范围0-1
            pressed_color (tuple): 按下状态颜色，RGBA格式，值范围0-1
            disabled_color (tuple): 禁用状态颜色，RGBA格式，值范围0-1
        """
        if normal_color:
            self.normal_color = normal_color
        
        if hover_color:
            self.hover_color = hover_color
        
        if pressed_color:
            self.pressed_color = pressed_color
        
        if disabled_color:
            self.disabled_color = disabled_color
        
        # 更新当前颜色
        self._update_colors()
    
    def set_border_colors(self, normal_color=None, hover_color=None, pressed_color=None, disabled_color=None):
        """
        设置边框颜色
        
        Args:
            normal_color (tuple): 正常状态边框颜色，RGBA格式，值范围0-1
            hover_color (tuple): 悬停状态边框颜色，RGBA格式，值范围0-1
            pressed_color (tuple): 按下状态边框颜色，RGBA格式，值范围0-1
            disabled_color (tuple): 禁用状态边框颜色，RGBA格式，值范围0-1
        """
        if normal_color:
            self.normal_border_color = normal_color
        
        if hover_color:
            self.hover_border_color = hover_color
        
        if pressed_color:
            self.pressed_border_color = pressed_color
        
        if disabled_color:
            self.disabled_border_color = disabled_color
        
        # 更新当前颜色
        self._update_colors()
    
    def set_text_colors(self, normal_color=None, hover_color=None, pressed_color=None, disabled_color=None):
        """
        设置文本颜色
        
        Args:
            normal_color (tuple): 正常状态文本颜色，RGBA格式，值范围0-1
            hover_color (tuple): 悬停状态文本颜色，RGBA格式，值范围0-1
            pressed_color (tuple): 按下状态文本颜色，RGBA格式，值范围0-1
            disabled_color (tuple): 禁用状态文本颜色，RGBA格式，值范围0-1
        """
        if normal_color:
            self.normal_text_color = normal_color
        
        if hover_color:
            self.hover_text_color = hover_color
        
        if pressed_color:
            self.pressed_text_color = pressed_color
        
        if disabled_color:
            self.disabled_text_color = disabled_color
        
        # 更新当前颜色
        self._update_colors()
    
    def _update_colors(self):
        """更新当前颜色"""
        if not self.enabled:
            self.background_color = self.disabled_color
            self.border_color = self.disabled_border_color
            self.text_color = self.disabled_text_color
        elif self.pressed:
            self.background_color = self.pressed_color
            self.border_color = self.pressed_border_color
            self.text_color = self.pressed_text_color
        elif self.hover:
            self.background_color = self.hover_color
            self.border_color = self.hover_border_color
            self.text_color = self.hover_text_color
        else:
            self.background_color = self.normal_color
            self.border_color = self.normal_border_color
            self.text_color = self.normal_text_color
        
        # 更新标签颜色
        self.label.text_color = self.text_color
    
    def set_size(self, width, height):
        """
        设置大小
        
        Args:
            width (float): 宽度
            height (float): 高度
        """
        super().set_size(width, height)
        
        # 更新标签大小
        self.label.set_size(width, height)
    
    def _handle_mouse_motion(self, event):
        """
        处理鼠标移动事件
        
        Args:
            event: Pygame鼠标移动事件
            
        Returns:
            bool: 事件是否被处理
        """
        result = super()._handle_mouse_motion(event)
        
        # 更新颜色
        self._update_colors()
        
        return result
    
    def _handle_mouse_down(self, event):
        """
        处理鼠标按下事件
        
        Args:
            event: Pygame鼠标按下事件
            
        Returns:
            bool: 事件是否被处理
        """
        if event.button != 1:  # 只处理左键
            return False
        
        x, y = event.pos
        
        if self.contains_point(x, y) and self.enabled:
            self.pressed = True
            self._update_colors()
            return True
        
        return False
    
    def _handle_mouse_up(self, event):
        """
        处理鼠标释放事件
        
        Args:
            event: Pygame鼠标释放事件
            
        Returns:
            bool: 事件是否被处理
        """
        if event.button != 1:  # 只处理左键
            return False
        
        was_pressed = self.pressed
        self.pressed = False
        
        x, y = event.pos
        
        if was_pressed and self.contains_point(x, y) and self.enabled:
            # 触发点击事件
            if self.on_click:
                self.on_click(self)
            
            # 更新颜色
            self._update_colors()
            
            return True
        
        # 更新颜色
        self._update_colors()
        
        return False
    
    def enable(self):
        """启用按钮"""
        if not self.enabled:
            self.enabled = True
            self._update_colors()
    
    def disable(self):
        """禁用按钮"""
        if self.enabled:
            self.enabled = False
            self.pressed = False
            self._update_colors()
    
    def update(self, delta_time):
        """
        更新按钮
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        super().update(delta_time)
    
    def render(self):
        """渲染按钮"""
        super().render() 