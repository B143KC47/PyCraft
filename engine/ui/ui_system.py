"""
UI系统，管理游戏内UI元素
"""

import pygame
from OpenGL.GL import *
import numpy as np
import os
import json
import time

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
        
        # 主题相关
        self.themes = {}  # 主题字典
        self.current_theme = "default"  # 当前主题
        
        # 动画相关
        self.animations = []  # 活动动画列表
        self.animation_enabled = True  # 是否启用动画
    
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
        
        # 加载默认主题
        self._init_default_theme()
        
        self.initialized = True
    
    def _init_default_theme(self):
        """初始化默认主题"""
        default_theme = {
            "colors": {
                "background": (32, 32, 32, 255),
                "text": (220, 220, 220, 255),
                "primary": (66, 150, 250, 255),
                "secondary": (180, 180, 180, 255),
                "accent": (255, 140, 0, 255),
                "success": (80, 200, 120, 255),
                "warning": (250, 180, 30, 255),
                "error": (230, 60, 60, 255),
                "disabled": (120, 120, 120, 128)
            },
            "font": {
                "default_size": 16,
                "title_size": 24,
                "small_size": 12,
                "line_height": 1.2
            },
            "button": {
                "padding": (10, 6),
                "border_radius": 4,
                "border_width": 1
            },
            "panel": {
                "padding": (10, 10),
                "border_radius": 4,
                "border_width": 1
            },
            "input": {
                "padding": (8, 4),
                "border_radius": 4,
                "border_width": 1
            }
        }
        
        self.themes["default"] = default_theme
        
        # 创建暗色主题
        dark_theme = default_theme.copy()
        dark_theme["colors"] = {
            "background": (16, 16, 16, 255),
            "text": (220, 220, 220, 255),
            "primary": (50, 120, 220, 255),
            "secondary": (150, 150, 150, 255),
            "accent": (255, 120, 0, 255),
            "success": (70, 180, 100, 255),
            "warning": (220, 160, 20, 255),
            "error": (200, 50, 50, 255),
            "disabled": (80, 80, 80, 128)
        }
        self.themes["dark"] = dark_theme
        
        # 创建亮色主题
        light_theme = default_theme.copy()
        light_theme["colors"] = {
            "background": (240, 240, 240, 255),
            "text": (30, 30, 30, 255),
            "primary": (40, 100, 200, 255),
            "secondary": (120, 120, 120, 255),
            "accent": (220, 100, 0, 255),
            "success": (40, 160, 80, 255),
            "warning": (200, 140, 10, 255),
            "error": (180, 30, 30, 255),
            "disabled": (180, 180, 180, 128)
        }
        self.themes["light"] = light_theme
    
    def load_theme(self, theme_path):
        """
        从文件加载主题
        
        Args:
            theme_path (str): 主题文件路径
            
        Returns:
            bool: 是否成功加载
        """
        try:
            with open(theme_path, 'r') as f:
                theme_data = json.load(f)
            
            theme_name = os.path.basename(theme_path).split('.')[0]
            self.themes[theme_name] = theme_data
            return True
        except Exception as e:
            print(f"加载主题失败: {e}")
            return False
    
    def set_theme(self, theme_name):
        """
        设置当前主题
        
        Args:
            theme_name (str): 主题名称
            
        Returns:
            bool: 是否成功设置
        """
        if theme_name in self.themes:
            self.current_theme = theme_name
            
            # 通知所有画布和组件主题已更改
            for canvas in self.canvases:
                canvas.on_theme_changed(self.themes[theme_name])
            
            return True
        
        return False
    
    def get_theme_value(self, path, default=None):
        """
        获取主题中的值
        
        Args:
            path (str): 路径，例如 "colors.primary"
            default: 如果未找到则返回的默认值
            
        Returns:
            value: 主题中的值
        """
        theme = self.themes.get(self.current_theme, self.themes.get("default"))
        if not theme:
            return default
            
        parts = path.split('.')
        value = theme
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
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
    
    def get_font(self, font_name=None, size=None):
        """
        获取字体
        
        Args:
            font_name (str): 字体名称，如果为None则使用默认字体
            size (int): 字体大小，如果为None则使用主题中的默认大小
            
        Returns:
            pygame.font.Font: 字体实例
        """
        # 如果没有指定大小，使用主题中的默认大小
        if size is None:
            size = self.get_theme_value("font.default_size", 16)
            
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
    
    def create_animation(self, target, property_name, end_value, duration=0.5, delay=0, easing="linear"):
        """
        创建UI动画
        
        Args:
            target: 目标对象
            property_name (str): 属性名称
            end_value: 结束值
            duration (float): 持续时间，单位为秒
            delay (float): 延迟时间，单位为秒
            easing (str): 缓动函数名称
            
        Returns:
            dict: 动画数据
        """
        if not self.animation_enabled:
            # 如果禁用动画，直接设置属性值
            setattr(target, property_name, end_value)
            return None
        
        # 获取起始值
        start_value = getattr(target, property_name)
        
        # 创建动画数据
        animation = {
            "target": target,
            "property": property_name,
            "start_value": start_value,
            "end_value": end_value,
            "duration": duration,
            "delay": delay,
            "easing": easing,
            "start_time": time.time() + delay,
            "elapsed": 0,
            "completed": False
        }
        
        self.animations.append(animation)
        return animation
    
    def _update_animations(self, delta_time):
        """
        更新动画
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        current_time = time.time()
        completed_animations = []
        
        for animation in self.animations:
            if animation["completed"]:
                completed_animations.append(animation)
                continue
                
            # 检查是否已开始
            if current_time < animation["start_time"]:
                continue
                
            # 计算已经过的时间
            animation["elapsed"] = current_time - animation["start_time"]
            progress = min(animation["elapsed"] / animation["duration"], 1.0)
            
            # 应用缓动函数
            eased_progress = self._apply_easing(progress, animation["easing"])
            
            # 计算当前值
            start = animation["start_value"]
            end = animation["end_value"]
            
            current_value = None
            
            # 根据类型计算当前值
            if isinstance(start, (int, float)) and isinstance(end, (int, float)):
                current_value = start + (end - start) * eased_progress
            elif isinstance(start, tuple) and isinstance(end, tuple) and len(start) == len(end):
                # 处理元组（如颜色、位置等）
                current_value = tuple(s + (e - s) * eased_progress for s, e in zip(start, end))
            
            # 设置属性值
            if current_value is not None:
                setattr(animation["target"], animation["property"], current_value)
            
            # 检查是否完成
            if progress >= 1.0:
                animation["completed"] = True
                completed_animations.append(animation)
        
        # 移除已完成的动画
        for animation in completed_animations:
            self.animations.remove(animation)
    
    def _apply_easing(self, t, easing_type):
        """
        应用缓动函数
        
        Args:
            t (float): 线性进度 (0-1)
            easing_type (str): 缓动函数类型
            
        Returns:
            float: 缓动后的进度值 (0-1)
        """
        # 线性
        if easing_type == "linear":
            return t
        
        # 平方缓入
        if easing_type == "easeIn":
            return t * t
        
        # 平方缓出
        if easing_type == "easeOut":
            return t * (2 - t)
        
        # 平方缓入缓出
        if easing_type == "easeInOut":
            return t * t * (3 - 2 * t)
        
        # 弹性缓出
        if easing_type == "elasticOut":
            if t == 0 or t == 1:
                return t
                
            p = 0.3
            s = p / 4
            return pow(2, -10 * t) * np.sin((t - s) * (2 * np.pi) / p) + 1
        
        # 弹跳缓出
        if easing_type == "bounceOut":
            if t < 1 / 2.75:
                return 7.5625 * t * t
            elif t < 2 / 2.75:
                t -= 1.5 / 2.75
                return 7.5625 * t * t + 0.75
            elif t < 2.5 / 2.75:
                t -= 2.25 / 2.75
                return 7.5625 * t * t + 0.9375
            else:
                t -= 2.625 / 2.75
                return 7.5625 * t * t + 0.984375
                
        # 默认线性
        return t
    
    def resize(self, width, height):
        """
        调整UI系统大小
        
        Args:
            width (int): 新宽度
            height (int): 新高度
        """
        self.screen_width = width
        self.screen_height = height
        
        # 重新计算缩放因子
        base_height = 720  # 基准高度
        self.scale_factor = height / base_height
        
        # 调整所有画布大小
        for canvas in self.canvases:
            canvas.resize(width, height)
    
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
        
        # 更新动画
        self._update_animations(delta_time)
        
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
        
        # 清除动画
        self.animations.clear()
        
        # 关闭Pygame字体
        pygame.font.quit()
        
        self.initialized = False
        
    def enable_animations(self, enabled=True):
        """
        启用或禁用动画
        
        Args:
            enabled (bool): 是否启用动画
        """
        self.animation_enabled = enabled