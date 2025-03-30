import pygame
import math
from ..resource_manager import resource_manager
from .weapon import Weapon
from .weapon_stats import WeaponStatType, WeaponStatsDict

class ThrownKnife(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_x, direction_y, stats):
        super().__init__()
        self.image = resource_manager.load_image('weapon_knife', 'images/weapons/knife_32x32.png')
        
        # 首先将图片旋转45度，使刀柄朝左，刀尖朝右
        base_image = pygame.transform.rotate(self.image, -45)
        
        # 然后根据飞行方向旋转图像
        # 计算飞行方向的角度（以水平向右为0度）
        angle = math.degrees(math.atan2(direction_y, direction_x))
        self.image = pygame.transform.rotate(base_image, -angle)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 起始位置和当前位置（世界坐标）
        self.start_x = float(x)
        self.start_y = float(y)
        self.world_x = float(x)
        self.world_y = float(y)
        
        # 投掷属性
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.damage = stats.get('damage', 20)
        self.speed = stats.get('projectile_speed', 400)
        
        # 投掷动画相关
        # 目前暂时没有用到，感觉往后也不会就用到。。。
        self.throw_time = 0
        self.throw_duration = 0.15
        self.throw_progress = 0
        
        # 存活时间
        self.lifetime = stats.get('lifetime', 3.0)
        
        # 初始化命中计数
        self.hit_count = 0
        
    def update(self, dt):
        # 更新投掷动画进度
        # FIXME: 看起来多此一举，加了缩放反而感觉卡顿。
        if False: # self.throw_time < self.throw_duration:
            self.throw_time += dt
            self.throw_progress = min(1.0, self.throw_time / self.throw_duration)
            
            # 使用缓动函数使动画更平滑
            progress = self._ease_out_quad(self.throw_progress)
            
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
        self.rect.centerx = round(self.world_x)
        self.rect.centery = round(self.world_y)
        
        # 更新存活时间
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            
    def _ease_out_quad(self, t):
        """
        缓动函数，使动画更自然
        t: 0-1之间的值
        """
        return -t * (t - 2)
            
    def render(self, screen, camera_x, camera_y):
        # 计算屏幕位置（相对于相机的偏移）
        screen_x = self.world_x - camera_x + screen.get_width() // 2
        screen_y = self.world_y - camera_y + screen.get_height() // 2
        
        # 根据投掷进度缩放图像
        # FIXME: 这里会让小刀变大，感觉很奇怪。 和update中的平滑同时关闭，感觉会好一些。
        if False: # self.throw_time < self.throw_duration:
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
        self.base_stats: WeaponStatsDict = {
            WeaponStatType.DAMAGE: 20,
            WeaponStatType.ATTACK_SPEED: 1.0,
            WeaponStatType.PROJECTILE_SPEED: 400,
            WeaponStatType.CAN_PENETRATE: False,
            WeaponStatType.MAX_PENETRATION: 1,
            WeaponStatType.PENETRATION_DAMAGE_REDUCTION: 0.2,
            WeaponStatType.PROJECTILES_PER_CAST: 1,
            WeaponStatType.SPREAD_ANGLE: 0,
            WeaponStatType.LIFETIME: 3.0
        }
        self.current_stats = self.base_stats.copy()
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_knife', 'images/weapons/knife_32x32.png')
        self.rect = self.image.get_rect()
        
        # 应用玩家的攻击力加成
        self._apply_player_attack_power()

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
