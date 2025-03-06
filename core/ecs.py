import numpy as np

class Entity:
    """实体类，游戏中的基本对象，只有ID和组件集合"""
    next_id = 0
    
    def __init__(self):
        self.id = Entity.next_id
        Entity.next_id += 1
        self.components = {}
        self.tags = set()  # 添加标签功能，方便分类
    
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
        
    def has_component(self, component_type):
        """检查是否有特定组件"""
        return component_type in self.components
        
    def add_tag(self, tag):
        """添加标签"""
        self.tags.add(tag)
        return self
        
    def remove_tag(self, tag):
        """移除标签"""
        if tag in self.tags:
            self.tags.remove(tag)
        return self
        
    def has_tag(self, tag):
        """检查是否有特定标签"""
        return tag in self.tags

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

# 示例组件
class Position(Component):
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x, self.y, self.z = x, y, z
        # 使用NumPy提高性能
        self.pos_array = np.array([x, y, z], dtype=np.float32)
        
    @property
    def position(self):
        """获取位置数组"""
        self.pos_array[0] = self.x
        self.pos_array[1] = self.y
        self.pos_array[2] = self.z
        return self.pos_array
        
    @position.setter
    def position(self, pos):
        """设置位置"""
        self.x, self.y, self.z = pos
        self.pos_array[:] = pos

class Graphic(Component):
    def __init__(self, model_path):
        self.model_path = model_path
        self.mesh = None  # 用于存储加载的网格数据
        self.texture = None  # 用于存储纹理
        
    def load_mesh(self):
        """加载模型网格"""
        # 实际实现中，这里会加载3D模型
        pass

# 添加更多有用的组件
class Velocity(Component):
    def __init__(self, vx=0.0, vy=0.0, vz=0.0):
        self.vx, self.vy, self.vz = vx, vy, vz
        self.vel_array = np.array([vx, vy, vz], dtype=np.float32)
        
class Physics(Component):
    def __init__(self, mass=1.0, is_dynamic=True):
        self.mass = mass
        self.is_dynamic = is_dynamic  # 是否受物理影响
        self.body_id = -1  # 在物理引擎中的ID
        
class Camera(Component):
    def __init__(self, fov=45.0, near=0.1, far=1000.0):
        self.fov = fov  # 视场角
        self.near = near  # 近平面
        self.far = far  # 远平面
        self.position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
