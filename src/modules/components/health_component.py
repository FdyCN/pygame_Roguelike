"""
生命值组件
负责管理实体的生命值、受伤和无敌状态
"""

from .base_component import Component

class HealthComponent(Component):
    """生命值组件，处理实体的生命值逻辑"""
    
    def __init__(self, owner, max_health=100, defense=0, health_regen=0):
        """
        初始化生命值组件
        
        Args:
            owner: 组件所属的实体
            max_health: 最大生命值
            defense: 防御力（0~1之间，表示减伤百分比）
            health_regen: 生命恢复速度（每秒）
        """
        super().__init__(owner)
        
        # 基础属性
        self.base_max_health = max_health
        self.base_defense = defense
        self.base_health_regen = health_regen
        
        # 当前属性（可以被加成修改）
        self.max_health = max_health
        self.health = max_health
        self.defense = defense
        self.health_regen = health_regen
        
        # 受伤和无敌状态
        self.hurt_timer = 0
        self.hurt_duration = 0.2
        self.invincible = False
        self.invincible_timer = 0
        self.invincible_duration = 2.0
        
        # 回调函数
        self.on_damaged = None  # 受伤时触发
        self.on_healed = None   # 治疗时触发
        self.on_death = None    # 死亡时触发
        
    def update(self, dt):
        """
        更新生命值状态
        
        Args:
            dt: 时间增量（秒）
        """
        if not self.enabled:
            return
            
        # 生命值恢复
        if self.health < self.max_health and self.health_regen > 0:
            self.health = min(self.max_health, self.health + self.health_regen * dt)
            
        # 更新受伤状态
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
            
        # 更新无敌时间
        if self.invincible:
            self.invincible_timer -= dt
            
            # 无敌时间结束
            if self.invincible_timer <= 0:
                self.invincible = False
                # 通知动画组件停止闪烁（如果需要）
                if hasattr(self.owner, 'animation') and hasattr(self.owner.animation, 'stop_blinking'):
                    self.owner.animation.stop_blinking()
    
    def take_damage(self, amount):
        """
        受到伤害
        
        Args:
            amount: 伤害量
            
        Returns:
            bool: 如果成功受到伤害返回True，否则返回False（例如处于无敌状态）
        """
        # 如果处于无敌状态，不受伤害
        if self.invincible:
            return False
            
        # 计算实际伤害（考虑防御力）
        actual_damage = amount * (1 - self.defense)
        self.health = max(0, self.health - actual_damage)
        
        # 设置受伤状态
        self.hurt_timer = self.hurt_duration
        
        # 检查是否死亡
        if self.health <= 0:
            if self.on_death:
                self.on_death()
        else:
            # 激活无敌时间
            self.start_invincibility(self.invincible_duration)
            
            # 触发受伤回调
            if self.on_damaged:
                self.on_damaged(actual_damage)
                
        return True
    
    def heal(self, amount):
        """
        治疗生命值
        
        Args:
            amount: 治疗量
            
        Returns:
            float: 实际恢复的生命值
        """
        if self.health >= self.max_health:
            return 0
            
        old_health = self.health
        self.health = min(self.health + amount, self.max_health)
        actual_heal = self.health - old_health
        
        # 触发治疗回调
        if actual_heal > 0 and self.on_healed:
            self.on_healed(actual_heal)
            
        return actual_heal
    
    def start_invincibility(self, duration):
        """
        开始无敌状态
        
        Args:
            duration: 无敌持续时间（秒）
        """
        self.invincible = True
        self.invincible_timer = duration
        
        # 通知动画组件开始闪烁（如果需要）
        if hasattr(self.owner, 'animation') and hasattr(self.owner.animation, 'start_blinking'):
            self.owner.animation.start_blinking(duration)
    
    def is_hurt(self):
        """
        检查是否处于受伤状态
        
        Returns:
            bool: 如果在受伤状态中返回True，否则返回False
        """
        return self.hurt_timer > 0
    
    def is_alive(self):
        """
        检查是否存活
        
        Returns:
            bool: 如果生命值大于0返回True，否则返回False
        """
        return self.health > 0 