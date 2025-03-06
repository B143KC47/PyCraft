# PyCraft 游戏引擎

PyCraft是一个基于Python的3D游戏引擎，使用ECS（实体-组件-系统）架构设计，旨在提供高性能和易用性。

## 特性

- 基于ECS架构，提供良好的模块化和性能
- 使用PyOpenGL进行3D渲染
- 使用PyBullet进行物理模拟
- 使用Pygame处理输入和窗口管理
- 场景管理系统
- 资源管理系统
- UI系统

## 安装

### 依赖项

- Python 3.7+
- PyOpenGL
- PyOpenGL_accelerate
- Pygame
- PyBullet
- NumPy

### 安装步骤

1. 克隆仓库：
   ```
   git clone https://github.com/yourusername/PyCraft.git
   cd PyCraft
   ```

2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

## 使用方法

### 运行示例

```
python main.py
```

### 创建自己的游戏

1. 创建一个新的场景类，继承自`Scene`类：

```python
from core.scene_manager import Scene
from core.components import ComponentType, TransformComponent, RenderComponent

class MyGameScene(Scene):
    def __init__(self, entity_manager, resource_manager, ui_system, game):
        super().__init__("MyGameScene", entity_manager, resource_manager)
        self.ui_system = ui_system
        self.game = game
    
    def load(self):
        # 创建实体
        my_entity = self.create_entity("MyEntity")
        transform = TransformComponent(position=(0, 0, 0))
        render = RenderComponent(visible=True)
        
        my_entity.add_component(ComponentType.TRANSFORM, transform)
        my_entity.add_component(ComponentType.RENDER, render)
        
        # 创建UI
        self.ui_system.create_label("My Game", (10, 10), font_size=24)
```

2. 在游戏初始化时添加场景：

```python
def init_scenes(self):
    # 添加其他场景...
    
    # 添加自定义场景
    my_scene = MyGameScene(self.entity_manager, self.resource_manager, self.ui_system, self)
    self.scene_manager.add_scene(my_scene)
```

3. 切换到自定义场景：

```python
self.scene_manager.change_scene("MyGameScene")
```

## 架构

### 核心模块

- `core/game.py`: 游戏主类，管理游戏状态和主循环
- `core/entity_manager.py`: 实体管理器，管理所有实体
- `core/components.py`: 组件定义，包含所有组件类型
- `core/resource_manager.py`: 资源管理器，负责加载和管理游戏资源
- `core/scene_manager.py`: 场景管理器，负责管理游戏场景

### 系统模块

- `systems/render_system.py`: 渲染系统，负责渲染所有可见实体
- `systems/physics_system.py`: 物理系统，负责处理物理模拟
- `systems/input_system.py`: 输入系统，负责处理用户输入
- `systems/ui_system.py`: UI系统，负责处理UI元素

## 贡献

欢迎贡献代码、报告问题或提出建议。请遵循以下步骤：

1. Fork仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。

## 致谢

- [PyOpenGL](http://pyopengl.sourceforge.net/)
- [Pygame](https://www.pygame.org/)
- [PyBullet](https://pybullet.org/)
- [NumPy](https://numpy.org/)