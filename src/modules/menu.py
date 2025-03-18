import pygame
from .utils import FontManager

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

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.is_active = False
        
        # 创建半透明背景
        self.overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # 黑色半透明
        
        # 创建菜单面板
        panel_width = 400
        panel_height = 300
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = (screen.get_height() - panel_height) // 2
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # 创建字体
        self.title_font = FontManager.get_font(48)
        self.button_font = FontManager.get_font(36)
        
        # 创建标题
        self.title_text = self.title_font.render("游戏暂停", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(screen.get_width() // 2, panel_y + 50))
        
        # 创建按钮
        button_width = 200
        button_height = 50
        button_x = panel_x + (panel_width - button_width) // 2
        
        self.continue_button = Button(
            button_x, panel_y + 120, 
            button_width, button_height, 
            "继续游戏", self.button_font
        )
        
        self.restart_button = Button(
            button_x, panel_y + 180, 
            button_width, button_height, 
            "重新开始", self.button_font
        )
        
        self.exit_button = Button(
            button_x, panel_y + 240, 
            button_width, button_height, 
            "退出游戏", self.button_font
        )
        
    def toggle(self):
        self.is_active = not self.is_active
        
    def update(self, mouse_pos):
        if not self.is_active:
            return
            
        self.continue_button.update(mouse_pos)
        self.restart_button.update(mouse_pos)
        self.exit_button.update(mouse_pos)
        
    def render(self):
        if not self.is_active:
            return
            
        # 绘制半透明背景
        self.screen.blit(self.overlay, (0, 0))
        
        # 绘制菜单面板
        pygame.draw.rect(self.screen, (30, 30, 30), self.panel_rect, 0, 15)
        pygame.draw.rect(self.screen, (100, 100, 100), self.panel_rect, 3, 15)
        
        # 绘制标题
        self.screen.blit(self.title_text, self.title_rect)
        
        # 绘制按钮
        self.continue_button.render(self.screen)
        self.restart_button.render(self.screen)
        self.exit_button.render(self.screen)
        
    def handle_event(self, event):
        if not self.is_active:
            return None
            
        if self.continue_button.is_clicked(event):
            return "continue"
        elif self.restart_button.is_clicked(event):
            return "restart"
        elif self.exit_button.is_clicked(event):
            return "exit"
            
        return None 