from ..enemy import Enemy
from ...resource_manager import resource_manager
import pygame

class Ghost(Enemy):
    def __init__(self, x, y, scale=1.0):
        # 幽灵的基础属性
        health = 50
        damage = 10
        speed = 100
        
        super().__init__(x, y, health, damage, speed, scale)
        self.type = 'ghost'
        self.score_value = 10
        
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
        """加载幽灵的动画"""
        # 加载精灵表
        idle_spritesheet = resource_manager.load_spritesheet(
            'ghost_idle_spritesheet', 'images/enemy/Ghost_Idle.png')
        walk_spritesheet = resource_manager.load_spritesheet(
            'ghost_walk_spritesheet', 'images/enemy/Ghost_Idle.png')
        hurt_spritesheet = resource_manager.load_spritesheet(
            'ghost_hurt_spritesheet', 'images/enemy/Ghost_Idle.png')
        
        # 创建动画
        self.animations = {
            'idle': resource_manager.create_animation('enemy_idle', idle_spritesheet, 
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=0.0333),  # 30 FPS
            'walk': resource_manager.create_animation('enemy_walk', walk_spritesheet,
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=0.0333),  # 30 FPS
            'hurt': resource_manager.create_animation('enemy_hurt', hurt_spritesheet,
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=0.0333),  # 30 FPS
        }