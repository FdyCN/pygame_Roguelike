import pygame
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health, damage, speed):
        super().__init__()
        self.image = pygame.Surface([32, 32])
        self.image.fill((255, 0, 0))  # 临时用红色方块表示敌人
        self.rect = self.image.get_rect()
        
        # 设置敌人在世界坐标系中的位置
        self.rect.x = x
        self.rect.y = y
        
        # 敌人属性
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.score_value = 10
        
        # 攻击冷却
        self.attack_cooldown = 0
        self.attack_cooldown_time = 0.5  # 攻击冷却时间（秒）
        self.has_damaged_player = False  # 是否已经对玩家造成伤害
        
    def update(self, dt, player):
        # 更新攻击冷却
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            if self.attack_cooldown <= 0:
                self.has_damaged_player = False
        
        # 计算到玩家的方向（使用世界坐标）
        dx = player.world_x - self.rect.x
        dy = player.world_y - self.rect.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance != 0:
            # 标准化方向向量
            dx = dx / distance
            dy = dy / distance
            
            # 更新位置（在世界坐标系中）
            self.rect.x += dx * self.speed * dt
            self.rect.y += dy * self.speed * dt
            
    def render(self, screen, screen_x, screen_y):
        # 创建一个临时的rect用于绘制
        draw_rect = self.rect.copy()
        draw_rect.x = screen_x
        draw_rect.y = screen_y
        
        # 绘制敌人
        screen.blit(self.image, draw_rect)
        
        # 绘制血条
        health_bar_width = 32
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (255, 0, 0),  # 红色背景
                        (screen_x, screen_y - 10,
                         health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0),  # 绿色血条
                        (screen_x, screen_y - 10,
                         health_bar_width * health_ratio, health_bar_height))
        
    def take_damage(self, amount):
        self.health -= amount
        
    def attack_player(self, player):
        # 如果冷却结束且未对玩家造成伤害，则造成伤害
        if self.attack_cooldown <= 0 and not self.has_damaged_player:
            player.take_damage(self.damage)
            self.attack_cooldown = self.attack_cooldown_time
            self.has_damaged_player = True
            return True
        return False 