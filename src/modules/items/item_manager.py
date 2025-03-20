import random
from .item import Item

class ItemManager:
    def __init__(self):
        self.items = []
        
    def spawn_item(self, x, y, enemy_type=None):
        # 必定掉落经验球
        self.items.append(Item(x, y, 'exp'))
        
        # 随机掉落其他物品
        if random.random() < 0.1:  # 10%概率掉落金币
            self.items.append(Item(x + random.randint(-10, 10), y + random.randint(-10, 10), 'coin'))
            
        if random.random() < 0.05:  # 5%概率掉落医疗包
            self.items.append(Item(x + random.randint(-10, 10), y + random.randint(-10, 10), 'health'))
            
    def update(self, dt, player):
        for item in self.items[:]:  # 使用切片创建副本以避免在迭代时修改列表
            item.update(dt, player)
            if item.collected:
                self.items.remove(item)
                
    def render(self, screen, camera_x, camera_y, screen_center_x, screen_center_y):
        for item in self.items:
            item.render(screen, camera_x, camera_y, screen_center_x, screen_center_y) 