import pygame
from ..resource_manager import resource_manager
from ..save_system import SaveSystem
from ..utils import FontManager

class SaveMenu:
    def __init__(self, screen, is_save_mode=True):
        self.screen = screen
        self.is_active = False
        self.is_save_mode = is_save_mode  # True为保存模式，False为读取模式
        self.save_system = SaveSystem()
        
        # 加载字体
        self.title_font = FontManager.get_font(60)
        self.info_font = FontManager.get_font(36)
        
        # 颜色设置
        self.title_color = (255, 255, 255)
        self.text_color = (200, 200, 200)
        self.hover_color = (255, 255, 0)
        self.empty_slot_color = (100, 100, 100)
        
        # 计算布局
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # 存档槽的大小和位置
        self.slot_width = 600
        self.slot_height = 150
        self.slot_padding = 20
        self.screenshot_size = (200, 120)  # 截图预览大小
        
        # 计算起始位置使存档槽垂直居中
        total_height = (self.slot_height + self.slot_padding) * 3
        self.start_y = (self.screen_height - total_height) // 2
        
        # 存储存档槽的矩形区域
        self.slot_rects = []
        self.selected_index = 0
        
        # 确认覆盖对话框
        self.show_confirm = False
        self.confirm_selected = 0  # 0: 否, 1: 是
        
        # 返回按钮
        self.back_button_rect = pygame.Rect(
            20, self.screen_height - 60, 100, 40
        )
        self.back_button_hover = False
        
    def show(self):
        """显示存档菜单"""
        self.is_active = True
        self.show_confirm = False
        self.selected_index = 0
        
    def hide(self):
        """隐藏存档菜单"""
        self.is_active = False
        self.show_confirm = False
        
    def handle_event(self, event):
        """处理输入事件"""
        if not self.is_active:
            return None
            
        if self.show_confirm:
            return self._handle_confirm_event(event)
            
        mouse_pos = pygame.mouse.get_pos()
        
        # 更新返回按钮悬停状态
        self.back_button_hover = self.back_button_rect.collidepoint(mouse_pos)
            
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_UP, pygame.K_w]:
                self.selected_index = (self.selected_index - 1) % 3
                resource_manager.play_sound("menu_move")
            elif event.key in [pygame.K_DOWN, pygame.K_s]:
                self.selected_index = (self.selected_index + 1) % 3
                resource_manager.play_sound("menu_move")
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                return self._handle_slot_selection()
            elif event.key == pygame.K_ESCAPE:
                return "back"
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 检查返回按钮点击
            if self.back_button_hover:
                resource_manager.play_sound("menu_select")
                return "back"
                
            # 检查存档槽点击
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    resource_manager.play_sound("menu_select")
                    return self._handle_slot_selection()
                    
        elif event.type == pygame.MOUSEMOTION:
            # 更新存档槽选择
            for i, rect in enumerate(self.slot_rects):
                if rect.collidepoint(mouse_pos):
                    if self.selected_index != i:
                        self.selected_index = i
                        resource_manager.play_sound("menu_move")
                    break
                    
        return None
        
    def _handle_confirm_event(self, event):
        """处理确认对话框的事件"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                self.confirm_selected = 0
                resource_manager.play_sound("menu_move")
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                self.confirm_selected = 1
                resource_manager.play_sound("menu_move")
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if self.confirm_selected == 0:  # 否
                    self.show_confirm = False
                else:  # 是
                    self.show_confirm = False
                    return f"slot_{self.selected_index + 1}"
            elif event.key == pygame.K_ESCAPE:
                self.show_confirm = False
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            # TODO: 添加确认按钮的点击检测
            
        return None
        
    def _handle_slot_selection(self):
        """处理存档槽的选择"""
        slot_id = self.selected_index + 1
        save_info = self.save_system.get_save_info(slot_id)
        
        # 如果是读取模式且存档槽为空，不做任何操作
        if not self.is_save_mode and not save_info:
            return None
            
        if self.is_save_mode and save_info:
            # 如果是保存模式且存档槽不为空，显示确认对话框
            self.show_confirm = True
            return None
            
        # 如果是读取模式，直接返回存档数据
        if not self.is_save_mode:
            save_data = self.save_system.load_game(slot_id)
            if save_data:
                return save_data
            return None
            
        # 返回选择的存档槽
        return f"slot_{slot_id}"
        
    def render(self):
        """渲染存档菜单"""
        if not self.is_active:
            return
            
        # 绘制纯黑色背景
        self.screen.fill((0, 0, 0))
        
        # 绘制标题
        title = "保存游戏" if self.is_save_mode else "读取游戏"
        title_text = self.title_font.render(title, True, self.title_color)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title_text, title_rect)
        
        # 清空之前的存档槽矩形
        self.slot_rects.clear()
        
        # 获取所有存档信息
        saves = self.save_system.get_all_saves()
        
        # 绘制存档槽
        for i in range(3):  # 固定显示3个存档槽
            slot_x = (self.screen_width - self.slot_width) // 2
            slot_y = self.start_y + i * (self.slot_height + self.slot_padding)
            
            # 创建存档槽矩形
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_width, self.slot_height)
            self.slot_rects.append(slot_rect)
            
            # 绘制存档槽背景
            color = self.hover_color if i == self.selected_index else self.text_color
            pygame.draw.rect(self.screen, color, slot_rect, 2)
            
            # 获取存档信息（如果存在）
            save = saves[i] if i < len(saves) else {'info': None}
            
            if save['info']:
                # 有存档数据时显示存档信息
                self._render_save_slot(slot_x, slot_y, save['info'])
            else:
                # 空存档槽
                empty_text = self.info_font.render("- 空存档槽 -", True, self.empty_slot_color)
                empty_rect = empty_text.get_rect(center=(slot_x + self.slot_width // 2, slot_y + self.slot_height // 2))
                self.screen.blit(empty_text, empty_rect)
        
        # 绘制返回按钮
        button_color = self.hover_color if self.back_button_hover else self.text_color
        pygame.draw.rect(self.screen, button_color, self.back_button_rect, 2)
        back_text = self.info_font.render("返回", True, button_color)
        back_rect = back_text.get_rect(center=self.back_button_rect.center)
        self.screen.blit(back_text, back_rect)
        
        # 绘制确认对话框
        if self.show_confirm:
            self._render_confirm_dialog()
            
    def _render_save_slot(self, slot_x, slot_y, save_info):
        """渲染单个存档槽的信息"""
        # 加载并显示截图
        if save_info['screenshot_path']:
            try:
                screenshot = pygame.image.load(save_info['screenshot_path'])
                screenshot = pygame.transform.scale(screenshot, self.screenshot_size)
                self.screen.blit(screenshot, (slot_x + 10, slot_y + 15))
            except:
                pass
        
        # 显示存档信息
        info_x = slot_x + self.screenshot_size[0] + 20
        info_y = slot_y + 15
        
        # 显示存档时间
        time_text = self.info_font.render(f"保存时间：{save_info['timestamp']}", True, self.text_color)
        self.screen.blit(time_text, (info_x, info_y))
        
        # 显示玩家等级
        level_text = self.info_font.render(f"玩家等级：{save_info['player_level']}", True, self.text_color)
        self.screen.blit(level_text, (info_x, info_y + 30))
        
        # 显示游戏时间
        game_time = save_info['game_time']
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = self.info_font.render(f"游戏时间：{minutes:02d}:{seconds:02d}", True, self.text_color)
        self.screen.blit(time_text, (info_x, info_y + 60))
        
    def _render_confirm_dialog(self):
        """渲染确认对话框"""
        # 创建对话框背景
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        # 绘制纯黑色背景
        self.screen.fill((0, 0, 0))
        
        # 绘制对话框背景
        pygame.draw.rect(self.screen, (50, 50, 50), (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, self.text_color, (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # 绘制提示文本
        warning_text = self.info_font.render("该存档槽已有数据，是否覆盖？", True, self.text_color)
        warning_rect = warning_text.get_rect(center=(self.screen_width // 2, dialog_y + 50))
        self.screen.blit(warning_text, warning_rect)
        
        # 绘制选项
        for i, option in enumerate(["否", "是"]):
            color = self.hover_color if i == self.confirm_selected else self.text_color
            option_text = self.info_font.render(option, True, color)
            option_x = dialog_x + dialog_width // 4 + (i * dialog_width // 2)
            option_rect = option_text.get_rect(center=(option_x, dialog_y + 120))
            self.screen.blit(option_text, option_rect) 