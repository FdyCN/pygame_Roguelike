import pygame
from .utils import FontManager

class UI:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = FontManager.get_font(36)
        
        # UI颜色
        self.health_bar_color = (255, 0, 0)  # 红色
        self.health_back_color = (100, 0, 0)  # 深红色
        self.exp_bar_color = (0, 255, 255)    # 青色
        self.exp_back_color = (0, 100, 100)   # 深青色
        self.text_color = (255, 255, 255)     # 白色
        self.coin_color = (255, 215, 0)       # 金色
        
        # UI尺寸和位置
        self.margin = 20
        self.bar_height = 20
        self.bar_width = 200
        
    def render(self, player):
        # 绘制血条背景
        pygame.draw.rect(self.screen, self.health_back_color,
                        (self.margin, self.margin, self.bar_width, self.bar_height))
        
        # 绘制血条
        health_width = (player.health / player.max_health) * self.bar_width
        pygame.draw.rect(self.screen, self.health_bar_color,
                        (self.margin, self.margin, health_width, self.bar_height))
        
        # 绘制经验条背景
        exp_bar_y = self.margin * 2 + self.bar_height
        pygame.draw.rect(self.screen, self.exp_back_color,
                        (self.margin, exp_bar_y, self.bar_width, self.bar_height))
        
        # 绘制经验条
        exp_width = (player.experience / player.exp_to_next_level) * self.bar_width
        pygame.draw.rect(self.screen, self.exp_bar_color,
                        (self.margin, exp_bar_y, exp_width, self.bar_height))
        
        # 渲染等级文本
        level_text = self.font.render(f"Level {player.level}", True, self.text_color)
        level_rect = level_text.get_rect()
        level_rect.left = self.margin + self.bar_width + 20
        level_rect.centery = exp_bar_y + self.bar_height / 2
        self.screen.blit(level_text, level_rect)
        
        # 渲染金币数量
        coin_text = self.font.render(f"Coins: {player.coins}", True, self.coin_color)
        coin_rect = coin_text.get_rect()
        coin_rect.right = self.screen.get_width() - self.margin
        coin_rect.top = self.margin
        self.screen.blit(coin_text, coin_rect)
        
        # 渲染血量数值
        health_text = self.font.render(f"{int(player.health)}/{player.max_health}", True, self.text_color)
        health_rect = health_text.get_rect()
        health_rect.left = self.margin + self.bar_width + 20
        health_rect.centery = self.margin + self.bar_height / 2
        self.screen.blit(health_text, health_rect) 