import pygame
from .knife import Knife

class WeaponManager:
    def __init__(self, player):
        self.player = player
        self.weapons = []
        self.available_weapons = {
            'knife': Knife
        }
        
        # 初始武器
        self.add_weapon('knife')
        # 将武器添加到玩家的武器列表中
        self.player.weapons = self.weapons
        
    def update(self, dt):
        for weapon in self.weapons[:]:
            weapon.update(dt)
            
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        for weapon in self.weapons:
            weapon.render(screen, camera_x, camera_y, screen_center_x, screen_center_y)
            
    def add_weapon(self, weapon_name):
        """添加武器到管理器
        
        Args:
            weapon_name: 武器名称
            
        Returns:
            Weapon: 创建的武器实例，如果创建失败则返回None
        """
        if weapon_name in self.available_weapons:
            weapon = self.available_weapons[weapon_name](self.player)
            self.weapons.append(weapon)
            return weapon
        return None
            
    def remove_weapon(self, weapon):
        if weapon in self.weapons:
            self.weapons.remove(weapon)
            
    def upgrade_weapon(self, weapon_name):
        for weapon in self.weapons:
            if isinstance(weapon, self.available_weapons[weapon_name]):
                weapon.level_up() 