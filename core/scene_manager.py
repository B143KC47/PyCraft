from core.components import ComponentType, TransformComponent, RenderComponent, PhysicsComponent, InputComponent, CameraComponent, UIComponent
import pygame

class Scene:
    """场景类，代表游戏中的一个场景"""
    
    def __init__(self, name, entity_manager, resource_manager):
        self.name = name
        self.entity_manager = entity_manager
        self.resource_manager = resource_manager
        self.entities = []
    
    def load(self):
        """加载场景"""
        print(f"加载场景: {self.name}")
        pass
    
    def unload(self):
        """卸载场景"""
        print(f"卸载场景: {self.name}")
        # 移除场景中的所有实体
        for entity_id in self.entities:
            self.entity_manager.remove_entity(entity_id)
        self.entities.clear()
    
    def update(self, delta_time):
        """更新场景"""
        # 基类中的默认实现，子类可以重写此方法
        pass
    
    def add_entity(self, entity):
        """添加实体到场景"""
        self.entities.append(entity.id)
        return entity
    
    def create_entity(self, name="Entity"):
        """创建一个新实体并添加到场景"""
        entity = self.entity_manager.create_entity(name)
        self.entities.append(entity.id)
        return entity

class TestScene(Scene):
    """测试场景，用于测试引擎功能"""
    
    def __init__(self, entity_manager, resource_manager, ui_system, game):
        super().__init__("TestScene", entity_manager, resource_manager)
        self.ui_system = ui_system
        self.game = game
    
    def load(self):
        """加载测试场景"""
        super().load()
        
        # 创建相机
        camera = self.create_entity("TestCamera")
        camera_transform = TransformComponent(position=(0, 2, 5))
        camera_component = CameraComponent(is_active=True)
        
        camera.add_component(ComponentType.TRANSFORM, camera_transform)
        camera.add_component(ComponentType.CAMERA, camera_component)
        print("创建相机")
        
        # 创建一个立方体
        cube = self.create_entity("TestCube")
        cube_transform = TransformComponent(position=(0, 0, 0))
        cube_render = RenderComponent(visible=True)
        cube_physics = PhysicsComponent(mass=1.0)
        
        cube.add_component(ComponentType.TRANSFORM, cube_transform)
        cube.add_component(ComponentType.RENDER, cube_render)
        cube.add_component(ComponentType.PHYSICS, cube_physics)
        print("创建立方体")
        
        # 创建地面
        ground = self.create_entity("Ground")
        ground_transform = TransformComponent(position=(0, -2, 0), scale=(10, 0.1, 10))
        ground_render = RenderComponent(visible=True)
        ground_physics = PhysicsComponent(mass=0, is_static=True)
        
        ground.add_component(ComponentType.TRANSFORM, ground_transform)
        ground.add_component(ComponentType.RENDER, ground_render)
        ground.add_component(ComponentType.PHYSICS, ground_physics)
        print("创建地面")
        
        # 创建UI元素
        fps_label = self.ui_system.create_label("FPS: 60", (10, 10), font_size=16)
        self.entities.append(fps_label.id)
        print("创建UI元素")

class MainMenuScene(Scene):
    """主菜单场景"""
    
    def __init__(self, entity_manager, resource_manager, ui_system, game):
        super().__init__("MainMenu", entity_manager, resource_manager)
        self.ui_system = ui_system
        self.game = game
    
    def load(self):
        """加载主菜单场景"""
        super().load()
        
        # 创建相机
        camera = self.create_entity("MenuCamera")
        camera_transform = TransformComponent(position=(0, 0, 5))
        camera_component = CameraComponent(is_active=True)
        
        camera.add_component(ComponentType.TRANSFORM, camera_transform)
        camera.add_component(ComponentType.CAMERA, camera_component)
        
        # 创建UI元素
        title = self.ui_system.create_label("PyCraft Engine", (self.game.width/2 - 100, 100), font_size=32)
        self.entities.append(title.id)
        
        start_button = self.ui_system.create_button("Start Game", (self.game.width/2 - 50, 200), (100, 50), 
                                                  callback=lambda e: self.game.change_scene("GameScene"))
        self.entities.append(start_button.id)
        
        test_button = self.ui_system.create_button("Test Scene", (self.game.width/2 - 50, 260), (100, 50),
                                                 callback=lambda e: self.game.change_scene("TestScene"))
        self.entities.append(test_button.id)
        
        # 添加UI编辑器按钮
        editor_button = self.ui_system.create_button("UI Editor", (self.game.width/2 - 50, 320), (100, 50),
                                                  callback=lambda e: self.game.change_scene("UIEditorScene"))
        self.entities.append(editor_button.id)
        
        exit_button = self.ui_system.create_button("Exit", (self.game.width/2 - 50, 380), (100, 50), 
                                                 callback=lambda e: setattr(self.game, 'running', False))
        self.entities.append(exit_button.id)

