#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
场景面板类
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QOpenGLWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QKeyEvent, QMatrix4x4, QVector3D, QFont, QPainter, QColor, QCursor
import OpenGL
OpenGL.ERROR_CHECKING = True  # 启用错误检查
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math


class ScenePanel(QWidget):
    """场景面板类"""
    
    def __init__(self):
        """初始化场景面板"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距，让OpenGL视图填充整个区域
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
        
        # 在创建OpenGL上下文之前不要使用任何OpenGL命令
        self.gl_initialized = False
        
        # 设置焦点策略
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 相机位置和方向
        self.camera_pos = QVector3D(0.0, 1.5, 5.0)
        self.camera_front = QVector3D(0.0, 0.0, -1.0)
        self.camera_up = QVector3D(0.0, 1.0, 0.0)
        
        # 相机旋转角度
        self.yaw = -90.0  # 水平旋转角度
        self.pitch = 0.0  # 垂直旋转角度
        
        # 鼠标上一次位置
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_pressed = False
        
        # 移动速度
        self.move_speed = 0.1
        
        # 坐标轴颜色
        self.x_axis_color = (0.9, 0.2, 0.2)  # 红色
        self.y_axis_color = (0.2, 0.9, 0.2)  # 绿色
        self.z_axis_color = (0.2, 0.2, 0.9)  # 蓝色
        
        # 按键状态
        self.keys = {
            Qt.Key_W: False,
            Qt.Key_A: False,
            Qt.Key_S: False,
            Qt.Key_D: False,
            Qt.Key_Space: False,
            Qt.Key_Control: False,
            Qt.Key_Shift: False  # 加速键
        }
        
        # 创建定时器，用于更新场景
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(16)  # 约60FPS
        
        # 网格数据
        self.grid_vertices = self.create_grid(20, 1.0)
        self.cube_vertices = self.create_cube()
        
        # 地面颜色
        self.ground_color = (0.3, 0.3, 0.35)  # 稍微带蓝色的灰色
        
        # 坐标轴长度
        self.axis_length = 1.0
        
        # 天空盒颜色 - 渐变
        self.sky_color_top = (0.2, 0.4, 0.8)  # 顶部蓝色
        self.sky_color_bottom = (0.5, 0.6, 0.8)  # 底部浅蓝色
        
        # 立方体位置
        self.cubes = [
            {"position": (0.0, 0.5, 0.0), "color": (0.9, 0.3, 0.3), "name": "红色立方体"},
            {"position": (3.0, 0.5, 2.0), "color": (0.3, 0.9, 0.3), "name": "绿色立方体"},
            {"position": (-2.0, 0.5, -3.0), "color": (0.3, 0.3, 0.9), "name": "蓝色立方体"},
            {"position": (4.0, 0.5, -2.0), "color": (0.9, 0.9, 0.3), "name": "黄色立方体"},
            {"position": (-3.0, 0.5, 4.0), "color": (0.3, 0.9, 0.9), "name": "青色立方体"}
        ]
        
        # 选中的立方体索引
        self.selected_cube = -1
        
        # 显示统计信息
        self.show_stats = True
        self.fps = 0
        self.frame_count = 0
        self.fps_timer = QTimer(self)
        self.fps_timer.timeout.connect(self.update_fps)
        self.fps_timer.start(1000)  # 每秒更新一次FPS
        
        # 辅助选项
        self.show_grid = True
        self.show_axes = True
        
        # 世界视窗模式
        self.world_view_mode = False
        self.world_view_height = 1.7  # 默认人眼高度
        self.player_radius = 0.3  # 玩家碰撞半径
        self.gravity_enabled = True  # 是否启用重力
        self.player_velocity = QVector3D(0.0, 0.0, 0.0)  # 玩家速度向量
        self.gravity = -0.01  # 重力加速度
        self.jump_force = 0.2  # 跳跃力度
        self.is_jumping = False  # 是否正在跳跃
        self.is_grounded = False  # 是否在地面上
        
        # 保存编辑器模式下的相机状态
        self.editor_camera_state = {
            'position': None,
            'front': None,
            'up': None,
            'yaw': None,
            'pitch': None
        }
    
    def update_fps(self):
        """更新FPS计数器"""
        self.fps = self.frame_count
        self.frame_count = 0
    
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
        glClearColor(0.2, 0.3, 0.4, 1.0)
        
        # 启用深度测试
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # 启用背面剔除
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
        # 启用混合
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 启用点光滑
        glEnable(GL_POINT_SMOOTH)
        glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
        
        # 启用线光滑
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        # 启用多重采样
        glEnable(GL_MULTISAMPLE)
        
        # 标记OpenGL已初始化
        self.gl_initialized = True
    
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
        
        # 绘制天空盒
        self.draw_skybox()
        
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
        
        # 保存当前的模型视图矩阵和投影矩阵，用于对象选择
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(projection.data())
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMultMatrixf(view.data())
        
        # 绘制网格
        if self.show_grid:
            self.draw_grid(view, projection)
        
        # 绘制坐标轴
        if self.show_axes:
            self.draw_axes(view, projection)
        
        # 绘制立方体
        for i, cube in enumerate(self.cubes):
            position = cube["position"]
            color = cube["color"]
            is_selected = (i == self.selected_cube)
            self.draw_cube(position, color, view, projection, is_selected)
        
        # 在世界视窗模式下绘制准星
        if self.world_view_mode:
            self.draw_crosshair()
        
        # 绘制统计信息
        if self.show_stats:
            self.frame_count += 1
            self.draw_stats()
    
    def draw_skybox(self):
        """绘制天空盒（渐变背景）"""
        # 禁用深度测试以确保天空盒始终在背景
        glDisable(GL_DEPTH_TEST)      
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        try:
            # 绘制填充整个屏幕的渐变四边形
            glBegin(GL_QUADS)
            try:
                # 上部颜色
                glColor3f(*self.sky_color_top)
                glVertex2f(-1.0, 1.0)  # 左上
                glVertex2f(1.0, 1.0)   # 右上
                # 下部颜色
                glColor3f(*self.sky_color_bottom)
                glVertex2f(1.0, -1.0)  # 右下
                glVertex2f(-1.0, -1.0) # 左下
            finally:
                glEnd()
        except OpenGL.error.GLError as e:
            print(f"绘制天空盒时出错: {e}")
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        # 重新启用深度测试
        glEnable(GL_DEPTH_TEST)
    
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
        glLineWidth(0.8)
        
        # 设置细网格颜色（稍微透明）
        glColor4f(self.ground_color[0], self.ground_color[1], self.ground_color[2], 0.3)
        
        try:
            # 绘制网格
            glBegin(GL_LINES)
            try:
                for i in range(0, len(self.grid_vertices), 3):
                    glVertex3f(
                        self.grid_vertices[i],
                        self.grid_vertices[i + 1],
                        self.grid_vertices[i + 2]
                    )
            finally:
                glEnd()
            
            # 绘制主网格线（坐标轴上的线更粗更亮）
            glLineWidth(1.5)
            glBegin(GL_LINES)
            try:
                # 沿X轴的线
                glColor4f(self.x_axis_color[0], self.x_axis_color[1], self.x_axis_color[2], 0.6)
                glVertex3f(-10.0, 0.0, 0.0)
                glVertex3f(10.0, 0.0, 0.0)
                
                # 沿Z轴的线
                glColor4f(self.z_axis_color[0], self.z_axis_color[1], self.z_axis_color[2], 0.6)
                glVertex3f(0.0, 0.0, -10.0)
                glVertex3f(0.0, 0.0, 10.0)
            finally:
                glEnd()
        except OpenGL.error.GLError as e:
            print(f"绘制网格时出错: {e}")
    
    def draw_axes(self, view, projection):
        """绘制坐标轴
        
        Args:
            view (QMatrix4x4): 视图矩阵
            projection (QMatrix4x4): 投影矩阵
        """
        # 设置线宽
        glLineWidth(2.0)
        
        # 设置模型矩阵
        model = QMatrix4x4()
        model.translate(0.0, 0.0, 0.0)
        
        # 使用屏幕空间固定大小
        screen_model = QMatrix4x4()
        screen_model.translate(-0.8, -0.8, -2.0)  # 左下角稍微内移
        screen_model.scale(0.1, 0.1, 0.1)  # 缩小绘制尺寸
        
        screen_mvp = projection * screen_model
        
        try:
            # 绘制坐标轴
            glBegin(GL_LINES)
            try:
                # X轴 (红色)
                glColor3f(*self.x_axis_color)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex3f(self.axis_length, 0.0, 0.0)
                
                # Y轴 (绿色)
                glColor3f(*self.y_axis_color)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex3f(0.0, self.axis_length, 0.0)
                
                # Z轴 (蓝色)
                glColor3f(*self.z_axis_color)
                glVertex3f(0.0, 0.0, 0.0)
                glVertex3f(0.0, 0.0, self.axis_length)
            finally:
                glEnd()
        except OpenGL.error.GLError as e:
            print(f"绘制坐标轴时出错: {e}")
        
        # 绘制坐标轴文字标签
        self.renderText(self.axis_length+0.05, 0.0, 0.0, "X", self.x_axis_color)
        self.renderText(0.0, self.axis_length+0.05, 0.0, "Y", self.y_axis_color)
        self.renderText(0.0, 0.0, self.axis_length+0.05, "Z", self.z_axis_color)
    
    def draw_cube(self, position, color, view, projection, selected=False):
        """绘制立方体
        
        Args:
            position (tuple): 位置
            color (tuple): 颜色
            view (QMatrix4x4): 视图矩阵
            projection (QMatrix4x4): 投影矩阵
            selected (bool): 是否选中
        """
        # 设置模型矩阵
        model = QMatrix4x4()
        model.translate(position[0], position[1], position[2])
        
        # 如果选中，增加轮廓效果
        if selected:
            # 稍微放大立方体以创建轮廓
            outline_model = QMatrix4x4()
            outline_model.translate(position[0], position[1], position[2])
            outline_model.scale(1.05, 1.05, 1.05)  # 放大5%
            
            # 绘制黑色轮廓
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(2.0)
            glColor3f(1.0, 1.0, 0.0)  # 黄色轮廓
            
            self.draw_cube_faces(outline_model)
            
            # 恢复填充模式
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
        # 设置MVP矩阵
        mvp = projection * view * model
        
        # 设置颜色
        glColor3f(*color)
        
        # 绘制立方体面
        self.draw_cube_faces(model)
    
    def draw_cube_faces(self, model):
        """绘制立方体面
        
        Args:
            model (QMatrix4x4): 模型矩阵
        """
        try:
            glBegin(GL_QUADS)
            try:
                for i in range(0, len(self.cube_vertices), 3):
                    if i % 12 == 0:
                        # 每个面的第一个顶点，设置面的颜色
                        face_index = i // 12
                        # 根据面的法线方向计算光照效果
                        lighting = 0.7 + 0.3 * (face_index % 3) / 2.0
                        
                        # 获取当前颜色
                        current_color = glGetFloatv(GL_CURRENT_COLOR)
                        # 调整颜色以反映光照
                        adjusted_color = (
                            current_color[0] * lighting,
                            current_color[1] * lighting,
                            current_color[2] * lighting
                        )
                        glColor3f(*adjusted_color)
                    
                    # 获取顶点位置
                    vertex = QVector3D(
                        self.cube_vertices[i],
                        self.cube_vertices[i + 1],
                        self.cube_vertices[i + 2]
                    )
                    # 应用模型变换
                    transformed = model.map(vertex)
                    # 设置顶点
                    glVertex3f(transformed.x(), transformed.y(), transformed.z())
            finally:
                glEnd()  # 确保在finally块中调用glEnd
        except OpenGL.error.GLError as e:
            print(f"OpenGL错误: {e}")
            # 如果发生错误，尝试结束当前的图元绘制
            try:
                glEnd()
            except:
                pass
    
    def renderText(self, x, y, z, text, color=(1.0, 1.0, 1.0)):
        """使用QPainter在3D空间渲染文本
        
        Args:
            x (float): X坐标
            y (float): Y坐标
            z (float): Z坐标
            text (str): 要渲染的文本
            color (tuple): 文本颜色
        """
        # 将3D点转换为屏幕坐标
        viewport = glGetIntegerv(GL_VIEWPORT)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        
        win_x, win_y, win_z = gluProject(x, y, z, modelview, projection, viewport)
        win_y = self.height() - win_y  # 翻转Y坐标
        
        # 创建QPainter在OpenGL上绘制
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # 设置字体
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # 设置颜色
        painter.setPen(QColor(int(color[0]*255), int(color[1]*255), int(color[2]*255)))
        
        # 绘制文本
        painter.drawText(int(win_x), int(win_y), text)
        
        # 结束绘制
        painter.end()
    
    def draw_stats(self):
        """绘制统计信息"""
        # 创建QPainter在OpenGL上绘制
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # 设置字体
        font = QFont("Arial", 9)
        painter.setFont(font)
        
        # 设置颜色
        painter.setPen(QColor(255, 255, 255))
        
        # 绘制FPS
        painter.drawText(10, 20, f"FPS: {self.fps}")
        
        # 绘制相机位置
        painter.drawText(10, 40, f"位置: ({self.camera_pos.x():.1f}, {self.camera_pos.y():.1f}, {self.camera_pos.z():.1f})")
        
        # 绘制选中的物体信息
        if not self.world_view_mode and self.selected_cube >= 0 and self.selected_cube < len(self.cubes):
            cube = self.cubes[self.selected_cube]
            painter.drawText(10, 60, f"选中: {cube['name']}")
            pos = cube["position"]
            painter.drawText(10, 80, f"物体位置: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
        
        # 在世界视窗模式下显示提示
        if self.world_view_mode:
            mode_text = "世界视窗模式 - 按ESC退出"
            if self.gravity_enabled:
                mode_text += " | 空格跳跃 | 按V切换重力"
            else:
                mode_text += " | 空格上升，Ctrl下降 | 按V切换重力"
            painter.drawText(10, self.height() - 20, mode_text)
        
        # 结束绘制
        painter.end()
    
    def update_scene(self):
        """更新场景"""
        # 处理键盘输入
        self.process_input()
        
        # 更新视图
        self.update()
    
    def process_input(self):
        """处理键盘输入"""
        # 确定移动速度 (按住Shift加速)
        speed = self.move_speed * (3.0 if self.keys[Qt.Key_Shift] else 1.0)
        
        # 在世界视窗模式下，移动方式不同
        if self.world_view_mode:
            # 计算前进方向（忽略Y轴，保持在水平面上移动）
            forward = QVector3D(self.camera_front.x(), 0.0, self.camera_front.z())
            forward.normalize()
            
            # 计算右方向
            right = QVector3D.crossProduct(self.camera_front, self.camera_up)
            right.normalize()
            
            # 计算新位置
            new_pos = QVector3D(self.camera_pos)
            
            # 前后移动
            if self.keys[Qt.Key_W]:
                new_pos += forward * speed
            if self.keys[Qt.Key_S]:
                new_pos -= forward * speed
            
            # 左右移动
            if self.keys[Qt.Key_A]:
                new_pos -= right * speed
            if self.keys[Qt.Key_D]:
                new_pos += right * speed
            
            # 跳跃
            if self.keys[Qt.Key_Space] and self.is_grounded:
                self.player_velocity.setY(self.jump_force)
                self.is_jumping = True
                self.is_grounded = False
            
            # 应用重力
            if self.gravity_enabled:
                self.player_velocity.setY(self.player_velocity.y() + self.gravity)
                new_pos.setY(new_pos.y() + self.player_velocity.y())
                
                # 检测地面碰撞
                if new_pos.y() < self.world_view_height:
                    new_pos.setY(self.world_view_height)
                    self.player_velocity.setY(0)
                    self.is_grounded = True
                    self.is_jumping = False
            else:
                # 不启用重力时的上下移动
                if self.keys[Qt.Key_Space]:
                    new_pos += QVector3D(0.0, 1.0, 0.0) * speed
                if self.keys[Qt.Key_Control]:
                    new_pos -= QVector3D(0.0, 1.0, 0.0) * speed
            
            # 检测与立方体的碰撞
            if self.check_collision(new_pos):
                # 如果发生碰撞，不更新位置
                pass
            else:
                # 如果没有碰撞，更新位置
                self.camera_pos = new_pos
        else:
            # 编辑器模式下的移动
            # 前后移动
            if self.keys[Qt.Key_W]:
                self.camera_pos += self.camera_front * speed
            if self.keys[Qt.Key_S]:
                self.camera_pos -= self.camera_front * speed
            
            # 左右移动
            if self.keys[Qt.Key_A]:
                right = QVector3D.crossProduct(self.camera_front, self.camera_up)
                right.normalize()
                self.camera_pos -= right * speed
            if self.keys[Qt.Key_D]:
                right = QVector3D.crossProduct(self.camera_front, self.camera_up)
                right.normalize()
                self.camera_pos += right * speed
            
            # 上下移动
            if self.keys[Qt.Key_Space]:
                self.camera_pos += self.camera_up * speed
            if self.keys[Qt.Key_Control]:
                self.camera_pos -= self.camera_up * speed
    
    def check_collision(self, position):
        """检查位置是否与立方体碰撞
        
        Args:
            position (QVector3D): 要检查的位置
            
        Returns:
            bool: 是否发生碰撞
        """
        # 检查与每个立方体的碰撞
        for cube in self.cubes:
            cube_pos = QVector3D(cube["position"][0], cube["position"][1], cube["position"][2])
            # 简单的球体-立方体碰撞检测
            # 计算立方体的边界框
            min_x = cube_pos.x() - 0.5
            max_x = cube_pos.x() + 0.5
            min_y = cube_pos.y() - 0.5
            max_y = cube_pos.y() + 0.5
            min_z = cube_pos.z() - 0.5
            max_z = cube_pos.z() + 0.5
            
            # 计算球体中心到立方体最近点的距离
            closest_x = max(min_x, min(position.x(), max_x))
            closest_y = max(min_y, min(position.y(), max_y))
            closest_z = max(min_z, min(position.z(), max_z))
            
            # 计算距离
            distance = QVector3D(closest_x - position.x(), 
                                closest_y - position.y(), 
                                closest_z - position.z()).length()
            
            # 如果距离小于球体半径，则发生碰撞
            if distance < self.player_radius:
                return True
        
        return False
    
    def mousePressEvent(self, event):
        """鼠标按下事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = True
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()
            self.setFocus()  # 确保OpenGL窗口获取焦点
        
        # 右键选择物体或进入世界视窗模式
        elif event.button() == Qt.RightButton:
            if not self.world_view_mode:
                # 尝试选择物体
                if self.try_select_object(event.x(), event.y()):
                    # 如果选中了物体，不进入世界视窗模式
                    pass
                else:
                    # 如果没有选中物体，进入世界视窗模式
                    self.enter_world_view_mode()
            else:
                # 在世界视窗模式下，右键可以用于交互
                self.try_interact_with_object()
    
    def try_select_object(self, x, y):
        """尝试选择物体
        
        Args:
            x (int): 鼠标X坐标
            y (int): 鼠标Y坐标
            
        Returns:
            bool: 是否选中了物体
        """
        if not self.gl_initialized:
            return False
            
        # 获取视口、投影矩阵和模型视图矩阵
        viewport = glGetIntegerv(GL_VIEWPORT)
        projection_matrix = glGetDoublev(GL_PROJECTION_MATRIX)
        modelview_matrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        
        # 将屏幕坐标转换为世界坐标中的射线
        y = self.height() - y  # 翻转Y坐标
        near_point = gluUnProject(x, y, 0.0, modelview_matrix, projection_matrix, viewport)
        far_point = gluUnProject(x, y, 1.0, modelview_matrix, projection_matrix, viewport)
        
        # 创建射线
        ray_origin = QVector3D(near_point[0], near_point[1], near_point[2])
        ray_direction = QVector3D(
            far_point[0] - near_point[0],
            far_point[1] - near_point[1],
            far_point[2] - near_point[2]
        )
        ray_direction.normalize()
        
        # 检查射线与每个立方体的交点
        closest_cube = -1
        closest_distance = float('inf')
        
        for i, cube in enumerate(self.cubes):
            position = cube["position"]
            cube_pos = QVector3D(position[0], position[1], position[2])
            
            # 简化的射线-立方体相交测试
            # 立方体的边界框
            min_x = cube_pos.x() - 0.5
            max_x = cube_pos.x() + 0.5
            min_y = cube_pos.y() - 0.5
            max_y = cube_pos.y() + 0.5
            min_z = cube_pos.z() - 0.5
            max_z = cube_pos.z() + 0.5
            
            # 计算射线与立方体的交点
            t_min = float('-inf')
            t_max = float('inf')
            
            # 检查X轴
            if abs(ray_direction.x()) < 1e-6:
                if ray_origin.x() < min_x or ray_origin.x() > max_x:
                    continue
            else:
                t1 = (min_x - ray_origin.x()) / ray_direction.x()
                t2 = (max_x - ray_origin.x()) / ray_direction.x()
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    continue
            
            # 检查Y轴
            if abs(ray_direction.y()) < 1e-6:
                if ray_origin.y() < min_y or ray_origin.y() > max_y:
                    continue
            else:
                t1 = (min_y - ray_origin.y()) / ray_direction.y()
                t2 = (max_y - ray_origin.y()) / ray_direction.y()
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    continue
            
            # 检查Z轴
            if abs(ray_direction.z()) < 1e-6:
                if ray_origin.z() < min_z or ray_origin.z() > max_z:
                    continue
            else:
                t1 = (min_z - ray_origin.z()) / ray_direction.z()
                t2 = (max_z - ray_origin.z()) / ray_direction.z()
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    continue
            
            # 如果到这里，射线与立方体相交
            if t_min > 0 and t_min < closest_distance:
                closest_distance = t_min
                closest_cube = i
        
        # 如果找到最近的立方体，选中它
        if closest_cube >= 0:
            self.selected_cube = closest_cube
            cube = self.cubes[self.selected_cube]
            print(f"已选中: {cube['name']}")
            return True
        
        return False
    
    def try_interact_with_object(self):
        """在世界视窗模式下尝试与物体交互"""
        # 计算前方射线
        ray_origin = QVector3D(self.camera_pos)
        ray_direction = QVector3D(self.camera_front)
        ray_direction.normalize()
        
        # 检查射线与每个立方体的交点
        closest_cube = -1
        closest_distance = float('inf')
        max_interaction_distance = 2.0  # 最大交互距离
        
        for i, cube in enumerate(self.cubes):
            position = cube["position"]
            cube_pos = QVector3D(position[0], position[1], position[2])
            
            # 简化的射线-立方体相交测试
            # 立方体的边界框
            min_x = cube_pos.x() - 0.5
            max_x = cube_pos.x() + 0.5
            min_y = cube_pos.y() - 0.5
            max_y = cube_pos.y() + 0.5
            min_z = cube_pos.z() - 0.5
            max_z = cube_pos.z() + 0.5
            
            # 计算射线与立方体的交点
            t_min = float('-inf')
            t_max = float('inf')
            
            # 检查X轴
            if abs(ray_direction.x()) < 1e-6:
                if ray_origin.x() < min_x or ray_origin.x() > max_x:
                    continue
            else:
                t1 = (min_x - ray_origin.x()) / ray_direction.x()
                t2 = (max_x - ray_origin.x()) / ray_direction.x()
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    continue
            
            # 检查Y轴
            if abs(ray_direction.y()) < 1e-6:
                if ray_origin.y() < min_y or ray_origin.y() > max_y:
                    continue
            else:
                t1 = (min_y - ray_origin.y()) / ray_direction.y()
                t2 = (max_y - ray_origin.y()) / ray_direction.y()
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    continue
            
            # 检查Z轴
            if abs(ray_direction.z()) < 1e-6:
                if ray_origin.z() < min_z or ray_origin.z() > max_z:
                    continue
            else:
                t1 = (min_z - ray_origin.z()) / ray_direction.z()
                t2 = (max_z - ray_origin.z()) / ray_direction.z()
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    continue
            
            # 如果到这里，射线与立方体相交
            if t_min > 0 and t_min < closest_distance and t_min < max_interaction_distance:
                closest_distance = t_min
                closest_cube = i
        
        # 如果找到最近的立方体，与它交互
        if closest_cube >= 0:
            cube = self.cubes[closest_cube]
            print(f"与 {cube['name']} 交互")
            # 这里可以添加更多交互逻辑
            return True
        
        return False
    
    def enter_world_view_mode(self):
        """进入世界视窗模式"""
        # 保存当前编辑器相机状态
        self.editor_camera_state = {
            'position': QVector3D(self.camera_pos),
            'front': QVector3D(self.camera_front),
            'up': QVector3D(self.camera_up),
            'yaw': self.yaw,
            'pitch': self.pitch
        }
        
        # 设置世界视窗模式标志
        self.world_view_mode = True
        
        # 设置初始视角（人眼高度）
        self.camera_pos = QVector3D(0.0, self.world_view_height, 0.0)
        
        # 重置玩家状态
        self.player_velocity = QVector3D(0.0, 0.0, 0.0)
        self.is_jumping = False
        self.is_grounded = True
        
        # 将视角设置为水平
        self.pitch = 0.0
        self.update_camera_vectors()
        
        # 捕获鼠标并隐藏鼠标指针
        self.setMouseTracking(True)
        self.setCursor(Qt.BlankCursor)
        
        # 将鼠标移动到屏幕中心
        center = self.mapToGlobal(QPoint(self.width() // 2, self.height() // 2))
        QCursor.setPos(center)
        
        print("已进入世界视窗模式，使用WASD移动，空格跳跃，鼠标控制视角，按ESC退出")
    
    def exit_world_view_mode(self):
        """退出世界视窗模式"""
        if not self.world_view_mode:
            return
            
        # 恢复编辑器相机状态
        self.camera_pos = self.editor_camera_state['position']
        self.camera_front = self.editor_camera_state['front']
        self.camera_up = self.editor_camera_state['up']
        self.yaw = self.editor_camera_state['yaw']
        self.pitch = self.editor_camera_state['pitch']
        
        # 重置世界视窗模式标志
        self.world_view_mode = False
        
        # 释放鼠标控制
        self.setMouseTracking(False)
        self.setCursor(Qt.ArrowCursor)
        
        print("已退出世界视窗模式")
    
    def update_camera_vectors(self):
        """更新相机向量"""
        # 计算新的相机前方向向量
        front = QVector3D()
        front.setX(math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)))
        front.setY(math.sin(math.radians(self.pitch)))
        front.setZ(math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)))
        front.normalize()
        self.camera_front = front
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件
        
        Args:
            event: 鼠标事件
        """
        if event.button() == Qt.LeftButton:
            self.mouse_pressed = False
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件
        
        Args:
            event: 鼠标事件
        """
        if self.world_view_mode:
            # 在世界视窗模式下，鼠标移动总是控制视角
            # 获取屏幕中心点
            center_x = self.width() // 2
            center_y = self.height() // 2
            
            # 计算鼠标移动的偏移量
            x_offset = event.x() - center_x
            y_offset = center_y - event.y()  # 反转Y坐标
            
            # 敏感度
            sensitivity = 0.1
            x_offset *= sensitivity
            y_offset *= sensitivity
            
            # 更新相机方向
            self.yaw += x_offset
            self.pitch += y_offset
            
            # 限制俯仰角度，防止翻转
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0
            
            # 计算新的相机前方向向量
            front = QVector3D()
            front.setX(math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)))
            front.setY(math.sin(math.radians(self.pitch)))
            front.setZ(math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)))
            front.normalize()
            self.camera_front = front
            
            # 将鼠标重置到屏幕中心
            cursor = QCursor()
            cursor.setPos(self.mapToGlobal(QPoint(center_x, center_y)))
            
        elif self.mouse_pressed:
            # 编辑器模式下的鼠标移动处理
            # 计算鼠标移动的偏移量
            x_offset = event.x() - self.last_mouse_x
            y_offset = self.last_mouse_y - event.y()  # 反转Y坐标
            
            # 更新最后的鼠标位置
            self.last_mouse_x = event.x()
            self.last_mouse_y = event.y()
            
            # 敏感度
            sensitivity = 0.2
            x_offset *= sensitivity
            y_offset *= sensitivity
            
            # 更新相机方向
            self.yaw += x_offset
            self.pitch += y_offset
            
            # 限制俯仰角度，防止翻转
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0
            
            # 计算新的相机前方向向量
            front = QVector3D()
            front.setX(math.cos(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)))
            front.setY(math.sin(math.radians(self.pitch)))
            front.setZ(math.sin(math.radians(self.yaw)) * math.cos(math.radians(self.pitch)))
            front.normalize()
            self.camera_front = front
    
    def wheelEvent(self, event):
        """鼠标滚轮事件
        
        Args:
            event: 滚轮事件
        """
        # 调整相机移动速度
        delta = event.angleDelta().y()
        if delta > 0:
            self.move_speed *= 1.1  # 增加速度
        else:
            self.move_speed *= 0.9  # 减少速度
            
        # 限制速度范围
        self.move_speed = max(0.01, min(0.5, self.move_speed))
    
    def keyPressEvent(self, event):
        """键盘按下事件
        
        Args:
            event (QKeyEvent): 键盘事件
        """
        if event.key() in self.keys:
            self.keys[event.key()] = True
        
        # ESC键退出世界视窗模式
        elif event.key() == Qt.Key_Escape and self.world_view_mode:
            self.exit_world_view_mode()
        
        # 切换网格显示
        elif event.key() == Qt.Key_G:
            self.show_grid = not self.show_grid
        
        # 切换坐标轴显示
        elif event.key() == Qt.Key_X:
            self.show_axes = not self.show_axes
        
        # 切换统计信息显示
        elif event.key() == Qt.Key_F:
            self.show_stats = not self.show_stats
            
        # 切换重力
        elif event.key() == Qt.Key_V and self.world_view_mode:
            self.gravity_enabled = not self.gravity_enabled
            if self.gravity_enabled:
                print("重力已启用")
            else:
                print("重力已禁用")
    
    def keyReleaseEvent(self, event):
        """键盘释放事件
        
        Args:
            event (QKeyEvent): 键盘事件
        """
        if event.key() in self.keys:
            self.keys[event.key()] = False
    
    def draw_crosshair(self):
        """绘制准星"""
        # 禁用深度测试以确保准星始终可见
        glDisable(GL_DEPTH_TEST)
        
        # 设置正交投影
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width(), 0, self.height(), -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        # 计算屏幕中心
        center_x = self.width() // 2
        center_y = self.height() // 2
        
        # 设置准星颜色和大小
        glColor3f(1.0, 1.0, 1.0)  # 白色
        glLineWidth(1.0)
        
        # 绘制十字准星
        size = 10  # 准星大小
        
        try:
            glBegin(GL_LINES)
            try:
                # 水平线
                glVertex2f(center_x - size, center_y)
                glVertex2f(center_x + size, center_y)
                
                # 垂直线
                glVertex2f(center_x, center_y - size)
                glVertex2f(center_x, center_y + size)
            finally:
                glEnd()
        except OpenGL.error.GLError as e:
            print(f"绘制准星时出错: {e}")
        
        # 恢复矩阵
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        # 重新启用深度测试
        glEnable(GL_DEPTH_TEST)