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