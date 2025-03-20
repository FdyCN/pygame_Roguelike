import pygame
from .player import Player
from .enemy_manager import EnemyManager
from .weapons.weapon_manager import WeaponManager
from .item_manager import ItemManager
from .ui import UI
from .menu import PauseMenu, GameOverMenu, UpgradeMenu
from .resource_manager import resource_manager

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.paused = False
        self.game_over = False
        
        # 初始化资源
        self._init_resources()
        
        # 获取屏幕中心点
        self.screen_center_x = self.screen.get_width() // 2
        self.screen_center_y = self.screen.get_height() // 2
        
        # 创建玩家在屏幕中心
        self.player = Player(self.screen_center_x, self.screen_center_y)
        
        # 相机位置（对应于世界坐标系中的位置）
        self.camera_x = 0
        self.camera_y = 0
        
        # 网格设置
        self.grid_size = 50  # 网格大小
        self.grid_color = (50, 50, 50)  # 网格颜色
        
        self.enemy_manager = EnemyManager()
        self.weapon_manager = WeaponManager(self.player)
        self.item_manager = ItemManager()
        self.ui = UI(screen)
        
        # 创建菜单
        self.pause_menu = PauseMenu(screen)
        self.game_over_menu = GameOverMenu(screen)
        self.upgrade_menu = UpgradeMenu(screen)  # 添加升级菜单
        
        # 游戏状态
        self.game_time = 0
        self.score = 0
        self.level = 1
        
        # 播放背景音乐
        resource_manager.play_music("background", loops=-1)
        
    def _init_resources(self):
        """初始化游戏所需的资源"""
        # 加载背景音乐
        resource_manager.load_music("background", "music/background.mp3")
        
        # 加载音效
        resource_manager.load_sound("hit", "sounds/hit.wav")
        resource_manager.load_sound("enemy_death", "sounds/enemy_death.wav")
        resource_manager.load_sound("player_hurt", "sounds/player_hurt.wav")
        resource_manager.load_sound("level_up", "sounds/level_up.wav")
        resource_manager.load_sound("collect_exp", "sounds/collect_exp.wav")
        resource_manager.load_sound("collect_coin", "sounds/collect_coin.wav")
        resource_manager.load_sound("heal", "sounds/heal.wav")
        resource_manager.load_sound("upgrade", "sounds/upgrade.wav")  # 添加升级选择音效
        
        # 设置音量
        resource_manager.set_music_volume(0.5)  # 背景音乐音量
        for sound_name in ["hit", "enemy_death", "player_hurt", "level_up", 
                          "collect_exp", "collect_coin", "heal", "upgrade"]:
            resource_manager.set_sound_volume(sound_name, 0.7)  # 音效音量
        
    def handle_event(self, event):
        # 处理游戏结束菜单事件
        if self.game_over:
            action = self.game_over_menu.handle_event(event)
            if action == "restart":
                self.restart()
            elif action == "exit":
                self.running = False
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
            elif action == "restart":
                self.restart()
            elif action == "exit":
                self.running = False
            return
            
        # 处理ESC键暂停
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.toggle_pause()
            return
            
        # 处理玩家输入
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
        
    def restart(self):
        # 重置游戏状态
        self.paused = False
        self.game_over = False
        self.pause_menu.is_active = False
        self.game_over_menu.hide()
        
        # 重置玩家
        self.player = Player(self.screen_center_x, self.screen_center_y)
        
        # 重置相机
        self.camera_x = 0
        self.camera_y = 0
        
        # 重置敌人和武器
        self.enemy_manager = EnemyManager()
        self.weapon_manager = WeaponManager(self.player)
        self.item_manager = ItemManager()
        
        # 重置游戏状态
        self.game_time = 0
        self.score = 0
        self.level = 1
        
        # 重新播放背景音乐
        resource_manager.play_music("background", loops=-1)
        
    def update(self, dt):
        # 如果游戏结束或暂停或正在选择升级，只更新菜单
        if self.game_over:
            self.game_over_menu.update(pygame.mouse.get_pos())
            return
            
        if self.paused or self.upgrade_menu.is_active:
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
        # 清空屏幕
        self.screen.fill((0, 0, 0))
        
        # 绘制网格
        self._draw_grid()
        
        # 渲染游戏对象（考虑相机偏移）
        self.enemy_manager.render(self.screen, self.camera_x, self.camera_y, 
                                self.screen_center_x, self.screen_center_y)
        self.weapon_manager.render(self.screen, self.camera_x, self.camera_y, 
                                 self.screen_center_x, self.screen_center_y)
        self.item_manager.render(self.screen, self.camera_x, self.camera_y, 
                               self.screen_center_x, self.screen_center_y)
        
        # 渲染玩家（始终在屏幕中心）
        self.player.render(self.screen)
        
        # 渲染UI
        self.ui.render(self.player)
        
        # 如果游戏暂停，渲染暂停菜单
        if self.paused:
            self.pause_menu.render()
            
        # 如果正在选择升级，渲染升级菜单
        if self.upgrade_menu.is_active:
            self.upgrade_menu.render()
            
        # 如果游戏结束，渲染游戏结束菜单
        if self.game_over:
            self.game_over_menu.render()
        
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
            for enemy in self.enemy_manager.enemies:
                # 计算世界坐标系中的距离
                dx = enemy.rect.x - (self.player.world_x + weapon.offset_x)
                dy = enemy.rect.y - (self.player.world_y + weapon.offset_y)
                distance = (dx**2 + dy**2)**0.5
                
                if distance < enemy.rect.width / 2 + weapon.rect.width / 2:
                    enemy.take_damage(weapon.damage)
                    # 播放击中音效
                    resource_manager.play_sound("hit")
                    if enemy.health <= 0:
                        self.score += enemy.score_value
                        # 在敌人死亡位置生成物品
                        self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type)
                        self.enemy_manager.remove_enemy(enemy)
                        # 播放敌人死亡音效
                        resource_manager.play_sound("enemy_death")
        
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