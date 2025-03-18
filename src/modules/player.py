import pygame
import math

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([32, 32])
        self.image.fill((255, 255, 255))  # 临时用白色方块表示玩家
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
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.moving['up'] = True
            elif event.key == pygame.K_s:
                self.moving['down'] = True
            elif event.key == pygame.K_a:
                self.moving['left'] = True
            elif event.key == pygame.K_d:
                self.moving['right'] = True
                
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
        # 更新速度向量
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()
        
        self.velocity = self.direction * self.speed
        
        # 更新世界坐标位置（实际位置）
        self.world_x += self.velocity.x * dt
        self.world_y += self.velocity.y * dt
        
    def render(self, screen):
        screen.blit(self.image, self.rect)
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            # 处理玩家死亡
            
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