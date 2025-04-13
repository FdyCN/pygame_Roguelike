import os
import json
import pygame
from datetime import datetime
import pickle

class SaveSystem:
    def __init__(self):
        # 创建存档目录
        self.save_dir = "saves"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
    def save_game(self, slot_id, game_state, screen):
        """
        保存游戏状态到指定存档位置
        
        Args:
            slot_id: 存档位置（1-3）
            game_state: 游戏状态对象
            screen: 当前游戏画面，用于保存截图
        """
        # 确保slot_id在有效范围内
        if not 1 <= slot_id <= 3:
            raise ValueError("存档位置必须在1-3之间")
            
        # 创建存档数据
        # TODO: refactor, 存档读档似乎没有需求。
        save_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'player_data': {
                'health': game_state.player.health,
                'max_health': game_state.player.max_health,
                'level': game_state.player.level,
                'experience': game_state.player.experience,
                'coins': game_state.player.coins,
                'world_x': game_state.player.world_x,
                'world_y': game_state.player.world_y,
                'weapons': [(w.type, w.level) for w in game_state.player.weapons],
                'hero_type': game_state.player.hero_type,
                'component_states': {
                    'movement': {
                        'speed': game_state.player.movement.speed
                    },
                    'health': {
                        'defense': game_state.player.health_component.defense,
                        'health_regen': game_state.player.health_component.health_regen
                    },
                    'progression': {
                        'exp_multiplier': game_state.player.progression.exp_multiplier,
                        'luck': game_state.player.progression.luck
                    },
                    'passive': {
                        'passive_levels': game_state.player.passive_levels
                    }
                }
            },
            'game_data': {
                'kill_num': game_state.kill_num,
                'game_time': game_state.game_time,
                'level': game_state.level
            },
            'enemies_data': [
                {
                    'type': enemy.__class__.__name__,
                    'health': enemy.health,
                    'x': enemy.rect.x,
                    'y': enemy.rect.y
                }
                for enemy in game_state.enemy_manager.enemies
            ]
        }
        
        # 保存截图
        screenshot_path = os.path.join(self.save_dir, f'save_{slot_id}_screenshot.png')
        pygame.image.save(screen, screenshot_path)
        
        # 保存游戏数据
        save_path = os.path.join(self.save_dir, f'save_{slot_id}.json')
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
    def load_game(self, slot_id):
        """
        从指定存档位置加载游戏状态
        
        Args:
            slot_id: 存档位置（1-3）
            
        Returns:
            save_data: 存档数据，如果不存在则返回None
        """
        save_path = os.path.join(self.save_dir, f'save_{slot_id}.json')
        if not os.path.exists(save_path):
            return None
            
        with open(save_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def get_save_info(self, slot_id):
        """
        获取指定存档位置的基本信息
        
        Args:
            slot_id: 存档位置（1-3）
            
        Returns:
            dict: 包含截图路径和保存时间的字典，如果存档不存在则返回None
        """
        save_path = os.path.join(self.save_dir, f'save_{slot_id}.json')
        screenshot_path = os.path.join(self.save_dir, f'save_{slot_id}_screenshot.png')
        
        if not os.path.exists(save_path):
            return None
            
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)
            
        return {
            'screenshot_path': screenshot_path if os.path.exists(screenshot_path) else None,
            'timestamp': save_data['timestamp'],
            'player_level': save_data['player_data']['level'],
            'game_time': save_data['game_data']['game_time'],
            'hero_type': save_data['player_data'].get('hero_type', 'ninja_frog')
        }
        
    def get_all_saves(self):
        """
        获取所有存档位置的信息
        
        Returns:
            list: 包含所有存档信息的列表
        """
        saves = []
        for slot_id in range(1, 4):
            save_info = self.get_save_info(slot_id)
            saves.append({
                'slot_id': slot_id,
                'info': save_info
            })
        return saves 