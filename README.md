# 游戏名字还没想好

这是一个使用 Cursor + Pygame 开发的2D像素风肉鸽游戏。边玩边学。

**（50% cursor聊天与生成 + 15% debug + 15% codereview + 10% 找素材 + 4% 开开脑洞 + 4% 等待时玩手机 + 1% 写一些没有意义的README）**

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
│       ├── components/      # Player组件
│       ├── enemies/         # 敌人相关
│       ├── weapons/         # 武器相关
│       ├── items/           # 物品相关
│       ├── menus/           # 菜单相关
│       ├── game.py          # 游戏主逻辑
│       ├── hero_config.py   # 不同英雄特性
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


## 当前实现
- 玩玩看就知道了

## 待实现功能
- [ ] 重构存档系统，感觉没必要支持存档（这个类型的游戏，没有开不同存档分支的必要）
- [ ] 添加更多武器类型
  - [x] 添加了火球术、冰霜新星的代码
  - [x] 完善火球术、冰霜新星的逻辑和特效
  - [ ] 添加武器debuff效果，如燃烧、减速等
- [x] 添加经验值系统
  - [x] 经验槽与经验值计算
  - [x] 与升级界面联动 
  - [x] 添加被动升级：攻击力、防御力、速度、生命恢复、幸运、拾取半径。
- [ ] 添加系统素材
  - [ ] 添加音效
  - [ ] 添加地图
- [ ] 敌人系统扩展，攻击方式和debuff判定等
  - [x] 添加Ghost\Radish\Bat\Slime三种敌人，其中Bat属于小boss类型，Slime属于远程攻击敌人
  - [ ] 优化敌人生成数量、时间等策略 
  - [ ] 增加敌人的debuff效果，如：减速、击退等
- [x] 优化物品掉落系统
  - [ ] 宝箱掉落与抽奖逻辑
  - [ ] 不同的经验球类型
  - [ ] 随机生成可击破的道具
- [ ] 交互菜单
  - [x] 主菜单、暂停菜单支持保存游戏和读取游戏
  - [ ] 开始新游戏，支持英雄选择、难易度选择
  - [ ] 支持设置
  - [ ] 支持全局的技能属性

## 致谢
素材：
- Ninja_Frog\Ghost\Bat\Radish 来自：[pixel-adventure](https://pixelfrog-assets.itch.io/pixel-adventure-1)
- weapons\passives image 来自：[raven-fantasy-icons](https://clockworkraven.itch.io/raven-fantasy-icons)
- chest image 来自：[Assorted RPG Icons ](https://merchant-shade.itch.io/16x16-mixed-rpg-icons)
- explotion 来自：[Pixel Effect RPG Part](https://bdragon1727.itch.io/64x64-pixel-effect-rpg-part-1)