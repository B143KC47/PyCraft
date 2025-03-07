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
            print(f"无法设置统一变量 {name}: 着色器程序未初始化")
            return
        
        # 获取位置
        location = self.get_uniform_location(name)
        
        if location == -1:
            # 统一变量不存在或未使用
            return
        
        # 根据值类型设置统一变量
        try:
            if isinstance(value, (int, bool)):
                glUniform1i(location, value)
            elif isinstance(value, float):
                glUniform1f(location, value)
            elif isinstance(value, (tuple, list)):
                # 判断元素类型和长度
                if len(value) == 2:
                    if isinstance(value[0], int):
                        glUniform2i(location, value[0], value[1])
                    else:
                        glUniform2f(location, value[0], value[1])
                elif len(value) == 3:
                    if isinstance(value[0], int):
                        glUniform3i(location, value[0], value[1], value[2])
                    else:
                        glUniform3f(location, value[0], value[1], value[2])
                elif len(value) == 4:
                    if isinstance(value[0], int):
                        glUniform4i(location, value[0], value[1], value[2], value[3])
                    else:
                        glUniform4f(location, value[0], value[1], value[2], value[3])
                else:
                    print(f"不支持的向量维度: {len(value)}")
            elif hasattr(value, 'size') and hasattr(value, 'dtype'):
                # NumPy数组
                if value.size == 4:
                    # 4x4矩阵
                    if value.shape == (4, 4):
                        glUniformMatrix4fv(location, 1, GL_FALSE, value)
                    else:
                        glUniform4fv(location, 1, value)
                elif value.size == 16:
                    # 可能是展平的4x4矩阵
                    glUniformMatrix4fv(location, 1, GL_FALSE, value)
                elif value.size == 9:
                    # 3x3矩阵
                    glUniformMatrix3fv(location, 1, GL_FALSE, value)
                elif value.size == 3:
                    glUniform3fv(location, 1, value)
                elif value.size == 2:
                    glUniform2fv(location, 1, value)
                else:
                    print(f"不支持的数组大小: {value.size}")
            else:
                print(f"不支持的统一变量类型: {type(value)}")
        except Exception as e:
            print(f"设置统一变量 {name} 失败: {e}")
    
    def set_uniform_matrix4(self, name, matrix):
        """
        设置4x4矩阵统一变量
        
        Args:
            name (str): 统一变量名称
            matrix: 4x4矩阵
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniformMatrix4fv(location, 1, GL_FALSE, matrix)
    
    def set_uniform_matrix3(self, name, matrix):
        """
        设置3x3矩阵统一变量
        
        Args:
            name (str): 统一变量名称
            matrix: 3x3矩阵
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniformMatrix3fv(location, 1, GL_FALSE, matrix)
    
    def set_uniform_int(self, name, value):
        """
        设置整数统一变量
        
        Args:
            name (str): 统一变量名称
            value (int): 整数值
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1i(location, value)
    
    def set_uniform_float(self, name, value):
        """
        设置浮点数统一变量
        
        Args:
            name (str): 统一变量名称
            value (float): 浮点数值
        """
        location = self.get_uniform_location(name)
        if location != -1:
            glUniform1f(location, value)
    
    def set_uniform_vec2(self, name, x, y=None):
        """
        设置二维向量统一变量
        
        Args:
            name (str): 统一变量名称
            x: x分量或二维向量
            y (float): y分量，可选
        """
        location = self.get_uniform_location(name)
        if location != -1:
            if y is None and (isinstance(x, (tuple, list)) or hasattr(x, '__getitem__')):
                glUniform2f(location, x[0], x[1])
            else:
                glUniform2f(location, x, y)
    
    def set_uniform_vec3(self, name, x, y=None, z=None):
        """
        设置三维向量统一变量
        
        Args:
            name (str): 统一变量名称
            x: x分量或三维向量
            y (float): y分量，可选
            z (float): z分量，可选
        """
        location = self.get_uniform_location(name)
        if location != -1:
            if y is None and z is None and (isinstance(x, (tuple, list)) or hasattr(x, '__getitem__')):
                glUniform3f(location, x[0], x[1], x[2])
            else:
                glUniform3f(location, x, y, z)
    
    def set_uniform_vec4(self, name, x, y=None, z=None, w=None):
        """
        设置四维向量统一变量
        
        Args:
            name (str): 统一变量名称
            x: x分量或四维向量
            y (float): y分量，可选
            z (float): z分量，可选
            w (float): w分量，可选
        """
        location = self.get_uniform_location(name)
        if location != -1:
            if y is None and z is None and w is None and (isinstance(x, (tuple, list)) or hasattr(x, '__getitem__')):
                glUniform4f(location, x[0], x[1], x[2], x[3])
            else:
                glUniform4f(location, x, y, z, w)
    
    def delete(self):
        """删除着色器程序"""
        if self.program:
            glDeleteProgram(self.program)
            self.program = None
            self.uniforms.clear()
    
    def __del__(self):
        """析构函数"""
        self.delete()