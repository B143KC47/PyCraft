"""
UI标签控件，用于显示文本
"""

import pygame
from OpenGL.GL import *
import numpy as np

from engine.ui.components.ui_component import UIComponent


class UILabel(UIComponent):
    """UI标签控件，用于显示文本"""
    
    def __init__(self, text="Label", x=0, y=0, width=100, height=30, font_size=16, font_name=None):
        """
        初始化UI标签
        
        Args:
            text (str): 文本内容
            x (float): X坐标
            y (float): Y坐标
            width (float): 宽度
            height (float): 高度
            font_size (int): 字体大小
            font_name (str): 字体名称，如果为None则使用默认字体
        """
        super().__init__(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.font_name = font_name
        self.font = None
        self.text_surface = None
        self.text_texture = None
        self.text_alignment = "left"  # left, center, right
        self.background_color = (0, 0, 0, 0)  # 透明背景
        self.border_width = 0  # 无边框
        self.auto_size = True  # 自动调整大小以适应文本
        self.multiline = False  # 是否支持多行文本
        self.line_spacing = 2  # 行间距
        self.word_wrap = False  # 是否自动换行
    
    def set_text(self, text):
        """
        设置文本内容
        
        Args:
            text (str): 文本内容
        """
        if self.text != text:
            self.text = text
            self._update_text_surface()
            
            # 如果启用自动大小，调整大小
            if self.auto_size:
                if self.text_surface:
                    self.width = self.text_surface.get_width() + self.padding * 2
                    self.height = self.text_surface.get_height() + self.padding * 2
    
    def set_font(self, font_name=None, font_size=None):
        """
        设置字体
        
        Args:
            font_name (str): 字体名称，如果为None则使用当前字体
            font_size (int): 字体大小，如果为None则使用当前大小
        """
        if font_name is not None:
            self.font_name = font_name
        
        if font_size is not None:
            self.font_size = font_size
        
        self._update_text_surface()
    
    def set_text_alignment(self, alignment):
        """
        设置文本对齐方式
        
        Args:
            alignment (str): 对齐方式，可选值为 "left", "center", "right"
        """
        if alignment in ["left", "center", "right"]:
            self.text_alignment = alignment
    
    def _update_text_surface(self):
        """更新文本表面"""
        if not pygame.font.get_init():
            pygame.font.init()
        
        # 获取字体
        if self.font_name:
            self.font = pygame.font.Font(self.font_name, self.font_size)
        else:
            self.font = pygame.font.Font(None, self.font_size)
        
        # 如果文本为空，创建空表面
        if not self.text:
            self.text_surface = pygame.Surface((1, 1), pygame.SRCALPHA)
            return
        
        # 处理多行文本
        if self.multiline:
            self._render_multiline_text()
        else:
            # 渲染文本
            self.text_surface = self.font.render(self.text, True, (
                int(self.text_color[0] * 255),
                int(self.text_color[1] * 255),
                int(self.text_color[2] * 255),
                int(self.text_color[3] * 255)
            ))
        
        # 创建纹理
        self._create_texture()
    
    def _render_multiline_text(self):
        """渲染多行文本"""
        lines = self.text.split('\n')
        
        # 如果启用自动换行，处理每一行
        if self.word_wrap:
            wrapped_lines = []
            for line in lines:
                if line:
                    words = line.split(' ')
                    current_line = words[0]
                    
                    for word in words[1:]:
                        test_line = current_line + ' ' + word
                        test_width = self.font.size(test_line)[0]
                        
                        if test_width <= self.width - self.padding * 2:
                            current_line = test_line
                        else:
                            wrapped_lines.append(current_line)
                            current_line = word
                    
                    wrapped_lines.append(current_line)
                else:
                    wrapped_lines.append('')
            
            lines = wrapped_lines
        
        # 渲染每一行
        line_surfaces = []
        max_width = 0
        
        for line in lines:
            if line:
                line_surface = self.font.render(line, True, (
                    int(self.text_color[0] * 255),
                    int(self.text_color[1] * 255),
                    int(self.text_color[2] * 255),
                    int(self.text_color[3] * 255)
                ))
                line_surfaces.append(line_surface)
                max_width = max(max_width, line_surface.get_width())
            else:
                # 空行
                line_surface = pygame.Surface((1, self.font.get_height()), pygame.SRCALPHA)
                line_surfaces.append(line_surface)
        
        # 创建合并的表面
        total_height = sum(surface.get_height() for surface in line_surfaces) + self.line_spacing * (len(line_surfaces) - 1)
        self.text_surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        
        # 绘制每一行
        y_offset = 0
        for line_surface in line_surfaces:
            # 根据对齐方式计算x偏移
            if self.text_alignment == "center":
                x_offset = (max_width - line_surface.get_width()) // 2
            elif self.text_alignment == "right":
                x_offset = max_width - line_surface.get_width()
            else:  # left
                x_offset = 0
            
            self.text_surface.blit(line_surface, (x_offset, y_offset))
            y_offset += line_surface.get_height() + self.line_spacing
    
    def _create_texture(self):
        """创建纹理"""
        if self.text_surface is None:
            return
        
        # 如果已有纹理，删除
        if self.text_texture:
            glDeleteTextures(1, [self.text_texture])
        
        # 获取表面数据
        width, height = self.text_surface.get_size()
        data = pygame.image.tostring(self.text_surface, "RGBA", 1)
        
        # 创建纹理
        self.text_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.text_texture)
        
        # 设置纹理参数
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        # 上传纹理数据
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    def update(self, delta_time):
        """
        更新标签
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        super().update(delta_time)
        
        # 如果没有文本表面，创建
        if self.text_surface is None:
            self._update_text_surface()
    
    def render(self):
        """渲染标签"""
        if not self.visible:
            return
        
        # 渲染背景和边框
        super().render()
        
        # 如果没有文本纹理，返回
        if self.text_texture is None:
            return
        
        # 获取绝对位置
        abs_x, abs_y = self.get_absolute_position()
        
        # 计算文本位置
        if self.text_surface:
            text_width, text_height = self.text_surface.get_size()
            
            # 根据对齐方式计算x偏移
            if self.text_alignment == "center":
                text_x = abs_x + (self.width - text_width) / 2
            elif self.text_alignment == "right":
                text_x = abs_x + self.width - text_width - self.padding
            else:  # left
                text_x = abs_x + self.padding
            
            # 垂直居中
            text_y = abs_y + (self.height - text_height) / 2
            
            # 渲染文本
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.text_texture)
            
            glColor4f(1, 1, 1, 1)  # 白色，不影响纹理颜色
            
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(text_x, text_y)
            glTexCoord2f(1, 0); glVertex2f(text_x + text_width, text_y)
            glTexCoord2f(1, 1); glVertex2f(text_x + text_width, text_y + text_height)
            glTexCoord2f(0, 1); glVertex2f(text_x, text_y + text_height)
            glEnd()
            
            glDisable(GL_TEXTURE_2D)
    
    def __del__(self):
        """析构函数"""
        # 删除纹理
        if self.text_texture:
            try:
                glDeleteTextures(1, [self.text_texture])
            except:
                pass 