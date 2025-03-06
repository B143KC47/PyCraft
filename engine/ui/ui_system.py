"""
UI系统，管理游戏内UI元素
"""

import pygame
from OpenGL.GL import *
import numpy as np

from engine.core.ecs.system import System
from engine.ui.components.ui_component import UIComponent
from engine.ui.widgets.ui_canvas import UICanvas


class UISystem(System):
    """UI系统，管理游戏内UI元素"""
    
    def __init__(self):
        """初始化UI系统"""
        super().__init__()
        self.canvases = []  # UI画布列表
        self.active_canvas = None  # 当前活动的画布
        self.font_cache = {}  # 字体缓存
        self.texture_cache = {}  # 纹理缓存
        self.screen_width = 0  # 屏幕宽度
        self.screen_height = 0  # 屏幕高度
        self.scale_factor = 1.0  # UI缩放因子
        self.initialized = False  # 是否已初始化
    
    def initialize(self, screen_width, screen_height):
        """
        初始化UI系统
        
        Args:
            screen_width (int): 屏幕宽度
            screen_height (int): 屏幕高度
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 计算UI缩放因子
        base_height = 720  # 基准高度
        self.scale_factor = screen_height / base_height
        
        # 初始化默认字体
        pygame.font.init()
        self.default_font = pygame.font.Font(None, int(24 * self.scale_factor))
        
        # 创建默认画布
        self.create_canvas("default")
        
        self.initialized = True
    
    def create_canvas(self, name):
        """
        创建UI画布
        
        Args:
            name (str): 画布名称
            
        Returns:
            UICanvas: 创建的画布
        """
        canvas = UICanvas(name, self.screen_width, self.screen_height)
        self.canvases.append(canvas)
        
        # 如果没有活动画布，设置为活动
        if self.active_canvas is None:
            self.active_canvas = canvas
        
        return canvas
    
    def get_canvas(self, name):
        """
        获取画布
        
        Args:
            name (str): 画布名称
            
        Returns:
            UICanvas: 画布实例，如果不存在则返回None
        """
        for canvas in self.canvases:
            if canvas.name == name:
                return canvas
        
        return None
    
    def set_active_canvas(self, name):
        """
        设置活动画布
        
        Args:
            name (str): 画布名称
            
        Returns:
            bool: 是否成功设置
        """
        canvas = self.get_canvas(name)
        
        if canvas:
            self.active_canvas = canvas
            return True
        
        return False
    
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
        if self.active_canvas is None:
            raise RuntimeError("没有活动的UI画布")
        
        return self.active_canvas.create_widget(widget_type, *args, **kwargs)
    
    def remove_widget(self, widget):
        """
        移除UI控件
        
        Args:
            widget: 要移除的控件
            
        Returns:
            bool: 是否成功移除
        """
        if self.active_canvas is None:
            return False
        
        return self.active_canvas.remove_widget(widget)
    
    def get_font(self, font_name=None, size=24):
        """
        获取字体
        
        Args:
            font_name (str): 字体名称，如果为None则使用默认字体
            size (int): 字体大小
            
        Returns:
            pygame.font.Font: 字体实例
        """
        # 调整字体大小
        size = int(size * self.scale_factor)
        
        # 如果没有指定字体名称，使用默认字体
        if font_name is None:
            if size == int(24 * self.scale_factor):
                return self.default_font
            
            return pygame.font.Font(None, size)
        
        # 检查缓存
        cache_key = f"{font_name}_{size}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # 创建字体
        try:
            font = pygame.font.Font(font_name, size)
            self.font_cache[cache_key] = font
            return font
        except:
            print(f"加载字体失败: {font_name}")
            return self.default_font
    
    def get_texture(self, image_path):
        """
        获取纹理
        
        Args:
            image_path (str): 图像文件路径
            
        Returns:
            int: 纹理ID
        """
        # 检查缓存
        if image_path in self.texture_cache:
            return self.texture_cache[image_path]
        
        # 加载图像
        try:
            image = pygame.image.load(image_path)
            image = pygame.transform.flip(image, False, True)  # OpenGL坐标系与Pygame相反
            image_data = pygame.image.tostring(image, "RGBA", 1)
            
            # 创建纹理
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # 设置纹理参数
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            
            # 上传纹理数据
            width, height = image.get_size()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            
            # 添加到缓存
            self.texture_cache[image_path] = texture_id
            
            return texture_id
        
        except Exception as e:
            print(f"加载纹理失败: {image_path}, {e}")
            return 0
    
    def process_event(self, event):
        """
        处理UI事件
        
        Args:
            event: Pygame事件
            
        Returns:
            bool: 事件是否被UI处理
        """
        if not self.initialized or self.active_canvas is None:
            return False
        
        return self.active_canvas.process_event(event)
    
    def update(self, delta_time):
        """
        更新UI系统
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        if not self.initialized:
            return
        
        # 更新所有画布
        for canvas in self.canvases:
            canvas.update(delta_time)
    
    def render(self):
        """渲染UI系统"""
        if not self.initialized:
            return
        
        # 设置OpenGL状态
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 设置正交投影
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.screen_width, self.screen_height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # 渲染所有画布
        for canvas in self.canvases:
            if canvas.visible:
                canvas.render()
        
        # 恢复OpenGL状态
        glEnable(GL_DEPTH_TEST)
    
    def shutdown(self):
        """关闭UI系统"""
        # 清除字体缓存
        self.font_cache.clear()
        
        # 清除纹理缓存
        for texture_id in self.texture_cache.values():
            glDeleteTextures(1, [texture_id])
        
        self.texture_cache.clear()
        
        # 清除画布
        for canvas in self.canvases:
            canvas.clear()
        
        self.canvases.clear()
        self.active_canvas = None
        
        # 关闭Pygame字体
        pygame.font.quit()
        
        self.initialized = False 