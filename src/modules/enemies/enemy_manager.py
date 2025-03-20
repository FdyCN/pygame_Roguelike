import pygame
import random
import math
from .enemy import Enemy

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 1.0  # 每秒生成一个敌人
        self.difficulty = 1
        
    def update(self, dt, player):
        self.spawn_timer += dt
        
        # 根据难度生成敌人
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self._spawn_enemy(player)
            
        # 更新所有敌人
        for enemy in self.enemies[:]:  # 使用切片创建副本以避免在迭代时修改列表
            enemy.update(dt, player)
            
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        for enemy in self.enemies:
            # 计算敌人在屏幕上的位置
            screen_x = screen_center_x + (enemy.rect.x - camera_x)
            screen_y = screen_center_y + (enemy.rect.y - camera_y)
            
            # 只渲染在屏幕范围内的敌人
            if -50 <= screen_x <= screen.get_width() + 50 and -50 <= screen_y <= screen.get_height() + 50:
                enemy.render(screen, screen_x, screen_y)
            
    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            
    def _spawn_enemy(self, player):
        # 在玩家周围的屏幕外随机位置生成敌人
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        spawn_distance = 600  # 生成距离
        
        # 随机角度
        angle = random.uniform(0, 2 * 3.14159)
        
        # 计算生成位置（世界坐标系）
        x = player.world_x + spawn_distance * math.cos(angle)
        y = player.world_y + spawn_distance * math.sin(angle)
            
        # 根据难度调整敌人属性
        health = 50 + (self.difficulty * 10)
        damage = 5 + (self.difficulty * 2)
        speed = 100 + (self.difficulty * 10)
        
        enemy = Enemy(x, y, health, damage, speed)
        self.enemies.append(enemy) 