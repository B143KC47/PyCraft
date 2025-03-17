# PyCraft 游戏引擎

PyCraft 是一个基于 Python 的游戏引擎，旨在为初学者提供一个易于使用的游戏开发工具，类似于 Unreal Engine 的编辑器。

## 🚧 半成品警告 🚧

PyCraft 仍处于积极开发阶段，许多功能尚未完成。请注意，使用过程中可能会遇到 bug 和不稳定性。欢迎您参与测试和反馈，帮助我们改进项目！

## 特性

- **基于 ECS 架构**：使用实体组件系统架构，提供高度模块化和可扩展性
- **3D 渲染**：使用 PyOpenGL 进行高性能 3D 图形渲染
- **物理模拟**：集成 PyBullet 物理引擎，提供真实的物理交互
- **场景管理**：强大的场景管理系统，支持场景的加载、保存和切换
- **编辑器**：类似 Unreal Engine 的编辑器界面，使用 PyQt 构建
- **视觉脚本**：直观的视觉脚本系统，无需编写代码即可创建游戏逻辑
- **跨平台**：支持 Windows、Linux 和 macOS

## 系统要求

- Python 3.7+
- 支持 OpenGL 3.3+ 的显卡

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/yourusername/pycraft.git
cd pycraft
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 快速开始

### 启动编辑器

**Windows 用户**：
- 双击 `启动编辑器.bat` 文件
- 或在命令行中运行：
  ```bash
  python start_editor.py
  ```

**Linux/Mac 用户**：
- 在终端中运行：
  ```bash
  chmod +x start_editor.sh
  ./start_editor.sh
  ```

**命令行选项**：
- 启动调试模式：`python start_editor.py --debug`
- 指定分辨率：`python start_editor.py --resolution=1920x1080`
- 打开项目：`python main.py --editor --project=/path/to/project`
- 加载场景：`python main.py --editor --scene=/path/to/scene.scene`

### 运行游戏引擎

```bash
python main.py
```

### 直接运行编辑器（旧方法）

```bash
python editor_main.py
```

## 架构概述

PyCraft 游戏引擎采用 Entity-Component-System (ECS) 架构，主要由以下部分组成：

### 核心模块 (engine/core)

- **应用程序 (application.py)**：游戏引擎的核心，管理游戏循环和系统
- **ECS 架构 (ecs/)**：
  - **实体 (entity.py)**：游戏对象的容器
  - **组件 (component.py)**：实体的数据容器
  - **系统 (system.py)**：处理特定功能的逻辑
- **场景管理 (scene/)**：
  - **场景 (scene.py)**：管理游戏场景中的实体
  - **场景管理器 (scene_manager.py)**：管理多个场景

### 渲染模块 (engine/rendering)

- **渲染系统 (render_system.py)**：使用 PyOpenGL 渲染场景
- **材质系统 (materials/)**：管理材质和着色器
- **模型加载 (models/)**：加载和处理 3D 模型

### 物理模块 (engine/physics)

- **物理系统 (physics_system.py)**：使用 PyBullet 进行物理模拟
- **碰撞器 (collider.py)**：定义碰撞形状
- **刚体 (rigidbody.py)**：物理对象的属性

### 输入模块 (engine/input)

- **输入系统 (input_system.py)**：处理键盘、鼠标和游戏手柄输入

### UI 模块 (engine/ui)

- **UI 系统 (ui_system.py)**：管理游戏内 UI
- **UI 组件 (components/)**：按钮、文本等 UI 元素

### 脚本模块 (engine/scripting)

- **脚本系统 (script_system.py)**：管理游戏脚本

### 编辑器模块 (editor/)

- **编辑器应用 (editor_app.py)**：编辑器的入口点
- **编辑器 UI (ui/)**：编辑器界面
  - **主窗口 (main_window.py)**：编辑器主窗口
  - **面板 (panels/)**：场景、属性、层级等面板
- **编辑器工具 (tools/)**：变换工具、视觉脚本等

## 示例

### 创建一个简单的游戏

```python
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
```

## 贡献

欢迎贡献代码、报告问题或提出建议。请先查看 [贡献指南](CONTRIBUTING.md)。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。