"""
着色器类，封装OpenGL着色器程序
"""

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np


class Shader:
    """着色器类，封装OpenGL着色器程序"""
    
    def __init__(self):
        """初始化着色器"""
        self.program = None  # 着色器程序
        self.uniforms = {}  # 统一变量位置缓存
    
    def create(self, vertex_source, fragment_source):
        """
        创建着色器程序
        
        Args:
            vertex_source (str): 顶点着色器源代码
            fragment_source (str): 片段着色器源代码
            
        Returns:
            bool: 是否成功创建
        """
        try:
            # 编译顶点着色器
            vertex_shader = compileShader(vertex_source, GL_VERTEX_SHADER)
            
            # 编译片段着色器
            fragment_shader = compileShader(fragment_source, GL_FRAGMENT_SHADER)
            
            # 链接着色器程序
            self.program = compileProgram(vertex_shader, fragment_shader)
            
            # 删除着色器对象
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            
            return True
        
        except Exception as e:
            print(f"创建着色器程序失败: {e}")
            return False
    
    def use(self):
        """使用着色器程序"""
        if self.program:
            glUseProgram(self.program)
    
    def get_uniform_location(self, name):
        """
        获取统一变量位置
        
        Args:
            name (str): 统一变量名称
            
        Returns:
            int: 统一变量位置
        """
        # 如果已缓存，直接返回
        if name in self.uniforms:
            return self.uniforms[name]
        
        # 获取位置
        location = glGetUniformLocation(self.program, name)
        
        # 缓存位置
        self.uniforms[name] = location
        
        return location
    
    def set_uniform(self, name, value):
        """
        设置统一变量
        
        Args:
            name (str): 统一变量名称
            value: 统一变量值
        """
        if not self.program:
            return
        
        # 获取位置
        location = self.get_uniform_location(name)
        
        if location == -1:
            return
        
        # 根据值类型设置统一变量
        if isinstance(value, bool):
            glUniform1i(location, int(value))
        elif isinstance(value, int):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, (list, tuple)):
            if len(value) == 2:
                glUniform2f(location, *value)
            elif len(value) == 3:
                glUniform3f(location, *value)
            elif len(value) == 4:
                glUniform4f(location, *value)
            elif len(value) == 9:
                glUniformMatrix3fv(location, 1, GL_FALSE, np.array(value, dtype=np.float32))
            elif len(value) == 16:
                glUniformMatrix4fv(location, 1, GL_FALSE, np.array(value, dtype=np.float32))
        elif isinstance(value, np.ndarray):
            if value.size == 2:
                glUniform2f(location, *value)
            elif value.size == 3:
                glUniform3f(location, *value)
            elif value.size == 4:
                glUniform4f(location, *value)
            elif value.size == 9:
                glUniformMatrix3fv(location, 1, GL_FALSE, value)
            elif value.size == 16:
                glUniformMatrix4fv(location, 1, GL_FALSE, value)
    
    def set_uniform_array(self, name, values, element_type="float"):
        """
        设置统一变量数组
        
        Args:
            name (str): 统一变量名称
            values (list): 统一变量值列表
            element_type (str): 元素类型，可选值为 "float", "int", "vec2", "vec3", "vec4"
        """
        if not self.program:
            return
        
        # 获取位置
        location = self.get_uniform_location(name)
        
        if location == -1:
            return
        
        # 根据元素类型设置统一变量数组
        if element_type == "float":
            glUniform1fv(location, len(values), np.array(values, dtype=np.float32))
        elif element_type == "int":
            glUniform1iv(location, len(values), np.array(values, dtype=np.int32))
        elif element_type == "vec2":
            glUniform2fv(location, len(values), np.array(values, dtype=np.float32).flatten())
        elif element_type == "vec3":
            glUniform3fv(location, len(values), np.array(values, dtype=np.float32).flatten())
        elif element_type == "vec4":
            glUniform4fv(location, len(values), np.array(values, dtype=np.float32).flatten())
    
    def set_uniform_matrix(self, name, matrix, transpose=False):
        """
        设置统一变量矩阵
        
        Args:
            name (str): 统一变量名称
            matrix (numpy.ndarray): 矩阵
            transpose (bool): 是否转置
        """
        if not self.program:
            return
        
        # 获取位置
        location = self.get_uniform_location(name)
        
        if location == -1:
            return
        
        # 根据矩阵大小设置统一变量矩阵
        if matrix.size == 4:  # 2x2
            glUniformMatrix2fv(location, 1, transpose, matrix)
        elif matrix.size == 9:  # 3x3
            glUniformMatrix3fv(location, 1, transpose, matrix)
        elif matrix.size == 16:  # 4x4
            glUniformMatrix4fv(location, 1, transpose, matrix)
    
    def delete(self):
        """删除着色器程序"""
        if self.program:
            glDeleteProgram(self.program)
            self.program = None
            self.uniforms.clear()
    
    def __del__(self):
        """析构函数"""
        self.delete() 