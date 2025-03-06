#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
场景面板类
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeyEvent, QMatrix4x4, QVector3D
from OpenGL.GL import *
import numpy as np
import math


class ScenePanel(QWidget):
    """场景面板类"""
    
    def __init__(self):
        """初始化场景面板"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建OpenGL窗口部件
        self.gl_widget = SceneGLWidget()
        layout.addWidget(self.gl_widget)
        
        # 设置焦点策略
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 将键盘事件传递给GL窗口部件
        self.keyPressEvent = self.gl_widget.keyPressEvent
        self.keyReleaseEvent = self.gl_widget.keyReleaseEvent
    
    def load_scene(self, scene_path):
        """加载场景
        
        Args:
            scene_path (str): 场景文件路径
        """
        # TODO: 实现场景加载功能
        pass


class SceneGLWidget(QOpenGLWidget):
    """场景OpenGL窗口部件"""
    
    def __init__(self):
        """初始化OpenGL窗口部件"""
        super().__init__()
        
        # 设置焦点策略
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 相机位置和方向
        self.camera_pos = QVector3D(0.0, 1.5, 5.0)
        self.camera_front = QVector3D(0.0, 0.0, -1.0)
        self.camera_up = QVector3D(0.0, 1.0, 0.0)
        
        # 移动速度
        self.move_speed = 0.1
        
        # 按键状态
        self.keys = {
            Qt.Key_W: False,
            Qt.Key_A: False,
            Qt.Key_S: False,
            Qt.Key_D: False,
            Qt.Key_Space: False,
            Qt.Key_Control: False
        }
        
        # 创建定时器，用于更新场景
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # 约60FPS
        
        # 网格数据
        self.grid_vertices = self.create_grid(20, 1.0)
        self.cube_vertices = self.create_cube()
        
        # 地面颜色
        self.ground_color = (0.5, 0.5, 0.5)
        
        # 立方体位置
        self.cubes = [
            {"position": (0.0, 0.5, 0.0), "color": (1.0, 0.0, 0.0)},
            {"position": (3.0, 0.5, 2.0), "color": (0.0, 1.0, 0.0)},
            {"position": (-2.0, 0.5, -3.0), "color": (0.0, 0.0, 1.0)},
            {"position": (4.0, 0.5, -2.0), "color": (1.0, 1.0, 0.0)},
            {"position": (-3.0, 0.5, 4.0), "color": (0.0, 1.0, 1.0)}
        ]
    
    def create_grid(self, size, step):
        """创建网格顶点数据
        
        Args:
            size (int): 网格大小
            step (float): 网格步长
            
        Returns:
            list: 网格顶点数据
        """
        vertices = []
        half_size = size * step / 2
        
        # 创建水平线
        for i in range(-size, size + 1):
            vertices.extend([
                -half_size, 0.0, i * step,
                half_size, 0.0, i * step
            ])
        
        # 创建垂直线
        for i in range(-size, size + 1):
            vertices.extend([
                i * step, 0.0, -half_size,
                i * step, 0.0, half_size
            ])
        
        return np.array(vertices, dtype=np.float32)
    
    def create_cube(self):
        """创建立方体顶点数据
        
        Returns:
            list: 立方体顶点数据
        """
        vertices = [
            # 前面
            -0.5, -0.5,  0.5,
             0.5, -0.5,  0.5,
             0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5,
            
            # 后面
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5,  0.5, -0.5,
            -0.5,  0.5, -0.5,
            
            # 左面
            -0.5, -0.5, -0.5,
            -0.5, -0.5,  0.5,
            -0.5,  0.5,  0.5,
            -0.5,  0.5, -0.5,
            
            # 右面
             0.5, -0.5, -0.5,
             0.5, -0.5,  0.5,
             0.5,  0.5,  0.5,
             0.5,  0.5, -0.5,
            
            # 上面
            -0.5,  0.5, -0.5,
             0.5,  0.5, -0.5,
             0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5,
            
            # 下面
            -0.5, -0.5, -0.5,
             0.5, -0.5, -0.5,
             0.5, -0.5,  0.5,
            -0.5, -0.5,  0.5
        ]
        
        return np.array(vertices, dtype=np.float32)
    
    def initializeGL(self):
        """初始化OpenGL"""
        # 设置清除颜色
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # 启用深度测试
        glEnable(GL_DEPTH_TEST)
        
        # 启用背面剔除
        glEnable(GL_CULL_FACE)
    
    def resizeGL(self, width, height):
        """调整OpenGL视口大小
        
        Args:
            width (int): 宽度
            height (int): 高度
        """
        glViewport(0, 0, width, height)
    
    def paintGL(self):
        """绘制OpenGL场景"""
        # 清除颜色缓冲区和深度缓冲区
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 设置投影矩阵
        aspect = self.width() / self.height()
        projection = QMatrix4x4()
        projection.perspective(45.0, aspect, 0.1, 100.0)
        
        # 设置视图矩阵
        view = QMatrix4x4()
        view.lookAt(
            self.camera_pos,
            self.camera_pos + self.camera_front,
            self.camera_up
        )
        
        # 绘制网格
        self.draw_grid(view, projection)
        
        # 绘制立方体
        for cube in self.cubes:
            position = cube["position"]
            color = cube["color"]
            self.draw_cube(position, color, view, projection)
    
    def draw_grid(self, view, projection):
        """绘制网格
        
        Args:
            view (QMatrix4x4): 视图矩阵
            projection (QMatrix4x4): 投影矩阵
        """
        # 设置模型矩阵
        model = QMatrix4x4()
        
        # 设置MVP矩阵
        mvp = projection * view * model
        
        # 设置线宽
        glLineWidth(1.0)
        
        # 设置颜色
        glColor3f(*self.ground_color)
        
        # 绘制网格
        glBegin(GL_LINES)
        for i in range(0, len(self.grid_vertices), 3):
            glVertex3f(
                self.grid_vertices[i],
                self.grid_vertices[i + 1],
                self.grid_vertices[i + 2]
            )
        glEnd()
    
    def draw_cube(self, position, color, view, projection):
        """绘制立方体
        
        Args:
            position (tuple): 位置
            color (tuple): 颜色
            view (QMatrix4x4): 视图矩阵
            projection (QMatrix4x4): 投影矩阵
        """
        # 设置模型矩阵
        model = QMatrix4x4()
        model.translate(position[0], position[1], position[2])
        
        # 设置MVP矩阵
        mvp = projection * view * model
        
        # 设置颜色
        glColor3f(*color)
        
        # 绘制立方体
        glBegin(GL_QUADS)
        for i in range(0, len(self.cube_vertices), 3):
            if i % 12 == 0:
                # 每个面的第一个顶点，设置面的颜色
                face_index = i // 12
                face_color = (
                    color[0] * (0.8 + 0.2 * (face_index % 3)),
                    color[1] * (0.8 + 0.2 * ((face_index + 1) % 3)),
                    color[2] * (0.8 + 0.2 * ((face_index + 2) % 3))
                )
                glColor3f(*face_color)
            
            glVertex3f(
                self.cube_vertices[i],
                self.cube_vertices[i + 1],
                self.cube_vertices[i + 2]
            )
        glEnd()
    
    def update_scene(self):
        """更新场景"""
        # 处理键盘输入
        self.process_input()
        
        # 更新视图
        self.update()
    
    def process_input(self):
        """处理键盘输入"""
        # 前后移动
        if self.keys[Qt.Key_W]:
            self.camera_pos += self.camera_front * self.move_speed
        if self.keys[Qt.Key_S]:
            self.camera_pos -= self.camera_front * self.move_speed
        
        # 左右移动
        if self.keys[Qt.Key_A]:
            right = QVector3D.crossProduct(self.camera_front, self.camera_up)
            right.normalize()
            self.camera_pos -= right * self.move_speed
        if self.keys[Qt.Key_D]:
            right = QVector3D.crossProduct(self.camera_front, self.camera_up)
            right.normalize()
            self.camera_pos += right * self.move_speed
        
        # 上下移动
        if self.keys[Qt.Key_Space]:
            self.camera_pos += self.camera_up * self.move_speed
        if self.keys[Qt.Key_Control]:
            self.camera_pos -= self.camera_up * self.move_speed
    
    def keyPressEvent(self, event):
        """键盘按下事件
        
        Args:
            event (QKeyEvent): 键盘事件
        """
        if event.key() in self.keys:
            self.keys[event.key()] = True
    
    def keyReleaseEvent(self, event):
        """键盘释放事件
        
        Args:
            event (QKeyEvent): 键盘事件
        """
        if event.key() in self.keys:
            self.keys[event.key()] = False 