class Entity:
    """实体类，游戏中的基本对象，只有ID和组件集合"""
    next_id = 0
    
    def __init__(self):
        self.id = Entity.next_id
        Entity.next_id += 1
        self.components = {}
    
    def add_component(self, component):
        """添加组件到实体"""
        component_type = type(component).__name__
        self.components[component_type] = component
        return self
    
    def remove_component(self, component_type):
        """从实体移除组件"""
        if component_type in self.components:
            del self.components[component_type]
        return self
    
    def get_component(self, component_type):
        """获取指定类型的组件"""
        return self.components.get(component_type)

class Component:
    """组件基类"""
    pass

class System:
    """系统基类"""
    def __init__(self, game):
        self.game = game
    
    def update(self, dt):
        """更新系统，dt为时间差"""
        raise NotImplementedError
