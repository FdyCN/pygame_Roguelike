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