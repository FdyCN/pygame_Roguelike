import random
from .item import Item

class ItemManager:
    def __init__(self):
        self.items = []
        
        # 基础掉落概率
        self.base_coin_drop_rate = 0.1  # 10%概率掉落金币
        self.base_health_drop_rate = 0.05  # 5%概率掉落医疗包
        
    def spawn_item(self, x, y, enemy_type=None, player=None):
        # 必定掉落经验球
        self.items.append(Item(x, y, 'exp'))

        # 如果是boss，必定掉落宝箱
        if enemy_type == 'bat':
            self.items.append(Item(x, y, 'chest'))
            return
        
        # 如果没有提供player参数，使用基础掉落概率
        luck_multiplier = player.luck if player else 1.0
        
        # 随机掉落其他物品，受幸运值影响
        if random.random() < self.base_coin_drop_rate * luck_multiplier:  # 受幸运值加成的金币掉落概率
            self.items.append(Item(x + random.randint(-10, 10), y + random.randint(-10, 10), 'coin'))
            
        if random.random() < self.base_health_drop_rate * luck_multiplier:  # 受幸运值加成的医疗包掉落概率
            self.items.append(Item(x + random.randint(-10, 10), y + random.randint(-10, 10), 'health'))
            
    def update(self, dt, player):
        for item in self.items[:]:  # 使用切片创建副本以避免在迭代时修改列表
            item.update(dt, player)
            if item.collected:
                self.items.remove(item)
                
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        for item in self.items:
            item.render(screen, camera_x, camera_y, screen_center_x, screen_center_y) 