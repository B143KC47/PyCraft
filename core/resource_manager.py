import pygame
import os
import json
from OpenGL.GL import *
import numpy as np

class ResourceManager:
    """资源管理器，负责加载和管理游戏资源"""
    
    def __init__(self):
        self.resources = {}
        self.textures = {}
        self.models = {}
        self.shaders = {}
        self.sounds = {}
        self.fonts = {}
    
    def load_texture(self, resource_id, file_path):
        """加载纹理"""
        try:
            if not os.path.exists(file_path):
                print(f"Error: Texture file not found: {file_path}")
                return False
                
            # 使用Pygame加载图像
            surface = pygame.image.load(file_path)
            texture_data = pygame.image.tostring(surface, "RGBA", True)
            width = surface.get_width()
            height = surface.get_height()
            
            # 创建OpenGL纹理
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            
            # 设置纹理参数
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            
            # 上传纹理数据
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            
            # 存储纹理信息
            self.textures[resource_id] = {
                "id": texture_id,
                "width": width,
                "height": height,
                "path": file_path
            }
            
            self.resources[resource_id] = {
                "type": "texture",
                "data": self.textures[resource_id]
            }
            
            return True
        except Exception as e:
            print(f"Error loading texture {file_path}: {e}")
            return False
    
    def load_model(self, resource_id, file_path):
        """加载3D模型"""
        try:
            if not os.path.exists(file_path):
                print(f"Error: Model file not found: {file_path}")
                return False
                
            # 这里应该实现模型加载逻辑
            # 简化版本，仅作为示例
            # 实际应用中应该使用专门的模型加载库，如PyAssimp
            
            # 假设模型文件是一个简单的JSON格式，包含顶点和索引
            with open(file_path, 'r') as f:
                model_data = json.load(f)
            
            vertices = np.array(model_data.get("vertices", []), dtype=np.float32)
            indices = np.array(model_data.get("indices", []), dtype=np.uint32)
            normals = np.array(model_data.get("normals", []), dtype=np.float32)
            uvs = np.array(model_data.get("uvs", []), dtype=np.float32)
            
            # 创建VAO和VBO
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            
            # 顶点缓冲
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            
            # 设置顶点属性
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
            glEnableVertexAttribArray(0)
            
            # 如果有法线
            if normals.size > 0:
                nbo = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, nbo)
                glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
                
                glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
                glEnableVertexAttribArray(1)
            
            # 如果有UV坐标
            if uvs.size > 0:
                tbo = glGenBuffers(1)
                glBindBuffer(GL_ARRAY_BUFFER, tbo)
                glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_STATIC_DRAW)
                
                glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 0, None)
                glEnableVertexAttribArray(2)
            
            # 如果有索引
            if indices.size > 0:
                ebo = glGenBuffers(1)
                glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
                glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
            
            # 解绑VAO
            glBindVertexArray(0)
            
            # 存储模型信息
            self.models[resource_id] = {
                "vao": vao,
                "vbo": vbo,
                "ebo": ebo if indices.size > 0 else None,
                "vertex_count": len(vertices) // 3,
                "index_count": len(indices),
                "has_indices": indices.size > 0,
                "path": file_path
            }
            
            self.resources[resource_id] = {
                "type": "model",
                "data": self.models[resource_id]
            }
            
            return True
        except Exception as e:
            print(f"Error loading model {file_path}: {e}")
            return False
    
    def load_shader(self, resource_id, vertex_path, fragment_path):
        """加载着色器程序"""
        try:
            if not os.path.exists(vertex_path) or not os.path.exists(fragment_path):
                print(f"Error: Shader files not found: {vertex_path} or {fragment_path}")
                return False
                
            # 读取着色器源码
            with open(vertex_path, 'r') as f:
                vertex_source = f.read()
                
            with open(fragment_path, 'r') as f:
                fragment_source = f.read()
            
            # 编译顶点着色器
            vertex_shader = glCreateShader(GL_VERTEX_SHADER)
            glShaderSource(vertex_shader, vertex_source)
            glCompileShader(vertex_shader)
            
            # 检查编译错误
            if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
                error = glGetShaderInfoLog(vertex_shader)
                print(f"Vertex shader compilation error: {error}")
                glDeleteShader(vertex_shader)
                return False
            
            # 编译片段着色器
            fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
            glShaderSource(fragment_shader, fragment_source)
            glCompileShader(fragment_shader)
            
            # 检查编译错误
            if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
                error = glGetShaderInfoLog(fragment_shader)
                print(f"Fragment shader compilation error: {error}")
                glDeleteShader(vertex_shader)
                glDeleteShader(fragment_shader)
                return False
            
            # 创建着色器程序
            shader_program = glCreateProgram()
            glAttachShader(shader_program, vertex_shader)
            glAttachShader(shader_program, fragment_shader)
            glLinkProgram(shader_program)
            
            # 检查链接错误
            if not glGetProgramiv(shader_program, GL_LINK_STATUS):
                error = glGetProgramInfoLog(shader_program)
                print(f"Shader program linking error: {error}")
                glDeleteShader(vertex_shader)
                glDeleteShader(fragment_shader)
                glDeleteProgram(shader_program)
                return False
            
            # 删除着色器对象
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            
            # 存储着色器程序
            self.shaders[resource_id] = {
                "program": shader_program,
                "vertex_path": vertex_path,
                "fragment_path": fragment_path
            }
            
            self.resources[resource_id] = {
                "type": "shader",
                "data": self.shaders[resource_id]
            }
            
            return True
        except Exception as e:
            print(f"Error loading shader: {e}")
            return False
    
    def load_sound(self, resource_id, file_path):
        """加载声音"""
        try:
            if not os.path.exists(file_path):
                print(f"Error: Sound file not found: {file_path}")
                return False
                
            # 初始化Pygame混音器
            if not pygame.mixer.get_init():
                pygame.mixer.init()
                
            # 加载声音
            sound = pygame.mixer.Sound(file_path)
            
            # 存储声音
            self.sounds[resource_id] = {
                "sound": sound,
                "path": file_path
            }
            
            self.resources[resource_id] = {
                "type": "sound",
                "data": self.sounds[resource_id]
            }
            
            return True
        except Exception as e:
            print(f"Error loading sound {file_path}: {e}")
            return False
    
    def load_font(self, resource_id, file_path, size=16):
        """加载字体"""
        try:
            if not os.path.exists(file_path):
                print(f"Error: Font file not found: {file_path}")
                return False
                
            # 加载字体
            font = pygame.font.Font(file_path, size)
            
            # 存储字体
            self.fonts[resource_id] = {
                "font": font,
                "path": file_path,
                "size": size
            }
            
            self.resources[resource_id] = {
                "type": "font",
                "data": self.fonts[resource_id]
            }
            
            return True
        except Exception as e:
            print(f"Error loading font {file_path}: {e}")
            return False
    
    def get_resource(self, resource_id):
        """获取资源"""
        return self.resources.get(resource_id)
    
    def get_texture(self, resource_id):
        """获取纹理"""
        return self.textures.get(resource_id)
    
    def get_model(self, resource_id):
        """获取模型"""
        return self.models.get(resource_id)
    
    def get_shader(self, resource_id):
        """获取着色器程序"""
        return self.shaders.get(resource_id)
    
    def get_sound(self, resource_id):
        """获取声音"""
        return self.sounds.get(resource_id)
    
    def get_font(self, resource_id):
        """获取字体"""
        return self.fonts.get(resource_id)
    
    def cleanup(self):
        """清理资源"""
        # 删除纹理
        for texture in self.textures.values():
            glDeleteTextures(1, [texture["id"]])
        
        # 删除模型
        for model in self.models.values():
            if "vao" in model:
                glDeleteVertexArrays(1, [model["vao"]])
            if "vbo" in model:
                glDeleteBuffers(1, [model["vbo"]])
            if "ebo" in model and model["ebo"] is not None:
                glDeleteBuffers(1, [model["ebo"]])
        
        # 删除着色器程序
        for shader in self.shaders.values():
            glDeleteProgram(shader["program"])
        
        # 清空资源字典
        self.resources.clear()
        self.textures.clear()
        self.models.clear()
        self.shaders.clear()
        self.sounds.clear()
        self.fonts.clear()
