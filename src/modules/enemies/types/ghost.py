from ..enemy import Enemy
from ...resource_manager import resource_manager
import pygame

class Ghost(Enemy):
    def __init__(self, x, y, enemy_type='ghost', difficulty="normal", level=1, scale=None):
        # 调用基类构造函数，传递敌人类型、难度和等级
        super().__init__(x, y, enemy_type, difficulty, level, scale)
        
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
        # 获取配置中的动画速度
        animation_speed = self.config.get("animation_speed", 0.0333)
        
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
                                                    frame_duration=animation_speed),
            'walk': resource_manager.create_animation('enemy_walk', walk_spritesheet,
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=animation_speed),
            'hurt': resource_manager.create_animation('enemy_hurt', hurt_spritesheet,
                                                    frame_width=44, frame_height=30,
                                                    frame_count=10, row=0,
                                                    frame_duration=animation_speed),
        }
        