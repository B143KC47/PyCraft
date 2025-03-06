"""
着色器管理器，负责加载和管理着色器
"""

import os
import pygame
from OpenGL.GL import *
import numpy as np

from engine.rendering.shaders.shader import Shader


class ShaderManager:
    """着色器管理器，负责加载和管理着色器"""
    
    def __init__(self):
        """初始化着色器管理器"""
        self.shaders = {}  # 着色器缓存
        self.shader_paths = {}  # 着色器路径
        
        # 设置默认着色器路径
        self._set_default_shader_paths()
    
    def _set_default_shader_paths(self):
        """设置默认着色器路径"""
        # 获取着色器目录
        shader_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "shaders")
        
        # 设置默认着色器路径
        self.shader_paths = {
            "default": {
                "vertex": os.path.join(shader_dir, "default.vert"),
                "fragment": os.path.join(shader_dir, "default.frag")
            },
            "skybox": {
                "vertex": os.path.join(shader_dir, "skybox.vert"),
                "fragment": os.path.join(shader_dir, "skybox.frag")
            },
            "terrain": {
                "vertex": os.path.join(shader_dir, "terrain.vert"),
                "fragment": os.path.join(shader_dir, "terrain.frag")
            },
            "water": {
                "vertex": os.path.join(shader_dir, "water.vert"),
                "fragment": os.path.join(shader_dir, "water.frag")
            },
            "particle": {
                "vertex": os.path.join(shader_dir, "particle.vert"),
                "fragment": os.path.join(shader_dir, "particle.frag")
            },
            "post_process": {
                "vertex": os.path.join(shader_dir, "post_process.vert"),
                "fragment": os.path.join(shader_dir, "post_process.frag")
            },
            "unlit": {
                "vertex": os.path.join(shader_dir, "unlit.vert"),
                "fragment": os.path.join(shader_dir, "unlit.frag")
            }
        }
    
    def load_shader(self, name):
        """
        加载着色器
        
        Args:
            name (str): 着色器名称
            
        Returns:
            Shader: 着色器实例，如果加载失败则返回None
        """
        # 如果已加载，直接返回
        if name in self.shaders:
            return self.shaders[name]
        
        # 检查是否有预定义路径
        if name not in self.shader_paths:
            print(f"未找到着色器路径: {name}")
            return None
        
        # 获取着色器路径
        shader_path = self.shader_paths[name]
        
        # 加载着色器
        try:
            # 读取顶点着色器
            with open(shader_path["vertex"], "r") as f:
                vertex_source = f.read()
            
            # 读取片段着色器
            with open(shader_path["fragment"], "r") as f:
                fragment_source = f.read()
            
            # 创建着色器
            shader = Shader()
            shader.create(vertex_source, fragment_source)
            
            # 缓存着色器
            self.shaders[name] = shader
            
            return shader
        
        except Exception as e:
            print(f"加载着色器失败: {name}, {e}")
            return None
    
    def get_shader(self, name):
        """
        获取着色器
        
        Args:
            name (str): 着色器名称
            
        Returns:
            Shader: 着色器实例，如果不存在则返回None
        """
        return self.shaders.get(name)
    
    def add_shader_path(self, name, vertex_path, fragment_path):
        """
        添加着色器路径
        
        Args:
            name (str): 着色器名称
            vertex_path (str): 顶点着色器路径
            fragment_path (str): 片段着色器路径
        """
        self.shader_paths[name] = {
            "vertex": vertex_path,
            "fragment": fragment_path
        }
    
    def reload_shader(self, name):
        """
        重新加载着色器
        
        Args:
            name (str): 着色器名称
            
        Returns:
            Shader: 着色器实例，如果重新加载失败则返回None
        """
        # 如果已加载，先删除
        if name in self.shaders:
            self.shaders[name].delete()
            del self.shaders[name]
        
        # 重新加载
        return self.load_shader(name)
    
    def reload_all_shaders(self):
        """
        重新加载所有着色器
        
        Returns:
            bool: 是否全部重新加载成功
        """
        success = True
        
        # 获取所有着色器名称
        shader_names = list(self.shaders.keys())
        
        # 重新加载每个着色器
        for name in shader_names:
            if not self.reload_shader(name):
                success = False
        
        return success
    
    def delete_shader(self, name):
        """
        删除着色器
        
        Args:
            name (str): 着色器名称
            
        Returns:
            bool: 是否成功删除
        """
        if name in self.shaders:
            self.shaders[name].delete()
            del self.shaders[name]
            return True
        
        return False
    
    def delete_all_shaders(self):
        """删除所有着色器"""
        for shader in self.shaders.values():
            shader.delete()
        
        self.shaders.clear()
    
    def __del__(self):
        """析构函数"""
        self.delete_all_shaders() 