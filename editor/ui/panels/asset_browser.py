#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
资源浏览器面板类
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QFileSystemModel,
    QMenu, QAction, QToolBar, QSplitter, QLabel, 
    QFileIconProvider, QFileDialog, QInputDialog, 
    QMessageBox, QListView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QDir, QSize, QModelIndex, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QImage


class CustomFileIconProvider(QFileIconProvider):
    """自定义文件图标提供器"""
    
    def __init__(self):
        super().__init__()
        # 自定义图标映射
        self.icon_map = {
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".bmp": "image",
            ".obj": "model",
            ".fbx": "model",
            ".gltf": "model",
            ".wav": "audio",
            ".mp3": "audio",
            ".ogg": "audio",
            ".scene": "scene",
            ".py": "script"
        }
        
        # 加载图标
        self.folder_icon = QIcon("resources/icons/folder.png")
        self.image_icon = QIcon("resources/icons/image.png")
        self.model_icon = QIcon("resources/icons/model.png")
        self.audio_icon = QIcon("resources/icons/audio.png")
        self.scene_icon = QIcon("resources/icons/scene.png")
        self.script_icon = QIcon("resources/icons/script.png")
        self.file_icon = QIcon("resources/icons/file.png")

    def icon(self, fileInfo):
        # 如果是目录
        if fileInfo.isDir():
            return self.folder_icon if self.folder_icon else super().icon(fileInfo)
        
        # 根据文件扩展名获取图标
        ext = os.path.splitext(fileInfo.fileName())[1].lower()
        icon_type = self.icon_map.get(ext)
        
        if icon_type == "image" and self.image_icon:
            return self.image_icon
        elif icon_type == "model" and self.model_icon:
            return self.model_icon
        elif icon_type == "audio" and self.audio_icon:
            return self.audio_icon
        elif icon_type == "scene" and self.scene_icon:
            return self.scene_icon
        elif icon_type == "script" and self.script_icon:
            return self.script_icon
        
        # 默认图标
        return self.file_icon if self.file_icon else super().icon(fileInfo)


