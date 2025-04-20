import pygame
import os

class FontManager:
    @staticmethod
    def get_font(size=36):
        """
        获取支持中文的字体
        
        Args:
            size: 字体大小
            
        Returns:
            pygame.font.Font: 支持中文的字体对象
        """
        # 检查常见的中文字体路径
        font_path = None
        possible_fonts = [
            # Windows 中文字体
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
            
            # macOS 中文字体
            "/System/Library/Fonts/PingFang.ttc",
            
            # Linux 中文字体
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        ]

        for font in possible_fonts:
            if os.path.exists(font):
                font_path = font
                break
        
        try:
            if font_path:
                return pygame.font.Font(font_path, size)
            else:
                # 如果找不到中文字体，使用系统默认字体
                return pygame.font.SysFont("arial", size)
        except:
            # 如果出错，回退到默认字体
            return pygame.font.Font(None, size) 
    

def create_default_knife_image():
    """
    创建一个默认的像素风格刀具图案
    返回: 保存的文件路径
    """
    # 创建一个32x32的surface
    surface = pygame.Surface((32, 32), pygame.SRCALPHA)
    
    # 定义刀具的颜色
    blade_color = (192, 192, 192)  # 银色
    handle_color = (139, 69, 19)   # 棕色
    
    # 绘制刀刃（一个简单的三角形）
    blade_points = [(16, 4), (20, 12), (12, 12)]
    pygame.draw.polygon(surface, blade_color, blade_points)
    
    # 绘制刀柄
    pygame.draw.rect(surface, handle_color, (14, 12, 4, 16))
    
    # 确保目录存在
    os.makedirs('assets/images/weapons', exist_ok=True)
    
    # 保存图像
    file_path = 'assets/images/weapons/knife.png'
    pygame.image.save(surface, file_path)
    
    return file_path 

def pixel_perfect_collision(surface1, rect1, surface2, rect2):
    """
    实现基于像素的精确碰撞检测
    
    Args:
        surface1: 第一个对象的Surface
        rect1: 第一个对象的矩形位置
        surface2: 第二个对象的Surface
        rect2: 第二个对象的矩形位置
        
    Returns:
        bool: 如果两个对象在像素级别发生碰撞则返回True
    """
    # 计算重叠区域
    overlap_rect = rect1.clip(rect2)
    
    if overlap_rect.width == 0 or overlap_rect.height == 0:
        return False
    
    # 计算重叠区域在每个表面上的坐标
    offset_1 = (overlap_rect.x - rect1.x, overlap_rect.y - rect1.y)
    offset_2 = (overlap_rect.x - rect2.x, overlap_rect.y - rect2.y)
    
    # 创建子表面
    try:
        subsurface1 = surface1.subsurface((offset_1[0], offset_1[1], overlap_rect.width, overlap_rect.height))
        subsurface2 = surface2.subsurface((offset_2[0], offset_2[1], overlap_rect.width, overlap_rect.height))
    except ValueError:
        # 如果无法创建子表面，可能是因为重叠区域位于表面之外
        return False
    
    # 获取重叠区域的像素数组
    pixels1 = pygame.surfarray.array_alpha(subsurface1)
    pixels2 = pygame.surfarray.array_alpha(subsurface2)
    
    # 检查是否有重叠的非透明像素
    for x in range(overlap_rect.width):
        for y in range(overlap_rect.height):
            if pixels1[x, y] > 127 and pixels2[x, y] > 127:
                return True
    
    return False

def create_mask_from_surface(surface, threshold=127):
    """
    从Surface创建碰撞遮罩，提取图像边缘
    
    Args:
        surface: 源Surface对象
        threshold: Alpha通道阈值，大于此值的像素被认为是不透明的
        
    Returns:
        pygame.mask.Mask: 基于非透明像素的遮罩
    """
    return pygame.mask.from_surface(surface, threshold)

def apply_mask_collision(sprite1, sprite2):
    """
    使用图像遮罩检测两个精灵之间的碰撞
    
    Args:
        sprite1: 第一个精灵对象(需要有image和rect属性)
        sprite2: 第二个精灵对象(需要有image和rect属性)
        
    Returns:
        bool: 如果遮罩碰撞则返回True，否则返回False
    """
    # 为精灵创建遮罩(如果尚未创建)
    if not hasattr(sprite1, 'mask') or sprite1.mask is None:
        sprite1.mask = create_mask_from_surface(sprite1.image)
    if not hasattr(sprite2, 'mask') or sprite2.mask is None:
        sprite2.mask = create_mask_from_surface(sprite2.image)
    
    # 计算偏移量
    offset = (
        sprite2.rect.x - sprite1.rect.x,
        sprite2.rect.y - sprite1.rect.y
    )
    
    # 检测遮罩碰撞
    return sprite1.mask.overlap(sprite2.mask, offset) is not None

def extract_sprite_outline(surface, outline_color=(255, 0, 0), outline_thickness=1):
    """
    提取精灵图像的轮廓并创建带轮廓的新图像
    
    Args:
        surface: 源Surface对象
        outline_color: 轮廓颜色(R,G,B)
        outline_thickness: 轮廓粗细，以像素为单位
        
    Returns:
        pygame.Surface: 包含原始图像和其轮廓的新Surface
    """
    # 创建一个与原始Surface相同大小的新Surface(带透明通道)
    if surface.get_alpha() is None:
        outline_surface = pygame.Surface(surface.get_size()).convert_alpha()
        outline_surface.fill((0, 0, 0, 0))
    else:
        outline_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA).convert_alpha()
        outline_surface.fill((0, 0, 0, 0))
    
    # 创建遮罩并提取轮廓
    mask = create_mask_from_surface(surface)
    outline_mask = pygame.mask.Mask(mask.get_size())
    
    # 扩大遮罩以创建轮廓
    for x in range(mask.get_size()[0]):
        for y in range(mask.get_size()[1]):
            if mask.get_at((x, y)):
                for dx in range(-outline_thickness, outline_thickness + 1):
                    for dy in range(-outline_thickness, outline_thickness + 1):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < mask.get_size()[0] and 0 <= ny < mask.get_size()[1]:
                            outline_mask.set_at((nx, ny), 1)
    
    # 保留轮廓而移除原始形状区域
    for x in range(mask.get_size()[0]):
        for y in range(mask.get_size()[1]):
            if mask.get_at((x, y)):
                outline_mask.set_at((x, y), 0)
    
    # 将轮廓绘制到新表面
    outline_surface_tmp = outline_mask.to_surface(setcolor=outline_color)
    outline_surface_tmp.set_colorkey((0, 0, 0))
    outline_surface.blit(outline_surface_tmp, (0, 0))
    
    # 将原始图像绘制在轮廓上方
    outline_surface.blit(surface, (0, 0))
    
    return outline_surface

def create_outlined_sprite(sprite, outline_color=(255, 0, 0), outline_thickness=1):
    """
    为精灵添加可见轮廓
    
    Args:
        sprite: 精灵对象(需要有image属性)
        outline_color: 轮廓颜色(R,G,B)
        outline_thickness: 轮廓粗细，以像素为单位
        
    Returns:
        pygame.Surface: 带有轮廓的图像
    """
    # 确保精灵有图像
    if not hasattr(sprite, 'image') or sprite.image is None:
        return None
    
    # 创建轮廓图像
    outlined_image = extract_sprite_outline(
        sprite.image,
        outline_color=outline_color,
        outline_thickness=outline_thickness
    )
    
    return outlined_image 