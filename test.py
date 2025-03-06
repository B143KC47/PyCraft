from engine.core.application import Application
from engine.core.ecs.entity import Entity
from engine.core.ecs.components.transform import Transform
from engine.core.ecs.components.mesh_renderer import MeshRenderer
from engine.core.ecs.components.camera import Camera

# 创建应用程序
app = Application(width=1280, height=720, title="My Game")

# 创建场景
scene = app.scene_manager.create_scene("My Scene")

# 创建相机
camera = scene.create_entity("Main Camera")
camera.add_component(Transform(position=(0, 0, 5)))
camera.add_component(Camera())

# 创建立方体
cube = scene.create_entity("Cube")
cube.add_component(Transform(position=(0, 0, 0)))
cube.add_component(MeshRenderer(mesh="cube", material="default"))

# 运行游戏
app.run()