"""
被动技能管理组件
负责管理实体的被动技能系统，包括被动技能升级和效果应用
"""

from .base_component import Component

class PassiveManager(Component):
    """被动技能管理组件，处理实体的被动技能系统"""
    
    def __init__(self, owner, max_passives=3):
        """
        初始化被动技能管理组件
        
        Args:
            owner: 组件所属的实体
            max_passives: 最大被动技能数量
        """
        super().__init__(owner)
        
        # 被动技能列表和等级
        self.passives = {}  # 被动技能字典 {'health_up': {...}, 'speed_up': {...}}
        self.passive_levels = {}  # 被动技能等级字典 {'health_up': 1, 'speed_up': 1}
        self.max_passives = max_passives
        
        # 属性回调
        self.on_stats_changed = None  # 当属性变化时的回调函数
    
    def apply_passive_upgrade(self, passive_type, level, effects):
        """
        应用被动技能升级
        
        Args:
            passive_type: 被动技能类型
            level: 升级后的等级
            effects: 升级效果
            
        Returns:
            bool: 成功应用升级返回True，失败返回False
        """
        # 特殊情况：金币奖励（直接应用，不作为被动技能）
        if passive_type == 'coins':
            if hasattr(self.owner, 'coins'):
                self.owner.coins += effects.get('coins', 0)
            return True
        
        # 已有该被动技能 - 升级
        if passive_type in self.passive_levels:
            self.passive_levels[passive_type] = level
            self.passives[passive_type] = effects
            
            # 通知属性变化
            if self.on_stats_changed:
                self.on_stats_changed()
                
            return True
            
        # 没有该被动技能且被动技能栏未满 - 添加新被动技能
        elif len(self.passives) < self.max_passives:
            self.passive_levels[passive_type] = level
            self.passives[passive_type] = effects
            
            # 通知属性变化
            if self.on_stats_changed:
                self.on_stats_changed()
                
            return True
                
        return False
    
    def get_passive_level(self, passive_type):
        """
        获取指定被动技能的等级
        
        Args:
            passive_type: 被动技能类型
            
        Returns:
            int: 被动技能等级，未持有返回0
        """
        return self.passive_levels.get(passive_type, 0)
    
    def has_max_passives(self):
        """
        检查是否已达到最大被动技能数量
        
        Returns:
            bool: 若已达到最大被动技能数量返回True，否则返回False
        """
        return len(self.passives) >= self.max_passives
    
    def calculate_stats(self, base_stats):
        """
        计算应用所有被动技能效果后的最终属性
        
        Args:
            base_stats: 基础属性字典
            
        Returns:
            dict: 最终属性字典
        """
        # 复制基础属性
        final_stats = base_stats.copy()
        
        # 应用被动效果
        for effects in self.passives.values():
            # 处理百分比增加的属性
            for stat, value in effects.items():
                if stat in final_stats:
                    # 根据属性类型应用不同的增益方式
                    if stat in ['speed', 'exp_multiplier', 'attack_power', 'luck']:
                        # 这些属性使用乘法修正（百分比增加）
                        final_stats[stat] *= (1 + value)
                    else:
                        # 其他属性直接加法修正
                        final_stats[stat] += value
        
        return final_stats
    
    def get_all_passive_effects(self):
        """
        获取所有被动技能效果
        
        Returns:
            dict: 被动技能效果字典
        """
        return self.passives.copy() 