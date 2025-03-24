from ..enemy import Enemy
from ...resource_manager import resource_manager
import pygame

class Radish(Enemy):
    def __init__(self, x, y, scale=1.0):
        # 萝卜的基础属性
        health = 80
        damage = 15
        speed = 80
        
        super().__init__(x, y, health, damage, speed, scale)
        self.type = 'radish'
        self.score_value = 15
        
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
        """加载萝卜的动画"""
        # 加载精灵表
        idle_spritesheet = resource_manager.load_spritesheet(
            'radish_idle_spritesheet', 'images/enemy/radish_idle_30x38.png')
        walk_spritesheet = resource_manager.load_spritesheet(
            'radish_walk_spritesheet', 'images/enemy/radish_idle_30x38.png')
        hurt_spritesheet = resource_manager.load_spritesheet(
            'radish_hurt_spritesheet', 'images/enemy/radish_idle_30x38.png')
        
        # 创建动画
        self.animations = {
            'idle': resource_manager.create_animation(
                'radish_idle', idle_spritesheet,
                frame_width=30, frame_height=38,
                frame_count=6, row=0,
                frame_duration=0.0333  # 30 FPS
            ),
            'walk': resource_manager.create_animation(
                'radish_walk', walk_spritesheet,
                frame_width=30, frame_height=38,
                frame_count=6, row=0,
                frame_duration=0.0333
            ),
            'hurt': resource_manager.create_animation(
                'radish_hurt', hurt_spritesheet,
                frame_width=30, frame_height=38,
                frame_count=6, row=0,
                frame_duration=0.0333
            )
        } 