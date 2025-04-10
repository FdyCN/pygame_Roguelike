from ..enemy import Enemy
from ...resource_manager import resource_manager
import pygame

class Bat(Enemy):
    def __init__(self, x, y, scale=2.0):
        # 蝙蝠的基础属性
        health = 300
        damage = 20
        speed = 120
        
        super().__init__(x, y, health, damage, speed, scale)
        self.type = 'bat'
        self.score_value = 100
        
        # 加载动画
        self.load_animations()
        
        # 设置初始图像
        self.current_animation = 'idle'
        self.image = self.animations[self.current_animation].get_current_frame()
        # 应用缩放
        original_size = self.image.get_size()
        new_size = (int(original_size[0] * self.scale), int(original_size[1] * self.scale))
        self.image = pygame.transform.scale(self.image, new_size)
        
    def load_animations(self):
        """加载蝙蝠的动画"""
        # 加载精灵表
        idle_spritesheet = resource_manager.load_spritesheet(
            'bat_idle_spritesheet', 'images/enemy/Bat_Flying_46x30.png')
        walk_spritesheet = resource_manager.load_spritesheet(
            'bat_walk_spritesheet', 'images/enemy/Bat_Flying_46x30.png')
        hurt_spritesheet = resource_manager.load_spritesheet(
            'bat_hurt_spritesheet', 'images/enemy/Bat_Flying_46x30.png')
        
        # 创建动画
        self.animations = {
            'idle': resource_manager.create_animation(
                'bat_idle', idle_spritesheet,
                frame_width=46, frame_height=30,
                frame_count=7, row=0,
                frame_duration=0.0333  # 12 FPS
            ),
            'walk': resource_manager.create_animation(
                'bat_walk', walk_spritesheet,
                frame_width=46, frame_height=30,
                frame_count=7, row=0,
                frame_duration=0.0333 
            ),
            'hurt': resource_manager.create_animation(
                'bat_hurt', hurt_spritesheet,
                frame_width=46, frame_height=30,
                frame_count=7, row=0,
                frame_duration=0.0333 
            )
        } 

    def attack(self, player, dt):
        """
        实现基类的抽象方法，对于蝙蝠，使用近战碰撞攻击
        
        Args:
            player: 攻击目标（玩家）
            dt: 时间增量
            
        Returns:
            bool: 攻击是否命中
        """
        return self.melee_attack(player) 