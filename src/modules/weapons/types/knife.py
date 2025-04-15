import pygame
import math
from ...resource_manager import resource_manager
from ..weapon import Weapon
from ..weapon_stats import WeaponStatType, WeaponStatsDict
from ..weapons_data import get_weapon_base_stats

class ThrownKnife(pygame.sprite.Sprite):
    """飞刀投射物类"""
    
    def __init__(self, x, y, direction_x, direction_y, stats):
        super().__init__()
        # 从资源管理器获取飞刀图像并旋转
        original_image = resource_manager.load_image('weapon_knife', 'images/weapons/knife_32x32.png')
        # 计算需要旋转的角度
        angle = math.degrees(math.atan2(direction_y, direction_x))
        # 原始图片刀尖朝上（-90度），需要调整基础角度
        base_angle = -45
        final_angle = -(angle - base_angle)
        self.image = pygame.transform.rotate(original_image, final_angle)
        self.rect = self.image.get_rect()
        self.rect.center = (int(x), int(y))
        
        # 设置飞刀属性
        self.start_x = float(x)  # 起始x坐标，用于动画
        self.start_y = float(y)  # 起始y坐标，用于动画
        self.world_x = float(x)
        self.world_y = float(y)
        self.direction_x = float(direction_x)
        self.direction_y = float(direction_y)
        self.damage = stats.get(WeaponStatType.DAMAGE, 20)  # 默认伤害20
        self.speed = stats.get(WeaponStatType.PROJECTILE_SPEED, 400)  # 默认速度400
        self.lifetime = stats.get(WeaponStatType.LIFETIME, 3.0)  # 默认生命周期3秒
        
        # 穿透相关属性
        self.can_penetrate = stats.get(WeaponStatType.CAN_PENETRATE, False)
        self.max_penetration = stats.get(WeaponStatType.MAX_PENETRATION, 0)
        self.penetration_damage_reduction = stats.get(WeaponStatType.PENETRATION_DAMAGE_REDUCTION, 0.2)
        self.hit_count = 0  # 命中敌人计数
        
        # 投掷动画相关
        self.throw_duration = 0.1  # 投掷动画持续时间
        self.throw_timer = 0  # 投掷动画计时器
        self.throw_progress = 0  # 投掷动画进度
        
        # 存活时间跟踪
        self.time_alive = 0
        
    def update(self, dt):
        # 更新投掷动画进度
        if self.throw_timer < self.throw_duration:
            self.throw_timer += dt
            progress = min(self.throw_timer / self.throw_duration, 1.0)
            self.throw_progress = progress
            
            # 从玩家位置插值到目标位置
            target_x = self.start_x + self.direction_x * self.speed * self.throw_duration
            target_y = self.start_y + self.direction_y * self.speed * self.throw_duration
            
            self.world_x = self.start_x + (target_x - self.start_x) * progress
            self.world_y = self.start_y + (target_y - self.start_y) * progress
        else:
            # 投掷动画结束后，正常移动
            self.world_x += self.direction_x * self.speed * dt
            self.world_y += self.direction_y * self.speed * dt
        
        # 更新碰撞盒位置
        self.rect.centerx = int(self.world_x)
        self.rect.centery = int(self.world_y)
        
        # 更新存活时间
        self.time_alive += dt
        if self.time_alive >= self.lifetime:
            self.kill()
            
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置（相对于相机的偏移）
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 根据投掷进度缩放图像
        # FIXME: 这里会让小刀变大，感觉很奇怪。 和update中的平滑同时关闭，感觉会好一些。
        if self.throw_timer < self.throw_duration:
            # 在投掷开始时略微放大，然后恢复正常大小
            scale = 1.0 + 0.5 * (1.0 - self.throw_progress)
            scaled_image = pygame.transform.scale(
                self.image,
                (int(self.image.get_width() * scale),
                 int(self.image.get_height() * scale))
            )
            # 调整绘制位置以保持中心点不变
            draw_x = screen_x - scaled_image.get_width() / 2
            draw_y = screen_y - scaled_image.get_height() / 2
            screen.blit(scaled_image, (draw_x, draw_y))
        else:
            # 正常渲染
            screen.blit(self.image, (screen_x - self.rect.width/2, screen_y - self.rect.height/2))

class Knife(Weapon):
    def __init__(self, player):
        super().__init__(player, 'knife')
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_knife', 'images/weapons/knife_32x32.png')
        self.rect = self.image.get_rect()

        # 加载攻击音效
        resource_manager.load_sound('knife_throw', 'sounds/weapons/knife_throw.wav')
        
    def update(self, dt):
        super().update(dt)
        
        # 检查是否可以投掷
        if self.can_attack():
            self.attack_timer = 0
            self.throw_knives()
            
        # 更新已投掷的小刀
        self.projectiles.update(dt)
        
    def throw_knives(self):
        """投掷小刀"""
        direction_x, direction_y = self.get_player_direction()
        knives_count = int(self.current_stats[WeaponStatType.PROJECTILES_PER_CAST])
        
        if knives_count > 1:
            # 计算扇形分布
            spread_angle = self.current_stats[WeaponStatType.SPREAD_ANGLE]
            angle_step = spread_angle / (knives_count - 1)
            base_angle = math.degrees(math.atan2(direction_y, direction_x))
            start_angle = base_angle - spread_angle / 2
            
            for i in range(knives_count):
                current_angle = math.radians(start_angle + angle_step * i)
                knife_dir_x = math.cos(current_angle)
                knife_dir_y = math.sin(current_angle)
                self._throw_single_knife(knife_dir_x, knife_dir_y)
        else:
            # 单个小刀直接投掷
            self._throw_single_knife(direction_x, direction_y)
            
        # 播放投掷音效
        resource_manager.play_sound('knife_throw')
        
    def _throw_single_knife(self, direction_x, direction_y):
        """投掷单个小刀"""
        knife = ThrownKnife(
            self.player.world_x,
            self.player.world_y,
            direction_x,
            direction_y,
            self.current_stats
        )
        self.projectiles.add(knife)
        
    def render(self, screen, camera_x, camera_y):
        # 渲染所有投掷出去的小刀
        for knife in self.projectiles:
            knife.render(screen, camera_x, camera_y)
