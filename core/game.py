import pygame
import sys
import time
import numpy as np
from core.entity_manager import EntityManager
from core.components import ComponentType, TransformComponent, RenderComponent, PhysicsComponent, InputComponent, CameraComponent, UIComponent
from core.resource_manager import ResourceManager
from core.scene_manager import SceneManager, MainMenuScene, GameScene, TestScene, UIEditorScene
from systems.render_system import RenderSystem
from systems.input_system import InputSystem
from systems.physics_system import PhysicsSystem
from systems.ui_system import UISystem
from systems.ui_editor_system import UIEditorSystem

class Game:
    """游戏主类，管理游戏状态和主循环"""
    def __init__(self, width=800, height=600, title="PyCraft Engine"):
        # 初始化Pygame
        pygame.init()
        
        # 设置窗口
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption(title)
        
        # 游戏状态
        self.running = True
        self.clock = pygame.time.Clock()
        self.delta_time = 0
        self.last_time = time.time()
        self.fps = 0
        
        # 实体管理器
        self.entity_manager = EntityManager()
        
        # 资源管理器
        self.resource_manager = ResourceManager()
        
        # 初始化系统
        self.input_system = InputSystem(self.entity_manager)
        self.physics_system = PhysicsSystem(self.entity_manager)
        self.render_system = RenderSystem(self.entity_manager, width, height)
        self.ui_system = UISystem(self.entity_manager, width, height)
        self.ui_editor_system = UIEditorSystem(self.entity_manager, self.ui_system, width, height)
        
        # 场景管理器
        self.scene_manager = SceneManager(self)
        
        # 初始化场景
        self.init_scenes()
        
        # 加载默认场景
        self.scene_manager.change_scene("MainMenu")  # 加载主菜单场景

    def init_scenes(self):
        """初始化场景"""
        # 创建主菜单场景
        main_menu = MainMenuScene(self.entity_manager, self.resource_manager, self.ui_system, self)
        self.scene_manager.add_scene(main_menu)
        
        # 创建游戏场景
        game_scene = GameScene(self.entity_manager, self.resource_manager, self.ui_system, self)
        self.scene_manager.add_scene(game_scene)
        
        # 创建测试场景
        test_scene = TestScene(self.entity_manager, self.resource_manager, self.ui_system, self)
        self.scene_manager.add_scene(test_scene)
        
        # 创建UI编辑器场景
        ui_editor_scene = UIEditorScene(self.entity_manager, self.resource_manager, self.ui_system, self, self.ui_editor_system)
        self.scene_manager.add_scene(ui_editor_scene)

    def handle_event(self, event):
        """处理游戏事件"""
        # 先让UI编辑器处理事件
        if hasattr(self, 'ui_editor_system') and self.ui_editor_system.active:
            if self.ui_editor_system.handle_event(event):
                return
        
        # 如果UI编辑器没有处理事件，则交给输入系统处理
        self.input_system.process_event(event)

    def update(self):
        """更新游戏逻辑"""
        # 计算帧间时间
        current_time = time.time()
        self.delta_time = current_time - self.last_time
        self.last_time = current_time
        
        # 计算FPS
        if self.delta_time > 0:
            self.fps = int(1.0 / self.delta_time)
        
        # 更新各系统
        self.input_system.update(self.delta_time)
        self.physics_system.update(self.delta_time)
        self.ui_system.update(self.delta_time)
        
        # 更新当前场景
        current_scene = self.scene_manager.get_current_scene()
        if current_scene:
            current_scene.update(self.delta_time)
        
        # 更新FPS显示
        self.update_fps_display()

    def render(self):
        """渲染游戏画面"""
        # 清除屏幕
        self.render_system.clear_screen()
        
        # 渲染游戏对象
        self.render_system.render()
        
        # 渲染UI
        self.ui_system.render()

    def cleanup(self):
        """清理资源"""
        self.render_system.cleanup()
        self.physics_system.cleanup()
        self.resource_manager.cleanup()
    
    def change_scene(self, scene_name):
        """切换场景"""
        return self.scene_manager.change_scene(scene_name)
    
    def update_fps_display(self):
        """更新FPS显示"""
        # 查找FPS标签
        fps_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
        for entity in fps_entities:
            ui_comp = entity.get_component(ComponentType.UI)
            if "FPS" in ui_comp.text:
                ui_comp.text = f"FPS: {self.fps}"
                break
        
    def create_entity(self, name="Entity"):
        """创建一个新实体"""
        return self.entity_manager.create_entity(name)
        
    def get_entity(self, entity_id):
        """获取特定ID的实体"""
        return self.entity_manager.get_entity(entity_id)
        
    def get_entities_with_components(self, *component_types):
        """获取拥有特定组件的所有实体"""
        return self.entity_manager.get_entities_with_components(*component_types)
        
    def load_resource(self, resource_id, resource_path, resource_type):
        """加载资源"""
        if resource_type == "texture":
            return self.resource_manager.load_texture(resource_id, resource_path)
        elif resource_type == "model":
            return self.resource_manager.load_model(resource_id, resource_path)
        elif resource_type == "sound":
            return self.resource_manager.load_sound(resource_id, resource_path)
        elif resource_type == "shader":
            # 假设着色器需要顶点和片段着色器路径
            vertex_path = resource_path + ".vert"
            fragment_path = resource_path + ".frag"
            return self.resource_manager.load_shader(resource_id, vertex_path, fragment_path)
        elif resource_type == "font":
            return self.resource_manager.load_font(resource_id, resource_path)
        return False
        
    def get_resource(self, resource_id):
        """获取资源"""
        return self.resource_manager.get_resource(resource_id)
