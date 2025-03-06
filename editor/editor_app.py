#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器应用程序类
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox, QStyleFactory, QProgressDialog
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize

# 引入主窗口类
from editor.ui.main_window import MainWindow


class EditorApp:
    """编辑器应用程序类"""
    
    def __init__(self, width=1920, height=1080, debug=False):
        """初始化编辑器应用程序
        
        Args:
            width (int): 窗口宽度
            height (int): 窗口高度
            debug (bool): 是否启用调试模式
        """
        self.width = width
        self.height = height
        self.debug = debug
        
        # 确保应用只有一个实例
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)
        
        # 设置应用程序图标
        self._set_application_icon()
        
        # 应用深色主题
        self._apply_dark_theme()
        
        # 创建加载进度对话框
        self._show_loading_progress()
        
        # 创建主窗口
        self.main_window = MainWindow(width, height)
        
        # 设置窗口图标
        self.main_window.setWindowIcon(QIcon(self._get_resource_path("icons/app_icon.png")))
        
        if debug:
            print("编辑器启动于调试模式")
        
        # 显示欢迎信息
        QTimer.singleShot(500, self._show_welcome_message)
    
    def _set_application_icon(self):
        """设置应用程序图标"""
        icon_path = self._get_resource_path("icons/app_icon.png")
        # 如果图标文件不存在，尝试创建默认图标
        if not os.path.exists(icon_path):
            self._create_default_resources()
        
        if os.path.exists(icon_path):
            self.app.setWindowIcon(QIcon(icon_path))
    
    def _get_resource_path(self, relative_path):
        """获取资源路径
        
        Args:
            relative_path (str): 相对路径
            
        Returns:
            str: 绝对路径
        """
        # 获取编辑器目录
        editor_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 返回资源绝对路径
        resource_path = os.path.join(editor_dir, "resources", relative_path)
        # 确保目录存在
        os.makedirs(os.path.dirname(resource_path), exist_ok=True)
        return resource_path
    
    def _create_default_resources(self):
        """创建默认资源文件"""
        # 创建资源目录
        icons_dir = os.path.dirname(self._get_resource_path("icons/app_icon.png"))
        os.makedirs(icons_dir, exist_ok=True)
        
        # 这里可以生成默认图标，但为简单起见，我们只创建目录
        if self.debug:
            print(f"已创建资源目录: {icons_dir}")
    
    def _apply_dark_theme(self):
        """应用深色主题样式"""
        # 设置Fusion风格，这是跨平台的现代风格
        self.app.setStyle(QStyleFactory.create("Fusion"))
        
        # 创建深色调色板
        dark_palette = QPalette()
        
        # 设置窗口背景色
        dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
        dark_palette.setColor(QPalette.WindowText, QColor(212, 212, 212))
        
        # 设置按钮和控件颜色
        dark_palette.setColor(QPalette.Button, QColor(60, 60, 60))
        dark_palette.setColor(QPalette.ButtonText, QColor(212, 212, 212))
        
        # 设置高亮和选择区域颜色
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # 设置工具提示颜色
        dark_palette.setColor(QPalette.ToolTipBase, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.ToolTipText, QColor(212, 212, 212))
        
        # 设置文本颜色
        dark_palette.setColor(QPalette.Text, QColor(212, 212, 212))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        
        # 设置链接颜色
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        
        # 设置面板颜色
        dark_palette.setColor(QPalette.Base, QColor(32, 32, 32))
        dark_palette.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        
        # 设置禁用状态颜色
        dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
        dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))
        
        # 应用调色板
        self.app.setPalette(dark_palette)
        
        # 设置样式表，进一步美化控件
        stylesheet = """
            QToolTip { 
                color: #d4d4d4; 
                background-color: #232323; 
                border: 1px solid #3a3a3a; 
                border-radius: 3px;
                padding: 5px;
            }
            
            QDockWidget::title {
                background: linear-gradient(#3a3a3a, #303030);
                color: #d4d4d4;
                padding: 6px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                font-weight: bold;
            }
            
            QMenuBar {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border-bottom: 1px solid #1a1a1a;
            }
            
            QMenuBar::item:selected {
                background-color: #3a3a3a;
                border-radius: 2px;
            }
            
            QMenu {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #1a1a1a;
                padding: 2px;
            }
            
            QMenu::item:selected {
                background-color: #3a3a3a;
                border-radius: 2px;
            }
            
            QStatusBar {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border-top: 1px solid #1a1a1a;
            }
            
            QTreeView {
                background-color: #282828;
                alternate-background-color: #303030;
                color: #d4d4d4;
                border: 1px solid #1a1a1a;
            }
            
            QTreeView::item:selected {
                background-color: #42648e;
                color: #ffffff;
            }
            
            QHeaderView::section {
                background-color: #3a3a3a;
                color: #d4d4d4;
                border: 1px solid #232323;
                padding: 4px;
            }
            
            QScrollBar:vertical {
                background-color: #282828;
                width: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #505050;
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #606060;
            }
            
            QScrollBar:horizontal {
                background-color: #282828;
                height: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #505050;
                min-width: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #606060;
            }
            
            QLineEdit, QTextEdit, QPlainTextEdit {
                background-color: #282828;
                color: #d4d4d4;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 3px 5px;
                selection-background-color: #42648e;
            }
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
                border: 1px solid #6090d0;
            }
            
            QPushButton {
                background-color: #3a3a3a;
                color: #d4d4d4;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 5px 15px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #505050;
                border: 1px solid #6090d0;
            }
            
            QPushButton:pressed {
                background-color: #2a5284;
            }
            
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #707070;
                border: 1px solid #3a3a3a;
            }
            
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #282828;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #d4d4d4;
                padding: 6px 12px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                margin-right: 1px;
                border: 1px solid #1a1a1a;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: #3a3a3a;
                border-bottom: 2px solid #42648e;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #333333;
            }
            
            QComboBox {
                background-color: #3a3a3a;
                color: #d4d4d4;
                border: 1px solid #505050;
                border-radius: 3px;
                padding: 2px 5px;
                min-height: 20px;
            }
            
            QComboBox:hover {
                border: 1px solid #6090d0;
            }
            
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left: 1px solid #505050;
            }
            
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #d4d4d4;
                border: 1px solid #505050;
                selection-background-color: #42648e;
                selection-color: #ffffff;
            }
            
            QCheckBox, QRadioButton {
                color: #d4d4d4;
                spacing: 5px;
            }
            
            QGroupBox {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                margin-top: 10px;
                font-weight: bold;
                color: #d4d4d4;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #282828;
                text-align: center;
                color: #d4d4d4;
            }
            
            QProgressBar::chunk {
                background-color: #42648e;
                border-radius: 2px;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #3a3a3a;
                height: 8px;
                background: #282828;
                margin: 2px 0;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #6090d0;
                border: 1px solid #6090d0;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #7aa8e0;
                border: 1px solid #7aa8e0;
            }
        """
        self.app.setStyleSheet(stylesheet)
        
    def _show_loading_progress(self):
        """显示加载进度对话框"""
        # 创建进度对话框
        progress = QProgressDialog("正在加载编辑器组件...", None, 0, 100)
        progress.setWindowTitle("PyCraft Editor")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)  # 立即显示
        progress.setAutoClose(True)
        progress.setWindowFlag(Qt.FramelessWindowHint)  # 无边框
        
        # 设置样式
        progress.setStyleSheet("""
            QProgressDialog {
                background-color: #2d2d2d;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
            QLabel {
                color: #d4d4d4;
                font-weight: bold;
                margin: 10px;
            }
        """)
        
        # 显示进度
        for i in range(1, 101):
            progress.setValue(i)
            if i < 20:
                progress.setLabelText("初始化编辑器环境...")
            elif i < 40:
                progress.setLabelText("加载核心模块...")
            elif i < 60:
                progress.setLabelText("准备渲染系统...")
            elif i < 80:
                progress.setLabelText("加载用户界面...")
            else:
                progress.setLabelText("完成加载...")
            
            # 模拟加载延迟
            QTimer.singleShot(20, lambda: None)
            self.app.processEvents()
    
    def _show_welcome_message(self):
        """显示欢迎信息"""
        if not self.debug:  # 在调试模式下不显示欢迎信息
            QMessageBox.information(
                self.main_window,
                "欢迎使用 PyCraft 编辑器",
                "<h3>欢迎使用 PyCraft 编辑器！</h3>"
                "<p>已创建一个初始的3D场景，您可以使用以下控制方式浏览场景：</p>"
                "<ul>"
                "<li><b>WASD 键</b>：前后左右移动</li>"
                "<li><b>空格键</b>：上升</li>"
                "<li><b>Ctrl 键</b>：下降</li>"
                "<li><b>鼠标拖动</b>：旋转视角</li>"
                "</ul>"
                "<p>请点击场景视图以获取焦点，然后开始操作。</p>"
                "<p><i>提示：可以在菜单 > 帮助 > 快捷键查看更多操作方式</i></p>"
            )
    
    def open_project(self, project_path):
        """打开项目
        
        Args:
            project_path (str): 项目路径
        """
        if self.debug:
            print(f"打开项目: {project_path}")
        self.main_window.open_project(project_path)
        # 设置窗口标题以包含项目名称
        project_name = os.path.basename(project_path)
        self.main_window.setWindowTitle(f"PyCraft Editor - {project_name}")
    
    def load_scene(self, scene_path):
        """加载场景
        
        Args:
            scene_path (str): 场景文件路径
        """
        if self.debug:
            print(f"加载场景: {scene_path}")
        self.main_window.load_scene(scene_path)
        # 更新窗口标题以包含场景名称
        scene_name = os.path.basename(scene_path)
        current_title = self.main_window.windowTitle()
        if " - " in current_title:
            project_part = current_title.split(" - ")[1]
            self.main_window.setWindowTitle(f"PyCraft Editor - {project_part} - {scene_name}")
        else:
            self.main_window.setWindowTitle(f"PyCraft Editor - {scene_name}")
    
    def run(self):
        """运行编辑器"""
        # 显示主窗口
        self.main_window.show()
        
        # 设置焦点到场景视图
        if hasattr(self.main_window, "scene_panel"):
            self.main_window.scene_panel.setFocus()
        
        # 运行Qt应用程序
        return self.app.exec_()