class AssetBrowser(QWidget):
    """资源浏览器面板类"""
    
    # 定义信号
    asset_selected = pyqtSignal(str)
    asset_double_clicked = pyqtSignal(str)
    
    def __init__(self):
        """初始化资源浏览器"""
        super().__init__()
        
        # 创建布局
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # 创建工具栏
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.main_layout.addWidget(self.toolbar)
        
        # 添加工具栏按钮
        self.new_folder_action = QAction("新建文件夹", self)
        self.new_folder_action.setIcon(QIcon("resources/icons/new_folder.png"))
        self.new_folder_action.triggered.connect(self._create_new_folder)
        self.toolbar.addAction(self.new_folder_action)
        
        self.import_action = QAction("导入资源", self)
        self.import_action.setIcon(QIcon("resources/icons/import.png"))
        self.import_action.triggered.connect(self._import_asset)
        self.toolbar.addAction(self.import_action)
        
        self.refresh_action = QAction("刷新", self)
        self.refresh_action.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_action.triggered.connect(self._refresh_view)
        self.toolbar.addAction(self.refresh_action)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)
        
        # 创建文件系统模型
        self.model = QFileSystemModel()
        self.model.setReadOnly(False)
        
        # 设置自定义图标提供器
        self.icon_provider = CustomFileIconProvider()
        self.model.setIconProvider(self.icon_provider)
        
        # 设置过滤器
        self.model.setNameFilters([
            "*.png", "*.jpg", "*.jpeg", "*.bmp",  # 图片
            "*.obj", "*.fbx", "*.gltf",           # 3D模型
            "*.wav", "*.mp3", "*.ogg",            # 音频
            "*.scene",                             # 场景文件
            "*.py"                                # 脚本文件
        ])
        self.model.setNameFilterDisables(False)
        
        # 创建树形视图
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
        self.tree_view.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        
        # 隐藏不需要的列
        self.tree_view.setColumnHidden(1, True)  # 大小
        self.tree_view.setColumnHidden(2, True)  # 类型
        self.tree_view.setColumnHidden(3, True)  # 修改日期
        
        # 选择变化时触发
        self.tree_view.selectionModel().selectionChanged.connect(self._on_selection_changed)
        # 双击时触发
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        
        self.splitter.addWidget(self.tree_view)
        
        # 创建预览面板
        self.preview_panel = QLabel("选择文件以预览")
        self.preview_panel.setAlignment(Qt.AlignCenter)
        self.preview_panel.setMinimumWidth(200)
        self.preview_panel.setStyleSheet("background-color: #1e1e1e; color: #d0d0d0; border: 1px solid #333;")
        self.splitter.addWidget(self.preview_panel)
        
        # 设置分割器比例
        self.splitter.setSizes([300, 150])
        
        # 当前路径
        self.current_path = None
    
    def set_root_path(self, path):
        """设置根路径
        
        Args:
            path (str): 资源根路径
        """
        if os.path.exists(path):
            # 设置根路径
            self.model.setRootPath(path)
            # 设置视图的根索引
            self.tree_view.setRootIndex(self.model.index(path))
            # 更新当前路径
            self.current_path = path
            # 设置列宽
            self.tree_view.setColumnWidth(0, 250)
            
    def _show_context_menu(self, position):
        """显示上下文菜单
        
        Args:
            position: 鼠标位置
        """
        menu = QMenu()
        
        # 获取选中的索引
        indexes = self.tree_view.selectedIndexes()
        if indexes and len(indexes) > 0:
            # 只使用第一列的索引
            selected_indexes = [idx for idx in indexes if idx.column() == 0]
            
            # 添加操作菜单项
            # 单个选择时的菜单项
            if len(selected_indexes) == 1:
                file_path = self.model.filePath(selected_indexes[0])
                
                # 如果是目录，添加"新建文件夹"菜单项
                if os.path.isdir(file_path):
                    new_folder_action = QAction("新建文件夹", self)
                    new_folder_action.triggered.connect(lambda: self._create_new_folder(file_path))
                    menu.addAction(new_folder_action)
                    
                    import_action = QAction("导入资源", self)
                    import_action.triggered.connect(lambda: self._import_asset(file_path))
                    menu.addAction(import_action)
                    
                    menu.addSeparator()
                
                # 添加重命名选项
                rename_action = QAction("重命名", self)
                rename_action.triggered.connect(lambda: self._rename_item(selected_indexes[0]))
                menu.addAction(rename_action)
                
                # 添加删除选项
                delete_action = QAction("删除", self)
                delete_action.triggered.connect(lambda: self._delete_items(selected_indexes))
                menu.addAction(delete_action)
            
            # 多选时的菜单项
            elif len(selected_indexes) > 1:
                delete_action = QAction(f"删除选中的 {len(selected_indexes)} 个项目", self)
                delete_action.triggered.connect(lambda: self._delete_items(selected_indexes))
                menu.addAction(delete_action)
        else:
            # 未选择文件时的菜单项
            new_folder_action = QAction("新建文件夹", self)
            new_folder_action.triggered.connect(self._create_new_folder)
            menu.addAction(new_folder_action)
            
            import_action = QAction("导入资源", self)
            import_action.triggered.connect(self._import_asset)
            menu.addAction(import_action)
            
            refresh_action = QAction("刷新", self)
            refresh_action.triggered.connect(self._refresh_view)
            menu.addAction(refresh_action)
        
        # 显示菜单
        if menu.actions():
            menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    def _create_new_folder(self, parent_path=None):
        """创建新文件夹
        
        Args:
            parent_path (str, optional): 父目录路径，如果为None则使用当前选择的目录或根目录
        """
        # 获取父目录
        if not parent_path:
            indexes = self.tree_view.selectedIndexes()
            if indexes and len(indexes) > 0:
                # 只使用第一列的索引
                selected_index = next((idx for idx in indexes if idx.column() == 0), None)
                if selected_index:
                    file_path = self.model.filePath(selected_index)
                    if os.path.isdir(file_path):
                        parent_path = file_path
            
            if not parent_path and self.current_path:
                parent_path = self.current_path
        
        if parent_path:
            # 弹出对话框获取文件夹名称
            folder_name, ok = QInputDialog.getText(
                self, "新建文件夹", "请输入文件夹名称:", text="新建文件夹"
            )
            
            if ok and folder_name:
                # 创建文件夹
                folder_path = os.path.join(parent_path, folder_name)
                try:
                    os.makedirs(folder_path, exist_ok=True)
                    
                    # 选择新创建的文件夹
                    self.tree_view.setCurrentIndex(self.model.index(folder_path))
                    
                except Exception as e:
                    QMessageBox.warning(self, "错误", f"无法创建文件夹: {str(e)}")
    
    def _import_asset(self, target_dir=None):
        """导入资源
        
        Args:
            target_dir (str, optional): 目标目录，如果为None则使用当前选择的目录或根目录
        """
        # 获取目标目录
        if not target_dir:
            indexes = self.tree_view.selectedIndexes()
            if indexes and len(indexes) > 0:
                # 只使用第一列的索引
                selected_index = next((idx for idx in indexes if idx.column() == 0), None)
                if selected_index:
                    file_path = self.model.filePath(selected_index)
                    if os.path.isdir(file_path):
                        target_dir = file_path
            
            if not target_dir and self.current_path:
                target_dir = self.current_path
        
        if target_dir:
            # 打开文件选择对话框
            file_paths, _ = QFileDialog.getOpenFileNames(
                self, 
                "选择要导入的资源", 
                "", 
                "所有支持的文件 (*.png *.jpg *.jpeg *.bmp *.obj *.fbx *.gltf *.wav *.mp3 *.ogg *.scene *.py);;"\
                "图片文件 (*.png *.jpg *.jpeg *.bmp);;"\
                "3D模型 (*.obj *.fbx *.gltf);;"\
                "音频文件 (*.wav *.mp3 *.ogg);;"\
                "场景文件 (*.scene);;"\
                "脚本文件 (*.py);;"\
                "所有文件 (*.*)"
            )
            
            if file_paths:
                # 导入所有选择的文件
                for file_path in file_paths:
                    try:
                        file_name = os.path.basename(file_path)
                        dest_path = os.path.join(target_dir, file_name)
                        
                        # 检查文件是否已存在
                        if os.path.exists(dest_path):
                            response = QMessageBox.question(
                                self, 
                                "文件已存在", 
                                f"文件 {file_name} 已存在，是否覆盖？",
                                QMessageBox.Yes | QMessageBox.No
                            )
                            
                            if response == QMessageBox.No:
                                continue
                        
                        # 复制文件
                        import shutil
                        shutil.copy2(file_path, dest_path)
                        
                    except Exception as e:
                        QMessageBox.warning(self, "导入错误", f"无法导入文件 {file_name}: {str(e)}")
                
                # 刷新视图
                self._refresh_view()
    
    def _rename_item(self, index):
        """重命名项目
        
        Args:
            index (QModelIndex): 要重命名的项目索引
        """
        if index.isValid():
            file_path = self.model.filePath(index)
            old_name = os.path.basename(file_path)
            
            # 弹出对话框获取新名称
            new_name, ok = QInputDialog.getText(
                self, "重命名", "请输入新名称:", text=old_name
            )
            
            if ok and new_name and new_name != old_name:
                try:
                    # 构建新路径
                    new_path = os.path.join(os.path.dirname(file_path), new_name)
                    
                    # 检查文件是否已存在
                    if os.path.exists(new_path):
                        QMessageBox.warning(self, "错误", f"文件 {new_name} 已存在")
                        return
                    
                    # 重命名文件
                    os.rename(file_path, new_path)
                    
                except Exception as e:
                    QMessageBox.warning(self, "重命名错误", f"无法重命名: {str(e)}")
    
    def _delete_items(self, indexes):
        """删除选中的项目
        
        Args:
            indexes (list): 要删除的项目索引列表
        """
        if indexes:
            # 确认删除
            message = f"确定要删除选中的 {len(indexes)} 个项目吗？此操作不可撤销。"
            response = QMessageBox.question(
                self, "确认删除", message, QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                for index in indexes:
                    if index.isValid() and index.column() == 0:
                        file_path = self.model.filePath(index)
                        try:
                            if os.path.isdir(file_path):
                                import shutil
                                shutil.rmtree(file_path)
                            else:
                                os.remove(file_path)
                        except Exception as e:
                            QMessageBox.warning(
                                self, 
                                "删除错误", 
                                f"无法删除 {os.path.basename(file_path)}: {str(e)}"
                            )
    
    def _refresh_view(self):
        """刷新视图"""
        if self.current_path:
            # 保存当前选择
            current_index = self.tree_view.currentIndex()
            current_path = self.model.filePath(current_index) if current_index.isValid() else None
            
            # 重新加载模型
            self.model.setRootPath(self.current_path)
            
            # 尝试恢复选择
            if current_path and os.path.exists(current_path):
                new_index = self.model.index(current_path)
                if new_index.isValid():
                    self.tree_view.setCurrentIndex(new_index)
    
    def _on_selection_changed(self):
        """选择改变时更新预览"""
        indexes = self.tree_view.selectionModel().selectedIndexes()
        if indexes and len(indexes) > 0:
            # 只使用第一列的索引
            selected_index = next((idx for idx in indexes if idx.column() == 0), None)
            if selected_index:
                file_path = self.model.filePath(selected_index)
                self._update_preview(file_path)
                
                # 发射信号
                self.asset_selected.emit(file_path)
    
    def _on_item_double_clicked(self, index):
        """双击项目时的回调
        
        Args:
            index (QModelIndex): 被双击的项目索引
        """
        if index.isValid() and index.column() == 0:
            file_path = self.model.filePath(index)
            # 发射信号
            self.asset_double_clicked.emit(file_path)
    
    def _update_preview(self, file_path):
        """更新预览面板
        
        Args:
            file_path (str): 文件路径
        """
        if os.path.isdir(file_path):
            # 显示目录信息
            num_files = len([f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))])
            num_dirs = len([d for d in os.listdir(file_path) if os.path.isdir(os.path.join(file_path, d))])
            
            self.preview_panel.setText(f"文件夹: {os.path.basename(file_path)}\n"
                                      f"包含 {num_files} 个文件\n"
                                      f"{num_dirs} 个子目录")
            
            self.preview_panel.setPixmap(QPixmap())  # 清除pixmap
            
        elif os.path.isfile(file_path):
            # 根据文件类型显示不同预览
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.png', '.jpg', '.jpeg', '.bmp']:
                # 图片预览
                self._preview_image(file_path)
                
            elif ext in ['.obj', '.fbx', '.gltf']:
                # 3D模型预览 (简化版)
                self.preview_panel.setText(f"3D模型: {os.path.basename(file_path)}\n"
                                          f"类型: {ext[1:].upper()}\n"
                                          f"大小: {self._get_file_size(file_path)}")
                self.preview_panel.setPixmap(QPixmap())
                
            elif ext in ['.wav', '.mp3', '.ogg']:
                # 音频文件预览
                self.preview_panel.setText(f"音频文件: {os.path.basename(file_path)}\n"
                                          f"类型: {ext[1:].upper()}\n"
                                          f"大小: {self._get_file_size(file_path)}")
                self.preview_panel.setPixmap(QPixmap())
                
            elif ext == '.scene':
                # 场景文件预览
                self.preview_panel.setText(f"场景文件: {os.path.basename(file_path)}\n"
                                          f"大小: {self._get_file_size(file_path)}")
                self.preview_panel.setPixmap(QPixmap())
                
            elif ext == '.py':
                # 脚本文件预览
                self._preview_script(file_path)
                
            else:
                # 其他文件
                self.preview_panel.setText(f"文件: {os.path.basename(file_path)}\n"
                                          f"类型: {ext[1:].upper() if ext else '未知'}\n"
                                          f"大小: {self._get_file_size(file_path)}")
                self.preview_panel.setPixmap(QPixmap())
    
    def _preview_image(self, file_path):
        """预览图片
        
        Args:
            file_path (str): 图片文件路径
        """
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # 获取图片尺寸
                width = pixmap.width()
                height = pixmap.height()
                
                # 调整图片大小以适应预览面板
                preview_width = self.preview_panel.width() - 10
                preview_height = self.preview_panel.height() - 40
                pixmap = pixmap.scaled(
                    preview_width, preview_height,
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                
                self.preview_panel.setPixmap(pixmap)
                # 在pixmap下方显示图片信息
                self.preview_panel.setText(f"\n\n\n\n\n\n{os.path.basename(file_path)}\n"
                                          f"{width}x{height}, {self._get_file_size(file_path)}")
            else:
                self.preview_panel.setText(f"无法预览图片:\n{os.path.basename(file_path)}")
                self.preview_panel.setPixmap(QPixmap())
        except Exception as e:
            self.preview_panel.setText(f"预览图片错误:\n{str(e)}")
            self.preview_panel.setPixmap(QPixmap())
    
    def _preview_script(self, file_path):
        """预览脚本文件
        
        Args:
            file_path (str): 脚本文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 只读取前10行
                lines = [next(f) for _ in range(10) if f]
                content = ''.join(lines)
                
                self.preview_panel.setText(f"脚本文件: {os.path.basename(file_path)}\n"
                                          f"大小: {self._get_file_size(file_path)}\n\n"
                                          f"预览:\n{content}\n...\n")
                self.preview_panel.setPixmap(QPixmap())
        except Exception as e:
            self.preview_panel.setText(f"预览脚本错误:\n{str(e)}")
            self.preview_panel.setPixmap(QPixmap())
    
    def _get_file_size(self, file_path):
        """获取文件大小的可读表示
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            str: 格式化的文件大小
        """
        try:
            size = os.path.getsize(file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except Exception:
            return "未知大小"