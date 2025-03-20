import pygame
from .utils import FontManager
from .upgrade_system import UpgradeManager, UpgradeType

class Button:
    def __init__(self, x, y, width, height, text, font, color=(200, 200, 200), hover_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.text_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.text_surface = self.font.render(self.text, True, self.hover_color if self.is_hovered else self.color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        
    def render(self, screen):
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 0, 10)
        if self.is_hovered:
            pygame.draw.rect(screen, (100, 100, 100), self.rect, 3, 10)
        screen.blit(self.text_surface, self.text_rect)
        
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        
        # 基础菜单样式
        self.width = 400
        self.height = 300
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # 基础颜色
        self.bg_color = (30, 30, 30)
        self.border_color = (100, 100, 100)
        self.selected_color = (80, 80, 80)
        self.text_color = (200, 200, 200)
        self.hover_color = (255, 255, 255)
        self.title_color = (255, 215, 0)  # 金色
        
        # 基础字体
        self.title_font = FontManager.get_font(48)
        self.option_font = FontManager.get_font(32)
        self.desc_font = FontManager.get_font(24)
        
    def show(self):
        self.is_active = True
        
    def hide(self):
        self.is_active = False
        
    def _create_overlay(self):
        """创建半透明背景"""
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
    def _draw_menu_background(self):
        """绘制菜单背景"""
        pygame.draw.rect(self.screen, self.bg_color, 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, self.border_color,
                        (self.x, self.y, self.width, self.height), 2)
                        
    def _is_mouse_over_option(self, mouse_pos, option_rect):
        """检查鼠标是否悬停在选项上"""
        return option_rect.collidepoint(mouse_pos)

class PauseMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.options = ["继续游戏", "重新开始", "退出游戏"]
        self.selected_index = 0
        self.option_rects = []  # 存储选项的矩形区域
        
    def handle_event(self, event):
        if not self.is_active:
            return None
            
        # 键盘控制
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._handle_selection(self.selected_index)
                
        # 鼠标控制
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    return self._handle_selection(i)
                    
        # 更新鼠标悬停状态
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break
                    
        return None
        
    def _handle_selection(self, index):
        """处理选项选择"""
        if index == 0:
            self.hide()
            return "continue"
        elif index == 1:
            return "restart"
        elif index == 2:
            return "exit"
        return None
        
    def render(self):
        if not self.is_active:
            return
            
        self._create_overlay()
        self._draw_menu_background()
        
        # 绘制标题
        title = self.title_font.render("游戏暂停", True, self.title_color)
        title_rect = title.get_rect(centerx=self.x + self.width//2, y=self.y + 20)
        self.screen.blit(title, title_rect)
        
        # 清空并重新计算选项矩形
        self.option_rects = []
        
        # 绘制选项
        for i, option in enumerate(self.options):
            color = self.hover_color if i == self.selected_index else self.text_color
            text = self.option_font.render(option, True, color)
            text_rect = text.get_rect(centerx=self.x + self.width//2,
                                    y=self.y + 100 + i * 50)
            
            # 绘制选中背景
            if i == self.selected_index:
                bg_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, self.selected_color, bg_rect)
                
            self.screen.blit(text, text_rect)
            self.option_rects.append(text_rect.inflate(20, 10))

class GameOverMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.options = ["重新开始", "退出游戏"]
        self.selected_index = 0
        self.option_rects = []
        
    def handle_event(self, event):
        if not self.is_active:
            return None
            
        # 键盘控制
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._handle_selection(self.selected_index)
                
        # 鼠标控制
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    return self._handle_selection(i)
                    
        # 更新鼠标悬停状态
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break
                    
        return None
        
    def _handle_selection(self, index):
        """处理选项选择"""
        if index == 0:
            return "restart"
        elif index == 1:
            return "exit"
        return None
        
    def render(self):
        if not self.is_active:
            return
            
        self._create_overlay()
        self._draw_menu_background()
        
        # 绘制标题
        title = self.title_font.render("游戏结束", True, self.title_color)
        title_rect = title.get_rect(centerx=self.x + self.width//2, y=self.y + 20)
        self.screen.blit(title, title_rect)
        
        # 清空并重新计算选项矩形
        self.option_rects = []
        
        # 绘制选项
        for i, option in enumerate(self.options):
            color = self.hover_color if i == self.selected_index else self.text_color
            text = self.option_font.render(option, True, color)
            text_rect = text.get_rect(centerx=self.x + self.width//2,
                                    y=self.y + 100 + i * 50)
            
            # 绘制选中背景
            if i == self.selected_index:
                bg_rect = text_rect.inflate(20, 10)
                pygame.draw.rect(self.screen, self.selected_color, bg_rect)
                
            self.screen.blit(text, text_rect)
            self.option_rects.append(text_rect.inflate(20, 10))

class UpgradeMenu(Menu):
    def __init__(self, screen):
        super().__init__(screen)
        self.options = []
        self.selected_index = 0
        self.upgrade_manager = UpgradeManager()
        self.option_rects = []
        
        # 修改菜单样式
        self.width = 800
        self.height = 500
        self.x = (screen.get_width() - self.width) // 2
        self.y = (screen.get_height() - self.height) // 2
        
        # 添加特殊颜色
        self.weapon_color = (255, 100, 100)  # 红色
        self.passive_color = (100, 255, 100)  # 绿色
        
    def show(self, player):
        self.is_active = True
        self.options = self.upgrade_manager.get_random_upgrades(player)
        self.selected_index = 0
        
    def handle_event(self, event):
        if not self.is_active:
            return None
            
        # 键盘控制
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                selected_upgrade = self.options[self.selected_index]
                self.hide()
                return selected_upgrade
                
        # 鼠标控制
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    selected_upgrade = self.options[i]
                    self.hide()
                    return selected_upgrade
                    
        # 更新鼠标悬停状态
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    break
                    
        return None
        
    def render(self):
        if not self.is_active:
            return
            
        self._create_overlay()
        self._draw_menu_background()
        
        # 绘制标题
        title = self.title_font.render("选择升级", True, self.title_color)
        title_rect = title.get_rect(centerx=self.x + self.width//2, y=self.y + 20)
        self.screen.blit(title, title_rect)
        
        # 清空并重新计算选项矩形
        self.option_rects = []
        
        # 绘制选项
        for i, option in enumerate(self.options):
            # 选项背景
            option_height = 120
            option_y = self.y + 90 + i * (option_height + 10)
            option_rect = pygame.Rect(self.x + 10, option_y, self.width - 20, option_height)
            
            # 绘制选中/悬停背景
            if i == self.selected_index:
                pygame.draw.rect(self.screen, self.selected_color, option_rect)
                pygame.draw.rect(self.screen, self.title_color, option_rect, 2)
            
            # 绘制图标背景和边框
            icon_bg_rect = pygame.Rect(self.x + 20, option_y + 10, 64, 64)
            pygame.draw.rect(self.screen, (50, 50, 50), icon_bg_rect)
            pygame.draw.rect(self.screen, self.border_color, icon_bg_rect, 1)
            
            # 绘制图标（如果有）
            if option.icon:
                icon_rect = option.icon.get_rect(center=icon_bg_rect.center)
                self.screen.blit(option.icon, icon_rect)
            
            # 绘制选项名称（根据类型使用不同颜色）
            name_color = self.weapon_color if option.upgrade_type == UpgradeType.WEAPON else self.passive_color
            if i == self.selected_index:
                name_color = self.hover_color
            name = self.option_font.render(option.name, True, name_color)
            self.screen.blit(name, (self.x + 100, option_y + 20))
            
            # 绘制选项描述
            desc = self.desc_font.render(option.description, True, self.text_color)
            self.screen.blit(desc, (self.x + 100, option_y + 60))
            
            # 保存选项矩形
            self.option_rects.append(option_rect) 