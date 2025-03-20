import pygame
import math
from .resource_manager import resource_manager

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health, damage, speed):
        super().__init__()
        
        # 敌人类型
        self.type = 'ghost'  # 默认类型
        
        # 加载精灵表并创建动画
        idle_spritesheet = resource_manager.load_spritesheet('enemy_idle_spritesheet', 'images/enemy/Ghost_Idle.png')
        walk_spritesheet = resource_manager.load_spritesheet('enemy_walk_spritesheet', 'images/enemy/Ghost_Idle.png')
        hurt_spritesheet = resource_manager.load_spritesheet('enemy_hurt_spritesheet', 'images/enemy/Ghost_Idle.png')
        
        # 创建各种状态的动画
        self.animations = {
            'idle': resource_manager.create_animation('enemy_idle', idle_spritesheet, 
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=0.0333),  # 30 FPS
            'walk': resource_manager.create_animation('enemy_walk', walk_spritesheet,
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=0.0333),  # 30 FPS
            'hurt': resource_manager.create_animation('enemy_hurt', hurt_spritesheet,
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=0.0333),  # 30 FPS
        }
        
        # 设置当前动画
        self.current_animation = 'idle'
        self.image = self.animations[self.current_animation].get_current_frame()
        # 翻转初始图像
        self.image = pygame.transform.flip(self.image, True, False)
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
        
        # 动画状态
        self.hurt_timer = 0
        self.hurt_duration = 0.2  # 受伤动画持续时间
        
        # 朝向
        self.facing_right = True
        
    def update(self, dt, player):
        # 更新当前动画
        self.animations[self.current_animation].update(dt)
        
        # 更新动画状态
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.current_animation = 'idle'
                self.animations[self.current_animation].reset()
        
        # 计算到玩家的方向（使用世界坐标）
        dx = player.world_x - self.rect.x
        dy = player.world_y - self.rect.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 更新朝向（根据玩家世界坐标位置）
        self.facing_right = dx > 0
        
        if distance != 0:
            # 标准化方向向量
            dx = dx / distance
            dy = dy / distance
            
            # 更新位置（在世界坐标系中）
            self.rect.x += dx * self.speed * dt
            self.rect.y += dy * self.speed * dt
            
            # 如果不在其他动画状态中，切换到行走动画
            if self.hurt_timer <= 0:
                if self.current_animation != 'walk':
                    self.current_animation = 'walk'
                    self.animations[self.current_animation].reset()
                
        elif self.hurt_timer <= 0:
            if self.current_animation != 'idle':
                self.current_animation = 'idle'
                self.animations[self.current_animation].reset()
            
        # 更新当前图像
        current_frame = self.animations[self.current_animation].get_current_frame()
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
        # 切换到受伤动画
        self.current_animation = 'hurt'
        self.animations[self.current_animation].reset()
        self.hurt_timer = self.hurt_duration
        
    def attack_player(self, player):
        # 计算与玩家的距离（使用世界坐标）
        dx = self.rect.x - player.world_x
        dy = self.rect.y - player.world_y
        distance = (dx**2 + dy**2)**0.5
        
        # 如果在攻击范围内
        if distance < self.rect.width / 2 + player.rect.width / 2:
            player.take_damage(self.damage)
            return True
        return False