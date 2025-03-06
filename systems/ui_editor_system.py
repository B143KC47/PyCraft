import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import json
import os
from core.components import ComponentType, UIComponent, UIButtonComponent, UILabelComponent, UIPanelComponent, UISliderComponent, UITextBoxComponent, UICheckBoxComponent, UIDropdownComponent, UIWindowComponent

class UIEditorSystem:
    """UI编辑器系统，提供类似Unreal Engine的UI编辑功能"""
    
    def __init__(self, entity_manager, ui_system, width, height):
        self.entity_manager = entity_manager
        self.ui_system = ui_system
        self.width = width
        self.height = height
        
        # 编辑器状态
        self.active = False  # 编辑器是否激活
        self.selected_element = None  # 当前选中的UI元素
        self.dragging = False  # 是否正在拖动元素
        self.drag_offset = (0, 0)  # 拖动偏移
        self.grid_snap = True  # 是否启用网格对齐
        self.grid_size = 10  # 网格大小
        
        # 编辑器UI元素
        self.editor_ui = {}  # 存储编辑器UI元素
        self.palette_items = []  # UI元素调色板
        self.property_panel = None  # 属性面板
        self.hierarchy_panel = None  # 层级面板
        
        # 创建UI元素模板
        self.ui_templates = {
            "按钮": UIButtonComponent,
            "标签": UILabelComponent,
            "面板": UIPanelComponent,
            "滑块": UISliderComponent,
            "文本框": UITextBoxComponent,
            "复选框": UICheckBoxComponent,
            "下拉菜单": UIDropdownComponent,
            "窗口": UIWindowComponent
        }
        
        # 初始化编辑器UI
        self.init_editor_ui()
    
    def init_editor_ui(self):
        """初始化编辑器UI"""
        # 创建编辑器主面板
        editor_panel = self.entity_manager.create_entity("EditorPanel")
        panel_comp = UIPanelComponent(position=(0, 0), size=(self.width, 40), text="UI编辑器")
        panel_comp.background_color = (40, 40, 40, 200)
        panel_comp.visible = False  # 默认隐藏
        editor_panel.add_component(ComponentType.UI, panel_comp)
        self.editor_ui["main_panel"] = editor_panel
        
        # 创建工具栏按钮
        x_offset = 10
        
        # 保存按钮
        save_btn = self.ui_system.create_button("保存", (x_offset, 5), (60, 30), self.save_ui_layout)
        save_btn.get_component(ComponentType.UI).visible = False
        self.editor_ui["save_btn"] = save_btn
        x_offset += 70
        
        # 加载按钮
        load_btn = self.ui_system.create_button("加载", (x_offset, 5), (60, 30), self.load_ui_layout)
        load_btn.get_component(ComponentType.UI).visible = False
        self.editor_ui["load_btn"] = load_btn
        x_offset += 70
        
        # 网格对齐按钮
        grid_btn = self.ui_system.create_button("网格", (x_offset, 5), (60, 30), self.toggle_grid_snap)
        grid_btn.get_component(ComponentType.UI).visible = False
        self.editor_ui["grid_btn"] = grid_btn
        x_offset += 70
        
        # 帮助按钮
        help_btn = self.ui_system.create_button("帮助", (x_offset, 5), (60, 30), self.toggle_help_panel)
        help_btn.get_component(ComponentType.UI).visible = False
        self.editor_ui["help_btn"] = help_btn
        x_offset += 70
        
        # 创建属性面板
        prop_panel = self.entity_manager.create_entity("PropertyPanel")
        prop_comp = UIPanelComponent(position=(self.width - 250, 50), size=(240, 400), text="属性")
        prop_comp.background_color = (40, 40, 40, 200)
        prop_comp.visible = False
        prop_panel.add_component(ComponentType.UI, prop_comp)
        self.editor_ui["property_panel"] = prop_panel
        self.property_panel = prop_panel
        
        # 创建UI元素调色板面板
        palette_panel = self.entity_manager.create_entity("PalettePanel")
        palette_comp = UIPanelComponent(position=(10, 50), size=(150, 400), text="UI元素")
        palette_comp.background_color = (40, 40, 40, 200)
        palette_comp.visible = False
        palette_panel.add_component(ComponentType.UI, palette_comp)
        self.editor_ui["palette_panel"] = palette_panel
        
        # 添加UI元素到调色板
        y_offset = 40
        for template_name in self.ui_templates:
            btn = self.ui_system.create_button(template_name, (20, 50 + y_offset), (130, 30), 
                                              lambda name=template_name: self.create_ui_element(name))
            btn.get_component(ComponentType.UI).visible = False
            self.palette_items.append(btn)
            y_offset += 40
        
        # 创建层级面板
        hierarchy_panel = self.entity_manager.create_entity("HierarchyPanel")
        hierarchy_comp = UIPanelComponent(position=(170, 50), size=(200, 400), text="层级")
        hierarchy_comp.background_color = (40, 40, 40, 200)
        hierarchy_comp.visible = False
        hierarchy_panel.add_component(ComponentType.UI, hierarchy_comp)
        self.editor_ui["hierarchy_panel"] = hierarchy_panel
        self.hierarchy_panel = hierarchy_panel
        
        # 创建帮助面板（默认隐藏）
        help_panel = self.entity_manager.create_entity("HelpPanel")
        help_comp = UIPanelComponent(position=(self.width/2 - 200, self.height/2 - 200), size=(400, 400), text="帮助")
        help_comp.background_color = (40, 40, 40, 220)
        help_comp.visible = False
        help_panel.add_component(ComponentType.UI, help_comp)
        self.editor_ui["help_panel"] = help_panel
        
        # 添加帮助内容
        self.create_help_content()
    
    def create_help_content(self):
        """创建帮助内容"""
        help_panel = self.editor_ui["help_panel"]
        panel_pos = help_panel.get_component(ComponentType.UI).position
        
        # 帮助标题
        title = self.entity_manager.create_entity("Help_Title")
        title_comp = UILabelComponent(position=(panel_pos[0] + 20, panel_pos[1] + 40), 
                                     size=(360, 30), text="UI编辑器使用说明")
        title_comp.font_size = 24
        title_comp.visible = False
        title.add_component(ComponentType.UI, title_comp)
        self.editor_ui["help_title"] = title
        
        # 帮助内容
        help_texts = [
            "基本操作:",
            "- 点击左侧面板中的UI元素类型创建新元素",
            "- 点击元素选中，拖动可移动元素",
            "- 右侧面板可编辑选中元素的属性",
            "- 中间面板显示UI元素层级",
            "",
            "快捷键:",
            "- Ctrl+S: 保存布局",
            "- Ctrl+O: 加载布局",
            "- Ctrl+C: 复制选中元素",
            "- Ctrl+V: 粘贴元素",
            "- Delete: 删除选中元素",
            "- 方向键: 移动选中元素",
            "- Ctrl+G: 切换网格对齐"
        ]
        
        y_offset = 80
        for i, text in enumerate(help_texts):
            help_text = self.entity_manager.create_entity(f"Help_Text_{i}")
            text_comp = UILabelComponent(position=(panel_pos[0] + 20, panel_pos[1] + y_offset), 
                                        size=(360, 20), text=text)
            text_comp.visible = False
            help_text.add_component(ComponentType.UI, text_comp)
            self.editor_ui[f"help_text_{i}"] = help_text
            y_offset += 20
        
        # 关闭按钮
        close_btn = self.ui_system.create_button("关闭", 
                                               (panel_pos[0] + 150, panel_pos[1] + 350), (100, 30),
                                               self.toggle_help_panel)
        close_btn.get_component(ComponentType.UI).visible = False
        self.editor_ui["help_close_btn"] = close_btn
    
    def toggle_editor(self):
        """切换编辑器状态"""
        self.active = not self.active
        
        # 显示/隐藏编辑器UI
        for entity_id, entity in self.editor_ui.items():
            ui_comp = entity.get_component(ComponentType.UI)
            ui_comp.visible = self.active
        
        # 显示/隐藏调色板项目
        for btn in self.palette_items:
            ui_comp = btn.get_component(ComponentType.UI)
            ui_comp.visible = self.active
        
        # 更新属性面板
        self.update_property_panel()
        
        # 更新层级面板
        self.update_hierarchy_panel()
    
    def update(self, delta_time):
        """更新编辑器状态"""
        if not self.active:
            return
        
        # 处理鼠标拖动
        if self.dragging and self.selected_element:
            mouse_pos = pygame.mouse.get_pos()
            ui_comp = self.selected_element.get_component(ComponentType.UI)
            
            # 计算新位置
            new_x = mouse_pos[0] - self.drag_offset[0]
            new_y = mouse_pos[1] - self.drag_offset[1]
            
            # 网格对齐
            if self.grid_snap:
                new_x = round(new_x / self.grid_size) * self.grid_size
                new_y = round(new_y / self.grid_size) * self.grid_size
            
            ui_comp.position = (new_x, new_y)
            
            # 更新属性面板
            self.update_property_panel()
    
    def handle_event(self, event):
        """处理编辑器事件"""
        if not self.active:
            return False
        
        # 处理鼠标点击
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 左键点击
            mouse_pos = pygame.mouse.get_pos()
            
            # 检查是否点击了UI元素
            ui_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
            
            # 过滤掉编辑器UI元素
            ui_entities = [e for e in ui_entities if e not in self.editor_ui.values() and e not in self.palette_items
                          and not e.name.startswith("Property_") and not e.name.startswith("Hierarchy_")
                          and not e.name.startswith("AddMenu_") and not e.name.startswith("SaveDialog_")
                          and not e.name.startswith("LoadDialog_")]
            
            # 按照Z顺序（从前到后）检查点击
            for entity in sorted(ui_entities, key=lambda e: e.get_component(ComponentType.UI).z_index, reverse=True):
                ui_comp = entity.get_component(ComponentType.UI)
                
                if not ui_comp.visible:
                    continue
                
                if self.ui_system.is_point_inside(ui_comp, mouse_pos[0], mouse_pos[1]):
                    self.selected_element = entity
                    self.dragging = True
                    self.drag_offset = (mouse_pos[0] - ui_comp.position[0], mouse_pos[1] - ui_comp.position[1])
                    
                    # 更新属性面板
                    self.update_property_panel()
                    self.update_hierarchy_panel()
                    return True
            
            # 如果点击了空白区域，取消选择
            self.selected_element = None
            self.update_property_panel()
            self.update_hierarchy_panel()
        
        # 处理鼠标释放
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # 左键释放
            self.dragging = False
        
        # 处理键盘事件
        elif event.type == pygame.KEYDOWN:
            # 删除选中的元素 (Delete)
            if event.key == pygame.K_DELETE and self.selected_element:
                self.delete_selected_element()
                return True
            
            # 复制选中的元素 (Ctrl+C)
            elif event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL and self.selected_element:
                self.duplicate_element()
                return True
            
            # 粘贴元素 (Ctrl+V)
            elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.paste_element()
                return True
            
            # 保存布局 (Ctrl+S)
            elif event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.save_ui_layout()
                return True
            
            # 加载布局 (Ctrl+O)
            elif event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.load_ui_layout()
                return True
            
            # 切换网格对齐 (Ctrl+G)
            elif event.key == pygame.K_g and pygame.key.get_mods() & pygame.KMOD_CTRL:
                self.toggle_grid_snap()
                return True
            
            # 上移元素 (↑)
            elif event.key == pygame.K_UP and self.selected_element:
                self.move_element(0, -self.grid_size if self.grid_snap else -1)
                return True
            
            # 下移元素 (↓)
            elif event.key == pygame.K_DOWN and self.selected_element:
                self.move_element(0, self.grid_size if self.grid_snap else 1)
                return True
            
            # 左移元素 (←)
            elif event.key == pygame.K_LEFT and self.selected_element:
                self.move_element(-self.grid_size if self.grid_snap else -1, 0)
                return True
            
            # 右移元素 (→)
            elif event.key == pygame.K_RIGHT and self.selected_element:
                self.move_element(self.grid_size if self.grid_snap else 1, 0)
                return True
        
        return False
    
    def create_ui_element(self, template_name):
        """从模板创建UI元素"""
        template_class = self.ui_templates.get(template_name)
        if not template_class:
            return
        
        # 创建新实体
        entity = self.entity_manager.create_entity(template_name)
        
        # 获取鼠标位置作为默认位置
        mouse_pos = pygame.mouse.get_pos()
        default_pos = (mouse_pos[0], mouse_pos[1])
        
        # 如果启用了网格对齐，则对齐到网格
        if self.grid_snap:
            default_pos = (
                round(default_pos[0] / self.grid_size) * self.grid_size,
                round(default_pos[1] / self.grid_size) * self.grid_size
            )
        
        # 创建组件
        if template_name == "按钮":
            ui_comp = template_class(position=default_pos, size=(100, 40), text="新按钮")
            ui_comp.normal_color = (100, 100, 200)
            ui_comp.hover_color = (120, 120, 220)
            ui_comp.pressed_color = (80, 80, 180)
        elif template_name == "标签":
            ui_comp = template_class(position=default_pos, size=(100, 30), text="新标签")
            ui_comp.alignment = "left"
            ui_comp.color = (255, 255, 255)
        elif template_name == "面板":
            ui_comp = template_class(position=default_pos, size=(200, 150), text="新面板")
            ui_comp.background_color = (50, 50, 50, 200)
            ui_comp.border_color = (100, 100, 100)
            ui_comp.border_width = 1
        elif template_name == "滑块":
            ui_comp = template_class(position=default_pos, size=(150, 30))
            ui_comp.min_value = 0.0
            ui_comp.max_value = 1.0
            ui_comp.value = 0.5
            ui_comp.handle_color = (150, 150, 150)
            ui_comp.track_color = (80, 80, 80)
        elif template_name == "文本框":
            ui_comp = template_class(position=default_pos, size=(150, 30))
            ui_comp.placeholder = "输入文本..."
            ui_comp.background_color = (30, 30, 30)
            ui_comp.border_color = (100, 100, 100)
            ui_comp.text_color = (255, 255, 255)
        elif template_name == "复选框":
            ui_comp = template_class(position=default_pos, size=(20, 20), text="新复选框")
            ui_comp.checked = False
            ui_comp.check_color = (255, 255, 255)
            ui_comp.box_color = (80, 80, 80)
        elif template_name == "下拉菜单":
            ui_comp = template_class(position=default_pos, size=(150, 30), text="选项")
            ui_comp.options = ["选项1", "选项2", "选项3"]
            ui_comp.selected_index = 0
            ui_comp.dropdown_color = (40, 40, 40)
        elif template_name == "窗口":
            ui_comp = template_class(position=default_pos, size=(300, 200), title="新窗口")
            ui_comp.title_bar_color = (60, 60, 100)
            ui_comp.background_color = (40, 40, 40, 220)
            ui_comp.draggable = True
        else:
            ui_comp = UIComponent(position=default_pos, size=(100, 50), text="新元素")
        
        # 设置通用属性
        ui_comp.z_index = 0  # 默认Z顺序
        
        # 添加组件到实体
        entity.add_component(ComponentType.UI, ui_comp)
        
        # 选中新创建的元素
        self.selected_element = entity
        self.update_property_panel()
        self.update_hierarchy_panel()
        
        return entity
    
    def duplicate_element(self):
        """复制选中的UI元素"""
        if not self.selected_element:
            return
        
        # 获取原始组件
        orig_ui_comp = self.selected_element.get_component(ComponentType.UI)
        
        # 创建新实体
        entity = self.entity_manager.create_entity(self.selected_element.name + "_copy")
        
        # 复制组件属性
        if isinstance(orig_ui_comp, UIButtonComponent):
            ui_comp = UIButtonComponent(
                position=(orig_ui_comp.position[0] + 20, orig_ui_comp.position[1] + 20),
                size=orig_ui_comp.size,
                text=orig_ui_comp.text,
                visible=orig_ui_comp.visible
            )
            ui_comp.normal_color = orig_ui_comp.normal_color
            ui_comp.hover_color = orig_ui_comp.hover_color
            ui_comp.pressed_color = orig_ui_comp.pressed_color
        else:
            # 默认复制基本UI组件
            ui_comp = UIComponent(
                position=(orig_ui_comp.position[0] + 20, orig_ui_comp.position[1] + 20),
                size=orig_ui_comp.size,
                text=orig_ui_comp.text,
                visible=orig_ui_comp.visible
            )
            ui_comp.color = orig_ui_comp.color
            ui_comp.font_size = orig_ui_comp.font_size
        
        # 添加组件到实体
        entity.add_component(ComponentType.UI, ui_comp)
        
        # 选中新创建的元素
        self.selected_element = entity
        self.update_property_panel()
        self.update_hierarchy_panel()
    
    def update_property_panel(self):
        """更新属性面板"""
        # 清除旧的属性控件
        property_entities = [e for e in self.entity_manager.entities.values() 
                            if e.name.startswith("Property_") and e != self.property_panel]
        for entity in property_entities:
            self.entity_manager.remove_entity(entity.id)
        
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        
        # 创建属性控件
        y_offset = 50
        
        # 名称属性
        name_label = self.ui_system.create_label(f"名称: {self.selected_element.name}", 
                                               (self.width - 240, y_offset))
        name_label.get_component(ComponentType.UI).visible = self.active
        name_label.name = "Property_Name"
        y_offset += 30
        
        # 位置属性
        pos_label = self.ui_system.create_label(f"位置: ", (self.width - 240, y_offset))
        pos_label.get_component(ComponentType.UI).visible = self.active
        pos_label.name = "Property_Position_Label"
        
        # X坐标输入框
        pos_x_btn = self.ui_system.create_button(f"X: {ui_comp.position[0]}", 
                                               (self.width - 200, y_offset), (70, 25),
                                               lambda e: self.edit_position_x())
        pos_x_btn.get_component(ComponentType.UI).visible = self.active
        pos_x_btn.name = "Property_Position_X"
        
        # Y坐标输入框
        pos_y_btn = self.ui_system.create_button(f"Y: {ui_comp.position[1]}", 
                                               (self.width - 120, y_offset), (70, 25),
                                               lambda e: self.edit_position_y())
        pos_y_btn.get_component(ComponentType.UI).visible = self.active
        pos_y_btn.name = "Property_Position_Y"
        
        y_offset += 30
        
        # 尺寸属性
        size_label = self.ui_system.create_label(f"尺寸: ", (self.width - 240, y_offset))
        size_label.get_component(ComponentType.UI).visible = self.active
        size_label.name = "Property_Size_Label"
        
        # 宽度输入框
        size_w_btn = self.ui_system.create_button(f"W: {ui_comp.size[0]}", 
                                                (self.width - 200, y_offset), (70, 25),
                                                lambda e: self.edit_size_width())
        size_w_btn.get_component(ComponentType.UI).visible = self.active
        size_w_btn.name = "Property_Size_Width"
        
        # 高度输入框
        size_h_btn = self.ui_system.create_button(f"H: {ui_comp.size[1]}", 
                                                (self.width - 120, y_offset), (70, 25),
                                                lambda e: self.edit_size_height())
        size_h_btn.get_component(ComponentType.UI).visible = self.active
        size_h_btn.name = "Property_Size_Height"
        
        y_offset += 30
        
        # 文本属性
        text_label = self.ui_system.create_label(f"文本: ", (self.width - 240, y_offset))
        text_label.get_component(ComponentType.UI).visible = self.active
        text_label.name = "Property_Text_Label"
        
        # 文本输入按钮
        text_btn = self.ui_system.create_button(f"{ui_comp.text[:10]}..." if len(ui_comp.text) > 10 else ui_comp.text, 
                                              (self.width - 200, y_offset), (140, 25),
                                              lambda e: self.edit_text())
        text_btn.get_component(ComponentType.UI).visible = self.active
        text_btn.name = "Property_Text_Button"
        
        y_offset += 30
        
        # 颜色属性
        color_label = self.ui_system.create_label(f"颜色: ", (self.width - 240, y_offset))
        color_label.get_component(ComponentType.UI).visible = self.active
        color_label.name = "Property_Color_Label"
        
        # 颜色预览
        color_preview = self.entity_manager.create_entity("Property_Color_Preview")
        preview_comp = UIComponent(position=(self.width - 200, y_offset), size=(25, 25), text="")
        preview_comp.color = ui_comp.color
        preview_comp.visible = self.active
        color_preview.add_component(ComponentType.UI, preview_comp)
        
        # 颜色编辑按钮
        color_btn = self.ui_system.create_button("编辑", (self.width - 170, y_offset), (50, 25),
                                               lambda e: self.edit_color())
        color_btn.get_component(ComponentType.UI).visible = self.active
        color_btn.name = "Property_Color_Button"
        
        y_offset += 30
        
        # 可见性属性
        visible_btn = self.ui_system.create_button(f"可见: {'是' if ui_comp.visible else '否'}", 
                                                 (self.width - 240, y_offset), (80, 25),
                                                 lambda e: self.toggle_visibility())
        visible_btn.get_component(ComponentType.UI).visible = self.active
        visible_btn.name = "Property_Visible"
        
        y_offset += 30
        
        # Z顺序属性
        z_label = self.ui_system.create_label(f"Z顺序: ", (self.width - 240, y_offset))
        z_label.get_component(ComponentType.UI).visible = self.active
        z_label.name = "Property_ZIndex_Label"
        
        # Z顺序减少按钮
        z_dec_btn = self.ui_system.create_button("-", (self.width - 200, y_offset), (25, 25),
                                               lambda e: self.decrease_z_index())
        z_dec_btn.get_component(ComponentType.UI).visible = self.active
        z_dec_btn.name = "Property_ZIndex_Dec"
        
        # Z顺序值
        z_value = self.ui_system.create_label(f"{ui_comp.z_index}", (self.width - 170, y_offset))
        z_value.get_component(ComponentType.UI).visible = self.active
        z_value.name = "Property_ZIndex_Value"
        
        # Z顺序增加按钮
        z_inc_btn = self.ui_system.create_button("+", (self.width - 140, y_offset), (25, 25),
                                               lambda e: self.increase_z_index())
        z_inc_btn.get_component(ComponentType.UI).visible = self.active
        z_inc_btn.name = "Property_ZIndex_Inc"
    
    def edit_position_x(self):
        """编辑X坐标"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        try:
            # 这里应该弹出一个输入对话框，但为简化起见，我们使用一个固定值增加
            ui_comp.position = (ui_comp.position[0] + 10, ui_comp.position[1])
            self.update_property_panel()
        except:
            pass
    
    def edit_position_y(self):
        """编辑Y坐标"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        try:
            # 这里应该弹出一个输入对话框，但为简化起见，我们使用一个固定值增加
            ui_comp.position = (ui_comp.position[0], ui_comp.position[1] + 10)
            self.update_property_panel()
        except:
            pass
    
    def edit_size_width(self):
        """编辑宽度"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        try:
            # 这里应该弹出一个输入对话框，但为简化起见，我们使用一个固定值增加
            ui_comp.size = (ui_comp.size[0] + 10, ui_comp.size[1])
            self.update_property_panel()
        except:
            pass
    
    def edit_size_height(self):
        """编辑高度"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        try:
            # 这里应该弹出一个输入对话框，但为简化起见，我们使用一个固定值增加
            ui_comp.size = (ui_comp.size[0], ui_comp.size[1] + 10)
            self.update_property_panel()
        except:
            pass
    
    def edit_text(self):
        """编辑文本"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        try:
            # 这里应该弹出一个输入对话框，但为简化起见，我们使用一个固定文本
            ui_comp.text = ui_comp.text + "_编辑"
            self.update_property_panel()
        except:
            pass
    
    def edit_color(self):
        """编辑颜色"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        try:
            # 这里应该弹出一个颜色选择器，但为简化起见，我们使用一个随机颜色
            import random
            ui_comp.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.update_property_panel()
        except:
            pass
    
    def toggle_visibility(self):
        """切换可见性"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        ui_comp.visible = not ui_comp.visible
        self.update_property_panel()
    
    def increase_z_index(self):
        """增加Z顺序"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        ui_comp.z_index += 1
        self.update_property_panel()
        self.update_hierarchy_panel()
    
    def decrease_z_index(self):
        """减少Z顺序"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        if ui_comp.z_index > 0:
            ui_comp.z_index -= 1
            self.update_property_panel()
            self.update_hierarchy_panel()
    
    def update_hierarchy_panel(self):
        """更新层级面板"""
        # 清除旧的层级控件
        hierarchy_entities = [e for e in self.entity_manager.entities.values() 
                             if e.name.startswith("Hierarchy_") and e != self.hierarchy_panel]
        for entity in hierarchy_entities:
            self.entity_manager.remove_entity(entity.id)
        
        # 获取所有UI实体（排除编辑器UI）
        ui_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
        ui_entities = [e for e in ui_entities if e not in self.editor_ui.values() and e not in self.palette_items
                      and not e.name.startswith("Property_") and not e.name.startswith("Hierarchy_")]
        
        # 按Z顺序排序
        ui_entities.sort(key=lambda e: e.get_component(ComponentType.UI).z_index)
        
        # 创建层级列表
        y_offset = 50
        for entity in ui_entities:
            # 创建层级项按钮
            item_btn = self.ui_system.create_button(f"{entity.name}", 
                                                  (180, y_offset), (180, 25),
                                                  lambda e, ent=entity: self.select_entity_from_hierarchy(ent))
            item_btn.get_component(ComponentType.UI).visible = self.active
            item_btn.name = f"Hierarchy_{entity.id}"
            
            # 如果是选中的元素，高亮显示
            if entity == self.selected_element:
                item_btn.get_component(ComponentType.UI).color = (255, 255, 0)
            
            y_offset += 30
        
        # 添加一个"添加新元素"按钮
        add_btn = self.ui_system.create_button("+ 添加新元素", (180, y_offset), (180, 25),
                                             lambda e: self.show_add_element_menu())
        add_btn.get_component(ComponentType.UI).visible = self.active
        add_btn.name = "Hierarchy_AddNew"
    
    def select_entity_from_hierarchy(self, entity):
        """从层级面板选择实体"""
        self.selected_element = entity
        self.update_property_panel()
        self.update_hierarchy_panel()
    
    def show_add_element_menu(self):
        """显示添加元素菜单"""
        # 清除旧的菜单
        menu_entities = [e for e in self.entity_manager.entities.values() 
                        if e.name.startswith("AddMenu_")]
        for entity in menu_entities:
            self.entity_manager.remove_entity(entity.id)
        
        # 创建菜单面板
        menu_panel = self.entity_manager.create_entity("AddMenu_Panel")
        panel_comp = UIPanelComponent(position=(180, 450), size=(180, 200), text="添加元素")
        panel_comp.background_color = (60, 60, 60, 220)
        panel_comp.visible = self.active
        menu_panel.add_component(ComponentType.UI, panel_comp)
        
        # 添加菜单项
        y_offset = 30
        for template_name in self.ui_templates:
            menu_btn = self.ui_system.create_button(template_name, 
                                                  (190, 450 + y_offset), (160, 25),
                                                  lambda e, name=template_name: self.create_ui_element_and_close_menu(name))
            menu_btn.get_component(ComponentType.UI).visible = self.active
            menu_btn.name = f"AddMenu_{template_name}"
            y_offset += 30
        
        # 添加关闭按钮
        close_btn = self.ui_system.create_button("关闭", (190, 450 + y_offset), (160, 25),
                                               lambda e: self.close_add_element_menu())
        close_btn.get_component(ComponentType.UI).visible = self.active
        close_btn.name = "AddMenu_Close"
    
    def create_ui_element_and_close_menu(self, template_name):
        """创建UI元素并关闭菜单"""
        self.create_ui_element(template_name)
        self.close_add_element_menu()
    
    def close_add_element_menu(self):
        """关闭添加元素菜单"""
        menu_entities = [e for e in self.entity_manager.entities.values() 
                        if e.name.startswith("AddMenu_")]
        for entity in menu_entities:
            self.entity_manager.remove_entity(entity.id)
    
    def toggle_grid_snap(self, entity=None):
        """切换网格对齐"""
        self.grid_snap = not self.grid_snap
        
        # 更新按钮文本
        grid_btn = self.editor_ui["grid_btn"]
        ui_comp = grid_btn.get_component(ComponentType.UI)
        ui_comp.text = "网格: 开" if self.grid_snap else "网格: 关"
    
    def save_ui_layout(self, entity=None):
        """保存UI布局到文件"""
        # 获取所有UI实体（排除编辑器UI）
        ui_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
        ui_entities = [e for e in ui_entities if e not in self.editor_ui.values() and e not in self.palette_items
                      and not e.name.startswith("Property_") and not e.name.startswith("Hierarchy_")
                      and not e.name.startswith("AddMenu_")]
        
        if not ui_entities:
            print("没有UI元素可保存")
            return
        
        # 显示保存对话框
        self.show_save_dialog()
    
    def show_save_dialog(self):
        """显示保存对话框"""
        # 清除旧的对话框
        dialog_entities = [e for e in self.entity_manager.entities.values() 
                          if e.name.startswith("SaveDialog_")]
        for entity in dialog_entities:
            self.entity_manager.remove_entity(entity.id)
        
        # 创建对话框面板
        dialog_panel = self.entity_manager.create_entity("SaveDialog_Panel")
        panel_comp = UIPanelComponent(position=(self.width/2 - 150, self.height/2 - 100), size=(300, 200), text="保存布局")
        panel_comp.background_color = (60, 60, 60, 220)
        panel_comp.visible = self.active
        dialog_panel.add_component(ComponentType.UI, panel_comp)
        
        # 添加布局名称标签
        name_label = self.ui_system.create_label("布局名称:", 
                                               (self.width/2 - 140, self.height/2 - 70))
        name_label.get_component(ComponentType.UI).visible = self.active
        name_label.name = "SaveDialog_NameLabel"
        
        # 添加默认布局名称
        import time
        default_name = f"layout_{int(time.time())}"
        
        # 添加布局名称按钮（模拟输入框）
        name_btn = self.ui_system.create_button(default_name, 
                                              (self.width/2 - 140, self.height/2 - 40), (280, 30),
                                              lambda e: self.edit_layout_name())
        name_btn.get_component(ComponentType.UI).visible = self.active
        name_btn.name = "SaveDialog_NameInput"
        
        # 添加保存按钮
        save_btn = self.ui_system.create_button("保存", 
                                              (self.width/2 - 140, self.height/2 + 10), (130, 30),
                                              lambda e: self.do_save_layout())
        save_btn.get_component(ComponentType.UI).visible = self.active
        save_btn.name = "SaveDialog_SaveBtn"
        
        # 添加取消按钮
        cancel_btn = self.ui_system.create_button("取消", 
                                                (self.width/2 + 10, self.height/2 + 10), (130, 30),
                                                lambda e: self.close_save_dialog())
        cancel_btn.get_component(ComponentType.UI).visible = self.active
        cancel_btn.name = "SaveDialog_CancelBtn"
    
    def edit_layout_name(self):
        """编辑布局名称"""
        # 这里应该弹出一个输入对话框，但为简化起见，我们使用一个固定名称
        name_btn = next((e for e in self.entity_manager.entities.values() 
                        if e.name == "SaveDialog_NameInput"), None)
        if name_btn:
            ui_comp = name_btn.get_component(ComponentType.UI)
            ui_comp.text = ui_comp.text + "_edited"
    
    def do_save_layout(self):
        """执行保存布局操作"""
        # 获取布局名称
        name_btn = next((e for e in self.entity_manager.entities.values() 
                        if e.name == "SaveDialog_NameInput"), None)
        if not name_btn:
            return
        
        layout_name = name_btn.get_component(ComponentType.UI).text
        
        # 获取所有UI实体（排除编辑器UI）
        ui_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
        ui_entities = [e for e in ui_entities if e not in self.editor_ui.values() and e not in self.palette_items
                      and not e.name.startswith("Property_") and not e.name.startswith("Hierarchy_")
                      and not e.name.startswith("AddMenu_") and not e.name.startswith("SaveDialog_")
                      and not e.name.startswith("LoadDialog_")]
        
        # 创建UI布局数据
        layout_data = []
        for entity in ui_entities:
            ui_comp = entity.get_component(ComponentType.UI)
            
            # 确定组件类型
            component_type = "UIComponent"
            if isinstance(ui_comp, UIButtonComponent):
                component_type = "UIButtonComponent"
            elif isinstance(ui_comp, UILabelComponent):
                component_type = "UILabelComponent"
            elif isinstance(ui_comp, UIPanelComponent):
                component_type = "UIPanelComponent"
            elif isinstance(ui_comp, UISliderComponent):
                component_type = "UISliderComponent"
            elif isinstance(ui_comp, UITextBoxComponent):
                component_type = "UITextBoxComponent"
            elif isinstance(ui_comp, UICheckBoxComponent):
                component_type = "UICheckBoxComponent"
            elif isinstance(ui_comp, UIDropdownComponent):
                component_type = "UIDropdownComponent"
            elif isinstance(ui_comp, UIWindowComponent):
                component_type = "UIWindowComponent"
            
            # 创建组件数据
            component_data = {
                "name": entity.name,
                "type": component_type,
                "position": ui_comp.position,
                "size": ui_comp.size,
                "text": ui_comp.text,
                "visible": ui_comp.visible,
                "color": ui_comp.color,
                "font_size": ui_comp.font_size,
                "z_index": ui_comp.z_index
            }
            
            # 添加特定组件的属性
            if component_type == "UIButtonComponent":
                component_data["normal_color"] = ui_comp.normal_color
                component_data["hover_color"] = ui_comp.hover_color
                component_data["pressed_color"] = ui_comp.pressed_color
            elif component_type == "UISliderComponent":
                component_data["min_value"] = ui_comp.min_value
                component_data["max_value"] = ui_comp.max_value
                component_data["value"] = ui_comp.value
            
            layout_data.append(component_data)
        
        # 保存到文件
        os.makedirs("assets/ui", exist_ok=True)
        with open(f"assets/ui/{layout_name}.json", "w") as f:
            json.dump(layout_data, f, indent=4)
        
        print(f"UI布局已保存到 assets/ui/{layout_name}.json")
        
        # 关闭对话框
        self.close_save_dialog()
    
    def close_save_dialog(self):
        """关闭保存对话框"""
        dialog_entities = [e for e in self.entity_manager.entities.values() 
                          if e.name.startswith("SaveDialog_")]
        for entity in dialog_entities:
            self.entity_manager.remove_entity(entity.id)
    
    def load_ui_layout(self, entity=None):
        """从文件加载UI布局"""
        # 显示加载对话框
        self.show_load_dialog()
    
    def show_load_dialog(self):
        """显示加载对话框"""
        # 清除旧的对话框
        dialog_entities = [e for e in self.entity_manager.entities.values() 
                          if e.name.startswith("LoadDialog_")]
        for entity in dialog_entities:
            self.entity_manager.remove_entity(entity.id)
        
        # 创建对话框面板
        dialog_panel = self.entity_manager.create_entity("LoadDialog_Panel")
        panel_comp = UIPanelComponent(position=(self.width/2 - 150, self.height/2 - 150), size=(300, 300), text="加载布局")
        panel_comp.background_color = (60, 60, 60, 220)
        panel_comp.visible = self.active
        dialog_panel.add_component(ComponentType.UI, panel_comp)
        
        # 获取可用布局列表
        layouts = self.get_available_layouts()
        
        if not layouts:
            # 显示无布局消息
            no_layouts_label = self.ui_system.create_label("没有可用的布局文件", 
                                                         (self.width/2 - 140, self.height/2 - 100))
            no_layouts_label.get_component(ComponentType.UI).visible = self.active
            no_layouts_label.name = "LoadDialog_NoLayouts"
        else:
            # 添加布局列表
            y_offset = -100
            for layout_name in layouts:
                layout_btn = self.ui_system.create_button(layout_name, 
                                                        (self.width/2 - 140, self.height/2 + y_offset), (280, 30),
                                                        lambda e, name=layout_name: self.do_load_layout(name))
                layout_btn.get_component(ComponentType.UI).visible = self.active
                layout_btn.name = f"LoadDialog_Layout_{layout_name}"
                y_offset += 40
        
        # 添加取消按钮
        cancel_btn = self.ui_system.create_button("取消", 
                                                (self.width/2 - 70, self.height/2 + 120), (140, 30),
                                                lambda e: self.close_load_dialog())
        cancel_btn.get_component(ComponentType.UI).visible = self.active
        cancel_btn.name = "LoadDialog_CancelBtn"
    
    def get_available_layouts(self):
        """获取可用的布局列表"""
        layouts = []
        try:
            if not os.path.exists("assets/ui"):
                return layouts
            
            for file in os.listdir("assets/ui"):
                if file.endswith(".json"):
                    layouts.append(os.path.splitext(file)[0])
            
            return layouts
        except Exception as e:
            print(f"获取布局列表时出错: {e}")
            return layouts
    
    def do_load_layout(self, layout_name):
        """执行加载布局操作"""
        try:
            # 检查文件是否存在
            layout_path = f"assets/ui/{layout_name}.json"
            if not os.path.exists(layout_path):
                print(f"布局文件不存在: {layout_path}")
                return
            
            # 加载布局数据
            with open(layout_path, "r") as f:
                layout_data = json.load(f)
            
            # 清除现有UI元素
            ui_entities = self.entity_manager.get_entities_with_components(ComponentType.UI)
            ui_entities = [e for e in ui_entities if e not in self.editor_ui.values() and e not in self.palette_items
                          and not e.name.startswith("Property_") and not e.name.startswith("Hierarchy_")
                          and not e.name.startswith("AddMenu_") and not e.name.startswith("SaveDialog_")
                          and not e.name.startswith("LoadDialog_")]
            
            for entity in ui_entities:
                self.entity_manager.remove_entity(entity.id)
            
            # 创建UI元素
            for component_data in layout_data:
                # 创建实体
                entity = self.entity_manager.create_entity(component_data["name"])
                
                # 创建组件
                component_type = component_data["type"]
                if component_type == "UIButtonComponent":
                    ui_comp = UIButtonComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                    if "normal_color" in component_data:
                        ui_comp.normal_color = component_data["normal_color"]
                    if "hover_color" in component_data:
                        ui_comp.hover_color = component_data["hover_color"]
                    if "pressed_color" in component_data:
                        ui_comp.pressed_color = component_data["pressed_color"]
                elif component_type == "UILabelComponent":
                    ui_comp = UILabelComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                elif component_type == "UIPanelComponent":
                    ui_comp = UIPanelComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                elif component_type == "UISliderComponent":
                    ui_comp = UISliderComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                    if "min_value" in component_data:
                        ui_comp.min_value = component_data["min_value"]
                    if "max_value" in component_data:
                        ui_comp.max_value = component_data["max_value"]
                    if "value" in component_data:
                        ui_comp.value = component_data["value"]
                elif component_type == "UITextBoxComponent":
                    ui_comp = UITextBoxComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                elif component_type == "UICheckBoxComponent":
                    ui_comp = UICheckBoxComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                elif component_type == "UIDropdownComponent":
                    ui_comp = UIDropdownComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                elif component_type == "UIWindowComponent":
                    ui_comp = UIWindowComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        title=component_data["text"],
                        visible=component_data["visible"]
                    )
                else:
                    ui_comp = UIComponent(
                        position=component_data["position"],
                        size=component_data["size"],
                        text=component_data["text"],
                        visible=component_data["visible"]
                    )
                
                # 设置其他属性
                ui_comp.color = component_data["color"]
                ui_comp.font_size = component_data["font_size"]
                ui_comp.z_index = component_data["z_index"]
                
                # 添加组件到实体
                entity.add_component(ComponentType.UI, ui_comp)
            
            # 更新层级面板
            self.update_hierarchy_panel()
            
            print(f"UI布局已加载: {layout_name}")
            
            # 关闭对话框
            self.close_load_dialog()
        except Exception as e:
            print(f"加载UI布局时出错: {e}")
    
    def close_load_dialog(self):
        """关闭加载对话框"""
        dialog_entities = [e for e in self.entity_manager.entities.values() 
                          if e.name.startswith("LoadDialog_")]
        for entity in dialog_entities:
            self.entity_manager.remove_entity(entity.id)
    
    def delete_selected_element(self):
        """删除选中的元素"""
        if not self.selected_element:
            return
        
        self.entity_manager.remove_entity(self.selected_element.id)
        self.selected_element = None
        self.update_property_panel()
        self.update_hierarchy_panel()
    
    def paste_element(self):
        """粘贴元素"""
        # 这个功能需要先复制一个元素，这里简化为直接复制选中的元素
        if self.selected_element:
            self.duplicate_element()
    
    def move_element(self, dx, dy):
        """移动元素"""
        if not self.selected_element:
            return
        
        ui_comp = self.selected_element.get_component(ComponentType.UI)
        ui_comp.position = (ui_comp.position[0] + dx, ui_comp.position[1] + dy)
        self.update_property_panel()
    
    def toggle_help_panel(self, entity=None):
        """切换帮助面板显示状态"""
        help_panel = self.editor_ui["help_panel"]
        help_visible = not help_panel.get_component(ComponentType.UI).visible
        
        # 设置帮助面板及其内容的可见性
        for entity_id, entity in self.editor_ui.items():
            if entity_id.startswith("help_") or entity_id == "help_panel":
                entity.get_component(ComponentType.UI).visible = help_visible and self.active 