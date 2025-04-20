import pygame
import math
import random
from ...resource_manager import resource_manager
from ..weapon import Weapon
from ..weapon_stats import WeaponStatType, WeaponStatsDict

class FrostExplosionEffect(pygame.sprite.Sprite):
    """冰霜新星爆炸特效"""
    def __init__(self, x, y, radius):
        super().__init__()
        self.world_x = x
        self.world_y = y
        self.radius = radius
        
        # 使用资源管理器的spritesheet和animation功能
        spritesheet = resource_manager.load_spritesheet('frost_explosion', 'images/effects/explosion_64x64.png')
        
        # 创建爆炸动画帧，使用第三行 (row=2)
        animation = resource_manager.create_animation(
            'frost_explosion_anim', spritesheet, 
            frame_width=64, frame_height=64,
            frame_count=8, row=2,
            frame_duration=0.033
        )
        
        self.frames = animation.frames
        self.total_frames = len(self.frames)
        self.animation_speed = animation.frame_duration
        
        self.current_frame = 0
        self.image = pygame.transform.scale(self.frames[0], (128, 128))
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        # 动画控制
        self.animation_timer = 0
    
    def update(self, dt):
        # 更新动画
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                # 动画结束，移除特效
                self.kill()
                return
            
            # 更新当前帧
            self.image = self.frames[self.current_frame]
            self.image = pygame.transform.scale(self.image, (128, 128))
            self.rect = self.image.get_rect(center=(int(self.world_x), int(self.world_y)))
    
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 渲染爆炸效果
        screen.blit(self.image, (screen_x - self.image.get_width() // 2, 
                                 screen_y - self.image.get_height() // 2))

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
        self.explosion_radius = stats.get(WeaponStatType.EXPLOSION_RADIUS, 50)
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

    def on_collision(self, enemy, enemies=None):
        """
        当冰霜新星与敌人碰撞时调用此方法，触发爆炸效果
        
        Args:
            enemy: 被击中的敌人
            enemies: 游戏中的所有敌人列表
        
        Returns:
            bool: 始终返回True，因为冰霜新星碰撞后总是需要销毁
        """
        # 触发爆炸
        self.explode(enemy, enemies)
        return True
        
    def explode(self, target_enemy, enemies=None):
        """
        冰霜新星爆炸，对范围内的敌人造成伤害和减速效果
        
        Args:
            target_enemy: 冰霜新星碰撞的目标敌人或爆炸位置
            enemies: 游戏中的敌人列表
        """
        # 确定爆炸中心点
        if hasattr(target_enemy, 'rect'):
            # 如果是敌人对象，使用敌人的中心点
            explosion_x = target_enemy.rect.centerx
            explosion_y = target_enemy.rect.centery
        else:
            # 如果是坐标元组或其他，直接使用当前位置
            explosion_x = self.world_x
            explosion_y = self.world_y
        
        # 创建爆炸特效
        if hasattr(self, 'effects_group') and self.effects_group is not None:
            explosion = FrostExplosionEffect(explosion_x, explosion_y, self.explosion_radius)
            self.effects_group.add(explosion)
        
        # 如果有敌人列表，对范围内敌人造成伤害和减速效果
        if enemies:
            # 创建可能受影响的敌人列表（预筛选）
            potential_targets = []
            for enemy in enemies:
                # 先做一个简单的矩形检测，快速排除明显不在范围内的敌人
                if (abs(enemy.rect.centerx - explosion_x) <= self.explosion_radius + enemy.rect.width // 2 and
                    abs(enemy.rect.centery - explosion_y) <= self.explosion_radius + enemy.rect.height // 2):
                    potential_targets.append(enemy)
            
            # 只对可能受影响的敌人进行精确的圆形范围检测
            for enemy in potential_targets:
                # 计算与敌人的距离
                dx = enemy.rect.centerx - explosion_x
                dy = enemy.rect.centery - explosion_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # 如果在爆炸范围内，造成伤害和减速
                if distance <= self.explosion_radius:
                    # 目标敌人受100%伤害，爆炸范围内敌人受50%伤害
                    damage_multiplier = 1.0 if enemy is target_enemy else 0.5
                    actual_damage = int(self.damage * damage_multiplier)
                    
                    # 造成伤害
                    enemy.take_damage(actual_damage)
                    
                    # 应用减速效果 - 所有被爆炸影响的敌人都会被减速
                    if hasattr(enemy, 'apply_slow_effect'):
                        enemy.apply_slow_effect(self.slow_amount, self.slow_duration)
        
        # 播放爆炸音效
        try:
            resource_manager.play_sound('frost_nova_explode')
        except Exception as e:
            # 在测试环境中可能没有音效资源，忽略错误
            print(f"Warning: Could not play frost explosion sound: {e}")
        
        # 销毁冰霜新星
        self.kill()

class FrostNova(Weapon):
    def __init__(self, player):
        super().__init__(player, 'frost_nova')
        
        # 加载音效
        try:
            resource_manager.load_sound('frost_nova_cast', 'sounds/weapons/frost_nova_cast.wav')
            resource_manager.load_sound('frost_nova_explode', 'sounds/weapons/frost_nova_explode.wav')
        except Exception as e:
            # 在测试环境中可能没有音效资源，忽略错误
            print(f"Warning: Could not load frost nova explosion sound: {e}")
        
        # 特效组 - 用于存放爆炸效果
        self.effects = pygame.sprite.Group()
        
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
        
        # 更新爆炸特效
        self.effects.update(dt)
        
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
        # 设置特效组，用于后续添加爆炸效果
        nova.effects_group = self.effects
        self.projectiles.add(nova)
        return nova  # 返回创建的投射物
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有冰霜新星
        for nova in self.projectiles:
            nova.render(screen, camera_x, camera_y)
            
        # 渲染所有爆炸特效
        for effect in self.effects:
            effect.render(screen, camera_x, camera_y) 