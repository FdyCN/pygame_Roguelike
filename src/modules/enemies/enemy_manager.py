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
        
        # 敌人类型配置
        self.enemy_types = {
            'normal': {
                'base_health': 50,
                'base_damage': 5,
                'base_speed': 100
            },
            'fast': {
                'base_health': 30,
                'base_damage': 3,
                'base_speed': 150
            },
            'tank': {
                'base_health': 100,
                'base_damage': 8,
                'base_speed': 70
            }
        }
        
    def spawn_enemy(self, enemy_type, x, y, health=None):
        """在指定位置生成指定类型和生命值的敌人
        
        Args:
            enemy_type: 敌人类型 ('normal', 'fast', 'tank')
            x: 世界坐标系中的x坐标
            y: 世界坐标系中的y坐标
            health: 指定生命值，如果为None则使用该类型的基础生命值
            
        Returns:
            Enemy: 生成的敌人实例
        """
        # 获取敌人类型的基础属性
        enemy_config = self.enemy_types.get(enemy_type, self.enemy_types['normal'])
        
        # 如果没有指定生命值，使用基础生命值
        if health is None:
            health = enemy_config['base_health']
            
        # 根据难度调整伤害和速度
        damage = enemy_config['base_damage'] + (self.difficulty * 2)
        speed = enemy_config['base_speed'] + (self.difficulty * 10)
        
        # 创建敌人实例
        enemy = Enemy(x, y, health, damage, speed)
        enemy.type = enemy_type  # 记录敌人类型
        self.enemies.append(enemy)
        
        return enemy
        
    def update(self, dt, player):
        self.spawn_timer += dt
        
        # 根据难度生成敌人
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.random_spawn_enemy(player)
            
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
        """在玩家周围随机位置生成随机类型的敌人"""
        # 在玩家周围的屏幕外随机位置生成敌人
        spawn_distance = 600  # 生成距离
        
        # 随机角度
        angle = random.uniform(0, 2 * math.pi)
        
        # 计算生成位置（世界坐标系）
        x = player.world_x + spawn_distance * math.cos(angle)
        y = player.world_y + spawn_distance * math.sin(angle)
        
        # 随机选择敌人类型
        enemy_type = random.choice(list(self.enemy_types.keys()))
        
        # 生成敌人
        self.spawn_enemy(enemy_type, x, y) 