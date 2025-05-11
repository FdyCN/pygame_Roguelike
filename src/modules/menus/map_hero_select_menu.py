import pygame
from ..resource_manager import resource_manager
from ..utils import FontManager

class MapHeroSelectMenu:
    """地图和英雄选择菜单"""
    
    def __init__(self, screen, on_start_game=None, on_back=None):
        """初始化地图和英雄选择菜单
        
        Args:
            screen: 游戏屏幕
            on_start_game: 开始游戏回调函数，接收地图ID和英雄ID作为参数
            on_back: 返回按钮回调函数
        """
        self.screen = screen
        self.on_start_game = on_start_game
        self.on_back = on_back
        
        # 菜单状态
        self.active = False
        self.selected_map = None  # 选中的地图ID
        self.selected_hero = None  # 选中的英雄ID
        
        # 界面参数
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # 使用FontManager加载字体
        self.title_font = FontManager.get_font(50)
        self.font = FontManager.get_font(32)
        self.small_font = FontManager.get_font(24)
        
        # 颜色设置 - 与主菜单保持一致
        self.title_color = (255, 255, 255)
        self.text_color = (200, 200, 200)
        self.hover_color = (255, 255, 0)
        self.selected_color = (80, 80, 80)
        self.bg_color = (30, 30, 30)
        self.border_color = (100, 100, 100)
        
        # 计算布局参数
        self._calculate_layout()
        
        # 加载可用地图和英雄
        self._load_maps_and_heroes()
        
        # 准备按钮
        self._prepare_buttons()
        
        # 加载背景图片（如果有的话）
        try:
            self.background = resource_manager.load_image('menu_background', 'images/menu/background.png')
            self.background = pygame.transform.scale(self.background, (screen.get_width(), screen.get_height()))
        except:
            self.background = None
        
    def _calculate_layout(self):
        """计算界面布局参数"""
        # 地图选择区域
        self.map_section_y = 120
        self.map_section_height = 200
        self.map_icon_size = 150
        self.map_icon_margin = 20
        
        # 英雄选择区域
        self.hero_section_y = self.map_section_y + self.map_section_height + 50
        self.hero_section_height = 150
        self.hero_icon_size = 100
        self.hero_icon_margin = 20
        
        # 按钮区域
        self.button_section_y = self.hero_section_y + self.hero_section_height + 50
        self.button_width = 200
        self.button_height = 50
        self.button_margin = 30
        
    def _load_maps_and_heroes(self):
        """加载可用的地图和英雄数据"""
        # 这里可以从配置文件、资源管理器等获取数据
        # 暂时使用硬编码示例数据
        
        self.maps = [
            {"id": "simple_map", "name": "森林", "unlocked": True},
            {"id": "desert_map", "name": "沙漠", "unlocked": False},
            {"id": "cave_map", "name": "洞穴", "unlocked": False},
        ]
        
        self.heroes = [
            {"id": "ninja_frog", "name": "忍者蛙", "unlocked": True},
            {"id": "knight", "name": "骑士", "unlocked": False},
            {"id": "warrior", "name": "战士", "unlocked": False},
            {"id": "mage", "name": "法师", "unlocked": False},
            {"id": "archer", "name": "弓箭手", "unlocked": False},
        ]
        
        # 加载图像
        self._load_images()
        
    def _load_images(self):
        """加载地图和英雄的图像"""
        # 加载地图图像
        self.map_images = {}
        for map_data in self.maps:
            try:
                # 尝试加载地图图像
                map_id = map_data["id"]
                if map_data["unlocked"]:
                    # 这里应该从资源管理器加载实际图像
                    # 暂时使用临时创建的表面
                    image = pygame.Surface((self.map_icon_size, self.map_icon_size))
                    image.fill((100, 180, 100))  # 绿色代表森林
                    if map_id == "desert_map":
                        image.fill((220, 180, 100))  # 黄色代表沙漠
                    elif map_id == "cave_map":
                        image.fill((100, 100, 150))  # 蓝灰色代表洞穴
                    
                    # 在图像上绘制地图名称
                    name_text = self.small_font.render(map_data["name"], True, (255, 255, 255))
                    image.blit(name_text, (10, 10))
                else:
                    # 未解锁的地图使用灰色问号图像
                    image = pygame.Surface((self.map_icon_size, self.map_icon_size))
                    image.fill((100, 100, 100))  # 灰色背景
                    # 绘制问号
                    question_mark = self.font.render("?", True, (255, 255, 255))
                    image.blit(question_mark, (self.map_icon_size//2 - question_mark.get_width()//2, 
                                              self.map_icon_size//2 - question_mark.get_height()//2))
                
                self.map_images[map_id] = image
            except Exception as e:
                print(f"加载地图图像失败: {e}")
                # 使用默认图像
                image = pygame.Surface((self.map_icon_size, self.map_icon_size))
                image.fill((255, 0, 0))  # 红色表示错误
                self.map_images[map_data["id"]] = image
        
        # 加载英雄图像
        self.hero_images = {}
        for hero_data in self.heroes:
            try:
                # 尝试加载英雄图像
                hero_id = hero_data["id"]
                if hero_data["unlocked"]:
                    # 这里应该从资源管理器加载实际图像
                    # 暂时使用临时创建的表面
                    image = pygame.Surface((self.hero_icon_size, self.hero_icon_size), pygame.SRCALPHA)
                    pygame.draw.circle(image, (100, 180, 100), 
                                      (self.hero_icon_size//2, self.hero_icon_size//2), 
                                      self.hero_icon_size//2)
                    
                    # 在图像上绘制英雄名称
                    name_text = self.small_font.render(hero_data["name"], True, (255, 255, 255))
                    image.blit(name_text, (self.hero_icon_size//2 - name_text.get_width()//2, 
                                          self.hero_icon_size//2 - name_text.get_height()//2))
                else:
                    # 未解锁的英雄使用灰色问号图像
                    image = pygame.Surface((self.hero_icon_size, self.hero_icon_size), pygame.SRCALPHA)
                    pygame.draw.circle(image, (100, 100, 100), 
                                      (self.hero_icon_size//2, self.hero_icon_size//2), 
                                      self.hero_icon_size//2)
                    # 绘制问号
                    question_mark = self.font.render("?", True, (255, 255, 255))
                    image.blit(question_mark, (self.hero_icon_size//2 - question_mark.get_width()//2, 
                                              self.hero_icon_size//2 - question_mark.get_height()//2))
                
                self.hero_images[hero_id] = image
            except Exception as e:
                print(f"加载英雄图像失败: {e}")
                # 使用默认图像
                image = pygame.Surface((self.hero_icon_size, self.hero_icon_size))
                image.fill((255, 0, 0))  # 红色表示错误
                self.hero_images[hero_data["id"]] = image
                
    def _prepare_buttons(self):
        """准备按钮"""
        # 开始游戏按钮
        self.start_button = {
            "rect": pygame.Rect(
                self.width//2 - self.button_width - self.button_margin//2,
                self.button_section_y,
                self.button_width,
                self.button_height
            ),
            "text": "开始游戏",
            "enabled": False,
            "hovered": False
        }
        
        # 返回按钮
        self.back_button = {
            "rect": pygame.Rect(
                self.width//2 + self.button_margin//2,
                self.button_section_y,
                self.button_width,
                self.button_height
            ),
            "text": "返回",
            "enabled": True,
            "hovered": False
        }
        
    def show(self):
        """显示菜单"""
        self.active = True
        resource_manager.play_sound("menu_show")
        
    def hide(self):
        """隐藏菜单"""
        self.active = False
        
    def handle_event(self, event):
        """处理事件
        
        Args:
            event: pygame事件
            
        Returns:
            str: 事件处理结果，如"back"、"start_game"等
        """
        if not self.active:
            return None
            
        # 更新按钮悬停状态
        mouse_pos = pygame.mouse.get_pos()
        old_start_hover = self.start_button["hovered"]
        old_back_hover = self.back_button["hovered"]
        
        self.start_button["hovered"] = self.start_button["rect"].collidepoint(mouse_pos) and self.start_button["enabled"]
        self.back_button["hovered"] = self.back_button["rect"].collidepoint(mouse_pos)
        
        # 如果悬停状态改变，播放移动音效
        if (old_start_hover != self.start_button["hovered"] and self.start_button["hovered"]) or \
           (old_back_hover != self.back_button["hovered"] and self.back_button["hovered"]):
            resource_manager.play_sound("menu_move")
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 鼠标左键点击
            # 检查是否点击了地图
            for i, map_data in enumerate(self.maps):
                map_id = map_data["id"]
                x = (self.width - (len(self.maps) * (self.map_icon_size + self.map_icon_margin) - self.map_icon_margin)) // 2 + i * (self.map_icon_size + self.map_icon_margin)
                y = self.map_section_y
                
                map_rect = pygame.Rect(x, y, self.map_icon_size, self.map_icon_size)
                if map_rect.collidepoint(mouse_pos) and map_data["unlocked"]:
                    self.selected_map = map_id
                    # 检查是否可以启用开始按钮
                    self.start_button["enabled"] = self.selected_map is not None and self.selected_hero is not None
                    resource_manager.play_sound("menu_select")
                    return "map_selected"
            
            # 检查是否点击了英雄
            for i, hero_data in enumerate(self.heroes):
                hero_id = hero_data["id"]
                x = (self.width - (len(self.heroes) * (self.hero_icon_size + self.hero_icon_margin) - self.hero_icon_margin)) // 2 + i * (self.hero_icon_size + self.hero_icon_margin)
                y = self.hero_section_y
                
                hero_rect = pygame.Rect(x, y, self.hero_icon_size, self.hero_icon_size)
                if hero_rect.collidepoint(mouse_pos) and hero_data["unlocked"]:
                    self.selected_hero = hero_id
                    # 检查是否可以启用开始按钮
                    self.start_button["enabled"] = self.selected_map is not None and self.selected_hero is not None
                    resource_manager.play_sound("menu_select")
                    return "hero_selected"
            
            # 检查是否点击了按钮
            if self.start_button["rect"].collidepoint(mouse_pos) and self.start_button["enabled"]:
                resource_manager.play_sound("menu_select")
                if self.on_start_game:
                    self.on_start_game(self.selected_map, self.selected_hero)
                return "start_game"
                
            if self.back_button["rect"].collidepoint(mouse_pos):
                resource_manager.play_sound("menu_select")
                if self.on_back:
                    self.on_back()
                return "back"
                
        return None
        
    def render(self):
        """渲染菜单"""
        if not self.active:
            return
            
        # 绘制背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            # 如果没有背景图片，填充纯色背景
            self.screen.fill(self.bg_color)
        
        # 创建半透明背景
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.fill(self.bg_color)
        overlay.set_alpha(200)  # 设置透明度
        self.screen.blit(overlay, (0, 0))
        
        # 绘制标题
        title_text = self.title_font.render("选择地图和英雄", True, self.title_color)
        self.screen.blit(title_text, (self.width//2 - title_text.get_width()//2, 30))
        
        # 绘制地图选择区域
        map_text = self.font.render("选择地图", True, self.text_color)
        self.screen.blit(map_text, (50, self.map_section_y - 40))
        
        # 绘制地图图像
        for i, map_data in enumerate(self.maps):
            map_id = map_data["id"]
            x = (self.width - (len(self.maps) * (self.map_icon_size + self.map_icon_margin) - self.map_icon_margin)) // 2 + i * (self.map_icon_size + self.map_icon_margin)
            y = self.map_section_y
            
            # 绘制地图图像
            self.screen.blit(self.map_images[map_id], (x, y))
            
            # 如果是选中的地图，绘制高亮边框
            if map_id == self.selected_map:
                pygame.draw.rect(self.screen, self.hover_color, 
                                 pygame.Rect(x-2, y-2, self.map_icon_size+4, self.map_icon_size+4), 3)
        
        # 绘制英雄选择区域
        hero_text = self.font.render("选择英雄", True, self.text_color)
        self.screen.blit(hero_text, (50, self.hero_section_y - 40))
        
        # 绘制英雄图像
        for i, hero_data in enumerate(self.heroes):
            hero_id = hero_data["id"]
            x = (self.width - (len(self.heroes) * (self.hero_icon_size + self.hero_icon_margin) - self.hero_icon_margin)) // 2 + i * (self.hero_icon_size + self.hero_icon_margin)
            y = self.hero_section_y
            
            # 绘制英雄图像
            self.screen.blit(self.hero_images[hero_id], (x, y))
            
            # 如果是选中的英雄，绘制高亮边框
            if hero_id == self.selected_hero:
                pygame.draw.rect(self.screen, self.hover_color, 
                                 pygame.Rect(x-2, y-2, self.hero_icon_size+4, self.hero_icon_size+4), 3)
        
        # 绘制按钮
        self._render_button(self.start_button)
        self._render_button(self.back_button)
        
    def _render_button(self, button):
        """渲染按钮
        
        Args:
            button: 按钮信息字典
        """
        # 按钮背景
        if button["enabled"]:
            if button["hovered"]:
                bg_color = (100, 100, 210)
            else:
                bg_color = (80, 80, 190)
        else:
            bg_color = (70, 70, 70)
            
        pygame.draw.rect(self.screen, bg_color, button["rect"], 0, 10)  # 圆角矩形
        
        # 边框
        if button["hovered"] and button["enabled"]:
            pygame.draw.rect(self.screen, self.hover_color, button["rect"], 2, 10)
        else:
            pygame.draw.rect(self.screen, self.border_color, button["rect"], 2, 10)
        
        # 按钮文本
        text_color = self.hover_color if button["hovered"] and button["enabled"] else self.text_color
        text = self.font.render(button["text"], True, text_color)
        self.screen.blit(text, (
            button["rect"].centerx - text.get_width()//2,
            button["rect"].centery - text.get_height()//2
        )) 