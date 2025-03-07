"""
应用程序类，作为引擎的入口点
"""

import os
import sys
import time
import pygame
from OpenGL.GL import *

from engine.core.scene.scene_manager import SceneManager
from engine.rendering.render_system import RenderSystem
from engine.physics.physics_system import PhysicsSystem
from engine.input.input_system import InputSystem
from engine.scripting.script_system import ScriptSystem
from engine.ui.ui_system import UISystem


class Application:
    """应用程序类，作为引擎的入口点"""
    
    def __init__(self, width=1280, height=720, title="PyCraft Engine", fullscreen=False, debug=False):
        """
        初始化应用程序
        
        Args:
            width (int): 窗口宽度
            height (int): 窗口高度
            title (str): 窗口标题
            fullscreen (bool): 是否全屏
            debug (bool): 是否启用调试模式
        """
        self.width = width
        self.height = height
        self.title = title
        self.fullscreen = fullscreen
        self.debug = debug
        self.running = False
        self.paused = False
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps
        self.delta_time = 0.0
        self.elapsed_time = 0.0
        self.frame_count = 0
        self.fps = 0
        self.window = None
        self.clock = None
        
        # 系统
        self.scene_manager = SceneManager()
        self.render_system = RenderSystem()
        self.physics_system = PhysicsSystem()
        self.input_system = InputSystem()
        self.script_system = ScriptSystem()
        self.ui_system = UISystem()
        
        # 初始化标志
        self.initialized = False
        
        # 自定义回调
        self.on_start_callback = None
        self.on_stop_callback = None
        self.on_update_callback = None
    
    def initialize(self):
        """初始化应用程序"""
        if self.initialized:
            return True
            
        # 初始化Pygame
        pygame.init()
        
        # 设置OpenGL属性
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        pygame.display.gl_set_attribute(pygame.GL_STENCIL_SIZE, 8)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        
        # 创建窗口
        flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        
        try:
            self.window = pygame.display.set_mode((self.width, self.height), flags)
            pygame.display.set_caption(self.title)
        except pygame.error as e:
            print(f"创建窗口失败: {e}")
            # 尝试使用兼容模式创建窗口
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 0)
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 0)
            try:
                self.window = pygame.display.set_mode((self.width, self.height), flags)
                pygame.display.set_caption(f"{self.title} (兼容模式)")
                print("已切换到兼容模式")
            except pygame.error as e2:
                print(f"创建兼容模式窗口失败: {e2}")
                return False
        
        # 创建时钟
        self.clock = pygame.time.Clock()
        
        # 初始化系统
        try:
            # 渲染系统必须在窗口创建后初始化
            self.render_system.initialize(self.width, self.height)
            self.physics_system.initialize(self.debug)
            self.input_system.initialize()
            self.script_system.initialize()
            self.ui_system.initialize(self.width, self.height)
        except Exception as e:
            print(f"初始化系统失败: {e}")
            return False
        
        # 创建默认场景
        self.scene_manager.create_scene("Default Scene")
        
        self.initialized = True
        return True
    
    def start(self):
        """启动应用程序但不进入主循环"""
        if not self.initialized and not self.initialize():
            print("初始化失败，无法启动应用程序")
            return False
            
        # 设置运行标志
        self.running = True
        self.paused = False
        
        # 重置计时器
        self.elapsed_time = 0.0
        self.frame_count = 0
        self.delta_time = 0.0
        
        # 启动脚本系统
        scene = self.scene_manager.get_active_scene()
        if scene:
            self.script_system.start_scripts(scene)
        
        # 调用启动回调
        if self.on_start_callback:
            try:
                self.on_start_callback(self)
            except Exception as e:
                print(f"启动回调异常: {e}")
        
        return True
    
    def stop(self):
        """停止应用程序"""
        # 设置停止标志
        self.running = False
        
        # 停止脚本系统
        self.script_system.stop_scripts()
        
        # 调用停止回调
        if self.on_stop_callback:
            try:
                self.on_stop_callback(self)
            except Exception as e:
                print(f"停止回调异常: {e}")
    
    def run(self):
        """运行应用程序"""
        # 启动应用程序
        if not self.start():
            return
        
        # 主循环
        while self.running:
            # 处理事件
            self._process_events()
            
            # 如果不再运行，退出循环
            if not self.running:
                break
            
            # 计算帧时间
            self.delta_time = self.clock.tick(self.target_fps) / 1000.0
            self.elapsed_time += self.delta_time
            self.frame_count += 1
            
            # 计算FPS
            if self.elapsed_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.elapsed_time = 0.0
                
                # 更新窗口标题
                pygame.display.set_caption(f"{self.title} - FPS: {self.fps}")
            
            # 更新
            if not self.paused:
                self._update()
            
            # 渲染
            self._render()
            
            # 交换缓冲区
            pygame.display.flip()
        
        # 清理
        self._cleanup()
    
    def run_once(self):
        """运行一帧"""
        if not self.initialized and not self.initialize():
            print("初始化失败，无法运行")
            return False
        
        if not self.running:
            return False
            
        # 处理事件
        self._process_events()
        
        # 如果不再运行，返回
        if not self.running:
            return False
        
        # 计算帧时间
        self.delta_time = self.clock.tick(self.target_fps) / 1000.0
        self.elapsed_time += self.delta_time
        self.frame_count += 1
        
        # 计算FPS
        if self.elapsed_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.elapsed_time = 0.0
            
            # 更新窗口标题
            pygame.display.set_caption(f"{self.title} - FPS: {self.fps}")
        
        # 更新
        if not self.paused:
            self._update()
        
        # 渲染
        self._render()
        
        # 交换缓冲区
        pygame.display.flip()
        
        return True
    
    def _process_events(self):
        """处理事件"""
        for event in pygame.event.get():
            # 退出事件
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # 窗口大小改变事件
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = event.size
                self.render_system.resize(self.width, self.height)
                self.ui_system.resize(self.width, self.height)
            
            # 键盘事件
            elif event.type == pygame.KEYDOWN:
                # ESC键退出
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                
                # F11键切换全屏
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                
                # 空格键暂停/恢复
                elif event.key == pygame.K_SPACE and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    self.toggle_pause()
            
            # 处理输入系统事件
            self.input_system.process_event(event)
            
            # 处理UI系统事件
            self.ui_system.process_event(event)
    
    def _update(self):
        """更新"""
        # 更新输入系统
        self.input_system.update()
        
        # 更新脚本系统
        self.script_system.update(self.delta_time)
        
        # 更新物理系统
        self.physics_system.update(self.delta_time)
        
        # 更新场景管理器
        self.scene_manager.update(self.delta_time)
        
        # 更新UI系统
        self.ui_system.update(self.delta_time)
        
        # 调用自定义更新回调
        if self.on_update_callback:
            try:
                self.on_update_callback(self, self.delta_time)
            except Exception as e:
                print(f"更新回调异常: {e}")
    
    def _render(self):
        """渲染"""
        # 清除屏幕
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 获取当前场景
        scene = self.scene_manager.get_active_scene()
        
        # 渲染场景
        if scene:
            self.render_system.render(scene)
        
        # 渲染UI
        self.ui_system.render()
    
    def _cleanup(self):
        """清理"""
        # 关闭系统
        self.render_system.shutdown()
        self.physics_system.shutdown()
        self.input_system.shutdown()
        self.script_system.shutdown()
        self.ui_system.shutdown()
        
        # 清空场景管理器
        self.scene_manager.clear()
        
        # 关闭Pygame
        pygame.quit()
        
        # 重置状态
        self.initialized = False
    
    def toggle_fullscreen(self):
        """切换全屏"""
        self.fullscreen = not self.fullscreen
        
        # 保存当前分辨率
        current_width, current_height = self.width, self.height
        
        # 重新创建窗口
        flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
        
        self.window = pygame.display.set_mode((current_width, current_height), flags)
        
        # 调整系统
        self.render_system.resize(current_width, current_height)
        self.ui_system.resize(current_width, current_height)
    
    def toggle_pause(self):
        """切换暂停/恢复状态"""
        self.paused = not self.paused
        
        # 更新窗口标题
        if self.paused:
            pygame.display.set_caption(f"{self.title} - 已暂停")
        else:
            pygame.display.set_caption(f"{self.title} - FPS: {self.fps}")
    
    def load_scene(self, path):
        """
        加载场景
        
        Args:
            path (str): 场景文件路径
            
        Returns:
            bool: 是否成功加载
        """
        scene = self.scene_manager.load_scene(path)
        
        if scene:
            # 设置为当前场景
            self.scene_manager.set_active_scene(scene.id)
            
            # 如果应用程序正在运行，启动脚本
            if self.running:
                self.script_system.start_scripts(scene)
            
            return True
        
        return False
    
    def save_scene(self, path=None):
        """
        保存当前场景
        
        Args:
            path (str): 保存路径，如果为None则使用当前路径
            
        Returns:
            bool: 是否成功保存
        """
        scene = self.scene_manager.get_active_scene()
        
        if scene:
            return self.scene_manager.save_scene(scene.id, path)
        
        return False
    
    def create_entity(self, name="Entity"):
        """
        创建实体
        
        Args:
            name (str): 实体名称
            
        Returns:
            Entity: 创建的实体，如果没有当前场景则返回None
        """
        scene = self.scene_manager.get_active_scene()
        
        if scene:
            return scene.create_entity(name)
        
        return None
    
    def get_entity(self, entity_id):
        """
        获取实体
        
        Args:
            entity_id (str): 实体ID
            
        Returns:
            Entity: 实体，如果不存在则返回None
        """
        scene = self.scene_manager.get_active_scene()
        
        if scene:
            return scene.get_entity(entity_id)
        
        return None
    
    def get_entity_by_name(self, name):
        """
        通过名称获取实体
        
        Args:
            name (str): 实体名称
            
        Returns:
            Entity: 实体，如果不存在则返回None
        """
        scene = self.scene_manager.get_active_scene()
        
        if scene:
            return scene.get_entity_by_name(name)
        
        return None
    
    def get_entities_with_component(self, component_type):
        """
        获取具有指定组件的实体
        
        Args:
            component_type: 组件类型
            
        Returns:
            list: 实体列表
        """
        scene = self.scene_manager.get_active_scene()
        
        if scene:
            return scene.get_entities_with_component(component_type)
        
        return []
    
    def get_entities_with_tag(self, tag):
        """
        获取具有指定标签的实体
        
        Args:
            tag (str): 标签
            
        Returns:
            list: 实体列表
        """
        scene = self.scene_manager.get_active_scene()
        
        if scene:
            return scene.get_entities_with_tag(tag)
        
        return []
    
    def set_camera(self, camera):
        """
        设置相机
        
        Args:
            camera: 相机实体或组件
        """
        self.render_system.set_camera(camera)
    
    def add_light(self, light):
        """
        添加光源
        
        Args:
            light: 光源实体或组件
        """
        self.render_system.add_light(light)
    
    def set_gravity(self, gravity):
        """
        设置重力
        
        Args:
            gravity (tuple): 重力向量，(x, y, z)
        """
        self.physics_system.set_gravity(gravity)
    
    def create_script(self, script_name, entity):
        """
        创建脚本实例
        
        Args:
            script_name (str): 脚本名称
            entity: 所属实体
            
        Returns:
            Script: 脚本实例，如果创建失败则返回None
        """
        return self.script_system.create_script(script_name, entity)
    
    def create_ui_canvas(self, name):
        """
        创建UI画布
        
        Args:
            name (str): 画布名称
            
        Returns:
            UICanvas: 创建的画布
        """
        return self.ui_system.create_canvas(name)
    
    def get_ui_canvas(self, name):
        """
        获取UI画布
        
        Args:
            name (str): 画布名称
            
        Returns:
            UICanvas: 画布，如果不存在则返回None
        """
        return self.ui_system.get_canvas(name)
    
    def set_active_ui_canvas(self, name):
        """
        设置当前活动的UI画布
        
        Args:
            name (str): 画布名称
            
        Returns:
            bool: 是否成功设置
        """
        return self.ui_system.set_active_canvas(name)
    
    def create_ui_widget(self, widget_type, *args, **kwargs):
        """
        创建UI控件
        
        Args:
            widget_type: 控件类型
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            widget: 创建的控件
        """
        return self.ui_system.create_widget(widget_type, *args, **kwargs)
    
    def set_on_start_callback(self, callback):
        """
        设置启动回调
        
        Args:
            callback: 回调函数，接受应用程序实例作为参数
        """
        self.on_start_callback = callback
    
    def set_on_stop_callback(self, callback):
        """
        设置停止回调
        
        Args:
            callback: 回调函数，接受应用程序实例作为参数
        """
        self.on_stop_callback = callback
    
    def set_on_update_callback(self, callback):
        """
        设置更新回调
        
        Args:
            callback: 回调函数，接受应用程序实例和delta_time作为参数
        """
        self.on_update_callback = callback
    
    def __str__(self):
        """字符串表示"""
        return f"Application(title={self.title}, width={self.width}, height={self.height}, fps={self.fps}, running={self.running}, paused={self.paused})"