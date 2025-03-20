import pygame
import random
from enum import Enum

class UpgradeType(Enum):
    WEAPON = "weapon"
    PASSIVE = "passive"

class UpgradeOption:
    def __init__(self, name, description, upgrade_type, effect_value=0, icon_path=None):
        self.name = name
        self.description = description
        self.upgrade_type = upgrade_type
        self.effect_value = effect_value
        self.icon = None
        if icon_path:
            try:
                self.icon = pygame.image.load(icon_path).convert_alpha()
                self.icon = pygame.transform.scale(self.icon, (48, 48))
            except:
                print(f"无法加载图标: {icon_path}")

class WeaponUpgrade(UpgradeOption):
    def __init__(self, name, description, weapon_type, damage=0, cooldown=0, icon_path=None):
        super().__init__(name, description, UpgradeType.WEAPON, icon_path=icon_path)
        self.weapon_type = weapon_type
        self.damage = damage
        self.cooldown = cooldown

class PassiveUpgrade(UpgradeOption):
    def __init__(self, name, description, stat_type, value, icon_path=None):
        super().__init__(name, description, UpgradeType.PASSIVE, effect_value=value, icon_path=icon_path)
        self.stat_type = stat_type

class UpgradeManager:
    def __init__(self):
        # 基础武器升级选项
        self.weapon_upgrades = {
            'knife': [
                WeaponUpgrade(
                    "飞刀强化 I",
                    "飞刀伤害提升30%，冷却时间减少10%",
                    "knife",
                    damage=0.3,
                    cooldown=-0.1,
                    icon_path="images/weapons/knife_upgrade1.png"
                ),
                WeaponUpgrade(
                    "飞刀强化 II",
                    "飞刀伤害提升50%，冷却时间减少15%",
                    "knife",
                    damage=0.5,
                    cooldown=-0.15,
                    icon_path="images/weapons/knife_upgrade2.png"
                ),
                WeaponUpgrade(
                    "飞刀强化 III",
                    "飞刀伤害提升80%，冷却时间减少20%",
                    "knife",
                    damage=0.8,
                    cooldown=-0.2,
                    icon_path="images/weapons/knife_upgrade3.png"
                )
            ]
        }
        
        # 新武器选项
        self.new_weapons = [
            WeaponUpgrade(
                "火球术",
                "发射一个火球，造成25点伤害并点燃敌人",
                "fireball",
                damage=25,
                cooldown=1.5,
                icon_path="images/weapons/fireball.png"
            ),
            WeaponUpgrade(
                "冰霜新星",
                "释放冰霜新星，对周围敌人造成20点伤害并减速",
                "frost_nova",
                damage=20,
                cooldown=2.0,
                icon_path="images/weapons/frost_nova.png"
            ),
            WeaponUpgrade(
                "闪电链",
                "发射闪电，可以在敌人之间跳跃，造成15点伤害",
                "lightning",
                damage=15,
                cooldown=1.0,
                icon_path="images/weapons/lightning.png"
            )
        ]
        
        # 被动升级选项
        self.passive_upgrades = [
            PassiveUpgrade(
                "生命强化 I",
                "增加50点最大生命值",
                "max_health",
                50,
                icon_path="images/passives/health_up1.png"
            ),
            PassiveUpgrade(
                "生命强化 II",
                "增加100点最大生命值",
                "max_health",
                100,
                icon_path="images/passives/health_up2.png"
            ),
            PassiveUpgrade(
                "迅捷 I",
                "移动速度提升15%",
                "speed",
                0.15,
                icon_path="images/passives/speed_up1.png"
            ),
            PassiveUpgrade(
                "迅捷 II",
                "移动速度提升25%",
                "speed",
                0.25,
                icon_path="images/passives/speed_up2.png"
            ),
            PassiveUpgrade(
                "经验加成 I",
                "获得的经验值增加20%",
                "exp_gain",
                0.2,
                icon_path="images/passives/exp_up1.png"
            ),
            PassiveUpgrade(
                "经验加成 II",
                "获得的经验值增加35%",
                "exp_gain",
                0.35,
                icon_path="images/passives/exp_up2.png"
            ),
            PassiveUpgrade(
                "金币加成",
                "获得的金币增加25%",
                "coin_gain",
                0.25,
                icon_path="images/passives/coin_up.png"
            ),
            PassiveUpgrade(
                "生命回复",
                "每秒回复1点生命值",
                "health_regen",
                1,
                icon_path="images/passives/health_regen.png"
            )
        ]
    
    def get_random_upgrades(self, player, count=3):
        """获取随机升级选项"""
        available_upgrades = []
        
        # 获取当前武器的升级选项
        for weapon in player.weapons:
            if weapon.type in self.weapon_upgrades:
                # 根据武器等级获取对应的升级选项
                weapon_level = weapon.level if hasattr(weapon, 'level') else 0
                if weapon_level < len(self.weapon_upgrades[weapon.type]):
                    available_upgrades.append(self.weapon_upgrades[weapon.type][weapon_level])
        
        # 如果玩家武器数量未达到上限，添加新武器选项
        if len(player.weapons) < 6:
            # 只添加还未拥有的武器
            current_weapon_types = {w.type for w in player.weapons}
            new_weapons = [w for w in self.new_weapons if w.weapon_type not in current_weapon_types]
            if new_weapons:
                available_upgrades.extend(random.sample(new_weapons, min(2, len(new_weapons))))
        
        # 添加被动升级选项
        # 过滤掉已经达到最高等级的被动
        available_passives = []
        for passive in self.passive_upgrades:
            current_value = player.passive_effects.get(passive.stat_type, 0)
            if passive.stat_type in ['max_health', 'speed', 'exp_gain']:
                # 检查是否已经达到最高等级
                if (passive.stat_type == 'max_health' and current_value < 200) or \
                   (passive.stat_type == 'speed' and current_value < 0.5) or \
                   (passive.stat_type == 'exp_gain' and current_value < 0.5):
                    available_passives.append(passive)
            else:
                # 其他被动技能只能获得一次
                if current_value == 0:
                    available_passives.append(passive)
        
        if available_passives:
            available_upgrades.extend(random.sample(available_passives, 
                                                  min(2, len(available_passives))))
        
        # 如果可用升级不足3个，随机重复一些选项
        while len(available_upgrades) < count:
            available_upgrades.append(random.choice(available_upgrades))
        
        # 随机选择指定数量的升级选项
        return random.sample(available_upgrades, count) 