"""
组件基类，所有组件都应继承自此类
"""


class Component:
    """组件基类，所有组件都应继承自此类"""
    
    def __init__(self):
        """初始化组件"""
        self.entity = None  # 所属实体
        self.enabled = True  # 是否启用
    
    def on_add(self):
        """当组件被添加到实体时调用"""
        pass
    
    def on_remove(self):
        """当组件从实体中移除时调用"""
        pass
    
    def on_enable(self):
        """当组件被启用时调用"""
        pass
    
    def on_disable(self):
        """当组件被禁用时调用"""
        pass
    
    def update(self, delta_time):
        """
        更新组件
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        pass
    
    def enable(self):
        """启用组件"""
        if not self.enabled:
            self.enabled = True
            self.on_enable()
    
    def disable(self):
        """禁用组件"""
        if self.enabled:
            self.enabled = False
            self.on_disable()
    
    def is_enabled(self):
        """
        检查组件是否启用
        
        Returns:
            bool: 是否启用
        """
        return self.enabled and (self.entity is None or self.entity.is_enabled())
    
    def __str__(self):
        """字符串表示"""
        return f"{self.__class__.__name__}(entity={self.entity.name if self.entity else None})" 