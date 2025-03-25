import unittest
import pygame
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.player import Player
from src.modules.weapons.weapon_manager import WeaponManager
from src.modules.upgrade_system import UpgradeManager
from src.modules.game import Game

class TestUpgrades(unittest.TestCase):
    def setUp(self):
        """测试前的初始化"""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.player = Player(400, 300)
        self.weapon_manager = WeaponManager(self.player)
        self.upgrade_manager = UpgradeManager()
        
    def test_initial_knife_stats(self):
        """测试初始飞刀属性是否正确"""
        knife = self.player.weapons[0]  # 玩家的初始武器是飞刀
        self.assertEqual(knife.type, 'knife')
        self.assertEqual(knife.level, 1)
        
        # 验证初始属性是否与1级飞刀配置一致
        expected_stats = {
            'damage': 20,
            'attack_speed': 1.0,
            'projectile_speed': 400,
            'penetration': False,
            'knives_per_throw': 1,
            'spread_angle': 0,
            'lifetime': 3.0
        }
        
        for stat, value in expected_stats.items():
            self.assertEqual(knife.current_stats[stat], value, 
                           f"{stat} should be {value} but got {knife.current_stats[stat]}")
            
    def test_knife_upgrade_level2(self):
        """测试飞刀升级到2级后的属性"""
        knife = self.player.weapons[0]
        
        # 获取2级飞刀的升级配置
        knife_upgrade = self.upgrade_manager.weapon_upgrades['knife'].levels[1]
        
        # 应用升级效果
        knife.apply_effects(knife_upgrade.effects)
        knife.level = 2
        
        # 验证升级后的属性
        expected_stats = {
            'damage': 20,
            'attack_speed': 1.1,
            'projectile_speed': 400,
            'penetration': False,
            'knives_per_throw': 2,
            'spread_angle': 15,
            'lifetime': 3.0
        }
        
        for stat, value in expected_stats.items():
            self.assertEqual(knife.current_stats[stat], value,
                           f"{stat} should be {value} but got {knife.current_stats[stat]}")
            
    def test_knife_upgrade_level3(self):
        """测试飞刀升级到3级后的属性"""
        knife = self.player.weapons[0]
        
        # 获取3级飞刀的升级配置
        knife_upgrade = self.upgrade_manager.weapon_upgrades['knife'].levels[2]
        
        # 应用升级效果
        knife.apply_effects(knife_upgrade.effects)
        knife.level = 3
        
        # 验证升级后的属性
        expected_stats = {
            'damage': 30,
            'attack_speed': 1.25,
            'projectile_speed': 400,
            'penetration': True,
            'knives_per_throw': 2,
            'spread_angle': 15,
            'lifetime': 3.0
        }
        
        for stat, value in expected_stats.items():
            self.assertEqual(knife.current_stats[stat], value,
                           f"{stat} should be {value} but got {knife.current_stats[stat]}")
            
    def test_passive_upgrade_health(self):
        """测试生命值被动升级效果"""
        initial_max_health = self.player.max_health
        
        # 获取1级生命强化升级
        health_upgrade = self.upgrade_manager.passive_upgrades['health'].levels[0]
        
        # 应用升级效果
        self.player.apply_passive_upgrade('health', 1, health_upgrade.effects)
        
        # 验证最大生命值增加了50
        self.assertEqual(self.player.max_health, initial_max_health + 50)
        
    def test_passive_upgrade_speed(self):
        """测试移动速度被动升级效果"""
        initial_speed = self.player.speed
        
        # 获取1级迅捷升级
        speed_upgrade = self.upgrade_manager.passive_upgrades['speed'].levels[0]
        
        # 应用升级效果
        self.player.apply_passive_upgrade('speed', 1, speed_upgrade.effects)
        
        # 验证移动速度提升了10%
        expected_speed = initial_speed * 1.1
        self.assertAlmostEqual(self.player.speed, expected_speed, places=1)
        
    def test_weapon_limit(self):
        """测试武器数量限制"""
        # 玩家初始有一个飞刀
        self.assertEqual(len(self.player.weapons), 1)
        
        # 尝试添加火球
        self.weapon_manager.add_weapon('fireball')
        self.assertEqual(len(self.player.weapons), 2)
        
        # 再次尝试添加火球（应该失败，因为已经有了）
        self.weapon_manager.add_weapon('fireball')
        self.assertEqual(len(self.player.weapons), 2)
        
    def test_passive_limit(self):
        """测试被动技能数量限制"""
        # 初始没有被动技能
        self.assertEqual(len(self.player.passives), 0)
        
        # 添加三个被动技能
        self.player.apply_passive_upgrade('health', 1, {'max_health': 50})
        self.player.apply_passive_upgrade('speed', 1, {'speed': 0.1})
        self.player.apply_passive_upgrade('health_regen', 1, {'health_regen': 1})
        
        self.assertEqual(len(self.player.passives), 3)
        
        # 尝试添加第四个被动技能（应该失败）
        result = self.player.apply_passive_upgrade('new_passive', 1, {'some_effect': 1})
        self.assertFalse(result)
        self.assertEqual(len(self.player.passives), 3)
        
    def tearDown(self):
        """测试后的清理"""
        pygame.quit()

if __name__ == '__main__':
    unittest.main() 