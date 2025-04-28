"""
移动组件
负责处理实体的移动、方向和速度计算
"""

import pygame
from .base_component import Component

class MovementComponent(Component):
    """移动组件，处理实体的移动逻辑"""
    
    def __init__(self, owner, speed=200):
        """
        初始化移动组件
        
        Args:
            owner: 组件所属的实体
            speed: 移动速度
        """
        super().__init__(owner)
        
        # 基础属性
        self.base_speed = speed
        self.speed = speed
        
        # 移动状态
        self.velocity = pygame.math.Vector2()
        self.direction = pygame.math.Vector2()
        self.last_movement_direction = pygame.math.Vector2(1, 0)
        
        # 移动输入状态
        self.moving = {
            'up': False, 
            'down': False, 
            'left': False, 
            'right': False
        }
        
        # 朝向状态
        self.current_direction = 'right'  # 当前移动方向文本描述
        self.facing_right = True
        
        # 边界检测
        self.boundaries = None  # (min_x, min_y, max_x, max_y)
        
    def set_boundaries(self, min_x, min_y, max_x, max_y):
        """
        设置移动边界
        
        Args:
            min_x: 最小X坐标
            min_y: 最小Y坐标
            max_x: 最大X坐标
            max_y: 最大Y坐标
        """
        self.boundaries = (min_x, min_y, max_x, max_y)
        
    def handle_event(self, event):
        """
        处理移动相关的输入事件
        
        Args:
            event: Pygame事件对象
        """
        if not self.enabled:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.moving['up'] = True
            elif event.key == pygame.K_s:
                self.moving['down'] = True
            elif event.key == pygame.K_a:
                self.moving['left'] = True
            elif event.key == pygame.K_d:
                self.moving['right'] = True
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.moving['up'] = False
            elif event.key == pygame.K_s:
                self.moving['down'] = False
            elif event.key == pygame.K_a:
                self.moving['left'] = False
            elif event.key == pygame.K_d:
                self.moving['right'] = False
        
        # 更新移动方向
        self._update_movement_direction()
        
    def update(self, dt):
        """
        更新移动状态
        
        Args:
            dt: 时间增量（秒）
        """
        if not self.enabled:
            return
            
        # 计算速度
        self.velocity = self.direction * self.speed
        
        # 更新实体位置
        if hasattr(self.owner, 'world_x') and hasattr(self.owner, 'world_y'):
            new_x = self.owner.world_x + self.velocity.x * dt
            new_y = self.owner.world_y + self.velocity.y * dt
            
            # 应用边界检测
            if self.boundaries:
                min_x, min_y, max_x, max_y = self.boundaries
                new_x = max(min_x, min(new_x, max_x))
                new_y = max(min_y, min(new_y, max_y))
            
            self.owner.world_x = new_x
            self.owner.world_y = new_y
    
    def _update_movement_direction(self):
        """更新移动方向和对应的角度"""
        # 确定当前移动方向
        if self.moving['right'] and not any([self.moving['up'], self.moving['down']]):
            self.current_direction = 'right'
        elif self.moving['right'] and self.moving['up']:
            self.current_direction = 'right_up'
        elif self.moving['right'] and self.moving['down']:
            self.current_direction = 'right_down'
        elif self.moving['left'] and not any([self.moving['up'], self.moving['down']]):
            self.current_direction = 'left'
        elif self.moving['left'] and self.moving['up']:
            self.current_direction = 'left_up'
        elif self.moving['left'] and self.moving['down']:
            self.current_direction = 'left_down'
        elif self.moving['up'] and not any([self.moving['left'], self.moving['right']]):
            self.current_direction = 'up'
        elif self.moving['down'] and not any([self.moving['left'], self.moving['right']]):
            self.current_direction = 'down'
            
        # 更新方向向量
        self.direction.x = float(self.moving['right']) - float(self.moving['left'])
        self.direction.y = float(self.moving['down']) - float(self.moving['up'])
        
        # 如果有移动输入，更新最后移动方向和角度
        if self.direction.x != 0 or self.direction.y != 0:
            self.last_movement_direction.x = self.direction.x
            self.last_movement_direction.y = self.direction.y
            
            # 标准化方向向量（如果长度不为0）
            if self.direction.length() > 0:
                self.direction = self.direction.normalize()
                
            # 更新朝向
            self.facing_right = 'right' in self.current_direction
            
    def is_moving(self):
        """
        检查是否正在移动
        
        Returns:
            bool: 如果正在移动返回True，否则返回False
        """
        return self.direction.length() > 0
        
    def set_speed(self, speed):
        """
        设置移动速度
        
        Args:
            speed: 新的移动速度
        """
        self.speed = speed 