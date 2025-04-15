import os
import pygame

class SpriteSheet:
    """精灵表类，用于管理包含多帧动画的图片"""
    def __init__(self, image):
        self.sheet = image

    def get_sprite(self, x, y, width, height):
        """从精灵表中获取单帧图像
        
        Args:
            x: 帧的x坐标
            y: 帧的y坐标
            width: 帧的宽度
            height: 帧的高度
            
        Returns:
            pygame.Surface: 裁剪出的单帧图像
        """
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite

class Animation:
    """动画类，用于管理一组帧的播放"""
    def __init__(self, frames, frame_duration=0.1, loop=True):
        """
        Args:
            frames: 帧列表
            frame_duration: 每帧持续时间(秒)
            loop: 是否循环播放
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.timer = 0
        self.finished = False

    def update(self, dt):
        """更新动画状态
        
        Args:
            dt: 时间增量
        """
        if self.finished:
            return

        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def get_current_frame(self):
        """获取当前帧"""
        return self.frames[self.current_frame]

    def reset(self):
        """重置动画状态"""
        self.current_frame = 0
        self.timer = 0
        self.finished = False

class ResourceManager:
    """资源管理器类,用于统一管理游戏资源"""
    
    def __init__(self):
        self.images = {}  # 存储图片资源
        self.sounds = {}  # 存储音效资源
        self.music = {}   # 存储音乐资源
        self.fonts = {}   # 存储字体资源
        self.animations = {}  # 存储动画资源
        
        # 资源根目录，使用规范化的路径
        current_file = os.path.abspath(__file__)
        src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        self.resource_dir = os.path.normpath(os.path.join(src_dir, "assets"))
        
    def load_image(self, name: str, file_path: str) -> pygame.Surface:
        """加载图片资源
        
        Args:
            name: 资源名称
            file_path: 相对于assets目录的文件路径
            
        Returns:
            pygame.Surface: 加载的图片surface
        """
        if name in self.images:
            return self.images[name]
            
        # 规范化路径，确保在所有操作系统上都能正确工作
        full_path = os.path.normpath(os.path.join(self.resource_dir, file_path))
        try:
            image = pygame.image.load(full_path).convert_alpha()
            self.images[name] = image
            return image
        except pygame.error as e:
            print(f"无法加载图片 {full_path}: {e}")
            # 返回一个1x1的紫色surface作为错误提示
            surface = pygame.Surface((1, 1))
            surface.fill((255, 0, 255))
            return surface
            
    def load_sound(self, name: str, file_path: str) -> pygame.mixer.Sound:
        """加载音效资源
        
        Args:
            name: 资源名称
            file_path: 相对于assets目录的文件路径
            
        Returns:
            pygame.mixer.Sound: 加载的音效对象
        """

        return None
    
        if name in self.sounds:
            return self.sounds[name]
            
        # 规范化路径，确保在所有操作系统上都能正确工作
        full_path = os.path.normpath(os.path.join(self.resource_dir, file_path))
        try:
            sound = pygame.mixer.Sound(full_path)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"无法加载音效 {full_path}: {e}")
            return None
            
    def load_music(self, name: str, file_path: str) -> str:
        """加载音乐资源
        
        Args:
            name: 资源名称
            file_path: 相对于assets目录的文件路径
            
        Returns:
            str: 音乐文件的完整路径
        """

        return None
        if name in self.music:
            return self.music[name]
            
        # 规范化路径，确保在所有操作系统上都能正确工作
        full_path = os.path.normpath(os.path.join(self.resource_dir, file_path))
        if os.path.exists(full_path):
            self.music[name] = full_path
            return full_path
        else:
            print(f"无法找到音乐文件 {full_path}")
            return None
            
    def get_image(self, name: str) -> pygame.Surface:
        """获取已加载的图片资源
        
        Args:
            name: 资源名称
            
        Returns:
            pygame.Surface: 图片surface,如果不存在返回错误提示图片
        """

        return None
        if name not in self.images:
            print(f"图片资源 {name} 未加载")
            surface = pygame.Surface((1, 1))
            surface.fill((255, 0, 255))
            return surface
        return self.images[name]
        
    def get_sound(self, name: str) -> pygame.mixer.Sound:
        """获取已加载的音效资源
        
        Args:
            name: 资源名称
            
        Returns:
            pygame.mixer.Sound: 音效对象,如果不存在返回None
        """
        return None
        if name not in self.sounds:
            print(f"音效资源 {name} 未加载")
            return None
        return self.sounds[name]
        
    def get_music(self, name: str) -> str:
        """获取已加载的音乐资源路径
        
        Args:
            name: 资源名称
            
        Returns:
            str: 音乐文件路径,如果不存在返回None
        """
        return None
        if name not in self.music:
            print(f"音乐资源 {name} 未加载")
            return None
        return self.music[name]
        
    def play_sound(self, name: str):
        """播放音效
        
        Args:
            name: 音效资源名称
        """
        return None
        sound = self.get_sound(name)
        if sound:
            sound.play()
            
    def play_music(self, name: str, loops: int = -1):
        """播放音乐
        
        Args:
            name: 音乐资源名称
            loops: 循环次数,-1表示无限循环
        """
        return None
        music_path = self.get_music(name)
        if music_path:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops)
            
    def stop_music(self):
        """停止当前播放的音乐"""
        pygame.mixer.music.stop()
        
    def pause_music(self):
        """暂停当前播放的音乐"""
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        """恢复播放暂停的音乐"""
        pygame.mixer.music.unpause()
        
    def set_music_volume(self, volume: float):
        """设置音乐音量
        
        Args:
            volume: 音量值(0.0 - 1.0)
        """
        pygame.mixer.music.set_volume(volume)
        
    def set_sound_volume(self, name: str, volume: float):
        """设置指定音效的音量
        
        Args:
            name: 音效资源名称
            volume: 音量值(0.0 - 1.0)
        """
        sound = self.get_sound(name)
        if sound:
            sound.set_volume(volume)
            
    def load_spritesheet(self, name: str, file_path: str) -> SpriteSheet:
        """加载精灵表
        
        Args:
            name: 资源名称
            file_path: 相对于assets目录的文件路径
            
        Returns:
            SpriteSheet: 精灵表对象
        """
        image = self.load_image(name, file_path)
        return SpriteSheet(image)

    def create_animation(self, name: str, spritesheet: SpriteSheet, 
                        frame_width: int, frame_height: int, 
                        frame_count: int, row: int = 0,
                        col: int = 0,
                        frame_duration: float = 0.1, loop: bool = True) -> Animation:
        """从精灵表创建动画
        
        Args:
            name: 动画名称
            spritesheet: 精灵表对象
            frame_width: 每帧宽度
            frame_height: 每帧高度
            frame_count: 帧数量
            row: 精灵表中的行号(从0开始)
            col: 精灵表中的起始列号(从0开始)
            frame_duration: 每帧持续时间
            loop: 是否循环播放
            
        Returns:
            Animation: 动画对象
        """
        frames = []
        for i in range(frame_count):
            frame = spritesheet.get_sprite((col + i) * frame_width, row * frame_height, 
                                         frame_width, frame_height)
            frames.append(frame)
        
        animation = Animation(frames, frame_duration, loop)
        self.animations[name] = animation
        return animation

    def get_animation(self, name: str) -> Animation:
        """获取已加载的动画
        
        Args:
            name: 动画名称
            
        Returns:
            Animation: 动画对象
        """
        if name not in self.animations:
            print(f"动画 {name} 未加载")
            return None
        return self.animations[name]
            
    def clear(self):
        """清除所有已加载的资源"""
        self.images.clear()
        self.sounds.clear()
        self.music.clear()
        self.fonts.clear()
        self.animations.clear()

    def _init_resources(self):
        """初始化游戏所需的资源"""
        # 加载背景音乐
        self.load_music("background", "music/background.mp3")
        
        # 加载音效
        self.load_sound("hit", "sounds/hit.wav")
        self.load_sound("enemy_death", "sounds/enemy_death.wav")
        self.load_sound("player_hurt", "sounds/player_hurt.wav")
        self.load_sound("player_death", "sounds/player_hurt.wav")  # 使用player_hurt音效作为临时替代
        self.load_sound("level_up", "sounds/level_up.wav")
        self.load_sound("collect_exp", "sounds/collect_exp.wav")
        self.load_sound("collect_coin", "sounds/collect_coin.wav")
        self.load_sound("heal", "sounds/heal.wav")
        self.load_sound("upgrade", "sounds/upgrade.wav")
        self.load_sound("menu_move", "sounds/menu_move.wav")
        self.load_sound("menu_select", "sounds/menu_select.wav")
        
        # 设置音量
        self.set_music_volume(0.5)  # 背景音乐音量
        for sound_name in ["hit", "enemy_death", "player_hurt", "level_up", 
                          "collect_exp", "collect_coin", "heal", "upgrade",
                          "menu_move", "menu_select"]:
            self.set_sound_volume(sound_name, 0.7)  # 音效音量

# 创建全局资源管理器实例
resource_manager = ResourceManager() 