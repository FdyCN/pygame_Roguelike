import pygame
import math
from .resource_manager import resource_manager
from .weapons.types.knife import Knife
from .weapons.types.fireball import Fireball
from .weapons.types.frost_nova import FrostNova
from .upgrade_system import UpgradeType, WeaponUpgradeLevel, PassiveUpgradeLevel
from .hero_config import get_hero_config
from .utils import create_outlined_sprite
from .components.components import (
    MovementComponent,
    AnimationComponent,
    HealthComponent,
    WeaponManager,
    PassiveManager,
    ProgressionSystem
)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, hero_type="ninja_frog"):
        super().__init__()
        
        # 加载英雄配置
        self.hero_config = get_hero_config(hero_type)
        self.hero_type = hero_type
        
        # 世界坐标（实际位置）
        self.world_x = x
        self.world_y = y
        
        # 初始化各组件
        self._init_components()
        
        # 设置初始图像和碰撞矩形
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 创建遮罩
        self.mask = None
        self.update_mask()
        
        # 轮廓相关
        self.show_outline = False
        self.outline_color = (255, 0, 0)  # 默认红色轮廓
        self.outline_thickness = 1
        
        # 添加初始武器
        starting_weapon = self.hero_config.get("starting_weapon", "knife")
        self.add_weapon(starting_weapon)
        
    def _init_components(self):
        """初始化所有组件"""
        
        # 基础属性
        base_stats = self.hero_config["base_stats"]
        
        # 1. 动画组件
        self.animation = AnimationComponent(self)
        self.animation.load_animations(self.hero_config["animations"])
        
        # 2. 移动组件
        self.movement = MovementComponent(self, speed=base_stats["speed"])
        
        # 3. 生命值组件
        self.health_component = HealthComponent(
            self,
            max_health=base_stats["max_health"],
            defense=base_stats["defense"],
            health_regen=base_stats["health_regen"]
        )
        # 设置受伤回调
        self.health_component.on_damaged = self._on_damaged
        
        # 4. 武器管理器
        self.weapon_manager = WeaponManager(self)
        self.weapon_manager.available_weapons = {
            'knife': Knife,
            'fireball': Fireball,
            'frost_nova': FrostNova
        }
        
        # 5. 被动技能管理器
        self.passive_manager = PassiveManager(self)
        self.passive_manager.on_stats_changed = self._update_stats
        
        # 6. 进阶系统
        self.progression = ProgressionSystem(self, base_exp_multiplier=base_stats["exp_multiplier"])
        self.progression.set_luck(base_stats["luck"])
        
        # 其他属性（兼容旧接口）
        self.pickup_range = base_stats["pickup_range"]
        self.attack_power = base_stats["attack_power"]
        
    def _on_damaged(self, amount):
        """受伤回调"""
        # 设置动画为受伤状态
        self.animation.set_animation('hurt')
        
    def _update_stats(self):
        """更新玩家属性"""
        # 获取基础属性
        base_stats = self.hero_config["base_stats"].copy()
        
        # 计算被动加成后的属性
        final_stats = self.passive_manager.calculate_stats(base_stats)
        
        # 应用属性到各组件
        self.movement.set_speed(final_stats["speed"])
        
        self.health_component.max_health = final_stats["max_health"]
        self.health_component.defense = final_stats["defense"]
        self.health_component.health_regen = final_stats["health_regen"]
        
        self.progression.set_exp_multiplier(final_stats["exp_multiplier"])
        self.progression.set_luck(final_stats["luck"])
        
        # 更新其他属性
        self.pickup_range = final_stats["pickup_range"]
        self.attack_power = final_stats["attack_power"]
        
        # 更新武器攻击力
        self.weapon_manager.apply_attack_power(self.attack_power)
        
    # 兼容旧接口的属性访问器
    @property
    def health(self):
        return self.health_component.health
        
    @health.setter
    def health(self, value):
        self.health_component.health = value
        
    @property
    def max_health(self):
        return self.health_component.max_health
        
    @property
    def defense(self):
        return self.health_component.defense
        
    @property
    def invincible(self):
        return self.health_component.invincible
        
    @property
    def weapons(self):
        return self.weapon_manager.weapons
        
    @property
    def weapon_levels(self):
        return self.weapon_manager.weapon_levels
        
    @property
    def passives(self):
        return self.passive_manager.passives
        
    @property
    def passive_levels(self):
        return self.passive_manager.passive_levels
        
    @property
    def level(self):
        return self.progression.level
        
    @property
    def experience(self):
        return self.progression.experience
        
    @property
    def exp_to_next_level(self):
        return self.progression.exp_to_next_level
        
    @property
    def coins(self):
        return self.progression.coins
        
    @coins.setter
    def coins(self, value):
        self.progression.coins = value
        
    @property
    def luck(self):
        return self.progression.luck
    
    # 公共方法 - 保持与旧接口兼容
    def handle_event(self, event):
        """处理输入事件"""
        self.movement.handle_event(event)
        
    def update(self, dt):
        """更新玩家状态"""
        # 更新各组件
        self.movement.update(dt)
        self.animation.update(dt)
        self.health_component.update(dt)
        
        # 更新动画状态
        self._update_animation_state()
        
        # 更新当前图像
        self.image = self.animation.get_current_frame(not self.movement.facing_right)
        
        # 更新遮罩
        self.update_mask()
        
    def update_mask(self):
        """更新精灵遮罩"""
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
        
    def render(self, screen):
        """渲染玩家"""
        if not self.health_component.invincible or self.animation.visible:
            if self.show_outline:
                # 创建带轮廓的图像
                outlined_image = create_outlined_sprite(
                    self,
                    outline_color=self.outline_color,
                    outline_thickness=self.outline_thickness
                )
                screen.blit(outlined_image, self.rect)
            else:
                screen.blit(self.image, self.rect)
            
    def _update_animation_state(self):
        """更新动画状态"""
        # 如果不在受伤状态
        if not self.health_component.is_hurt():
            # 根据移动状态切换动画
            if self.movement.is_moving():
                self.animation.set_animation('run')
            else:
                self.animation.set_animation('idle')
                
    def take_damage(self, amount):
        """受到伤害"""
        return self.health_component.take_damage(amount)
        
    def heal(self, amount):
        """治疗生命值"""
        return self.health_component.heal(amount)
        
    def apply_weapon_upgrade(self, weapon_type, level, effects):
        """应用武器升级"""
        return self.weapon_manager.apply_weapon_upgrade(weapon_type, level, effects)
            
    def apply_passive_upgrade(self, passive_type, level, effects):
        """应用被动升级"""
        return self.passive_manager.apply_passive_upgrade(passive_type, level, effects)
        
    def get_weapon_level(self, weapon_type):
        """获取指定武器的等级"""
        return self.weapon_manager.get_weapon_level(weapon_type)
        
    def get_passive_level(self, passive_type):
        """获取指定被动的等级"""
        return self.passive_manager.get_passive_level(passive_type)
        
    def add_weapon(self, weapon_type):
        """添加武器"""
        return self.weapon_manager.add_weapon(weapon_type)
        
    def update_weapons(self, dt, enemies=None):
        """更新所有武器状态"""
        self.weapon_manager.update(dt, enemies)
        
    def render_weapons(self, screen, camera_x, camera_y):
        """渲染所有武器"""
        self.weapon_manager.render(screen, camera_x, camera_y)
        
    def remove_weapon(self, weapon_type):
        """移除指定类型的武器"""
        self.weapon_manager.remove_weapon(weapon_type)
        
    def add_experience(self, amount):
        """添加经验值"""
        return self.progression.add_experience(amount)
            
    def level_up(self):
        """升级处理"""
        return self.progression.level_up()
        
    def add_coins(self, amount):
        """添加金币"""
        return self.progression.add_coins(amount) 