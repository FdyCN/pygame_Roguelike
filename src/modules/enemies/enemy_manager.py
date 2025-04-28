import pygame
import random
import math
from .types import Ghost, Radish, Bat, Slime

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 1.0  # 每秒生成一个敌人
        self.difficulty = "normal"  # 默认难度为normal
        self.difficulty_level = 1   # 难度等级，随游戏时间增长
        self.game_time = 0  # 游戏进行时间
        self.bat_spawn_timer = 0  # 蝙蝠生成计时器
        
        # 地图边界相关
        self.map_boundaries = None  # (min_x, min_y, max_x, max_y)
        
    def set_map_boundaries(self, min_x, min_y, max_x, max_y):
        """设置地图边界
        
        Args:
            min_x: 最小X坐标
            min_y: 最小Y坐标
            max_x: 最大X坐标
            max_y: 最大Y坐标
        """
        self.map_boundaries = (min_x, min_y, max_x, max_y)
        
    def spawn_enemy(self, enemy_type, x, y, health=None):
        """在指定位置生成指定类型和生命值的敌人
        
        Args:
            enemy_type: 敌人类型 ('ghost', 'radish', 'bat', 'slime')
            x: 世界坐标系中的x坐标
            y: 世界坐标系中的y坐标
            health: 指定生命值，如果为None则使用该类型的默认生命值
            
        Returns:
            Enemy: 生成的敌人实例
        """
        # 根据类型创建对应的敌人实例
        enemy = None
        
        # 使用新的构造函数，传递敌人类型、难度和等级
        if enemy_type == 'ghost':
            enemy = Ghost(x, y, enemy_type, self.difficulty, self.difficulty_level)
        elif enemy_type == 'radish':
            enemy = Radish(x, y, enemy_type, self.difficulty, self.difficulty_level)
        elif enemy_type == 'bat':
            enemy = Bat(x, y, enemy_type, self.difficulty, self.difficulty_level)
        elif enemy_type == 'slime':
            enemy = Slime(x, y, enemy_type, self.difficulty, self.difficulty_level)
            
        # 如果指定了生命值，覆盖配置的生命值
        if enemy and health is not None:
            enemy.health = health
            enemy.max_health = health
            
        if enemy:
            self.enemies.append(enemy)
            
        return enemy
        
    def update(self, dt, player):
        self.game_time += dt
        self.spawn_timer += dt
        
        # 更新难度等级（根据游戏时间）
        self.difficulty_level = max(1, int(self.game_time // 60) + 1)  # 每60秒提升一级
        
        # 根据时间和玩家等级生成敌人
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.random_spawn_enemy(player)
            
        # 如果玩家等级达到5级，更新蝙蝠生成计时器
        if player.level >= 1:
            # 如果是刚达到5级,立即生成一只蝙蝠
            if self.bat_spawn_timer == 0:
                self.spawn_bat(player)
                self.bat_spawn_timer = 0.1  # 设置一个很小的值,避免重复触发初始生成
            
            self.bat_spawn_timer += dt
            if self.bat_spawn_timer >= 60:  # 每60秒生成一只蝙蝠
                self.bat_spawn_timer = 0.1  # 重置为0.1而不是0
                self.spawn_bat(player)
            
        # 更新所有敌人
        for enemy in self.enemies[:]:  # 使用切片创建副本以避免在迭代时修改列表
            enemy.update(dt, player)
            
            # 检查敌人是否已死亡（包括被燃烧伤害杀死的）
            if not enemy.alive():
                try:
                    self.enemies.remove(enemy)
                    # 注意：在这里我们不再播放死亡音效，因为在enemy.py中已经播放
                except ValueError:
                    # 如果敌人已经被移除，忽略错误
                    pass
            
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
        """在玩家周围随机位置生成敌人，确保在地图边界内"""
        # 在玩家周围的随机位置生成敌人
        spawn_distance = 600  # 生成距离
        
        # 尝试生成位置，最多尝试10次以找到在边界内的位置
        for _ in range(10):
            # 随机角度
            angle = random.uniform(0, 2 * math.pi)
            
            # 计算生成位置（世界坐标系）
            x = player.world_x + spawn_distance * math.cos(angle)
            y = player.world_y + spawn_distance * math.sin(angle)
            
            # 如果有地图边界限制，确保敌人在边界内生成
            if self.map_boundaries:
                min_x, min_y, max_x, max_y = self.map_boundaries
                
                # 检查生成位置是否在边界内
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    break  # 位置有效，跳出循环
                
                # 如果位置无效，将坐标限制在边界内
                x = max(min_x, min(x, max_x))
                y = max(min_y, min(y, max_y))
                break  # 使用修正后的位置
        
        # 根据游戏时间决定生成什么类型的敌人
        if self.game_time < 10:  # 游戏开始10秒内
            self.spawn_enemy('slime', x, y)
        else:  # 10秒后可以生成幽灵和萝卜
            enemy_type = random.choice(['ghost', 'radish', 'slime'])
            self.spawn_enemy(enemy_type, x, y)
            
    def set_difficulty(self, difficulty):
        """设置游戏难度
        
        Args:
            difficulty (str): 难度级别 ('easy', 'normal', 'hard', 'nightmare')
        """
        self.difficulty = difficulty
            
    def spawn_bat(self, player):
        """在玩家周围生成一个蝙蝠，确保在地图边界内"""
        spawn_distance = 600
        
        # 尝试生成位置，最多尝试10次以找到在边界内的位置
        for _ in range(10):
            angle = random.uniform(0, 2 * math.pi)
            x = player.world_x + spawn_distance * math.cos(angle)
            y = player.world_y + spawn_distance * math.sin(angle)
            
            # 如果有地图边界限制，确保蝙蝠在边界内生成
            if self.map_boundaries:
                min_x, min_y, max_x, max_y = self.map_boundaries
                
                # 检查生成位置是否在边界内
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    break  # 位置有效，跳出循环
                
                # 如果位置无效，将坐标限制在边界内
                x = max(min_x, min(x, max_x))
                y = max(min_y, min(y, max_y))
                break  # 使用修正后的位置
        
        self.spawn_enemy('bat', x, y) 