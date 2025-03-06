"""
场景管理器，负责管理场景
"""

import os
from engine.core.scene.scene import Scene


class SceneManager:
    """场景管理器，负责管理场景"""
    
    def __init__(self):
        """初始化场景管理器"""
        self.scenes = {}  # 场景字典，键为场景ID，值为场景实例
        self.active_scene = None  # 当前激活的场景
        self.scene_paths = {}  # 场景路径字典，键为场景名称，值为场景文件路径
    
    def create_scene(self, name="Scene"):
        """
        创建场景
        
        Args:
            name (str): 场景名称
            
        Returns:
            Scene: 创建的场景
        """
        scene = Scene(name)
        self.add_scene(scene)
        return scene
    
    def add_scene(self, scene):
        """
        添加场景
        
        Args:
            scene: 场景
            
        Returns:
            scene: 添加的场景
        """
        self.scenes[scene.id] = scene
        return scene
    
    def remove_scene(self, scene_id):
        """
        移除场景
        
        Args:
            scene_id (str): 场景ID
            
        Returns:
            bool: 是否成功移除
        """
        if scene_id in self.scenes:
            scene = self.scenes[scene_id]
            
            # 如果是当前激活的场景，取消激活
            if scene == self.active_scene:
                self.active_scene = None
            
            # 从场景字典中移除
            del self.scenes[scene_id]
            
            return True
        
        return False
    
    def get_scene(self, scene_id):
        """
        获取场景
        
        Args:
            scene_id (str): 场景ID
            
        Returns:
            Scene: 场景，如果不存在则返回None
        """
        return self.scenes.get(scene_id)
    
    def get_scenes(self):
        """
        获取所有场景
        
        Returns:
            list: 场景列表
        """
        return list(self.scenes.values())
    
    def get_scene_by_name(self, name):
        """
        通过名称获取场景
        
        Args:
            name (str): 场景名称
            
        Returns:
            Scene: 场景，如果不存在则返回None
        """
        for scene in self.scenes.values():
            if scene.name == name:
                return scene
        
        return None
    
    def set_active_scene(self, scene_id):
        """
        设置当前激活的场景
        
        Args:
            scene_id (str): 场景ID
            
        Returns:
            bool: 是否成功设置
        """
        if scene_id in self.scenes:
            # 如果有当前激活的场景，取消激活
            if self.active_scene:
                self.active_scene.deactivate()
            
            # 设置新的激活场景
            self.active_scene = self.scenes[scene_id]
            self.active_scene.activate()
            
            return True
        
        return False
    
    def get_active_scene(self):
        """
        获取当前激活的场景
        
        Returns:
            Scene: 当前激活的场景，如果没有则返回None
        """
        return self.active_scene
    
    def load_scene(self, path):
        """
        加载场景
        
        Args:
            path (str): 场景文件路径
            
        Returns:
            Scene: 加载的场景，如果加载失败则返回None
        """
        if not os.path.exists(path):
            return None
        
        # 创建新场景
        scene = Scene()
        
        # 加载场景
        if scene.load(path):
            # 添加到场景字典
            self.add_scene(scene)
            
            # 添加到场景路径字典
            self.scene_paths[scene.name] = path
            
            return scene
        
        return None
    
    def save_scene(self, scene_id, path=None):
        """
        保存场景
        
        Args:
            scene_id (str): 场景ID
            path (str): 保存路径，如果为None则使用当前路径
            
        Returns:
            bool: 是否成功保存
        """
        if scene_id not in self.scenes:
            return False
        
        scene = self.scenes[scene_id]
        
        # 保存场景
        if scene.save(path):
            # 更新场景路径字典
            if path:
                self.scene_paths[scene.name] = path
            
            return True
        
        return False
    
    def reload_scene(self, scene_id):
        """
        重新加载场景
        
        Args:
            scene_id (str): 场景ID
            
        Returns:
            bool: 是否成功重新加载
        """
        if scene_id not in self.scenes:
            return False
        
        scene = self.scenes[scene_id]
        
        # 如果没有路径，无法重新加载
        if not scene.path:
            return False
        
        # 重新加载场景
        return scene.load(scene.path)
    
    def clear(self):
        """清空场景管理器"""
        # 清空所有场景
        for scene in list(self.scenes.values()):
            scene.clear()
        
        # 清空场景字典
        self.scenes.clear()
        
        # 清空当前激活的场景
        self.active_scene = None
    
    def update(self, delta_time):
        """
        更新场景管理器
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        # 更新当前激活的场景
        if self.active_scene:
            self.active_scene.update(delta_time)
    
    def __str__(self):
        """字符串表示"""
        active_scene_name = self.active_scene.name if self.active_scene else "None"
        return f"SceneManager(scenes={len(self.scenes)}, active_scene={active_scene_name})" 