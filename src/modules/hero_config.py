"""
英雄配置模块
定义不同英雄的基础属性和能力
"""

# 默认英雄配置（忍者蛙）
DEFAULT_HERO_CONFIG = {
    "name": "忍者蛙",
    "description": "平衡型英雄，适合初学者",
    "animations": {
        "idle": {
            "sprite_sheet": "images/player/Ninja_frog_Idle_32x32.png",
            "frame_count": 11,
            "frame_duration": 0.0333,
            "frame_width": 32,
            "frame_height": 32
        },
        "run": {
            "sprite_sheet": "images/player/Ninja_frog_Run_32x32.png",
            "frame_count": 12,
            "frame_duration": 0.0333,
            "frame_width": 32,
            "frame_height": 32
        },
        "hurt": {
            "sprite_sheet": "images/player/Ninja_frog_Hit_32x32.png",
            "frame_count": 7,
            "frame_duration": 0.0333,
            "frame_width": 32,
            "frame_height": 32
        }
    },
    "base_stats": {
        "max_health": 100,
        "speed": 200,
        "defense": 0,
        "health_regen": 0,
        "exp_multiplier": 1.0,
        "pickup_range": 50,
        "attack_power": 1.0,
        "luck": 1.0
    },
    "starting_weapon": "frost_nova",
    "unlock_condition": None  # 默认解锁
}

# 英雄配置字典
HERO_CONFIGS = {
    "ninja_frog": DEFAULT_HERO_CONFIG,
    
    "masked_dude": {
        "name": "蒙面侠",
        "description": "高速度，低血量的敏捷型英雄",
        "animations": {
            "idle": {
                "sprite_sheet": "images/player/Masked_Dude_Idle_32x32.png",
                "frame_count": 11,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "run": {
                "sprite_sheet": "images/player/Masked_Dude_Run_32x32.png",
                "frame_count": 12,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "hurt": {
                "sprite_sheet": "images/player/Masked_Dude_Hit_32x32.png",
                "frame_count": 7,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            }
        },
        "base_stats": {
            "max_health": 80,
            "speed": 250,
            "defense": 0,
            "health_regen": 0,
            "exp_multiplier": 1.0,
            "pickup_range": 60,
            "attack_power": 0.9,
            "luck": 1.2
        },
        "starting_weapon": "fireball",
        "unlock_condition": "reach_level_10"  # 达到10级解锁
    },
    
    "pink_man": {
        "name": "粉红侠",
        "description": "高防御，高生命值的坦克型英雄",
        "animations": {
            "idle": {
                "sprite_sheet": "images/player/Pink_Man_Idle_32x32.png",
                "frame_count": 11,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "run": {
                "sprite_sheet": "images/player/Pink_Man_Run_32x32.png",
                "frame_count": 12,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            },
            "hurt": {
                "sprite_sheet": "images/player/Pink_Man_Hit_32x32.png",
                "frame_count": 7,
                "frame_duration": 0.0333,
                "frame_width": 32,
                "frame_height": 32
            }
        },
        "base_stats": {
            "max_health": 120,
            "speed": 180,
            "defense": 0.2,
            "health_regen": 0.5,
            "exp_multiplier": 0.9,
            "pickup_range": 40,
            "attack_power": 1.1,
            "luck": 0.8
        },
        "starting_weapon": "frost_nova",
        "unlock_condition": "collect_1000_coins"  # 收集1000金币解锁
    }
}

def get_hero_config(hero_type):
    """
    获取指定英雄的配置
    
    Args:
        hero_type: 英雄类型
        
    Returns:
        dict: 英雄配置字典
    """
    return HERO_CONFIGS.get(hero_type, DEFAULT_HERO_CONFIG)

def get_available_heroes():
    """
    获取所有可用英雄类型
    
    Returns:
        list: 英雄类型列表
    """
    return list(HERO_CONFIGS.keys()) 