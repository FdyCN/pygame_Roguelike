import pygame
from ..resource_manager import resource_manager
from enum import Enum, auto
from .weapon_stats import WeaponStatType, DEFAULT_WEAPON_STATS
import math
from ..constants import DIRECTION_ANGLES

class WeaponType(Enum):
    MELEE = auto()      # 近战武器
    PROJECTILE = auto() # 投射物武器
    
class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, weapon_type):
        super().__init__()
        self.player = player
        self.type = weapon_type

        self.base_stats = DEFAULT_WEAPON_STATS.copy()
        self.current_stats = self.base_stats.copy()
        
        # 等级
        self.level = 1
        
        # 攻击状态
        self.attack_timer = 0
        self.attack_interval = 1.0 / self.current_stats.get(WeaponStatType.ATTACK_SPEED, 1.0)
        
        # 投射物列表（如果是投射物类型的武器）
        self.projectiles = pygame.sprite.Group()
        

        
    def get_projectiles(self):
        """获取武器的投射物列表，如果没有则返回空列表"""
        return self.projectiles if hasattr(self, 'projectiles') else pygame.sprite.Group()
        
    def handle_collision(self, projectile, enemy):
        """处理武器投射物与敌人的碰撞
        
        Args:
            projectile: 武器的投射物
            enemy: 被击中的敌人
            
        Returns:
            bool: 是否应该销毁投射物
        """
        # 检查敌人是否处于无敌状态
        if hasattr(enemy, 'invincible_timer') and enemy.invincible_timer > 0:
            # 敌人处于无敌状态，不计算新的碰撞
            return False
            
        # 造成伤害
        enemy.take_damage(projectile.damage)
        
        # 检查穿透属性
        if not hasattr(projectile, 'can_penetrate'):
            return True
            
        # 增加命中计数（只有在实际造成伤害时才增加）
        projectile.hit_count += 1
            
        # 如果投射物可以穿透且未达到最大穿透次数，继续保持投射物
        if projectile.can_penetrate and projectile.hit_count < projectile.max_penetration:
            # 每次穿透后降低伤害
            projectile.damage *= (1 - projectile.penetration_damage_reduction)
            return False
            
        return True
        
    def _apply_player_attack_power(self):
        """应用玩家的攻击力加成到武器伤害"""
        if WeaponStatType.DAMAGE in self.current_stats:
            # 使用当前伤害值乘以玩家攻击力加成
            current_damage = self.current_stats[WeaponStatType.DAMAGE]
            self.current_stats[WeaponStatType.DAMAGE] = int(current_damage * self.player.attack_power)
        
    def apply_effects(self, effects):
        """应用升级效果"""
        # 保存旧的攻击间隔用于比较
        old_attack_speed = self.current_stats.get(WeaponStatType.ATTACK_SPEED, 1.0)
        
        # 应用所有效果
        for stat, value in effects.items():
            if stat in self.current_stats:
                if isinstance(value, dict):
                    # 处理复杂效果，如 {'multiply': 1.2} 或 {'add': 10}
                    if 'multiply' in value:
                        self.current_stats[stat] *= value['multiply']
                    elif 'add' in value:
                        self.current_stats[stat] += value['add']
                else:
                    # 直接设置值
                    self.current_stats[stat] = value
                    
        # 如果攻击速度改变，更新攻击间隔
        new_attack_speed = self.current_stats.get(WeaponStatType.ATTACK_SPEED, 1.0)
        if new_attack_speed != old_attack_speed:
            self.attack_interval = 1.0 / new_attack_speed
            
        # 在应用效果后重新应用玩家的攻击力加成
        self._apply_player_attack_power()
            
    def can_attack(self):
        """检查是否可以攻击"""
        return self.attack_timer >= self.attack_interval
        
    def update(self, dt):
        """更新武器状态"""
        self.attack_timer += dt
        
    def get_player_direction(self):
        """获取玩家的攻击方向"""
        direction_x = self.player.direction.x
        direction_y = self.player.direction.y
        
        # 如果玩家没有移动，使用最后的移动方向和角度
        if direction_x == 0 and direction_y == 0:
            direction_x = self.player.last_movement_direction.x
            direction_y = self.player.last_movement_direction.y

        # 标准化方向向量
        length = (direction_x**2 + direction_y**2) ** 0.5
        if length > 0:
            direction_x /= length
            direction_y /= length
            
        return direction_x, direction_y
    
    def render(self, screen, camera_x, camera_y):
        """渲染武器"""
        pass    
