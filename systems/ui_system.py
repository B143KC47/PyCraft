import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from core.components import ComponentType, UIComponent

class UISystem:
    """UI系统，负责处理UI元素"""
    
    def __init__(self, entity_manager, width, height):
        self.entity_manager = entity_manager
        self.width = width
        self.height = height
        self.font = pygame.font.Font(None, 36)  # 默认字体
        self.active_ui = None  # 当前活动的UI元素
    
    def update(self, delta_time):
        """更新UI系统"""
        # 检查鼠标点击
        if pygame.mouse.get_pressed()[0]:  # 左键点击
            mouse_pos = pygame.mouse.get_pos()
            self.handle_click(mouse_pos[0], mouse_pos[1])
    
    def handle_click(self, x, y):
        """处理鼠标点击"""
        ui_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
        
        # 按照Z顺序（从前到后）检查点击
        for entity in sorted(ui_entities, key=lambda e: e.get_component(ComponentType.UI).position[1]):
            ui_comp = entity.get_component(ComponentType.UI)
            
            if not ui_comp.visible:
                continue
                
            # 检查点是否在UI元素内
            if self.is_point_inside(ui_comp, x, y):
                if ui_comp.on_click:
                    ui_comp.on_click(entity)
                self.active_ui = ui_comp
                return
        
        # 如果点击了空白区域，清除活动UI
        self.active_ui = None
    
    def is_point_inside(self, ui_comp, x, y):
        """检查点是否在UI元素内"""
        return (ui_comp.position[0] <= x <= ui_comp.position[0] + ui_comp.size[0] and 
                ui_comp.position[1] <= y <= ui_comp.position[1] + ui_comp.size[1])
    
    def render(self):
        """渲染UI元素"""
        # 切换到正交投影以便于绘制2D UI
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 渲染所有UI元素
        ui_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
        
        # 按照Z顺序（从后到前）渲染
        for entity in sorted(ui_entities, key=lambda e: e.get_component(ComponentType.UI).position[1], reverse=True):
            ui_comp = entity.get_component(ComponentType.UI)
            if ui_comp.visible:
                self.render_ui_element(ui_comp)
        
        # 恢复OpenGL状态
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        
        glMatrixMode(GL_MODELVIEW)
    
    def render_ui_element(self, ui_comp):
        """渲染单个UI元素"""
        # 绘制UI元素背景
        glBegin(GL_QUADS)
        glColor4f(ui_comp.color[0]/255, ui_comp.color[1]/255, ui_comp.color[2]/255, 0.5)
        glVertex2f(ui_comp.position[0], ui_comp.position[1])
        glVertex2f(ui_comp.position[0] + ui_comp.size[0], ui_comp.position[1])
        glVertex2f(ui_comp.position[0] + ui_comp.size[0], ui_comp.position[1] + ui_comp.size[1])
        glVertex2f(ui_comp.position[0], ui_comp.position[1] + ui_comp.size[1])
        glEnd()
        
        # 渲染文本
        if ui_comp.text:
            # 这里需要临时切换回pygame渲染模式来绘制文本
            # 实际项目中建议使用专门的文本渲染库或预渲染文本到纹理
            self.render_text(ui_comp.text, ui_comp.position[0] + 5, ui_comp.position[1] + 5, ui_comp.color, ui_comp.font_size)
    
    def render_text(self, text, x, y, color=(255, 255, 255), font_size=None):
        """渲染文本"""
        # 如果指定了字体大小，使用指定大小的字体
        font = self.font
        if font_size:
            font = pygame.font.Font(None, font_size)
            
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        width = text_surface.get_width()
        height = text_surface.get_height()
        
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + width, y)
        glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
        glTexCoord2f(0, 1); glVertex2f(x, y + height)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures(1, [texture])
    
    def create_button(self, text, position, size, callback=None, color=(100, 100, 200)):
        """创建一个按钮UI元素"""
        entity = self.entity_manager.create_entity("Button")
        ui_comp = UIComponent(position=position, size=size, text=text, visible=True)
        ui_comp.color = color
        ui_comp.on_click = callback
        entity.add_component(ComponentType.UI, ui_comp)
        return entity
    
    def create_label(self, text, position, font_size=16, color=(255, 255, 255)):
        """创建一个文本标签UI元素"""
        entity = self.entity_manager.create_entity("Label")
        ui_comp = UIComponent(position=position, size=(len(text) * font_size // 2, font_size), text=text, visible=True)
        ui_comp.color = color
        ui_comp.font_size = font_size
        entity.add_component(ComponentType.UI, ui_comp)
        return entity
