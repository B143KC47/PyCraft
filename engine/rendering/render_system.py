"""
渲染系统，负责3D图形渲染
"""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math

from engine.core.ecs.system import System
from engine.core.ecs.entity import Entity


class RenderSystem(System):
    """渲染系统，负责3D图形渲染"""
    
    def __init__(self):
        """初始化渲染系统"""
        super().__init__()
        self.priority = 100  # 渲染系统优先级较低，在其他系统之后更新
        self.camera = None  # 当前相机
        self.lights = []  # 光源列表
        self.skybox = None  # 天空盒
        self.fog_enabled = False  # 是否启用雾效
        self.fog_color = (0.5, 0.5, 0.5, 1.0)  # 雾的颜色
        self.fog_start = 10.0  # 雾的起始距离
        self.fog_end = 50.0  # 雾的结束距离
        self.ambient_color = (0.2, 0.2, 0.2, 1.0)  # 环境光颜色
        self.clear_color = (0.1, 0.1, 0.1, 1.0)  # 清屏颜色
        self.shader_cache = {}  # 着色器缓存
        self.texture_cache = {}  # 纹理缓存
        self.mesh_cache = {}  # 网格缓存
        self.material_cache = {}  # 材质缓存
        self.render_targets = {}  # 渲染目标
        self.post_processors = []  # 后处理器
        self.width = 0  # 渲染宽度
        self.height = 0  # 渲染高度
        self.aspect_ratio = 1.0  # 宽高比
        self.initialized = False  # 是否已初始化
    
    def initialize(self, width, height):
        """
        初始化渲染系统
        
        Args:
            width (int): 渲染宽度
            height (int): 渲染高度
        """
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        
        # 初始化OpenGL
        glViewport(0, 0, width, height)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # 设置清屏颜色
        glClearColor(*self.clear_color)
        
        # 初始化着色器
        self._init_shaders()
        
        # 初始化默认材质
        self._init_materials()
        
        # 初始化默认网格
        self._init_meshes()
        
        self.initialized = True
    
    def _init_shaders(self):
        """初始化着色器"""
        # 加载默认着色器
        from engine.rendering.shaders.shader_manager import ShaderManager
        shader_manager = ShaderManager()
        
        # 加载基础着色器
        self.shader_cache["default"] = shader_manager.load_shader("default")
        self.shader_cache["skybox"] = shader_manager.load_shader("skybox")
        self.shader_cache["terrain"] = shader_manager.load_shader("terrain")
        self.shader_cache["water"] = shader_manager.load_shader("water")
        self.shader_cache["particle"] = shader_manager.load_shader("particle")
    
    def _init_materials(self):
        """初始化材质"""
        # 加载默认材质
        from engine.rendering.materials.material_manager import MaterialManager
        material_manager = MaterialManager()
        
        # 加载基础材质
        self.material_cache["default"] = material_manager.load_material("default")
        self.material_cache["unlit"] = material_manager.load_material("unlit")
    
    def _init_meshes(self):
        """初始化网格"""
        # 加载默认网格
        from engine.rendering.models.mesh_manager import MeshManager
        mesh_manager = MeshManager()
        
        # 加载基础网格
        self.mesh_cache["cube"] = mesh_manager.load_mesh("cube")
        self.mesh_cache["sphere"] = mesh_manager.load_mesh("sphere")
        self.mesh_cache["plane"] = mesh_manager.load_mesh("plane")
        self.mesh_cache["quad"] = mesh_manager.load_mesh("quad")
    
    def set_camera(self, camera):
        """
        设置当前相机
        
        Args:
            camera: 相机实体或组件
        """
        self.camera = camera
    
    def add_light(self, light):
        """
        添加光源
        
        Args:
            light: 光源实体或组件
        """
        self.lights.append(light)
    
    def remove_light(self, light):
        """
        移除光源
        
        Args:
            light: 光源实体或组件
            
        Returns:
            bool: 是否成功移除
        """
        if light in self.lights:
            self.lights.remove(light)
            return True
        
        return False
    
    def set_skybox(self, skybox):
        """
        设置天空盒
        
        Args:
            skybox: 天空盒实体或组件
        """
        self.skybox = skybox
    
    def set_fog(self, enabled, color=None, start=None, end=None):
        """
        设置雾效
        
        Args:
            enabled (bool): 是否启用雾效
            color (tuple): 雾的颜色，RGBA格式，值范围0-1
            start (float): 雾的起始距离
            end (float): 雾的结束距离
        """
        self.fog_enabled = enabled
        
        if color:
            self.fog_color = color
        
        if start is not None:
            self.fog_start = start
        
        if end is not None:
            self.fog_end = end
    
    def set_ambient_color(self, color):
        """
        设置环境光颜色
        
        Args:
            color (tuple): 环境光颜色，RGBA格式，值范围0-1
        """
        self.ambient_color = color
    
    def set_clear_color(self, color):
        """
        设置清屏颜色
        
        Args:
            color (tuple): 清屏颜色，RGBA格式，值范围0-1
        """
        self.clear_color = color
        glClearColor(*color)
    
    def create_render_target(self, name, width, height, has_depth=True):
        """
        创建渲染目标
        
        Args:
            name (str): 渲染目标名称
            width (int): 宽度
            height (int): 高度
            has_depth (bool): 是否有深度缓冲
            
        Returns:
            int: 渲染目标ID
        """
        # 创建帧缓冲对象
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)
        
        # 创建颜色附件
        color_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, color_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_texture, 0)
        
        # 创建深度附件
        depth_texture = None
        if has_depth:
            depth_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, depth_texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, width, height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, depth_texture, 0)
        
        # 检查帧缓冲是否完整
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print(f"帧缓冲不完整: {name}")
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            return None
        
        # 重置绑定
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # 存储渲染目标
        self.render_targets[name] = {
            "fbo": fbo,
            "color_texture": color_texture,
            "depth_texture": depth_texture,
            "width": width,
            "height": height
        }
        
        return fbo
    
    def get_render_target(self, name):
        """
        获取渲染目标
        
        Args:
            name (str): 渲染目标名称
            
        Returns:
            dict: 渲染目标信息
        """
        return self.render_targets.get(name)
    
    def delete_render_target(self, name):
        """
        删除渲染目标
        
        Args:
            name (str): 渲染目标名称
            
        Returns:
            bool: 是否成功删除
        """
        if name in self.render_targets:
            render_target = self.render_targets[name]
            
            # 删除纹理
            if render_target["color_texture"]:
                glDeleteTextures(1, [render_target["color_texture"]])
            
            if render_target["depth_texture"]:
                glDeleteTextures(1, [render_target["depth_texture"]])
            
            # 删除帧缓冲
            glDeleteFramebuffers(1, [render_target["fbo"]])
            
            # 从字典中移除
            del self.render_targets[name]
            
            return True
        
        return False
    
    def add_post_processor(self, post_processor):
        """
        添加后处理器
        
        Args:
            post_processor: 后处理器
        """
        self.post_processors.append(post_processor)
    
    def remove_post_processor(self, post_processor):
        """
        移除后处理器
        
        Args:
            post_processor: 后处理器
            
        Returns:
            bool: 是否成功移除
        """
        if post_processor in self.post_processors:
            self.post_processors.remove(post_processor)
            return True
        
        return False
    
    def update(self, delta_time):
        """
        更新渲染系统
        
        Args:
            delta_time (float): 帧时间，单位为秒
        """
        # 更新后处理器
        for post_processor in self.post_processors:
            post_processor.update(delta_time)
    
    def render(self, scene):
        """
        渲染场景
        
        Args:
            scene: 要渲染的场景
        """
        if not self.initialized or not scene:
            return
        
        # 如果没有相机，返回
        if not self.camera:
            return
        
        # 清除屏幕
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 设置投影矩阵
        self._set_projection_matrix()
        
        # 设置视图矩阵
        self._set_view_matrix()
        
        # 渲染天空盒
        if self.skybox:
            self._render_skybox()
        
        # 渲染不透明物体
        self._render_opaque_objects(scene)
        
        # 渲染透明物体
        self._render_transparent_objects(scene)
        
        # 应用后处理
        self._apply_post_processing()
    
    def _set_projection_matrix(self):
        """设置投影矩阵"""
        # 获取相机组件
        from engine.core.ecs.components.camera import Camera
        camera_component = None
        
        if isinstance(self.camera, Entity):
            camera_component = self.camera.get_component(Camera)
        elif isinstance(self.camera, Camera):
            camera_component = self.camera
        
        if not camera_component:
            return
        
        # 设置投影矩阵
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        if camera_component.projection_type == "perspective":
            gluPerspective(
                camera_component.fov,
                self.aspect_ratio,
                camera_component.near_plane,
                camera_component.far_plane
            )
        else:  # orthographic
            size = camera_component.ortho_size
            aspect = self.aspect_ratio
            glOrtho(
                -size * aspect, size * aspect,
                -size, size,
                camera_component.near_plane,
                camera_component.far_plane
            )
    
    def _set_view_matrix(self):
        """设置视图矩阵"""
        # 获取相机组件
        from engine.core.ecs.components.camera import Camera
        from engine.core.ecs.components.transform import Transform
        
        camera_component = None
        transform_component = None
        
        if isinstance(self.camera, Entity):
            camera_component = self.camera.get_component(Camera)
            transform_component = self.camera.get_component(Transform)
        elif isinstance(self.camera, Camera):
            camera_component = self.camera
            transform_component = camera_component.entity.get_component(Transform) if camera_component.entity else None
        
        if not camera_component or not transform_component:
            return
        
        # 设置视图矩阵
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # 获取相机位置和方向
        position = transform_component.position
        rotation = transform_component.rotation
        
        # 计算前方向
        forward_x = -math.sin(math.radians(rotation[1])) * math.cos(math.radians(rotation[0]))
        forward_y = math.sin(math.radians(rotation[0]))
        forward_z = -math.cos(math.radians(rotation[1])) * math.cos(math.radians(rotation[0]))
        
        # 计算上方向
        up_x = math.sin(math.radians(rotation[2])) * math.sin(math.radians(rotation[1]))
        up_y = math.cos(math.radians(rotation[2]))
        up_z = math.sin(math.radians(rotation[2])) * math.cos(math.radians(rotation[1]))
        
        # 设置视图
        target = (position[0] + forward_x, position[1] + forward_y, position[2] + forward_z)
        up = (up_x, up_y, up_z)
        
        gluLookAt(
            position[0], position[1], position[2],
            target[0], target[1], target[2],
            up[0], up[1], up[2]
        )
    
    def _render_skybox(self):
        """渲染天空盒"""
        # 禁用深度写入
        glDepthMask(GL_FALSE)
        
        # 使用天空盒着色器
        skybox_shader = self.shader_cache.get("skybox")
        if skybox_shader:
            skybox_shader.use()
        
        # 渲染天空盒
        # 这里简化处理，实际应该使用立方体贴图
        
        # 恢复深度写入
        glDepthMask(GL_TRUE)
    
    def _render_opaque_objects(self, scene):
        """
        渲染不透明物体
        
        Args:
            scene: 要渲染的场景
        """
        # 获取所有有MeshRenderer组件的实体
        from engine.core.ecs.components.mesh_renderer import MeshRenderer
        from engine.core.ecs.components.transform import Transform
        
        entities = scene.get_entities_with_component(MeshRenderer)
        
        # 按材质分组
        opaque_entities = {}
        
        for entity in entities:
            if not entity.enabled:
                continue
            
            mesh_renderer = entity.get_component(MeshRenderer)
            
            if not mesh_renderer or not mesh_renderer.enabled or mesh_renderer.transparent:
                continue
            
            material_name = mesh_renderer.material
            
            if material_name not in opaque_entities:
                opaque_entities[material_name] = []
            
            opaque_entities[material_name].append(entity)
        
        # 渲染每组实体
        for material_name, material_entities in opaque_entities.items():
            material = self.material_cache.get(material_name)
            
            if not material:
                continue
            
            # 使用材质的着色器
            shader = self.shader_cache.get(material.shader)
            
            if not shader:
                continue
            
            shader.use()
            
            # 设置材质属性
            material.apply(shader)
            
            # 设置光照
            self._set_lighting(shader)
            
            # 渲染实体
            for entity in material_entities:
                mesh_renderer = entity.get_component(MeshRenderer)
                transform = entity.get_component(Transform)
                
                if not transform:
                    continue
                
                # 设置模型矩阵
                glPushMatrix()
                
                # 应用变换
                glTranslatef(*transform.position)
                glRotatef(transform.rotation[0], 1, 0, 0)
                glRotatef(transform.rotation[1], 0, 1, 0)
                glRotatef(transform.rotation[2], 0, 0, 1)
                glScalef(*transform.scale)
                
                # 渲染网格
                mesh = self.mesh_cache.get(mesh_renderer.mesh)
                
                if mesh:
                    mesh.render()
                
                glPopMatrix()
    
    def _render_transparent_objects(self, scene):
        """
        渲染透明物体
        
        Args:
            scene: 要渲染的场景
        """
        # 获取所有有MeshRenderer组件的实体
        from engine.core.ecs.components.mesh_renderer import MeshRenderer
        from engine.core.ecs.components.transform import Transform
        
        entities = scene.get_entities_with_component(MeshRenderer)
        
        # 收集透明实体
        transparent_entities = []
        
        for entity in entities:
            if not entity.enabled:
                continue
            
            mesh_renderer = entity.get_component(MeshRenderer)
            
            if not mesh_renderer or not mesh_renderer.enabled or not mesh_renderer.transparent:
                continue
            
            transform = entity.get_component(Transform)
            
            if not transform:
                continue
            
            # 计算与相机的距离
            camera_position = (0, 0, 0)
            
            if isinstance(self.camera, Entity):
                camera_transform = self.camera.get_component(Transform)
                if camera_transform:
                    camera_position = camera_transform.position
            
            # 计算距离
            dx = transform.position[0] - camera_position[0]
            dy = transform.position[1] - camera_position[1]
            dz = transform.position[2] - camera_position[2]
            distance_squared = dx * dx + dy * dy + dz * dz
            
            transparent_entities.append((entity, distance_squared))
        
        # 按距离排序，从远到近渲染
        transparent_entities.sort(key=lambda x: x[1], reverse=True)
        
        # 启用混合
        glEnable(GL_BLEND)
        
        # 渲染透明实体
        for entity, _ in transparent_entities:
            mesh_renderer = entity.get_component(MeshRenderer)
            transform = entity.get_component(Transform)
            
            material = self.material_cache.get(mesh_renderer.material)
            
            if not material:
                continue
            
            # 使用材质的着色器
            shader = self.shader_cache.get(material.shader)
            
            if not shader:
                continue
            
            shader.use()
            
            # 设置材质属性
            material.apply(shader)
            
            # 设置光照
            self._set_lighting(shader)
            
            # 设置模型矩阵
            glPushMatrix()
            
            # 应用变换
            glTranslatef(*transform.position)
            glRotatef(transform.rotation[0], 1, 0, 0)
            glRotatef(transform.rotation[1], 0, 1, 0)
            glRotatef(transform.rotation[2], 0, 0, 1)
            glScalef(*transform.scale)
            
            # 渲染网格
            mesh = self.mesh_cache.get(mesh_renderer.mesh)
            
            if mesh:
                mesh.render()
            
            glPopMatrix()
        
        # 禁用混合
        glDisable(GL_BLEND)
    
    def _set_lighting(self, shader):
        """
        设置光照
        
        Args:
            shader: 着色器
        """
        # 设置环境光
        shader.set_uniform("ambient_color", self.ambient_color)
        
        # 设置雾效
        shader.set_uniform("fog_enabled", self.fog_enabled)
        
        if self.fog_enabled:
            shader.set_uniform("fog_color", self.fog_color)
            shader.set_uniform("fog_start", self.fog_start)
            shader.set_uniform("fog_end", self.fog_end)
        
        # 设置光源
        light_count = min(len(self.lights), 8)  # 最多支持8个光源
        shader.set_uniform("light_count", light_count)
        
        for i in range(light_count):
            light = self.lights[i]
            
            # 获取光源组件
            from engine.core.ecs.components.light import Light
            from engine.core.ecs.components.transform import Transform
            
            light_component = None
            transform_component = None
            
            if isinstance(light, Entity):
                light_component = light.get_component(Light)
                transform_component = light.get_component(Transform)
            elif isinstance(light, Light):
                light_component = light
                transform_component = light_component.entity.get_component(Transform) if light_component.entity else None
            
            if not light_component:
                continue
            
            # 设置光源属性
            position = (0, 0, 0)
            if transform_component:
                position = transform_component.position
            
            shader.set_uniform(f"lights[{i}].position", position)
            shader.set_uniform(f"lights[{i}].color", light_component.color)
            shader.set_uniform(f"lights[{i}].intensity", light_component.intensity)
            shader.set_uniform(f"lights[{i}].range", light_component.range)
            shader.set_uniform(f"lights[{i}].type", light_component.type)
            
            # 如果是聚光灯，设置方向和角度
            if light_component.type == Light.TYPE_SPOT:
                direction = (0, -1, 0)
                if transform_component:
                    # 计算前方向
                    rotation = transform_component.rotation
                    direction_x = -math.sin(math.radians(rotation[1])) * math.cos(math.radians(rotation[0]))
                    direction_y = math.sin(math.radians(rotation[0]))
                    direction_z = -math.cos(math.radians(rotation[1])) * math.cos(math.radians(rotation[0]))
                    direction = (direction_x, direction_y, direction_z)
                
                shader.set_uniform(f"lights[{i}].direction", direction)
                shader.set_uniform(f"lights[{i}].angle", light_component.spot_angle)
    
    def _apply_post_processing(self):
        """应用后处理"""
        # 如果没有后处理器，返回
        if not self.post_processors:
            return
        
        # 创建后处理渲染目标
        if "post_process" not in self.render_targets:
            self.create_render_target("post_process", self.width, self.height)
        
        # 获取渲染目标
        render_target = self.render_targets["post_process"]
        
        # 绑定帧缓冲
        glBindFramebuffer(GL_FRAMEBUFFER, render_target["fbo"])
        
        # 清除屏幕
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 应用后处理
        for post_processor in self.post_processors:
            post_processor.apply(render_target["color_texture"])
        
        # 重置绑定
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        # 渲染后处理结果到屏幕
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 1, 0, 1, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        
        # 使用后处理着色器
        shader = self.shader_cache.get("post_process")
        
        if shader:
            shader.use()
            shader.set_uniform("screen_texture", 0)
        
        # 绑定纹理
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, render_target["color_texture"])
        
        # 渲染全屏四边形
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(1, 0)
        glTexCoord2f(1, 1); glVertex2f(1, 1)
        glTexCoord2f(0, 1); glVertex2f(0, 1)
        glEnd()
        
        # 恢复状态
        glEnable(GL_DEPTH_TEST)
    
    def resize(self, width, height):
        """
        调整渲染系统大小
        
        Args:
            width (int): 新宽度
            height (int): 新高度
        """
        self.width = width
        self.height = height
        self.aspect_ratio = width / height
        
        # 调整视口
        glViewport(0, 0, width, height)
        
        # 重新创建渲染目标
        for name in list(self.render_targets.keys()):
            self.delete_render_target(name)
            self.create_render_target(name, width, height)
    
    def shutdown(self):
        """关闭渲染系统"""
        # 删除渲染目标
        for name in list(self.render_targets.keys()):
            self.delete_render_target(name)
        
        # 删除着色器
        for shader in self.shader_cache.values():
            shader.delete()
        
        # 删除纹理
        for texture in self.texture_cache.values():
            glDeleteTextures(1, [texture])
        
        # 删除网格
        for mesh in self.mesh_cache.values():
            mesh.delete()
        
        # 清空缓存
        self.shader_cache.clear()
        self.texture_cache.clear()
        self.mesh_cache.clear()
        self.material_cache.clear()
        self.render_targets.clear()
        
        # 重置状态
        self.camera = None
        self.lights.clear()
        self.skybox = None
        self.post_processors.clear()
        
        self.initialized = False 