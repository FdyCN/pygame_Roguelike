import pygame
import math
from .resource_manager import resource_manager

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # 加载精灵表并创建动画
        idle_spritesheet = resource_manager.load_spritesheet('player', 'images/player/Knight_Idle.png')
        run_spritesheet = resource_manager.load_spritesheet('player', 'images/player/Knight_Run.png')
        hurt_spritesheet = resource_manager.load_spritesheet('player', 'images/player/Knight_Hit.png')
        # 创建各种状态的动画
        self.animations = {
            'idle': resource_manager.create_animation('player_idle', idle_spritesheet, 
                                                    frame_width=32, frame_height=32,
                                                    frame_count=10, row=0,
                                                    frame_duration=0.1),
            'run': resource_manager.create_animation('player_run', run_spritesheet,
                                                   frame_width=32, frame_height=32,
                                                   frame_count=10, row=0,
                                                   frame_duration=0.1),
            'hurt': resource_manager.create_animation('player_hurt', hurt_spritesheet,
                                                    frame_width=32, frame_height=32,
                                                    frame_count=1, row=0,
                                                    frame_duration=0.1, loop=False)
        }
        
        # 设置当前动画
        self.current_animation = 'idle'
        self.image = self.animations[self.current_animation].get_current_frame()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 世界坐标（游戏中的实际位置）
        self.world_x = 0
        self.world_y = 0
        
        # 玩家属性
        self.speed = 300
        self.max_health = 100
        self.health = self.max_health
        self.level = 1
        self.experience = 0
        
        # 移动相关
        self.velocity = pygame.math.Vector2()
        self.direction = pygame.math.Vector2()
        self.moving = {'up': False, 'down': False, 'left': False, 'right': False}
        self.facing_right = True  # 添加朝向标记
        
        # 受伤状态
        self.hurt_timer = 0
        self.hurt_duration = 0.2  # 受伤动画持续时间
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.moving['up'] = True
            elif event.key == pygame.K_s:
                self.moving['down'] = True
            elif event.key == pygame.K_a:
                self.moving['left'] = True
                self.facing_right = False  # 更新朝向
            elif event.key == pygame.K_d:
                self.moving['right'] = True
                self.facing_right = True  # 更新朝向
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.moving['up'] = False
            elif event.key == pygame.K_s:
                self.moving['down'] = False
            elif event.key == pygame.K_a:
                self.moving['left'] = False
            elif event.key == pygame.K_d:
                self.moving['right'] = False
        
        # 更新方向向量
        self.direction.x = float(self.moving['right']) - float(self.moving['left'])
        self.direction.y = float(self.moving['down']) - float(self.moving['up'])
                
    def update(self, dt):
        # 更新当前动画
        self.animations[self.current_animation].update(dt)
        
        # 更新受伤状态
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0 and self.current_animation == 'hurt':
                # 受伤动画播放完毕
                if self.direction.length() > 0:
                    self.current_animation = 'run'
                else:
                    self.current_animation = 'idle'
                self.animations[self.current_animation].reset()
        
        # 更新速度向量和动画状态
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
            if self.hurt_timer <= 0 and self.current_animation != 'run':
                self.current_animation = 'run'
                self.animations[self.current_animation].reset()
        elif self.hurt_timer <= 0 and self.current_animation != 'idle':
            self.current_animation = 'idle'
            self.animations[self.current_animation].reset()
        
        self.velocity = self.direction * self.speed
        
        # 更新世界坐标位置（实际位置）
        self.world_x += self.velocity.x * dt
        self.world_y += self.velocity.y * dt
        
        # 更新当前图像
        current_frame = self.animations[self.current_animation].get_current_frame()
        
        # 根据朝向翻转图像
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
            
        self.image = current_frame
        
    def render(self, screen):
        screen.blit(self.image, self.rect)
        
        # 绘制血条
        health_bar_width = 32
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (255, 0, 0),  # 红色背景
                        (self.rect.x, self.rect.y - 10,
                         health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0),  # 绿色血条
                        (self.rect.x, self.rect.y - 10,
                         health_bar_width * health_ratio, health_bar_height))
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            # 处理玩家死亡
        else:
            # 切换到受伤动画
            self.current_animation = 'hurt'
            self.animations[self.current_animation].reset()
            self.hurt_timer = self.hurt_duration
            
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        
    def add_experience(self, amount):
        self.experience += amount
        # 检查是否升级
        if self.experience >= self.level * 100:  # 简单的升级公式
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.experience = 0
        self.max_health += 10
        self.health = self.max_health
        self.speed += 10 