from ..enemy import Enemy
from ...resource_manager import resource_manager
import pygame
import math

class Slime(Enemy):
    """远程攻击敌人示例类"""
    
    def __init__(self, x, y, enemy_type='slime', difficulty="normal", level=1, scale=None):
        # 调用基类构造函数，传递敌人类型、难度和等级
        super().__init__(x, y, enemy_type, difficulty, level, scale)
        
        # 从配置获取远程攻击相关属性
        self.attack_range = self.config.get("attack_range", 800)        # 攻击距离
        self.min_attack_range = self.config.get("min_attack_range", 300) # 最小攻击距离，太近不会发射
        self.attack_cooldown = 0
        self.attack_cooldown_time = self.config.get("attack_cooldown", 2.0)  # 攻击冷却时间（秒）
        self.projectile_speed = self.config.get("projectile_speed", 180)
        self.projectiles = pygame.sprite.Group()  # 存储投射物
        
        # 加载动画
        self.load_animations()
        
        # 设置初始图像
        self.current_animation = 'idle'
        self.image = self.animations[self.current_animation].get_current_frame()
        # 应用缩放
        original_size = self.image.get_size()
        new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
        self.image = pygame.transform.scale(self.image, new_size)
        
    def load_animations(self):
        """加载远程敌人的动画"""
        # 获取配置中的动画速度
        animation_speed = self.config.get("animation_speed", 0.0333)
        
        # 加载精灵表
        idle_spritesheet = resource_manager.load_spritesheet(
            'slime_idle_spritesheet', 'images/enemy/Slime_Idle_44x30.png')
        walk_spritesheet = resource_manager.load_spritesheet(
            'slime_walk_spritesheet', 'images/enemy/Slime_Idle_44x30.png')
        hurt_spritesheet = resource_manager.load_spritesheet(
            'slime_hurt_spritesheet', 'images/enemy/Slime_Idle_44x30.png')
        
        # 创建动画
        self.animations = {
            'idle': resource_manager.create_animation(
                'ranger_idle', idle_spritesheet,
                frame_width=44, frame_height=30,
                frame_count=10, row=0,
                frame_duration=animation_speed
            ),
            'walk': resource_manager.create_animation(
                'ranger_walk', walk_spritesheet,
                frame_width=44, frame_height=30,
                frame_count=10, row=0,
                frame_duration=animation_speed
            ),
            'hurt': resource_manager.create_animation(
                'ranger_hurt', hurt_spritesheet,
                frame_width=44, frame_height=30,
                frame_count=10, row=0,
                frame_duration=animation_speed
            )
        }
        
    def update(self, dt, player):
        # 首先调用父类更新方法
        super().update(dt, player)
        
        # 更新冷却时间
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # 更新投射物
        self.projectiles.update(dt)
        
    def render(self, screen, screen_x, screen_y):
        # 先调用父类渲染方法
        super().render(screen, screen_x, screen_y)
        
        # 渲染投射物
        for projectile in self.projectiles:
            # 计算投射物相对于敌人的偏移
            projectile_offset_x = projectile.x - self.rect.centerx
            projectile_offset_y = projectile.y - self.rect.centery
            
            # 计算投射物在屏幕上的位置 = 敌人屏幕位置 + 相对偏移
            projectile_screen_x = screen_x + projectile_offset_x
            projectile_screen_y = screen_y + projectile_offset_y
            
            # 渲染投射物
            screen.blit(projectile.image, 
                      (projectile_screen_x - projectile.image.get_width()//2, 
                       projectile_screen_y - projectile.image.get_height()//2))
        
    def attack(self, player, dt):
        """
        实现基类的抽象方法，远程攻击逻辑
        
        Args:
            player: 攻击目标（玩家）
            dt: 时间增量
            
        Returns:
            bool: 攻击是否命中
        """
        # 更新所有投射物
        hit = False
        for projectile in list(self.projectiles):
            # 检查投射物是否击中玩家
            if self._check_projectile_hit(projectile, player):
                projectile.kill()
                hit = True
                
        # 如果冷却完成，检查是否可以进行新的攻击
        if self.attack_cooldown <= 0:
            # 计算到玩家的距离
            dx = player.world_x - self.rect.centerx
            dy = player.world_y - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 如果在攻击范围内但不是太近
            if self.min_attack_range < distance < self.attack_range:
                # 计算攻击方向
                if distance > 0:
                    direction_x = dx / distance
                    direction_y = dy / distance
                    
                    # 发射投射物
                    self._fire_projectile(direction_x, direction_y)
                    
                    # 重置攻击冷却
                    self.attack_cooldown = self.attack_cooldown_time
                    
        return hit
                
    def _fire_projectile(self, direction_x, direction_y):
        """
        发射投射物
        
        Args:
            direction_x: X方向单位向量
            direction_y: Y方向单位向量
        """
        # 创建投射物，使用rect中心坐标
        projectile = RangerProjectile(
            self.rect.centerx, 
            self.rect.centery,
            direction_x,
            direction_y,
            self.damage,
            self.projectile_speed
        )
        self.projectiles.add(projectile)
        
    def _check_projectile_hit(self, projectile, player):
        """
        检查投射物是否击中玩家
        
        Args:
            projectile: 投射物对象
            player: 玩家对象
            
        Returns:
            bool: 是否击中
        """
        # 计算投射物和玩家之间的距离
        dx = projectile.x - player.world_x
        dy = projectile.y - player.world_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 如果距离小于碰撞半径，则判定为击中
        if distance < player.rect.width / 2 + projectile.radius:
            # 玩家受到伤害
            player.take_damage(projectile.damage)
            return True
            
        return False


class RangerProjectile(pygame.sprite.Sprite):
    """远程敌人的投射物类"""
    
    def __init__(self, x, y, direction_x, direction_y, damage, speed):
        super().__init__()
        # 基本属性
        self.x = x  # 投射物的世界 x 坐标
        self.y = y  # 投射物的世界 y 坐标
        self.direction_x = direction_x  # 横向方向向量（已归一化）
        self.direction_y = direction_y  # 纵向方向向量（已归一化）
        self.damage = damage  # 投射物伤害
        self.speed = speed  # 投射物速度
        self.radius = 8  # 碰撞半径
        self.lifetime = 5.0  # 生命周期（秒）
        
        # 创建更大更明显的投射物图像
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (8, 8), 8)  # 红色圆形投射物
        
        # 根据方向添加"尾巴"，使弹道更明显
        end_x = 8 - int(direction_x * 8)
        end_y = 8 - int(direction_y * 8)
        pygame.draw.line(self.image, (255, 200, 200), (8, 8), (end_x, end_y), 3)
        
        # 设置rect用于渲染和碰撞检测
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self, dt):
        """更新投射物状态"""
        # 按照固定方向和速度更新位置
        self.x += self.direction_x * self.speed * dt
        self.y += self.direction_y * self.speed * dt
        
        # 更新rect位置
        self.rect.center = (self.x, self.y)
        
        # 更新生命周期
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            
    def render(self, screen, camera_x, camera_y):
        """渲染投射物(已在Slime的render方法中实现，此方法不再使用)"""
        pass