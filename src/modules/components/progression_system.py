"""
进阶系统组件
负责管理实体的经验值、等级和金币系统
"""

from .base_component import Component
from ..resource_manager import resource_manager

class ProgressionSystem(Component):
    """进阶系统组件，处理实体的经验值、等级和金币系统"""
    
    def __init__(self, owner, base_exp_multiplier=1.0):
        """
        初始化进阶系统组件
        
        Args:
            owner: 组件所属的实体
            base_exp_multiplier: 基础经验值倍率
        """
        super().__init__(owner)
        
        # 经验和等级
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        self.exp_growth_rate = 1.2  # 每级经验值增长率
        
        # 经验值倍率
        self.base_exp_multiplier = base_exp_multiplier
        self.exp_multiplier = base_exp_multiplier
        
        # 幸运值
        self.base_luck = 1.0
        self.luck = self.base_luck
        
        # 金币
        self.coins = 0
        
        # 回调函数
        self.on_level_up = None  # 升级时触发
        self.on_exp_gained = None  # 获得经验值时触发
        self.on_coins_gained = None  # 获得金币时触发
    
    def add_experience(self, amount):
        """
        添加经验值并检查是否升级
        
        Args:
            amount: 经验值数量
            
        Returns:
            bool: 如果升级返回True，否则返回False
        """
        actual_amount = amount * self.exp_multiplier
        self.experience += actual_amount
        
        if self.on_exp_gained:
            self.on_exp_gained(actual_amount)
        
        # 不立即升级，只返回是否达到升级条件
        return self.experience >= self.exp_to_next_level
    
    def level_up(self):
        """
        处理升级逻辑
        
        Returns:
            bool: 升级成功返回True
        """
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * self.exp_growth_rate)
        
        # 播放升级音效
        resource_manager.play_sound("level_up")
        
        # 触发升级回调
        if self.on_level_up:
            self.on_level_up(self.level)
            
        # 检查是否需要再次升级（如果经验值仍然超过下一级所需）
        if self.experience >= self.exp_to_next_level:
            self.level_up()
            
        return True
    
    def add_coins(self, amount):
        """
        添加金币
        
        Args:
            amount: 金币数量
            
        Returns:
            int: 当前金币总数
        """
        self.coins += amount
        
        # 播放收集金币音效
        resource_manager.play_sound("collect_coin")
        
        # 触发金币获得回调
        if self.on_coins_gained:
            self.on_coins_gained(amount)
            
        return self.coins
    
    def set_exp_multiplier(self, multiplier):
        """
        设置经验值倍率
        
        Args:
            multiplier: 新的经验值倍率
        """
        self.exp_multiplier = multiplier
    
    def get_level_progress(self):
        """
        获取当前等级进度
        
        Returns:
            float: 当前等级进度（0-1之间）
        """
        return self.experience / self.exp_to_next_level 

    def set_luck(self, luck_multiplier):
        """
        设置幸运值
        
        Args:
            luck_multiplier: 新的幸运值倍率
        """
        self.luck = self.base_luck * luck_multiplier 