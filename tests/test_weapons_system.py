import unittest
import sys
import os
sys.path.append('.')

from src.modules.weapons.weapons_data import get_weapon_config, get_weapon_base_stats
from src.modules.weapons.weapon_utils import create_weapon, get_available_weapon_types
from src.modules.weapons.weapon_stats import WeaponStatType

# 创建一个模拟玩家对象，用于测试
class MockPlayer:
    def __init__(self):
        self.world_x = 0
        self.world_y = 0
        self.attack_power = 1.0
        
        # 模拟Movement组件
        class MockMovement:
            def __init__(self):
                self.direction = type('obj', (object,), {'x': 1.0, 'y': 0.0})
                self.last_movement_direction = type('obj', (object,), {'x': 1.0, 'y': 0.0})
        
        self.movement = MockMovement()

class TestWeaponsSystem(unittest.TestCase):
    def setUp(self):
        self.player = MockPlayer()
        
    def test_weapon_config_data(self):
        """测试武器配置数据是否可以正确获取"""
        # 获取飞刀武器的配置
        knife_config = get_weapon_config('knife')
        
        # 检查基本属性
        self.assertIsNotNone(knife_config)
        self.assertEqual(knife_config['name'], '飞刀')
        self.assertEqual(knife_config['max_level'], 3)
        self.assertEqual(len(knife_config['levels']), 3)
        
        # 检查飞刀1级配置
        level1_config = knife_config['levels'][0]
        self.assertEqual(level1_config['level'], 1)
        self.assertEqual(level1_config['effects'][WeaponStatType.DAMAGE], 20)
        self.assertEqual(level1_config['effects'][WeaponStatType.PROJECTILES_PER_CAST], 1)
        
        # 检查飞刀3级配置
        level3_config = knife_config['levels'][2]
        self.assertEqual(level3_config['level'], 3)
        self.assertEqual(level3_config['effects'][WeaponStatType.DAMAGE], 30)
        self.assertEqual(level3_config['effects'][WeaponStatType.CAN_PENETRATE], True)
        
    def test_weapon_base_stats(self):
        """测试获取武器基础属性"""
        knife_stats = get_weapon_base_stats('knife')
        
        self.assertIsNotNone(knife_stats)
        self.assertEqual(knife_stats[WeaponStatType.DAMAGE], 20)
        self.assertEqual(knife_stats[WeaponStatType.ATTACK_SPEED], 1.0)
        
    def test_create_weapon(self):
        """测试武器创建工厂方法"""
        # 测试创建飞刀
        knife = create_weapon('knife', self.player)
        self.assertIsNotNone(knife)
        self.assertEqual(knife.type, 'knife')
        
        # 检查基础属性是否正确加载
        self.assertEqual(knife.current_stats[WeaponStatType.DAMAGE], 20)
        self.assertEqual(knife.current_stats[WeaponStatType.ATTACK_SPEED], 1.0)
        
        # 测试创建不存在的武器类型
        invalid_weapon = create_weapon('not_exist', self.player)
        self.assertIsNone(invalid_weapon)
        
    def test_available_weapon_types(self):
        """测试获取可用武器类型"""
        weapon_types = get_available_weapon_types()
        
        self.assertIsInstance(weapon_types, list)
        self.assertIn('knife', weapon_types)
        self.assertIn('fireball', weapon_types)
        
    def test_fireball_creation_with_config(self):
        """测试使用配置数据创建火球"""
        # 从配置数据获取基础属性
        fireball_base_stats = get_weapon_base_stats('fireball')
        self.assertIsNotNone(fireball_base_stats, "火球基础属性应该存在")
        
        # 创建火球武器
        fireball = create_weapon('fireball', self.player)
        self.assertIsNotNone(fireball, "应该能够创建火球武器")
        self.assertEqual(fireball.type, 'fireball', "武器类型应该是火球")
        
        # 检查火球属性是否从配置数据加载
        # 注意：这些值应该与weapons_data.py中的配置值匹配
        self.assertEqual(fireball.current_stats[WeaponStatType.DAMAGE], 
                        fireball_base_stats[WeaponStatType.DAMAGE], 
                        "火球伤害值应该与配置匹配")
        
        self.assertEqual(fireball.current_stats[WeaponStatType.BURN_DAMAGE], 
                        fireball_base_stats[WeaponStatType.BURN_DAMAGE], 
                        "火球燃烧伤害应该与配置匹配")
        
        self.assertEqual(fireball.current_stats[WeaponStatType.EXPLOSION_RADIUS], 
                        fireball_base_stats[WeaponStatType.EXPLOSION_RADIUS], 
                        "火球爆炸范围应该与配置匹配")
        
        # 创建投射物并检查属性
        mock_target = type('obj', (object,), {'rect': type('rect', (object,), {'centerx': 100, 'centery': 100}), 'alive': lambda: True})
        fireball_projectile = fireball._cast_single_fireball(mock_target)
        
        # 检查投射物是否从武器的当前状态获取属性
        self.assertEqual(fireball_projectile.damage, fireball.current_stats[WeaponStatType.DAMAGE])
        self.assertEqual(fireball_projectile.burn_damage, fireball.current_stats[WeaponStatType.BURN_DAMAGE])
        
    def test_frost_nova_creation_with_config(self):
        """测试使用配置数据创建冰霜新星"""
        # 从配置数据获取基础属性
        frost_nova_base_stats = get_weapon_base_stats('frost_nova')
        self.assertIsNotNone(frost_nova_base_stats, "冰霜新星基础属性应该存在")
        
        # 创建冰霜新星武器
        frost_nova = create_weapon('frost_nova', self.player)
        self.assertIsNotNone(frost_nova, "应该能够创建冰霜新星武器")
        self.assertEqual(frost_nova.type, 'frost_nova', "武器类型应该是冰霜新星")
        
        # 检查冰霜新星属性是否从配置数据加载
        # 注意：这些值应该与weapons_data.py中的配置值匹配
        self.assertEqual(frost_nova.current_stats[WeaponStatType.DAMAGE], 
                        frost_nova_base_stats[WeaponStatType.DAMAGE], 
                        "冰霜新星伤害值应该与配置匹配")
        
        self.assertEqual(frost_nova.current_stats[WeaponStatType.FREEZE_DURATION], 
                        frost_nova_base_stats[WeaponStatType.FREEZE_DURATION], 
                        "冰霜新星冻结持续时间应该与配置匹配")
        
        self.assertEqual(frost_nova.current_stats[WeaponStatType.SLOW_PERCENT], 
                        frost_nova_base_stats[WeaponStatType.SLOW_PERCENT], 
                        "冰霜新星减速百分比应该与配置匹配")
        
        # 创建投射物并检查属性
        mock_target = type('obj', (object,), {'rect': type('rect', (object,), {'centerx': 100, 'centery': 100}), 'alive': lambda: True})
        frost_nova_projectile = frost_nova._cast_single_nova(mock_target)
        
        # 检查投射物是否从武器的当前状态获取属性
        self.assertEqual(frost_nova_projectile.damage, frost_nova.current_stats[WeaponStatType.DAMAGE])
        # 检查减速效果是否正确转换
        self.assertEqual(frost_nova_projectile.slow_amount, frost_nova.current_stats[WeaponStatType.SLOW_PERCENT] / 100)
        
if __name__ == '__main__':
    unittest.main() 