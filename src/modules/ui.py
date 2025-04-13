import pygame
from .utils import FontManager
from .resource_manager import resource_manager
from .upgrade_system import UpgradeManager

class UI:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = FontManager.get_font(24)
        self.small_font = FontManager.get_font(24)  # 较小的字体用于时间显示
        
        # UI颜色
        self.exp_bar_color = (0, 255, 255)    # 青色
        self.exp_back_color = (0, 100, 100)   # 深青色
        self.health_bar_color = (255, 0, 0)   # 红色
        self.health_back_color = (100, 0, 0)  # 深红色
        self.text_color = (255, 255, 255)     # 白色
        self.coin_color = (255, 215, 0)       # 金色
        
        # UI尺寸和位置
        self.margin = 10  # 减小边距
        self.bar_height = 20
        self.icon_size = 32  # 技能图标大小
        self.icon_spacing = 10  # 图标之间的间距
        
        # 加载金币图标
        self.coin_icon = resource_manager.load_image('coin', 'images/items/coin_32x32.png')
        self.coin_icon = pygame.transform.scale(self.coin_icon, (24, 24))  # 调整金币图标大小
        
        # 加载击杀统计图标
        self.kill_icon = resource_manager.load_image('kill_count', 'images/enemy/enemy_kill_32x32.png')
        self.kill_icon = pygame.transform.scale(self.kill_icon, (24, 24))  # 调整击杀图标大小
        
        # 创建升级管理器实例用于获取图标
        self.upgrade_manager = UpgradeManager()
        
    def render(self, player, game_time, game_kill_num):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 绘制经验条背景（顶部）
        pygame.draw.rect(self.screen, self.exp_back_color,
                        (0, 0, screen_width, self.bar_height))
        
        # 绘制经验条
        exp_width = (player.experience / player.exp_to_next_level) * screen_width
        pygame.draw.rect(self.screen, self.exp_bar_color,
                        (0, 0, exp_width, self.bar_height))
        
        # 渲染等级文本（嵌入在经验条中间）
        level_text = f"Lv.{player.level}"
        
        # 创建文本对象以获取尺寸
        text = self.font.render(level_text, True, self.text_color)
        text_rect = text.get_rect()
        text_rect.centerx = screen_width // 2
        text_rect.centery = self.bar_height // 2
        
        # 渲染文本阴影（略微偏移）
        shadow_text = self.font.render(level_text, True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect()
        shadow_rect.centerx = screen_width // 2 + 2
        shadow_rect.centery = self.bar_height // 2 + 2
        self.screen.blit(shadow_text, shadow_rect)
        
        # 渲染主文本
        self.screen.blit(text, text_rect)
        
        # 绘制生命槽背景（底部）
        pygame.draw.rect(self.screen, self.health_back_color,
                        (0, screen_height - self.bar_height, screen_width, self.bar_height))
        
        # 绘制生命槽
        health_width = (player.health / player.max_health) * screen_width
        pygame.draw.rect(self.screen, self.health_bar_color,
                        (0, screen_height - self.bar_height, health_width, self.bar_height))
        
        # 计算技能图标框的总宽度（每排3个）
        total_icons_width = 3 * (self.icon_size + self.icon_spacing) - self.icon_spacing
        start_x = (screen_width - total_icons_width) // 2
        
        # 武器图标位于上排
        weapon_y = screen_height - self.bar_height - (self.icon_size + self.icon_spacing) * 2 - 5
        # 被动图标位于下排
        passive_y = screen_height - self.bar_height - self.icon_size - 5
        
        # 绘制3个武器图标框（上排）
        for i in range(3):
            icon_x = start_x + i * (self.icon_size + self.icon_spacing)
            icon_rect = pygame.Rect(icon_x, weapon_y, self.icon_size, self.icon_size)
            
            # 绘制半透明背景
            s = pygame.Surface((self.icon_size, self.icon_size))
            s.set_alpha(128)
            s.fill((50, 50, 50))
            self.screen.blit(s, icon_rect)
            
            # 绘制边框
            pygame.draw.rect(self.screen, (100, 100, 100), icon_rect, 1)
            
            # 如果有对应的武器，绘制其图标
            if i < len(player.weapons):
                weapon = player.weapons[i]
                weapon_type = weapon.type
                weapon_level = player.weapon_levels.get(weapon_type, 1)
                if weapon_type in self.upgrade_manager.weapon_upgrades:
                    upgrade = self.upgrade_manager.weapon_upgrades[weapon_type]
                    if weapon_level <= len(upgrade.levels):
                        icon = upgrade.levels[weapon_level - 1].icon
                        if icon:
                            # 缩放图标到合适大小
                            scaled_icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
                            self.screen.blit(scaled_icon, icon_rect)
                            
        # 绘制3个被动技能图标框（下排）
        for i in range(3):
            icon_x = start_x + i * (self.icon_size + self.icon_spacing)
            icon_rect = pygame.Rect(icon_x, passive_y, self.icon_size, self.icon_size)
            
            # 绘制半透明背景
            s = pygame.Surface((self.icon_size, self.icon_size))
            s.set_alpha(128)
            s.fill((50, 50, 50))
            self.screen.blit(s, icon_rect)
            
            # 绘制边框
            pygame.draw.rect(self.screen, (100, 100, 100), icon_rect, 1)
            
            # 如果有对应的被动技能，绘制其图标
            if i < len(player.passives):
                passive_type = list(player.passives.keys())[i]
                passive_level = player.passive_levels.get(passive_type, 1)
                if passive_type in self.upgrade_manager.passive_upgrades:
                    upgrade = self.upgrade_manager.passive_upgrades[passive_type]
                    if passive_level <= len(upgrade.levels):
                        icon = upgrade.levels[passive_level - 1].icon
                        if icon:
                            # 缩放图标到合适大小
                            scaled_icon = pygame.transform.scale(icon, (self.icon_size, self.icon_size))
                            self.screen.blit(scaled_icon, icon_rect)
        
        # 渲染游戏时间（左上角，紧贴经验条下方）
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = self.small_font.render(f"{minutes:02d}:{seconds:02d}", True, self.text_color)
        time_rect = time_text.get_rect()
        time_rect.left = self.margin
        time_rect.top = self.bar_height + self.margin
        self.screen.blit(time_text, time_rect)
        
        # 渲染击杀统计（中间，紧贴经验条下方）
        kill_count = game_kill_num
        kill_text = self.font.render(str(kill_count), True, self.text_color)
        kill_text_rect = kill_text.get_rect()
        kill_icon_rect = self.kill_icon.get_rect()
        
        # 计算击杀统计文本和图标的位置（居中）
        total_width = kill_icon_rect.width + 5 + kill_text_rect.width
        center_x = screen_width // 2
        kill_icon_rect.right = center_x - 5
        kill_icon_rect.top = self.bar_height + self.margin
        kill_text_rect.left = center_x + 5
        kill_text_rect.centery = kill_icon_rect.centery
        
        # 渲染击杀统计文本和图标
        self.screen.blit(self.kill_icon, kill_icon_rect)
        self.screen.blit(kill_text, kill_text_rect)
        
        # 渲染金币数量和图标（右上角，紧贴经验条下方）
        coin_text = self.font.render(str(player.coins), True, self.coin_color)
        coin_text_rect = coin_text.get_rect()
        coin_icon_rect = self.coin_icon.get_rect()
        
        # 计算金币文本和图标的位置
        coin_text_rect.right = screen_width - self.margin - coin_icon_rect.width - 5
        coin_text_rect.top = self.bar_height + self.margin
        coin_icon_rect.right = coin_text_rect.left - 5
        coin_icon_rect.centery = coin_text_rect.centery
        
        # 渲染金币文本和图标
        self.screen.blit(coin_text, coin_text_rect)
        self.screen.blit(self.coin_icon, coin_icon_rect) 