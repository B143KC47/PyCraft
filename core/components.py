import numpy as np
from enum import Enum, auto

# 组件类型枚举
class ComponentType(Enum):
    TRANSFORM = auto()
    RENDER = auto()
    PHYSICS = auto()
    INPUT = auto()
    CAMERA = auto()
    UI = auto()
    UI_BUTTON = auto()    # 按钮组件
    UI_LABEL = auto()     # 标签组件
    UI_PANEL = auto()     # 面板组件
    UI_SLIDER = auto()    # 滑块组件
    UI_TEXTBOX = auto()   # 文本框组件
    UI_CHECKBOX = auto()  # 复选框组件
    UI_DROPDOWN = auto()  # 下拉菜单组件
    UI_WINDOW = auto()    # 窗口组件

class TransformComponent:
    """变换组件，存储实体的位置、旋转和缩放"""
    
    def __init__(self, position=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
        self.position = np.array(position, dtype=np.float32)
        self.rotation = np.array(rotation, dtype=np.float32)
        self.scale = np.array(scale, dtype=np.float32)
        self.matrix = np.identity(4, dtype=np.float32)
        self.update_matrix()
    
    def update_matrix(self):
        """更新变换矩阵"""
        # 简化版本，实际应用中需要完整的矩阵计算
        # 这里只是一个占位符
        pass
    
    def translate(self, x, y, z):
        """移动实体"""
        self.position += np.array([x, y, z], dtype=np.float32)
        self.update_matrix()
    
    def rotate(self, x, y, z):
        """旋转实体"""
        self.rotation += np.array([x, y, z], dtype=np.float32)
        self.update_matrix()
    
    def set_scale(self, x, y, z):
        """设置实体缩放"""
        self.scale = np.array([x, y, z], dtype=np.float32)
        self.update_matrix()

class RenderComponent:
    """渲染组件，存储实体的渲染信息"""
    
    def __init__(self, mesh=None, material=None, visible=True):
        self.mesh = mesh  # 网格数据
        self.material = material  # 材质数据
        self.visible = visible  # 是否可见
        self.shader = None  # 着色器程序

class PhysicsComponent:
    """物理组件，存储实体的物理属性"""
    
    def __init__(self, mass=1.0, is_static=False):
        self.mass = mass  # 质量
        self.is_static = is_static  # 是否静态（不受物理影响）
        self.velocity = np.zeros(3, dtype=np.float32)  # 速度
        self.acceleration = np.zeros(3, dtype=np.float32)  # 加速度
        self.forces = np.zeros(3, dtype=np.float32)  # 作用力
        self.collider = None  # 碰撞体
        self.restitution = 0.5  # 弹性系数
        self.friction = 0.5  # 摩擦系数
        self.body_id = -1  # 物理引擎中的ID

class InputComponent:
    """输入组件，定义实体如何响应输入"""
    
    def __init__(self, controllable=True):
        self.controllable = controllable  # 是否可控制
        self.input_map = {}  # 输入映射
    
    def add_input_mapping(self, input_key, action):
        """添加输入映射"""
        self.input_map[input_key] = action

class CameraComponent:
    """相机组件，定义视角和投影"""
    
    def __init__(self, fov=60.0, near=0.1, far=1000.0, is_active=False):
        self.fov = fov  # 视场角
        self.near = near  # 近裁剪面
        self.far = far  # 远裁剪面
        self.is_active = is_active  # 是否激活
        self.projection_matrix = np.identity(4, dtype=np.float32)  # 投影矩阵
        self.view_matrix = np.identity(4, dtype=np.float32)  # 视图矩阵
        self.update_projection_matrix()
    
    def update_projection_matrix(self):
        """更新投影矩阵"""
        # 简化版本，实际应用中需要完整的矩阵计算
        # 这里只是一个占位符
        pass
    
    def update_view_matrix(self, transform):
        """根据变换更新视图矩阵"""
        # 简化版本，实际应用中需要完整的矩阵计算
        # 这里只是一个占位符
        pass

# 基础UI组件
class UIComponent:
    """UI组件，定义UI元素"""
    
    def __init__(self, position=(0, 0), size=(100, 50), text="", visible=True):
        self.position = position  # UI元素位置
        self.size = size  # UI元素大小
        self.text = text  # UI文本
        self.visible = visible  # 是否可见
        self.color = (255, 255, 255)  # 颜色
        self.font_size = 16  # 字体大小
        self.on_click = None  # 点击回调
        self.parent = None  # 父组件
        self.children = []  # 子组件
        self.z_index = 0  # Z轴顺序，值越大越靠前
        self.enabled = True  # 是否启用
        self.focused = False  # 是否获得焦点
        self.hovered = False  # 是否悬停
        self.draggable = False  # 是否可拖动
        self.drag_offset = (0, 0)  # 拖动偏移
    
    def get_absolute_position(self):
        """获取绝对位置（考虑父组件）"""
        if self.parent:
            parent_pos = self.parent.get_absolute_position()
            return (self.position[0] + parent_pos[0], self.position[1] + parent_pos[1])
        return self.position
    
    def contains_point(self, x, y):
        """检查点是否在UI元素内"""
        abs_pos = self.get_absolute_position()
        return (abs_pos[0] <= x <= abs_pos[0] + self.size[0] and 
                abs_pos[1] <= y <= abs_pos[1] + self.size[1])
    
    def add_child(self, child):
        """添加子组件"""
        child.parent = self
        self.children.append(child)
    
    def remove_child(self, child):
        """移除子组件"""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

# 按钮组件
class UIButtonComponent(UIComponent):
    """按钮组件，可点击的UI元素"""
    
    def __init__(self, position=(0, 0), size=(100, 50), text="Button", visible=True):
        super().__init__(position, size, text, visible)
        self.normal_color = (100, 100, 200)  # 正常状态颜色
        self.hover_color = (120, 120, 220)  # 悬停状态颜色
        self.pressed_color = (80, 80, 180)  # 按下状态颜色
        self.disabled_color = (150, 150, 150)  # 禁用状态颜色
        self.color = self.normal_color
        self.pressed = False  # 是否按下
        self.on_click = None  # 点击回调
    
    def update(self):
        """更新按钮状态"""
        if not self.enabled:
            self.color = self.disabled_color
        elif self.pressed:
            self.color = self.pressed_color
        elif self.hovered:
            self.color = self.hover_color
        else:
            self.color = self.normal_color

# 标签组件
class UILabelComponent(UIComponent):
    """标签组件，显示文本的UI元素"""
    
    def __init__(self, position=(0, 0), size=(100, 30), text="Label", visible=True):
        super().__init__(position, size, text, visible)
        self.alignment = "left"  # 文本对齐方式：left, center, right
        self.color = (255, 255, 255)  # 文本颜色
        self.background_color = None  # 背景颜色，None表示透明

# 面板组件
class UIPanelComponent(UIComponent):
    """面板组件，可包含其他UI元素的容器"""
    
    def __init__(self, position=(0, 0), size=(300, 200), text="", visible=True):
        super().__init__(position, size, text, visible)
        self.background_color = (50, 50, 50, 200)  # 背景颜色，带透明度
        self.border_color = (100, 100, 100)  # 边框颜色
        self.border_width = 1  # 边框宽度
        self.padding = (10, 10)  # 内边距

# 滑块组件
class UISliderComponent(UIComponent):
    """滑块组件，可调节数值的UI元素"""
    
    def __init__(self, position=(0, 0), size=(200, 30), text="", visible=True):
        super().__init__(position, size, text, visible)
        self.min_value = 0.0  # 最小值
        self.max_value = 1.0  # 最大值
        self.value = 0.5  # 当前值
        self.handle_size = (20, 20)  # 滑块手柄大小
        self.handle_color = (150, 150, 150)  # 滑块手柄颜色
        self.track_color = (80, 80, 80)  # 滑块轨道颜色
        self.on_value_changed = None  # 值变化回调
    
    def set_value(self, value):
        """设置滑块值"""
        old_value = self.value
        self.value = max(self.min_value, min(self.max_value, value))
        if self.value != old_value and self.on_value_changed:
            self.on_value_changed(self.value)
    
    def get_handle_position(self):
        """获取滑块手柄位置"""
        abs_pos = self.get_absolute_position()
        normalized_value = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = abs_pos[0] + normalized_value * (self.size[0] - self.handle_size[0])
        handle_y = abs_pos[1] + (self.size[1] - self.handle_size[1]) / 2
        return (handle_x, handle_y)
    
    def handle_contains_point(self, x, y):
        """检查点是否在滑块手柄内"""
        handle_pos = self.get_handle_position()
        return (handle_pos[0] <= x <= handle_pos[0] + self.handle_size[0] and 
                handle_pos[1] <= y <= handle_pos[1] + self.handle_size[1])

# 文本框组件
class UITextBoxComponent(UIComponent):
    """文本框组件，可输入文本的UI元素"""
    
    def __init__(self, position=(0, 0), size=(200, 30), text="", visible=True):
        super().__init__(position, size, text, visible)
        self.placeholder = "Enter text..."  # 占位文本
        self.background_color = (30, 30, 30)  # 背景颜色
        self.border_color = (100, 100, 100)  # 边框颜色
        self.border_width = 1  # 边框宽度
        self.text_color = (255, 255, 255)  # 文本颜色
        self.placeholder_color = (150, 150, 150)  # 占位文本颜色
        self.cursor_position = 0  # 光标位置
        self.cursor_visible = True  # 光标是否可见
        self.cursor_blink_time = 0.5  # 光标闪烁时间
        self.cursor_timer = 0  # 光标计时器
        self.on_text_changed = None  # 文本变化回调
        self.max_length = 100  # 最大文本长度
    
    def insert_text(self, text):
        """在光标位置插入文本"""
        if len(self.text) + len(text) <= self.max_length:
            self.text = self.text[:self.cursor_position] + text + self.text[self.cursor_position:]
            self.cursor_position += len(text)
            if self.on_text_changed:
                self.on_text_changed(self.text)
    
    def delete_text(self, forward=False):
        """删除光标位置的文本"""
        if forward and self.cursor_position < len(self.text):
            self.text = self.text[:self.cursor_position] + self.text[self.cursor_position+1:]
        elif not forward and self.cursor_position > 0:
            self.text = self.text[:self.cursor_position-1] + self.text[self.cursor_position:]
            self.cursor_position -= 1
        if self.on_text_changed:
            self.on_text_changed(self.text)
    
    def move_cursor(self, offset):
        """移动光标"""
        self.cursor_position = max(0, min(len(self.text), self.cursor_position + offset))
        self.cursor_timer = 0  # 重置光标计时器
        self.cursor_visible = True

# 复选框组件
class UICheckBoxComponent(UIComponent):
    """复选框组件，可选中/取消选中的UI元素"""
    
    def __init__(self, position=(0, 0), size=(20, 20), text="", visible=True):
        super().__init__(position, size, text, visible)
        self.checked = False  # 是否选中
        self.box_color = (80, 80, 80)  # 复选框颜色
        self.check_color = (255, 255, 255)  # 选中标记颜色
        self.on_checked_changed = None  # 选中状态变化回调
    
    def toggle(self):
        """切换选中状态"""
        self.checked = not self.checked
        if self.on_checked_changed:
            self.on_checked_changed(self.checked)

# 下拉菜单组件
class UIDropdownComponent(UIComponent):
    """下拉菜单组件，可选择多个选项的UI元素"""
    
    def __init__(self, position=(0, 0), size=(200, 30), text="", visible=True):
        super().__init__(position, size, text, visible)
        self.options = []  # 选项列表
        self.selected_index = -1  # 选中的选项索引
        self.dropdown_open = False  # 下拉菜单是否打开
        self.dropdown_height = 150  # 下拉菜单高度
        self.option_height = 30  # 选项高度
        self.background_color = (50, 50, 50)  # 背景颜色
        self.option_color = (70, 70, 70)  # 选项颜色
        self.hover_option_color = (90, 90, 90)  # 悬停选项颜色
        self.selected_option_color = (100, 100, 150)  # 选中选项颜色
        self.border_color = (100, 100, 100)  # 边框颜色
        self.border_width = 1  # 边框宽度
        self.on_selection_changed = None  # 选择变化回调
        self.hovered_option = -1  # 悬停的选项索引
    
    def add_option(self, option):
        """添加选项"""
        self.options.append(option)
        if self.selected_index == -1 and len(self.options) > 0:
            self.selected_index = 0
            self.text = self.options[0]
    
    def select_option(self, index):
        """选择选项"""
        if 0 <= index < len(self.options):
            old_index = self.selected_index
            self.selected_index = index
            self.text = self.options[index]
            self.dropdown_open = False
            if old_index != index and self.on_selection_changed:
                self.on_selection_changed(index, self.options[index])
    
    def toggle_dropdown(self):
        """切换下拉菜单状态"""
        self.dropdown_open = not self.dropdown_open
    
    def get_dropdown_rect(self):
        """获取下拉菜单矩形"""
        abs_pos = self.get_absolute_position()
        return (abs_pos[0], abs_pos[1] + self.size[1], 
                self.size[0], min(self.dropdown_height, len(self.options) * self.option_height))
    
    def get_option_rect(self, index):
        """获取选项矩形"""
        dropdown_rect = self.get_dropdown_rect()
        return (dropdown_rect[0], dropdown_rect[1] + index * self.option_height, 
                dropdown_rect[2], self.option_height)
    
    def option_at_point(self, x, y):
        """获取点所在的选项索引"""
        if not self.dropdown_open:
            return -1
        
        dropdown_rect = self.get_dropdown_rect()
        if (dropdown_rect[0] <= x <= dropdown_rect[0] + dropdown_rect[2] and 
            dropdown_rect[1] <= y <= dropdown_rect[1] + dropdown_rect[3]):
            option_index = int((y - dropdown_rect[1]) / self.option_height)
            if 0 <= option_index < len(self.options):
                return option_index
        return -1

# 窗口组件
class UIWindowComponent(UIPanelComponent):
    """窗口组件，可拖动的UI容器"""
    
    def __init__(self, position=(0, 0), size=(400, 300), title="Window", visible=True):
        super().__init__(position, size, "", visible)
        self.title = title  # 窗口标题
        self.title_bar_height = 30  # 标题栏高度
        self.title_bar_color = (70, 70, 100)  # 标题栏颜色
        self.close_button_size = (20, 20)  # 关闭按钮大小
        self.close_button_color = (200, 80, 80)  # 关闭按钮颜色
        self.draggable = True  # 窗口可拖动
        self.resizable = True  # 窗口可调整大小
        self.min_size = (100, 100)  # 最小窗口大小
        self.on_close = None  # 关闭回调
    
    def get_title_bar_rect(self):
        """获取标题栏矩形"""
        abs_pos = self.get_absolute_position()
        return (abs_pos[0], abs_pos[1], self.size[0], self.title_bar_height)
    
    def get_close_button_rect(self):
        """获取关闭按钮矩形"""
        title_bar_rect = self.get_title_bar_rect()
        return (title_bar_rect[0] + title_bar_rect[2] - self.close_button_size[0] - 5, 
                title_bar_rect[1] + (title_bar_rect[3] - self.close_button_size[1]) / 2, 
                self.close_button_size[0], self.close_button_size[1])
    
    def close_button_contains_point(self, x, y):
        """检查点是否在关闭按钮内"""
        close_rect = self.get_close_button_rect()
        return (close_rect[0] <= x <= close_rect[0] + close_rect[2] and 
                close_rect[1] <= y <= close_rect[1] + close_rect[3])
    
    def title_bar_contains_point(self, x, y):
        """检查点是否在标题栏内"""
        title_rect = self.get_title_bar_rect()
        return (title_rect[0] <= x <= title_rect[0] + title_rect[2] and 
                title_rect[1] <= y <= title_rect[1] + title_rect[3])
    
    def close(self):
        """关闭窗口"""
        self.visible = False
        if self.on_close:
            self.on_close() 