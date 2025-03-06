class Entity:
    """实体类，代表游戏中的一个对象"""
    
    _next_id = 0
    
    def __init__(self, name="Entity"):
        self.id = Entity._next_id
        Entity._next_id += 1
        self.name = name
        self.components = {}
        self.active = True
    
    def add_component(self, component_type, component):
        """添加组件到实体"""
        self.components[component_type] = component
        return self
    
    def remove_component(self, component_type):
        """从实体中移除组件"""
        if component_type in self.components:
            del self.components[component_type]
    
    def get_component(self, component_type):
        """获取实体的特定组件"""
        return self.components.get(component_type)
    
    def has_component(self, component_type):
        """检查实体是否有特定组件"""
        return component_type in self.components


class EntityManager:
    """实体管理器，管理所有实体"""
    
    def __init__(self):
        self.entities = {}
        self.component_stores = {}
    
    def create_entity(self, name="Entity"):
        """创建一个新实体"""
        entity = Entity(name)
        self.entities[entity.id] = entity
        return entity
    
    def remove_entity(self, entity_id):
        """移除一个实体"""
        if entity_id in self.entities:
            del self.entities[entity_id]
    
    def get_entity(self, entity_id):
        """获取特定ID的实体"""
        return self.entities.get(entity_id)
    
    def get_all_entities(self):
        """获取所有实体"""
        return list(self.entities.values())
    
    def get_entities_with_components(self, *component_types):
        """获取拥有特定组件的所有实体"""
        result = []
        for entity in self.entities.values():
            if all(entity.has_component(ct) for ct in component_types):
                result.append(entity)
        return result 