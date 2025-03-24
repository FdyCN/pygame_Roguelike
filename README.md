# 游戏名字还没想好

这是一个使用 Cursor + Pygame 开发的2D像素风肉鸽游戏。边玩边学。
（50% cursor聊天与生成 + 15% debug + 15% codereview + 10% 找素材 + 4% 开开脑洞 + 4% 等待时玩手机 + 1% 写一些没有意义的README）
使用cursor 0.47.8 + claude-3.5-sonnet进行开发

## 项目结构

```
game_python/
├── assets/          # 游戏资源文件
│   ├── images/     # 图片资源
│   ├── sounds/     # 音效资源
│   └── fonts/      # 字体资源
├── saves/          # 存档文件夹
├── src/            # 源代码
│   ├── main.py     # 游戏入口
│   └── modules/    # 游戏模块
│       ├── enemies/         # 敌人相关
│       ├── weapons/         # 武器相关
│       ├── items/           # 物品相关
│       ├── menus/           # 菜单相关
│       ├── game.py          # 游戏主逻辑
│       ├── player.py        # 玩家类
│       ├── menu.py          # 菜单基类
│       ├── ui.py            # UI系统
│       ├── utils.py         # 工具函数
│       ├── upgrade_system.py # 升级系统
│       ├── save_system.py   # 存档系统
│       └── resource_manager.py # 资源管理器
├── requirements.txt  # 项目依赖
└── README.md        # 项目说明
```

## 安装

1. 确保已安装Python 3.8或更高版本
2. 安装依赖：
```bash
pip install -r requirements.txt
```
3. cursor版本：0.47.8
4. LLM: claude-3.5-sonnet （实测过程中不建议切换LLM来做代码生成，可能会导致代码风格差异比较大）

## 运行

在项目根目录下运行：
```bash
python src/main.py
```

## 游戏控制

- WASD：移动
- 鼠标左键：攻击
- ESC：暂停游戏
- 空格：确认/选择

## 游戏特性

- 多种敌人类型（幽灵、萝卜、蝙蝠）
- 武器系统（飞刀）
- 升级系统
- 存档系统
- 物品掉落系统
- 动画系统
- 音效系统

## 开发说明

- 使用Python 3.8+
- 基于Pygame 2.5.0
- 采用面向对象设计
- 模块化架构
- 支持存档功能
- 完整的资源管理系统

## 游戏特点

- 自动攻击系统
- 升级系统
- 敌人生成系统
- 难度随时间递增


## 游戏控制

- W/A/S/D - 移动角色
- ESC - 暂停游戏

## 开发说明

项目结构：
```
project/
├── assets/          # 图片、音效等资源
├── src/             # 源代码
│   ├── main.py      # 游戏入口
│   └── modules/     # 游戏模块
├── requirements.txt  # 项目依赖
└── README.md        # 项目说明
```

## 当前实现
- 玩玩看就知道了

## 待实现功能

- [ ] 添加更多武器类型
  - [ ] 重构下weapon_manager，被player持有更好些，方便后续的武器升级逻辑
- [x] 添加经验值系统
  - [x] 经验槽与经验值计算
  - [x] 与升级界面联动 
  - [ ] 升级效果关联武器和被动属性
- [x] 添加升级选择界面
  - [x] 支持随机升级三选一
  - [ ] 升级选项实现 
- [ ] 添加音效和背景音乐
- [ ] 添加更多敌人类型
  - [x] 添加Ghost\Radish\Bat三种敌人，其中Bat属于小boss类型
  - [ ] 优化敌人生成数量、时间等策略 
  - [ ] 增加敌人的debuff效果，如：减速、击退等
- [x] 实现物品掉落系统
  - [x] 金币掉落
  - [x] 经验球掉落
  - [x] 医疗包掉落
  - [ ] 宝箱掉落
- [ ] 主菜单
  - [x] 支持保存游戏和读取游戏
  - [ ] 支持设置
  - [ ] 支持全局的技能属性

## 致谢
素材：Ninja_Frog\Ghost\Bat\Radish 来自：[pixel-adventure](https://pixelfrog-assets.itch.io/pixel-adventure-1)