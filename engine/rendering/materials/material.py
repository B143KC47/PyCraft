"""
材质类，定义物体的渲染属性
"""

import pygame
from OpenGL.GL import *
import numpy as np


class Material:
    """材质类，定义物体的渲染属性"""
    
    def __init__(self, name="Default"):
        """
        初始化材质
        
        Args:
            name (str): 材质名称
        """
        self.name = name
        self.shader = "default"  # 使用的着色器名称
        
        # 基本属性
        self.color = (1.0, 1.0, 1.0, 1.0)  # 颜色，RGBA格式，值范围0-1
        self.specular_color = (1.0, 1.0, 1.0, 1.0)  # 高光颜色
        self.shininess = 32.0  # 光泽度
        self.emission_color = (0.0, 0.0, 0.0, 0.0)  # 自发光颜色
        
        # 纹理
        self.diffuse_texture = None  # 漫反射纹理
        self.specular_texture = None  # 高光纹理
        self.normal_texture = None  # 法线纹理
        self.emission_texture = None  # 自发光纹理
        
        # 渲染属性
        self.transparent = False  # 是否透明
        self.alpha_cutoff = 0.5  # Alpha测试阈值
        self.double_sided = False  # 是否双面渲染
        self.wireframe = False  # 是否线框模式
        self.receive_shadows = True  # 是否接收阴影
        self.cast_shadows = True  # 是否投射阴影
        
        # 自定义属性
        self.custom_properties = {}  # 自定义属性字典
    
    def set_shader(self, shader_name):
        """
        设置着色器
        
        Args:
            shader_name (str): 着色器名称
        """
        self.shader = shader_name
    
    def set_color(self, color):
        """
        设置颜色
        
        Args:
            color (tuple): 颜色，RGBA格式，值范围0-1
        """
        self.color = color
    
    def set_specular(self, color, shininess):
        """
        设置高光属性
        
        Args:
            color (tuple): 高光颜色，RGBA格式，值范围0-1
            shininess (float): 光泽度
        """
        self.specular_color = color
        self.shininess = shininess
    
    def set_emission(self, color):
        """
        设置自发光颜色
        
        Args:
            color (tuple): 自发光颜色，RGBA格式，值范围0-1
        """
        self.emission_color = color
    
    def set_diffuse_texture(self, texture):
        """
        设置漫反射纹理
        
        Args:
            texture: 纹理ID或路径
        """
        self.diffuse_texture = texture
    
    def set_specular_texture(self, texture):
        """
        设置高光纹理
        
        Args:
            texture: 纹理ID或路径
        """
        self.specular_texture = texture
    
    def set_normal_texture(self, texture):
        """
        设置法线纹理
        
        Args:
            texture: 纹理ID或路径
        """
        self.normal_texture = texture
    
    def set_emission_texture(self, texture):
        """
        设置自发光纹理
        
        Args:
            texture: 纹理ID或路径
        """
        self.emission_texture = texture
    
    def set_transparent(self, transparent, alpha_cutoff=0.5):
        """
        设置透明属性
        
        Args:
            transparent (bool): 是否透明
            alpha_cutoff (float): Alpha测试阈值
        """
        self.transparent = transparent
        self.alpha_cutoff = alpha_cutoff
    
    def set_double_sided(self, double_sided):
        """
        设置双面渲染
        
        Args:
            double_sided (bool): 是否双面渲染
        """
        self.double_sided = double_sided
    
    def set_wireframe(self, wireframe):
        """
        设置线框模式
        
        Args:
            wireframe (bool): 是否线框模式
        """
        self.wireframe = wireframe
    
    def set_shadows(self, receive, cast):
        """
        设置阴影属性
        
        Args:
            receive (bool): 是否接收阴影
            cast (bool): 是否投射阴影
        """
        self.receive_shadows = receive
        self.cast_shadows = cast
    
    def set_custom_property(self, name, value):
        """
        设置自定义属性
        
        Args:
            name (str): 属性名称
            value: 属性值
        """
        self.custom_properties[name] = value
    
    def get_custom_property(self, name, default=None):
        """
        获取自定义属性
        
        Args:
            name (str): 属性名称
            default: 默认值
            
        Returns:
            属性值，如果不存在则返回默认值
        """
        return self.custom_properties.get(name, default)
    
    def apply(self, shader):
        """
        应用材质到着色器
        
        Args:
            shader: 着色器实例
        """
        # 设置基本属性
        shader.set_uniform("material.color", self.color)
        shader.set_uniform("material.specular_color", self.specular_color)
        shader.set_uniform("material.shininess", self.shininess)
        shader.set_uniform("material.emission_color", self.emission_color)
        
        # 设置纹理
        texture_unit = 0
        
        if self.diffuse_texture is not None:
            glActiveTexture(GL_TEXTURE0 + texture_unit)
            glBindTexture(GL_TEXTURE_2D, self.diffuse_texture)
            shader.set_uniform("material.diffuse_texture", texture_unit)
            shader.set_uniform("material.has_diffuse_texture", True)
            texture_unit += 1
        else:
            shader.set_uniform("material.has_diffuse_texture", False)
        
        if self.specular_texture is not None:
            glActiveTexture(GL_TEXTURE0 + texture_unit)
            glBindTexture(GL_TEXTURE_2D, self.specular_texture)
            shader.set_uniform("material.specular_texture", texture_unit)
            shader.set_uniform("material.has_specular_texture", True)
            texture_unit += 1
        else:
            shader.set_uniform("material.has_specular_texture", False)
        
        if self.normal_texture is not None:
            glActiveTexture(GL_TEXTURE0 + texture_unit)
            glBindTexture(GL_TEXTURE_2D, self.normal_texture)
            shader.set_uniform("material.normal_texture", texture_unit)
            shader.set_uniform("material.has_normal_texture", True)
            texture_unit += 1
        else:
            shader.set_uniform("material.has_normal_texture", False)
        
        if self.emission_texture is not None:
            glActiveTexture(GL_TEXTURE0 + texture_unit)
            glBindTexture(GL_TEXTURE_2D, self.emission_texture)
            shader.set_uniform("material.emission_texture", texture_unit)
            shader.set_uniform("material.has_emission_texture", True)
            texture_unit += 1
        else:
            shader.set_uniform("material.has_emission_texture", False)
        
        # 设置渲染属性
        shader.set_uniform("material.transparent", self.transparent)
        shader.set_uniform("material.alpha_cutoff", self.alpha_cutoff)
        shader.set_uniform("material.receive_shadows", self.receive_shadows)
        
        # 设置自定义属性
        for name, value in self.custom_properties.items():
            shader.set_uniform(f"material.{name}", value)
        
        # 设置渲染状态
        if self.double_sided:
            glDisable(GL_CULL_FACE)
        else:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)
        
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    def clone(self):
        """
        克隆材质
        
        Returns:
            Material: 克隆的材质
        """
        material = Material(self.name + "_clone")
        
        # 复制基本属性
        material.shader = self.shader
        material.color = self.color
        material.specular_color = self.specular_color
        material.shininess = self.shininess
        material.emission_color = self.emission_color
        
        # 复制纹理
        material.diffuse_texture = self.diffuse_texture
        material.specular_texture = self.specular_texture
        material.normal_texture = self.normal_texture
        material.emission_texture = self.emission_texture
        
        # 复制渲染属性
        material.transparent = self.transparent
        material.alpha_cutoff = self.alpha_cutoff
        material.double_sided = self.double_sided
        material.wireframe = self.wireframe
        material.receive_shadows = self.receive_shadows
        material.cast_shadows = self.cast_shadows
        
        # 复制自定义属性
        material.custom_properties = self.custom_properties.copy()
        
        return material
    
    def __str__(self):
        """字符串表示"""
        return f"Material(name={self.name}, shader={self.shader})" 