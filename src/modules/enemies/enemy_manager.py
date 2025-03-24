import pygame
import random
import math
from .types import Ghost, Radish, Bat

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 1.0  # 每秒生成一个敌人
        self.difficulty = 1
        self.game_time = 0  # 游戏进行时间
        self.bat_spawn_timer = 0  # 蝙蝠生成计时器
        
    def spawn_enemy(self, enemy_type, x, y, health=None):
        """在指定位置生成指定类型和生命值的敌人
        
        Args:
            enemy_type: 敌人类型 ('ghost', 'radish', 'bat')
            x: 世界坐标系中的x坐标
            y: 世界坐标系中的y坐标
            health: 指定生命值，如果为None则使用该类型的默认生命值
            
        Returns:
            Enemy: 生成的敌人实例
        """
        # 根据类型创建对应的敌人实例
        enemy = None
        if enemy_type == 'ghost':
            enemy = Ghost(x, y)
        elif enemy_type == 'radish':
            enemy = Radish(x, y)
        elif enemy_type == 'bat':
            enemy = Bat(x, y)
            
        if enemy and health is not None:
            enemy.health = health
            enemy.max_health = health
            
        if enemy:
            self.enemies.append(enemy)
            
        return enemy
        
    def update(self, dt, player):
        self.game_time += dt
        self.spawn_timer += dt
        
        # 根据时间和玩家等级生成敌人
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.random_spawn_enemy(player)
            
        # 如果玩家等级达到5级，更新蝙蝠生成计时器
        if player.level >= 5:
            self.bat_spawn_timer += dt
            if int(self.bat_spawn_timer) % 60 == 0:  # 每60秒生成一个蝙蝠
                self.bat_spawn_timer = 0
                self.spawn_bat(player)
            
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
            
    def random_spawn_enemy(self, player):
        """在玩家周围随机位置生成敌人"""
        # 在玩家周围的屏幕外随机位置生成敌人
        spawn_distance = 600  # 生成距离
        
        # 随机角度
        angle = random.uniform(0, 2 * math.pi)
        
        # 计算生成位置（世界坐标系）
        x = player.world_x + spawn_distance * math.cos(angle)
        y = player.world_y + spawn_distance * math.sin(angle)
        
        # 根据游戏时间决定生成什么类型的敌人
        if self.game_time < 10:  # 游戏开始10秒内
            self.spawn_enemy('ghost', x, y)
        else:  # 10秒后可以生成幽灵和萝卜
            enemy_type = random.choice(['ghost', 'radish'])
            self.spawn_enemy(enemy_type, x, y)
            
    def spawn_bat(self, player):
        """在玩家周围生成一个蝙蝠"""
        spawn_distance = 600
        angle = random.uniform(0, 2 * math.pi)
        x = player.world_x + spawn_distance * math.cos(angle)
        y = player.world_y + spawn_distance * math.sin(angle)
        self.spawn_enemy('bat', x, y) 