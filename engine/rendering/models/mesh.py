"""
网格类，封装3D模型的顶点数据和渲染功能
"""

import numpy as np
from OpenGL.GL import *


class Mesh:
    """网格类，封装3D模型的顶点数据和渲染功能"""
    
    def __init__(self, name="Mesh"):
        """
        初始化网格
        
        Args:
            name (str): 网格名称
        """
        self.name = name
        self.vertices = None  # 顶点坐标数组
        self.normals = None  # 法线数组
        self.texcoords = None  # 纹理坐标数组
        self.tangents = None  # 切线数组
        self.colors = None  # 顶点颜色数组
        self.indices = None  # 索引数组
        
        self.vao = None  # 顶点数组对象
        self.vbos = {}  # 顶点缓冲对象字典
        self.ebo = None  # 索引缓冲对象
        
        self.vertex_count = 0  # 顶点数量
        self.index_count = 0  # 索引数量
        self.primitive_type = GL_TRIANGLES  # 图元类型
        
        self.aabb_min = np.array([0.0, 0.0, 0.0])  # 包围盒最小点
        self.aabb_max = np.array([0.0, 0.0, 0.0])  # 包围盒最大点
        
        self.sub_meshes = []  # 子网格列表
    
    def set_vertices(self, vertices):
        """
        设置顶点坐标
        
        Args:
            vertices (numpy.ndarray): 顶点坐标数组，形状为 (n, 3)
        """
        self.vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = len(self.vertices)
        
        # 计算包围盒
        if self.vertex_count > 0:
            self.aabb_min = np.min(self.vertices, axis=0)
            self.aabb_max = np.max(self.vertices, axis=0)
    
    def set_normals(self, normals):
        """
        设置法线
        
        Args:
            normals (numpy.ndarray): 法线数组，形状为 (n, 3)
        """
        self.normals = np.array(normals, dtype=np.float32)
    
    def set_texcoords(self, texcoords):
        """
        设置纹理坐标
        
        Args:
            texcoords (numpy.ndarray): 纹理坐标数组，形状为 (n, 2)
        """
        self.texcoords = np.array(texcoords, dtype=np.float32)
    
    def set_tangents(self, tangents):
        """
        设置切线
        
        Args:
            tangents (numpy.ndarray): 切线数组，形状为 (n, 3)
        """
        self.tangents = np.array(tangents, dtype=np.float32)
    
    def set_colors(self, colors):
        """
        设置顶点颜色
        
        Args:
            colors (numpy.ndarray): 顶点颜色数组，形状为 (n, 4)
        """
        self.colors = np.array(colors, dtype=np.float32)
    
    def set_indices(self, indices):
        """
        设置索引
        
        Args:
            indices (numpy.ndarray): 索引数组
        """
        self.indices = np.array(indices, dtype=np.uint32)
        self.index_count = len(self.indices)
    
    def set_primitive_type(self, primitive_type):
        """
        设置图元类型
        
        Args:
            primitive_type (int): 图元类型，如 GL_TRIANGLES, GL_LINES 等
        """
        self.primitive_type = primitive_type
    
    def add_sub_mesh(self, sub_mesh):
        """
        添加子网格
        
        Args:
            sub_mesh (Mesh): 子网格
        """
        self.sub_meshes.append(sub_mesh)
    
    def calculate_normals(self):
        """计算法线"""
        if self.vertices is None:
            return
        
        # 如果没有索引，创建索引
        if self.indices is None:
            self.indices = np.arange(self.vertex_count, dtype=np.uint32)
            self.index_count = self.vertex_count
        
        # 创建法线数组
        self.normals = np.zeros((self.vertex_count, 3), dtype=np.float32)
        
        # 计算每个面的法线，并累加到顶点
        for i in range(0, self.index_count, 3):
            i1, i2, i3 = self.indices[i:i+3]
            
            v1 = self.vertices[i1]
            v2 = self.vertices[i2]
            v3 = self.vertices[i3]
            
            # 计算面法线
            edge1 = v2 - v1
            edge2 = v3 - v1
            normal = np.cross(edge1, edge2)
            
            # 累加到顶点
            self.normals[i1] += normal
            self.normals[i2] += normal
            self.normals[i3] += normal
        
        # 归一化
        lengths = np.sqrt(np.sum(self.normals * self.normals, axis=1))
        lengths = np.where(lengths == 0, 1, lengths)  # 避免除以零
        self.normals = self.normals / lengths[:, np.newaxis]
    
    def calculate_tangents(self):
        """计算切线"""
        if self.vertices is None or self.normals is None or self.texcoords is None:
            return
        
        # 如果没有索引，创建索引
        if self.indices is None:
            self.indices = np.arange(self.vertex_count, dtype=np.uint32)
            self.index_count = self.vertex_count
        
        # 创建切线数组
        self.tangents = np.zeros((self.vertex_count, 3), dtype=np.float32)
        
        # 计算每个面的切线，并累加到顶点
        for i in range(0, self.index_count, 3):
            i1, i2, i3 = self.indices[i:i+3]
            
            v1 = self.vertices[i1]
            v2 = self.vertices[i2]
            v3 = self.vertices[i3]
            
            w1 = self.texcoords[i1]
            w2 = self.texcoords[i2]
            w3 = self.texcoords[i3]
            
            # 计算边
            edge1 = v2 - v1
            edge2 = v3 - v1
            
            # 计算纹理坐标差
            delta_u1 = w2[0] - w1[0]
            delta_v1 = w2[1] - w1[1]
            delta_u2 = w3[0] - w1[0]
            delta_v2 = w3[1] - w1[1]
            
            # 计算切线
            f = 1.0 / (delta_u1 * delta_v2 - delta_u2 * delta_v1)
            
            tangent = np.zeros(3, dtype=np.float32)
            tangent[0] = f * (delta_v2 * edge1[0] - delta_v1 * edge2[0])
            tangent[1] = f * (delta_v2 * edge1[1] - delta_v1 * edge2[1])
            tangent[2] = f * (delta_v2 * edge1[2] - delta_v1 * edge2[2])
            
            # 累加到顶点
            self.tangents[i1] += tangent
            self.tangents[i2] += tangent
            self.tangents[i3] += tangent
        
        # 归一化
        lengths = np.sqrt(np.sum(self.tangents * self.tangents, axis=1))
        lengths = np.where(lengths == 0, 1, lengths)  # 避免除以零
        self.tangents = self.tangents / lengths[:, np.newaxis]
        
        # 使切线垂直于法线
        for i in range(self.vertex_count):
            normal = self.normals[i]
            tangent = self.tangents[i]
            
            # 格拉姆-施密特正交化
            t = tangent - normal * np.dot(normal, tangent)
            
            # 归一化
            length = np.sqrt(np.sum(t * t))
            if length > 0:
                self.tangents[i] = t / length
    
    def create_buffers(self):
        """创建OpenGL缓冲对象"""
        # 如果已创建，先删除
        self.delete_buffers()
        
        # 创建顶点数组对象
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # 创建顶点缓冲对象
        if self.vertices is not None:
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(0)
            self.vbos["vertices"] = vbo
        
        if self.normals is not None:
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, self.normals.nbytes, self.normals, GL_STATIC_DRAW)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(1)
            self.vbos["normals"] = vbo
        
        if self.texcoords is not None:
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, self.texcoords.nbytes, self.texcoords, GL_STATIC_DRAW)
            glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(2)
            self.vbos["texcoords"] = vbo
        
        if self.tangents is not None:
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, self.tangents.nbytes, self.tangents, GL_STATIC_DRAW)
            glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(3)
            self.vbos["tangents"] = vbo
        
        if self.colors is not None:
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
            glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(4)
            self.vbos["colors"] = vbo
        
        # 创建索引缓冲对象
        if self.indices is not None:
            self.ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        # 解绑顶点数组对象
        glBindVertexArray(0)
        
        # 为子网格创建缓冲
        for sub_mesh in self.sub_meshes:
            sub_mesh.create_buffers()
    
    def render(self):
        """渲染网格"""
        # 如果没有顶点数组对象，创建
        if self.vao is None:
            self.create_buffers()
        
        # 绑定顶点数组对象
        glBindVertexArray(self.vao)
        
        # 渲染
        if self.indices is not None:
            glDrawElements(self.primitive_type, self.index_count, GL_UNSIGNED_INT, None)
        else:
            glDrawArrays(self.primitive_type, 0, self.vertex_count)
        
        # 解绑顶点数组对象
        glBindVertexArray(0)
        
        # 渲染子网格
        for sub_mesh in self.sub_meshes:
            sub_mesh.render()
    
    def delete_buffers(self):
        """删除OpenGL缓冲对象"""
        # 删除顶点缓冲对象
        for vbo in self.vbos.values():
            glDeleteBuffers(1, [vbo])
        
        self.vbos.clear()
        
        # 删除索引缓冲对象
        if self.ebo is not None:
            glDeleteBuffers(1, [self.ebo])
            self.ebo = None
        
        # 删除顶点数组对象
        if self.vao is not None:
            glDeleteVertexArrays(1, [self.vao])
            self.vao = None
        
        # 删除子网格的缓冲
        for sub_mesh in self.sub_meshes:
            sub_mesh.delete_buffers()
    
    def get_aabb(self):
        """
        获取轴对齐包围盒
        
        Returns:
            tuple: (min_point, max_point)
        """
        return (self.aabb_min, self.aabb_max)
    
    def get_center(self):
        """
        获取中心点
        
        Returns:
            numpy.ndarray: 中心点坐标
        """
        return (self.aabb_min + self.aabb_max) * 0.5
    
    def get_size(self):
        """
        获取大小
        
        Returns:
            numpy.ndarray: 大小
        """
        return self.aabb_max - self.aabb_min
    
    def __del__(self):
        """析构函数"""
        self.delete_buffers() 