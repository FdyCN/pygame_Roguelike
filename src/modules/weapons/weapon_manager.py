import pygame
from .knife import Knife
from .fireball import Fireball
from .frost_nova import FrostNova

class WeaponManager:
    def __init__(self, player):
        self.player = player
        self.weapons = []
        self.available_weapons = {
            'knife': Knife,
            'fireball': Fireball,
            'frost_nova': FrostNova
        }
        
        # 初始武器
        self.add_weapon('knife')
        # 将武器添加到玩家的武器列表中
        self.player.weapons = self.weapons
        
    def update(self, dt):
        for weapon in self.weapons[:]:
            weapon.update(dt)
            
    def render(self, screen, camera_x, camera_y):
        for weapon in self.weapons:
            weapon.render(screen, camera_x, camera_y)
            
    def add_weapon(self, weapon_name):
        if weapon_name in self.available_weapons:
            weapon = self.available_weapons[weapon_name](self.player)
            self.weapons.append(weapon)
            
    def remove_weapon(self, weapon):
        if weapon in self.weapons:
            self.weapons.remove(weapon)
            
    def upgrade_weapon(self, weapon_name):
        for weapon in self.weapons:
            if isinstance(weapon, self.available_weapons[weapon_name]):
                weapon.level_up() 