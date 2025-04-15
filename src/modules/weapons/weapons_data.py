"""
武器配置数据
集中存储所有武器的配置信息，包括名称、图标路径、不同等级的属性等
此文件作为武器系统和升级系统的单一数据源
"""

from .weapon_stats import WeaponStatType

# 所有武器的配置数据
WEAPONS_CONFIG = {
    'knife': {
        'name': '飞刀',
        'icon_path': 'images/weapons/knife_32x32.png',
        'max_level': 3,
        'levels': [
            {
                'level': 1,
                'effects': {
                    WeaponStatType.DAMAGE: 200,
                    WeaponStatType.ATTACK_SPEED: 1.0,
                    WeaponStatType.PROJECTILE_SPEED: 400,
                    WeaponStatType.CAN_PENETRATE: False,
                    WeaponStatType.PROJECTILES_PER_CAST: 1,
                    WeaponStatType.SPREAD_ANGLE: 0,
                    WeaponStatType.LIFETIME: 3.0
                },
                'description': '基础飞刀，单发直线飞行'
            },
            {
                'level': 2,
                'effects': {
                    WeaponStatType.DAMAGE: 20,
                    WeaponStatType.ATTACK_SPEED: 1.1,
                    WeaponStatType.PROJECTILE_SPEED: 400,
                    WeaponStatType.CAN_PENETRATE: False,
                    WeaponStatType.PROJECTILES_PER_CAST: 2,
                    WeaponStatType.SPREAD_ANGLE: 15,
                    WeaponStatType.LIFETIME: 3.0
                },
                'description': '同时发射两把飞刀，呈扇形分布'
            },
            {
                'level': 3,
                'effects': {
                    WeaponStatType.DAMAGE: 30,
                    WeaponStatType.ATTACK_SPEED: 1.25,
                    WeaponStatType.PROJECTILE_SPEED: 400,
                    WeaponStatType.CAN_PENETRATE: True,
                    WeaponStatType.PROJECTILES_PER_CAST: 2,
                    WeaponStatType.SPREAD_ANGLE: 15,
                    WeaponStatType.LIFETIME: 3.0,
                    WeaponStatType.MAX_PENETRATION: 10,
                    WeaponStatType.PENETRATION_DAMAGE_REDUCTION: 0.2
                },
                'description': '飞刀可以穿透敌人，伤害提升'
            }
        ]
    },
    'fireball': {
        'name': '火球术',
        'icon_path': 'images/weapons/fireball_32x32.png',
        'max_level': 3,
        'levels': [
            {
                'level': 1,
                'effects': {
                    WeaponStatType.DAMAGE: 25,
                    WeaponStatType.EXPLOSION_RADIUS: 60,
                    WeaponStatType.BURN_DURATION: 3,
                    WeaponStatType.BURN_DAMAGE: 5,
                    WeaponStatType.COOLDOWN: 1.5
                },
                'description': '发射火球，造成范围伤害并点燃敌人'
            },
            {
                'level': 2,
                'effects': {
                    WeaponStatType.DAMAGE: 25,
                    WeaponStatType.EXPLOSION_RADIUS: 70,
                    WeaponStatType.BURN_DURATION: 4,
                    WeaponStatType.BURN_DAMAGE: 8,
                    WeaponStatType.COOLDOWN: 1.5
                },
                'description': '增加爆炸范围和燃烧伤害'
            },
            {
                'level': 3,
                'effects': {
                    WeaponStatType.DAMAGE: 35,
                    WeaponStatType.EXPLOSION_RADIUS: 80,
                    WeaponStatType.BURN_DURATION: 5,
                    WeaponStatType.BURN_DAMAGE: 10,
                    WeaponStatType.COOLDOWN: 1.2
                },
                'description': '提升伤害和燃烧效果，减少冷却时间'
            }
        ]
    },
    'frost_nova': {
        'name': '冰锥术',
        'icon_path': 'images/weapons/nova_32x32.png',
        'max_level': 3,
        'levels': [
            {
                'level': 1,
                'effects': {
                    WeaponStatType.DAMAGE: 25,
                    WeaponStatType.EXPLOSION_RADIUS: 60,
                    WeaponStatType.FREEZE_DURATION: 3,
                    WeaponStatType.SLOW_PERCENT: 50,
                    WeaponStatType.COOLDOWN: 1.5
                },
                'description': '发射冰锥，造成单体伤害并减速敌人'
            },
            {
                'level': 2,
                'effects': {
                    WeaponStatType.DAMAGE: 25,
                    WeaponStatType.EXPLOSION_RADIUS: 70,
                    WeaponStatType.FREEZE_DURATION: 4,
                    WeaponStatType.SLOW_PERCENT: 50,
                    WeaponStatType.COOLDOWN: 1.5
                },
                'description': '造成爆炸范围和减速'
            },
            {
                'level': 3,
                'effects': {
                    WeaponStatType.DAMAGE: 35,
                    WeaponStatType.EXPLOSION_RADIUS: 80,
                    WeaponStatType.FREEZE_DURATION: 5,
                    WeaponStatType.SLOW_PERCENT: 50,
                    WeaponStatType.COOLDOWN: 1.2
                },
                'description': '提升伤害和减速效果，减少冷却时间'
            }
        ]
    }
}

def get_weapon_config(weapon_type, level=None):
    """
    获取指定武器类型和等级的配置数据
    
    Args:
        weapon_type: 武器类型名称
        level: 武器等级，如果不指定则返回所有等级的配置
        
    Returns:
        dict: 武器配置数据字典，未找到返回None
    """
    if weapon_type not in WEAPONS_CONFIG:
        return None
        
    weapon_config = WEAPONS_CONFIG[weapon_type]
    
    if level is None:
        return weapon_config
    
    # 查找指定等级的配置
    for level_config in weapon_config['levels']:
        if level_config['level'] == level:
            return level_config
            
    return None

def get_weapon_base_stats(weapon_type):
    """
    获取指定武器类型的基础属性（1级属性）
    
    Args:
        weapon_type: 武器类型名称
        
    Returns:
        dict: 武器基础属性字典，未找到返回None
    """
    level_config = get_weapon_config(weapon_type, 1)
    if level_config:
        return level_config['effects']
    return None 