import numpy as np
from collections import defaultdict
from core.ecs import Component

class ComponentManager:
    """组件管理器，用于有效管理实体的组件"""
    def __init__(self):
        self.component_store = defaultdict(dict)  # 类型 -> (实体ID -> 组件)
        
    def add_component(self, entity_id, component):
        """为实体添加组件"""
        component_type = type(component).__name__
        self.component_store[component_type][entity_id] = component
        
    def remove_component(self, entity_id, component_type):
        """从实体移除组件"""
        if component_type in self.component_store and entity_id in self.component_store[component_type]:
            del self.component_store[component_type][entity_id]
            
    def get_component(self, entity_id, component_type):
        """获取实体的特定组件"""
        if component_type in self.component_store and entity_id in self.component_store[component_type]:
            return self.component_store[component_type][entity_id]
        return None
        
    def get_entities_with_components(self, *component_types):
        """获取拥有特定组件类型的所有实体ID"""
        if not component_types:
            return set()
            
        entities = set(self.component_store[component_types[0]].keys())
        for component_type in component_types[1:]:
            entities &= set(self.component_store[component_type].keys())
            
        return entities
