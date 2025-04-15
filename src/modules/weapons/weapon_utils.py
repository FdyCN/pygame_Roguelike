"""
武器工具函数
提供简单的工厂方法来创建武器实例
"""

from .types.knife import Knife
from .types.fireball import Fireball
from .types.frost_nova import FrostNova
from .weapons_data import get_weapon_config

# 武器类映射
WEAPON_CLASSES = {
    'knife': Knife,
    'fireball': Fireball,
    'frost_nova': FrostNova
}

def create_weapon(weapon_type, player):
    """
    创建指定类型的武器实例
    
    Args:
        weapon_type: 武器类型名称
        player: 玩家实例
        
    Returns:
        object: 武器实例，如果类型不存在则返回None
    """
    if weapon_type not in WEAPON_CLASSES:
        return None
        
    weapon_class = WEAPON_CLASSES[weapon_type]
    return weapon_class(player)
    
def get_available_weapon_types():
    """
    获取所有可用的武器类型
    
    Returns:
        list: 武器类型名称列表
    """
    return list(WEAPON_CLASSES.keys())
    
def get_weapon_info(weapon_type):
    """
    获取武器信息
    
    Args:
        weapon_type: 武器类型名称
        
    Returns:
        dict: 武器信息字典，包含名称、描述等
    """
    return get_weapon_config(weapon_type) 