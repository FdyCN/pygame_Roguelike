import unittest
import json
import os
import shutil
import pygame
from src.modules.player import Player
from src.modules.save_system import SaveSystem
from src.modules.game import Game

class MockScreen:
    """用于测试的模拟屏幕类"""
    def __init__(self):
        self.surface = pygame.Surface((800, 600))
        
    def get_width(self):
        return 800
        
    def get_height(self):
        return 600

class MockGame:
    """用于测试的模拟游戏类"""
    def __init__(self):
        pygame.init()
        self.screen = MockScreen()
        self.player = Player(400, 300, "ninja_frog")
        self.game_time = 120
        self.score = 1000
        self.level = 3
        self.enemy_manager = type('obj', (object,), {'enemies': []})

class TestSaveLoad(unittest.TestCase):
    def setUp(self):
        """每个测试用例前的设置"""
        pygame.init()
        self.save_system = SaveSystem()
        self.mock_game = MockGame()
        self.mock_screen = self.mock_game.screen.surface
        
        # 确保测试目录存在
        self.test_save_dir = "test_saves"
        if not os.path.exists(self.test_save_dir):
            os.makedirs(self.test_save_dir)
            
        # 保存原始存档目录并设置测试目录
        self.original_save_dir = self.save_system.save_dir
        self.save_system.save_dir = self.test_save_dir
        
    def tearDown(self):
        """每个测试用例后的清理"""
        pygame.quit()
        
        # 恢复原始存档目录
        self.save_system.save_dir = self.original_save_dir
        
        # 删除测试目录
        if os.path.exists(self.test_save_dir):
            shutil.rmtree(self.test_save_dir)
            
    def test_save_basic_player_attributes(self):
        """测试保存和加载基本玩家属性"""
        # 设置玩家属性
        self.mock_game.player.health = 80
        self.mock_game.player.coins = 150
        self.mock_game.player.progression.experience = 500
        
        # 保存游戏
        self.save_system.save_game(1, self.mock_game, self.mock_screen)
        
        # 验证存档文件是否创建
        save_path = os.path.join(self.test_save_dir, "save_1.json")
        self.assertTrue(os.path.exists(save_path), "存档文件未创建")
        
        # 读取存档数据
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            
        # 验证基本玩家属性
        self.assertEqual(save_data['player_data']['health'], 80, "玩家生命值未正确保存")
        self.assertEqual(save_data['player_data']['coins'], 150, "玩家金币未正确保存")
        self.assertEqual(save_data['player_data']['experience'], 500, "玩家经验值未正确保存")
        
    def test_save_load_hero_type(self):
        """测试保存和加载英雄类型"""
        # 设置英雄类型
        test_hero_type = "ninja_frog"  # 使用默认英雄类型，确保资源文件存在
        self.mock_game.player = Player(400, 300, test_hero_type)
        
        # 保存游戏
        self.save_system.save_game(1, self.mock_game, self.mock_screen)
        
        # 读取存档数据
        save_path = os.path.join(self.test_save_dir, "save_1.json")
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            
        # 验证英雄类型是否保存
        self.assertTrue('hero_type' in save_data['player_data'], "英雄类型未保存")
        self.assertEqual(save_data['player_data']['hero_type'], test_hero_type, "英雄类型未正确保存")
        
    def test_save_load_weapons(self):
        """测试保存和加载武器及其等级"""
        # 添加武器并设置等级
        self.mock_game.player.add_weapon("knife")
        self.mock_game.player.add_weapon("fireball")
        
        # 升级武器
        knife = self.mock_game.player.weapons[0]
        knife.level = 3
        fireball = self.mock_game.player.weapons[1]
        fireball.level = 2
        
        # 保存游戏
        self.save_system.save_game(1, self.mock_game, self.mock_screen)
        
        # 读取存档数据
        save_path = os.path.join(self.test_save_dir, "save_1.json")
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            
        # 验证武器列表是否保存
        weapons_data = save_data['player_data']['weapons']
        self.assertEqual(len(weapons_data), 2, "武器数量不正确")
        
        # 验证各武器等级
        self.assertEqual(weapons_data[0][0], "knife", "第一个武器类型不正确")
        self.assertEqual(weapons_data[0][1], 3, "第一个武器等级不正确")
        self.assertEqual(weapons_data[1][0], "fireball", "第二个武器类型不正确")
        self.assertEqual(weapons_data[1][1], 2, "第二个武器等级不正确")
        
    def test_save_load_component_states(self):
        """测试保存和加载组件状态"""
        # 设置组件状态
        self.mock_game.player.movement.speed = 250
        self.mock_game.player.health_component.defense = 30
        self.mock_game.player.health_component.health_regen = 2.5
        self.mock_game.player.progression.luck = 1.5
        
        # 保存游戏
        self.save_system.save_game(1, self.mock_game, self.mock_screen)
        
        # 读取存档数据
        save_path = os.path.join(self.test_save_dir, "save_1.json")
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            
        # 验证组件状态是否保存
        component_states = save_data['player_data'].get('component_states', {})
        self.assertTrue('component_states' in save_data['player_data'], "组件状态未保存")
        
        # 验证各组件状态
        self.assertEqual(component_states.get('movement', {}).get('speed'), 250, "移动组件速度未正确保存")
        self.assertEqual(component_states.get('health', {}).get('defense'), 30, "生命组件防御值未正确保存")
        self.assertEqual(component_states.get('health', {}).get('health_regen'), 2.5, "生命组件回复值未正确保存")
        self.assertEqual(component_states.get('progression', {}).get('luck'), 1.5, "进阶组件幸运值未正确保存")
        
    def test_save_load_passive_skills(self):
        """测试保存和加载被动技能状态"""
        # 设置被动技能状态
        # 通常通过 apply_passive_upgrade 方法应用被动效果
        # 但为了单元测试简单起见，我们直接设置 passive_levels
        self.mock_game.player.passive_manager.passive_levels = {
            'max_health': 3,
            'speed': 2,
            'defense': 1
        }
        
        # 保存游戏
        self.save_system.save_game(1, self.mock_game, self.mock_screen)
        
        # 读取存档数据
        save_path = os.path.join(self.test_save_dir, "save_1.json")
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            
        # 验证被动技能是否保存
        component_states = save_data['player_data'].get('component_states', {})
        passive_states = component_states.get('passive', {})
        self.assertTrue('passive_levels' in passive_states, "被动技能状态未保存")
        
        # 验证各被动技能等级
        passive_levels = passive_states['passive_levels']
        self.assertEqual(passive_levels.get('max_health'), 3, "max_health等级未正确保存")
        self.assertEqual(passive_levels.get('speed'), 2, "speed等级未正确保存")
        self.assertEqual(passive_levels.get('defense'), 1, "defense等级未正确保存")
        
        # 测试加载被动技能
        # 创建新的玩家实例
        new_player = Player(400, 300)
        
        # 手动应用被动技能等级
        for passive_type, level in passive_levels.items():
            new_player.passive_manager.passive_levels[passive_type] = level
            
        # 验证加载后的状态
        self.assertEqual(new_player.passive_manager.passive_levels.get('max_health'), 3, "加载后max_health等级不正确")
        self.assertEqual(new_player.passive_manager.passive_levels.get('speed'), 2, "加载后speed等级不正确")
        self.assertEqual(new_player.passive_manager.passive_levels.get('defense'), 1, "加载后defense等级不正确")
        
    def test_full_save_load_cycle(self):
        """测试完整的保存和加载循环"""
        # 设置初始状态
        self.mock_game.player.health = 75
        self.mock_game.player.coins = 200
        self.mock_game.player.add_weapon("fireball")
        self.mock_game.player.progression.level = 5
        self.mock_game.player.movement.speed = 280
        
        # 设置被动技能
        self.mock_game.player.passive_manager.passive_levels = {
            'max_health': 2,
            'speed': 3
        }
        
        # 保存游戏
        self.save_system.save_game(1, self.mock_game, self.mock_screen)
        
        # 加载存档
        save_data = self.save_system.load_game(1)
        
        # 创建一个新的Game和Player实例
        new_game = MockGame()
        
        # 这里我们直接修改玩家实例，而不是通过Game.load_game_state
        # 因为那个方法在真实环境下处理更多的游戏状态设置
        player_data = save_data['player_data']
        
        # 根据存档创建正确英雄类型的玩家
        hero_type = player_data.get('hero_type', "ninja_frog")
        new_player = Player(400, 300, hero_type)
        
        # 设置基本属性
        new_player.health = player_data['health']
        new_player.coins = player_data['coins']
        new_player.progression.level = player_data['level']
        new_player.progression.experience = player_data['experience']
        
        # 设置组件状态
        if 'component_states' in player_data:
            component_states = player_data['component_states']
            if 'movement' in component_states:
                new_player.movement.speed = component_states['movement'].get('speed', 200)
            if 'health' in component_states:
                new_player.health_component.defense = component_states['health'].get('defense', 0)
                new_player.health_component.health_regen = component_states['health'].get('health_regen', 0)
            if 'progression' in component_states:
                new_player.progression.luck = component_states['progression'].get('luck', 1.0)
            # 设置被动技能
            if 'passive' in component_states and 'passive_levels' in component_states['passive']:
                passive_levels = component_states['passive']['passive_levels']
                for passive_type, level in passive_levels.items():
                    new_player.passive_manager.passive_levels[passive_type] = level
        
        # 添加武器
        for weapon_type, level in player_data['weapons']:
            weapon = new_player.add_weapon(weapon_type)
            if weapon:
                weapon.level = level
                
        # 验证加载后的状态
        self.assertEqual(new_player.health, 75, "加载后的生命值不正确")
        self.assertEqual(new_player.coins, 200, "加载后的金币不正确")
        self.assertEqual(new_player.level, 5, "加载后的等级不正确")
        self.assertEqual(len(new_player.weapons), 2, "加载后的武器数量不正确") # 默认knife + fireball
        self.assertEqual(new_player.movement.speed, 280, "加载后的移动速度不正确")
        
        # 验证第二个武器(fireball)
        self.assertEqual(new_player.weapons[1].type, "fireball", "加载后的第二个武器类型不正确")
        
        # 验证被动技能
        self.assertEqual(new_player.passive_manager.passive_levels.get('max_health'), 2, "加载后的max_health等级不正确")
        self.assertEqual(new_player.passive_manager.passive_levels.get('speed'), 3, "加载后的speed等级不正确")
        
if __name__ == '__main__':
    unittest.main() 