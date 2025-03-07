#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器主窗口
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QDockWidget, QMenuBar, QMenu,
    QAction, QMessageBox, QFileDialog, QLabel, QVBoxLayout
)
from PyQt5.QtCore import Qt

from editor.ui.panels.scene_panel import ScenePanel
from editor.ui.panels.property_panel import PropertyPanel
from editor.ui.panels.hierarchy_panel import HierarchyPanel
from editor.ui.panels.asset_browser import AssetBrowser


class MainWindow(QMainWindow):
    """编辑器主窗口类"""
    
    def __init__(self, width, height):
        """初始化主窗口
        
        Args:
            width (int): 窗口宽度
            height (int): 窗口高度
        """
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("PyCraft Editor")
        self.resize(width, height)
        
        # 初始化UI
        self._init_ui()
        
        # 当前项目路径
        self.current_project = None
        # 当前场景路径
        self.current_scene = None
    
    def _init_ui(self):
        """初始化UI"""
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建场景面板，并将其设置为中央窗口部件
        self.scene_panel = ScenePanel()
        self.setCentralWidget(self.scene_panel)
        
        # 设置场景面板为焦点
        self.scene_panel.setFocus()
        
        # 创建层级面板
        self.hierarchy_panel = HierarchyPanel()
        hierarchy_dock = QDockWidget("层级视图", self)
        hierarchy_dock.setWidget(self.hierarchy_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, hierarchy_dock)
        
        # 创建属性面板
        self.property_panel = PropertyPanel()
        property_dock = QDockWidget("属性", self)
        property_dock.setWidget(self.property_panel)
        self.addDockWidget(Qt.RightDockWidgetArea, property_dock)
        
        # 创建资源浏览器
        self.asset_browser = AssetBrowser()
        asset_dock = QDockWidget("资源", self)
        asset_dock.setWidget(self.asset_browser)
        self.addDockWidget(Qt.BottomDockWidgetArea, asset_dock)
        
        # 添加状态栏信息
        self.statusBar().showMessage("准备就绪")
        
        # 添加WASD控制提示
        control_label = QLabel("使用WASD键移动，空格键上升，Ctrl键下降")
        self.statusBar().addPermanentWidget(control_label)
        
        # 添加世界视窗模式提示
        world_view_label = QLabel("右键点击进入世界视窗模式，ESC退出")
        self.statusBar().addPermanentWidget(world_view_label)
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 新建项目
        new_project_action = QAction("新建项目", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._on_new_project)
        file_menu.addAction(new_project_action)
        
        # 打开项目
        open_project_action = QAction("打开项目", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.triggered.connect(self._on_open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        # 保存场景
        save_scene_action = QAction("保存场景", self)
        save_scene_action.setShortcut("Ctrl+S")
        save_scene_action.triggered.connect(self._on_save_scene)
        file_menu.addAction(save_scene_action)
        
        # 另存为场景
        save_scene_as_action = QAction("场景另存为", self)
        save_scene_as_action.setShortcut("Ctrl+Shift+S")
        save_scene_as_action.triggered.connect(self._on_save_scene_as)
        file_menu.addAction(save_scene_as_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        # 撤销
        undo_action = QAction("撤销", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        # 重做
        redo_action = QAction("重做", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)
    
    def open_project(self, project_path):
        """打开项目
        
        Args:
            project_path (str): 项目路径
        """
        self.current_project = project_path
        # TODO: 加载项目配置和资源
        self.asset_browser.set_root_path(project_path)
    
    def load_scene(self, scene_path):
        """加载场景
        
        Args:
            scene_path (str): 场景文件路径
        """
        self.current_scene = scene_path
        # TODO: 加载场景到场景面板
        self.scene_panel.load_scene(scene_path)
    
    def _on_new_project(self):
        """新建项目"""
        # TODO: 实现新建项目功能
        QMessageBox.information(self, "提示", "新建项目功能尚未实现")
    
    def _on_open_project(self):
        """打开项目"""
        project_path = QFileDialog.getExistingDirectory(
            self,
            "选择项目目录",
            "",
            QFileDialog.ShowDirsOnly
        )
        if project_path:
            self.open_project(project_path)
    
    def _on_save_scene(self):
        """保存场景"""
        if not self.current_scene:
            self._on_save_scene_as()
        else:
            # TODO: 保存场景
            QMessageBox.information(self, "提示", "保存场景功能尚未实现")
    
    def _on_save_scene_as(self):
        """场景另存为"""
        scene_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存场景",
            "",
            "场景文件 (*.scene);;所有文件 (*.*)"
        )
        if scene_path:
            self.current_scene = scene_path
            self._on_save_scene()
    
    def _on_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 PyCraft Editor",
            "PyCraft Editor\n\n"
            "一个基于Python的3D游戏引擎编辑器\n"
            "版本: 0.1.0\n"
            "作者: Your Name"
        )