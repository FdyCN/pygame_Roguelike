from enum import Enum, auto
from typing import Dict, Union, Any

class WeaponStatType(Enum):
    """武器属性类型枚举"""
    
    # 基础属性 Base Stats
    DAMAGE = 'damage'                    # 基础伤害值
    ATTACK_SPEED = 'attack_speed'        # 攻击速度(每秒攻击次数)
    LIFETIME = 'lifetime'                # 投射物存在时间(秒)
    COOLDOWN = 'cooldown'                # 技能冷却时间
    
    # 投射物属性 Projectile Stats
    PROJECTILE_SPEED = 'projectile_speed'      # 投射物移动速度(像素/秒)
    PROJECTILES_PER_CAST = 'projectiles_per_cast'  # 每次施放的投射物数量
    SPREAD_ANGLE = 'spread_angle'              # 多个投射物之间的散射角度(度)
    RADIUS = 'radius'                          # 效果范围半径
    
    # 穿透属性 Penetration Stats
    CAN_PENETRATE = 'can_penetrate'             # 是否可以穿透敌人
    MAX_PENETRATION = 'max_penetration'         # 最大穿透次数
    PENETRATION_DAMAGE_REDUCTION = 'penetration_damage_reduction' # 每次穿透后的伤害衰减系数(0-1)
    
    # 元素效果 Elemental Effects
    BURN_DAMAGE = 'burn_damage'               # 燃烧伤害(每秒)
    BURN_DURATION = 'burn_duration'           # 燃烧持续时间(秒)
    SLOW_AMOUNT = 'slow_amount'               # 减速效果强度(0-1)
    SLOW_DURATION = 'slow_duration'           # 减速持续时间(秒)
    FREEZE_DURATION = 'freeze_duration'       # 冰冻持续时间(秒)
    SLOW_PERCENT = 'slow_percent'             # 减速百分比(0-100)
    EXPLOSION_RADIUS = 'explosion_radius'     # 爆炸范围半径(像素)

# 武器属性的默认值
DEFAULT_WEAPON_STATS: Dict[WeaponStatType, Any] = {
    WeaponStatType.DAMAGE: 10,
    WeaponStatType.ATTACK_SPEED: 1.0,
    WeaponStatType.LIFETIME: 2.0,
    WeaponStatType.COOLDOWN: 1.0,
    WeaponStatType.PROJECTILE_SPEED: 300,
    WeaponStatType.PROJECTILES_PER_CAST: 1,
    WeaponStatType.SPREAD_ANGLE: 0,
    WeaponStatType.RADIUS: 30,
    WeaponStatType.CAN_PENETRATE: False,
    WeaponStatType.MAX_PENETRATION: 1,
    WeaponStatType.PENETRATION_DAMAGE_REDUCTION: 0.5,
    WeaponStatType.BURN_DAMAGE: 0,
    WeaponStatType.BURN_DURATION: 0,
    WeaponStatType.SLOW_AMOUNT: 0,
    WeaponStatType.SLOW_DURATION: 0,
    WeaponStatType.FREEZE_DURATION: 0,
    WeaponStatType.SLOW_PERCENT: 0,
}

WeaponStatsDict = Dict[WeaponStatType, Union[int, float, bool]] 