import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from core.ecs import System
from core.game import Position, Graphic

class RenderSystem(System):
    """渲染系统，负责使用PyOpenGL渲染实体"""
    def __init__(self, game):
        super().__init__(game)
        pygame.display.set_mode((game.width, game.height), pygame.DOUBLEBUF | pygame.OPENGL)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        
        # 初始化透视投影
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (game.width / game.height), 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)

    def render(self):
        """渲染所有具有Graphic组件的实体"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 设置相机位置
        gluLookAt(0, 0, -5, 0, 0, 0, 0, 1, 0)
        
        for entity in self.game.entities.values():
            position = entity.get_component("Position")
            graphic = entity.get_component("Graphic")
            
            if position and graphic:
                self.render_entity(entity, position, graphic)
        
        pygame.display.flip()

    def render_entity(self, entity, position, graphic):
        """渲染单个实体"""
        # 示例：简单绘制一个立方体
        glPushMatrix()
        glTranslatef(position.x, position.y, position.z)
        self.draw_cube()
        glPopMatrix()

    def draw_cube(self):
        """绘制一个立方体"""
        glBegin(GL_QUADS)
        
        # 顶面
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        
        # 底面
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)
        
        # 前面
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)
        
        # 后面
        glColor3f(1.0, 1.0, 0.0)
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)
        
        # 左面
        glColor3f(1.0, 0.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        
        # 右面
        glColor3f(0.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, -1.0)
        
        glEnd()
