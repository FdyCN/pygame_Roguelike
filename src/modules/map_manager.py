import os
import pygame
import pytmx
import pyscroll
from pytmx.util_pygame import load_pygame
from .resource_manager import resource_manager

class MapManager:
    """地图管理器类，用于加载和渲染TMX地图文件"""
    
    def __init__(self, screen):
        """初始化地图管理器
        
        Args:
            screen: pygame显示屏幕
        """
        self.screen = screen
        self.current_map = None
        self.map_layer = None
        self.map_group = None
        self.tmx_data = None  # 保存原始TMX数据，用于直接渲染
        
        # 性能优化：添加图块缓存和视口计算
        self.tile_cache = {}  # 缓存已渲染的图块
        self.last_camera_pos = None  # 上一次相机位置，用于检测相机是否移动
        self.visible_tiles = []  # 当前视口可见的图块
        self.use_direct_render = False  # 是否使用直接渲染（作为后备方案）
        
    def load_map(self, map_name):
        """加载TMX地图文件
        
        Args:
            map_name: 地图文件名，不包含扩展名
            
        Returns:
            bool: 加载成功返回True，否则返回False
        """
        # 构建地图文件的完整路径
        map_path = os.path.join(resource_manager.resource_dir, "maps", f"{map_name}.tmx")
        print("load map from {}".format(map_path))
        
        try:
            # 使用pytmx.util_pygame直接加载TMX文件
            try:
                self.tmx_data = load_pygame(map_path)
                print(f"TMX文件加载成功，图层数量: {len(self.tmx_data.layers)}")
                
                # 输出图块集信息
                print("\n图块集信息:")
                for i, tileset in enumerate(self.tmx_data.tilesets):
                    print(f"图块集 {i+1}:")
                    print(f"  首GID: {tileset.firstgid}")
                    print(f"  名称: {tileset.name}")
                    if hasattr(tileset, 'source') and tileset.source:
                        print(f"  源文件: {tileset.source}")
                        # 检查源文件是否存在
                        source_path = os.path.join(os.path.dirname(map_path), tileset.source)
                        print(f"  源文件完整路径: {source_path}")
                        print(f"  源文件是否存在: {os.path.exists(source_path)}")
                
                # 获取地图尺寸
                self.tile_width = self.tmx_data.tilewidth
                self.tile_height = self.tmx_data.tileheight
                self.map_width = self.tmx_data.width * self.tile_width
                self.map_height = self.tmx_data.height * self.tile_height
                
                print(f"\n地图尺寸: {self.map_width}x{self.map_height} 像素")
                print(f"图块尺寸: {self.tile_width}x{self.tile_height} 像素")
                
                # 存储地图数据
                self.current_map = {
                    'name': map_name,
                    'tmx_data': self.tmx_data
                }
                
                # 性能优化：预缓存所有图块
                self._cache_all_tiles()
                
                # 尝试创建pyscroll的渲染器（可能会失败，但不影响直接渲染）
                try:
                    # 创建地图数据
                    map_data = pyscroll.data.TiledMapData(self.tmx_data)
                    
                    # 创建地图层
                    self.map_layer = pyscroll.orthographic.BufferedRenderer(
                        map_data,
                        self.screen.get_size(),
                        clamp_camera=True  # 限制相机不超出地图边界
                    )
                    
                    # 缩放比例可以调整
                    self.map_layer.zoom = 1.0
                    
                    # 创建地图精灵组
                    self.map_group = pyscroll.PyscrollGroup(map_layer=self.map_layer)
                    print("成功创建pyscroll渲染器")
                    self.use_direct_render = False
                except Exception as e:
                    print(f"创建pyscroll渲染器失败，将使用优化的直接渲染: {e}")
                    self.map_layer = None
                    self.map_group = None
                    self.use_direct_render = True
                
                print(f"地图 '{map_name}' 加载成功")
                return True
                
            except Exception as e:
                print(f"加载TMX文件时出错: {e}")
                import traceback
                traceback.print_exc()
                return False
                
        except Exception as e:
            print(f"加载地图 '{map_name}' 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _cache_all_tiles(self):
        """预缓存所有图块，提高渲染性能"""
        if not self.tmx_data:
            return
            
        self.tile_cache = {}
        
        # 遍历所有图层和图块，缓存它们
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    if gid:  # 图块ID不为0
                        if gid not in self.tile_cache:
                            tile = self.tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                self.tile_cache[gid] = tile
        
        print(f"已缓存 {len(self.tile_cache)} 个不同的图块")
    
    def _calculate_visible_tiles(self, camera_x, camera_y):
        """计算当前视口内可见的图块
        
        Args:
            camera_x: 相机X位置（实际是负的偏移量）
            camera_y: 相机Y位置（实际是负的偏移量）
        """
        if not self.tmx_data:
            return
        
        # 计算视口边界（以图块为单位）
        viewport_left = max(0, int(-camera_x / self.tile_width))
        viewport_top = max(0, int(-camera_y / self.tile_height))
        
        # 计算视口右下角，多加几个图块确保覆盖整个屏幕
        viewport_right = min(
            self.tmx_data.width, 
            viewport_left + int(self.screen.get_width() / self.tile_width) + 2
        )
        viewport_bottom = min(
            self.tmx_data.height, 
            viewport_top + int(self.screen.get_height() / self.tile_height) + 2
        )
        
        # 存储可见的图块信息
        self.visible_tiles = []
        
        # 遍历所有图层
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                # 只处理视口内的图块
                layer_tiles = []
                for x in range(viewport_left, viewport_right):
                    for y in range(viewport_top, viewport_bottom):
                        gid = layer.data[y][x]  # 注意：在pytmx中y是行，x是列
                        if gid:
                            tile = self.tile_cache.get(gid)
                            if tile:
                                # 计算屏幕坐标
                                pos_x = x * self.tile_width + camera_x
                                pos_y = y * self.tile_height + camera_y
                                layer_tiles.append((tile, pos_x, pos_y))
                
                self.visible_tiles.append(layer_tiles)
    
    def render(self, camera_x, camera_y):
        """渲染地图
        
        Args:
            camera_x: 相机在世界坐标系中的X位置
            camera_y: 相机在世界坐标系中的Y位置
        """
        # 使用pyscroll渲染
        if self.map_layer and self.map_group and not self.use_direct_render:
            try:
                # 设置相机位置
                self.map_layer.center((camera_x, camera_y))
                
                # 绘制地图
                self.map_group.draw(self.screen)
                return
            except Exception as e:
                print(f"pyscroll渲染失败，切换到优化的直接渲染: {e}")
                self.use_direct_render = True
        
        # 优化的直接渲染
        if self.tmx_data:
            # 检查相机是否移动，如果移动了才重新计算可见图块
            if self.last_camera_pos != (camera_x, camera_y):
                self._calculate_visible_tiles(camera_x, camera_y)
                self.last_camera_pos = (camera_x, camera_y)
            
            # 绘制所有可见图块
            for layer_tiles in self.visible_tiles:
                for tile, pos_x, pos_y in layer_tiles:
                    self.screen.blit(tile, (pos_x, pos_y))
    
    def get_map_size(self):
        """获取地图尺寸
        
        Returns:
            tuple: (宽度,高度) 地图的像素尺寸
        """
        if not self.current_map:
            return (0, 0)
        
        return (self.map_width, self.map_height)
    
    def get_tile_size(self):
        """获取地图的瓦片尺寸
        
        Returns:
            tuple: (宽度,高度) 瓦片的像素尺寸
        """
        if not self.current_map:
            return (0, 0)
        
        return (self.tile_width, self.tile_height)
    
    def get_collision_tiles(self, layer_name="collision"):
        """获取指定层上的碰撞图块
        
        Args:
            layer_name: 碰撞层的名称
            
        Returns:
            list: 包含所有碰撞图块的矩形列表
        """
        if not self.current_map:
            return []
            
        tmx_data = self.current_map['tmx_data']
        collision_rects = []
        
        # 查找指定的碰撞层
        for layer in tmx_data.visible_layers:
            if hasattr(layer, 'name') and layer.name == layer_name:
                # 这是一个图块层
                if hasattr(layer, 'data'):
                    for x, y, gid in layer.iter_data():
                        if gid:  # 如果图块ID不为0
                            collision_rects.append(
                                pygame.Rect(
                                    x * self.tile_width,
                                    y * self.tile_height,
                                    self.tile_width,
                                    self.tile_height
                                )
                            )
                break
        
        return collision_rects
    
    def get_objects(self, layer_name):
        """获取指定对象层上的所有对象
        
        Args:
            layer_name: 对象层的名称
            
        Returns:
            list: 对象列表
        """
        if not self.current_map:
            return []
            
        tmx_data = self.current_map['tmx_data']
        objects = []
        
        # 查找指定的对象层
        try:
            object_layer = tmx_data.get_layer_by_name(layer_name)
            for obj in object_layer:
                objects.append({
                    'id': obj.id,
                    'name': getattr(obj, 'name', ''),
                    'type': getattr(obj, 'type', ''),
                    'x': obj.x,
                    'y': obj.y,
                    'width': getattr(obj, 'width', 0),
                    'height': getattr(obj, 'height', 0),
                    'properties': getattr(obj, 'properties', {})
                })
        except ValueError:
            # 如果找不到指定名称的层
            print(f"找不到名为 '{layer_name}' 的对象层")
        
        return objects 