import pygame
import math
from ..resource_manager import resource_manager
from .weapon import Weapon

class FrostNovaEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, target, stats):
        super().__init__()
        self.image = resource_manager.load_image('weapon_frost_nova', 'images/weapons/nova_32x32.png')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 位置信息
        self.world_x = float(x)
        self.world_y = float(y)
        
        # 目标信息
        self.target = target
        
        # 效果属性
        self.damage = stats.get('damage', 25)
        self.slow_amount = stats.get('slow_amount', 0.5)  # 减速效果（百分比）
        self.slow_duration = stats.get('slow_duration', 2.0)  # 减速持续时间
        self.speed = stats.get('projectile_speed', 250)  # 移动速度
        
        # 动画效果
        self.lifetime = stats.get('lifetime', 2.0)  # 存活时间
        self.current_time = 0
        self.alpha = 255  # 透明度
        self.scale = 0.5  # 初始大小
        
        # 初始化方向
        self.direction_x = 0
        self.direction_y = 0
        self._update_direction()
        
    def _update_direction(self):
        """更新朝向目标的方向"""
        if self.target and self.target.alive():
            dx = self.target.rect.x - self.world_x
            dy = self.target.rect.y - self.world_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                self.direction_x = dx / distance
                self.direction_y = dy / distance
        
    def update(self, dt):
        self.current_time += dt
        
        if self.current_time >= self.lifetime:
            self.kill()
            return
            
        # 更新方向和位置
        self._update_direction()
        self.world_x += self.direction_x * self.speed * dt
        self.world_y += self.direction_y * self.speed * dt
        self.rect.center = (self.world_x, self.world_y)
        
        # 更新透明度
        self.alpha = int(255 * (1 - self.current_time / self.lifetime))
        
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置
        screen_x = self.world_x - camera_x + screen.get_width() // 2 - self.rect.width // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2 - self.rect.height // 2
        
        # 创建一个临时surface用于设置透明度
        temp_surface = self.image.copy()
        temp_surface.set_alpha(self.alpha)
        
        # 绘制特效
        screen.blit(temp_surface, (screen_x, screen_y))

class FrostNova(Weapon):
    def __init__(self, player):
        # 定义基础属性
        base_stats = {
            'damage': 25, 
            'attack_speed': 0.5,
            'projectile_speed': 250,
            'slow_amount': 0.5,
            'slow_duration': 2.0,
            'lifetime': 2.0,
            'nova_count': 1  # 同时释放的新星数量
        }
        
        super().__init__(player, 'frost_nova', base_stats)
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_frost_nova', 'images/weapons/nova_32x32.png')
        self.rect = self.image.get_rect()
        
        # 特效列表
        self.effects = pygame.sprite.Group()
        
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
        
        # 检查是否可以释放冰霜新星
        if self.can_attack():
            self.attack_timer = 0
            self.cast_frost_nova(enemies)
            
        # 更新所有特效
        self.effects.update(dt)
        
    def cast_frost_nova(self, enemies):
        """释放冰霜新星"""
        target = self.find_nearest_enemy(enemies)
        if not target:
            return
            
        nova_count = int(self.current_stats['nova_count'])
        
        # 在玩家周围创建多个新星
        for i in range(nova_count):
            # 如果有多个新星，在玩家周围随机位置生成
            if nova_count > 1:
                offset_angle = (i / nova_count) * 2 * math.pi
                offset_distance = 30  # 固定偏移距离
                offset_x = math.cos(offset_angle) * offset_distance
                offset_y = math.sin(offset_angle) * offset_distance
                x = self.player.world_x + offset_x
                y = self.player.world_y + offset_y
            else:
                x = self.player.world_x
                y = self.player.world_y
                
            effect = FrostNovaEffect(x, y, target, self.current_stats)
            self.effects.add(effect)
            
        # 播放施法音效
        resource_manager.play_sound('frost_nova_cast')
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有特效
        for effect in self.effects:
            effect.render(screen, camera_x, camera_y) 