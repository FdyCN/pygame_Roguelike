import pygame
from .player import Player
from .enemies.enemy_manager import EnemyManager
from .weapons.weapon_manager import WeaponManager
from .items.item_manager import ItemManager
from .ui import UI
from .menu import PauseMenu, GameOverMenu, UpgradeMenu
from .menus.main_menu import MainMenu
from .menus.save_menu import SaveMenu
from .save_system import SaveSystem
from .resource_manager import resource_manager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.paused = False
        self.game_over = False
        self.in_main_menu = True  # 是否在主菜单
        
        
        # 获取屏幕中心点
        self.screen_center_x = self.screen.get_width() // 2
        self.screen_center_y = self.screen.get_height() // 2
        
        # 创建玩家在屏幕中心
        self.player = None
        
        # 相机位置（对应于世界坐标系中的位置）
        self.camera_x = 0
        self.camera_y = 0
        
        # 网格设置
        self.grid_size = 50  # 网格大小
        self.grid_color = (50, 50, 50)  # 网格颜色
        
        # 游戏管理器
        self.enemy_manager = None
        self.weapon_manager = None
        self.item_manager = None
        self.save_system = SaveSystem()
        
        # 创建UI和菜单
        self.ui = UI(screen)
        self.main_menu = MainMenu(screen)
        self.pause_menu = PauseMenu(screen)
        self.game_over_menu = GameOverMenu(screen)
        self.upgrade_menu = UpgradeMenu(screen)
        self.save_menu = SaveMenu(screen, True)  # 保存菜单
        self.load_menu = SaveMenu(screen, False)  # 读取菜单
        
        # 游戏状态
        self.game_time = 0
        self.score = 0
        self.level = 1
        
    def start_new_game(self):
        """开始新游戏，重置所有游戏状态"""
        self.in_main_menu = False
        self.game_over = False
        self.paused = False
        
        # 创建新的玩家
        self.player = Player(self.screen_center_x, self.screen_center_y)
        
        # 初始化游戏管理器
        self.enemy_manager = EnemyManager()
        self.weapon_manager = WeaponManager(self.player)
        self.item_manager = ItemManager()
        
        # 重置游戏状态
        self.game_time = 0
        self.score = 0
        self.level = 1
        
        # 重置相机位置
        self.camera_x = self.player.world_x
        self.camera_y = self.player.world_y
        
        # 播放背景音乐
        resource_manager.play_music("background", loops=-1)
        
    def load_game_state(self, save_data):
        """从存档数据中加载游戏状态"""
        try:
            # 重置游戏状态
            self.in_main_menu = False
            self.game_over = False
            self.paused = False
            
            # 加载玩家数据
            player_data = save_data.get('player_data', {})
            if not player_data:
                print("存档数据损坏：缺少玩家数据")
                return False
                
            # 创建新的玩家实例
            self.player = Player(self.screen_center_x, self.screen_center_y)
            
            # 设置玩家属性
            self.player.health = player_data.get('health', self.player.health)
            self.player.max_health = player_data.get('max_health', self.player.max_health)
            self.player.level = player_data.get('level', self.player.level)
            self.player.experience = player_data.get('experience', 0)
            self.player.coins = player_data.get('coins', 0)
            self.player.world_x = player_data.get('world_x', self.screen_center_x)
            self.player.world_y = player_data.get('world_y', self.screen_center_y)
            
            # 初始化游戏管理器
            self.enemy_manager = EnemyManager()
            self.weapon_manager = WeaponManager(self.player)
            self.item_manager = ItemManager()
            
            # 恢复武器状态
            weapons_data = player_data.get('weapons', [])
            for weapon_type, weapon_level in weapons_data:
                # 确保武器被正确添加并返回
                weapon = self.weapon_manager.add_weapon(weapon_type)
                if weapon:  # 只有当武器成功创建时才设置等级
                    for w in self.weapon_manager.weapons:
                        if isinstance(w, self.weapon_manager.available_weapons[weapon_type]):
                            w.level = weapon_level
                            break
            
            # 恢复游戏状态
            game_data = save_data.get('game_data', {})
            self.game_time = game_data.get('game_time', 0)
            self.score = game_data.get('score', 0)
            self.level = game_data.get('level', 1)
            
            # 恢复敌人状态
            enemies_data = save_data.get('enemies_data', [])
            for enemy_data in enemies_data:
                try:
                    self.enemy_manager.spawn_enemy(
                        enemy_data.get('type', 'normal'),
                        enemy_data.get('x', 0),
                        enemy_data.get('y', 0),
                        enemy_data.get('health', 50)
                    )
                except Exception as e:
                    print(f"加载敌人时出错: {e}")
                    continue
            
            # 设置相机位置
            self.camera_x = self.player.world_x
            self.camera_y = self.player.world_y
            
            # 播放背景音乐
            resource_manager.play_music("background", loops=-1)
            
            return True
            
        except Exception as e:
            print(f"加载存档时出错: {e}")
            # 如果加载失败，重置到初始状态
            self.start_new_game()
            return False
        
    def handle_event(self, event):
        # 如果在主菜单中
        if self.in_main_menu:
            # 如果读取菜单激活，优先处理读取菜单事件
            if self.load_menu.is_active:
                action = self.load_menu.handle_event(event)
                if action == "back":
                    self.load_menu.hide()
                elif isinstance(action, dict):  # 选择了存档
                    if self.load_game_state(action):
                        self.in_main_menu = False
                        self.load_menu.hide()
                    else:
                        print("加载存档失败")
                return
            
            # 处理主菜单事件
            action = self.main_menu.handle_event(event)
            if action == "start":
                self.start_new_game()
                self.in_main_menu = False
            elif action == "load":
                print("显示读取菜单")  # 调试信息
                self.load_menu.show()
            elif action == "quit":
                return "quit"
            return
            
        # 如果在暂停菜单中且读取菜单激活
        if self.load_menu.is_active:
            action = self.load_menu.handle_event(event)
            if action == "back":
                self.load_menu.hide()
            elif isinstance(action, dict):  # 选择了存档
                if self.load_game_state(action):
                    self.load_menu.hide()
                    self.paused = False  # 取消暂停状态
                else:
                    print("加载存档失败")
            return
            
        # 处理保存菜单事件
        if self.save_menu.is_active:
            action = self.save_menu.handle_event(event)
            if action and action.startswith("slot_"):
                slot_id = int(action.split("_")[1])
                self.save_system.save_game(slot_id, self, self.screen)
                self.save_menu.hide()
                self.paused = False
            elif action == "back":
                self.save_menu.hide()
            return
            
        # 处理游戏结束菜单事件
        if self.game_over:
            action = self.game_over_menu.handle_event(event)
            if action == "restart":
                self.start_new_game()
            elif action == "exit":
                self.in_main_menu = True
                self.game_over = False
            return
            
        # 处理升级菜单事件
        if self.upgrade_menu.is_active:
            selected_upgrade = self.upgrade_menu.handle_event(event)
            if selected_upgrade:
                self.player.apply_upgrade(selected_upgrade)
                resource_manager.play_sound("upgrade")
            return
            
        # 处理暂停菜单事件
        if self.paused:
            action = self.pause_menu.handle_event(event)
            if action == "continue":
                self.toggle_pause()
            elif action == "save":
                self.save_menu.show()
            elif action == "restart":
                self.start_new_game()
            elif action == "main_menu":  # 返回主菜单
                self.in_main_menu = True
                self.paused = False
                resource_manager.stop_music()  # 停止游戏音乐
            elif action == "exit":  # 退出游戏
                self.running = False  # 直接退出游戏
            return
            
        # 处理ESC键暂停
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle_pause()
            return
            
        # 处理玩家输入
        if self.player:
            self.player.handle_event(event)
            
    def toggle_pause(self):
        """切换游戏暂停状态"""
        self.paused = not self.paused
        if self.paused:
            self.pause_menu.show()
            resource_manager.pause_music()
        else:
            self.pause_menu.hide()
            resource_manager.unpause_music()
        
    def update(self, dt):
        """更新游戏状态"""
        if self.in_main_menu or self.game_over or self.paused:
            return
            
        # 如果游戏结束或暂停或正在选择升级，只更新菜单
        if self.game_over:
            self.game_over_menu.update(pygame.mouse.get_pos())
            return
            
        if self.paused or self.upgrade_menu.is_active or self.save_menu.is_active:
            return
            
        self.game_time += dt
        
        # 更新玩家位置（在世界坐标系中）
        self.player.update(dt)
        
        # 检查玩家是否死亡
        if self.player.health <= 0 and not self.game_over:
            self.game_over = True
            self.game_over_menu.show()
            return
            
        # 更新相机位置（跟随玩家）
        self.camera_x = self.player.world_x
        self.camera_y = self.player.world_y
        
        # 更新其他游戏对象
        self.enemy_manager.update(dt, self.player)
        self.weapon_manager.update(dt)
        self.item_manager.update(dt, self.player)
        
        # 检测碰撞
        self._check_collisions()
        
        # 检查是否升级
        if self.player.add_experience(0):  # 检查是否可以升级，不添加经验值
            self.player.level_up()
            self.upgrade_menu.show(self.player)  # 显示升级选择菜单
            
    def render(self):
        """渲染游戏画面"""
        # 如果在主菜单中
        if self.in_main_menu:
            # 如果读取菜单激活，只渲染读取菜单
            if self.load_menu.is_active:
                self.load_menu.render()
            else:
                # 否则渲染主菜单
                self.main_menu.render()
            pygame.display.flip()
            return
            
        # 清空屏幕
        self.screen.fill((0, 0, 0))
        
        # 绘制游戏场景
        self._draw_grid()
        
        # 渲染游戏对象（考虑相机偏移）
        self.enemy_manager.render(self.screen, self.camera_x, self.camera_y, 
                                self.screen_center_x, self.screen_center_y)
        self.weapon_manager.render(self.screen, self.camera_x, self.camera_y, 
                                 self.screen_center_x, self.screen_center_y)
        self.item_manager.render(self.screen, self.camera_x, self.camera_y, 
                               self.screen_center_x, self.screen_center_y)
        
        # 渲染玩家（始终在屏幕中心）
        if self.player:
            self.player.render(self.screen)
            
        # 渲染UI
        if self.player:
            self.ui.render(self.player)
            
        # 如果游戏暂停，渲染暂停菜单
        if self.paused:
            self.pause_menu.render()
            
        # 如果正在保存游戏，渲染保存菜单
        if self.save_menu.is_active:
            self.save_menu.render()
            
        # 如果正在选择升级，渲染升级菜单
        if self.upgrade_menu.is_active:
            self.upgrade_menu.render()
            
        # 如果游戏结束，渲染游戏结束菜单
        if self.game_over:
            self.game_over_menu.render()
            
        # 更新显示
        pygame.display.flip()
        
    def _draw_grid(self):
        # 计算网格偏移量（基于相机位置）
        offset_x = (self.camera_x % self.grid_size)
        offset_y = (self.camera_y % self.grid_size)
        
        # 绘制垂直线
        for i in range(int(self.screen.get_width() / self.grid_size) + 2):
            x = i * self.grid_size - offset_x
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, self.screen.get_height()))
            
        # 绘制水平线
        for i in range(int(self.screen.get_height() / self.grid_size) + 2):
            y = i * self.grid_size - offset_y
            pygame.draw.line(self.screen, self.grid_color, (0, y), (self.screen.get_width(), y))
        
    def _check_collisions(self):
        # 检测武器和敌人的碰撞
        for weapon in self.weapon_manager.weapons:
            # 对于每个投掷出去的小刀
            for thrown_knife in weapon.thrown_knives:
                for enemy in self.enemy_manager.enemies:
                    # 计算世界坐标系中的距离
                    dx = enemy.rect.x - thrown_knife.world_x
                    dy = enemy.rect.y - thrown_knife.world_y
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < enemy.rect.width / 2 + thrown_knife.rect.width / 2:
                        if thrown_knife.can_damage_enemy(enemy):
                            thrown_knife.register_hit(enemy)
                            enemy.take_damage(thrown_knife.damage)
                            # 播放击中音效
                            resource_manager.play_sound("hit")
                            if enemy.health <= 0:
                                self.score += enemy.score_value
                                # 在敌人死亡位置生成物品
                                self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type)
                                self.enemy_manager.remove_enemy(enemy)
                                # 播放敌人死亡音效
                                resource_manager.play_sound("enemy_death")
                            # 如果武器不能穿透，则销毁它
                            if not thrown_knife.penetration:
                                thrown_knife.kill()
                        else:
                            # DO NOTHING
                            pass
        
        # 检测玩家和敌人的碰撞
        for enemy in self.enemy_manager.enemies:
            # 计算世界坐标系中的距离
            dx = enemy.rect.x - self.player.world_x
            dy = enemy.rect.y - self.player.world_y
            distance = (dx**2 + dy**2)**0.5
            
            if distance < enemy.rect.width / 2 + self.player.rect.width / 2:
                # 敌人攻击玩家，只有当攻击成功时才播放音效
                if enemy.attack_player(self.player):
                    # 播放玩家受伤音效
                    resource_manager.play_sound("player_hurt")
        
    def _update_game_state(self):
        # 获取当前等级
        current_level = int(self.game_time // 60) + 1  # 每60秒提升一级
        
        # 如果等级提升了
        if current_level > self.level:
            # 播放升级音效
            resource_manager.play_sound("level_up")
            
        # 更新等级和难度
        self.level = current_level
        self.enemy_manager.difficulty = self.level 