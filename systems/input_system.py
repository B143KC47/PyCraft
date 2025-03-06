import pygame
from core.components import ComponentType, TransformComponent, InputComponent

class InputSystem:
    """输入系统，负责处理用户输入"""
    
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager
        self.key_actions = {}
        self.setup_default_key_actions()
    
    def setup_default_key_actions(self):
        """设置默认按键映射"""
        self.key_actions[pygame.K_w] = self.move_forward
        self.key_actions[pygame.K_s] = self.move_backward
        self.key_actions[pygame.K_a] = self.move_left
        self.key_actions[pygame.K_d] = self.move_right
        self.key_actions[pygame.K_SPACE] = self.jump
    
    def process_event(self, event):
        """处理pygame事件"""
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self.handle_keyup(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.handle_mouse_down(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_mouse_up(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_motion(event)
    
    def handle_keydown(self, key):
        """处理按键按下事件"""
        if key in self.key_actions:
            self.key_actions[key](True)
    
    def handle_keyup(self, key):
        """处理按键抬起事件"""
        if key in self.key_actions:
            self.key_actions[key](False)
    
    def handle_mouse_down(self, event):
        """处理鼠标按下事件"""
        pass
    
    def handle_mouse_up(self, event):
        """处理鼠标抬起事件"""
        pass
    
    def handle_mouse_motion(self, event):
        """处理鼠标移动事件"""
        pass
    
    def update(self, delta_time):
        """更新输入状态"""
        # 获取所有可控制的实体
        input_entities = self.entity_manager.get_entities_with_components(
            ComponentType.INPUT, ComponentType.TRANSFORM
        )
        
        # 处理连续输入
        keys = pygame.key.get_pressed()
        for key, action in self.key_actions.items():
            if keys[key]:
                action(True)
    
    # 默认动作函数
    def move_forward(self, pressed):
        """向前移动"""
        input_entities = self.entity_manager.get_entities_with_components(
            ComponentType.INPUT, ComponentType.TRANSFORM
        )
        
        for entity in input_entities:
            input_comp = entity.get_component(ComponentType.INPUT)
            if input_comp.controllable:
                transform_comp = entity.get_component(ComponentType.TRANSFORM)
                transform_comp.translate(0, 0, 0.1 if pressed else 0)
    
    def move_backward(self, pressed):
        """向后移动"""
        input_entities = self.entity_manager.get_entities_with_components(
            ComponentType.INPUT, ComponentType.TRANSFORM
        )
        
        for entity in input_entities:
            input_comp = entity.get_component(ComponentType.INPUT)
            if input_comp.controllable:
                transform_comp = entity.get_component(ComponentType.TRANSFORM)
                transform_comp.translate(0, 0, -0.1 if pressed else 0)
    
    def move_left(self, pressed):
        """向左移动"""
        input_entities = self.entity_manager.get_entities_with_components(
            ComponentType.INPUT, ComponentType.TRANSFORM
        )
        
        for entity in input_entities:
            input_comp = entity.get_component(ComponentType.INPUT)
            if input_comp.controllable:
                transform_comp = entity.get_component(ComponentType.TRANSFORM)
                transform_comp.translate(-0.1 if pressed else 0, 0, 0)
    
    def move_right(self, pressed):
        """向右移动"""
        input_entities = self.entity_manager.get_entities_with_components(
            ComponentType.INPUT, ComponentType.TRANSFORM
        )
        
        for entity in input_entities:
            input_comp = entity.get_component(ComponentType.INPUT)
            if input_comp.controllable:
                transform_comp = entity.get_component(ComponentType.TRANSFORM)
                transform_comp.translate(0.1 if pressed else 0, 0, 0)
    
    def jump(self, pressed):
        """跳跃"""
        if not pressed:
            return
            
        input_entities = self.entity_manager.get_entities_with_components(
            ComponentType.INPUT, ComponentType.TRANSFORM, ComponentType.PHYSICS
        )
        
        for entity in input_entities:
            input_comp = entity.get_component(ComponentType.INPUT)
            if input_comp.controllable:
                physics_comp = entity.get_component(ComponentType.PHYSICS)
                if physics_comp and not physics_comp.is_static:
                    # 应用向上的力
                    physics_comp.velocity[1] += 5.0
