"""
武器管理组件
负责管理实体的武器系统，包括武器升级、切换和使用
"""

from .base_component import Component
import inspect
from ..weapons.weapon_utils import create_weapon

class WeaponManager(Component):
    """武器管理组件，处理实体的武器系统"""
    
    def __init__(self, owner, max_weapons=3):
        """
        初始化武器管理组件
        
        Args:
            owner: 组件所属的实体
            max_weapons: 最大武器数量
        """
        super().__init__(owner)
        
        # 武器列表和等级
        self.weapons = []  # 武器实例列表
        self.weapon_levels = {}  # 武器等级字典 {'knife': 1, 'fireball': 1}
        self.max_weapons = max_weapons
        
        # 可用武器类型
        self.available_weapons = {}  # 将在player类中初始化
    
    def add_weapon(self, weapon_type):
        """
        添加武器到武器列表
        
        Args:
            weapon_type: 武器类型名称
            
        Returns:
            object: 成功时返回武器实例，失败时返回None
        """
        if len(self.weapons) < self.max_weapons and weapon_type in self.available_weapons:
            # 检查是否已有该类型武器
            for weapon in self.weapons:
                if weapon.type == weapon_type:
                    return None
            
            # 尝试使用工厂方法创建武器
            weapon = create_weapon(weapon_type, self.owner)
            
            # 如果工厂创建失败，使用旧方法兼容
            if weapon is None and weapon_type in self.available_weapons:
                weapon = self.available_weapons[weapon_type](self.owner)
                
            if weapon:
                self.weapons.append(weapon)
                self.weapon_levels[weapon_type] = 1
                
                # 应用玩家的攻击力加成
                if hasattr(self.owner, 'attack_power') and self.owner.attack_power != 1.0:
                    weapon._apply_player_attack_power(self.owner.attack_power)
                    
                return weapon
        return None
    
    def remove_weapon(self, weapon_type):
        """
        移除指定类型的武器
        
        Args:
            weapon_type: 武器类型
            
        Returns:
            bool: 成功移除返回True，失败返回False
        """
        for i, weapon in enumerate(self.weapons):
            if weapon.type == weapon_type:
                self.weapons.pop(i)
                if weapon_type in self.weapon_levels:
                    del self.weapon_levels[weapon_type]
                return True
        return False
    
    def update(self, dt, enemies=None):
        """
        更新所有武器状态
        
        Args:
            dt: 时间增量
            enemies: 敌人列表，用于武器追踪
        """
        if not self.enabled:
            return
            
        if not enemies:
            enemies = []
        
        for weapon in self.weapons:
            # 检查weapon.update方法所需的参数数量
            update_signature = inspect.signature(weapon.update)
            
            # 根据参数数量决定如何调用update方法
            if len(update_signature.parameters) > 1:  # 如果需要额外参数（比如敌人列表）
                weapon.update(dt, enemies)
            else:
                weapon.update(dt)
        
        # 更新玩家的攻击力影响
        if hasattr(self.owner, 'passive') and self.owner.passive:
            attack_power = self.owner.passive.get_passive_level('attack_power')
            if attack_power > 0:
                self.apply_attack_power_bonus()
    
    def render(self, screen, camera_x, camera_y):
        """
        渲染所有武器
        
        Args:
            screen: 目标Surface
            camera_x: 相机X坐标
            camera_y: 相机Y坐标
        """
        for weapon in self.weapons:
            if hasattr(weapon, 'render'):
                weapon.render(screen, camera_x, camera_y)
    
    def apply_weapon_upgrade(self, weapon_type, level, effects):
        """
        应用武器升级
        
        Args:
            weapon_type: 武器类型
            level: 升级后的等级
            effects: 升级效果
            
        Returns:
            bool: 成功应用升级返回True，失败返回False
        """
        # 已有该武器 - 升级
        if weapon_type in self.weapon_levels:
            self.weapon_levels[weapon_type] = level
            # 更新武器属性
            for weapon in self.weapons:
                if weapon.type == weapon_type:
                    weapon.level = level
                    if hasattr(weapon, 'apply_effects'):
                        weapon.apply_effects(effects)
                    break
            return True
            
        # 没有该武器且武器栏未满 - 添加新武器
        elif len(self.weapons) < self.max_weapons and weapon_type in self.available_weapons:
            weapon = self.add_weapon(weapon_type)
            if weapon:
                self.weapon_levels[weapon_type] = level
                if level > 1 and hasattr(weapon, 'apply_effects'):
                    weapon.apply_effects(effects)
                return True
                
        return False
    
    def get_weapon_level(self, weapon_type):
        """
        获取指定武器的等级
        
        Args:
            weapon_type: 武器类型
            
        Returns:
            int: 武器等级，未持有返回0
        """
        return self.weapon_levels.get(weapon_type, 0)
    
    def has_max_weapons(self):
        """
        检查是否已达到最大武器数量
        
        Returns:
            bool: 若已达到最大武器数量返回True，否则返回False
        """
        return len(self.weapons) >= self.max_weapons
    
    def apply_attack_power(self, attack_power):
        """
        应用攻击力修正到所有武器
        
        Args:
            attack_power: 攻击力倍率
        """
        for weapon in self.weapons:
            if hasattr(weapon, '_apply_player_attack_power'):
                weapon._apply_player_attack_power(attack_power) 