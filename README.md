# 游戏名字还没想好

这是一个使用 Cursor + Pygame 开发的2D像素风肉鸽游戏。边玩边学。
（60% cursor聊天与生成 + 10% debug + 10% codereview + 10% 找素材 + 4% 开开脑洞 + 4% 等待时玩手机 + 1% 写一些没有意义的README）

## 游戏特点

- 自动攻击系统
- 升级系统
- 敌人生成系统
- 难度随时间递增

## 安装说明

1. 确保已安装 Python 3.8 或更高版本
2. 创建并激活虚拟环境（推荐）：
```bash
conda create -n vampire-survivor python=3.8
conda activate vampire-survivor
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 运行游戏

```bash
cd src
python main.py
```

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
- [x] 实现物品掉落系统
  - [x] 金币掉落
  - [x] 经验球掉落
  - [x] 医疗包掉落
  - [ ] 宝箱掉落
- [ ] 主菜单
  - [x] 支持保存游戏和读取游戏
  - [ ] 支持设置
  - [ ] 支持全局的技能属性