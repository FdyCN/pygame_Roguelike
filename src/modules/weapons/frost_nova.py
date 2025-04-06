import pygame
import math
import random
from ..resource_manager import resource_manager
from .weapon import Weapon
from .weapon_stats import WeaponStatType, WeaponStatsDict

class FrostNovaProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, stats):
        super().__init__()
        # 加载基础图像
        self.base_image = resource_manager.load_image('weapon_frost_nova', 'images/weapons/nova_32x32.png')
        self.image = self.base_image
        self.rect = self.image.get_rect()
        
        # 位置信息（世界坐标）
        self.world_x = float(x)
        self.world_y = float(y)
        self.rect.centerx = self.world_x
        self.rect.centery = self.world_y
        
        # 目标信息
        self.target = target
        
        # 投射物属性
        self.damage = stats.get(WeaponStatType.DAMAGE, 25)
        self.speed = float(stats.get(WeaponStatType.PROJECTILE_SPEED, 250))  # 确保速度是浮点数
        
        # 初始化方向
        self.direction_x = 0.0
        self.direction_y = 0.0
        
        # 冰霜特有属性
        self.slow_amount = stats.get(WeaponStatType.SLOW_PERCENT, 50) / 100  # 转换为百分比
        self.slow_duration = stats.get(WeaponStatType.FREEZE_DURATION, 2.0)
        
        # 存活时间
        self.lifetime = stats.get(WeaponStatType.LIFETIME, 2.0)
        
        # 动画效果
        self.scale = 1.0
        self.pulse_time = 0
        self.pulse_duration = 0.5

        self.hit_count = 0  # 命中敌人计数
        
        # 初始方向
        self._update_direction()
        
    def _update_direction(self):
        """更新朝向目标的方向"""
        if self.target and self.target.alive():
            # 使用世界坐标计算方向
            dx = self.target.rect.centerx - self.world_x
            dy = self.target.rect.centery - self.world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                # 更新方向向量（确保是标准化的单位向量）
                self.direction_x = dx / distance
                self.direction_y = dy / distance
                
                # 更新图像旋转
                angle = math.degrees(math.atan2(-dy, dx))  # 注意：pygame的y轴是向下的，所以需要取负
                self.image = pygame.transform.rotate(self.base_image, angle)
                # 保持旋转后的图像中心点不变
                new_rect = self.image.get_rect()
                new_rect.center = self.rect.center
                self.rect = new_rect
        
    def update(self, dt):
        # 更新方向（追踪目标）
        self._update_direction()
        
        # 更新位置（使用浮点数计算）
        self.world_x += self.direction_x * self.speed * dt
        self.world_y += self.direction_y * self.speed * dt
        
        # 更新碰撞盒位置
        self.rect.centerx = round(self.world_x)
        self.rect.centery = round(self.world_y)
        
        # 更新动画
        self.pulse_time = (self.pulse_time + dt) % self.pulse_duration
        self.scale = 1.0 + 0.2 * math.sin(self.pulse_time * 2 * math.pi / self.pulse_duration)
        
        # 更新存活时间
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 缩放图像
        scaled_size = (int(self.image.get_width() * self.scale),
                      int(self.image.get_height() * self.scale))
        scaled_image = pygame.transform.scale(self.image, scaled_size)
        
        # 调整绘制位置以保持中心点不变
        draw_x = screen_x - scaled_image.get_width() / 2
        draw_y = screen_y - scaled_image.get_height() / 2
        screen.blit(scaled_image, (draw_x, draw_y))

    def apply_slow_effect(self, enemy, slow_amount=None):
        """对敌人应用减速效果
        
        参数:
            enemy (Enemy): 要减速的敌人对象
            slow_amount (float, optional): 减速系数，范围[0-1]。如果未提供，使用projectile的slow_amount。
        """
        if slow_amount is None:
            slow_amount = self.slow_amount
        
        # 保存敌人原始速度（如果尚未保存）
        if not hasattr(enemy, 'original_speed') or enemy.original_speed is None:
            enemy.original_speed = enemy.speed
            
        # 应用减速效果
        enemy.speed = enemy.original_speed * (1 - slow_amount)
        
        # 设置敌人的减速状态和持续时间
        enemy.is_slowed = True
        enemy.slow_timer = self.slow_duration
        
    def calculate_direction(self):
        """计算朝向目标的方向向量"""
        if self.target:
            # 计算到目标的方向
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            
            # 标准化方向向量
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.direction_x = dx / distance
                self.direction_y = dy / distance
            else:
                # 目标与投射物在同一位置，选择随机方向
                self.direction_x = random.uniform(-1, 1)
                self.direction_y = random.uniform(-1, 1)
                # 标准化随机方向
                random_dir_length = math.sqrt(self.direction_x**2 + self.direction_y**2)
                self.direction_x /= random_dir_length
                self.direction_y /= random_dir_length

class FrostNova(Weapon):
    def __init__(self, player):
        super().__init__(player, 'frost_nova')
        
        # 加载音效
        resource_manager.load_sound('frost_nova_cast', 'sounds/weapons/frost_nova_cast.wav')
        
    def find_nearest_enemy(self, enemies):
        """寻找最近的敌人"""
        nearest_enemy = None
        min_distance = float('inf')
        
        for enemy in enemies:
            dx = enemy.rect.x - self.player.world_x
            dy = enemy.rect.y - self.player.world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
                
        return nearest_enemy
        
    def update(self, dt, enemies):
        super().update(dt)
        
        # 检查是否可以施放冰霜新星
        if self.can_attack():
            self.attack_timer = 0
            self.cast_novas(enemies)
            
        # 更新所有冰霜新星
        self.projectiles.update(dt)
        
    def cast_novas(self, enemies):
        """施放冰霜新星"""
        target = self.find_nearest_enemy(enemies)
        if not target:
            return
            
        nova_count = int(self.current_stats.get(WeaponStatType.PROJECTILES_PER_CAST, 1))
        
        if nova_count > 1:
            # 计算扇形分布
            spread_angle = self.current_stats.get(WeaponStatType.SPREAD_ANGLE, 20)
            angle_step = spread_angle / (nova_count - 1)
            base_angle = math.degrees(math.atan2(
                target.world_y - self.player.world_y,
                target.world_x - self.player.world_x
            ))
            start_angle = base_angle - spread_angle / 2
            
            for i in range(nova_count):
                self._cast_single_nova(target)
        else:
            # 单个新星直接施放
            self._cast_single_nova(target)
            
        # 播放施法音效
        resource_manager.play_sound('frost_nova_cast')
        
    def _cast_single_nova(self, target):
        """施放单个冰霜新星"""
        nova = FrostNovaProjectile(
            self.player.world_x,
            self.player.world_y,
            target,
            self.current_stats
        )
        self.projectiles.add(nova)
        return nova  # 返回创建的投射物
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有冰霜新星
        for nova in self.projectiles:
            nova.render(screen, camera_x, camera_y) 