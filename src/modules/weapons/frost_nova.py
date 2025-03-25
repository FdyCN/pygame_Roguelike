import pygame
import math
from ..resource_manager import resource_manager
from .weapon import Weapon

class FrostNovaEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, stats):
        super().__init__()
        self.image = resource_manager.load_image('weapon_frost_nova', 'images/weapons/nova_32x32.png')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 位置信息
        self.world_x = float(x)
        self.world_y = float(y)
        
        # 效果属性
        self.damage = stats.get('damage', 25)
        self.slow_amount = stats.get('slow_amount', 0.5)  # 减速效果（百分比）
        self.slow_duration = stats.get('slow_duration', 2.0)  # 减速持续时间
        self.radius = stats.get('radius', 100)  # 效果范围
        
        # 动画效果
        self.lifetime = 0.5  # 动画持续时间
        self.current_time = 0
        self.alpha = 255  # 透明度
        self.scale = 0.1  # 初始大小
        
        # 创建一个透明的surface用于特效
        self.effect_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        
    def update(self, dt):
        self.current_time += dt
        progress = self.current_time / self.lifetime
        
        if progress >= 1:
            self.kill()
            return
            
        # 更新缩放和透明度
        self.scale = progress
        self.alpha = int(255 * (1 - progress))
        
        # 更新特效surface
        self.effect_surface.fill((0, 0, 0, 0))
        scaled_size = (int(self.radius * 2 * self.scale), int(self.radius * 2 * self.scale))
        scaled_image = pygame.transform.scale(self.image, scaled_size)
        
        # 设置透明度
        scaled_image.set_alpha(self.alpha)
        
        # 在surface中心绘制
        pos_x = self.radius - scaled_size[0] // 2
        pos_y = self.radius - scaled_size[1] // 2
        self.effect_surface.blit(scaled_image, (pos_x, pos_y))
        
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置
        screen_x = self.world_x - camera_x + screen.get_width() // 2 - self.radius
        screen_y = self.world_y - camera_y + screen.get_height() // 2 - self.radius
        
        # 绘制特效
        screen.blit(self.effect_surface, (screen_x, screen_y))
        
class FrostNova(Weapon):
    def __init__(self, player):
        # 定义基础属性
        base_stats = {
            'damage': 25,
            'attack_speed': 0.5,
            'radius': 100,
            'slow_amount': 0.5,
            'slow_duration': 2.0,
            'nova_count': 1  # 同时释放的新星数量
        }
        
        super().__init__(player, 'frost_nova', base_stats)
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_frost_nova', 'images/weapons/frost_nova.png')
        self.rect = self.image.get_rect()
        
        # 特效列表
        self.effects = pygame.sprite.Group()
        
        # 加载音效
        resource_manager.load_sound('frost_nova_cast', 'sounds/weapons/frost_nova_cast.wav')
        
    def update(self, dt):
        super().update(dt)
        
        # 检查是否可以释放冰霜新星
        if self.can_attack():
            self.attack_timer = 0
            self.cast_frost_nova()
            
        # 更新所有特效
        self.effects.update(dt)
        
    def cast_frost_nova(self):
        """释放冰霜新星"""
        nova_count = int(self.current_stats['nova_count'])
        
        # 在玩家周围创建多个新星
        for i in range(nova_count):
            # 如果有多个新星，在玩家周围随机位置生成
            if nova_count > 1:
                offset_angle = (i / nova_count) * 2 * math.pi
                offset_distance = self.current_stats['radius'] * 0.5
                offset_x = math.cos(offset_angle) * offset_distance
                offset_y = math.sin(offset_angle) * offset_distance
                x = self.player.world_x + offset_x
                y = self.player.world_y + offset_y
            else:
                x = self.player.world_x
                y = self.player.world_y
                
            effect = FrostNovaEffect(x, y, self.current_stats)
            self.effects.add(effect)
            
        # 播放施法音效
        resource_manager.play_sound('frost_nova_cast')
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有特效
        for effect in self.effects:
            effect.render(screen, camera_x, camera_y) 