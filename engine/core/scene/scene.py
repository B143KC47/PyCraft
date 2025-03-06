"""
场景类，管理实体和系统
"""

import uuid
import json
import os

from engine.core.ecs.entity import Entity


class Scene:
    """场景类，管理实体和系统"""
    
    def __init__(self, name="Scene"):
        """
        初始化场景
        
        Args:
            name (str): 场景名称
        """
        self.id = str(uuid.uuid4())  # 唯一ID
        self.name = name  # 场景名称
        self.entities = {}  # 实体字典，键为实体ID，值为实体实例
        self.systems = []  # 系统列表
        self.root_entities = []  # 根实体列表
        self.active = False  # 是否激活
        self.path = None  # 场景文件路径
    
    def create_entity(self, name="Entity"):
        """
        创建实体
        
        Args:
            name (str): 实体名称
            
        Returns:
            Entity: 创建的实体
        """
        entity = Entity(name)
        self.add_entity(entity)
        return entity
    
    def add_entity(self, entity):
        """
        添加实体
        
        Args:
            entity: 实体
            
        Returns:
            entity: 添加的实体
        """
        self.entities[entity.id] = entity
        entity.scene = self
        
        # 如果没有父实体，添加到根实体列表
        if entity.parent is None:
            self.root_entities.append(entity)
        
        return entity
    
    def remove_entity(self, entity):
        """
        移除实体
        
        Args:
            entity: 实体
            
        Returns:
            bool: 是否成功移除
        """
        if entity.id in self.entities:
            # 从根实体列表中移除
            if entity in self.root_entities:
                self.root_entities.remove(entity)
            
            # 从实体字典中移除
            del self.entities[entity.id]
            entity.scene = None
            
            return True
        
        return False
    
    def get_entity(self, entity_id):
        """
        获取实体
        
        Args:
            entity_id (str): 实体ID
            
        Returns:
            Entity: 实体，如果不存在则返回None
        """
        return self.entities.get(entity_id)
    
    def get_entities(self):
        """
        获取所有实体
        
        Returns:
            list: 实体列表
        """
        return list(self.entities.values())
    
    def get_entities_with_component(self, component_type):
        """
        获取具有指定组件的实体
        
        Args:
            component_type: 组件类型
            
        Returns:
            list: 实体列表
        """
        return [entity for entity in self.entities.values() if entity.has_component(component_type)]
    
    def get_entities_with_tag(self, tag):
        """
        获取具有指定标签的实体
        
        Args:
            tag (str): 标签
            
        Returns:
            list: 实体列表
        """
        return [entity for entity in self.entities.values() if entity.has_tag(tag)]
    
    def get_entity_by_name(self, name):
        """
        通过名称获取实体
        
        Args:
            name (str): 实体名称
            
        Returns:
            Entity: 实体，如果不存在则返回None
        """
        for entity in self.entities.values():
            if entity.name == name:
                return entity
        
        return None
    
    def add_system(self, system):
        """
        添加系统
        
        Args:
            system: 系统
            
        Returns:
            system: 添加的系统
        """
        self.systems.append(system)
        
        # 按优先级排序
        self.systems.sort(key=lambda s: s.priority)
        
        return system
    
    def remove_system(self, system):
        """
        移除系统
        
        Args:
            system: 系统
            
        Returns:
            bool: 是否成功移除
        """
        if system in self.systems:
            self.systems.remove(system)
            return True
        
        return False
    
    def get_system(self, system_type):
        """
        获取系统
        
        Args:
            system_type: 系统类型
            
        Returns:
            system: 系统，如果不存在则返回None
        """
        for system in self.systems:
            if isinstance(system, system_type):
                return system
        
        return None
    
    def get_systems(self):
        """
        获取所有系统
        
        Returns:
            list: 系统列表
        """
        return self.systems.copy()
    
    def update(self, delta_time):
        """
        更新场景
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        # 更新系统
        for system in self.systems:
            if system.is_enabled():
                system.update(delta_time)
    
    def activate(self):
        """激活场景"""
        self.active = True
    
    def deactivate(self):
        """停用场景"""
        self.active = False
    
    def is_active(self):
        """
        检查场景是否激活
        
        Returns:
            bool: 是否激活
        """
        return self.active
    
    def clear(self):
        """清空场景"""
        # 销毁所有实体
        for entity in list(self.entities.values()):
            entity.destroy()
        
        # 清空实体字典和根实体列表
        self.entities.clear()
        self.root_entities.clear()
    
    def save(self, path=None):
        """
        保存场景
        
        Args:
            path (str): 保存路径，如果为None则使用当前路径
            
        Returns:
            bool: 是否成功保存
        """
        if path:
            self.path = path
        
        if not self.path:
            return False
        
        try:
            # 创建场景数据
            scene_data = {
                "id": self.id,
                "name": self.name,
                "entities": []
            }
            
            # 添加实体数据
            for entity in self.root_entities:
                scene_data["entities"].append(self._serialize_entity(entity))
            
            # 保存到文件
            with open(self.path, "w") as f:
                json.dump(scene_data, f, indent=4)
            
            return True
        
        except Exception as e:
            print(f"保存场景失败: {e}")
            return False
    
    def load(self, path):
        """
        加载场景
        
        Args:
            path (str): 加载路径
            
        Returns:
            bool: 是否成功加载
        """
        if not os.path.exists(path):
            return False
        
        try:
            # 清空当前场景
            self.clear()
            
            # 加载场景数据
            with open(path, "r") as f:
                scene_data = json.load(f)
            
            # 设置场景属性
            self.id = scene_data.get("id", str(uuid.uuid4()))
            self.name = scene_data.get("name", "Scene")
            self.path = path
            
            # 加载实体
            for entity_data in scene_data.get("entities", []):
                self._deserialize_entity(entity_data)
            
            return True
        
        except Exception as e:
            print(f"加载场景失败: {e}")
            return False
    
    def _serialize_entity(self, entity):
        """
        序列化实体
        
        Args:
            entity: 实体
            
        Returns:
            dict: 实体数据
        """
        entity_data = {
            "id": entity.id,
            "name": entity.name,
            "enabled": entity.enabled,
            "tags": list(entity.tags),
            "layer": entity.layer,
            "components": [],
            "children": []
        }
        
        # 添加组件数据
        for component in entity.get_components():
            if hasattr(component, "serialize"):
                component_data = {
                    "type": component.__class__.__name__,
                    "data": component.serialize()
                }
                entity_data["components"].append(component_data)
        
        # 添加子实体数据
        for child in entity.children:
            entity_data["children"].append(self._serialize_entity(child))
        
        return entity_data
    
    def _deserialize_entity(self, entity_data, parent=None):
        """
        反序列化实体
        
        Args:
            entity_data (dict): 实体数据
            parent: 父实体
            
        Returns:
            Entity: 实体
        """
        # 创建实体
        entity = Entity(entity_data.get("name", "Entity"))
        entity.id = entity_data.get("id", entity.id)
        entity.enabled = entity_data.get("enabled", True)
        entity.tags = set(entity_data.get("tags", []))
        entity.layer = entity_data.get("layer", 0)
        
        # 添加到场景
        self.add_entity(entity)
        
        # 设置父实体
        if parent:
            parent.add_child(entity)
        
        # 添加组件
        for component_data in entity_data.get("components", []):
            component_type = component_data.get("type")
            component_class = self._get_component_class(component_type)
            
            if component_class:
                component = component_class()
                entity.add_component(component)
                
                if hasattr(component, "deserialize"):
                    component.deserialize(component_data.get("data", {}))
        
        # 添加子实体
        for child_data in entity_data.get("children", []):
            self._deserialize_entity(child_data, entity)
        
        return entity
    
    def _get_component_class(self, component_type):
        """
        获取组件类
        
        Args:
            component_type (str): 组件类型名称
            
        Returns:
            class: 组件类，如果不存在则返回None
        """
        # 导入组件模块
        try:
            # 尝试从组件模块导入
            module = __import__(f"engine.core.ecs.components.{component_type.lower()}", fromlist=[component_type])
            return getattr(module, component_type)
        except (ImportError, AttributeError):
            try:
                # 尝试从自定义组件模块导入
                module = __import__(f"game.components.{component_type.lower()}", fromlist=[component_type])
                return getattr(module, component_type)
            except (ImportError, AttributeError):
                print(f"找不到组件类: {component_type}")
                return None
    
    def __str__(self):
        """字符串表示"""
        return f"Scene(id={self.id}, name={self.name}, entities={len(self.entities)}, systems={len(self.systems)})" 