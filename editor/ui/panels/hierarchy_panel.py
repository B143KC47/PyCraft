#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
层级面板类
"""

import os
import uuid
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, 
    QHeaderView, QMenu, QAction, QInputDialog, QMessageBox,
    QToolBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QColor, QBrush, QFont


class EntityTreeItem(QTreeWidgetItem):
    """实体树项目类"""
    
    def __init__(self, entity, parent=None):
        """初始化实体树项
        
        Args:
            entity: 实体对象
            parent: 父项目
        """
        super().__init__(parent)
        
        self.entity_id = entity.id if hasattr(entity, "id") else str(uuid.uuid4())
        self.entity_name = entity.name if hasattr(entity, "name") else "Entity"
        self.entity = entity
        
        # 设置显示名称
        self.setText(0, self.entity_name)
        
        # 设置图标（根据实体类型或组件设置不同图标）
        self.setIcon(0, self._get_entity_icon(entity))
        
        # 设置工具提示
        self.setToolTip(0, f"ID: {self.entity_id}\n类型: {self._get_entity_type(entity)}")
        
        # 设置实体是否激活的样式
        if hasattr(entity, "enabled") and not entity.enabled:
            # 使用灰色文本来表示禁用的实体
            self.setForeground(0, QBrush(QColor(150, 150, 150)))
            # 设置斜体字
            font = self.font(0)
            font.setItalic(True)
            self.setFont(0, font)
    
    def _get_entity_icon(self, entity):
        """获取实体图标
        
        Args:
            entity: 实体对象
            
        Returns:
            QIcon: 实体图标
        """
        # 根据实体类型或组件设置不同图标
        # 这里可以根据实际需求扩展
        if hasattr(entity, "components"):
            components = entity.get_components() if callable(getattr(entity, "get_components", None)) else []
            component_types = [comp.__class__.__name__ for comp in components]
            
            # 根据组件类型返回对应图标
            if "CameraComponent" in component_types:
                return QIcon("resources/icons/camera.png")
            elif "LightComponent" in component_types:
                return QIcon("resources/icons/light.png")
            elif "MeshComponent" in component_types:
                return QIcon("resources/icons/mesh.png")
            elif "AudioComponent" in component_types:
                return QIcon("resources/icons/audio.png")
            elif "ScriptComponent" in component_types:
                return QIcon("resources/icons/script.png")
        
        # 默认图标
        return QIcon("resources/icons/entity.png")
    
    def _get_entity_type(self, entity):
        """获取实体类型描述
        
        Args:
            entity: 实体对象
            
        Returns:
            str: 实体类型描述
        """
        if hasattr(entity, "components"):
            components = entity.get_components() if callable(getattr(entity, "get_components", None)) else []
            if components:
                return ", ".join([comp.__class__.__name__ for comp in components])
        
        return entity.__class__.__name__


class HierarchyPanel(QWidget):
    """层级面板类"""
    
    # 定义信号
    entity_selected = pyqtSignal(object)  # 实体选择信号
    scene_changed = pyqtSignal()  # 场景变更信号
    
    def __init__(self):
        """初始化层级面板"""
        super().__init__()
        
        # 创建布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # 创建工具栏
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        layout.addWidget(self.toolbar)
        
        # 添加工具栏按钮
        self.add_entity_action = QAction("添加实体", self)
        self.add_entity_action.setIcon(QIcon("resources/icons/add.png"))
        self.add_entity_action.triggered.connect(self._add_entity)
        self.toolbar.addAction(self.add_entity_action)
        
        self.delete_entity_action = QAction("删除实体", self)
        self.delete_entity_action.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_entity_action.triggered.connect(self._delete_entity)
        self.toolbar.addAction(self.delete_entity_action)
        
        self.refresh_action = QAction("刷新", self)
        self.refresh_action.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_action.triggered.connect(self.refresh_tree)
        self.toolbar.addAction(self.refresh_action)
        
        # 创建树形视图
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("场景层级")
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_widget.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree_widget.setDragDropMode(QTreeWidget.InternalMove)
        
        # 设置标题栏格式
        header = self.tree_widget.header()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # 连接信号
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.tree_widget)
        
        # 当前场景
        self.current_scene = None
        
        # 实体到树项目的映射
        self.entity_items = {}
    
    def load_scene(self, scene):
        """加载场景
        
        Args:
            scene: 场景对象
        """
        self.current_scene = scene
        self.refresh_tree()
    
    def refresh_tree(self):
        """刷新实体树"""
        # 清空树
        self.tree_widget.clear()
        self.entity_items = {}
        
        if self.current_scene:
            # 获取场景中的根实体
            root_entities = []
            
            # 尝试不同的方法获取根实体
            if hasattr(self.current_scene, "root_entities"):
                # 直接访问根实体属性
                root_entities = self.current_scene.root_entities
            elif hasattr(self.current_scene, "get_root_entities") and callable(self.current_scene.get_root_entities):
                # 调用获取根实体的方法
                root_entities = self.current_scene.get_root_entities()
            elif hasattr(self.current_scene, "get_entities") and callable(self.current_scene.get_entities):
                # 获取所有实体，然后筛选出根实体
                all_entities = self.current_scene.get_entities()
                root_entities = [e for e in all_entities if not hasattr(e, "parent") or e.parent is None]
            
            # 递归添加实体
            for entity in root_entities:
                self._add_entity_to_tree(entity, None)
            
            # 展开第一级节点
            self.tree_widget.expandToDepth(0)
    
    def _add_entity_to_tree(self, entity, parent_item):
        """递归添加实体到树
        
        Args:
            entity: 实体对象
            parent_item: 父树项
            
        Returns:
            EntityTreeItem: 创建的树项
        """
        # 创建树项
        item = EntityTreeItem(entity, parent_item if parent_item else self.tree_widget)
        
        # 保存实体到树项的映射
        self.entity_items[entity.id if hasattr(entity, "id") else id(entity)] = item
        
        # 添加子实体
        if hasattr(entity, "children"):
            for child in entity.children:
                self._add_entity_to_tree(child, item)
        
        return item
    
    def select_entity(self, entity_id):
        """选择指定实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            bool: 是否成功选择
        """
        if entity_id in self.entity_items:
            item = self.entity_items[entity_id]
            self.tree_widget.setCurrentItem(item)
            return True
        return False
    
    def get_selected_entities(self):
        """获取当前选中的实体列表
        
        Returns:
            list: 实体列表
        """
        selected_items = self.tree_widget.selectedItems()
        return [item.entity for item in selected_items]
    
    def _on_selection_changed(self):
        """选择改变时的处理函数"""
        selected_entities = self.get_selected_entities()
        # 发射实体选择信号
        if selected_entities:
            self.entity_selected.emit(selected_entities[0] if len(selected_entities) == 1 else selected_entities)
    
    def _on_item_double_clicked(self, item, column):
        """项目双击事件处理
        
        Args:
            item: 被双击的项目
            column: 列号
        """
        # 双击时可以重命名实体
        self._rename_entity(item)
    
    def _show_context_menu(self, position):
        """显示上下文菜单
        
        Args:
            position: 鼠标位置
        """
        menu = QMenu()
        
        # 获取选中的项目
        selected_items = self.tree_widget.selectedItems()
        
        if selected_items:
            # 单选时的菜单项
            if len(selected_items) == 1:
                item = selected_items[0]
                
                # 添加子实体选项
                add_child_action = QAction("添加子实体", self)
                add_child_action.triggered.connect(lambda: self._add_child_entity(item))
                menu.addAction(add_child_action)
                
                # 重命名选项
                rename_action = QAction("重命名", self)
                rename_action.triggered.connect(lambda: self._rename_entity(item))
                menu.addAction(rename_action)
                
                # 激活/禁用选项
                if hasattr(item.entity, "enabled"):
                    toggle_action = QAction("禁用" if item.entity.enabled else "激活", self)
                    toggle_action.triggered.connect(lambda: self._toggle_entity_state(item))
                    menu.addAction(toggle_action)
                
                # 添加分隔线
                menu.addSeparator()
            
            # 删除选项（单选和多选都有）
            delete_action = QAction(f"删除选中的实体", self)
            delete_action.triggered.connect(self._delete_entity)
            menu.addAction(delete_action)
        else:
            # 未选中任何项目时的菜单
            add_entity_action = QAction("添加实体", self)
            add_entity_action.triggered.connect(self._add_entity)
            menu.addAction(add_entity_action)
        
        if menu.actions():
            menu.exec_(self.tree_widget.viewport().mapToGlobal(position))
    
    def _add_entity(self):
        """添加根实体"""
        if not self.current_scene:
            return
            
        # 获取实体名称
        name, ok = QInputDialog.getText(self, "添加实体", "请输入实体名称:", text="New Entity")
        if ok and name:
            try:
                # 创建实体
                if hasattr(self.current_scene, "create_entity") and callable(self.current_scene.create_entity):
                    entity = self.current_scene.create_entity(name)
                    # 刷新树
                    self.refresh_tree()
                    # 选择新创建的实体
                    if entity.id in self.entity_items:
                        self.tree_widget.setCurrentItem(self.entity_items[entity.id])
                    
                    # 发射场景变更信号
                    self.scene_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建实体: {str(e)}")
    
    def _add_child_entity(self, parent_item):
        """添加子实体
        
        Args:
            parent_item: 父项目
        """
        if not self.current_scene or not parent_item or not hasattr(parent_item, "entity"):
            return
            
        # 获取实体名称
        name, ok = QInputDialog.getText(self, "添加子实体", "请输入实体名称:", text="Child Entity")
        if ok and name:
            try:
                parent_entity = parent_item.entity
                
                # 创建子实体
                if hasattr(self.current_scene, "create_entity") and callable(self.current_scene.create_entity):
                    child_entity = self.current_scene.create_entity(name)
                    
                    # 设置父子关系
                    if hasattr(parent_entity, "add_child") and callable(parent_entity.add_child):
                        parent_entity.add_child(child_entity)
                    
                    # 刷新树
                    self.refresh_tree()
                    # 选择新创建的实体
                    if child_entity.id in self.entity_items:
                        self.tree_widget.setCurrentItem(self.entity_items[child_entity.id])
                    
                    # 发射场景变更信号
                    self.scene_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建子实体: {str(e)}")
    
    def _delete_entity(self):
        """删除选中的实体"""
        if not self.current_scene:
            return
        
        selected_items = self.tree_widget.selectedItems()
        if not selected_items:
            return
        
        # 确认删除
        message = f"确定要删除选中的 {len(selected_items)} 个实体吗？此操作不可撤销。"
        response = QMessageBox.question(
            self, "确认删除", message, QMessageBox.Yes | QMessageBox.No
        )
        
        if response == QMessageBox.Yes:
            try:
                # 先收集要删除的实体ID，避免在循环中修改
                entity_ids = [item.entity_id for item in selected_items]
                
                for entity_id in entity_ids:
                    # 从场景中删除实体
                    if hasattr(self.current_scene, "remove_entity") and callable(self.current_scene.remove_entity):
                        entity = self.current_scene.get_entity(entity_id)
                        if entity:
                            self.current_scene.remove_entity(entity)
                
                # 刷新树
                self.refresh_tree()
                
                # 发射场景变更信号
                self.scene_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "删除错误", f"无法删除实体: {str(e)}")
    
    def _rename_entity(self, item):
        """重命名实体
        
        Args:
            item: 要重命名的项目
        """
        if not item or not hasattr(item, "entity"):
            return
            
        # 获取新名称
        old_name = item.entity_name
        new_name, ok = QInputDialog.getText(
            self, "重命名实体", "请输入新名称:", text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            try:
                # 设置实体名称
                item.entity.name = new_name
                # 更新树项目文本
                item.setText(0, new_name)
                item.entity_name = new_name
                
                # 发射场景变更信号
                self.scene_changed.emit()
            except Exception as e:
                QMessageBox.warning(self, "重命名错误", f"无法重命名实体: {str(e)}")
    
    def _toggle_entity_state(self, item):
        """切换实体激活状态
        
        Args:
            item: 实体项目
        """
        if not item or not hasattr(item, "entity") or not hasattr(item.entity, "enabled"):
            return
            
        try:
            # 切换状态
            item.entity.enabled = not item.entity.enabled
            
            # 更新样式
            if not item.entity.enabled:
                item.setForeground(0, QBrush(QColor(150, 150, 150)))
                font = item.font(0)
                font.setItalic(True)
                item.setFont(0, font)
            else:
                item.setForeground(0, QBrush(QColor(0, 0, 0)))
                font = item.font(0)
                font.setItalic(False)
                item.setFont(0, font)
            
            # 发射场景变更信号
            self.scene_changed.emit()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法切换实体状态: {str(e)}")