class GameScene(Scene):
    """游戏场景"""
    
    def __init__(self, entity_manager, resource_manager, ui_system, game):
        super().__init__("GameScene", entity_manager, resource_manager)
        self.ui_system = ui_system
        self.game = game
    
    def load(self):
        """加载游戏场景"""
        super().load()
        
        # 创建地面
        ground = self.create_entity("Ground")
        ground_transform = TransformComponent(position=(0, -1, 0), scale=(10, 0.1, 10))
        ground_physics = PhysicsComponent(mass=0, is_static=True)
        ground_render = RenderComponent(visible=True)
        
        ground.add_component(ComponentType.TRANSFORM, ground_transform)
        ground.add_component(ComponentType.PHYSICS, ground_physics)
        ground.add_component(ComponentType.RENDER, ground_render)
        
        # 创建玩家
        player = self.create_entity("Player")
        player_transform = TransformComponent(position=(0, 0, 0))
        player_physics = PhysicsComponent(mass=1.0)
        player_render = RenderComponent(visible=True)
        player_input = InputComponent(controllable=True)
        
        player.add_component(ComponentType.TRANSFORM, player_transform)
        player.add_component(ComponentType.PHYSICS, player_physics)
        player.add_component(ComponentType.RENDER, player_render)
        player.add_component(ComponentType.INPUT, player_input)
        
        # 创建相机
        camera = self.create_entity("MainCamera")
        camera_transform = TransformComponent(position=(0, 2, 5))
        camera_component = CameraComponent(is_active=True)
        
        camera.add_component(ComponentType.TRANSFORM, camera_transform)
        camera.add_component(ComponentType.CAMERA, camera_component)
        
        # 创建UI元素
        fps_label = self.ui_system.create_label("FPS: 60", (10, 10), font_size=16)
        self.entities.append(fps_label.id)
        
        pause_button = self.ui_system.create_button("Pause", (self.game.width - 70, 10), (60, 30))
        self.entities.append(pause_button.id)

class SceneManager:
    """场景管理器，负责管理游戏场景"""
    
    def __init__(self, game):
        self.game = game
        self.scenes = {}
        self.current_scene = None
    
    def add_scene(self, scene):
        """添加场景"""
        self.scenes[scene.name] = scene
        print(f"添加场景: {scene.name}")
    
    def change_scene(self, scene_name):
        """切换场景"""
        if scene_name not in self.scenes:
            print(f"错误: 场景 {scene_name} 不存在")
            return False
        
        print(f"切换场景: {scene_name}")
        
        # 卸载当前场景
        if self.current_scene:
            self.current_scene.unload()
        
        # 加载新场景
        self.current_scene = self.scenes[scene_name]
        self.current_scene.load()
        
        return True
    
    def get_current_scene(self):
        """获取当前场景"""
        return self.current_scene 

class UIEditorScene(Scene):
    """UI编辑器场景"""
    
    def __init__(self, entity_manager, resource_manager, ui_system, game, ui_editor_system):
        super().__init__("UIEditorScene", entity_manager, resource_manager)
        self.ui_system = ui_system
        self.game = game
        self.ui_editor_system = ui_editor_system
    
    def load(self):
        """加载UI编辑器场景"""
        super().load()
        
        # 创建返回按钮
        back_btn = self.ui_system.create_button("返回", (10, 10), (60, 30), 
                                              callback=lambda e: self.game.change_scene("MainMenu"))
        self.entities.append(back_btn.id)
        
        # 创建编辑器切换按钮
        editor_btn = self.ui_system.create_button("编辑模式", (80, 10), (80, 30), 
                                                callback=lambda e: self.ui_editor_system.toggle_editor())
        self.entities.append(editor_btn.id)
        
        # 创建FPS显示
        fps_label = self.ui_system.create_label("FPS: 0", (170, 10), 16)
        self.entities.append(fps_label.id)
        
        # 激活编辑器
        self.ui_editor_system.toggle_editor()
    
    def unload(self):
        """卸载UI编辑器场景"""
        # 如果编辑器处于激活状态，关闭它
        if self.ui_editor_system.active:
            self.ui_editor_system.toggle_editor()
        
        # 调用父类的unload方法
        super().unload()
    
    def update(self, delta_time):
        """更新UI编辑器场景"""
        # 更新编辑器系统
        self.ui_editor_system.update(delta_time) 