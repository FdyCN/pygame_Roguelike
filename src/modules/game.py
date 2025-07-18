import pygame
from .player import Player
from .enemies.enemy_manager import EnemyManager
from .items.item_manager import ItemManager
from .ui import UI
from .menu import PauseMenu, GameOverMenu, UpgradeMenu
from .menus.main_menu import MainMenu
from .menus.save_menu import SaveMenu
from .save_system import SaveSystem
from .resource_manager import resource_manager
from .upgrade_system import UpgradeManager, WeaponUpgradeLevel, PassiveUpgradeLevel
from .utils import apply_mask_collision
from .map_manager import MapManager
from .menus.map_hero_select_menu import MapHeroSelectMenu

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.paused = False
        self.game_over = False
        self.in_main_menu = True  # 是否在主菜单
        self.in_map_hero_select = False  # 是否在地图和英雄选择界面
        
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
        self.item_manager = None
        self.save_system = SaveSystem()
        self.upgrade_manager = UpgradeManager()
        self.map_manager = MapManager(screen)  # 创建地图管理器
        
        # 创建UI和菜单
        self.ui = UI(screen)
        self.main_menu = MainMenu(screen)
        self.pause_menu = PauseMenu(screen)
        self.game_over_menu = GameOverMenu(screen)
        self.upgrade_menu = UpgradeMenu(screen)
        self.save_menu = SaveMenu(screen, True)  # 保存菜单
        self.load_menu = SaveMenu(screen, False)  # 读取菜单
        
        # 创建地图和英雄选择菜单
        self.map_hero_select_menu = MapHeroSelectMenu(
            screen,
            on_start_game=self._start_game_with_selection,
            on_back=self._back_to_main_menu
        )
        
        # 游戏状态
        self.game_time = 0
        self.kill_num = 0 # 击杀数
        self.level = 1
        
        # 地图状态
        self.current_map = None  # 当前地图名称
        
    def _set_map_boundaries(self):
        """根据当前地图尺寸设置边界
        
        设置玩家的移动边界和敌人的生成边界
        """
        if not self.current_map:
            return
            
        # 获取地图尺寸
        map_width, map_height = self.map_manager.get_map_size()
        
        # 计算围栏宽度（两排32x32的围栏）
        fence_width = 2 * 32
        
        # 计算边界
        min_x = fence_width
        min_y = fence_width
        max_x = map_width - fence_width
        max_y = map_height - fence_width
        
        # 设置玩家移动边界
        if self.player:
            self.player.movement.set_boundaries(min_x, min_y, max_x, max_y)
            
        # 设置敌人生成边界
        if self.enemy_manager:
            self.enemy_manager.set_map_boundaries(min_x, min_y, max_x, max_y)
            
    def _set_player_boundaries(self):
        """设置玩家的移动边界
        
        根据当前地图的尺寸和围栏宽度设置玩家的移动边界
        """
        # 使用通用的边界设置方法
        self._set_map_boundaries()
        
    def _start_game_with_selection(self, map_id, hero_id):
        """根据选择的地图和英雄开始新游戏
        
        Args:
            map_id: 地图ID
            hero_id: 英雄ID
        """
        self.in_map_hero_select = False
        self.game_over = False
        self.paused = False
        
        # 加载选中的地图
        self.load_map(map_id)
        
        # 获取地图尺寸
        map_width, map_height = self.map_manager.get_map_size()
        
        # 创建新的玩家在地图中心
        self.player = Player(self.screen_center_x, self.screen_center_y, hero_id)
        
        # 设置玩家的世界坐标为地图中心
        self.player.world_x = map_width // 2
        self.player.world_y = map_height // 2
        
        # 初始化游戏管理器
        self.enemy_manager = EnemyManager()
        self.enemy_manager.set_difficulty("normal")  # 设置初始难度
        self.item_manager = ItemManager()
        
        # 设置边界
        self._set_map_boundaries()
        
        # 重置游戏状态
        self.game_time = 0
        self.kill_num = 0
        self.level = 1
        
        # 设置相机位置为玩家位置
        self.camera_x = self.player.world_x
        self.camera_y = self.player.world_y
        
        # 播放背景音乐
        resource_manager.play_music("background", loops=-1)
        
    def _back_to_main_menu(self):
        """从地图和英雄选择界面返回主菜单"""
        self.in_map_hero_select = False
        self.in_main_menu = True
        
    def start_new_game(self):
        """显示地图和英雄选择界面"""
        self.in_main_menu = False
        self.in_map_hero_select = True
        self.map_hero_select_menu.show()
            
    def load_map(self, map_name):
        """加载指定名称的地图"""
        success = self.map_manager.load_map(map_name)
        if success:
            self.current_map = map_name
            
            # 获取地图尺寸
            map_width, map_height = self.map_manager.get_map_size()
            
            # 根据地图尺寸设置玩家的起始位置和边界
            if self.player:
                # 将玩家放置在地图中心
                self.player.world_x = map_width // 2
                self.player.world_y = map_height // 2
                
                # 更新相机位置跟随玩家
                self.camera_x = self.player.world_x
                self.camera_y = self.player.world_y
                
                # 设置玩家和敌人边界
                self._set_map_boundaries()
            
        else:
            print(f"加载地图 '{map_name}' 失败")
            
        return success

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
                
            # 创建新的玩家实例，使用存档中的英雄类型
            hero_type = player_data.get('hero_type', 'ninja_frog')
            self.player = Player(self.screen_center_x, self.screen_center_y, hero_type)
            
            # 设置玩家属性
            self.player.health = player_data.get('health', self.player.health)
            self.player.health_component.max_health = player_data.get('max_health', self.player.health_component.max_health)
            self.player.progression.level = player_data.get('level', self.player.progression.level)
            self.player.progression.experience = player_data.get('experience', 0)
            self.player.progression.coins = player_data.get('coins', 0)
            self.player.world_x = player_data.get('world_x', self.screen_center_x)
            self.player.world_y = player_data.get('world_y', self.screen_center_y)
            
            # 加载组件状态
            component_states = player_data.get('component_states', {})
            if component_states:
                # 移动组件
                movement_states = component_states.get('movement', {})
                if movement_states:
                    self.player.movement.speed = movement_states.get('speed', self.player.movement.speed)
                    # 重置移动状态，确保加载存档后可以正常移动
                    self.player.movement.direction = pygame.math.Vector2(0, 0)
                    self.player.movement.velocity = pygame.math.Vector2(0, 0)
                    self.player.movement.moving = {
                        'up': False, 
                        'down': False, 
                        'left': False, 
                        'right': False
                    }
                    # 保留朝向状态，如果有的话
                    if 'facing_right' in movement_states:
                        self.player.movement.facing_right = movement_states.get('facing_right')
                    if 'last_direction_x' in movement_states and 'last_direction_y' in movement_states:
                        self.player.movement.last_movement_direction.x = movement_states.get('last_direction_x', 1)
                        self.player.movement.last_movement_direction.y = movement_states.get('last_direction_y', 0)
                
                # 生命值组件
                health_states = component_states.get('health', {})
                if health_states:
                    self.player.health_component.defense = health_states.get('defense', self.player.health_component.defense)
                    self.player.health_component.health_regen = health_states.get('health_regen', self.player.health_component.health_regen)
                
                # 进阶组件
                progression_states = component_states.get('progression', {})
                if progression_states:
                    self.player.progression.exp_multiplier = progression_states.get('exp_multiplier', self.player.progression.exp_multiplier)
                    self.player.progression.luck = progression_states.get('luck', self.player.progression.luck)
                
                # 被动组件
                passive_states = component_states.get('passive', {})
                if passive_states and 'passive_levels' in passive_states:
                    # 恢复被动技能状态
                    passive_levels = passive_states['passive_levels']
                    for passive_type, level in passive_levels.items():
                        # 获取被动技能对应等级的效果
                        if passive_type in self.upgrade_manager.passive_upgrades:
                            upgrade = self.upgrade_manager.passive_upgrades[passive_type]
                            # 查找对应等级的效果
                            effect = None
                            for lvl in upgrade.levels:
                                if lvl.level == level:
                                    effect = lvl.effects
                                    break
                            
                            # 应用被动技能效果
                            if effect:
                                self.player.apply_passive_upgrade(passive_type, level, effect)
                            else:
                                # 如果找不到具体效果，直接设置等级
                                self.player.passive_manager.passive_levels[passive_type] = level
                        else:
                            # 如果找不到具体升级，直接设置等级
                            self.player.passive_manager.passive_levels[passive_type] = level
                    
                    # 更新状态以应用所有被动效果
                    self.player._update_stats()
            
            # 加载武器
            weapons_data = player_data.get('weapons', [])
            if weapons_data:
                # 清空现有武器
                for weapon in list(self.player.weapons):
                    self.player.weapon_manager.remove_weapon(weapon.type)
                
                # 添加存档中的武器
                for weapon_type, level in weapons_data:
                    weapon = self.player.add_weapon(weapon_type)
                    if weapon:
                        weapon.level = level
            
            # 初始化游戏管理器
            self.enemy_manager = EnemyManager()
            self.item_manager = ItemManager()
            
            # 恢复游戏状态
            game_data = save_data.get('game_data', {})
            self.game_time = game_data.get('game_time', 0)
            self.kill_num = game_data.get('kill_num', 0)
            self.level = game_data.get('level', 1)
            
            # 设置敌人管理器的难度和等级
            self.enemy_manager.difficulty_level = self.level
            self.enemy_manager.set_difficulty(game_data.get('difficulty', 'normal'))
            
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
            
            # 设置边界
            self._set_map_boundaries()
            
            # 播放背景音乐
            resource_manager.play_music("background", loops=-1)
            
            return True
            
        except Exception as e:
            print(f"加载存档时出错: {e}")
            # 如果加载失败，重置到初始状态
            self.start_new_game()
            return False
        
    def handle_event(self, event):
        # 如果在地图和英雄选择界面
        if self.in_map_hero_select:
            result = self.map_hero_select_menu.handle_event(event)
            # 不需要处理返回值，因为已经在回调函数中处理了
            return
            
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
            elif action == "load":
                print("显示读取菜单")  # 调试信息
                self.load_menu.show()
            elif action == "quit":
                self.running = False  # 设置running为False以退出游戏
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
            elif action == "main_menu":
                self.in_main_menu = True
                self.game_over = False
                resource_manager.stop_music()  # 停止游戏音乐
            elif action == "exit":
                self.running = False  # 退出游戏
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
               
        # 如果正在选择升级
        if self.upgrade_menu.is_active:
            selected_upgrade = self.upgrade_menu.handle_event(event)
            if selected_upgrade:
                self._apply_upgrade(selected_upgrade)
                self.upgrade_menu.hide()  # 关闭升级菜单，让游戏继续
            return True
            
        # ESC键暂停游戏
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()
                return True
            elif event.key == pygame.K_F2:
                # 切换显示轮廓
                # TODO: 显示轮廓的逻辑放到全局的'设置'菜单中进行
                if self.player:
                    self.player.toggle_outline()
                    # 切换敌人的轮廓
                    for enemy in self.enemy_manager.enemies:
                        enemy.toggle_outline()
                return True
            
        # 处理玩家输入
        if self.player:
            self.player.handle_event(event)
            
        return True
        
    def _apply_upgrade(self, upgrade_level):
        """应用升级效果
        
        Args:
            upgrade_level: WeaponUpgradeLevel 或 PassiveUpgradeLevel 实例
        """
        if isinstance(upgrade_level, WeaponUpgradeLevel):
            # 获取武器类型
            weapon_type = None
            for type_, upgrade in self.upgrade_manager.weapon_upgrades.items():
                if upgrade_level in upgrade.levels:
                    weapon_type = type_
                    break
                    
            if weapon_type:
                if self.player.apply_weapon_upgrade(weapon_type, upgrade_level.level, upgrade_level.effects):
                    # 如果是新武器，创建并添加到玩家的武器列表
                    if len([w for w in self.player.weapons if w.type == weapon_type]) == 0:
                        self.player.add_weapon(weapon_type)
                        
        elif isinstance(upgrade_level, PassiveUpgradeLevel):
            # 获取被动类型
            passive_type = None
            for type_, upgrade in self.upgrade_manager.passive_upgrades.items():
                if upgrade_level in upgrade.levels:
                    passive_type = type_
                    break
                    
            if passive_type:
                self.player.apply_passive_upgrade(passive_type, upgrade_level.level, upgrade_level.effects)
                
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
        # 保持游戏状态的更新
        if self.in_main_menu:
            return
            
        # 如果在地图和英雄选择界面，只更新菜单，不更新游戏逻辑
        if self.in_map_hero_select:
            return
            
        # 检查玩家是否死亡
        if self.player and self.player.health <= 0 and not self.game_over:
            self.game_over = True
            self.game_over_menu.show()
            # 播放游戏结束音效
            resource_manager.play_sound("player_death")
            return
            
        # 如果游戏结束，更新游戏结束菜单
        if self.game_over:
            self.game_over_menu.update(pygame.mouse.get_pos())
            return
            
        # 如果暂停或者正在选择升级，不更新游戏状态
        if self.paused or self.upgrade_menu.is_active or self.save_menu.is_active:
            return
            
        self.game_time += dt
        
        # 确保玩家对象存在再更新
        if self.player:
            # 更新玩家位置（在世界坐标系中）
            self.player.update(dt)
            
            # 边界检测已在MovementComponent中处理
            # 如果需要，可以作为额外的保障措施
            # self._set_map_boundaries()
            
            # 更新相机位置（跟随玩家）
            self.camera_x = self.player.world_x
            self.camera_y = self.player.world_y
        
        # 更新其他游戏对象，注意检查player和enemy_manager是否存在
        if self.enemy_manager and self.player:
            # 处理被状态效果（如燃烧）导致死亡的敌人
            for enemy in list(self.enemy_manager.enemies):  # 使用列表复制避免在迭代时修改
                if enemy in self.enemy_manager.enemies and not enemy.alive():
                    self.kill_num += 1
                    # 在敌人死亡位置生成物品，传递player对象以应用幸运值加成
                    if self.item_manager:
                        self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type, self.player)
                    # 敌人已经在enemy_manager.update()中被移除，无需再次移除
            
            # 更新敌人和武器
            self.enemy_manager.update(dt, self.player)
            self.player.update_weapons(dt, self.enemy_manager.enemies)
            
            # 更新物品
            if self.item_manager:
                self.item_manager.update(dt, self.player)
            
            # 检测碰撞
            self._check_collisions()
            
            # 检查是否可以升级
            if self.player.add_experience(0):  # 检查是否可以升级，不添加经验值
                self.player.level_up()
                self.upgrade_menu.show(self.player, self)  # 显示升级选择菜单，传入Game实例
        
    def render(self):
        """渲染游戏画面"""
        # 清屏
        self.screen.fill((0, 0, 0))  # 黑色背景
        
        # 如果在主菜单
        if self.in_main_menu:
            # 如果读取菜单激活，只渲染读取菜单
            if self.load_menu.is_active:
                self.load_menu.render()
            else:
                # 否则渲染主菜单
                self.main_menu.render()
            pygame.display.flip()
            return
            
        # 如果在地图和英雄选择界面
        if self.in_map_hero_select:
            self.map_hero_select_menu.render()
            pygame.display.flip()
            return
            
        # 如果正在保存游戏
        if self.save_menu.is_active:
            self.save_menu.render()
            return
            
        # 绘制地图（如果已加载）
        if self.current_map:
            self.map_manager.render(self.camera_x, self.camera_y)
        else:
            # 如果没有地图，绘制网格作为背景
            self._draw_grid()
        
        # 确保游戏对象存在再渲染
        if self.enemy_manager:
            # 渲染游戏对象（考虑相机偏移）
            self.enemy_manager.render(self.screen, self.camera_x, self.camera_y, 
                                   self.screen_center_x, self.screen_center_y)
        
        if self.item_manager:
            self.item_manager.render(self.screen, self.camera_x, self.camera_y, 
                                  self.screen_center_x, self.screen_center_y)
        
        # 渲染玩家（始终在屏幕中心）
        if self.player:
            self.player.render(self.screen)
            self.player.render_weapons(self.screen, self.camera_x, self.camera_y)
            
            # 渲染UI
            self.ui.render(self.player, self.game_time, self.kill_num)
            
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
        """检测碰撞"""
        # 确保玩家和敌人管理器存在
        if not self.player or not self.enemy_manager:
            return
            
        # 检测武器碰撞
        for weapon in self.player.weapons:
            for projectile in weapon.get_projectiles():
                for enemy in self.enemy_manager.enemies:
                    # 首先使用矩形做快速检测
                    # 计算世界坐标系中的距离
                    dx = enemy.rect.x - projectile.world_x
                    dy = enemy.rect.y - projectile.world_y
                    distance = (dx**2 + dy**2)**0.5
                    
                    if distance < enemy.rect.width / 2 + projectile.rect.width / 2:
                        # 进行更精确的像素级碰撞检测
                        # 调整projectile的rect以匹配world坐标
                        projectile_rect = projectile.rect.copy()
                        projectile_rect.centerx = projectile.world_x
                        projectile_rect.centery = projectile.world_y
                        
                        if apply_mask_collision(enemy, projectile):
                            # 处理碰撞
                            should_destroy = weapon.handle_collision(projectile, enemy, self.enemy_manager.enemies)
                            # 播放击中音效
                            resource_manager.play_sound("hit")
                            
                            if enemy.health <= 0:
                                self.kill_num += 1
                                # 在敌人死亡位置生成物品，传递player对象以应用幸运值加成
                                if self.item_manager:
                                    self.item_manager.spawn_item(enemy.rect.x, enemy.rect.y, enemy.type, self.player)
                                self.enemy_manager.remove_enemy(enemy)
                                # 播放敌人死亡音效
                                resource_manager.play_sound("enemy_death")
                                
                            if should_destroy:
                                projectile.kill()
        
        # 检测玩家和敌人的碰撞
        for enemy in self.enemy_manager.enemies:
            if not self.player.invincible:  # 只在玩家不处于无敌状态时检测碰撞
                # 首先进行矩形快速检测
                player_rect = self.player.rect.copy()
                player_rect.centerx = self.player.world_x
                player_rect.centery = self.player.world_y
                
                # 对于Slime等远程攻击敌人，即使不直接碰撞也需要触发attack_player
                # 这样才能正确生成投射物并处理碰撞逻辑
                if hasattr(enemy, 'projectiles'):
                    enemy.attack_player(self.player)
                
                # 对于直接碰撞的敌人，进行常规碰撞检测
                if player_rect.colliderect(enemy.rect):
                    # 进行像素级碰撞检测
                    if apply_mask_collision(self.player, enemy):
                        if enemy.attack_player(self.player):
                            # 播放受伤音效
                            resource_manager.play_sound("player_hurt")
                            break  # 一次只处理一个碰撞
        
    def _update_game_state(self):
        # 获取当前等级
        current_level = int(self.game_time // 60) + 1  # 每60秒提升一级
        
        # 如果等级提升了
        if current_level > self.level:
            # 播放升级音效
            resource_manager.play_sound("level_up")
            
        # 更新等级和难度
        self.level = current_level
        
        # 确保敌人管理器存在再更新难度
        if self.enemy_manager:
            self.enemy_manager.difficulty_level = self.level  # 更新敌人管理器中的难度等级 