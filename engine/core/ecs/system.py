"""
系统基类，所有系统都应继承自此类
"""


class System:
    """系统基类，所有系统都应继承自此类"""
    
    def __init__(self):
        """初始化系统"""
        self.priority = 0  # 系统优先级，数值越小优先级越高
        self.enabled = True  # 是否启用
    
    def initialize(self):
        """初始化系统，在系统被添加到引擎时调用"""
        pass
    
    def update(self, delta_time):
        """
        更新系统
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        pass
    
    def render(self):
        """渲染系统，每帧调用"""
        pass
    
    def shutdown(self):
        """关闭系统，在系统被移除或引擎关闭时调用"""
        pass
    
    def enable(self):
        """启用系统"""
        self.enabled = True
    
    def disable(self):
        """禁用系统"""
        self.enabled = False
    
    def is_enabled(self):
        """
        检查系统是否启用
        
        Returns:
            bool: 是否启用
        """
        return self.enabled
    
    def __str__(self):
        """字符串表示"""
        return f"{self.__class__.__name__}(enabled={self.enabled}, priority={self.priority})" 