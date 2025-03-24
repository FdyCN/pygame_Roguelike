import pygame
import math
from ..resource_manager import resource_manager

class ThrownKnife(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_x, direction_y, damage, speed=400, penetration=True):
        super().__init__()
        self.image = resource_manager.load_image('weapon_knife', 'images/weapons/knife.png')
        # 根据方向旋转图像
        angle = math.degrees(math.atan2(-direction_y, direction_x))
        self.image = pygame.transform.rotate(self.image, -angle)
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
        self.damage = damage
        self.speed = speed
        self.penetration = penetration  # 是否可以穿透
        
        # 投掷动画相关
        self.throw_time = 0
        self.throw_duration = 0.15  # 投掷动画持续时间（秒）
        self.throw_progress = 0  # 投掷进度（0-1）
        
        # 存活时间（3秒后消失）
        self.lifetime = 3.0
        
        # 记录已经击中的敌人
        self.hit_enemies = set()
        
    def can_damage_enemy(self, enemy):
        """检查是否可以对敌人造成伤害"""
        # 如果敌人已经被击中过，且武器不能穿透，返回False
        if enemy in self.hit_enemies:
            return False
        return True
        
    def register_hit(self, enemy):
        """记录对敌人的命中"""
        self.hit_enemies.add(enemy)
        # 如果武器不能穿透，则在击中后销毁
        if not self.penetration:
            self.kill()
        
    def update(self, dt):
        # 更新投掷动画进度
        if self.throw_time < self.throw_duration:
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
        self.rect.centerx = self.world_x
        self.rect.centery = self.world_y
        
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
        if self.throw_time < self.throw_duration:
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

class Knife(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.type = 'knife'
        
        # 加载武器图像
        self.image = resource_manager.load_image('weapon_knife', 'images/weapons/knife.png')
        self.rect = self.image.get_rect()
        
        # 武器属性
        self.level = 1
        self.damage = 20
        self.attack_speed = 1  # 每秒投掷次数
        self.knives_per_throw = 1  # 每次投掷的小刀数量
        
        # 升级属性
        self.upgrade_stats = {
            'damage': {'base': 20, 'increment': 10, 'description': '伤害'},
            'attack_speed': {'base': 1, 'increment': 0.2, 'description': '投掷速度'},
            'knives_per_throw': {'base': 1, 'increment': 1, 'description': '投掷数量'}
        }
        
        # 攻击状态
        self.attack_timer = 0
        self.attack_interval = 1.0 / self.attack_speed
        
        # 投掷的小刀列表
        self.thrown_knives = pygame.sprite.Group()
        
        # 加载攻击音效
        resource_manager.load_sound('knife_throw', 'sounds/weapons/knife_throw.wav')
        
    def upgrade(self, upgrade_type):
        """
        处理武器升级
        upgrade_type: 升级类型（'damage', 'attack_speed', 'knives_per_throw'）
        """
        if upgrade_type in self.upgrade_stats:
            stat = self.upgrade_stats[upgrade_type]
            if upgrade_type == 'damage':
                self.damage += stat['increment']
            elif upgrade_type == 'attack_speed':
                self.attack_speed += stat['increment']
                self.attack_interval = 1.0 / self.attack_speed
            elif upgrade_type == 'knives_per_throw':
                self.knives_per_throw += int(stat['increment'])
            
            self.level += 1
            return True
        return False
        
    def get_upgrade_description(self, upgrade_type):
        """
        获取升级描述
        """
        if upgrade_type in self.upgrade_stats:
            stat = self.upgrade_stats[upgrade_type]
            current_value = getattr(self, upgrade_type)
            if upgrade_type == 'knives_per_throw':
                return f"提升{stat['description']}：{current_value} → {current_value + int(stat['increment'])}"
            return f"提升{stat['description']}：{current_value:.1f} → {current_value + stat['increment']:.1f}"
        return ""
        
    def update(self, dt):
        # 更新投掷计时器
        self.attack_timer += dt
        
        # 获取玩家移动方向
        direction_x = self.player.direction.x
        direction_y = self.player.direction.y
        
        # 如果玩家没有移动，使用玩家朝向
        if direction_x == 0 and direction_y == 0:
            direction_x = 1 if self.player.facing_right else -1
            direction_y = 0
            
        # 标准化方向向量
        length = math.sqrt(direction_x**2 + direction_y**2)
        if length > 0:
            direction_x /= length
            direction_y /= length
        
        # 检查是否可以投掷
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0
            
            # 计算扇形分布的角度
            if self.knives_per_throw > 1:
                angle_spread = 30  # 总扇形角度
                angle_step = angle_spread / (self.knives_per_throw - 1)
                base_angle = math.atan2(direction_y, direction_x)
                start_angle = base_angle - math.radians(angle_spread / 2)
            
            # 投掷多个小刀
            for i in range(self.knives_per_throw):
                if self.knives_per_throw > 1:
                    # 计算当前小刀的角度
                    current_angle = start_angle + math.radians(angle_step * i)
                    throw_dir_x = math.cos(current_angle)
                    throw_dir_y = math.sin(current_angle)
                else:
                    throw_dir_x = direction_x
                    throw_dir_y = direction_y
                
                # 创建新的投掷小刀（使用屏幕中心坐标）
                knife = ThrownKnife(
                    self.player.rect.centerx,  # 使用玩家的屏幕位置
                    self.player.rect.centery,
                    throw_dir_x,
                    throw_dir_y,
                    self.damage
                )
                # 设置小刀的世界坐标
                knife.world_x = self.player.world_x
                knife.world_y = self.player.world_y
                knife.start_x = self.player.world_x
                knife.start_y = self.player.world_y
                self.thrown_knives.add(knife)
            
            # 播放投掷音效
            resource_manager.play_sound('knife_throw')
        
        # 更新所有投掷的小刀
        self.thrown_knives.update(dt)
        
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        # 渲染所有投掷的小刀
        for knife in self.thrown_knives:
            knife.render(screen, camera_x, camera_y)
        
    def level_up(self):
        """
        通用升级方法，提升所有属性
        """
        self.level += 1
        self.damage += self.upgrade_stats['damage']['increment']
        self.attack_speed += self.upgrade_stats['attack_speed']['increment']
        self.knives_per_throw += int(self.upgrade_stats['knives_per_throw']['increment'])
        self.attack_interval = 1.0 / self.attack_speed 