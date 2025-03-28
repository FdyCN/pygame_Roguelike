import pygame
import random
from enum import Enum
from .resource_manager import resource_manager

class UpgradeType(Enum):
    WEAPON = "weapon"
    PASSIVE = "passive"

class WeaponUpgradeLevel:
    def __init__(self, name, level, effects, description, icon_path=None):
        self.name = name
        self.level = level
        self.effects = effects  # 字典，包含各种效果的变化
        self.description = description
        self.icon = None
        if icon_path:
            try:
                self.icon = resource_manager.load_image(f'weapon_upgrade_{name}_{level}', icon_path)
                self.icon = pygame.transform.scale(self.icon, (48, 48))
            except:
                print(f"无法加载图标: {icon_path}")

class WeaponUpgrade:
    def __init__(self, name, max_level, levels):
        self.name = name
        self.max_level = max_level
        self.levels = levels  # 列表，每个元素是WeaponUpgradeLevel
        self.type = UpgradeType.WEAPON

class PassiveUpgradeLevel:
    def __init__(self, name, level, effects, description, icon_path=None):
        self.name = name
        self.level = level
        self.effects = effects
        self.description = description
        self.icon = None
        if icon_path:
            try:
                self.icon = resource_manager.load_image(f'passive_upgrade_{level}', icon_path)
                self.icon = pygame.transform.scale(self.icon, (48, 48))
            except:
                print(f"无法加载图标: {icon_path}")

class PassiveUpgrade:
    def __init__(self, name, max_level, levels):
        self.name = name
        self.max_level = max_level
        self.levels = levels
        self.type = UpgradeType.PASSIVE

