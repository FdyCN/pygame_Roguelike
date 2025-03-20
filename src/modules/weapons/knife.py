import pygame
import math
from ..resource_manager import resource_manager

class Knife(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.type = 'knife'
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_knife', 'images/weapons/knife.png')
        self.rect = self.image.get_rect()
        
        # 武器属性
        self.level = 1
        self.damage = 20
        self.attack_speed = 2  # 每秒攻击次数
        self.range = 50  # 攻击范围
        
        # 攻击状态
        self.attack_timer = 0
        self.attack_interval = 1.0 / self.attack_speed
        self.angle = 0
        
        # 相对于玩家的偏移量（世界坐标系）
        self.offset_x = 0
        self.offset_y = 0
        
        # 加载攻击音效
        resource_manager.load_sound('knife_swing', 'sounds/weapons/knife_swing.wav')
        
    def update(self, dt):
        self.attack_timer += dt
        
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            self.angle = (self.angle + 45) % 360  # 旋转45度
            # 播放挥舞音效
            resource_manager.play_sound('knife_swing')
            
        # 更新相对于玩家的偏移量（世界坐标系）
        angle_rad = math.radians(self.angle)
        self.offset_x = math.cos(angle_rad) * self.range
        self.offset_y = math.sin(angle_rad) * self.range
        
        # 更新位置（用于碰撞检测）
        self.rect.centerx = self.player.rect.centerx + self.offset_x
        self.rect.centery = self.player.rect.centery + self.offset_y
        
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        # 创建旋转后的图像
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        
        # 计算武器在屏幕上的位置
        screen_x = screen_center_x + self.offset_x
        screen_y = screen_center_y + self.offset_y
        
        # 创建旋转后的矩形
        rotated_rect = rotated_image.get_rect(center=(screen_x, screen_y))
        
        # 绘制武器
        screen.blit(rotated_image, rotated_rect)
        
    def level_up(self):
        self.level += 1
        self.damage += 10
        self.attack_speed += 0.5
        self.range += 10
        self.attack_interval = 1.0 / self.attack_speed 