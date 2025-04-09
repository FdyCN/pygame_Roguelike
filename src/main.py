import pygame
import sys
from modules.game import Game

def main():
    pygame.init()
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("像素生存")
    
    clock = pygame.time.Clock()
    game = Game(screen)
    
    while game.running:
        dt = clock.tick(30) / 1000.0  # 转换为秒
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        
        game.update(dt)
        game.render()
        pygame.display.flip()
    
    # 如果游戏结束，退出
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 