class UpgradeManager:
    def __init__(self):
        # 武器升级配置
        self.weapon_upgrades = {
            'knife': WeaponUpgrade(
                name="飞刀",
                max_level=3,
                levels=[
                    WeaponUpgradeLevel(
                        name="飞刀",
                        level=1,
                        effects={
                            'damage': 20,
                            'attack_speed': 1.0,
                            'projectile_speed': 400,
                            'can_penetrate': False,
                            'knives_per_throw': 1,
                            'spread_angle': 0,
                            'lifetime': 3.0
                        },
                        description="基础飞刀，单发直线飞行",
                        icon_path="images/weapons/knife_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="飞刀",
                        level=2,
                        effects={
                            'damage': 20,
                            'attack_speed': 1.1,
                            'projectile_speed': 400,
                            'can_penetrate': False,
                            'knives_per_throw': 2,
                            'spread_angle': 15,
                            'lifetime': 3.0
                        },
                        description="同时发射两把飞刀，呈扇形分布",
                        icon_path="images/weapons/knife_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="飞刀",
                        level=3,
                        effects={
                            'damage': 30,
                            'attack_speed': 1.25,
                            'projectile_speed': 400,
                            'can_penetrate': True,
                            'knives_per_throw': 2,
                            'spread_angle': 15,
                            'lifetime': 3.0
                        },
                        description="飞刀可以穿透敌人，伤害提升",
                        icon_path="images/weapons/knife_32x32.png"
                    )
                ]
            ),
            'fireball': WeaponUpgrade(
                name="火球术",
                max_level=3,
                levels=[
                    WeaponUpgradeLevel(
                        name="火球术",
                        level=1,
                        effects={
                            'damage': 25,
                            'radius': 30,
                            'burn_duration': 3,
                            'burn_damage': 5,
                            'cooldown': 1.5
                        },
                        description="发射火球，造成范围伤害并点燃敌人",
                        icon_path="images/weapons/fireball_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="火球术",
                        level=2,
                        effects={
                            'damage': 25,
                            'radius': 40,
                            'burn_duration': 4,
                            'burn_damage': 8,
                            'cooldown': 1.5
                        },
                        description="增加爆炸范围和燃烧伤害",
                        icon_path="images/weapons/fireball_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="火球术",
                        level=3,
                        effects={
                            'damage': 35,
                            'radius': 40,
                            'burn_duration': 5,
                            'burn_damage': 10,
                            'cooldown': 1.2
                        },
                        description="提升伤害和燃烧效果，减少冷却时间",
                        icon_path="images/weapons/fireball_32x32.png"
                    )
                ]
            ),
            'frost_nova': WeaponUpgrade(
                name="冰锥术",
                max_level=3,
                levels=[
                    WeaponUpgradeLevel(
                        name="冰锥术",
                        level=1,
                        effects={
                            'damage': 25,
                            'radius': 30,
                            'freeze_duration': 3,
                            'slow_percent': 50,
                            'cooldown': 1.5
                        },
                        description="发射冰锥，造成单体伤害并减速敌人",
                        icon_path="images/weapons/nova_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="冰锥术",
                        level=2,
                        effects={
                            'damage': 25,
                            'radius': 40,
                            'freeze_duration': 4,
                            'slow_percent': 50,
                            'cooldown': 1.5
                        },
                        description="造成爆炸范围和减速",
                        icon_path="images/weapons/nova_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="冰锥术",
                        level=3,
                        effects={
                            'damage': 35,
                            'radius': 40,
                            'freeze_duration': 5,
                            'slow_percent': 50,
                            'cooldown': 1.2
                        },
                        description="提升伤害和减速效果，减少冷却时间",
                        icon_path="images/weapons/nova_32x32.png"
                    )
                ]
            )
        }
        
        # 被动升级配置
        self.passive_upgrades = {
            'health': PassiveUpgrade(
                name="生命强化",
                max_level=3,
                levels=[
                    PassiveUpgradeLevel(
                        name="生命强化",
                        level=1,
                        effects={'max_health': 50},
                        description="增加50点最大生命值",
                        icon_path="images/passives/max_health_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="生命强化",
                        level=2,
                        effects={'max_health': 100},
                        description="增加100点最大生命值",
                        icon_path="images/passives/max_health_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="生命强化",
                        level=3,
                        effects={'max_health': 200},
                        description="增加200点最大生命值",
                        icon_path="images/passives/max_health_up_32x32.png"
                    )
                ]
            ),
            'speed': PassiveUpgrade(
                name="迅捷",
                max_level=3,
                levels=[
                    PassiveUpgradeLevel(
                        name="迅捷",
                        level=1,
                        effects={'speed': 0.1},
                        description="移动速度提升10%",
                        icon_path="images/passives/speed_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="迅捷",
                        level=2,
                        effects={'speed': 0.2},
                        description="移动速度提升20%",
                        icon_path="images/passives/speed_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="迅捷",
                        level=3,
                        effects={'speed': 0.3},
                        description="移动速度提升30%",
                        icon_path="images/passives/speed_up_32x32.png"
                    )
                ]
            ),
            'health_regen': PassiveUpgrade(
                name="生命回复",
                max_level=3,
                levels=[
                    PassiveUpgradeLevel(
                        name="生命回复",
                        level=1,
                        effects={'health_regen': 1},
                        description="每秒回复1点生命值",
                        icon_path="images/passives/heal_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="生命回复",
                        level=2,
                        effects={'health_regen': 2},
                        description="每秒回复2点生命值",
                        icon_path="images/passives/heal_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="生命回复",
                        level=3,
                        effects={'health_regen': 3},
                        description="每秒回复3点生命值",
                        icon_path="images/passives/heal_up_32x32.png"
                    )
                ]
            ),
            'luck': PassiveUpgrade(
                name="幸运",
                max_level=3,
                levels=[
                    PassiveUpgradeLevel(
                        name="幸运",
                        level=1,
                        effects={'luck': 0.5},
                        description="幸运值提升50%",
                        icon_path="images/passives/lucky_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="幸运",
                        level=2,
                        effects={'luck': 1},
                        description="幸运值提升100%",
                        icon_path="images/passives/lucky_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="幸运",
                        level=3,
                        effects={'luck': 1.5},
                        description="幸运值提升150%",
                        icon_path="images/passives/lucky_up_32x32.png"
                    )
                ]
            ),
            'attack_power': PassiveUpgrade(
                name="攻击力",
                max_level=3,
                levels=[
                    PassiveUpgradeLevel(
                        name="攻击力",
                        level=1,
                        effects={'attack_power': 0.1},
                        description="攻击力提升10%",
                        icon_path="images/passives/damage_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="攻击力",
                        level=2,
                        effects={'attack_power': 0.2},
                        description="攻击力提升20%",
                        icon_path="images/passives/damage_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="攻击力",
                        level=3,
                        effects={'attack_power': 0.3},
                        description="攻击力提升30%",
                        icon_path="images/passives/damage_up_32x32.png"
                    )
                ]
            ),
            'defense': PassiveUpgrade(
                name="防御力",
                max_level=3,
                levels=[
                    PassiveUpgradeLevel(
                        name="防御力",
                        level=1,
                        effects={'defense': 0.1},
                        description="防御力提升10%",
                        icon_path="images/passives/defense_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="防御力",
                        level=2,
                        effects={'defense': 0.2},
                        description="防御力提升20%",
                        icon_path="images/passives/defense_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="防御力",
                        level=3,
                        effects={'defense': 0.3},
                        description="防御力提升30%",
                        icon_path="images/passives/defense_up_32x32.png"
                    )
                ]
            ),
            'pickup_range': PassiveUpgrade(
                name="拾取范围",
                max_level=3,
                levels=[
                    PassiveUpgradeLevel(
                        name="拾取范围",
                        level=1,
                        effects={'pickup_range': 25},
                        description="拾取范围增加25",
                        icon_path="images/passives/pickup_range_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="拾取范围",
                        level=2,
                        effects={'pickup_range': 50},
                        description="拾取范围增加50",
                        icon_path="images/passives/pickup_range_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="拾取范围",
                        level=3,
                        effects={'pickup_range': 100},
                        description="拾取范围增加100",
                        icon_path="images/passives/pickup_range_up_32x32.png"
                    )
                ]
            )    
        }
        
    def get_random_upgrades(self, player, count=3):
        """获取随机升级选项
        
        Args:
            player: 玩家对象
            count: 需要返回的升级选项数量
            
        Returns:
            list: 升级选项列表
        """
        available_upgrades = []
        
        # 获取当前武器的升级选项
        for weapon in player.weapons:
            if weapon.type in self.weapon_upgrades:
                weapon_upgrade = self.weapon_upgrades[weapon.type]
                if weapon.level < weapon_upgrade.max_level:
                    available_upgrades.append(weapon_upgrade.levels[weapon.level])
        
        # 如果玩家武器数量未达到上限，添加新武器选项
        if len(player.weapons) < 3:  # 最多3个武器
            current_weapon_types = {w.type for w in player.weapons}
            new_weapons = [w for w in self.weapon_upgrades.keys() 
                         if w not in current_weapon_types]
            if new_weapons:
                # 随机选择一个新武器，添加其1级升级选项
                new_weapon = random.choice(new_weapons)
                available_upgrades.append(self.weapon_upgrades[new_weapon].levels[0])
        
        # 获取可用的被动升级选项
        for passive in player.weapons:
            if passive.type in self.passive_upgrades:
                passive_upgrade = self.passive_upgrades[passive.type]
                if passive.level < passive_upgrade.max_level:
                    available_upgrades.append(passive_upgrade.levels[passive.level])
        
        # 如果玩家被动数量未达到上限，添加新被动选项
        if len(player.passives) < 3:  # 最多3个被动
            current_passive_types = set(player.passives.keys())
            new_passives = [p for p in self.passive_upgrades.keys() 
                          if p not in current_passive_types]
            if new_passives:
                # 随机选择一个新被动，添加其1级升级选项
                new_passive = random.choice(new_passives)
                available_upgrades.append(self.passive_upgrades[new_passive].levels[0])
        
        # 如果可用升级不足count个，随机重复一些选项
        while len(available_upgrades) < count:
            if not available_upgrades:  # 如果没有任何可用升级
                break
            available_upgrades.append(random.choice(available_upgrades))
        
        # 随机选择指定数量的升级选项
        return random.sample(available_upgrades, min(len(available_upgrades), count)) 