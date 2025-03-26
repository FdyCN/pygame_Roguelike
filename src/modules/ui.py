import pygame
from .utils import FontManager
from .resource_manager import resource_manager

class UI:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = FontManager.get_font(36)
        self.small_font = FontManager.get_font(24)  # 较小的字体用于时间显示
        
        # UI颜色
        self.exp_bar_color = (0, 255, 255)    # 青色
        self.exp_back_color = (0, 100, 100)   # 深青色
        self.text_color = (255, 255, 255)     # 白色
        self.coin_color = (255, 215, 0)       # 金色
        
        # UI尺寸和位置
        self.margin = 10  # 减小边距
        self.bar_height = 20
        
        # 加载金币图标
        spritesheet = resource_manager.load_spritesheet('money_spritesheet', 'images/items/money.png')
        self.coin_icon = resource_manager.create_animation('coin', spritesheet,
                                                         frame_width=16, frame_height=16,
                                                         frame_count=1, row=0,
                                                         frame_duration=0.1).get_current_frame()
        self.coin_icon = pygame.transform.scale(self.coin_icon, (24, 24))  # 调整金币图标大小
        
    def render(self, player, game_time):
        screen_width = self.screen.get_width()
        
        # 绘制经验条背景
        pygame.draw.rect(self.screen, self.exp_back_color,
                        (0, 0, screen_width, self.bar_height))
        
        # 绘制经验条
        exp_width = (player.experience / player.exp_to_next_level) * screen_width
        pygame.draw.rect(self.screen, self.exp_bar_color,
                        (0, 0, exp_width, self.bar_height))
        
        # 渲染等级文本（在经验条下方居中）
        level_text = self.font.render(f"Level {player.level}", True, self.text_color)
        level_rect = level_text.get_rect()
        level_rect.centerx = screen_width // 2
        level_rect.top = self.bar_height + self.margin
        self.screen.blit(level_text, level_rect)
        
        # 渲染游戏时间（经验条左下方）
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = self.small_font.render(f"{minutes:02d}:{seconds:02d}", True, self.text_color)
        time_rect = time_text.get_rect()
        time_rect.left = self.margin
        time_rect.top = self.bar_height + self.margin
        self.screen.blit(time_text, time_rect)
        
        # 渲染金币数量和图标（经验条右下方）
        coin_text = self.font.render(str(player.coins), True, self.coin_color)
        coin_text_rect = coin_text.get_rect()
        coin_icon_rect = self.coin_icon.get_rect()
        
        # 计算金币文本和图标的位置
        coin_text_rect.right = screen_width - self.margin - coin_icon_rect.width - 5
        coin_text_rect.top = self.bar_height + self.margin
        coin_icon_rect.left = coin_text_rect.right + 5
        coin_icon_rect.centery = coin_text_rect.centery
        
        # 渲染金币文本和图标
        self.screen.blit(coin_text, coin_text_rect)
        self.screen.blit(self.coin_icon, coin_icon_rect) 