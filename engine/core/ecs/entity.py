"""
实体类，代表游戏中的对象
"""

import uuid


class Entity:
    """实体类，代表游戏中的对象"""
    
    def __init__(self, name="Entity"):
        """
        初始化实体
        
        Args:
            name (str): 实体名称
        """
        self.id = str(uuid.uuid4())  # 唯一ID
        self.name = name  # 实体名称
        self.enabled = True  # 是否启用
        self.components = {}  # 组件字典，键为组件类型，值为组件实例
        self.parent = None  # 父实体
        self.children = []  # 子实体列表
        self.scene = None  # 所属场景
        self.tags = set()  # 标签集合
        self.layer = 0  # 层级
    
    def add_component(self, component):
        """
        添加组件
        
        Args:
            component: 组件实例
            
        Returns:
            component: 添加的组件
        """
        component_type = component.__class__
        self.components[component_type] = component
        component.entity = self
        
        # 调用组件的添加方法
        if hasattr(component, "on_add"):
            component.on_add()
        
        return component
    
    def remove_component(self, component_type):
        """
        移除组件
        
        Args:
            component_type: 组件类型
            
        Returns:
            bool: 是否成功移除
        """
        if component_type in self.components:
            component = self.components[component_type]
            
            # 调用组件的移除方法
            if hasattr(component, "on_remove"):
                component.on_remove()
            
            component.entity = None
            del self.components[component_type]
            return True
        
        return False
    
    def get_component(self, component_type):
        """
        获取组件
        
        Args:
            component_type: 组件类型
            
        Returns:
            component: 组件实例，如果不存在则返回None
        """
        return self.components.get(component_type)
    
    def has_component(self, component_type):
        """
        检查是否有组件
        
        Args:
            component_type: 组件类型
            
        Returns:
            bool: 是否有组件
        """
        return component_type in self.components
    
    def get_components(self):
        """
        获取所有组件
        
        Returns:
            list: 组件列表
        """
        return list(self.components.values())
    
    def add_child(self, entity):
        """
        添加子实体
        
        Args:
            entity: 子实体
            
        Returns:
            entity: 子实体
        """
        if entity.parent:
            entity.parent.remove_child(entity)
        
        entity.parent = self
        self.children.append(entity)
        
        return entity
    
    def remove_child(self, entity):
        """
        移除子实体
        
        Args:
            entity: 子实体
            
        Returns:
            bool: 是否成功移除
        """
        if entity in self.children:
            entity.parent = None
            self.children.remove(entity)
            return True
        
        return False
    
    def get_children(self):
        """
        获取所有子实体
        
        Returns:
            list: 子实体列表
        """
        return self.children.copy()
    
    def get_child_by_name(self, name):
        """
        通过名称获取子实体
        
        Args:
            name (str): 子实体名称
            
        Returns:
            entity: 子实体，如果不存在则返回None
        """
        for child in self.children:
            if child.name == name:
                return child
        
        return None
    
    def get_child_by_id(self, entity_id):
        """
        通过ID获取子实体
        
        Args:
            entity_id (str): 子实体ID
            
        Returns:
            entity: 子实体，如果不存在则返回None
        """
        for child in self.children:
            if child.id == entity_id:
                return child
        
        return None
    
    def add_tag(self, tag):
        """
        添加标签
        
        Args:
            tag (str): 标签
        """
        self.tags.add(tag)
    
    def remove_tag(self, tag):
        """
        移除标签
        
        Args:
            tag (str): 标签
            
        Returns:
            bool: 是否成功移除
        """
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        
        return False
    
    def has_tag(self, tag):
        """
        检查是否有标签
        
        Args:
            tag (str): 标签
            
        Returns:
            bool: 是否有标签
        """
        return tag in self.tags
    
    def set_layer(self, layer):
        """
        设置层级
        
        Args:
            layer (int): 层级
        """
        self.layer = layer
    
    def get_layer(self):
        """
        获取层级
        
        Returns:
            int: 层级
        """
        return self.layer
    
    def enable(self):
        """启用实体"""
        self.enabled = True
        
        # 启用所有组件
        for component in self.components.values():
            if hasattr(component, "enable"):
                component.enable()
    
    def disable(self):
        """禁用实体"""
        self.enabled = False
        
        # 禁用所有组件
        for component in self.components.values():
            if hasattr(component, "disable"):
                component.disable()
    
    def is_enabled(self):
        """
        检查实体是否启用
        
        Returns:
            bool: 是否启用
        """
        return self.enabled
    
    def destroy(self):
        """销毁实体"""
        # 销毁所有子实体
        for child in self.children.copy():
            child.destroy()
        
        # 移除所有组件
        for component_type in list(self.components.keys()):
            self.remove_component(component_type)
        
        # 从父实体中移除
        if self.parent:
            self.parent.remove_child(self)
        
        # 从场景中移除
        if self.scene:
            self.scene.remove_entity(self)
    
    def __str__(self):
        """字符串表示"""
        return f"Entity(id={self.id}, name={self.name}, components={len(self.components)})" 