import unittest
import pygame
import math
from src.modules.player import Player
from src.modules.weapons.knife import Knife, ThrownKnife
from src.modules.weapons.fireball import Fireball, FireballProjectile
from src.modules.weapons.frost_nova import FrostNova, FrostNovaEffect
from src.modules.enemies.enemy import Enemy
from src.modules.enemies.types import Ghost

class MockEnemy(Ghost):
    """用于测试的模拟敌人类"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.damage_taken = 0
        self.is_slowed = False
        self.original_speed = self.speed
    
    def take_damage(self, amount):
        self.damage_taken = amount
        self.health -= amount

class TestWeapons(unittest.TestCase):
    def setUp(self):
        """每个测试用例前的设置"""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.player = Player(400, 300)
        
    def tearDown(self):
        """每个测试用例后的清理"""
        pygame.quit()
        
    def test_knife_creation(self):
        """测试飞刀的创建和基本属性"""
        knife = Knife(self.player)
        self.assertEqual(knife.type, 'knife')
        self.assertEqual(knife.current_stats['damage'], 20)
        self.assertEqual(knife.current_stats['attack_speed'], 1.0)
        
    def test_knife_throw(self):
        """测试飞刀的投掷功能"""
        knife = Knife(self.player)
        # 设置玩家朝向右边
        self.player.direction.x = 1
        self.player.direction.y = 0
        # 投掷飞刀
        knife.throw_knives()
        self.assertEqual(len(knife.thrown_knives), 1)
        thrown = list(knife.thrown_knives)[0]
        # 由于玩家朝右，飞刀应该向右飞行
        self.assertAlmostEqual(thrown.direction_x, 1)
        self.assertAlmostEqual(thrown.direction_y, 0)
        
    def test_fireball_creation(self):
        """测试火球的创建和基本属性"""
        fireball = Fireball(self.player)
        self.assertEqual(fireball.type, 'fireball')
        self.assertEqual(fireball.current_stats['damage'], 30)
        self.assertEqual(fireball.current_stats['attack_speed'], 0.8)
        
    def test_fireball_tracking(self):
        """测试火球的追踪功能"""
        fireball = Fireball(self.player)
        enemy = MockEnemy(500, 300)  # 在玩家右侧创建敌人
        
        # 测试寻找最近敌人
        nearest = fireball.find_nearest_enemy([enemy])
        self.assertEqual(nearest, enemy)
        
        # 测试发射火球
        fireball.cast_fireballs([enemy])
        self.assertEqual(len(fireball.projectiles), 1)
        
        # 测试火球追踪
        projectile = list(fireball.projectiles)[0]
        self.assertIsNotNone(projectile.target)
        
        # 更新一帧，检查火球是否朝向敌人移动
        projectile.update(0.016)  # 约60FPS
        dx = enemy.rect.x - projectile.world_x
        dy = enemy.rect.y - projectile.world_y
        angle = math.degrees(math.atan2(dy, dx))
        projectile_angle = math.degrees(math.atan2(projectile.direction_y, projectile.direction_x))
        self.assertAlmostEqual(angle, projectile_angle, delta=1.0)
        
    def test_frost_nova_creation(self):
        """测试冰霜新星的创建和基本属性"""
        frost_nova = FrostNova(self.player)
        self.assertEqual(frost_nova.type, 'frost_nova')
        self.assertEqual(frost_nova.current_stats['damage'], 25)
        self.assertEqual(frost_nova.current_stats['attack_speed'], 0.5)
        
    def test_frost_nova_tracking(self):
        """测试冰霜新星的追踪功能"""
        frost_nova = FrostNova(self.player)
        enemy = MockEnemy(500, 300)
        
        # 测试寻找最近敌人
        nearest = frost_nova.find_nearest_enemy([enemy])
        self.assertEqual(nearest, enemy)
        
        # 测试释放新星
        frost_nova.cast_frost_nova([enemy])
        self.assertEqual(len(frost_nova.effects), 1)
        
        # 测试新星追踪
        effect = list(frost_nova.effects)[0]
        self.assertIsNotNone(effect.target)
        
        # 更新一帧，检查新星是否朝向敌人移动
        effect.update(0.016)  # 约60FPS
        dx = enemy.rect.x - effect.world_x
        dy = enemy.rect.y - effect.world_y
        angle = math.degrees(math.atan2(dy, dx))
        effect_angle = math.degrees(math.atan2(effect.direction_y, effect.direction_x))
        self.assertAlmostEqual(angle, effect_angle, delta=1.0)
        
    def test_weapon_collision(self):
        """测试武器碰撞检测"""
        enemy = MockEnemy(450, 300)  # 在玩家右侧50像素处创建敌人
        
        # 测试飞刀碰撞
        knife = Knife(self.player)
        # 设置玩家朝向右边
        self.player.direction.x = 1
        self.player.direction.y = 0
        # 投掷飞刀
        knife.throw_knives()
        thrown = list(knife.thrown_knives)[0]
        # 移动飞刀到接近敌人的位置
        thrown.world_x = enemy.rect.x - 10
        thrown.world_y = enemy.rect.y
        # 检查碰撞
        dx = enemy.rect.x - thrown.world_x
        dy = enemy.rect.y - thrown.world_y
        distance = math.sqrt(dx**2 + dy**2)
        self.assertTrue(distance < enemy.rect.width / 2 + thrown.rect.width / 2)
        
        # 测试火球碰撞
        fireball = Fireball(self.player)
        fireball.cast_fireballs([enemy])
        projectile = list(fireball.projectiles)[0]
        # 移动火球到接近敌人的位置
        projectile.world_x = enemy.rect.x - 10
        projectile.world_y = enemy.rect.y
        # 检查碰撞
        dx = enemy.rect.x - projectile.world_x
        dy = enemy.rect.y - projectile.world_y
        distance = math.sqrt(dx**2 + dy**2)
        self.assertTrue(distance < enemy.rect.width / 2 + projectile.rect.width / 2)
        
        # 测试冰霜新星碰撞
        frost_nova = FrostNova(self.player)
        frost_nova.cast_frost_nova([enemy])
        effect = list(frost_nova.effects)[0]
        # 移动新星到接近敌人的位置
        effect.world_x = enemy.rect.x - 10
        effect.world_y = enemy.rect.y
        # 检查碰撞
        dx = enemy.rect.x - effect.world_x
        dy = enemy.rect.y - effect.world_y
        distance = math.sqrt(dx**2 + dy**2)
        self.assertTrue(distance < enemy.rect.width / 2 + effect.rect.width / 2)
        
    def test_weapon_effects(self):
        """测试武器效果"""
        enemy = MockEnemy(450, 300)
        
        # 测试火球伤害
        fireball = Fireball(self.player)
        fireball.cast_fireballs([enemy])
        projectile = list(fireball.projectiles)[0]
        initial_health = enemy.health
        enemy.take_damage(projectile.damage)
        self.assertEqual(enemy.damage_taken, projectile.damage)
        self.assertEqual(enemy.health, initial_health - projectile.damage)
        
        # 测试冰霜新星减速效果
        frost_nova = FrostNova(self.player)
        frost_nova.cast_frost_nova([enemy])
        effect = list(frost_nova.effects)[0]
        initial_speed = enemy.speed
        enemy.speed *= (1 - effect.slow_amount)
        self.assertLess(enemy.speed, initial_speed)

    def test_multiple_weapons(self):
        """测试玩家同时装备多个武器"""
        # 创建敌人
        enemy = MockEnemy(500, 300)  # 在玩家右侧创建敌人
        enemies = [enemy]

        # 为玩家添加三种武器
        self.player.add_weapon('knife')
        self.player.add_weapon('fireball')
        self.player.add_weapon('frost_nova')

        # 获取玩家的武器
        knife = next(w for w in self.player.weapons if w.type == 'knife')
        fireball = next(w for w in self.player.weapons if w.type == 'fireball')
        frost_nova = next(w for w in self.player.weapons if w.type == 'frost_nova')

        # 验证武器是否成功添加
        self.assertEqual(len(self.player.weapons), 3)
        self.assertIsNotNone(knife)
        self.assertIsNotNone(fireball)
        self.assertIsNotNone(frost_nova)

        # 验证每个武器的基础属性
        self.assertEqual(knife.current_stats['damage'], 20)
        self.assertEqual(fireball.current_stats['damage'], 30)
        self.assertEqual(frost_nova.current_stats['damage'], 25)

        # 设置玩家朝向
        self.player.direction.x = 1
        self.player.direction.y = 0

        # 测试每个武器的攻击功能
        knife.throw_knives()
        fireball.cast_fireballs(enemies)
        frost_nova.cast_frost_nova(enemies)

        # 验证每个武器都创建了正确的投射物/效果
        self.assertEqual(len(knife.thrown_knives), 1)
        self.assertEqual(len(fireball.projectiles), 1)
        self.assertEqual(len(frost_nova.effects), 1)

        # 更新一帧，测试所有武器的投射物/效果都能正常移动
        dt = 0.016  # 约60FPS
        knife.thrown_knives.update(dt)
        fireball.projectiles.update(dt)
        frost_nova.effects.update(dt)

        # 获取各个武器的投射物/效果
        thrown_knife = list(knife.thrown_knives)[0]
        fireball_proj = list(fireball.projectiles)[0]
        frost_effect = list(frost_nova.effects)[0]

        # 验证飞刀方向
        self.assertAlmostEqual(thrown_knife.direction_x, 1)
        self.assertAlmostEqual(thrown_knife.direction_y, 0)

        # 验证火球和冰霜新星的目标追踪
        self.assertEqual(fireball_proj.target, enemy)
        self.assertEqual(frost_effect.target, enemy)

        # 验证武器等级
        self.assertEqual(self.player.get_weapon_level('knife'), 1)
        self.assertEqual(self.player.get_weapon_level('fireball'), 1)
        self.assertEqual(self.player.get_weapon_level('frost_nova'), 1)

        # 验证武器冷却时间
        self.assertEqual(knife.attack_timer, 0)
        self.assertEqual(fireball.attack_timer, 0)
        self.assertEqual(frost_nova.attack_timer, 0)

        # 验证武器属性互不影响
        self.assertEqual(knife.current_stats['damage'], 20)
        self.assertEqual(fireball.current_stats['damage'], 30)
        self.assertEqual(frost_nova.current_stats['damage'], 25)
        
if __name__ == '__main__':
    unittest.main() 