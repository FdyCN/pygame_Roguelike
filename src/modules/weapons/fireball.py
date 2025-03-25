import pygame
import math
from ..resource_manager import resource_manager
from .weapon import Weapon

class FireballProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_x, direction_y, stats):
        super().__init__()
        self.image = resource_manager.load_image('weapon_fireball', 'images/weapons/fireball.png')
        # 根据方向旋转图像
        angle = math.degrees(math.atan2(-direction_y, direction_x))
        self.image = pygame.transform.rotate(self.image, -angle)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 位置信息
        self.world_x = float(x)
        self.world_y = float(y)
        
        # 投射物属性
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.damage = stats.get('damage', 30)
        self.speed = stats.get('projectile_speed', 300)
        self.explosion_radius = stats.get('explosion_radius', 50)
        self.burn_damage = stats.get('burn_damage', 5)
        self.burn_duration = stats.get('burn_duration', 3.0)
        
        # 存活时间
        self.lifetime = stats.get('lifetime', 2.0)
        
        # 动画效果
        self.scale = 1.0
        self.pulse_time = 0
        self.pulse_duration = 0.5
        
    def update(self, dt):
        # 更新位置
        self.world_x += self.direction_x * self.speed * dt
        self.world_y += self.direction_y * self.speed * dt
        self.rect.center = (self.world_x, self.world_y)
        
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
        self.image = resource_manager.load_image('weapon_fireball', 'images/weapons/fireball.png')
        self.rect = self.image.get_rect()
        
        # 投射物列表
        self.projectiles = pygame.sprite.Group()
        
        # 加载音效
        resource_manager.load_sound('fireball_cast', 'sounds/weapons/fireball_cast.wav')
        resource_manager.load_sound('fireball_explode', 'sounds/weapons/fireball_explode.wav')
        
    def update(self, dt):
        super().update(dt)
        
        # 检查是否可以施放火球
        if self.can_attack():
            self.attack_timer = 0
            self.cast_fireballs()
            
        # 更新所有火球
        self.projectiles.update(dt)
        
    def cast_fireballs(self):
        """施放火球"""
        direction_x, direction_y = self.get_player_direction()
        fireball_count = int(self.current_stats['fireballs_per_cast'])
        
        if fireball_count > 1:
            # 计算扇形分布
            spread_angle = self.current_stats['spread_angle']
            angle_step = spread_angle / (fireball_count - 1)
            base_angle = math.degrees(math.atan2(-direction_y, direction_x))
            start_angle = base_angle - spread_angle / 2
            
            for i in range(fireball_count):
                current_angle = math.radians(start_angle + angle_step * i)
                fireball_dir_x = math.cos(current_angle)
                fireball_dir_y = -math.sin(current_angle)
                self._cast_single_fireball(fireball_dir_x, fireball_dir_y)
        else:
            # 单个火球直接施放
            self._cast_single_fireball(direction_x, direction_y)
            
        # 播放施法音效
        resource_manager.play_sound('fireball_cast')
        
    def _cast_single_fireball(self, direction_x, direction_y):
        """施放单个火球"""
        fireball = FireballProjectile(
            self.player.world_x,
            self.player.world_y,
            direction_x,
            direction_y,
            self.current_stats
        )
        self.projectiles.add(fireball)
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有火球
        for fireball in self.projectiles:
            fireball.render(screen, camera_x, camera_y) 