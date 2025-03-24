import pygame
import math
from ..resource_manager import resource_manager
from abc import ABC, abstractmethod

class Enemy(pygame.sprite.Sprite, ABC):
    def __init__(self, x, y, health, damage, speed, scale=2.0):
        super().__init__()
        
        # 敌人基本属性
        self.type = None  # 子类需要设置具体类型
        self.animations = {}  # 子类需要设置具体动画
        self.current_animation = 'idle'
        self.scale = scale  # 缩放因子
        
        # 设置敌人在世界坐标系中的位置
        self.rect = pygame.Rect(x, y, 44 * scale, 30 * scale)  # 根据缩放调整碰撞箱大小
        
        # 敌人属性
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.score_value = 10  # 默认分数值，子类可以修改
        
        # 攻击冷却
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.5  # 攻击冷却时间（秒）
        self.has_damaged_player = False
        
        # 动画状态
        self.hurt_timer = 0
        self.hurt_duration = 0.2
        
        # 朝向
        self.facing_right = True
        
    @abstractmethod
    def load_animations(self):
        """加载敌人的动画，子类必须实现"""
        pass
        
    def update(self, dt, player):
        # 更新当前动画
        if self.current_animation in self.animations:
            self.animations[self.current_animation].update(dt)
        
        # 更新动画状态
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.current_animation = 'idle'
                if self.current_animation in self.animations:
                    self.animations[self.current_animation].reset()
        
        # 计算到玩家的方向（使用世界坐标）
        dx = player.world_x - self.rect.x
        dy = player.world_y - self.rect.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 更新朝向
        self.facing_right = dx > 0
        
        if distance != 0:
            # 标准化方向向量
            dx = dx / distance
            dy = dy / distance
            
            # 更新位置
            self.rect.x += dx * self.speed * dt
            self.rect.y += dy * self.speed * dt
            
            # 如果不在受伤状态，切换到行走动画
            if self.hurt_timer <= 0:
                if self.current_animation != 'walk':
                    self.current_animation = 'walk'
                    if self.current_animation in self.animations:
                        self.animations[self.current_animation].reset()
                
        elif self.hurt_timer <= 0:
            if self.current_animation != 'idle':
                self.current_animation = 'idle'
                if self.current_animation in self.animations:
                    self.animations[self.current_animation].reset()
                    
        # 更新当前图像
        self.update_image()
            
    def update_image(self):
        """更新敌人的当前图像"""
        if self.current_animation in self.animations:
            current_frame = self.animations[self.current_animation].get_current_frame()
            
            # 缩放图像
            original_size = current_frame.get_size()
            new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
            current_frame = pygame.transform.scale(current_frame, new_size)
            
        # 总是翻转当前帧
        current_frame = pygame.transform.flip(current_frame, True, False)
        
        # 根据朝向再次翻转图像
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
            
        self.image = current_frame
            
    def render(self, screen, screen_x, screen_y):
        # 创建一个临时的rect用于绘制
        draw_rect = self.rect.copy()
        draw_rect.x = screen_x
        draw_rect.y = screen_y
        
        # 绘制敌人
        if hasattr(self, 'image'):
            screen.blit(self.image, draw_rect)
        
        # 绘制血条
        health_bar_width = 32 * self.scale  # 血条也要相应缩放
        health_bar_height = 5 * self.scale
        health_ratio = self.health / self.max_health
        
        # 调整血条位置，使其位于敌人上方
        bar_x = screen_x
        bar_y = screen_y - 10 * self.scale
        
        pygame.draw.rect(screen, (255, 0, 0),  # 红色背景
                        (bar_x, bar_y,
                         health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0),  # 绿色血条
                        (bar_x, bar_y,
                         health_bar_width * health_ratio, health_bar_height))
        
    def take_damage(self, amount):
        """受到伤害"""
        self.health -= amount
        # 切换到受伤动画
        self.current_animation = 'hurt'
        if self.current_animation in self.animations:
            self.animations[self.current_animation].reset()
        self.hurt_timer = self.hurt_duration
        
    def attack_player(self, player):
        """攻击玩家"""
        # 计算与玩家的距离
        dx = self.rect.x - player.world_x
        dy = self.rect.y - player.world_y
        distance = (dx**2 + dy**2)**0.5
        
        # 如果在攻击范围内
        if distance < self.rect.width / 2 + player.rect.width / 2:
            player.take_damage(self.damage)
            return True
        return False