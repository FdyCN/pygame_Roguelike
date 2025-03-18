import pygame
from .utils import FontManager

class UI:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = FontManager.get_font(36)
        
    def render(self, score, level, health):
        # 渲染分数
        score_text = self.font.render(f'分数: {score}', True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        # 渲染等级
        level_text = self.font.render(f'等级: {level}', True, (255, 255, 255))
        self.screen.blit(level_text, (10, 50))
        
        # 渲染血条
        health_bar_width = 200
        health_bar_height = 20
        health_ratio = health / 100  # 假设最大血量是100
        
        # 血条背景
        pygame.draw.rect(self.screen, (255, 0, 0),
                        (10, 90, health_bar_width, health_bar_height))
        
        # 当前血量
        pygame.draw.rect(self.screen, (0, 255, 0),
                        (10, 90, health_bar_width * health_ratio, health_bar_height))
        
        # 血量文字
        health_text = self.font.render(f'HP: {health}/100', True, (255, 255, 255))
        self.screen.blit(health_text, (220, 90)) 