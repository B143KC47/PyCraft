import pybullet as p
import pybullet_data
from core.ecs import System
from core.game import Position

class PhysicsSystem(System):
    """物理系统，负责处理物理模拟"""
    def __init__(self, game):
        super().__init__(game)
        self.physicsClient = p.connect(p.GUI)  # 或 p.DIRECT
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, -10)
        
        # 加载地面
        p.loadURDF("plane.urdf")
        
        # 创建一个简单的方块
        self.boxId = p.loadURDF("cube.urdf", [0, 0, 1])

    def update(self, dt):
        """更新物理世界"""
        p.stepSimulation()
        
        # 更新实体的位置
        for entity in self.game.entities.values():
            position = entity.get_component("Position")
            if position:
                # 获取物体的位置和姿态
                pos, _ = p.getBasePositionAndOrientation(self.boxId)
                position.x, position.y, position.z = pos
