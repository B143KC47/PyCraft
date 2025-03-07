"""
脚本系统，处理和管理游戏脚本
"""

import importlib
import os
import sys
import inspect
from engine.core.ecs.system import System

class Script:
    
    def __init__(self):
        """初始化脚本"""
        self.entity = None  # 所属实体
        self.enabled = True  # 是否启用
    
    def on_add(self):
        """当脚本被添加到实体时调用"""
        pass
    
    def on_remove(self):
        """当脚本从实体中移除时调用"""
        pass
    
    def on_enable(self):
        """当脚本被启用时调用"""
        pass
    
    def on_disable(self):
        """当脚本被禁用时调用"""
        pass
    
    def start(self):
        """当场景开始时调用"""
        pass
    
    def update(self, delta_time):
        """
        每帧更新时调用
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        pass


class ScriptSystem(System):
    """脚本系统，处理和管理游戏脚本"""
    
    def __init__(self):
        """初始化脚本系统"""
        super().__init__()
        self.script_paths = []  # 脚本路径列表
        self.script_classes = {}  # 脚本类字典，键为脚本名称，值为脚本类
        self.active_scripts = []  # 活动脚本列表
        self.initialized = False  # 是否已初始化
        self.running = False  # 脚本系统是否正在运行
    
    def initialize(self):
        """初始化脚本系统"""
        # 添加默认脚本路径
        default_script_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scripts"),  # 引擎脚本目录
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "game", "scripts")  # 游戏脚本目录
        ]
        
        for path in default_script_paths:
            if os.path.exists(path):
                self.add_script_path(path)
        
        self.initialized = True
    
    def add_script_path(self, path):
        """
        添加脚本路径
        
        Args:
            path (str): 脚本目录路径
        """
        if os.path.exists(path) and path not in self.script_paths:
            self.script_paths.append(path)
            
            # 将路径添加到Python模块搜索路径
            if path not in sys.path:
                sys.path.append(path)
    
    def load_script_class(self, script_name):
        """
        加载脚本类
        
        Args:
            script_name (str): 脚本名称
            
        Returns:
            class: 脚本类，如果不存在则返回None
        """
        # 如果已经加载，直接返回
        if script_name in self.script_classes:
            return self.script_classes[script_name]
        
        # 尝试导入脚本模块
        try:
            # 尝试直接导入
            module = importlib.import_module(script_name)
            
            # 查找脚本类
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Script) and obj != Script:
                    # 缓存脚本类
                    self.script_classes[script_name] = obj
                    return obj
            
            print(f"找不到脚本类: {script_name}")
            return None
            
        except ImportError:
            # 如果直接导入失败，尝试从脚本路径中查找
            for path in self.script_paths:
                script_path = os.path.join(path, f"{script_name}.py")
                
                if os.path.exists(script_path):
                    # 获取相对模块名称
                    rel_path = os.path.relpath(script_path, os.path.dirname(path))
                    module_name = os.path.splitext(rel_path.replace(os.path.sep, "."))[0]
                    
                    try:
                        # 导入模块
                        module = importlib.import_module(module_name)
                        
                        # 查找脚本类
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and issubclass(obj, Script) and obj != Script:
                                # 缓存脚本类
                                self.script_classes[script_name] = obj
                                return obj
                        
                        print(f"找不到脚本类: {script_name}")
                        return None
                        
                    except Exception as e:
                        print(f"加载脚本失败: {script_name}, {e}")
            
            print(f"找不到脚本文件: {script_name}")
            return None
    
    def create_script(self, script_name, entity):
        """
        创建脚本实例
        
        Args:
            script_name (str): 脚本名称
            entity: 所属实体
            
        Returns:
            Script: 脚本实例，如果创建失败则返回None
        """
        # 加载脚本类
        script_class = self.load_script_class(script_name)
        
        if script_class:
            try:
                # 创建脚本实例
                script = script_class()
                script.entity = entity
                
                # 添加到活动脚本列表
                self.active_scripts.append(script)
                
                # 调用添加方法
                script.on_add()
                
                return script
                
            except Exception as e:
                print(f"创建脚本实例失败: {script_name}, {e}")
                return None
        
        return None
    
    def start_scripts(self, scene):
        """
        启动场景中的所有脚本
        
        Args:
            scene: 场景
        """
        # 清空活动脚本列表
        self.active_scripts = []
        
        # 获取场景中所有实体
        entities = scene.get_entities()
        
        # 收集所有脚本组件
        for entity in entities:
            # 在这里我们需要查找实体上的脚本组件
            # 由于没有具体的脚本组件类，我们假设它继承自Script
            for component in entity.get_components():
                if isinstance(component, Script):
                    self.active_scripts.append(component)
        
        # 调用所有脚本的start方法
        for script in self.active_scripts:
            if script.enabled:
                try:
                    script.start()
                except Exception as e:
                    print(f"调用脚本start方法失败: {script.__class__.__name__}, {e}")
        
        # 启动脚本系统
        self.running = True
    
    def stop_scripts(self):
        """停止所有脚本"""
        # 停止脚本系统
        self.running = False
        
        # 清空活动脚本列表
        self.active_scripts = []
    
    def update(self, delta_time):
        """
        更新脚本系统
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        if not self.initialized or not self.running:
            return
        
        # 更新所有活动脚本
        for script in self.active_scripts:
            if script.enabled:
                try:
                    script.update(delta_time)
                except Exception as e:
                    print(f"调用脚本update方法失败: {script.__class__.__name__}, {e}")
    
    def reload_scripts(self):
        """重新加载所有脚本"""
        # 清除脚本类缓存
        self.script_classes.clear()
        
        # 记录当前活动脚本
        active_scripts = []
        for script in self.active_scripts:
            active_scripts.append({
                "name": script.__class__.__module__,
                "entity": script.entity
            })
        
        # 清空活动脚本列表
        self.active_scripts = []
        
        # 重新创建脚本
        for script_info in active_scripts:
            script = self.create_script(script_info["name"], script_info["entity"])
            if script and self.running:
                script.start()
    
    def shutdown(self):
        """关闭脚本系统"""
        # 停止所有脚本
        self.stop_scripts()
        
        # 清除脚本类缓存
        self.script_classes.clear()
        
        # 重置系统状态
        self.initialized = False