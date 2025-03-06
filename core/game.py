import pygame
from core.ecs import Entity, Component, System
from systems.render_system import RenderSystem
from systems.input_system import InputSystem
#from systems.physics_system import PhysicsSystem  # 物理系统暂时注释掉，如果需要再启用

class Game:
    """游戏主类，管理游戏状态和主循环"""
    def __init__(self, width, height, title):
        pygame.init()
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.entities = {}
        self.systems = []
        
        self.init_systems()
        self.init_entities()

    def init_systems(self):
        """初始化所有系统"""
        self.render_system = RenderSystem(self)
        self.input_system = InputSystem(self)
        #self.physics_system = PhysicsSystem(self)  # 物理系统暂时注释掉，如果需要再启用
        
        self.systems.append(self.render_system)
        self.systems.append(self.input_system)
        #self.systems.append(self.physics_system)  # 物理系统暂时注释掉，如果需要再启用

    def init_entities(self):
        """初始化实体，例如玩家、敌人等"""
        # 示例：创建一个玩家实体
        player = Entity()
        player.add_component(Position(0, 0, 0))
        player.add_component(Graphic("path/to/player/model"))  # 假设Graphic组件需要模型路径
        self.add_entity(player)

    def add_entity(self, entity):
        """添加实体到游戏"""
        self.entities[entity.id] = entity

    def remove_entity(self, entity_id):
        """从游戏移除实体"""
        if entity_id in self.entities:
            del self.entities[entity_id]

    def handle_event(self, event):
        """处理pygame事件"""
        self.input_system.handle_event(event)

    def update(self):
        """更新游戏逻辑"""
        dt = self.clock.get_time() / 1000.0  # 转换为秒
        for system in self.systems:
            system.update(dt)

    def render(self):
        """渲染游戏画面"""
        self.render_system.render()

    def cleanup(self):
        """清理资源"""
        pygame.quit()

# 示例组件
class Position(Component):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z

class Graphic(Component):
    def __init__(self, model_path):
        self.model_path = model_path
