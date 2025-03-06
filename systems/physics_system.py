import pybullet as p
import pybullet_data
import numpy as np
from core.components import ComponentType, TransformComponent, PhysicsComponent

class PhysicsSystem:
    """物理系统，负责处理物理模拟"""
    
    def __init__(self, entity_manager):
        self.entity_manager = entity_manager
        
        # 初始化物理引擎
        self.physicsClient = p.connect(p.DIRECT)  # 使用DIRECT模式提高性能，或GUI模式进行调试
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, -9.81, 0)  # 设置重力
        
        # 加载地面
        try:
            self.ground_id = p.loadURDF("plane.urdf")
            print("成功加载地面URDF")
        except Exception as e:
            print(f"加载地面URDF失败: {e}")
            # 创建一个简单的地面作为备选
            self.create_simple_ground()
        
        # 初始化物理实体
        self.init_physics_entities()
    
    def create_simple_ground(self):
        """创建一个简单的地面"""
        print("创建简单地面...")
        collision_shape_id = p.createCollisionShape(p.GEOM_BOX, halfExtents=[10, 0.1, 10])
        self.ground_id = p.createMultiBody(
            baseMass=0,  # 质量为0表示静态物体
            baseCollisionShapeIndex=collision_shape_id,
            basePosition=[0, -1, 0]
        )
    
    def init_physics_entities(self):
        """初始化物理实体"""
        physics_entities = self.entity_manager.get_entities_with_components(
            ComponentType.PHYSICS, ComponentType.TRANSFORM
        )
        
        for entity in physics_entities:
            physics_comp = entity.get_component(ComponentType.PHYSICS)
            transform_comp = entity.get_component(ComponentType.TRANSFORM)
            
            # 创建刚体
            if entity.has_component(ComponentType.RENDER):
                render_comp = entity.get_component(ComponentType.RENDER)
                # 根据模型决定使用哪种形状
                # 简化示例，使用立方体
                collision_shape_id = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.5, 0.5, 0.5])
            else:
                # 默认使用球体
                collision_shape_id = p.createCollisionShape(p.GEOM_SPHERE, radius=0.5)
            
            try:
                body_id = p.createMultiBody(
                    baseMass=physics_comp.mass if not physics_comp.is_static else 0,
                    baseCollisionShapeIndex=collision_shape_id,
                    basePosition=transform_comp.position
                )
                
                # 保存物理引擎中的ID
                physics_comp.body_id = body_id
                print(f"创建物理实体: {entity.name}, ID: {body_id}")
            except Exception as e:
                print(f"创建物理实体失败: {e}")
                physics_comp.body_id = -1

    def update(self, delta_time):
        """更新物理世界"""
        # 模拟物理步骤
        p.stepSimulation()
        
        # 更新实体的位置
        physics_entities = self.entity_manager.get_entities_with_components(
            ComponentType.PHYSICS, ComponentType.TRANSFORM
        )
        
        for entity in physics_entities:
            physics_comp = entity.get_component(ComponentType.PHYSICS)
            transform_comp = entity.get_component(ComponentType.TRANSFORM)
            
            if not physics_comp.is_static and hasattr(physics_comp, 'body_id') and physics_comp.body_id != -1:
                # 获取物体的位置和姿态
                pos, orn = p.getBasePositionAndOrientation(physics_comp.body_id)
                transform_comp.position = np.array(pos, dtype=np.float32)
                # 可以根据需要更新旋转
    
    def apply_force(self, entity, force_vector):
        """对实体施加力"""
        if entity.has_component(ComponentType.PHYSICS):
            physics_comp = entity.get_component(ComponentType.PHYSICS)
            if not physics_comp.is_static and hasattr(physics_comp, 'body_id') and physics_comp.body_id != -1:
                p.applyExternalForce(
                    physics_comp.body_id,
                    -1,  # -1表示施加到base上，而不是特定的link
                    force_vector,
                    [0, 0, 0],  # 力的作用点相对于对象中心的偏移
                    p.WORLD_FRAME
                )
    
    def cleanup(self):
        """清理物理引擎资源"""
        p.disconnect()
        print("物理系统资源已清理")
