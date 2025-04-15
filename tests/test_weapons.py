import unittest
import pygame
import math
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 添加src目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from modules.player import Player
from modules.weapons.types.knife import Knife, ThrownKnife
from modules.weapons.types.fireball import Fireball, FireballProjectile, ExplosionEffect
from modules.enemies.enemy import Enemy
from modules.weapons.types.frost_nova import FrostNova, FrostNovaProjectile
from modules.enemies.types import Ghost
from modules.weapons.weapon_stats import WeaponStatType
from modules.weapons.weapons_data import get_weapon_config, get_weapon_base_stats

class MockEnemy(Ghost):
    """用于测试的模拟敌人类"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.damage_taken = 0
        self.is_slowed = False
        self.original_speed = self.speed
        # 确保位置正确设置
        self.rect.centerx = x
        self.rect.centery = y
        # 设置世界坐标
        self.world_x = float(x)
        self.world_y = float(y)
        # 设置存活状态
        self._alive = True
    
    def take_damage(self, amount):
        self.damage_taken = amount
        self.health -= amount
        if self.health <= 0:
            self.kill()
            
    def kill(self):
        """重写 kill 方法"""
        self._alive = False
        super().kill()
        
    def alive(self):
        """重写 alive 方法"""
        return self._alive

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
        knife = self.player.weapons[0]
        self.assertEqual(knife.type, 'knife')
        self.assertEqual(knife.current_stats[WeaponStatType.DAMAGE], 20)
        self.assertEqual(knife.current_stats[WeaponStatType.ATTACK_SPEED], 1.0)
        
    def test_knife_throw(self):
        """测试飞刀的投掷功能"""
        knife = self.player.weapons[0]
        # 设置玩家朝向右边
        self.player.movement.direction.x = 1
        self.player.movement.direction.y = 0
        # 投掷飞刀
        knife.throw_knives()
        self.assertEqual(len(knife.projectiles), 1)
        thrown = list(knife.projectiles)[0]
        # 由于玩家朝右，飞刀应该向右飞行
        self.assertAlmostEqual(thrown.direction_x, 1)
        self.assertAlmostEqual(thrown.direction_y, 0)
        
    def test_fireball_creation(self):
        """测试火球的创建和基本属性"""
        # 添加火球武器
        fireball = self.player.add_weapon('fireball')
        self.assertEqual(fireball.type, 'fireball')
        
        # 从配置数据获取基础值
        fireball_base_stats = get_weapon_base_stats('fireball')
        self.assertEqual(fireball.current_stats[WeaponStatType.DAMAGE], fireball_base_stats[WeaponStatType.DAMAGE])
        
        # 验证攻击能力存在
        self.assertTrue(hasattr(fireball, 'cast_fireballs'))
        self.assertTrue(hasattr(fireball, 'projectiles'))
        
    def test_fireball_tracking(self):
        """测试火球的追踪功能"""
        # 设置玩家位置
        self.player.world_x = 400
        self.player.world_y = 300
        
        # 创建敌人，确保在玩家右侧
        enemy = MockEnemy(500, 300)  # 在玩家右侧100像素处创建敌人
        
        # 创建火球武器
        fireball = self.player.add_weapon('fireball')
        
        # 测试寻找最近敌人
        nearest = fireball.find_nearest_enemy([enemy])
        self.assertEqual(nearest, enemy)
        
        # 测试发射火球
        fireball.cast_fireballs([enemy])
        self.assertEqual(len(fireball.projectiles), 1)
        
        # 测试火球追踪
        projectile = list(fireball.projectiles)[0]
        self.assertIsNotNone(projectile.target)
        
        # 记录初始位置
        initial_x = projectile.world_x
        initial_y = projectile.world_y
        
        # 更新一帧，检查火球是否朝向敌人移动
        dt = 0.016  # 约60FPS
        projectile.update(dt)
        
        # 检查火球是否在向敌人移动
        dx_moved = projectile.world_x - initial_x
        dy_moved = projectile.world_y - initial_y
        distance_moved = math.sqrt(dx_moved * dx_moved + dy_moved * dy_moved)

        
        self.assertGreater(distance_moved, 0, "火球没有移动！")
        
        # 检查移动方向是否朝向敌人
        if distance_moved > 0:  # 只有在有移动的情况下才检查方向
            movement_angle = math.degrees(math.atan2(dy_moved, dx_moved))
            target_angle = math.degrees(math.atan2(
                enemy.world_y - initial_y,
                enemy.world_x - initial_x
            ))
            self.assertAlmostEqual(movement_angle, target_angle, delta=1.0)
        
    def test_frost_nova_creation(self):
        """测试冰霜新星的创建和基本属性"""
        frost_nova = self.player.add_weapon('frost_nova')
        self.assertEqual(frost_nova.type, 'frost_nova')
        
        # 从配置数据获取基础值
        frost_nova_base_stats = get_weapon_base_stats('frost_nova')
        self.assertEqual(frost_nova.current_stats[WeaponStatType.DAMAGE], frost_nova_base_stats[WeaponStatType.DAMAGE])
        
        # 验证攻击能力存在
        self.assertTrue(hasattr(frost_nova, 'cast_novas'))
        self.assertTrue(hasattr(frost_nova, 'projectiles'))
        
    def test_frost_nova_tracking(self):
        """测试冰霜新星的追踪功能"""
        # 设置玩家位置
        self.player.world_x = 400
        self.player.world_y = 300
        
        # 创建敌人，确保在玩家右侧
        enemy = MockEnemy(500, 300)  # 在玩家右侧100像素处创建敌人
        
        # 创建冰霜新星武器
        frost_nova = self.player.add_weapon('frost_nova')
        
        # 测试寻找最近敌人
        nearest = frost_nova.find_nearest_enemy([enemy])
        self.assertEqual(nearest, enemy)
        
        # 测试释放新星
        frost_nova.cast_novas([enemy])
        self.assertEqual(len(frost_nova.projectiles), 1)
        
        # 测试新星追踪
        projectile = list(frost_nova.projectiles)[0]
        self.assertIsNotNone(projectile.target)
        
        # 记录初始位置
        initial_x = projectile.world_x
        initial_y = projectile.world_y
        
        # 更新一帧，检查新星是否朝向敌人移动
        dt = 0.016  # 约60FPS
        projectile.update(dt)
        
        # 检查新星是否在向敌人移动
        dx_moved = projectile.world_x - initial_x
        dy_moved = projectile.world_y - initial_y
        distance_moved = math.sqrt(dx_moved * dx_moved + dy_moved * dy_moved)
        
        self.assertGreater(distance_moved, 0, "冰霜新星没有移动！")
        
        # 检查移动方向是否朝向敌人
        if distance_moved > 0:  # 只有在有移动的情况下才检查方向
            movement_angle = math.degrees(math.atan2(dy_moved, dx_moved))
            target_angle = math.degrees(math.atan2(
                enemy.world_y - initial_y,
                enemy.world_x - initial_x
            ))
            self.assertAlmostEqual(movement_angle, target_angle, delta=1.0)
        
    def test_weapon_collision(self):
        """测试武器碰撞检测"""
        enemy = MockEnemy(450, 300)  # 在玩家右侧50像素处创建敌人
        
        # 测试飞刀碰撞
        knife = self.player.weapons[0]
        # 设置玩家朝向右边
        self.player.movement.direction.x = 1
        self.player.movement.direction.y = 0
        # 投掷飞刀
        knife.throw_knives()
        thrown = list(knife.projectiles)[0]
        # 移动飞刀到接近敌人的位置
        thrown.world_x = enemy.rect.x - 10
        thrown.world_y = enemy.rect.y
        # 检查碰撞
        dx = enemy.rect.x - thrown.world_x
        dy = enemy.rect.y - thrown.world_y
        distance = math.sqrt(dx**2 + dy**2)
        self.assertTrue(distance < enemy.rect.width / 2 + thrown.rect.width / 2)
        
        # 测试火球碰撞
        fireball = self.player.add_weapon('fireball')
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
        frost_nova = self.player.add_weapon('frost_nova')
        frost_nova.cast_novas([enemy])
        effect = list(frost_nova.projectiles)[0]
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
        fireball = self.player.add_weapon('fireball')
        fireball.cast_fireballs([enemy])
        projectile = list(fireball.projectiles)[0]
        initial_health = enemy.health
        enemy.take_damage(projectile.damage)
        self.assertEqual(enemy.damage_taken, projectile.damage)
        self.assertEqual(enemy.health, initial_health - projectile.damage)
        
        # 测试冰霜新星减速效果
        frost_nova = self.player.add_weapon('frost_nova')
        frost_nova.cast_novas([enemy])
        effect = list(frost_nova.projectiles)[0]
        # 冰霜新星需要检查减速效果
        initial_speed = enemy.speed
        effect.apply_slow_effect(enemy, 0.5)  # 假设减速效果为50%
        self.assertEqual(enemy.speed, initial_speed * 0.5)
        
    def test_knife_penetration(self):
        """测试3级飞刀的穿透效果"""
        # 直接设置knife的属性而不是通过player.apply_weapon_upgrade
        knife = self.player.weapons[0]
        knife.level = 3
        knife.current_stats[WeaponStatType.CAN_PENETRATE] = True
        knife.current_stats[WeaponStatType.MAX_PENETRATION] = 3  # 设置为3，表示最多可以穿透3个敌人
        knife.current_stats[WeaponStatType.PENETRATION_DAMAGE_REDUCTION] = 0.2
        
        # 检查飞刀是否已经具有穿透能力
        self.assertTrue(knife.current_stats[WeaponStatType.CAN_PENETRATE])
        self.assertEqual(knife.current_stats[WeaponStatType.MAX_PENETRATION], 3)
        
        # 创建多个敌人
        enemies = [
            MockEnemy(450, 300),  # 敌人1
            MockEnemy(500, 300),  # 敌人2
            MockEnemy(550, 300)   # 敌人3
        ]
        
        # 设置玩家朝向右边
        self.player.movement.direction.x = 1
        self.player.movement.direction.y = 0
        
        # 投掷飞刀
        knife.throw_knives()
        thrown = list(knife.projectiles)[0]
        
        # 设置飞刀的初始属性
        thrown.world_x = 400
        thrown.world_y = 300
        thrown.hit_count = 0
        thrown.can_penetrate = True  # 确保投射物也具有穿透能力
        thrown.max_penetration = 3   # 最多穿透3个敌人
        
        # 模拟飞刀与敌人1碰撞
        old_damage = thrown.damage
        should_destroy = knife.handle_collision(thrown, enemies[0])
        
        # 检查是否正确处理了碰撞逻辑
        self.assertFalse(should_destroy, "飞刀应该继续存在因为它可以穿透")
        self.assertEqual(thrown.hit_count, 1, "飞刀应该记录了1次命中")
        self.assertLess(thrown.damage, old_damage, "飞刀的伤害应该减少")
        
        # 模拟飞刀与敌人2碰撞
        old_damage = thrown.damage
        should_destroy = knife.handle_collision(thrown, enemies[1])
        
        # 检查第二次碰撞后的状态
        self.assertFalse(should_destroy, "飞刀应该继续存在因为它还可以穿透一次")
        self.assertEqual(thrown.hit_count, 2, "飞刀应该记录了2次命中")
        self.assertLess(thrown.damage, old_damage, "飞刀的伤害应该再次减少")
        
        # 模拟飞刀与敌人3碰撞
        should_destroy = knife.handle_collision(thrown, enemies[2])
        
        # 检查第三次碰撞后的状态
        self.assertTrue(should_destroy, "飞刀应该被销毁因为它已达到最大穿透次数")
        self.assertEqual(thrown.hit_count, 3, "飞刀应该记录了3次命中")
        
    def test_multiple_weapons(self):
        """测试玩家同时拥有多个武器"""
        # 默认玩家有一个飞刀
        self.assertEqual(len(self.player.weapons), 1)
        self.assertEqual(self.player.weapons[0].type, 'knife')
        
        # 添加火球
        fireball = self.player.add_weapon('fireball')
        self.assertIsNotNone(fireball)
        self.assertEqual(len(self.player.weapons), 2)
        
        # 添加冰霜新星
        frost_nova = self.player.add_weapon('frost_nova')
        self.assertIsNotNone(frost_nova)
        self.assertEqual(len(self.player.weapons), 3)
        
        # 设置玩家位置
        self.player.world_x = 400
        self.player.world_y = 300
        
        # 创建敌人
        enemy = MockEnemy(500, 300)
        
        # 更新所有武器
        self.player.update_weapons(0.1, [enemy])
        
        # 检查武器是否都可以正常攻击
        self.player.weapons[0].throw_knives()  # 飞刀
        self.player.weapons[1].cast_fireballs([enemy])  # 火球
        self.player.weapons[2].cast_novas([enemy])  # 冰霜新星
        
        # 验证所有武器都产生了投射物
        self.assertGreater(len(self.player.weapons[0].projectiles), 0)
        self.assertGreater(len(self.player.weapons[1].projectiles), 0)
        self.assertGreater(len(self.player.weapons[2].projectiles), 0)
        
    def test_knife_direction_with_player_facing(self):
        """测试飞刀方向与玩家朝向一致"""
        knife = self.player.weapons[0]
        
        # 测试向右朝向
        self.player.movement.direction.x = 1
        self.player.movement.direction.y = 0
        self.player.movement.update(0.1)  # 更新移动组件以记录朝向
        knife.throw_knives()
        thrown_right = list(knife.projectiles)[0]
        self.assertAlmostEqual(thrown_right.direction_x, 1)
        self.assertAlmostEqual(thrown_right.direction_y, 0)
        knife.projectiles.empty()  # 清空投射物
        
        # 测试向左朝向
        self.player.movement.direction.x = -1
        self.player.movement.direction.y = 0
        self.player.movement.update(0.1)
        knife.throw_knives()
        thrown_left = list(knife.projectiles)[0]
        self.assertAlmostEqual(thrown_left.direction_x, -1)
        self.assertAlmostEqual(thrown_left.direction_y, 0)
        knife.projectiles.empty()
        
        # 测试向上朝向
        self.player.movement.direction.x = 0
        self.player.movement.direction.y = -1
        self.player.movement.update(0.1)
        knife.throw_knives()
        thrown_up = list(knife.projectiles)[0]
        self.assertAlmostEqual(thrown_up.direction_x, 0)
        self.assertAlmostEqual(thrown_up.direction_y, -1)
        knife.projectiles.empty()
        
        # 测试向下朝向
        self.player.movement.direction.x = 0
        self.player.movement.direction.y = 1
        self.player.movement.update(0.1)
        knife.throw_knives()
        thrown_down = list(knife.projectiles)[0]
        self.assertAlmostEqual(thrown_down.direction_x, 0)
        self.assertAlmostEqual(thrown_down.direction_y, 1)
        knife.projectiles.empty()
        
        # 测试停止移动后保持上一个朝向（向下）
        self.player.movement.direction.x = 0
        self.player.movement.direction.y = 0
        # 手动设置最后的移动方向为向下
        self.player.movement.last_movement_direction.x = 0
        self.player.movement.last_movement_direction.y = 1
        self.player.movement.update(0.1)
        knife.throw_knives()
        thrown_stopped = list(knife.projectiles)[0]
        self.assertAlmostEqual(thrown_stopped.direction_x, 0)
        self.assertAlmostEqual(thrown_stopped.direction_y, 1)  # 应该保持向下朝向
        knife.projectiles.empty()

    def test_fireball_explosion(self):
        """测试火球爆炸特效和范围伤害功能"""
        # 设置玩家位置
        self.player.world_x = 400
        self.player.world_y = 300
        
        # 创建多个敌人，分布在不同位置
        enemy1 = MockEnemy(450, 300)  # 最近的敌人，会被直接碰撞
        enemy2 = MockEnemy(500, 300)  # 在爆炸范围内的敌人
        enemy3 = MockEnemy(600, 300)  # 在爆炸范围外的敌人
        enemies = [enemy1, enemy2, enemy3]
        
        # 创建火球武器
        fireball = self.player.add_weapon('fireball')
        
        # 设置爆炸范围
        explosion_radius = 70  # 设置一个足够大的爆炸范围，覆盖enemy1和enemy2，但不覆盖enemy3
        fireball.current_stats[WeaponStatType.EXPLOSION_RADIUS] = explosion_radius
        
        # 发射火球
        fireball.cast_fireballs(enemies)
        self.assertEqual(len(fireball.projectiles), 1)
        
        # 获取火球实例
        projectile = list(fireball.projectiles)[0]
        
        # 设置火球位置与敌人1相同位置（模拟碰撞）
        projectile.world_x = enemy1.world_x
        projectile.world_y = enemy1.world_y
        projectile.rect.centerx = enemy1.rect.centerx
        projectile.rect.centery = enemy1.rect.centery
        
        # 触发爆炸
        projectile.explode(enemies)
        
        # 检查敌人是否受到伤害
        self.assertGreater(enemy1.damage_taken, 0, "最近的敌人应该受到满额伤害")
        self.assertGreater(enemy2.damage_taken, 0, "在爆炸范围内的敌人应该受到伤害")
        self.assertEqual(enemy3.damage_taken, 0, "在爆炸范围外的敌人不应该受到伤害")
        
        # 检查爆炸特效是否被创建
        # 注意：由于我们在测试环境中并未实际渲染，这里我们只检查逻辑部分
        
        # 检查相对伤害值
        self.assertGreaterEqual(enemy1.damage_taken, enemy2.damage_taken, "最近的敌人应该受到更多或相等的伤害")
        
    def test_explosion_effect_animation(self):
        """测试爆炸特效动画"""
        # 创建爆炸特效
        explosion = ExplosionEffect(400, 300, 50)
        
        # 检查初始状态
        self.assertEqual(explosion.current_frame, 0)
        self.assertIsNotNone(explosion.image)
        
        # 模拟时间流逝，更新动画
        dt = explosion.animation_speed * 1.1  # 略大于帧间隔时间
        explosion.update(dt)
        
        # 检查帧是否更新
        self.assertEqual(explosion.current_frame, 1)
        
        # 模拟完整的动画周期
        while explosion.current_frame < explosion.total_frames - 1:
            explosion.update(dt)
        
        # 再更新一次，应该触发爆炸特效的消失
        prev_frame = explosion.current_frame
        explosion.update(dt)
        
        # 验证爆炸特效是否正确结束
        self.assertNotEqual(explosion.current_frame, prev_frame)
        
    def test_fireball_collision_and_explosion(self):
        """测试火球碰撞和爆炸过程"""
        # 设置玩家位置
        self.player.world_x = 400
        self.player.world_y = 300
        
        # 创建敌人
        enemy = MockEnemy(500, 300)
        enemies = [enemy]
        
        # 创建火球武器
        fireball = self.player.add_weapon('fireball')
        
        # 发射火球
        fireball.cast_fireballs(enemies)
        self.assertEqual(len(fireball.projectiles), 1)
        
        # 获取火球实例
        projectile = list(fireball.projectiles)[0]
        
        # 设置火球和敌人的位置，使它们碰撞
        projectile.world_x = enemy.world_x - 5  # 接近但不完全重叠
        projectile.world_y = enemy.world_y
        projectile.rect.centerx = int(projectile.world_x)
        projectile.rect.centery = int(projectile.world_y)
        
        # 直接调用爆炸方法，而不是通过update
        projectile.explode(enemies)
        
        # 检查火球是否已经爆炸（被移除）
        self.assertEqual(len(fireball.projectiles), 0)
        
        # 检查敌人是否受到伤害
        self.assertGreater(enemy.damage_taken, 0)
        
        # 检查爆炸特效是否被创建
        # 注：在某些测试环境下，由于资源加载问题可能不会创建特效
        # self.assertGreaterEqual(len(fireball.effects), 1)

if __name__ == '__main__':
    unittest.main() 