import pygame
import sys
from core.game import Game

def main():
    # 初始化游戏
    game = Game(width=800, height=600, title="PyCraft Engine")
    
    # 游戏主循环
    while game.running:
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            game.handle_event(event)
        
        # 更新游戏逻辑
        game.update()
        
        # 渲染游戏
        game.render()
        
        # 更新显示
        pygame.display.flip()
        
        # 控制帧率
        game.clock.tick(60)
    
    # 清理资源
    game.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
