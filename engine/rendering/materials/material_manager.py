"""
材质管理器，负责加载和管理材质
"""

import os
import json
import pygame
from OpenGL.GL import *
import numpy as np

from engine.rendering.materials.material import Material


class MaterialManager:
    """材质管理器，负责加载和管理材质"""
    
    def __init__(self):
        """初始化材质管理器"""
        self.materials = {}  # 材质缓存
        self.material_paths = {}  # 材质路径
        
        # 设置默认材质路径
        self._set_default_material_paths()
        
        # 创建默认材质
        self._create_default_materials()
    
    def _set_default_material_paths(self):
        """设置默认材质路径"""
        # 获取材质目录
        material_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "materials")
        
        # 设置默认材质路径
        self.material_paths = {
            "default": os.path.join(material_dir, "default.json"),
            "unlit": os.path.join(material_dir, "unlit.json")
        }
    
    def _create_default_materials(self):
        """创建默认材质"""
        # 创建默认材质
        default_material = Material("default")
        default_material.set_shader("default")
        default_material.set_color((1.0, 1.0, 1.0, 1.0))
        default_material.set_specular((0.5, 0.5, 0.5, 1.0), 32.0)
        
        # 添加到缓存
        self.materials["default"] = default_material
        
        # 创建无光照材质
        unlit_material = Material("unlit")
        unlit_material.set_shader("unlit")
        unlit_material.set_color((1.0, 1.0, 1.0, 1.0))
        
        # 添加到缓存
        self.materials["unlit"] = unlit_material
    
    def load_material(self, name):
        """
        加载材质
        
        Args:
            name (str): 材质名称
            
        Returns:
            Material: 材质实例，如果加载失败则返回默认材质
        """
        # 如果已加载，直接返回
        if name in self.materials:
            return self.materials[name]
        
        # 检查是否有预定义路径
        if name not in self.material_paths:
            print(f"未找到材质路径: {name}")
            return self.materials.get("default")
        
        # 获取材质路径
        material_path = self.material_paths[name]
        
        # 加载材质
        try:
            # 读取材质文件
            with open(material_path, "r") as f:
                material_data = json.load(f)
            
            # 创建材质
            material = Material(name)
            
            # 设置基本属性
            if "shader" in material_data:
                material.set_shader(material_data["shader"])
            
            if "color" in material_data:
                material.set_color(tuple(material_data["color"]))
            
            if "specular_color" in material_data and "shininess" in material_data:
                material.set_specular(tuple(material_data["specular_color"]), material_data["shininess"])
            
            if "emission_color" in material_data:
                material.set_emission(tuple(material_data["emission_color"]))
            
            # 设置纹理
            if "diffuse_texture" in material_data:
                material.set_diffuse_texture(material_data["diffuse_texture"])
            
            if "specular_texture" in material_data:
                material.set_specular_texture(material_data["specular_texture"])
            
            if "normal_texture" in material_data:
                material.set_normal_texture(material_data["normal_texture"])
            
            if "emission_texture" in material_data:
                material.set_emission_texture(material_data["emission_texture"])
            
            # 设置渲染属性
            if "transparent" in material_data:
                material.set_transparent(material_data["transparent"], material_data.get("alpha_cutoff", 0.5))
            
            if "double_sided" in material_data:
                material.set_double_sided(material_data["double_sided"])
            
            if "wireframe" in material_data:
                material.set_wireframe(material_data["wireframe"])
            
            if "receive_shadows" in material_data and "cast_shadows" in material_data:
                material.set_shadows(material_data["receive_shadows"], material_data["cast_shadows"])
            
            # 设置自定义属性
            if "custom_properties" in material_data:
                for name, value in material_data["custom_properties"].items():
                    material.set_custom_property(name, value)
            
            # 缓存材质
            self.materials[name] = material
            
            return material
        
        except Exception as e:
            print(f"加载材质失败: {name}, {e}")
            return self.materials.get("default")
    
    def get_material(self, name):
        """
        获取材质
        
        Args:
            name (str): 材质名称
            
        Returns:
            Material: 材质实例，如果不存在则返回默认材质
        """
        return self.materials.get(name, self.materials.get("default"))
    
    def add_material(self, material):
        """
        添加材质
        
        Args:
            material (Material): 材质实例
        """
        self.materials[material.name] = material
    
    def add_material_path(self, name, path):
        """
        添加材质路径
        
        Args:
            name (str): 材质名称
            path (str): 材质文件路径
        """
        self.material_paths[name] = path
    
    def reload_material(self, name):
        """
        重新加载材质
        
        Args:
            name (str): 材质名称
            
        Returns:
            Material: 材质实例，如果重新加载失败则返回默认材质
        """
        # 如果已加载，先删除
        if name in self.materials:
            del self.materials[name]
        
        # 重新加载
        return self.load_material(name)
    
    def save_material(self, material, path=None):
        """
        保存材质到文件
        
        Args:
            material (Material): 材质实例
            path (str): 保存路径，如果为None则使用预定义路径
            
        Returns:
            bool: 是否成功保存
        """
        # 如果没有指定路径，使用预定义路径
        if path is None:
            if material.name not in self.material_paths:
                print(f"未找到材质路径: {material.name}")
                return False
            
            path = self.material_paths[material.name]
        
        # 构建材质数据
        material_data = {
            "shader": material.shader,
            "color": material.color,
            "specular_color": material.specular_color,
            "shininess": material.shininess,
            "emission_color": material.emission_color,
            "transparent": material.transparent,
            "alpha_cutoff": material.alpha_cutoff,
            "double_sided": material.double_sided,
            "wireframe": material.wireframe,
            "receive_shadows": material.receive_shadows,
            "cast_shadows": material.cast_shadows,
            "custom_properties": material.custom_properties
        }
        
        # 添加纹理路径
        if material.diffuse_texture is not None:
            material_data["diffuse_texture"] = material.diffuse_texture
        
        if material.specular_texture is not None:
            material_data["specular_texture"] = material.specular_texture
        
        if material.normal_texture is not None:
            material_data["normal_texture"] = material.normal_texture
        
        if material.emission_texture is not None:
            material_data["emission_texture"] = material.emission_texture
        
        # 保存到文件
        try:
            with open(path, "w") as f:
                json.dump(material_data, f, indent=4)
            
            return True
        
        except Exception as e:
            print(f"保存材质失败: {material.name}, {e}")
            return False
    
    def delete_material(self, name):
        """
        删除材质
        
        Args:
            name (str): 材质名称
            
        Returns:
            bool: 是否成功删除
        """
        if name in self.materials:
            del self.materials[name]
            return True
        
        return False 