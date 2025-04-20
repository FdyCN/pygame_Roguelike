import pygame
import math
from ..resource_manager import resource_manager
from ..utils import create_outlined_sprite
from abc import ABC, abstractmethod
from .enemy_config import get_enemy_config

class Enemy(pygame.sprite.Sprite, ABC):
    def __init__(self, x, y, enemy_type, difficulty="normal", level=1, scale=None):
        super().__init__()
        
        # 设置敌人类型
        self.type = enemy_type
        
        # 从配置获取敌人属性
        self.config = get_enemy_config(enemy_type, difficulty, level)
        
        # 设置基本属性
        self.health = self.config["health"]
        self.max_health = self.config["health"]
        self.damage = self.config["damage"]
        self.speed = self.config["speed"]
        self.score_value = self.config["score_value"]
        
        # 设置缩放因子
        self.scale = scale if scale is not None else self.config.get("scale", 2.0)
        
        # 动画相关
        self.animations = {}  # 子类需要设置具体动画
        self.current_animation = 'idle'
        
        # 设置敌人在世界坐标系中的位置
        self.rect = pygame.Rect(x, y, 44 * self.scale, 30 * self.scale)  # 根据缩放调整碰撞箱大小
        
        # 存活状态
        self._alive = True
        
        # 攻击冷却
        self.attack_cooldown = 0
        self.attack_cooldown_time = self.config.get("attack_cooldown", 0.5)  # 攻击冷却时间（秒）
        self.has_damaged_player = False
        
        # 动画状态
        self.hurt_timer = 0
        self.hurt_duration = 0.2
        
        # 朝向
        self.facing_right = True
        
        # 无敌时间相关
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 0.15  # 受伤后的无敌时间（秒）
        
        # 状态效果系统
        self.status_effects = {}  # 格式: {'burn': {...}, 'slow': {...}}
        self.original_speed = self.speed  # 保存原始速度值
        
        # 特效相关
        self.burn_flash_timer = 0.0  # 燃烧闪烁计时器
        self.burn_flash_duration = 0.15  # 燃烧闪烁持续时间
        
        # 轮廓相关
        self.show_outline = False
        self.outline_color = (0, 255, 0)  # 默认绿色轮廓
        self.outline_thickness = 1
        
        # 创建遮罩
        self.mask = None
        
    @abstractmethod
    def load_animations(self):
        """加载敌人的动画，子类必须实现"""
        pass
        
    def apply_burn_effect(self, damage_per_second, duration):
        """
        应用燃烧效果，导致敌人持续受到伤害
        
        Args:
            damage_per_second: 每秒造成的伤害值
            duration: 效果持续时间（秒）
        """
        # 如果已有燃烧效果，延长持续时间而不是重置
        if 'burn' in self.status_effects:
            self.status_effects['burn']['duration'] = max(
                self.status_effects['burn']['duration'],
                duration
            )
            # 更新伤害值为较高者
            self.status_effects['burn']['damage_per_sec'] = max(
                self.status_effects['burn']['damage_per_sec'],
                damage_per_second
            )
        else:
            self.status_effects['burn'] = {
                'duration': duration,
                'damage_per_sec': damage_per_second,
                'timer': 0.0,  # 用于计时何时造成伤害
                'total_timer': 0.0  # 总计时器
            }
            
    def apply_slow_effect(self, slow_percent, duration):
        """
        应用减速效果，降低敌人移动速度
        
        Args:
            slow_percent: 减速百分比（0.0-1.0）
            duration: 效果持续时间（秒）
        """
        # 如果已有减速效果，选择较强的减速效果和较长的持续时间
        if 'slow' in self.status_effects:
            self.status_effects['slow']['duration'] = max(
                self.status_effects['slow']['duration'],
                duration
            )
            if slow_percent > self.status_effects['slow']['slow_percent']:
                self.status_effects['slow']['slow_percent'] = slow_percent
                # 更新减速值
                self.speed = self.original_speed * (1 - slow_percent)
        else:
            # 只有在未减速状态才保存原始速度
            self.original_speed = self.speed
            
            self.status_effects['slow'] = {
                'duration': duration,
                'slow_percent': slow_percent,
                'timer': 0.0  # 总计时器
            }
            # 立即应用减速
            self.speed = self.original_speed * (1 - slow_percent)
            
    def update_status_effects(self, dt):
        """
        更新所有状态效果
        
        Args:
            dt: 时间增量（秒）
        """
        # 更新燃烧闪烁计时器
        if self.burn_flash_timer > 0:
            self.burn_flash_timer -= dt
            if self.burn_flash_timer <= 0:
                self.burn_flash_timer = 0
        
        # 处理燃烧效果
        if 'burn' in self.status_effects:
            effect = self.status_effects['burn']
            effect['total_timer'] += dt
            effect['timer'] += dt
            
            # 每0.5秒造成一次伤害
            if effect['timer'] >= 0.5:
                damage = effect['damage_per_sec'] * 0.5
                self.health -= damage  # 直接扣除生命值，不触发无敌状态
                effect['timer'] = 0.0
                
                # 触发燃烧闪烁效果
                self.burn_flash_timer = self.burn_flash_duration
                
                # 检查敌人是否死亡
                if self.health <= 0:
                    # 标记敌人为死亡状态
                    self._alive = False
                    # 播放死亡音效
                    resource_manager.play_sound("enemy_death")
                    # 注意：实际移除敌人的操作是在EnemyManager中进行的
                
            # 检查是否结束
            if effect['total_timer'] >= effect['duration']:
                del self.status_effects['burn']
        
        # 处理减速效果
        if 'slow' in self.status_effects:
            effect = self.status_effects['slow']
            effect['timer'] += dt
            
            # 检查是否结束
            if effect['timer'] >= effect['duration']:
                # 恢复速度
                self.speed = self.original_speed
                del self.status_effects['slow']
        
    def attack(self, player, dt):
        """
        敌人默认使用近战碰撞攻击
        
        Args:
            player: 攻击目标（玩家）
            dt: 时间增量
            
        Returns:
            bool: 攻击是否命中
        """
        return self.melee_attack(player) 
        
    def update(self, dt, player):
        # 更新状态效果
        self.update_status_effects(dt)
        
        # 更新无敌状态
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
                self.invincible_timer = 0
        
        # 更新当前动画
        if self.current_animation in self.animations:
            self.animations[self.current_animation].update(dt)
        
        # 更新动画状态
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0:
                self.current_animation = 'idle'
                if self.current_animation in self.animations:
                    self.animations[self.current_animation].reset()
        
        # 计算到玩家的方向（使用世界坐标）
        dx = player.world_x - self.rect.x
        dy = player.world_y - self.rect.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 更新朝向
        self.facing_right = dx > 0
        
        if distance != 0:
            # 标准化方向向量
            dx = dx / distance
            dy = dy / distance
            
            # 更新位置
            self.rect.x += dx * self.speed * dt
            self.rect.y += dy * self.speed * dt
            
            # 如果不在受伤状态，切换到行走动画
            if self.hurt_timer <= 0:
                if self.current_animation != 'walk':
                    self.current_animation = 'walk'
                    if self.current_animation in self.animations:
                        self.animations[self.current_animation].reset()
                
        elif self.hurt_timer <= 0:
            if self.current_animation != 'idle':
                self.current_animation = 'idle'
                if self.current_animation in self.animations:
                    self.animations[self.current_animation].reset()
                    
        # 更新当前图像
        self.update_image()
            
    def update_image(self):
        """更新敌人的当前图像"""
        if self.current_animation in self.animations:
            current_frame = self.animations[self.current_animation].get_current_frame()
            
            # 缩放图像
            original_size = current_frame.get_size()
            new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
            current_frame = pygame.transform.scale(current_frame, new_size)
            
            # 总是翻转当前帧
            current_frame = pygame.transform.flip(current_frame, True, False)
            
            # 根据朝向再次翻转图像
            if not self.facing_right:
                current_frame = pygame.transform.flip(current_frame, True, False)
            
            # 应用状态效果的视觉变化
            modified_frame = current_frame.copy()
            
            # 创建遮罩以获取实际边缘和区域
            mask = pygame.mask.from_surface(current_frame)
            mask_outline = mask.outline()
            
            # 如果有减速效果
            if 'slow' in self.status_effects:
                # 创建与原图大小相同的透明表面
                slow_effect = pygame.Surface(modified_frame.get_size(), pygame.SRCALPHA)
                
                # 为边缘添加蓝色光晕
                if mask_outline:
                    for point in mask_outline:
                        # 绘制蓝色光晕点
                        pygame.draw.circle(slow_effect, (0, 0, 200, 100), point, 3)
                
                # 为实际区域添加淡蓝色
                mask_surface = mask.to_surface(setcolor=(0, 0, 100, 70), unsetcolor=(0, 0, 0, 0))
                slow_effect.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                
                # 叠加到原图
                modified_frame.blit(slow_effect, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            # 如果有燃烧闪烁效果
            if self.burn_flash_timer > 0:
                # 创建与原图大小相同的透明表面
                fire_effect = pygame.Surface(modified_frame.get_size(), pygame.SRCALPHA)
                
                # 为边缘添加红色光晕
                if mask_outline:
                    for point in mask_outline:
                        # 绘制红色/橙色光晕点
                        pygame.draw.circle(fire_effect, (255, 100, 0, 150), point, 3)
                
                # 为实际区域添加淡红色
                mask_surface = mask.to_surface(setcolor=(50, 0, 0, 50), unsetcolor=(0, 0, 0, 0))
                fire_effect.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                
                # 叠加到原图
                modified_frame.blit(fire_effect, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            
            self.image = modified_frame
            
            # 更新遮罩
            self.mask = pygame.mask.from_surface(self.image)
            
    def toggle_outline(self, show=None, color=None, thickness=None):
        """
        切换是否显示轮廓
        
        Args:
            show: 是否显示轮廓，None表示切换当前状态
            color: 轮廓颜色，None表示使用当前颜色
            thickness: 轮廓粗细，None表示使用当前粗细
        """
        if show is not None:
            self.show_outline = show
        else:
            self.show_outline = not self.show_outline
            
        if color is not None:
            self.outline_color = color
            
        if thickness is not None:
            self.outline_thickness = thickness
    
    def render(self, screen, screen_x, screen_y):
        # 创建一个临时的rect用于绘制
        draw_rect = self.rect.copy()
        draw_rect.x = screen_x
        draw_rect.y = screen_y
        
        # 绘制敌人
        if hasattr(self, 'image'):
            if self.show_outline:
                # 创建带轮廓的图像
                outlined_image = create_outlined_sprite(
                    self,
                    outline_color=self.outline_color,
                    outline_thickness=self.outline_thickness
                )
                screen.blit(outlined_image, draw_rect)
            else:
                screen.blit(self.image, draw_rect)
        
        # 绘制血条
        health_bar_width = 32 * self.scale
        health_bar_height = 5 * self.scale
        health_ratio = self.health / self.max_health
        
        # 调整血条位置，使其位于敌人上方
        bar_x = screen_x
        bar_y = screen_y - 10 * self.scale
        
        pygame.draw.rect(screen, (255, 0, 0),  # 红色背景
                        (bar_x, bar_y,
                         health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0),  # 绿色血条
                        (bar_x, bar_y,
                         health_bar_width * health_ratio, health_bar_height))
        
    def take_damage(self, amount):
        """受到伤害
        
        Args:
            amount: 伤害值
            
        Returns:
            bool: 是否实际造成了伤害
        """
        # 如果处于无敌状态，不造成伤害
        if self.invincible:
            return False
            
        # 造成伤害
        self.health -= amount
        
        # 进入无敌状态
        self.invincible = True
        self.invincible_timer = self.invincible_duration
        
        # 切换到受伤动画
        self.current_animation = 'hurt'
        if self.current_animation in self.animations:
            self.animations[self.current_animation].reset()
        self.hurt_timer = self.hurt_duration
        
        # 播放受伤音效
        resource_manager.play_sound("enemy_hit")
        
        return True
        
    def melee_attack(self, player):
        """
        近战碰撞攻击逻辑
        
        Args:
            player: 攻击目标（玩家）
            
        Returns:
            bool: 攻击是否命中
        """
        # 计算与玩家的距离
        dx = self.rect.x - player.world_x
        dy = self.rect.y - player.world_y
        distance = (dx**2 + dy**2)**0.5
        
        # 如果在攻击范围内
        if distance < self.rect.width / 2 + player.rect.width / 2:
            player.take_damage(self.damage)
            return True
        return False
        
    def attack_player(self, player):
        """
        攻击玩家方法，调用子类实现的attack方法
        保持向后兼容性
        
        Args:
            player: 攻击目标（玩家）
            
        Returns:
            bool: 攻击是否命中
        """
        # 使用一个很小的时间增量，保持现有行为一致
        return self.attack(player, 0.016)  # 约等于60fps的时间增量

    def kill(self):
        """重写 kill 方法，确保正确处理存活状态"""
        self._alive = False
        super().kill()
        
    def alive(self):
        """返回敌人是否存活
        
        Returns:
            bool: 如果敌人还活着返回 True，否则返回 False
        """
        return self._alive and self.health > 0