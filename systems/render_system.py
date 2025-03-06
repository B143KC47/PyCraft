import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os
from core.components import ComponentType, TransformComponent, RenderComponent, CameraComponent

class RenderSystem:
    """渲染系统，负责渲染所有可见实体"""
    
    def __init__(self, entity_manager, width, height):
        self.entity_manager = entity_manager
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        
        # 初始化OpenGL
        self.init_gl()
        
        # 着色器程序
        self.default_shader = None
        self.current_shader = None
        
        # 加载着色器
        self.load_shaders()
        
        # 相机
        self.active_camera = None
        
        # 创建一个简单的立方体用于测试
        self.create_test_cube()
    
    def init_gl(self):
        """初始化OpenGL设置"""
        # 设置清屏颜色
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # 启用深度测试
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # 启用背面剔除
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # 设置视口
        glViewport(0, 0, self.width, self.height)
    
    def load_shaders(self):
        """加载着色器程序"""
        # 简化版本，直接使用固定管线
        # 在实际应用中，应该加载和编译GLSL着色器
        print("使用固定管线渲染...")
    
    def create_test_cube(self):
        """创建一个测试用的立方体"""
        # 立方体顶点（8个顶点）
        self.cube_vertices = [
            # 前面
            -0.5, -0.5,  0.5,  # 左下
             0.5, -0.5,  0.5,  # 右下
             0.5,  0.5,  0.5,  # 右上
            -0.5,  0.5,  0.5,  # 左上
            # 后面
            -0.5, -0.5, -0.5,  # 左下
             0.5, -0.5, -0.5,  # 右下
             0.5,  0.5, -0.5,  # 右上
            -0.5,  0.5, -0.5,  # 左上
        ]
        
        # 立方体颜色（每个顶点一个颜色）
        self.cube_colors = [
            1.0, 0.0, 0.0,  # 红
            0.0, 1.0, 0.0,  # 绿
            0.0, 0.0, 1.0,  # 蓝
            1.0, 1.0, 0.0,  # 黄
            1.0, 0.0, 1.0,  # 紫
            0.0, 1.0, 1.0,  # 青
            1.0, 1.0, 1.0,  # 白
            0.5, 0.5, 0.5,  # 灰
        ]
        
        # 立方体面（6个面，每个面2个三角形，每个三角形3个顶点索引）
        self.cube_indices = [
            0, 1, 2, 2, 3, 0,  # 前面
            1, 5, 6, 6, 2, 1,  # 右面
            5, 4, 7, 7, 6, 5,  # 后面
            4, 0, 3, 3, 7, 4,  # 左面
            3, 2, 6, 6, 7, 3,  # 上面
            4, 5, 1, 1, 0, 4   # 下面
        ]
    
    def find_active_camera(self):
        """查找激活的相机"""
        camera_entities = self.entity_manager.get_entities_with_components(
            ComponentType.TRANSFORM, ComponentType.CAMERA
        )
        
        for entity in camera_entities:
            camera_comp = entity.get_component(ComponentType.CAMERA)
            if camera_comp.is_active:
                transform_comp = entity.get_component(ComponentType.TRANSFORM)
                self.active_camera = (camera_comp, transform_comp)
                return
        
        # 如果没有找到激活的相机，创建一个默认相机
        if not self.active_camera:
            self.create_default_camera()
    
    def create_default_camera(self):
        """创建默认相机"""
        camera_entity = self.entity_manager.create_entity("DefaultCamera")
        transform_comp = TransformComponent(position=(0, 0, 5))
        camera_comp = CameraComponent(is_active=True)
        
        camera_entity.add_component(ComponentType.TRANSFORM, transform_comp)
        camera_entity.add_component(ComponentType.CAMERA, camera_comp)
        
        self.active_camera = (camera_comp, transform_comp)
        print("创建了默认相机")
    
    def clear_screen(self):
        """清除屏幕"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def render(self):
        """渲染所有可见实体"""
        # 查找激活的相机
        self.find_active_camera()
        
        if not self.active_camera:
            print("没有找到活动相机")
            return
        
        camera_comp, camera_transform = self.active_camera
        
        # 设置投影矩阵
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(camera_comp.fov, self.aspect_ratio, camera_comp.near, camera_comp.far)
        
        # 设置视图矩阵
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # 设置相机位置
        cam_pos = camera_transform.position
        gluLookAt(
            cam_pos[0], cam_pos[1], cam_pos[2],  # 相机位置
            0, 0, 0,                             # 看向的点
            0, 1, 0                              # 上方向
        )
        
        # 渲染测试立方体
        self.render_test_cube()
        
        # 获取所有可渲染实体
        render_entities = self.entity_manager.get_entities_with_components(
            ComponentType.TRANSFORM, ComponentType.RENDER
        )
        
        # 渲染每个实体
        for entity in render_entities:
            transform_comp = entity.get_component(ComponentType.TRANSFORM)
            render_comp = entity.get_component(ComponentType.RENDER)
            
            if not render_comp.visible:
                continue
            
            # 保存当前矩阵
            glPushMatrix()
            
            # 应用变换
            pos = transform_comp.position
            scale = transform_comp.scale
            glTranslatef(pos[0], pos[1], pos[2])
            glScalef(scale[0], scale[1], scale[2])
            
            # 绘制实体（简化版，使用彩色立方体）
            self.draw_colored_cube()
            
            # 恢复矩阵
            glPopMatrix()
    
    def render_test_cube(self):
        """渲染测试立方体"""
        glPushMatrix()
        
        # 旋转立方体以便更好地看到它
        glRotatef(pygame.time.get_ticks() / 20, 0, 1, 0)  # 绕Y轴旋转
        
        # 绘制立方体
        self.draw_colored_cube()
        
        glPopMatrix()
    
    def draw_colored_cube(self):
        """绘制彩色立方体"""
        glBegin(GL_TRIANGLES)
        
        for i in range(0, len(self.cube_indices), 3):
            # 获取三角形的三个顶点索引
            idx1 = self.cube_indices[i]
            idx2 = self.cube_indices[i+1]
            idx3 = self.cube_indices[i+2]
            
            # 设置颜色
            glColor3f(
                self.cube_colors[idx1*3], 
                self.cube_colors[idx1*3+1], 
                self.cube_colors[idx1*3+2]
            )
            # 设置顶点
            glVertex3f(
                self.cube_vertices[idx1*3], 
                self.cube_vertices[idx1*3+1], 
                self.cube_vertices[idx1*3+2]
            )
            
            # 设置颜色
            glColor3f(
                self.cube_colors[idx2*3], 
                self.cube_colors[idx2*3+1], 
                self.cube_colors[idx2*3+2]
            )
            # 设置顶点
            glVertex3f(
                self.cube_vertices[idx2*3], 
                self.cube_vertices[idx2*3+1], 
                self.cube_vertices[idx2*3+2]
            )
            
            # 设置颜色
            glColor3f(
                self.cube_colors[idx3*3], 
                self.cube_colors[idx3*3+1], 
                self.cube_colors[idx3*3+2]
            )
            # 设置顶点
            glVertex3f(
                self.cube_vertices[idx3*3], 
                self.cube_vertices[idx3*3+1], 
                self.cube_vertices[idx3*3+2]
            )
        
        glEnd()
    
    def draw_mesh(self, mesh):
        """绘制网格"""
        # 简化版本，使用彩色立方体代替
        self.draw_colored_cube()
    
    def cleanup(self):
        """清理资源"""
        # 删除着色器程序
        if self.default_shader:
            glDeleteProgram(self.default_shader)
        print("渲染系统资源已清理")
