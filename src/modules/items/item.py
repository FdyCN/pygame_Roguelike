import pygame
from ..resource_manager import resource_manager

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        self.world_x = x
        self.world_y = y
        self.item_type = item_type
        self.collected = False
        
        # 根据物品类型设置图像
        if item_type == 'exp':
            # 加载宝石精灵表并获取第一个宝石
            spritesheet = resource_manager.load_spritesheet('gems_spritesheet', 'images/items/gems.png')
            self.image = resource_manager.create_animation('exp_gem', spritesheet,
                                                         frame_width=16, frame_height=16,
                                                         frame_count=1, row=0,
                                                         frame_duration=0.1).get_current_frame()
            self.value = 100  # 经验值
        elif item_type == 'coin':
            spritesheet = resource_manager.load_spritesheet('money_spritesheet', 'images/items/money.png')
            self.image = resource_manager.create_animation('coin', spritesheet,
                                                         frame_width=16, frame_height=16,
                                                         frame_count=1, row=0,
                                                         frame_duration=0.1).get_current_frame()
            self.value = 1  # 金币值
        elif item_type == 'health':
            spritesheet = resource_manager.load_spritesheet('potions_spritesheet', 'images/items/potions.png')
            self.image = resource_manager.create_animation('health', spritesheet,
                                                         frame_width=16, frame_height=16,
                                                         frame_count=1, row=0,
                                                         frame_duration=0.1).get_current_frame()
            self.value = 20  # 恢复血量
        # 杀boss掉落，开宝箱抽奖(武器、被动升级卡片，组合超武升级只能通过宝箱)
        elif item_type == 'chest':
            spritesheet = resource_manager.load_spritesheet('chest_spritesheet', 'images/items/chests_bundled_16x16.png')
            self.image = resource_manager.create_animation('chest', spritesheet,
                                                         frame_width=16, frame_height=16, 
                                                         frame_count=1, row=0, col=6,
                                                         frame_duration=0.1).get_current_frame()


        # 缩放图片到合适大小
        if item_type == 'chest':
            self.image = pygame.transform.scale(self.image, (24, 24))  # 将物品图片缩放为24x24像素
        else:
            self.image = pygame.transform.scale(self.image, (16, 16))  # 将物品图片缩放为16x16像素
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 物品移动速度
        self.attract_speed = 350
        
    def update(self, dt, player):
        if self.collected:
            return
            
        # 计算与玩家的距离
        dx = player.world_x - self.world_x
        dy = player.world_y - self.world_y
        distance = (dx**2 + dy**2)**0.5
        
        # 如果在玩家的拾取范围内，向玩家移动
        if distance < player.pickup_range:
            if distance > 0:
                self.world_x += (dx/distance) * self.attract_speed * dt
                self.world_y += (dy/distance) * self.attract_speed * dt
                
        # 如果足够接近玩家，触发收集
        if distance < 10:
            self.collect(player)
            
    def collect(self, player):
        if self.collected:
            return
            
        self.collected = True
        
        if self.item_type == 'exp':
            player.add_experience(self.value)
        elif self.item_type == 'coin':
            player.add_coins(self.value)
        elif self.item_type == 'health':
            player.heal(self.value)
        elif self.item_type == 'chest':
            # TODO: 宝箱掉落物品,随机掉落武器、被动升级卡片、组合超武升级
            pass

    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        if self.collected:
            return
            
        # 计算屏幕位置
        screen_x = screen_center_x + (self.world_x - camera_x)
        screen_y = screen_center_y + (self.world_y - camera_y)
        self.rect.center = (screen_x, screen_y)
        
        screen.blit(self.image, self.rect) 