import pygame
import random
from enum import Enum
from .resource_manager import resource_manager
from .weapons.weapon_stats import WeaponStatType

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
                self.icon = resource_manager.load_image(f'passive_upgrade_{name}_{level}', icon_path)
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
                            WeaponStatType.DAMAGE: 20,
                            WeaponStatType.ATTACK_SPEED: 1.0,
                            WeaponStatType.PROJECTILE_SPEED: 400,
                            WeaponStatType.CAN_PENETRATE: False,
                            WeaponStatType.PROJECTILES_PER_CAST: 1,
                            WeaponStatType.SPREAD_ANGLE: 0,
                            WeaponStatType.LIFETIME: 3.0
                        },
                        description="基础飞刀，单发直线飞行",
                        icon_path="images/weapons/knife_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="飞刀",
                        level=2,
                        effects={
                            WeaponStatType.DAMAGE: 20,
                            WeaponStatType.ATTACK_SPEED: 1.1,
                            WeaponStatType.PROJECTILE_SPEED: 400,
                            WeaponStatType.CAN_PENETRATE: False,
                            WeaponStatType.PROJECTILES_PER_CAST: 2,
                            WeaponStatType.SPREAD_ANGLE: 15,
                            WeaponStatType.LIFETIME: 3.0
                        },
                        description="同时发射两把飞刀，呈扇形分布",
                        icon_path="images/weapons/knife_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="飞刀",
                        level=3,
                        effects={
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
                            WeaponStatType.DAMAGE: 25,
                            WeaponStatType.EXPLOSION_RADIUS: 30,
                            WeaponStatType.BURN_DURATION: 3,
                            WeaponStatType.BURN_DAMAGE: 5,
                            WeaponStatType.COOLDOWN: 1.5
                        },
                        description="发射火球，造成范围伤害并点燃敌人",
                        icon_path="images/weapons/fireball_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="火球术",
                        level=2,
                        effects={
                            WeaponStatType.DAMAGE: 25,
                            WeaponStatType.EXPLOSION_RADIUS: 40,
                            WeaponStatType.BURN_DURATION: 4,
                            WeaponStatType.BURN_DAMAGE: 8,
                            WeaponStatType.COOLDOWN: 1.5
                        },
                        description="增加爆炸范围和燃烧伤害",
                        icon_path="images/weapons/fireball_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="火球术",
                        level=3,
                        effects={
                            WeaponStatType.DAMAGE: 35,
                            WeaponStatType.EXPLOSION_RADIUS: 40,
                            WeaponStatType.BURN_DURATION: 5,
                            WeaponStatType.BURN_DAMAGE: 10,
                            WeaponStatType.COOLDOWN: 1.2
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
                            WeaponStatType.DAMAGE: 25,
                            WeaponStatType.EXPLOSION_RADIUS: 30,
                            WeaponStatType.FREEZE_DURATION: 3,
                            WeaponStatType.SLOW_PERCENT: 50,
                            WeaponStatType.COOLDOWN: 1.5
                        },
                        description="发射冰锥，造成单体伤害并减速敌人",
                        icon_path="images/weapons/nova_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="冰锥术",
                        level=2,
                        effects={
                            WeaponStatType.DAMAGE: 25,
                            WeaponStatType.EXPLOSION_RADIUS: 40,
                            WeaponStatType.FREEZE_DURATION: 4,
                            WeaponStatType.SLOW_PERCENT: 50,
                            WeaponStatType.COOLDOWN: 1.5
                        },
                        description="造成爆炸范围和减速",
                        icon_path="images/weapons/nova_32x32.png"
                    ),
                    WeaponUpgradeLevel(
                        name="冰锥术",
                        level=3,
                        effects={
                            WeaponStatType.DAMAGE: 35,
                            WeaponStatType.EXPLOSION_RADIUS: 40,
                            WeaponStatType.FREEZE_DURATION: 5,
                            WeaponStatType.SLOW_PERCENT: 50,
                            WeaponStatType.COOLDOWN: 1.2
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
                        icon_path="images/passives/absorb_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="拾取范围",
                        level=2,
                        effects={'pickup_range': 50},
                        description="拾取范围增加50",
                        icon_path="images/passives/absorb_up_32x32.png"
                    ),
                    PassiveUpgradeLevel(
                        name="拾取范围",
                        level=3,
                        effects={'pickup_range': 100},
                        description="拾取范围增加100",
                        icon_path="images/passives/absorb_up_32x32.png"
                    )
                ]
            ),
            'coins': PassiveUpgrade(
                name="金币奖励",
                max_level=1,
                levels=[
                    PassiveUpgradeLevel(
                        name="金币奖励",
                        level=1,
                        effects={'coins': 25},
                        description="获得25金币",
                        icon_path="images/items/coin_32x32.png"
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
        # 构建候选池
        candidate_pool = []
        
        # 检查是否所有武器和被动都已满级
        all_maxed = True
        
        # 检查武器
        for weapon in player.weapons:
            if weapon.type in self.weapon_upgrades:
                weapon_upgrade = self.weapon_upgrades[weapon.type]
                if weapon.level < weapon_upgrade.max_level:
                    all_maxed = False
                    break
                    
        # 检查被动
        if all_maxed:
            for passive_type in player.passives:
                if passive_type in self.passive_upgrades:
                    passive_upgrade = self.passive_upgrades[passive_type]
                    current_level = player.passive_levels.get(passive_type, 0)
                    if current_level < passive_upgrade.max_level:
                        all_maxed = False
                        break
        
        # 创建一个金币奖励选项
        coin_reward = self.passive_upgrades['coins'].levels[0]

        # 如果所有武器和被动都满级了，返回金币奖励
        if all_maxed:
            return [coin_reward] * count
            
        # 检查武器槽和被动槽是否已满
        weapons_full = len(player.weapons) >= 3
        passives_full = len(player.passives) >= 3
        
        # 如果两个槽都满了，只添加现有武器和被动的升级选项
        if weapons_full and passives_full:
            # 添加现有武器的升级选项
            for weapon in player.weapons:
                if weapon.type in self.weapon_upgrades:
                    weapon_upgrade = self.weapon_upgrades[weapon.type]
                    if weapon.level < weapon_upgrade.max_level:
                        candidate_pool.append(weapon_upgrade.levels[weapon.level])
            
            # 添加现有被动的升级选项
            for passive_type in player.passives:
                if passive_type in self.passive_upgrades:
                    passive_upgrade = self.passive_upgrades[passive_type]
                    current_level = player.passive_levels.get(passive_type, 0)
                    if current_level < passive_upgrade.max_level:
                        candidate_pool.append(passive_upgrade.levels[current_level])
        else:
            # 添加所有武器选项
            for weapon_type, weapon_upgrade in self.weapon_upgrades.items():
                # 检查玩家是否已有该武器
                player_weapon = next((w for w in player.weapons if w.type == weapon_type), None)
                if player_weapon:
                    # 如果武器未达到最高级，添加下一级升级选项
                    if player_weapon.level < weapon_upgrade.max_level:
                        candidate_pool.append(weapon_upgrade.levels[player_weapon.level])
                elif not weapons_full:
                    # 如果武器槽未满，添加1级选项
                    candidate_pool.append(weapon_upgrade.levels[0])
                    
            # 添加所有被动选项
            for passive_type, passive_upgrade in self.passive_upgrades.items():
                # 检查玩家是否已有该被动
                current_level = player.passive_levels.get(passive_type, 0)
                if current_level > 0:
                    # 如果被动未达到最高级，添加下一级升级选项
                    if current_level < passive_upgrade.max_level:
                        candidate_pool.append(passive_upgrade.levels[current_level])
                elif not passives_full:
                    # 如果被动槽未满，添加1级选项
                    candidate_pool.append(passive_upgrade.levels[0])
        
        # 如果候选池为空，返回空列表
        if not candidate_pool:
            return []
        
        # 如果候选池数量小于count，则在空位添加金币奖励选项
        if len(candidate_pool) < count:
            candidate_pool.append(coin_reward)

        # 从候选池中随机选择指定数量的选项
        selected_upgrades = random.sample(
            candidate_pool,
            min(len(candidate_pool), count)
        )
        
        return selected_upgrades 