"""
组件系统导出模块
提供对所有组件的集中访问
"""

from .base_component import Component
from .movement_component import MovementComponent
from .animation_component import AnimationComponent
from .health_component import HealthComponent
from .weapon_manager import WeaponManager
from .passive_manager import PassiveManager
from .progression_system import ProgressionSystem

# 导出所有组件类，便于统一导入
__all__ = [
    'Component',
    'MovementComponent',
    'AnimationComponent',
    'HealthComponent',
    'WeaponManager',
    'PassiveManager',
    'ProgressionSystem'
] 