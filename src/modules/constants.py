import math

# 定义8个方向的角度（弧度）
DIRECTION_ANGLES = {
    'right': 0,
    'right_down': math.pi / 4,
    'down': math.pi / 2,
    'left_down': 3 * math.pi / 4,
    'left': math.pi,
    'left_up': -3 * math.pi / 4,
    'up': -math.pi / 2,
    'right_up': -math.pi / 4
} 