"""
组件系统基类
定义所有组件的基本接口和生命周期
"""

class Component:
    """组件基类"""
    
    def __init__(self, owner):
        """
        初始化组件
        
        Args:
            owner: 组件所属的实体
        """
        self.owner = owner
        self.enabled = True
        
    def update(self, dt):
        """
        更新组件状态
        
        Args:
            dt: 时间增量（秒）
        """
        pass
        
    def enable(self):
        """启用组件"""
        self.enabled = True
        
    def disable(self):
        """禁用组件"""
        self.enabled = False 