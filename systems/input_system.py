import pygame
from core.ecs import System
from core.game import Position

class InputSystem(System):
    """输入系统，负责处理用户输入"""
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        """处理pygame事件"""
        if event.type == pygame.KEYDOWN:
            self.handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self.handle_keyup(event.key)

    def handle_keydown(self, key):
        """处理按键按下事件"""
        # 示例：按下W键，玩家向上移动
        if key == pygame.K_w:
            for entity in self.game.entities.values():
                position = entity.get_component("Position")
                if position:
                    position.y += 0.1

    def handle_keyup(self, key):
        """处理按键抬起事件"""
        pass
