import pygame
from ..resource_manager import resource_manager

class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, weapon_type, base_stats):
        super().__init__()
        self.player = player
        self.type = weapon_type
        
        # 基础属性
        self.base_stats = base_stats.copy()
        self.current_stats = base_stats.copy()
        
        # 等级
        self.level = 1
        
        # 攻击状态
        self.attack_timer = 0
        self.attack_interval = 1.0 / self.current_stats.get('attack_speed', 1.0)
        
    def apply_effects(self, effects):
        """应用升级效果"""
        # 保存旧的攻击间隔用于比较
        old_attack_speed = self.current_stats.get('attack_speed', 1.0)
        
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
        new_attack_speed = self.current_stats.get('attack_speed', 1.0)
        if new_attack_speed != old_attack_speed:
            self.attack_interval = 1.0 / new_attack_speed
            
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
        
        # 如果玩家没有移动，使用朝向
        if direction_x == 0 and direction_y == 0:
            direction_x = 1 if self.player.facing_right else -1
            direction_y = 0
            
        # 标准化方向向量
        length = (direction_x**2 + direction_y**2) ** 0.5
        if length > 0:
            direction_x /= length
            direction_y /= length
            
        return direction_x, direction_y 
    
    def render(self, screen, camera_x, camera_y):
        """渲染武器"""
        pass    
