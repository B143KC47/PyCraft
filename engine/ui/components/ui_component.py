"""
UI组件基类，所有UI组件的基础
"""

import pygame
from OpenGL.GL import *
import numpy as np


class UIComponent:
    """UI组件基类，所有UI组件都应继承自此类"""
    
    def __init__(self, x=0, y=0, width=100, height=30):
        """
        初始化UI组件
        
        Args:
            x (float): X坐标
            y (float): Y坐标
            width (float): 宽度
            height (float): 高度
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.enabled = True
        self.parent = None
        self.children = []
        self.background_color = (0.2, 0.2, 0.2, 0.8)  # RGBA
        self.border_color = (0.5, 0.5, 0.5, 1.0)  # RGBA
        self.text_color = (1.0, 1.0, 1.0, 1.0)  # RGBA
        self.border_width = 1
        self.padding = 5
        self.hover = False
        self.focused = False
        self.dragging = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.on_click = None  # 点击事件回调
        self.on_hover = None  # 悬停事件回调
        self.on_focus = None  # 获取焦点事件回调
        self.on_blur = None  # 失去焦点事件回调
    
    def set_position(self, x, y):
        """
        设置位置
        
        Args:
            x (float): X坐标
            y (float): Y坐标
        """
        self.x = x
        self.y = y
    
    def set_size(self, width, height):
        """
        设置大小
        
        Args:
            width (float): 宽度
            height (float): 高度
        """
        self.width = width
        self.height = height
    
    def get_absolute_position(self):
        """
        获取绝对位置
        
        Returns:
            tuple: (x, y) 绝对坐标
        """
        if self.parent:
            parent_x, parent_y = self.parent.get_absolute_position()
            return (parent_x + self.x, parent_y + self.y)
        
        return (self.x, self.y)
    
    def contains_point(self, x, y):
        """
        检查点是否在组件内
        
        Args:
            x (float): X坐标
            y (float): Y坐标
            
        Returns:
            bool: 点是否在组件内
        """
        abs_x, abs_y = self.get_absolute_position()
        return (abs_x <= x <= abs_x + self.width and
                abs_y <= y <= abs_y + self.height)
    
    def add_child(self, child):
        """
        添加子组件
        
        Args:
            child (UIComponent): 子组件
            
        Returns:
            UIComponent: 子组件
        """
        child.parent = self
        self.children.append(child)
        return child
    
    def remove_child(self, child):
        """
        移除子组件
        
        Args:
            child (UIComponent): 子组件
            
        Returns:
            bool: 是否成功移除
        """
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            return True
        
        return False
    
    def process_event(self, event):
        """
        处理事件
        
        Args:
            event: Pygame事件
            
        Returns:
            bool: 事件是否被处理
        """
        if not self.visible or not self.enabled:
            return False
        
        # 处理子组件事件
        for child in reversed(self.children):  # 从上到下处理
            if child.process_event(event):
                return True
        
        # 处理鼠标事件
        if event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self._handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            return self._handle_mouse_up(event)
        
        return False
    
    def _handle_mouse_motion(self, event):
        """
        处理鼠标移动事件
        
        Args:
            event: Pygame鼠标移动事件
            
        Returns:
            bool: 事件是否被处理
        """
        x, y = event.pos
        
        # 检查悬停状态
        was_hover = self.hover
        self.hover = self.contains_point(x, y)
        
        # 悬停状态改变
        if was_hover != self.hover and self.on_hover:
            self.on_hover(self, self.hover)
        
        # 处理拖动
        if self.dragging:
            self.x = x - self.drag_offset_x
            self.y = y - self.drag_offset_y
            return True
        
        return self.hover
    
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
        
        if self.contains_point(x, y):
            # 设置焦点
            self._set_focus(True)
            
            # 开始拖动
            abs_x, abs_y = self.get_absolute_position()
            self.drag_offset_x = x - abs_x
            self.drag_offset_y = y - abs_y
            self.dragging = True
            
            return True
        else:
            # 失去焦点
            self._set_focus(False)
            
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
        
        was_dragging = self.dragging
        self.dragging = False
        
        x, y = event.pos
        
        if was_dragging and self.contains_point(x, y):
            # 点击事件
            if self.on_click:
                self.on_click(self)
            
            return True
        
        return False
    
    def _set_focus(self, focused):
        """
        设置焦点状态
        
        Args:
            focused (bool): 是否获取焦点
        """
        if self.focused != focused:
            self.focused = focused
            
            if focused and self.on_focus:
                self.on_focus(self)
            elif not focused and self.on_blur:
                self.on_blur(self)
    
    def update(self, delta_time):
        """
        更新组件
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        # 更新子组件
        for child in self.children:
            child.update(delta_time)
    
    def render(self):
        """渲染组件"""
        if not self.visible:
            return
        
        # 获取绝对位置
        abs_x, abs_y = self.get_absolute_position()
        
        # 渲染背景
        self._render_background(abs_x, abs_y)
        
        # 渲染边框
        self._render_border(abs_x, abs_y)
        
        # 渲染子组件
        for child in self.children:
            child.render()
    
    def _render_background(self, x, y):
        """
        渲染背景
        
        Args:
            x (float): X坐标
            y (float): Y坐标
        """
        glColor4f(*self.background_color)
        
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + self.width, y)
        glVertex2f(x + self.width, y + self.height)
        glVertex2f(x, y + self.height)
        glEnd()
    
    def _render_border(self, x, y):
        """
        渲染边框
        
        Args:
            x (float): X坐标
            y (float): Y坐标
        """
        if self.border_width <= 0:
            return
        
        glColor4f(*self.border_color)
        glLineWidth(self.border_width)
        
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + self.width, y)
        glVertex2f(x + self.width, y + self.height)
        glVertex2f(x, y + self.height)
        glEnd()
    
    def __str__(self):
        """字符串表示"""
        return f"{self.__class__.__name__}(x={self.x}, y={self.y}, width={self.width}, height={self.height})" 