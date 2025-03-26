import pygame
import math
from .resource_manager import resource_manager
from .weapons.knife import Knife
from .weapons.fireball import Fireball
from .weapons.frost_nova import FrostNova
from .upgrade_system import UpgradeType, WeaponUpgradeLevel, PassiveUpgradeLevel

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # 加载精灵表并创建动画
        idle_spritesheet = resource_manager.load_spritesheet('player_idle_sprite', 'images/player/Ninja_frog_Idle_32x32.png')
        run_spritesheet = resource_manager.load_spritesheet('player_run_sprite', 'images/player/Ninja_frog_Run_32x32.png')
        hurt_spritesheet = resource_manager.load_spritesheet('player_hurt_sprite', 'images/player/Ninja_frog_Hit_32x32.png')
        
        # 创建各种状态的动画
        self.animations = {
            'idle': resource_manager.create_animation('player_idle', idle_spritesheet, 
                                                    frame_width=32, frame_height=32,
                                                    frame_count=11, row=0,
                                                    frame_duration=0.0333),
            'run': resource_manager.create_animation('player_run', run_spritesheet,
                                                   frame_width=32, frame_height=32,
                                                   frame_count=12, row=0,
                                                   frame_duration=0.0333),
            'hurt': resource_manager.create_animation('player_hurt', hurt_spritesheet,
                                                    frame_width=32, frame_height=32,
                                                    frame_count=7, row=0,
                                                    frame_duration=0.0333)
        }
        
        # 设置当前动画
        self.current_animation = 'idle'
        self.image = self.animations[self.current_animation].get_current_frame()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        # 世界坐标
        self.world_x = x
        self.world_y = y
        
        # 武器系统
        self.weapons = []  # 最多3个武器
        self.weapon_levels = {}  # 记录每个武器的等级 {'knife': 1, 'fireball': 1}
        self.available_weapons = {
            'knife': Knife,
            'fireball': Fireball,
            'frost_nova': FrostNova
        }
        
        # 被动系统
        self.passives = {}  # 最多3个被动 {'health': PassiveUpgrade, 'speed': PassiveUpgrade}
        self.passive_levels = {}  # 记录每个被动的等级 {'health': 1, 'speed': 1}
        
        # 基础属性
        self.base_max_health = 100
        self.base_speed = 200
        self.base_exp_multiplier = 1.0
        self.base_health_regen = 0  # 基础生命恢复速度
        self.base_defense = 0  # 基础防御力
        self.base_luck = 1.0  # 基础幸运值
        self.base_pickup_range = 50  # 基础拾取范围
        self.base_attack_power = 1.0  # 基础攻击力倍率
        
        # 当前属性（包含被动加成）
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.speed = self.base_speed
        self.exp_multiplier = self.base_exp_multiplier
        self.health_regen = self.base_health_regen
        self.defense = self.base_defense
        self.luck = self.base_luck
        self.pickup_range = self.base_pickup_range
        self.attack_power = self.base_attack_power  # 当前攻击力倍率
        
        # 等级和经验值
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        
        # 金币
        self.coins = 0
        
        # 移动相关
        self.velocity = pygame.math.Vector2()
        self.direction = pygame.math.Vector2()
        self.moving = {'up': False, 'down': False, 'left': False, 'right': False}
        self.facing_right = True
        
        # 受伤状态
        self.hurt_timer = 0
        self.hurt_duration = 0.2
        
        # 无敌时间相关
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 2.0
        self.blink_interval = 0.1
        self.blink_timer = 0
        self.visible = True
        
        # 添加初始武器
        self.add_weapon('knife')
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.moving['up'] = True
            elif event.key == pygame.K_s:
                self.moving['down'] = True
            elif event.key == pygame.K_a:
                self.moving['left'] = True
                self.facing_right = False  # 更新朝向
            elif event.key == pygame.K_d:
                self.moving['right'] = True
                self.facing_right = True  # 更新朝向
                
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_w:
                self.moving['up'] = False
            elif event.key == pygame.K_s:
                self.moving['down'] = False
            elif event.key == pygame.K_a:
                self.moving['left'] = False
            elif event.key == pygame.K_d:
                self.moving['right'] = False
        
        # 更新方向向量
        self.direction.x = float(self.moving['right']) - float(self.moving['left'])
        self.direction.y = float(self.moving['down']) - float(self.moving['up'])
                
    def update(self, dt):
        # 更新当前动画
        self.animations[self.current_animation].update(dt)
        
        # 生命值恢复
        if self.health < self.max_health and self.health_regen > 0:
            self.health = min(self.max_health, self.health + self.health_regen * dt)
        
        # 更新受伤状态
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            if self.hurt_timer <= 0 and self.current_animation == 'hurt':
                # 受伤动画播放完毕
                if self.direction.length() > 0:
                    self.current_animation = 'run'
                else:
                    self.current_animation = 'idle'
                self.animations[self.current_animation].reset()
        
        # 更新无敌时间
        if self.invincible:
            self.invincible_timer -= dt
            self.blink_timer -= dt
            
            # 更新闪烁效果
            if self.blink_timer <= 0:
                self.visible = not self.visible
                self.blink_timer = self.blink_interval
            
            # 无敌时间结束
            if self.invincible_timer <= 0:
                self.invincible = False
                self.visible = True
        
        # 更新速度向量和动画状态
        if self.direction.length() > 0:
            # 标准化方向向量
            self.direction = self.direction.normalize()
            # 如果不在受伤状态且当前不是跑步动画，切换到跑步动画
            if self.hurt_timer <= 0 and self.current_animation != 'run':
                self.current_animation = 'run'
                self.animations[self.current_animation].reset()
        # 如果没有移动且不在受伤状态，切换到待机动画
        elif self.hurt_timer <= 0 and self.current_animation != 'idle':
            self.current_animation = 'idle'
            self.animations[self.current_animation].reset()
        
        # 计算速度
        self.velocity = self.direction * self.speed
        
        # 更新世界坐标位置（实际位置）
        self.world_x += self.velocity.x * dt
        self.world_y += self.velocity.y * dt
        
        # 更新当前图像
        current_frame = self.animations[self.current_animation].get_current_frame()
        
        # 根据朝向翻转图像
        if not self.facing_right:
            current_frame = pygame.transform.flip(current_frame, True, False)
            
        self.image = current_frame
        # print(self.current_animation)
        
    def render(self, screen):
        # 如果在无敌状态且当前应该隐藏，则不渲染玩家
        if not self.invincible or self.visible:
            screen.blit(self.image, self.rect)
        
    def take_damage(self, amount):
        # 如果处于无敌状态，不受伤害
        if self.invincible:
            return False
            
        # 计算实际伤害（考虑防御力）
        actual_damage = amount * (1 - self.defense)
        self.health = max(0, self.health - actual_damage)
        
        if self.health <= 0:
            self.health = 0
            # 处理玩家死亡
        else:
            # 切换到受伤动画
            self.current_animation = 'hurt'
            self.animations[self.current_animation].reset()
            self.hurt_timer = self.hurt_duration
            
            # 激活无敌时间
            self.invincible = True
            self.invincible_timer = self.invincible_duration
            self.blink_timer = self.blink_interval
            self.visible = True
            
        return True
        
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        return True
        
    def apply_weapon_upgrade(self, weapon_type, level, effects):
        """应用武器升级
        
        Args:
            weapon_type: 武器类型（如'knife', 'fireball'等）
            level: 升级后的等级
            effects: 升级效果
        """
        if weapon_type not in self.weapon_levels and weapon_type not in self.weapons:
            # 新武器
            if len(self.weapons) < 3:  # 检查武器数量上限
                self.weapon_levels[weapon_type] = level
                return True
        else:
            # 升级现有武器
            self.weapon_levels[weapon_type] = level
            # 更新武器属性
            for weapon in self.weapons:
                if weapon.type == weapon_type:
                    weapon.level = level
                    weapon.apply_effects(effects)
                    break
            return True
        return False
            
    def apply_passive_upgrade(self, passive_type, level, effects):
        """应用被动升级
        
        Args:
            passive_type: 被动类型（如'health', 'speed'等）
            level: 升级后的等级
            effects: 升级效果
        """
        if passive_type not in self.passive_levels:
            # 新被动
            if len(self.passives) < 3:  # 检查被动数量上限
                self.passive_levels[passive_type] = level
                self.passives[passive_type] = effects
                self._update_stats()
                return True
        else:
            # 升级现有被动
            self.passive_levels[passive_type] = level
            self.passives[passive_type] = effects
            self._update_stats()
            return True
        return False
        
    def get_weapon_level(self, weapon_type):
        """获取指定武器的等级"""
        return self.weapon_levels.get(weapon_type, 0)
        
    def get_passive_level(self, passive_type):
        """获取指定被动的等级"""
        return self.passive_levels.get(passive_type, 0)
        
    def add_weapon(self, weapon_type):
        """添加武器到玩家的武器列表
        
        Args:
            weapon_type: 武器类型名称（字符串）
        Returns:
            Weapon: 成功时返回武器实例，失败时返回None
        """
        if len(self.weapons) < 3 and weapon_type in self.available_weapons:
            # 检查是否已有该类型武器
            for weapon in self.weapons:
                if isinstance(weapon, self.available_weapons[weapon_type]):
                    return None
            
            # 创建新武器
            weapon = self.available_weapons[weapon_type](self)
            self.weapons.append(weapon)
            self.weapon_levels[weapon_type] = 1
            return weapon
        return None

    def update_weapons(self, dt):
        """更新所有武器状态"""
        for weapon in self.weapons:
            weapon.update(dt)

    def render_weapons(self, screen, camera_x, camera_y):
        """渲染所有武器"""
        for weapon in self.weapons:
            weapon.render(screen, camera_x, camera_y)
        
    def remove_weapon(self, weapon_type):
        """移除指定类型的武器
        
        Args:
            weapon_type: 武器类型
        """
        self.weapons = [w for w in self.weapons if w.type != weapon_type]
        if weapon_type in self.weapon_levels:
            del self.weapon_levels[weapon_type]
            
    def _update_stats(self):
        """更新玩家属性（考虑所有被动效果）"""
        # 重置为基础属性
        self.max_health = self.base_max_health
        self.speed = self.base_speed
        self.exp_multiplier = self.base_exp_multiplier
        self.health_regen = self.base_health_regen
        self.defense = self.base_defense
        self.luck = self.base_luck
        self.pickup_range = self.base_pickup_range
        self.attack_power = self.base_attack_power  # 重置攻击力为基础值
        
        # 应用被动效果
        for effects in self.passives.values():
            if 'max_health' in effects:
                self.max_health += effects['max_health']
            if 'speed' in effects:
                self.speed *= (1 + effects['speed'])
            if 'exp_gain' in effects:
                self.exp_multiplier *= (1 + effects['exp_gain'])
            if 'health_regen' in effects:
                self.health_regen += effects['health_regen']
            if 'defense' in effects:
                self.defense += effects['defense']
            if 'luck' in effects:
                self.luck *= (1 + effects['luck'])
            if 'pickup_range' in effects:
                self.pickup_range += effects['pickup_range']
            if 'attack_power' in effects:
                self.attack_power *= (1 + effects['attack_power'])
        
        # 确保当前生命值不超过最大生命值
        self.health = min(self.health, self.max_health)
        
        # 更新所有武器的伤害
        for weapon in self.weapons:
            weapon._apply_player_attack_power()
        
    def add_experience(self, amount):
        """添加经验值并检查是否升级"""
        self.experience += amount * (1 + self.exp_multiplier)
        return self.experience >= self.exp_to_next_level
            
    def level_up(self):
        """升级处理"""
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level = int(self.exp_to_next_level * 1.2)  # 每级所需经验值增加20%
        # 移除自动增加属性的代码，改为只播放音效
        resource_manager.play_sound("level_up")
        return True
        
    def add_coins(self, amount):
        """添加金币"""
        self.coins += amount
        # 播放收集金币音效
        resource_manager.play_sound("collect_coin") 