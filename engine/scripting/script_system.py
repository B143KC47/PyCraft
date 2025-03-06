"""
脚本系统，负责管理和执行脚本
"""

import os
import importlib.util
import sys
import inspect
import traceback

from engine.core.ecs.system import System


class Script:
    """脚本基类，所有脚本都应继承自此类"""
    
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
    
    def fixed_update(self, delta_time):
        """
        固定时间步长更新时调用
        
        Args:
            delta_time (float): 固定帧时间，单位为秒
        """
        pass
    
    def late_update(self, delta_time):
        """
        在所有更新之后调用
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        pass
    
    def on_collision_enter(self, other):
        """
        当碰撞开始时调用
        
        Args:
            other: 碰撞的另一个实体
        """
        pass
    
    def on_collision_stay(self, other):
        """
        当碰撞持续时调用
        
        Args:
            other: 碰撞的另一个实体
        """
        pass
    
    def on_collision_exit(self, other):
        """
        当碰撞结束时调用
        
        Args:
            other: 碰撞的另一个实体
        """
        pass
    
    def on_trigger_enter(self, other):
        """
        当触发器开始时调用
        
        Args:
            other: 触发的另一个实体
        """
        pass
    
    def on_trigger_stay(self, other):
        """
        当触发器持续时调用
        
        Args:
            other: 触发的另一个实体
        """
        pass
    
    def on_trigger_exit(self, other):
        """
        当触发器结束时调用
        
        Args:
            other: 触发的另一个实体
        """
        pass
    
    def on_destroy(self):
        """当实体被销毁时调用"""
        pass


class ScriptSystem(System):
    """脚本系统，负责管理和执行脚本"""
    
    def __init__(self):
        """初始化脚本系统"""
        super().__init__()
        self.priority = 20  # 脚本系统优先级中等，在输入系统之后，物理系统之前更新
        self.scripts = {}  # 脚本字典，键为脚本名称，值为脚本类
        self.script_instances = {}  # 脚本实例字典，键为实体ID，值为脚本实例列表
        self.script_paths = []  # 脚本路径列表
        self.fixed_time_step = 1.0 / 60.0  # 固定时间步长
        self.accumulated_time = 0.0  # 累积时间
        self.initialized = False  # 是否已初始化
    
    def initialize(self, script_paths=None):
        """
        初始化脚本系统
        
        Args:
            script_paths (list): 脚本路径列表
        """
        if script_paths:
            self.script_paths = script_paths
        
        # 加载脚本
        self._load_scripts()
        
        self.initialized = True
    
    def _load_scripts(self):
        """加载脚本"""
        for script_path in self.script_paths:
            if os.path.isdir(script_path):
                # 如果是目录，加载目录下的所有脚本
                for root, _, files in os.walk(script_path):
                    for file in files:
                        if file.endswith(".py"):
                            self._load_script_file(os.path.join(root, file))
            elif os.path.isfile(script_path) and script_path.endswith(".py"):
                # 如果是文件，加载单个脚本
                self._load_script_file(script_path)
    
    def _load_script_file(self, file_path):
        """
        加载脚本文件
        
        Args:
            file_path (str): 脚本文件路径
        """
        try:
            # 获取模块名
            module_name = os.path.basename(file_path)[:-3]  # 去掉.py后缀
            
            # 加载模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 查找脚本类
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, Script) and obj != Script:
                    self.scripts[name] = obj
        
        except Exception as e:
            print(f"加载脚本失败: {file_path}, {e}")
            traceback.print_exc()
    
    def add_script_path(self, script_path):
        """
        添加脚本路径
        
        Args:
            script_path (str): 脚本路径
        """
        if script_path not in self.script_paths:
            self.script_paths.append(script_path)
            
            # 加载脚本
            if os.path.isdir(script_path):
                # 如果是目录，加载目录下的所有脚本
                for root, _, files in os.walk(script_path):
                    for file in files:
                        if file.endswith(".py"):
                            self._load_script_file(os.path.join(root, file))
            elif os.path.isfile(script_path) and script_path.endswith(".py"):
                # 如果是文件，加载单个脚本
                self._load_script_file(script_path)
    
    def reload_scripts(self):
        """重新加载脚本"""
        # 清空脚本字典
        self.scripts.clear()
        
        # 重新加载脚本
        self._load_scripts()
    
    def create_script(self, script_name, entity):
        """
        创建脚本实例
        
        Args:
            script_name (str): 脚本名称
            entity: 所属实体
            
        Returns:
            Script: 脚本实例，如果创建失败则返回None
        """
        if not self.initialized:
            return None
        
        if script_name not in self.scripts:
            print(f"脚本不存在: {script_name}")
            return None
        
        try:
            # 创建脚本实例
            script = self.scripts[script_name]()
            script.entity = entity
            
            # 添加到脚本实例字典
            entity_id = entity.id
            if entity_id not in self.script_instances:
                self.script_instances[entity_id] = []
            
            self.script_instances[entity_id].append(script)
            
            # 调用脚本的添加方法
            script.on_add()
            
            return script
        
        except Exception as e:
            print(f"创建脚本实例失败: {script_name}, {e}")
            traceback.print_exc()
            return None
    
    def remove_script(self, entity, script):
        """
        移除脚本实例
        
        Args:
            entity: 所属实体
            script: 脚本实例
            
        Returns:
            bool: 是否成功移除
        """
        if not self.initialized:
            return False
        
        entity_id = entity.id
        
        if entity_id not in self.script_instances:
            return False
        
        if script in self.script_instances[entity_id]:
            # 调用脚本的移除方法
            script.on_remove()
            
            # 从脚本实例字典中移除
            self.script_instances[entity_id].remove(script)
            
            return True
        
        return False
    
    def remove_all_scripts(self, entity):
        """
        移除实体的所有脚本
        
        Args:
            entity: 所属实体
            
        Returns:
            bool: 是否成功移除
        """
        if not self.initialized:
            return False
        
        entity_id = entity.id
        
        if entity_id not in self.script_instances:
            return False
        
        # 调用所有脚本的移除方法
        for script in self.script_instances[entity_id]:
            script.on_remove()
        
        # 清空脚本实例列表
        self.script_instances[entity_id].clear()
        
        # 从脚本实例字典中移除
        del self.script_instances[entity_id]
        
        return True
    
    def get_script(self, entity, script_type):
        """
        获取实体的脚本实例
        
        Args:
            entity: 所属实体
            script_type: 脚本类型
            
        Returns:
            Script: 脚本实例，如果不存在则返回None
        """
        if not self.initialized:
            return None
        
        entity_id = entity.id
        
        if entity_id not in self.script_instances:
            return None
        
        for script in self.script_instances[entity_id]:
            if isinstance(script, script_type):
                return script
        
        return None
    
    def get_scripts(self, entity):
        """
        获取实体的所有脚本实例
        
        Args:
            entity: 所属实体
            
        Returns:
            list: 脚本实例列表
        """
        if not self.initialized:
            return []
        
        entity_id = entity.id
        
        if entity_id not in self.script_instances:
            return []
        
        return self.script_instances[entity_id].copy()
    
    def start_scripts(self, scene):
        """
        启动场景中的所有脚本
        
        Args:
            scene: 场景
        """
        if not self.initialized:
            return
        
        # 调用所有脚本的start方法
        for entity_id, scripts in self.script_instances.items():
            entity = scene.get_entity(entity_id)
            
            if entity and entity.enabled:
                for script in scripts:
                    if script.enabled:
                        try:
                            script.start()
                        except Exception as e:
                            print(f"脚本start方法执行失败: {script.__class__.__name__}, {e}")
                            traceback.print_exc()
    
    def update(self, delta_time):
        """
        更新脚本系统
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        if not self.initialized:
            return
        
        # 更新所有脚本
        for entity_id, scripts in list(self.script_instances.items()):
            for script in scripts:
                if script.enabled and script.entity and script.entity.enabled:
                    try:
                        script.update(delta_time)
                    except Exception as e:
                        print(f"脚本update方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
        
        # 累积时间
        self.accumulated_time += delta_time
        
        # 固定时间步长更新
        while self.accumulated_time >= self.fixed_time_step:
            self.accumulated_time -= self.fixed_time_step
            
            # 更新所有脚本的fixed_update方法
            for entity_id, scripts in list(self.script_instances.items()):
                for script in scripts:
                    if script.enabled and script.entity and script.entity.enabled:
                        try:
                            script.fixed_update(self.fixed_time_step)
                        except Exception as e:
                            print(f"脚本fixed_update方法执行失败: {script.__class__.__name__}, {e}")
                            traceback.print_exc()
        
        # 更新所有脚本的late_update方法
        for entity_id, scripts in list(self.script_instances.items()):
            for script in scripts:
                if script.enabled and script.entity and script.entity.enabled:
                    try:
                        script.late_update(delta_time)
                    except Exception as e:
                        print(f"脚本late_update方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
    
    def on_collision_enter(self, entity_a, entity_b):
        """
        处理碰撞开始事件
        
        Args:
            entity_a: 第一个实体
            entity_b: 第二个实体
        """
        if not self.initialized:
            return
        
        entity_a_id = entity_a.id
        
        if entity_a_id in self.script_instances:
            for script in self.script_instances[entity_a_id]:
                if script.enabled:
                    try:
                        script.on_collision_enter(entity_b)
                    except Exception as e:
                        print(f"脚本on_collision_enter方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
    
    def on_collision_stay(self, entity_a, entity_b):
        """
        处理碰撞持续事件
        
        Args:
            entity_a: 第一个实体
            entity_b: 第二个实体
        """
        if not self.initialized:
            return
        
        entity_a_id = entity_a.id
        
        if entity_a_id in self.script_instances:
            for script in self.script_instances[entity_a_id]:
                if script.enabled:
                    try:
                        script.on_collision_stay(entity_b)
                    except Exception as e:
                        print(f"脚本on_collision_stay方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
    
    def on_collision_exit(self, entity_a, entity_b):
        """
        处理碰撞结束事件
        
        Args:
            entity_a: 第一个实体
            entity_b: 第二个实体
        """
        if not self.initialized:
            return
        
        entity_a_id = entity_a.id
        
        if entity_a_id in self.script_instances:
            for script in self.script_instances[entity_a_id]:
                if script.enabled:
                    try:
                        script.on_collision_exit(entity_b)
                    except Exception as e:
                        print(f"脚本on_collision_exit方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
    
    def on_trigger_enter(self, entity_a, entity_b):
        """
        处理触发器开始事件
        
        Args:
            entity_a: 第一个实体
            entity_b: 第二个实体
        """
        if not self.initialized:
            return
        
        entity_a_id = entity_a.id
        
        if entity_a_id in self.script_instances:
            for script in self.script_instances[entity_a_id]:
                if script.enabled:
                    try:
                        script.on_trigger_enter(entity_b)
                    except Exception as e:
                        print(f"脚本on_trigger_enter方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
    
    def on_trigger_stay(self, entity_a, entity_b):
        """
        处理触发器持续事件
        
        Args:
            entity_a: 第一个实体
            entity_b: 第二个实体
        """
        if not self.initialized:
            return
        
        entity_a_id = entity_a.id
        
        if entity_a_id in self.script_instances:
            for script in self.script_instances[entity_a_id]:
                if script.enabled:
                    try:
                        script.on_trigger_stay(entity_b)
                    except Exception as e:
                        print(f"脚本on_trigger_stay方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
    
    def on_trigger_exit(self, entity_a, entity_b):
        """
        处理触发器结束事件
        
        Args:
            entity_a: 第一个实体
            entity_b: 第二个实体
        """
        if not self.initialized:
            return
        
        entity_a_id = entity_a.id
        
        if entity_a_id in self.script_instances:
            for script in self.script_instances[entity_a_id]:
                if script.enabled:
                    try:
                        script.on_trigger_exit(entity_b)
                    except Exception as e:
                        print(f"脚本on_trigger_exit方法执行失败: {script.__class__.__name__}, {e}")
                        traceback.print_exc()
    
    def on_entity_destroy(self, entity):
        """
        处理实体销毁事件
        
        Args:
            entity: 实体
        """
        if not self.initialized:
            return
        
        entity_id = entity.id
        
        if entity_id in self.script_instances:
            for script in self.script_instances[entity_id]:
                try:
                    script.on_destroy()
                except Exception as e:
                    print(f"脚本on_destroy方法执行失败: {script.__class__.__name__}, {e}")
                    traceback.print_exc()
            
            # 清空脚本实例列表
            self.script_instances[entity_id].clear()
            
            # 从脚本实例字典中移除
            del self.script_instances[entity_id]
    
    def shutdown(self):
        """关闭脚本系统"""
        if not self.initialized:
            return
        
        # 清空脚本实例字典
        self.script_instances.clear()
        
        # 清空脚本字典
        self.scripts.clear()
        
        self.initialized = False 