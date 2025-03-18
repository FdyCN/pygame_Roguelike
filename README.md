# 吸血鬼幸存者克隆版

这是一个使用 Pygame 开发的《吸血鬼幸存者》游戏克隆版。

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

## 待实现功能

- [ ] 添加更多武器类型
- [ ] 添加经验值系统
- [ ] 添加升级选择界面
- [ ] 添加音效和背景音乐
- [ ] 添加更多敌人类型
- [ ] 实现物品掉落系统
- [ ] 添加技能树系统 