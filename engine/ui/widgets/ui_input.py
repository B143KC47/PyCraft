"""
UI输入框控件，用于文本输入
"""

import pygame
from OpenGL.GL import *
import numpy as np

from engine.ui.components.ui_component import UIComponent
from engine.ui.widgets.ui_label import UILabel


class UIInput(UIComponent):
    """UI输入框控件，用于文本输入"""
    
    def __init__(self, text="", placeholder="输入文本...", x=0, y=0, width=200, height=30, font_size=16, font_name=None):
        """
        初始化UI输入框
        
        Args:
            text (str): 初始文本
            placeholder (str): 占位符文本，当输入框为空时显示
            x (float): X坐标
            y (float): Y坐标
            width (float): 宽度
            height (float): 高度
            font_size (int): 字体大小
            font_name (str): 字体名称，如果为None则使用默认字体
        """
        super().__init__(x, y, width, height)
        
        # 输入框状态
        self.text = text
        self.placeholder = placeholder
        self.cursor_position = len(text)  # 光标位置
        self.selection_start = -1  # 选择开始位置，-1表示没有选择
        self.selection_end = -1  # 选择结束位置，-1表示没有选择
        self.cursor_visible = True  # 光标是否可见
        self.cursor_blink_time = 0.5  # 光标闪烁时间，单位为秒
        self.cursor_timer = 0  # 光标计时器
        self.password_mode = False  # 密码模式
        self.password_char = '*'  # 密码字符
        self.max_length = 0  # 最大长度，0表示无限制
        
        # 输入框颜色
        self.normal_color = (0.2, 0.2, 0.2, 0.8)  # 正常状态颜色
        self.hover_color = (0.25, 0.25, 0.25, 0.8)  # 悬停状态颜色
        self.focus_color = (0.3, 0.3, 0.3, 0.8)  # 焦点状态颜色
        self.disabled_color = (0.15, 0.15, 0.15, 0.5)  # 禁用状态颜色
        
        # 边框颜色
        self.normal_border_color = (0.5, 0.5, 0.5, 1.0)  # 正常状态边框颜色
        self.hover_border_color = (0.6, 0.6, 0.6, 1.0)  # 悬停状态边框颜色
        self.focus_border_color = (0.7, 0.7, 0.7, 1.0)  # 焦点状态边框颜色
        self.disabled_border_color = (0.3, 0.3, 0.3, 0.5)  # 禁用状态边框颜色
        
        # 文本颜色
        self.text_color = (1.0, 1.0, 1.0, 1.0)  # 文本颜色
        self.placeholder_color = (0.7, 0.7, 0.7, 0.7)  # 占位符颜色
        self.selection_color = (0.2, 0.4, 0.8, 0.5)  # 选择区域颜色
        self.cursor_color = (1.0, 1.0, 1.0, 1.0)  # 光标颜色
        
        # 设置初始颜色
        self.background_color = self.normal_color
        self.border_color = self.normal_border_color
        
        # 创建文本标签
        self.label = UILabel("", 0, 0, width, height, font_size, font_name)
        self.label.background_color = (0, 0, 0, 0)  # 透明背景
        self.label.border_width = 0  # 无边框
        self.label.text_color = self.text_color
        self.label.text_alignment = "left"  # 左对齐
        self.label.padding = 5  # 内边距
        self.add_child(self.label)
        
        # 创建占位符标签
        self.placeholder_label = UILabel(placeholder, 0, 0, width, height, font_size, font_name)
        self.placeholder_label.background_color = (0, 0, 0, 0)  # 透明背景
        self.placeholder_label.border_width = 0  # 无边框
        self.placeholder_label.text_color = self.placeholder_color
        self.placeholder_label.text_alignment = "left"  # 左对齐
        self.placeholder_label.padding = 5  # 内边距
        self.add_child(self.placeholder_label)
        
        # 更新标签文本
        self._update_label_text()
        
        # 事件回调
        self.on_text_changed = None  # 文本改变事件回调
        self.on_enter = None  # 回车键事件回调
    
    def set_text(self, text):
        """
        设置文本
        
        Args:
            text (str): 文本内容
        """
        if self.text != text:
            old_text = self.text
            self.text = text
            self.cursor_position = len(text)
            self.selection_start = -1
            self.selection_end = -1
            
            # 更新标签文本
            self._update_label_text()
            
            # 触发文本改变事件
            if self.on_text_changed:
                self.on_text_changed(self, old_text, self.text)
    
    def get_text(self):
        """
        获取文本
        
        Returns:
            str: 文本内容
        """
        return self.text
    
    def set_placeholder(self, placeholder):
        """
        设置占位符
        
        Args:
            placeholder (str): 占位符文本
        """
        self.placeholder = placeholder
        self.placeholder_label.set_text(placeholder)
    
    def set_password_mode(self, password_mode, password_char='*'):
        """
        设置密码模式
        
        Args:
            password_mode (bool): 是否启用密码模式
            password_char (str): 密码字符
        """
        self.password_mode = password_mode
        self.password_char = password_char
        
        # 更新标签文本
        self._update_label_text()
    
    def set_max_length(self, max_length):
        """
        设置最大长度
        
        Args:
            max_length (int): 最大长度，0表示无限制
        """
        self.max_length = max_length
    
    def set_font(self, font_name=None, font_size=None):
        """
        设置字体
        
        Args:
            font_name (str): 字体名称，如果为None则使用当前字体
            font_size (int): 字体大小，如果为None则使用当前大小
        """
        self.label.set_font(font_name, font_size)
        self.placeholder_label.set_font(font_name, font_size)
    
    def set_colors(self, normal_color=None, hover_color=None, focus_color=None, disabled_color=None):
        """
        设置输入框颜色
        
        Args:
            normal_color (tuple): 正常状态颜色，RGBA格式，值范围0-1
            hover_color (tuple): 悬停状态颜色，RGBA格式，值范围0-1
            focus_color (tuple): 焦点状态颜色，RGBA格式，值范围0-1
            disabled_color (tuple): 禁用状态颜色，RGBA格式，值范围0-1
        """
        if normal_color:
            self.normal_color = normal_color
        
        if hover_color:
            self.hover_color = hover_color
        
        if focus_color:
            self.focus_color = focus_color
        
        if disabled_color:
            self.disabled_color = disabled_color
        
        # 更新当前颜色
        self._update_colors()
    
    def set_border_colors(self, normal_color=None, hover_color=None, focus_color=None, disabled_color=None):
        """
        设置边框颜色
        
        Args:
            normal_color (tuple): 正常状态边框颜色，RGBA格式，值范围0-1
            hover_color (tuple): 悬停状态边框颜色，RGBA格式，值范围0-1
            focus_color (tuple): 焦点状态边框颜色，RGBA格式，值范围0-1
            disabled_color (tuple): 禁用状态边框颜色，RGBA格式，值范围0-1
        """
        if normal_color:
            self.normal_border_color = normal_color
        
        if hover_color:
            self.hover_border_color = hover_color
        
        if focus_color:
            self.focus_border_color = focus_color
        
        if disabled_color:
            self.disabled_border_color = disabled_color
        
        # 更新当前颜色
        self._update_colors()
    
    def set_text_color(self, text_color):
        """
        设置文本颜色
        
        Args:
            text_color (tuple): 文本颜色，RGBA格式，值范围0-1
        """
        self.text_color = text_color
        self.label.text_color = text_color
    
    def set_placeholder_color(self, placeholder_color):
        """
        设置占位符颜色
        
        Args:
            placeholder_color (tuple): 占位符颜色，RGBA格式，值范围0-1
        """
        self.placeholder_color = placeholder_color
        self.placeholder_label.text_color = placeholder_color
    
    def set_selection_color(self, selection_color):
        """
        设置选择区域颜色
        
        Args:
            selection_color (tuple): 选择区域颜色，RGBA格式，值范围0-1
        """
        self.selection_color = selection_color
    
    def set_cursor_color(self, cursor_color):
        """
        设置光标颜色
        
        Args:
            cursor_color (tuple): 光标颜色，RGBA格式，值范围0-1
        """
        self.cursor_color = cursor_color
    
    def _update_colors(self):
        """更新当前颜色"""
        if not self.enabled:
            self.background_color = self.disabled_color
            self.border_color = self.disabled_border_color
        elif self.focused:
            self.background_color = self.focus_color
            self.border_color = self.focus_border_color
        elif self.hover:
            self.background_color = self.hover_color
            self.border_color = self.hover_border_color
        else:
            self.background_color = self.normal_color
            self.border_color = self.normal_border_color
    
    def _update_label_text(self):
        """更新标签文本"""
        # 更新文本标签
        if self.text:
            # 如果是密码模式，显示密码字符
            if self.password_mode:
                display_text = self.password_char * len(self.text)
            else:
                display_text = self.text
            
            self.label.set_text(display_text)
            self.placeholder_label.visible = False
        else:
            self.label.set_text("")
            self.placeholder_label.visible = True
    
    def _insert_text(self, text):
        """
        插入文本
        
        Args:
            text (str): 要插入的文本
        """
        # 如果有选择区域，先删除
        if self.selection_start != -1 and self.selection_end != -1:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            
            old_text = self.text
            self.text = self.text[:start] + self.text[end:]
            self.cursor_position = start
            self.selection_start = -1
            self.selection_end = -1
        
        # 检查最大长度
        if self.max_length > 0 and len(self.text) + len(text) > self.max_length:
            text = text[:self.max_length - len(self.text)]
        
        # 插入文本
        if text:
            old_text = self.text
            self.text = self.text[:self.cursor_position] + text + self.text[self.cursor_position:]
            self.cursor_position += len(text)
            
            # 更新标签文本
            self._update_label_text()
            
            # 触发文本改变事件
            if self.on_text_changed:
                self.on_text_changed(self, old_text, self.text)
    
    def _delete_text(self, forward=False):
        """
        删除文本
        
        Args:
            forward (bool): 是否向前删除，True表示Delete键，False表示Backspace键
        """
        # 如果有选择区域，删除选择区域
        if self.selection_start != -1 and self.selection_end != -1:
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            
            old_text = self.text
            self.text = self.text[:start] + self.text[end:]
            self.cursor_position = start
            self.selection_start = -1
            self.selection_end = -1
            
            # 更新标签文本
            self._update_label_text()
            
            # 触发文本改变事件
            if self.on_text_changed:
                self.on_text_changed(self, old_text, self.text)
        
        # 否则删除一个字符
        elif forward and self.cursor_position < len(self.text):
            # Delete键，删除光标后的字符
            old_text = self.text
            self.text = self.text[:self.cursor_position] + self.text[self.cursor_position + 1:]
            
            # 更新标签文本
            self._update_label_text()
            
            # 触发文本改变事件
            if self.on_text_changed:
                self.on_text_changed(self, old_text, self.text)
        
        elif not forward and self.cursor_position > 0:
            # Backspace键，删除光标前的字符
            old_text = self.text
            self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
            self.cursor_position -= 1
            
            # 更新标签文本
            self._update_label_text()
            
            # 触发文本改变事件
            if self.on_text_changed:
                self.on_text_changed(self, old_text, self.text)
    
    def _move_cursor(self, direction, select=False):
        """
        移动光标
        
        Args:
            direction (int): 移动方向，-1表示向左，1表示向右
            select (bool): 是否选择文本
        """
        # 如果是选择模式，更新选择区域
        if select:
            # 如果没有选择区域，开始选择
            if self.selection_start == -1:
                self.selection_start = self.cursor_position
            
            # 移动光标
            if direction < 0 and self.cursor_position > 0:
                self.cursor_position -= 1
            elif direction > 0 and self.cursor_position < len(self.text):
                self.cursor_position += 1
            
            # 更新选择结束位置
            self.selection_end = self.cursor_position
        else:
            # 如果有选择区域，取消选择
            if self.selection_start != -1 and self.selection_end != -1:
                # 如果向左移动，光标移动到选择区域开始位置
                if direction < 0:
                    self.cursor_position = min(self.selection_start, self.selection_end)
                # 如果向右移动，光标移动到选择区域结束位置
                else:
                    self.cursor_position = max(self.selection_start, self.selection_end)
                
                self.selection_start = -1
                self.selection_end = -1
            else:
                # 移动光标
                if direction < 0 and self.cursor_position > 0:
                    self.cursor_position -= 1
                elif direction > 0 and self.cursor_position < len(self.text):
                    self.cursor_position += 1
    
    def _select_all(self):
        """全选文本"""
        self.selection_start = 0
        self.selection_end = len(self.text)
        self.cursor_position = len(self.text)
    
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
            # 设置焦点
            self._set_focus(True)
            
            # 更新颜色
            self._update_colors()
            
            # 计算光标位置
            # 这里简化处理，实际应该根据鼠标位置计算光标位置
            self.cursor_position = len(self.text)
            self.selection_start = -1
            self.selection_end = -1
            
            return True
        else:
            # 失去焦点
            self._set_focus(False)
            
            # 更新颜色
            self._update_colors()
            
            return False
    
    def process_event(self, event):
        """
        处理事件
        
        Args:
            event: Pygame事件
            
        Returns:
            bool: 事件是否被处理
        """
        # 处理鼠标事件
        if event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            return super().process_event(event)
        
        # 处理键盘事件
        if event.type == pygame.KEYDOWN and self.focused and self.enabled:
            # 处理文本输入
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                # 回车键
                if self.on_enter:
                    self.on_enter(self)
                return True
            
            elif event.key == pygame.K_BACKSPACE:
                # 退格键
                self._delete_text(False)
                return True
            
            elif event.key == pygame.K_DELETE:
                # 删除键
                self._delete_text(True)
                return True
            
            elif event.key == pygame.K_LEFT:
                # 左方向键
                self._move_cursor(-1, pygame.key.get_mods() & pygame.KMOD_SHIFT)
                return True
            
            elif event.key == pygame.K_RIGHT:
                # 右方向键
                self._move_cursor(1, pygame.key.get_mods() & pygame.KMOD_SHIFT)
                return True
            
            elif event.key == pygame.K_HOME:
                # Home键
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if self.selection_start == -1:
                        self.selection_start = self.cursor_position
                    self.cursor_position = 0
                    self.selection_end = 0
                else:
                    self.cursor_position = 0
                    self.selection_start = -1
                    self.selection_end = -1
                return True
            
            elif event.key == pygame.K_END:
                # End键
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    if self.selection_start == -1:
                        self.selection_start = self.cursor_position
                    self.cursor_position = len(self.text)
                    self.selection_end = len(self.text)
                else:
                    self.cursor_position = len(self.text)
                    self.selection_start = -1
                    self.selection_end = -1
                return True
            
            elif event.key == pygame.K_a and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Ctrl+A，全选
                self._select_all()
                return True
            
            elif event.key == pygame.K_c and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Ctrl+C，复制
                if self.selection_start != -1 and self.selection_end != -1:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    pygame.scrap.put(pygame.SCRAP_TEXT, self.text[start:end].encode())
                return True
            
            elif event.key == pygame.K_x and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Ctrl+X，剪切
                if self.selection_start != -1 and self.selection_end != -1:
                    start = min(self.selection_start, self.selection_end)
                    end = max(self.selection_start, self.selection_end)
                    pygame.scrap.put(pygame.SCRAP_TEXT, self.text[start:end].encode())
                    self._delete_text()
                return True
            
            elif event.key == pygame.K_v and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # Ctrl+V，粘贴
                if pygame.scrap.has(pygame.SCRAP_TEXT):
                    text = pygame.scrap.get(pygame.SCRAP_TEXT).decode()
                    self._insert_text(text)
                return True
            
            elif event.unicode and not (pygame.key.get_mods() & pygame.KMOD_CTRL):
                # 普通文本输入
                self._insert_text(event.unicode)
                return True
        
        # 处理文本输入事件
        elif event.type == pygame.TEXTINPUT and self.focused and self.enabled:
            self._insert_text(event.text)
            return True
        
        return False
    
    def update(self, delta_time):
        """
        更新输入框
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        super().update(delta_time)
        
        # 更新光标闪烁
        if self.focused:
            self.cursor_timer += delta_time
            if self.cursor_timer >= self.cursor_blink_time:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible
    
    def render(self):
        """渲染输入框"""
        # 渲染背景和边框
        super().render()
        
        # 如果有选择区域，渲染选择区域
        if self.focused and self.selection_start != -1 and self.selection_end != -1 and self.text:
            # 获取绝对位置
            abs_x, abs_y = self.get_absolute_position()
            
            # 计算选择区域位置
            # 这里简化处理，实际应该根据字体计算位置
            start = min(self.selection_start, self.selection_end)
            end = max(self.selection_start, self.selection_end)
            
            # 获取字体
            font = self.label.font
            if not font:
                if not pygame.font.get_init():
                    pygame.font.init()
                font = pygame.font.Font(None, self.label.font_size)
            
            # 计算选择区域位置
            if self.password_mode:
                text_width = font.size(self.password_char * start)[0]
                selection_width = font.size(self.password_char * (end - start))[0]
            else:
                text_width = font.size(self.text[:start])[0]
                selection_width = font.size(self.text[start:end])[0]
            
            # 渲染选择区域
            glColor4f(*self.selection_color)
            
            glBegin(GL_QUADS)
            glVertex2f(abs_x + self.padding + text_width, abs_y + self.padding)
            glVertex2f(abs_x + self.padding + text_width + selection_width, abs_y + self.padding)
            glVertex2f(abs_x + self.padding + text_width + selection_width, abs_y + self.height - self.padding)
            glVertex2f(abs_x + self.padding + text_width, abs_y + self.height - self.padding)
            glEnd()
        
        # 渲染光标
        if self.focused and self.cursor_visible and self.enabled:
            # 获取绝对位置
            abs_x, abs_y = self.get_absolute_position()
            
            # 计算光标位置
            # 这里简化处理，实际应该根据字体计算位置
            font = self.label.font
            if not font:
                if not pygame.font.get_init():
                    pygame.font.init()
                font = pygame.font.Font(None, self.label.font_size)
            
            if self.password_mode:
                cursor_x = abs_x + self.padding + font.size(self.password_char * self.cursor_position)[0]
            else:
                cursor_x = abs_x + self.padding + font.size(self.text[:self.cursor_position])[0]
            
            # 渲染光标
            glColor4f(*self.cursor_color)
            glLineWidth(1)
            
            glBegin(GL_LINES)
            glVertex2f(cursor_x, abs_y + self.padding)
            glVertex2f(cursor_x, abs_y + self.height - self.padding)
            glEnd()
    
    def enable(self):
        """启用输入框"""
        if not self.enabled:
            self.enabled = True
            self._update_colors()
    
    def disable(self):
        """禁用输入框"""
        if self.enabled:
            self.enabled = False
            self.focused = False
            self._update_colors()
    
    def __del__(self):
        """析构函数"""
        # 清理资源
        pass 