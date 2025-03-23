import pygame
import math
from .resource_manager import resource_manager
from .weapons.knife import Knife
from .upgrade_system import UpgradeType

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
        
        # 基础属性
        self.base_max_health = 100
        self.base_speed = 200
        self.base_exp_multiplier = 1.0
        
        # 当前属性（包含被动加成）
        self.max_health = self.base_max_health
        self.health = self.max_health
        self.speed = self.base_speed
        self.exp_multiplier = self.base_exp_multiplier
        
        # 等级和经验值
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        
        # 金币
        self.coins = 0
        
        # 武器列表
        self.weapons = []  # 武器将由WeaponManager管理
        
        # 被动效果
        self.passive_effects = {
            'max_health': 0,  # 额外生命值
            'speed': 0,       # 速度加成（百分比）
            'exp_gain': 0,    # 经验获取加成（百分比）
            'coin_gain': 0,    # 经验获取加成（百分比）
        }
        
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
        self.invincible_duration = 2.0  # 无敌时间持续2秒
        self.blink_interval = 0.1  # 闪烁间隔
        self.blink_timer = 0
        self.visible = True  # 控制闪烁显示
        
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
        
        # 绘制血条
        health_bar_width = 32
        health_bar_height = 5
        health_ratio = self.health / self.max_health
        
        pygame.draw.rect(screen, (255, 0, 0),  # 红色背景
                        (self.rect.x, self.rect.y - 10,
                         health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (0, 255, 0),  # 绿色血条
                        (self.rect.x, self.rect.y - 10,
                         health_bar_width * health_ratio, health_bar_height))
        
    def take_damage(self, amount):
        # 如果处于无敌状态，不受伤害
        if self.invincible:
            return False
            
        self.health = max(0, self.health - amount)
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
        
    def apply_upgrade(self, upgrade):
        """应用升级效果"""
        if upgrade.upgrade_type == UpgradeType.WEAPON:
            weapon_class = None
            if upgrade.weapon_type == "knife":
                weapon_class = Knife
            # 这里可以继续添加其他武器类型的判断
            
            if weapon_class:
                if upgrade.weapon_type in [w.type for w in self.weapons]:
                    # 升级现有武器
                    for weapon in self.weapons:
                        if weapon.type == upgrade.weapon_type:
                            weapon.upgrade(upgrade)
                else:
                    # 添加新武器
                    if len(self.weapons) < 6:
                        new_weapon = weapon_class()
                        self.weapons.append(new_weapon)
        
        elif upgrade.upgrade_type == UpgradeType.PASSIVE:
            # 应用被动效果
            self.passive_effects[upgrade.stat_type] += upgrade.effect_value
            self._update_stats()
            
    def _update_stats(self):
        """更新所有属性（包含被动加成）"""
        # 更新最大生命值
        old_max_health = self.max_health
        self.max_health = self.base_max_health + self.passive_effects['max_health']
        # 如果最大生命值增加，当前生命值也相应增加
        if self.max_health > old_max_health:
            self.health += (self.max_health - old_max_health)
        
        # 更新速度（基础速度 * (1 + 速度加成百分比)）
        self.speed = self.base_speed * (1 + self.passive_effects['speed'])
        
        # 更新经验获取倍率
        self.exp_multiplier = self.base_exp_multiplier + self.passive_effects['exp_gain']
        
    def add_coins(self, amount):
        """添加金币"""
        self.coins += amount
        # 播放收集金币音效
        resource_manager.play_sound("collect_coin") 