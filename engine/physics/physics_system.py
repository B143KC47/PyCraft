"""
物理系统，负责物理模拟
"""

import pybullet as p
import pybullet_data
import numpy as np
import time

from engine.core.ecs.system import System


class PhysicsSystem(System):
    """物理系统，负责物理模拟"""
    
    def __init__(self):
        """初始化物理系统"""
        super().__init__()
        self.priority = 50  # 物理系统优先级中等，在输入系统之后，渲染系统之前更新
        self.client_id = None  # PyBullet客户端ID
        self.gravity = (0, -9.81, 0)  # 重力
        self.time_step = 1.0 / 60.0  # 物理模拟时间步长
        self.max_sub_steps = 5  # 最大子步数
        self.solver_iterations = 10  # 求解器迭代次数
        self.collision_objects = {}  # 碰撞对象字典，键为实体ID，值为碰撞对象ID
        self.constraints = {}  # 约束字典，键为约束名称，值为约束ID
        self.debug_mode = False  # 调试模式
        self.initialized = False  # 是否已初始化
    
    def initialize(self, debug_mode=False):
        """
        初始化物理系统
        
        Args:
            debug_mode (bool): 是否启用调试模式
        """
        # 如果已初始化，先关闭
        if self.initialized:
            self.shutdown()
        
        # 设置调试模式
        self.debug_mode = debug_mode
        
        # 初始化PyBullet
        if debug_mode:
            self.client_id = p.connect(p.GUI)  # 使用GUI模式
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)  # 禁用内置GUI
        else:
            self.client_id = p.connect(p.DIRECT)  # 使用直接模式
        
        # 设置重力
        p.setGravity(*self.gravity, physicsClientId=self.client_id)
        
        # 设置求解器参数
        p.setPhysicsEngineParameter(
            fixedTimeStep=self.time_step,
            numSolverIterations=self.solver_iterations,
            physicsClientId=self.client_id
        )
        
        # 加载PyBullet数据路径
        p.setAdditionalSearchPath(pybullet_data.getDataPath(), physicsClientId=self.client_id)
        
        self.initialized = True
    
    def set_gravity(self, gravity):
        """
        设置重力
        
        Args:
            gravity (tuple): 重力向量，(x, y, z)
        """
        self.gravity = gravity
        
        if self.initialized:
            p.setGravity(*gravity, physicsClientId=self.client_id)
    
    def set_time_step(self, time_step):
        """
        设置时间步长
        
        Args:
            time_step (float): 时间步长，单位为秒
        """
        self.time_step = time_step
        
        if self.initialized:
            p.setPhysicsEngineParameter(
                fixedTimeStep=time_step,
                physicsClientId=self.client_id
            )
    
    def set_solver_iterations(self, iterations):
        """
        设置求解器迭代次数
        
        Args:
            iterations (int): 迭代次数
        """
        self.solver_iterations = iterations
        
        if self.initialized:
            p.setPhysicsEngineParameter(
                numSolverIterations=iterations,
                physicsClientId=self.client_id
            )
    
    def create_collision_box(self, entity_id, half_extents, position=(0, 0, 0), rotation=(0, 0, 0), mass=0.0, restitution=0.0, friction=0.5):
        """
        创建碰撞箱
        
        Args:
            entity_id (str): 实体ID
            half_extents (tuple): 半尺寸，(x, y, z)
            position (tuple): 位置，(x, y, z)
            rotation (tuple): 旋转，(x, y, z)，欧拉角，单位为度
            mass (float): 质量，0表示静态物体
            restitution (float): 弹性系数，0-1
            friction (float): 摩擦系数，0-1
            
        Returns:
            int: 碰撞对象ID
        """
        if not self.initialized:
            return None
        
        # 创建碰撞形状
        collision_shape = p.createCollisionShape(
            p.GEOM_BOX,
            halfExtents=half_extents,
            physicsClientId=self.client_id
        )
        
        # 创建刚体
        rotation_quaternion = p.getQuaternionFromEuler([
            np.radians(rotation[0]),
            np.radians(rotation[1]),
            np.radians(rotation[2])
        ])
        
        body_id = p.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=collision_shape,
            basePosition=position,
            baseOrientation=rotation_quaternion,
            physicsClientId=self.client_id
        )
        
        # 设置物理属性
        p.changeDynamics(
            body_id,
            -1,
            restitution=restitution,
            lateralFriction=friction,
            physicsClientId=self.client_id
        )
        
        # 存储碰撞对象
        self.collision_objects[entity_id] = body_id
        
        return body_id
    
    def create_collision_sphere(self, entity_id, radius, position=(0, 0, 0), mass=0.0, restitution=0.0, friction=0.5):
        """
        创建碰撞球
        
        Args:
            entity_id (str): 实体ID
            radius (float): 半径
            position (tuple): 位置，(x, y, z)
            mass (float): 质量，0表示静态物体
            restitution (float): 弹性系数，0-1
            friction (float): 摩擦系数，0-1
            
        Returns:
            int: 碰撞对象ID
        """
        if not self.initialized:
            return None
        
        # 创建碰撞形状
        collision_shape = p.createCollisionShape(
            p.GEOM_SPHERE,
            radius=radius,
            physicsClientId=self.client_id
        )
        
        # 创建刚体
        body_id = p.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=collision_shape,
            basePosition=position,
            physicsClientId=self.client_id
        )
        
        # 设置物理属性
        p.changeDynamics(
            body_id,
            -1,
            restitution=restitution,
            lateralFriction=friction,
            physicsClientId=self.client_id
        )
        
        # 存储碰撞对象
        self.collision_objects[entity_id] = body_id
        
        return body_id
    
    def create_collision_capsule(self, entity_id, radius, height, position=(0, 0, 0), rotation=(0, 0, 0), mass=0.0, restitution=0.0, friction=0.5):
        """
        创建碰撞胶囊体
        
        Args:
            entity_id (str): 实体ID
            radius (float): 半径
            height (float): 高度
            position (tuple): 位置，(x, y, z)
            rotation (tuple): 旋转，(x, y, z)，欧拉角，单位为度
            mass (float): 质量，0表示静态物体
            restitution (float): 弹性系数，0-1
            friction (float): 摩擦系数，0-1
            
        Returns:
            int: 碰撞对象ID
        """
        if not self.initialized:
            return None
        
        # 创建碰撞形状
        collision_shape = p.createCollisionShape(
            p.GEOM_CAPSULE,
            radius=radius,
            height=height,
            physicsClientId=self.client_id
        )
        
        # 创建刚体
        rotation_quaternion = p.getQuaternionFromEuler([
            np.radians(rotation[0]),
            np.radians(rotation[1]),
            np.radians(rotation[2])
        ])
        
        body_id = p.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=collision_shape,
            basePosition=position,
            baseOrientation=rotation_quaternion,
            physicsClientId=self.client_id
        )
        
        # 设置物理属性
        p.changeDynamics(
            body_id,
            -1,
            restitution=restitution,
            lateralFriction=friction,
            physicsClientId=self.client_id
        )
        
        # 存储碰撞对象
        self.collision_objects[entity_id] = body_id
        
        return body_id
    
    def create_collision_mesh(self, entity_id, mesh_path, position=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1), mass=0.0, restitution=0.0, friction=0.5):
        """
        创建碰撞网格
        
        Args:
            entity_id (str): 实体ID
            mesh_path (str): 网格文件路径
            position (tuple): 位置，(x, y, z)
            rotation (tuple): 旋转，(x, y, z)，欧拉角，单位为度
            scale (tuple): 缩放，(x, y, z)
            mass (float): 质量，0表示静态物体
            restitution (float): 弹性系数，0-1
            friction (float): 摩擦系数，0-1
            
        Returns:
            int: 碰撞对象ID
        """
        if not self.initialized:
            return None
        
        # 创建碰撞形状
        collision_shape = p.createCollisionShape(
            p.GEOM_MESH,
            fileName=mesh_path,
            meshScale=scale,
            physicsClientId=self.client_id
        )
        
        # 创建刚体
        rotation_quaternion = p.getQuaternionFromEuler([
            np.radians(rotation[0]),
            np.radians(rotation[1]),
            np.radians(rotation[2])
        ])
        
        body_id = p.createMultiBody(
            baseMass=mass,
            baseCollisionShapeIndex=collision_shape,
            basePosition=position,
            baseOrientation=rotation_quaternion,
            physicsClientId=self.client_id
        )
        
        # 设置物理属性
        p.changeDynamics(
            body_id,
            -1,
            restitution=restitution,
            lateralFriction=friction,
            physicsClientId=self.client_id
        )
        
        # 存储碰撞对象
        self.collision_objects[entity_id] = body_id
        
        return body_id
    
    def create_constraint(self, name, body_a, body_b, link_a=-1, link_b=-1, joint_type=p.JOINT_FIXED, joint_axis=(0, 0, 1), parent_frame_position=(0, 0, 0), child_frame_position=(0, 0, 0), parent_frame_orientation=(0, 0, 0), child_frame_orientation=(0, 0, 0)):
        """
        创建约束
        
        Args:
            name (str): 约束名称
            body_a (int): 第一个刚体ID
            body_b (int): 第二个刚体ID
            link_a (int): 第一个刚体的链接索引，-1表示基础链接
            link_b (int): 第二个刚体的链接索引，-1表示基础链接
            joint_type (int): 关节类型，如p.JOINT_FIXED, p.JOINT_POINT2POINT, p.JOINT_HINGE等
            joint_axis (tuple): 关节轴，(x, y, z)
            parent_frame_position (tuple): 父框架位置，(x, y, z)
            child_frame_position (tuple): 子框架位置，(x, y, z)
            parent_frame_orientation (tuple): 父框架旋转，(x, y, z)，欧拉角，单位为度
            child_frame_orientation (tuple): 子框架旋转，(x, y, z)，欧拉角，单位为度
            
        Returns:
            int: 约束ID
        """
        if not self.initialized:
            return None
        
        # 转换欧拉角为四元数
        parent_frame_quaternion = p.getQuaternionFromEuler([
            np.radians(parent_frame_orientation[0]),
            np.radians(parent_frame_orientation[1]),
            np.radians(parent_frame_orientation[2])
        ])
        
        child_frame_quaternion = p.getQuaternionFromEuler([
            np.radians(child_frame_orientation[0]),
            np.radians(child_frame_orientation[1]),
            np.radians(child_frame_orientation[2])
        ])
        
        # 创建约束
        constraint_id = p.createConstraint(
            parentBodyUniqueId=body_a,
            parentLinkIndex=link_a,
            childBodyUniqueId=body_b,
            childLinkIndex=link_b,
            jointType=joint_type,
            jointAxis=joint_axis,
            parentFramePosition=parent_frame_position,
            childFramePosition=child_frame_position,
            parentFrameOrientation=parent_frame_quaternion,
            childFrameOrientation=child_frame_quaternion,
            physicsClientId=self.client_id
        )
        
        # 存储约束
        self.constraints[name] = constraint_id
        
        return constraint_id
    
    def remove_collision_object(self, entity_id):
        """
        移除碰撞对象
        
        Args:
            entity_id (str): 实体ID
            
        Returns:
            bool: 是否成功移除
        """
        if not self.initialized:
            return False
        
        if entity_id in self.collision_objects:
            body_id = self.collision_objects[entity_id]
            p.removeBody(body_id, physicsClientId=self.client_id)
            del self.collision_objects[entity_id]
            return True
        
        return False
    
    def remove_constraint(self, name):
        """
        移除约束
        
        Args:
            name (str): 约束名称
            
        Returns:
            bool: 是否成功移除
        """
        if not self.initialized:
            return False
        
        if name in self.constraints:
            constraint_id = self.constraints[name]
            p.removeConstraint(constraint_id, physicsClientId=self.client_id)
            del self.constraints[name]
            return True
        
        return False
    
    def get_collision_object(self, entity_id):
        """
        获取碰撞对象
        
        Args:
            entity_id (str): 实体ID
            
        Returns:
            int: 碰撞对象ID，如果不存在则返回None
        """
        return self.collision_objects.get(entity_id)
    
    def get_constraint(self, name):
        """
        获取约束
        
        Args:
            name (str): 约束名称
            
        Returns:
            int: 约束ID，如果不存在则返回None
        """
        return self.constraints.get(name)
    
    def get_position_and_orientation(self, entity_id):
        """
        获取位置和方向
        
        Args:
            entity_id (str): 实体ID
            
        Returns:
            tuple: ((x, y, z), (qx, qy, qz, qw))，如果不存在则返回None
        """
        if not self.initialized:
            return None
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return None
        
        return p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)
    
    def get_linear_velocity(self, entity_id):
        """
        获取线速度
        
        Args:
            entity_id (str): 实体ID
            
        Returns:
            tuple: (vx, vy, vz)，如果不存在则返回None
        """
        if not self.initialized:
            return None
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return None
        
        return p.getBaseVelocity(body_id, physicsClientId=self.client_id)[0]
    
    def get_angular_velocity(self, entity_id):
        """
        获取角速度
        
        Args:
            entity_id (str): 实体ID
            
        Returns:
            tuple: (wx, wy, wz)，如果不存在则返回None
        """
        if not self.initialized:
            return None
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return None
        
        return p.getBaseVelocity(body_id, physicsClientId=self.client_id)[1]
    
    def set_position(self, entity_id, position):
        """
        设置位置
        
        Args:
            entity_id (str): 实体ID
            position (tuple): 位置，(x, y, z)
            
        Returns:
            bool: 是否成功设置
        """
        if not self.initialized:
            return False
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return False
        
        pos, orn = p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)
        p.resetBasePositionAndOrientation(body_id, position, orn, physicsClientId=self.client_id)
        
        return True
    
    def set_orientation(self, entity_id, rotation):
        """
        设置方向
        
        Args:
            entity_id (str): 实体ID
            rotation (tuple): 旋转，(x, y, z)，欧拉角，单位为度
            
        Returns:
            bool: 是否成功设置
        """
        if not self.initialized:
            return False
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return False
        
        pos, _ = p.getBasePositionAndOrientation(body_id, physicsClientId=self.client_id)
        
        rotation_quaternion = p.getQuaternionFromEuler([
            np.radians(rotation[0]),
            np.radians(rotation[1]),
            np.radians(rotation[2])
        ])
        
        p.resetBasePositionAndOrientation(body_id, pos, rotation_quaternion, physicsClientId=self.client_id)
        
        return True
    
    def set_linear_velocity(self, entity_id, velocity):
        """
        设置线速度
        
        Args:
            entity_id (str): 实体ID
            velocity (tuple): 速度，(vx, vy, vz)
            
        Returns:
            bool: 是否成功设置
        """
        if not self.initialized:
            return False
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return False
        
        p.resetBaseVelocity(body_id, linearVelocity=velocity, physicsClientId=self.client_id)
        
        return True
    
    def set_angular_velocity(self, entity_id, velocity):
        """
        设置角速度
        
        Args:
            entity_id (str): 实体ID
            velocity (tuple): 角速度，(wx, wy, wz)
            
        Returns:
            bool: 是否成功设置
        """
        if not self.initialized:
            return False
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return False
        
        p.resetBaseVelocity(body_id, angularVelocity=velocity, physicsClientId=self.client_id)
        
        return True
    
    def apply_force(self, entity_id, force, position=None):
        """
        施加力
        
        Args:
            entity_id (str): 实体ID
            force (tuple): 力，(fx, fy, fz)
            position (tuple): 施加点，(x, y, z)，如果为None则施加到质心
            
        Returns:
            bool: 是否成功施加
        """
        if not self.initialized:
            return False
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return False
        
        if position is None:
            p.applyExternalForce(body_id, -1, force, [0, 0, 0], p.WORLD_FRAME, physicsClientId=self.client_id)
        else:
            p.applyExternalForce(body_id, -1, force, position, p.WORLD_FRAME, physicsClientId=self.client_id)
        
        return True
    
    def apply_torque(self, entity_id, torque):
        """
        施加扭矩
        
        Args:
            entity_id (str): 实体ID
            torque (tuple): 扭矩，(tx, ty, tz)
            
        Returns:
            bool: 是否成功施加
        """
        if not self.initialized:
            return False
        
        body_id = self.get_collision_object(entity_id)
        
        if body_id is None:
            return False
        
        p.applyExternalTorque(body_id, -1, torque, p.WORLD_FRAME, physicsClientId=self.client_id)
        
        return True
    
    def ray_test(self, from_position, to_position):
        """
        射线测试
        
        Args:
            from_position (tuple): 起点，(x, y, z)
            to_position (tuple): 终点，(x, y, z)
            
        Returns:
            tuple: (hit_entity_id, hit_position, hit_normal)，如果没有碰撞则返回(None, None, None)
        """
        if not self.initialized:
            return None, None, None
        
        results = p.rayTest(from_position, to_position, physicsClientId=self.client_id)
        
        if results[0][0] == -1:
            return None, None, None
        
        hit_body_id = results[0][0]
        hit_position = results[0][3]
        hit_normal = results[0][4]
        
        # 查找实体ID
        hit_entity_id = None
        for entity_id, body_id in self.collision_objects.items():
            if body_id == hit_body_id:
                hit_entity_id = entity_id
                break
        
        return hit_entity_id, hit_position, hit_normal
    
    def update(self, delta_time):
        """
        更新物理系统
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        if not self.initialized:
            return
        
        # 步进模拟
        p.stepSimulation(physicsClientId=self.client_id)
    
    def shutdown(self):
        """关闭物理系统"""
        if self.initialized:
            # 断开连接
            p.disconnect(physicsClientId=self.client_id)
            
            # 清空碰撞对象和约束
            self.collision_objects.clear()
            self.constraints.clear()
            
            self.initialized = False 