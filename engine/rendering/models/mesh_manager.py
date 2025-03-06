"""
网格管理器，负责加载和管理3D模型
"""

import os
import numpy as np
from OpenGL.GL import *

from engine.rendering.models.mesh import Mesh


class MeshManager:
    """网格管理器，负责加载和管理3D模型"""
    
    def __init__(self):
        """初始化网格管理器"""
        self.meshes = {}  # 网格缓存
        self.mesh_paths = {}  # 网格路径
        
        # 设置默认网格路径
        self._set_default_mesh_paths()
        
        # 创建默认网格
        self._create_default_meshes()
    
    def _set_default_mesh_paths(self):
        """设置默认网格路径"""
        # 获取模型目录
        model_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "assets", "models")
        
        # 设置默认网格路径
        self.mesh_paths = {
            "cube": os.path.join(model_dir, "cube.obj"),
            "sphere": os.path.join(model_dir, "sphere.obj"),
            "plane": os.path.join(model_dir, "plane.obj"),
            "quad": os.path.join(model_dir, "quad.obj")
        }
    
    def _create_default_meshes(self):
        """创建默认网格"""
        # 创建立方体
        self._create_cube()
        
        # 创建球体
        self._create_sphere()
        
        # 创建平面
        self._create_plane()
        
        # 创建四边形
        self._create_quad()
    
    def _create_cube(self):
        """创建立方体网格"""
        mesh = Mesh("cube")
        
        # 顶点坐标
        vertices = np.array([
            # 前面
            [-0.5, -0.5,  0.5],
            [ 0.5, -0.5,  0.5],
            [ 0.5,  0.5,  0.5],
            [-0.5,  0.5,  0.5],
            # 后面
            [-0.5, -0.5, -0.5],
            [ 0.5, -0.5, -0.5],
            [ 0.5,  0.5, -0.5],
            [-0.5,  0.5, -0.5],
            # 左面
            [-0.5, -0.5, -0.5],
            [-0.5, -0.5,  0.5],
            [-0.5,  0.5,  0.5],
            [-0.5,  0.5, -0.5],
            # 右面
            [ 0.5, -0.5, -0.5],
            [ 0.5, -0.5,  0.5],
            [ 0.5,  0.5,  0.5],
            [ 0.5,  0.5, -0.5],
            # 上面
            [-0.5,  0.5,  0.5],
            [ 0.5,  0.5,  0.5],
            [ 0.5,  0.5, -0.5],
            [-0.5,  0.5, -0.5],
            # 下面
            [-0.5, -0.5,  0.5],
            [ 0.5, -0.5,  0.5],
            [ 0.5, -0.5, -0.5],
            [-0.5, -0.5, -0.5]
        ], dtype=np.float32)
        
        # 法线
        normals = np.array([
            # 前面
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            # 后面
            [0.0, 0.0, -1.0],
            [0.0, 0.0, -1.0],
            [0.0, 0.0, -1.0],
            [0.0, 0.0, -1.0],
            # 左面
            [-1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            [-1.0, 0.0, 0.0],
            # 右面
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            # 上面
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            # 下面
            [0.0, -1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, -1.0, 0.0]
        ], dtype=np.float32)
        
        # 纹理坐标
        texcoords = np.array([
            # 前面
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
            # 后面
            [1.0, 0.0],
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            # 左面
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0],
            # 右面
            [1.0, 0.0],
            [0.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            # 上面
            [0.0, 1.0],
            [1.0, 1.0],
            [1.0, 0.0],
            [0.0, 0.0],
            # 下面
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ], dtype=np.float32)
        
        # 索引
        indices = np.array([
            # 前面
            0, 1, 2, 2, 3, 0,
            # 后面
            4, 5, 6, 6, 7, 4,
            # 左面
            8, 9, 10, 10, 11, 8,
            # 右面
            12, 13, 14, 14, 15, 12,
            # 上面
            16, 17, 18, 18, 19, 16,
            # 下面
            20, 21, 22, 22, 23, 20
        ], dtype=np.uint32)
        
        # 设置网格数据
        mesh.set_vertices(vertices)
        mesh.set_normals(normals)
        mesh.set_texcoords(texcoords)
        mesh.set_indices(indices)
        
        # 计算切线
        mesh.calculate_tangents()
        
        # 添加到缓存
        self.meshes["cube"] = mesh
    
    def _create_sphere(self):
        """创建球体网格"""
        mesh = Mesh("sphere")
        
        # 球体参数
        radius = 0.5
        stacks = 16
        slices = 32
        
        # 顶点、法线、纹理坐标和索引列表
        vertices = []
        normals = []
        texcoords = []
        indices = []
        
        # 生成顶点数据
        for i in range(stacks + 1):
            v = i / stacks
            phi = v * np.pi
            
            for j in range(slices + 1):
                u = j / slices
                theta = u * 2 * np.pi
                
                # 球面坐标转笛卡尔坐标
                x = radius * np.sin(phi) * np.cos(theta)
                y = radius * np.cos(phi)
                z = radius * np.sin(phi) * np.sin(theta)
                
                # 顶点坐标
                vertices.append([x, y, z])
                
                # 法线（归一化的顶点坐标）
                nx = np.sin(phi) * np.cos(theta)
                ny = np.cos(phi)
                nz = np.sin(phi) * np.sin(theta)
                normals.append([nx, ny, nz])
                
                # 纹理坐标
                texcoords.append([u, v])
        
        # 生成索引
        for i in range(stacks):
            for j in range(slices):
                # 当前行的第一个顶点索引
                first = i * (slices + 1) + j
                # 下一行的第一个顶点索引
                second = first + slices + 1
                
                # 第一个三角形
                indices.append(first)
                indices.append(second)
                indices.append(first + 1)
                
                # 第二个三角形
                indices.append(second)
                indices.append(second + 1)
                indices.append(first + 1)
        
        # 设置网格数据
        mesh.set_vertices(np.array(vertices, dtype=np.float32))
        mesh.set_normals(np.array(normals, dtype=np.float32))
        mesh.set_texcoords(np.array(texcoords, dtype=np.float32))
        mesh.set_indices(np.array(indices, dtype=np.uint32))
        
        # 计算切线
        mesh.calculate_tangents()
        
        # 添加到缓存
        self.meshes["sphere"] = mesh
    
    def _create_plane(self):
        """创建平面网格"""
        mesh = Mesh("plane")
        
        # 顶点坐标
        vertices = np.array([
            [-0.5, 0.0, -0.5],
            [ 0.5, 0.0, -0.5],
            [ 0.5, 0.0,  0.5],
            [-0.5, 0.0,  0.5]
        ], dtype=np.float32)
        
        # 法线
        normals = np.array([
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0]
        ], dtype=np.float32)
        
        # 纹理坐标
        texcoords = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ], dtype=np.float32)
        
        # 索引
        indices = np.array([
            0, 1, 2, 2, 3, 0
        ], dtype=np.uint32)
        
        # 设置网格数据
        mesh.set_vertices(vertices)
        mesh.set_normals(normals)
        mesh.set_texcoords(texcoords)
        mesh.set_indices(indices)
        
        # 计算切线
        mesh.calculate_tangents()
        
        # 添加到缓存
        self.meshes["plane"] = mesh
    
    def _create_quad(self):
        """创建四边形网格"""
        mesh = Mesh("quad")
        
        # 顶点坐标
        vertices = np.array([
            [-0.5, -0.5, 0.0],
            [ 0.5, -0.5, 0.0],
            [ 0.5,  0.5, 0.0],
            [-0.5,  0.5, 0.0]
        ], dtype=np.float32)
        
        # 法线
        normals = np.array([
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0]
        ], dtype=np.float32)
        
        # 纹理坐标
        texcoords = np.array([
            [0.0, 0.0],
            [1.0, 0.0],
            [1.0, 1.0],
            [0.0, 1.0]
        ], dtype=np.float32)
        
        # 索引
        indices = np.array([
            0, 1, 2, 2, 3, 0
        ], dtype=np.uint32)
        
        # 设置网格数据
        mesh.set_vertices(vertices)
        mesh.set_normals(normals)
        mesh.set_texcoords(texcoords)
        mesh.set_indices(indices)
        
        # 计算切线
        mesh.calculate_tangents()
        
        # 添加到缓存
        self.meshes["quad"] = mesh
    
    def load_mesh(self, name):
        """
        加载网格
        
        Args:
            name (str): 网格名称
            
        Returns:
            Mesh: 网格实例，如果加载失败则返回None
        """
        # 如果已加载，直接返回
        if name in self.meshes:
            return self.meshes[name]
        
        # 检查是否有预定义路径
        if name not in self.mesh_paths:
            print(f"未找到网格路径: {name}")
            return None
        
        # 获取网格路径
        mesh_path = self.mesh_paths[name]
        
        # 加载网格
        try:
            # 根据文件扩展名选择加载方法
            ext = os.path.splitext(mesh_path)[1].lower()
            
            if ext == ".obj":
                mesh = self._load_obj(mesh_path, name)
            elif ext == ".fbx":
                mesh = self._load_fbx(mesh_path, name)
            else:
                print(f"不支持的文件格式: {ext}")
                return None
            
            # 缓存网格
            if mesh:
                self.meshes[name] = mesh
            
            return mesh
        
        except Exception as e:
            print(f"加载网格失败: {name}, {e}")
            return None
    
    def _load_obj(self, file_path, name):
        """
        加载OBJ文件
        
        Args:
            file_path (str): 文件路径
            name (str): 网格名称
            
        Returns:
            Mesh: 网格实例，如果加载失败则返回None
        """
        # 创建网格
        mesh = Mesh(name)
        
        # 顶点、法线、纹理坐标和索引列表
        vertices = []
        normals = []
        texcoords = []
        indices = []
        
        # 顶点、法线和纹理坐标数据
        v_data = []
        vn_data = []
        vt_data = []
        
        # 读取OBJ文件
        with open(file_path, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                
                values = line.split()
                if not values:
                    continue
                
                if values[0] == "v":
                    v_data.append([float(values[1]), float(values[2]), float(values[3])])
                elif values[0] == "vn":
                    vn_data.append([float(values[1]), float(values[2]), float(values[3])])
                elif values[0] == "vt":
                    vt_data.append([float(values[1]), float(values[2]) if len(values) > 2 else 0.0])
                elif values[0] == "f":
                    # 面数据
                    face_indices = []
                    for v in values[1:]:
                        w = v.split("/")
                        # OBJ索引从1开始，需要减1
                        vi = int(w[0]) - 1
                        vti = int(w[1]) - 1 if len(w) > 1 and w[1] else -1
                        vni = int(w[2]) - 1 if len(w) > 2 and w[2] else -1
                        
                        # 添加顶点数据
                        vertices.append(v_data[vi])
                        
                        # 添加纹理坐标
                        if vti >= 0:
                            texcoords.append(vt_data[vti])
                        else:
                            texcoords.append([0.0, 0.0])
                        
                        # 添加法线
                        if vni >= 0:
                            normals.append(vn_data[vni])
                        else:
                            normals.append([0.0, 0.0, 0.0])
                        
                        # 添加索引
                        face_indices.append(len(vertices) - 1)
                    
                    # 三角化面
                    for i in range(1, len(face_indices) - 1):
                        indices.append(face_indices[0])
                        indices.append(face_indices[i])
                        indices.append(face_indices[i + 1])
        
        # 设置网格数据
        mesh.set_vertices(np.array(vertices, dtype=np.float32))
        
        if normals:
            mesh.set_normals(np.array(normals, dtype=np.float32))
        else:
            mesh.calculate_normals()
        
        if texcoords:
            mesh.set_texcoords(np.array(texcoords, dtype=np.float32))
        
        mesh.set_indices(np.array(indices, dtype=np.uint32))
        
        # 计算切线
        if texcoords:
            mesh.calculate_tangents()
        
        return mesh
    
    def _load_fbx(self, file_path, name):
        """
        加载FBX文件
        
        Args:
            file_path (str): 文件路径
            name (str): 网格名称
            
        Returns:
            Mesh: 网格实例，如果加载失败则返回None
        """
        # 这里简化处理，实际应该使用FBX SDK或其他库加载FBX文件
        print("FBX加载功能尚未实现")
        return None
    
    def get_mesh(self, name):
        """
        获取网格
        
        Args:
            name (str): 网格名称
            
        Returns:
            Mesh: 网格实例，如果不存在则返回None
        """
        return self.meshes.get(name)
    
    def add_mesh(self, mesh):
        """
        添加网格
        
        Args:
            mesh (Mesh): 网格实例
        """
        self.meshes[mesh.name] = mesh
    
    def add_mesh_path(self, name, path):
        """
        添加网格路径
        
        Args:
            name (str): 网格名称
            path (str): 网格文件路径
        """
        self.mesh_paths[name] = path
    
    def reload_mesh(self, name):
        """
        重新加载网格
        
        Args:
            name (str): 网格名称
            
        Returns:
            Mesh: 网格实例，如果重新加载失败则返回None
        """
        # 如果已加载，先删除
        if name in self.meshes:
            self.meshes[name].delete_buffers()
            del self.meshes[name]
        
        # 重新加载
        return self.load_mesh(name)
    
    def delete_mesh(self, name):
        """
        删除网格
        
        Args:
            name (str): 网格名称
            
        Returns:
            bool: 是否成功删除
        """
        if name in self.meshes:
            self.meshes[name].delete_buffers()
            del self.meshes[name]
            return True
        
        return False
    
    def delete_all_meshes(self):
        """删除所有网格"""
        for mesh in self.meshes.values():
            mesh.delete_buffers()
        
        self.meshes.clear()
    
    def __del__(self):
        """析构函数"""
        self.delete_all_meshes() 