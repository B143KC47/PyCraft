import pygame
import sys
from core.game import Game

def main():
    print("启动PyCraft引擎...")
    
    # 初始化游戏
    game = Game(width=800, height=600, title="PyCraft Engine")
    print("游戏初始化完成")
    
    # 游戏主循环
    print("进入游戏主循环")
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
    print("清理资源...")
    game.cleanup()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)
