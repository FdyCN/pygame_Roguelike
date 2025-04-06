import unittest
import pygame
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.player import Player
from src.modules.upgrade_system import UpgradeManager
from src.modules.game import Game
from src.modules.weapons.weapon_stats import WeaponStatType

class TestUpgrades(unittest.TestCase):
    def setUp(self):
        """测试前的初始化"""
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.player = Player(400, 300)
        self.upgrade_manager = UpgradeManager()
        
    def test_initial_knife_stats(self):
        """测试初始飞刀属性是否正确"""
        knife = self.player.weapons[0]  # 玩家的初始武器是飞刀
        self.assertEqual(knife.type, 'knife')
        self.assertEqual(knife.level, 1)
        
        # 验证初始属性是否与1级飞刀配置一致
        expected_stats = {
            WeaponStatType.DAMAGE: 20,
            WeaponStatType.ATTACK_SPEED: 1.0,
            WeaponStatType.PROJECTILE_SPEED: 400,
            WeaponStatType.CAN_PENETRATE: False,
            WeaponStatType.PROJECTILES_PER_CAST: 1,
            WeaponStatType.SPREAD_ANGLE: 0,
            WeaponStatType.LIFETIME: 3.0
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
        self.player.apply_weapon_upgrade('knife', 2, knife_upgrade.effects)
        
        # 验证升级后的属性
        expected_stats = {
            WeaponStatType.DAMAGE: 20,
            WeaponStatType.ATTACK_SPEED: 1.1,
            WeaponStatType.PROJECTILE_SPEED: 400,
            WeaponStatType.CAN_PENETRATE: False,
            WeaponStatType.PROJECTILES_PER_CAST: 2,
            WeaponStatType.SPREAD_ANGLE: 15,
            WeaponStatType.LIFETIME: 3.0
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
        self.player.apply_weapon_upgrade('knife', 3, knife_upgrade.effects)
        
        # 验证升级后的属性
        expected_stats = {
            WeaponStatType.DAMAGE: 30,
            WeaponStatType.ATTACK_SPEED: 1.25,
            WeaponStatType.PROJECTILE_SPEED: 400,
            WeaponStatType.CAN_PENETRATE: True,
            WeaponStatType.PROJECTILES_PER_CAST: 2,
            WeaponStatType.SPREAD_ANGLE: 15,
            WeaponStatType.LIFETIME: 3.0
        }
        
        for stat, value in expected_stats.items():
            self.assertEqual(knife.current_stats[stat], value,
                           f"{stat} should be {value} but got {knife.current_stats[stat]}")
            
    def test_passive_upgrade_health(self):
        """测试生命值被动升级效果"""
        initial_max_health = self.player.health_component.max_health
        
        # 获取1级生命强化升级
        health_upgrade = self.upgrade_manager.passive_upgrades['health'].levels[0]
        
        # 应用升级效果
        self.player.apply_passive_upgrade('health', 1, health_upgrade.effects)
        
        # 验证最大生命值增加了50
        self.assertEqual(self.player.health_component.max_health, initial_max_health + 50)
        
    def test_passive_upgrade_speed(self):
        """测试移动速度被动升级效果"""
        initial_speed = self.player.movement.speed
        
        # 获取1级迅捷升级
        speed_upgrade = self.upgrade_manager.passive_upgrades['speed'].levels[0]
        
        # 应用升级效果
        self.player.apply_passive_upgrade('speed', 1, speed_upgrade.effects)
        
        # 验证移动速度提升了10%
        expected_speed = initial_speed * 1.1
        self.assertAlmostEqual(self.player.movement.speed, expected_speed, places=1)
        
    def test_weapon_limit(self):
        """测试武器数量限制"""
        # 玩家初始有一个飞刀
        self.assertEqual(len(self.player.weapons), 1)
        
        # 尝试添加火球
        self.player.add_weapon('fireball')
        self.assertEqual(len(self.player.weapons), 2)
        
        # 再次尝试添加火球（应该失败，因为已经有了）
        result = self.player.add_weapon('fireball')
        self.assertIsNone(result)
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

    def test_upgrade_level(self):
        """测试武器升级等级"""
        # 检查初始状态 - 玩家应该有1级飞刀
        self.assertEqual(len(self.player.weapons), 1)
        knife = self.player.weapons[0]
        self.assertEqual(knife.level, 1)
        
        # 获取2级飞刀升级
        knife_upgrade_2 = self.upgrade_manager.weapon_upgrades['knife'].levels[1]
        # 第一次升级飞刀到2级
        self.player.apply_weapon_upgrade('knife', 2, knife_upgrade_2.effects)
        self.assertEqual(knife.level, 2)
        
        # 获取3级飞刀升级
        knife_upgrade_3 = self.upgrade_manager.weapon_upgrades['knife'].levels[2]
        # 第二次升级飞刀到3级
        self.player.apply_weapon_upgrade('knife', 3, knife_upgrade_3.effects)
        self.assertEqual(knife.level, 3)
        
    def test_passive_upgrade_health_regen(self):
        """测试生命恢复被动升级效果"""
        initial_health = self.player.health_component.health
        self.player.health_component.health = 50  # 设置当前生命值为50
        
        # 获取1级生命恢复升级
        health_regen_upgrade = self.upgrade_manager.passive_upgrades['health_regen'].levels[0]
        
        # 应用升级效果
        self.player.apply_passive_upgrade('health_regen', 1, {'health_regen': 1})
        
        # 验证生命恢复速率是否正确
        self.assertEqual(self.player.health_component.health_regen, 1)
        
        # 模拟1秒的游戏时间
        self.player.update(1.0)
        
        # 验证生命值是否恢复了1点
        self.assertEqual(self.player.health_component.health, 51)
        
    def test_passive_upgrade_defense(self):
        """测试防御力被动升级效果"""
        # 获取1级防御升级
        defense_upgrade = self.upgrade_manager.passive_upgrades['defense'].levels[0]
        
        # 应用升级效果（10%减伤）
        self.player.apply_passive_upgrade('defense', 1, {'defense': 0.1})
        
        # 验证防御力是否正确
        self.assertEqual(self.player.health_component.defense, 0.1)
        
        # 模拟受到100点伤害
        initial_health = self.player.health_component.health
        self.player.take_damage(100)
        
        # 验证实际受到的伤害是否为90点（100 * (1-0.1)）
        expected_health = initial_health - 90
        self.assertEqual(self.player.health_component.health, expected_health)
        
    def test_passive_upgrade_luck(self):
        """测试幸运值被动升级效果"""
        # 获取1级幸运升级
        luck_upgrade = self.upgrade_manager.passive_upgrades['luck'].levels[0]
        
        # 应用升级效果（增加20%幸运值）
        self.player.apply_passive_upgrade('luck', 1, {'luck': 0.2})
        
        # 验证幸运值是否正确（基础值1.0 * (1 + 0.2) = 1.2）
        self.assertAlmostEqual(self.player.progression.luck, 1.2)
        
    def test_multiple_passive_upgrades(self):
        """测试多个被动升级的叠加效果"""
        # 应用多个被动升级
        self.player.apply_passive_upgrade('health_regen', 1, {'health_regen': 1})  # 使用正确的1级效果值
        self.player.apply_passive_upgrade('defense', 1, {'defense': 0.1})  # 使用正确的1级效果值
        self.player.apply_passive_upgrade('luck', 1, {'luck': 0.5})  # 使用正确的1级效果值
        
        # 验证所有属性是否正确
        self.assertEqual(self.player.health_component.health_regen, 1)  # 1级生命恢复为1
        self.assertEqual(self.player.health_component.defense, 0.1)  # 1级防御为0.1
        self.assertAlmostEqual(self.player.progression.luck, 1.5)  # 基础值1.0 * (1 + 0.5) = 1.5
        
        # 测试生命恢复效果
        self.player.health_component.health = 50
        self.player.update(1.0)
        self.assertEqual(self.player.health_component.health, 51)  # 1秒恢复1点生命
        
        # 测试减伤效果
        initial_health = self.player.health_component.health
        damage = 100
        self.player.take_damage(damage)
        expected_damage = damage * (1 - 0.1)  # 100 * (1-0.1) = 90
        expected_health = max(0, initial_health - expected_damage)  # 确保生命值不会低于0
        self.assertEqual(self.player.health_component.health, expected_health)
        
    def test_passive_upgrade_limits(self):
        """测试被动升级的数量限制"""
        # 添加三个被动升级（应该成功）
        result1 = self.player.apply_passive_upgrade('health_regen', 1, {'health_regen': 1})
        result2 = self.player.apply_passive_upgrade('defense', 1, {'defense': 0.1})
        result3 = self.player.apply_passive_upgrade('luck', 1, {'luck': 0.2})
        
        self.assertTrue(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)
        
        # 尝试添加第四个被动升级（应该失败）
        result4 = self.player.apply_passive_upgrade('speed', 1, {'speed': 0.1})
        self.assertFalse(result4)
        
        # 验证只有三个被动升级生效
        self.assertEqual(len(self.player.passives), 3)
        
    def test_passive_upgrade_stacking(self):
        """测试相同被动升级的堆叠效果"""
        # 应用1级生命恢复
        self.player.apply_passive_upgrade('health_regen', 1, {'health_regen': 1})
        self.assertEqual(self.player.health_component.health_regen, 1)
        
        # 应用2级生命恢复（应该覆盖1级效果）
        self.player.apply_passive_upgrade('health_regen', 2, {'health_regen': 2})
        self.assertEqual(self.player.health_component.health_regen, 2)
        
        # 应用3级生命恢复（应该覆盖2级效果）
        self.player.apply_passive_upgrade('health_regen', 3, {'health_regen': 3})
        self.assertEqual(self.player.health_component.health_regen, 3)
        
    def test_passive_upgrade_pickup_range(self):
        """测试拾取范围被动升级效果"""
        initial_pickup_range = self.player.pickup_range
        
        # 获取1级拾取范围升级
        pickup_range_upgrade = self.upgrade_manager.passive_upgrades['pickup_range'].levels[0]
        
        # 应用升级效果
        self.player.apply_passive_upgrade('pickup_range', 1, pickup_range_upgrade.effects)
        
        # 验证拾取范围是否增加了25
        self.assertEqual(self.player.pickup_range, initial_pickup_range + 25)
        
        # 应用2级拾取范围升级
        pickup_range_upgrade = self.upgrade_manager.passive_upgrades['pickup_range'].levels[1]
        self.player.apply_passive_upgrade('pickup_range', 2, pickup_range_upgrade.effects)
        
        # 验证拾取范围是否增加到基础值+50
        self.assertEqual(self.player.pickup_range, initial_pickup_range + 50)
        
        # 应用3级拾取范围升级
        pickup_range_upgrade = self.upgrade_manager.passive_upgrades['pickup_range'].levels[2]
        self.player.apply_passive_upgrade('pickup_range', 3, pickup_range_upgrade.effects)
        
        # 验证拾取范围是否增加到基础值+100
        self.assertEqual(self.player.pickup_range, initial_pickup_range + 100)
        
    def test_pickup_range_effect_on_items(self):
        """测试拾取范围对物品拾取的实际影响"""
        from src.modules.items.item import Item
        
        # 创建一个测试物品，放在玩家拾取范围边缘
        test_item = Item(
            self.player.world_x + self.player.pickup_range - 1,  # 刚好在拾取范围内
            self.player.world_y,
            'exp'
        )
        
        # 验证物品会向玩家移动
        initial_x = test_item.world_x
        initial_y = test_item.world_y
        
        test_item.update(0.1, self.player)  # 更新一帧
        
        # 确认物品向玩家移动了
        self.assertLess(test_item.world_x, initial_x)
        self.assertEqual(test_item.world_y, initial_y)  # y坐标不变
        self.assertFalse(test_item.collected)  # 还未被收集
        
        # 将物品移动到玩家位置
        test_item.world_x = self.player.world_x
        test_item.world_y = self.player.world_y
        test_item.update(0.1, self.player)
        
        # 此时物品应该被收集
        self.assertTrue(test_item.collected)
        
        # 创建一个在基础拾取范围外但在升级后范围内的物品
        test_item2 = Item(
            self.player.world_x + self.player.pickup_range + 20,  # 在基础拾取范围外
            self.player.world_y,
            'exp'
        )
        
        # 应用拾取范围升级
        self.player.apply_passive_upgrade('pickup_range', 1, {'pickup_range': 25})
        
        # 验证物品会向玩家移动
        initial_x = test_item2.world_x
        initial_y = test_item2.world_y
        
        test_item2.update(0.1, self.player)  # 更新一帧
        
        # 确认物品向玩家移动了
        self.assertLess(test_item2.world_x, initial_x)
        self.assertEqual(test_item2.world_y, initial_y)  # y坐标不变
        self.assertFalse(test_item2.collected)  # 还未被收集
        
        # 将物品移动到玩家位置
        test_item2.world_x = self.player.world_x
        test_item2.world_y = self.player.world_y
        test_item2.update(0.1, self.player)
        
        # 此时物品应该被收集
        self.assertTrue(test_item2.collected)
        
    def test_luck_effect_on_item_drops(self):
        """测试幸运值对物品掉落概率的影响"""
        from src.modules.items.item_manager import ItemManager
        
        # 创建物品管理器
        item_manager = ItemManager()
        
        # 记录基础掉落数量（无幸运加成）
        base_coins = 0
        base_health = 0
        test_iterations = 1000
        
        # 测试基础掉落率
        for _ in range(test_iterations):
            item_manager.items.clear()  # 清空之前的物品
            item_manager.spawn_item(0, 0, None, None)  # 不传player，使用基础概率
            for item in item_manager.items:
                if item.item_type == 'coin':
                    base_coins += 1
                elif item.item_type == 'health':
                    base_health += 1
        
        # 计算基础掉落率
        base_coin_rate = base_coins / test_iterations
        base_health_rate = base_health / test_iterations
        
        # 测试幸运值加成后的掉落率
        self.player.progression.luck = 2.0  # 设置幸运值为200%
        lucky_coins = 0
        lucky_health = 0
        
        for _ in range(test_iterations):
            item_manager.items.clear()
            item_manager.spawn_item(0, 0, None, self.player)
            for item in item_manager.items:
                if item.item_type == 'coin':
                    lucky_coins += 1
                elif item.item_type == 'health':
                    lucky_health += 1
        
        # 计算幸运加成后的掉落率
        lucky_coin_rate = lucky_coins / test_iterations
        lucky_health_rate = lucky_health / test_iterations
        
        # 验证幸运值加成效果（幸运值加成后的掉落率应该高于基础掉落率）
        self.assertGreater(lucky_coin_rate, base_coin_rate)
        self.assertGreater(lucky_health_rate, base_health_rate)
        
    def test_pickup_range_passive_upgrade(self):
        """测试拾取范围被动升级的效果"""
        from src.modules.items.item import Item
        
        # 记录初始拾取范围
        initial_range = self.player.pickup_range
        
        # 创建一个在初始拾取范围外的物品
        test_item = Item(
            self.player.world_x + initial_range + 10,  # 放在初始范围外
            self.player.world_y,
            'exp'
        )
        
        # 验证物品不会被拾取
        test_item.update(0.1, self.player)
        self.assertFalse(test_item.collected)
        
        # 应用拾取范围升级
        self.player.apply_passive_upgrade('pickup_range', 1, {'pickup_range': 25})
        
        # 验证拾取范围已增加
        self.assertEqual(self.player.pickup_range, initial_range + 25)
        
        # 验证物品会向玩家移动
        initial_x = test_item.world_x
        initial_y = test_item.world_y
        
        test_item.update(0.1, self.player)  # 更新一帧
        
        # 确认物品向玩家移动了
        self.assertLess(test_item.world_x, initial_x)
        self.assertEqual(test_item.world_y, initial_y)  # y坐标不变
        self.assertFalse(test_item.collected)  # 还未被收集
        
        # 将物品移动到玩家位置
        test_item.world_x = self.player.world_x
        test_item.world_y = self.player.world_y
        test_item.update(0.1, self.player)
        
        # 此时物品应该被收集
        self.assertTrue(test_item.collected)
        
    def test_pickup_range_movement(self):
        """测试物品在拾取范围内的移动行为"""
        from src.modules.items.item import Item
        import math
        
        # 创建一个在拾取范围边缘的物品
        test_item = Item(
            self.player.world_x + self.player.pickup_range - 5,  # 放在拾取范围内
            self.player.world_y,
            'exp'
        )
        
        # 记录初始位置
        initial_x = test_item.world_x
        initial_y = test_item.world_y
        
        # 更新一帧
        dt = 0.1
        test_item.update(dt, self.player)
        
        # 验证物品向玩家移动
        dx = self.player.world_x - initial_x
        dy = self.player.world_y - initial_y
        distance = math.sqrt(dx**2 + dy**2)
        
        # 计算物品应该移动的距离
        expected_movement = test_item.attract_speed * dt
        
        # 计算实际移动距离
        actual_dx = self.player.world_x - test_item.world_x
        actual_dy = self.player.world_y - test_item.world_y
        actual_distance = math.sqrt(actual_dx**2 + actual_dy**2)
        
        # 验证物品移动速度正确（允许0.1的误差）
        self.assertAlmostEqual(distance - actual_distance, expected_movement, delta=0.1)
        
    def test_attack_power_effect_on_weapons(self):
        """测试攻击力加成对武器伤害的影响"""
        # 获取初始武器（飞刀）的基础伤害
        knife = self.player.weapons[0]
        base_damage = knife.current_stats[WeaponStatType.DAMAGE]
        
        # 应用攻击力加成
        self.player.apply_passive_upgrade('attack_power', 1, {'attack_power': 0.1})  # 10%攻击力提升
        
        # 验证武器伤害已经提升
        self.assertEqual(knife.current_stats[WeaponStatType.DAMAGE], int(base_damage * 1.1))
        
        # 应用更高级别的攻击力加成
        base_damage = knife.current_stats[WeaponStatType.DAMAGE]
        self.player.apply_passive_upgrade('attack_power', 2, {'attack_power': 0.2})  # 20%攻击力提升
        
        # 验证武器伤害已经更新
        self.assertEqual(knife.current_stats[WeaponStatType.DAMAGE], int(base_damage * 1.2))
        
        # 添加新武器并验证攻击力加成是否应用
        self.player.add_weapon('fireball')
        fireball = next(w for w in self.player.weapons if w.type == 'fireball')
        base_fireball_damage = fireball.current_stats[WeaponStatType.DAMAGE]
        
        # 验证新武器的伤害也受到攻击力加成
        expected_damage = int(25 * 1.2)  # 固定使用基础伤害 25 * 20% 加成 = 30
        self.assertEqual(fireball.current_stats[WeaponStatType.DAMAGE], expected_damage)
        
    def test_attack_power_on_weapon_upgrade(self):
        """测试武器升级时攻击力加成的正确应用"""
        # 获取初始武器（飞刀）
        knife = self.player.weapons[0]
        base_damage = knife.base_stats[WeaponStatType.DAMAGE]
        
        # 先应用攻击力加成
        self.player.apply_passive_upgrade('attack_power', 1, {'attack_power': 0.1})  # 10%攻击力提升
        
        # 应用武器升级
        upgrade_effects = {
            WeaponStatType.DAMAGE: 30,
            WeaponStatType.ATTACK_SPEED: 1.25,
            WeaponStatType.PROJECTILE_SPEED: 400,
            WeaponStatType.CAN_PENETRATE: True,
            WeaponStatType.PROJECTILES_PER_CAST: 2,
            WeaponStatType.SPREAD_ANGLE: 15,
            WeaponStatType.LIFETIME: 3.0
        }
        self.player.apply_weapon_upgrade('knife', 3, upgrade_effects)
        
        # 验证最终伤害是升级后的基础伤害乘以攻击力加成
        expected_damage = int(upgrade_effects[WeaponStatType.DAMAGE] * 1.1)  # 升级后的伤害 * 1.1
        self.assertEqual(knife.current_stats[WeaponStatType.DAMAGE], expected_damage)
        
    def tearDown(self):
        """测试后的清理"""
        pygame.quit()

if __name__ == '__main__':
    unittest.main() 