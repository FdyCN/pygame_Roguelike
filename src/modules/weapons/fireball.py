import pygame
import math
from ..resource_manager import resource_manager
from .weapon import Weapon

class FireballProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target, stats):
        super().__init__()
        # 加载基础图像
        self.base_image = resource_manager.load_image('weapon_fireball', 'images/weapons/fireball_32x32.png')
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
        self.damage = stats.get('damage', 30)
        self.speed = stats.get('projectile_speed', 300)
        
        # 初始化方向
        self.direction_x = 0
        self.direction_y = 0
        
        self.explosion_radius = stats.get('explosion_radius', 50)
        self.burn_damage = stats.get('burn_damage', 5)
        self.burn_duration = stats.get('burn_duration', 3.0)
        
        # 存活时间
        self.lifetime = stats.get('lifetime', 2.0)
        
        # 动画效果
        self.scale = 1.0
        self.pulse_time = 0
        self.pulse_duration = 0.5
        
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
                # 更新方向向量
                self.direction_x = dx / distance
                self.direction_y = dy / distance
                
                # 更新图像旋转
                angle = math.degrees(math.atan2(-dy, dx))
                self.image = pygame.transform.rotate(self.base_image, -angle)
                # 保持旋转后的图像中心点不变
                new_rect = self.image.get_rect()
                new_rect.center = self.rect.center
                self.rect = new_rect
        
    def update(self, dt):
        # 更新方向（追踪目标）
        self._update_direction()
        
        # 更新位置
        self.world_x += self.direction_x * self.speed * dt
        self.world_y += self.direction_y * self.speed * dt
        
        # 更新碰撞盒位置
        self.rect.centerx = self.world_x
        self.rect.centery = self.world_y
        
        # 更新动画
        self.pulse_time = (self.pulse_time + dt) % self.pulse_duration
        self.scale = 1.0 + 0.2 * math.sin(self.pulse_time * 2 * math.pi / self.pulse_duration)
        
        # 更新存活时间
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.explode()
            
    def explode(self):
        # TODO: 创建爆炸效果
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

class Fireball(Weapon):
    def __init__(self, player):
        # 定义基础属性
        base_stats = {
            'damage': 30,
            'attack_speed': 0.8,
            'projectile_speed': 300,
            'explosion_radius': 50,
            'burn_damage': 5,
            'burn_duration': 3.0,
            'lifetime': 2.0,
            'fireballs_per_cast': 1,
            'spread_angle': 20
        }
        
        super().__init__(player, 'fireball', base_stats)
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_fireball', 'images/weapons/fireball_32x32.png')
        self.rect = self.image.get_rect()
        
        # 投射物列表
        self.projectiles = pygame.sprite.Group()
        
        # 加载音效
        resource_manager.load_sound('fireball_cast', 'sounds/weapons/fireball_cast.wav')
        resource_manager.load_sound('fireball_explode', 'sounds/weapons/fireball_explode.wav')
        
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
        
        # 检查是否可以施放火球
        if self.can_attack():
            self.attack_timer = 0
            self.cast_fireballs(enemies)
            
        # 更新所有火球
        self.projectiles.update(dt)
        
    def cast_fireballs(self, enemies):
        """施放火球"""
        target = self.find_nearest_enemy(enemies)
        if not target:
            return
            
        fireball_count = int(self.current_stats['fireballs_per_cast'])
        
        if fireball_count > 1:
            # 计算扇形分布
            spread_angle = self.current_stats['spread_angle']
            angle_step = spread_angle / (fireball_count - 1)
            base_angle = math.degrees(math.atan2(
                target.rect.y - self.player.world_y,
                target.rect.x - self.player.world_x
            ))
            start_angle = base_angle - spread_angle / 2
            
            for i in range(fireball_count):
                self._cast_single_fireball(target)
        else:
            # 单个火球直接施放
            self._cast_single_fireball(target)
            
        # 播放施法音效
        resource_manager.play_sound('fireball_cast')
        
    def _cast_single_fireball(self, target):
        """施放单个火球"""
        fireball = FireballProjectile(
            self.player.world_x,
            self.player.world_y,
            target,
            self.current_stats
        )
        self.projectiles.add(fireball)
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有火球
        for fireball in self.projectiles:
            fireball.render(screen, camera_x, camera_y) 