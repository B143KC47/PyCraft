"""
输入系统，负责处理用户输入
"""

import pygame
import numpy as np

from engine.core.ecs.system import System


class InputSystem(System):
    """输入系统，负责处理用户输入"""
    
    # 键盘按键常量
    KEY_UNKNOWN = -1
    KEY_SPACE = pygame.K_SPACE
    KEY_ESCAPE = pygame.K_ESCAPE
    KEY_ENTER = pygame.K_RETURN
    KEY_TAB = pygame.K_TAB
    KEY_BACKSPACE = pygame.K_BACKSPACE
    KEY_INSERT = pygame.K_INSERT
    KEY_DELETE = pygame.K_DELETE
    KEY_RIGHT = pygame.K_RIGHT
    KEY_LEFT = pygame.K_LEFT
    KEY_DOWN = pygame.K_DOWN
    KEY_UP = pygame.K_UP
    KEY_PAGE_UP = pygame.K_PAGEUP
    KEY_PAGE_DOWN = pygame.K_PAGEDOWN
    KEY_HOME = pygame.K_HOME
    KEY_END = pygame.K_END
    KEY_CAPS_LOCK = pygame.K_CAPSLOCK
    KEY_SCROLL_LOCK = pygame.K_SCROLLLOCK
    KEY_NUM_LOCK = pygame.K_NUMLOCK
    KEY_PRINT_SCREEN = pygame.K_PRINT
    KEY_PAUSE = pygame.K_PAUSE
    KEY_F1 = pygame.K_F1
    KEY_F2 = pygame.K_F2
    KEY_F3 = pygame.K_F3
    KEY_F4 = pygame.K_F4
    KEY_F5 = pygame.K_F5
    KEY_F6 = pygame.K_F6
    KEY_F7 = pygame.K_F7
    KEY_F8 = pygame.K_F8
    KEY_F9 = pygame.K_F9
    KEY_F10 = pygame.K_F10
    KEY_F11 = pygame.K_F11
    KEY_F12 = pygame.K_F12
    KEY_LEFT_SHIFT = pygame.K_LSHIFT
    KEY_LEFT_CONTROL = pygame.K_LCTRL
    KEY_LEFT_ALT = pygame.K_LALT
    KEY_LEFT_SUPER = pygame.K_LSUPER
    KEY_RIGHT_SHIFT = pygame.K_RSHIFT
    KEY_RIGHT_CONTROL = pygame.K_RCTRL
    KEY_RIGHT_ALT = pygame.K_RALT
    KEY_RIGHT_SUPER = pygame.K_RSUPER
    KEY_KB_MENU = pygame.K_MENU
    KEY_LEFT_BRACKET = pygame.K_LEFTBRACKET
    KEY_BACKSLASH = pygame.K_BACKSLASH
    KEY_RIGHT_BRACKET = pygame.K_RIGHTBRACKET
    KEY_GRAVE = pygame.K_BACKQUOTE
    KEY_A = pygame.K_a
    KEY_B = pygame.K_b
    KEY_C = pygame.K_c
    KEY_D = pygame.K_d
    KEY_E = pygame.K_e
    KEY_F = pygame.K_f
    KEY_G = pygame.K_g
    KEY_H = pygame.K_h
    KEY_I = pygame.K_i
    KEY_J = pygame.K_j
    KEY_K = pygame.K_k
    KEY_L = pygame.K_l
    KEY_M = pygame.K_m
    KEY_N = pygame.K_n
    KEY_O = pygame.K_o
    KEY_P = pygame.K_p
    KEY_Q = pygame.K_q
    KEY_R = pygame.K_r
    KEY_S = pygame.K_s
    KEY_T = pygame.K_t
    KEY_U = pygame.K_u
    KEY_V = pygame.K_v
    KEY_W = pygame.K_w
    KEY_X = pygame.K_x
    KEY_Y = pygame.K_y
    KEY_Z = pygame.K_z
    KEY_0 = pygame.K_0
    KEY_1 = pygame.K_1
    KEY_2 = pygame.K_2
    KEY_3 = pygame.K_3
    KEY_4 = pygame.K_4
    KEY_5 = pygame.K_5
    KEY_6 = pygame.K_6
    KEY_7 = pygame.K_7
    KEY_8 = pygame.K_8
    KEY_9 = pygame.K_9
    
    # 鼠标按键常量
    MOUSE_LEFT_BUTTON = 1
    MOUSE_MIDDLE_BUTTON = 2
    MOUSE_RIGHT_BUTTON = 3
    
    def __init__(self):
        """初始化输入系统"""
        super().__init__()
        self.priority = 10  # 输入系统优先级较高，在其他系统之前更新
        
        # 键盘状态
        self.key_pressed = {}  # 当前按下的键
        self.key_down = {}  # 本帧按下的键
        self.key_up = {}  # 本帧释放的键
        
        # 鼠标状态
        self.mouse_position = (0, 0)  # 鼠标位置
        self.mouse_delta = (0, 0)  # 鼠标移动增量
        self.mouse_wheel_move = 0  # 鼠标滚轮移动
        self.mouse_button_pressed = {}  # 当前按下的鼠标按键
        self.mouse_button_down = {}  # 本帧按下的鼠标按键
        self.mouse_button_up = {}  # 本帧释放的鼠标按键
        
        # 游戏手柄状态
        self.gamepads = []  # 游戏手柄列表
        self.gamepad_button_pressed = {}  # 当前按下的游戏手柄按键
        self.gamepad_button_down = {}  # 本帧按下的游戏手柄按键
        self.gamepad_button_up = {}  # 本帧释放的游戏手柄按键
        self.gamepad_axis_values = {}  # 游戏手柄轴的值
        
        # 事件回调
        self.key_callbacks = {}  # 键盘事件回调
        self.mouse_callbacks = {}  # 鼠标事件回调
        self.gamepad_callbacks = {}  # 游戏手柄事件回调
        
        # 初始化标志
        self.initialized = False
    
    def initialize(self):
        """初始化输入系统"""
        # 初始化Pygame
        if not pygame.get_init():
            pygame.init()
        
        # 初始化游戏手柄
        pygame.joystick.init()
        
        # 获取游戏手柄数量
        joystick_count = pygame.joystick.get_count()
        
        # 初始化游戏手柄
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.gamepads.append(joystick)
            
            # 初始化游戏手柄按键状态
            gamepad_id = joystick.get_instance_id()
            self.gamepad_button_pressed[gamepad_id] = {}
            self.gamepad_button_down[gamepad_id] = {}
            self.gamepad_button_up[gamepad_id] = {}
            self.gamepad_axis_values[gamepad_id] = {}
            
            # 初始化游戏手柄轴的值
            for j in range(joystick.get_numaxes()):
                self.gamepad_axis_values[gamepad_id][j] = 0.0
        
        self.initialized = True
    
    def process_event(self, event):
        """
        处理事件
        
        Args:
            event: Pygame事件
            
        Returns:
            bool: 事件是否被处理
        """
        if not self.initialized:
            return False
        
        # 处理键盘事件
        if event.type == pygame.KEYDOWN:
            key = event.key
            self.key_pressed[key] = True
            self.key_down[key] = True
            
            # 调用回调函数
            if key in self.key_callbacks:
                for callback in self.key_callbacks[key]:
                    callback(key, True)
            
            return True
        
        elif event.type == pygame.KEYUP:
            key = event.key
            self.key_pressed[key] = False
            self.key_up[key] = True
            
            # 调用回调函数
            if key in self.key_callbacks:
                for callback in self.key_callbacks[key]:
                    callback(key, False)
            
            return True
        
        # 处理鼠标事件
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_position = event.pos
            self.mouse_delta = event.rel
            
            # 调用回调函数
            if "motion" in self.mouse_callbacks:
                for callback in self.mouse_callbacks["motion"]:
                    callback(self.mouse_position, self.mouse_delta)
            
            return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            button = event.button
            self.mouse_button_pressed[button] = True
            self.mouse_button_down[button] = True
            
            # 调用回调函数
            if button in self.mouse_callbacks:
                for callback in self.mouse_callbacks[button]:
                    callback(button, True, event.pos)
            
            return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            button = event.button
            self.mouse_button_pressed[button] = False
            self.mouse_button_up[button] = True
            
            # 调用回调函数
            if button in self.mouse_callbacks:
                for callback in self.mouse_callbacks[button]:
                    callback(button, False, event.pos)
            
            return True
        
        elif event.type == pygame.MOUSEWHEEL:
            self.mouse_wheel_move = event.y
            
            # 调用回调函数
            if "wheel" in self.mouse_callbacks:
                for callback in self.mouse_callbacks["wheel"]:
                    callback(self.mouse_wheel_move)
            
            return True
        
        # 处理游戏手柄事件
        elif event.type == pygame.JOYBUTTONDOWN:
            gamepad_id = event.instance_id
            button = event.button
            
            if gamepad_id in self.gamepad_button_pressed:
                self.gamepad_button_pressed[gamepad_id][button] = True
                self.gamepad_button_down[gamepad_id][button] = True
                
                # 调用回调函数
                if (gamepad_id, button) in self.gamepad_callbacks:
                    for callback in self.gamepad_callbacks[(gamepad_id, button)]:
                        callback(gamepad_id, button, True)
            
            return True
        
        elif event.type == pygame.JOYBUTTONUP:
            gamepad_id = event.instance_id
            button = event.button
            
            if gamepad_id in self.gamepad_button_pressed:
                self.gamepad_button_pressed[gamepad_id][button] = False
                self.gamepad_button_up[gamepad_id][button] = True
                
                # 调用回调函数
                if (gamepad_id, button) in self.gamepad_callbacks:
                    for callback in self.gamepad_callbacks[(gamepad_id, button)]:
                        callback(gamepad_id, button, False)
            
            return True
        
        elif event.type == pygame.JOYAXISMOTION:
            gamepad_id = event.instance_id
            axis = event.axis
            value = event.value
            
            if gamepad_id in self.gamepad_axis_values:
                self.gamepad_axis_values[gamepad_id][axis] = value
                
                # 调用回调函数
                if (gamepad_id, "axis", axis) in self.gamepad_callbacks:
                    for callback in self.gamepad_callbacks[(gamepad_id, "axis", axis)]:
                        callback(gamepad_id, axis, value)
            
            return True
        
        return False
    
    def update(self):
        """更新输入系统"""
        if not self.initialized:
            return
        
        # 清除本帧按下和释放的键
        self.key_down.clear()
        self.key_up.clear()
        
        # 清除本帧按下和释放的鼠标按键
        self.mouse_button_down.clear()
        self.mouse_button_up.clear()
        
        # 重置鼠标增量和滚轮移动
        self.mouse_delta = (0, 0)
        self.mouse_wheel_move = 0
        
        # 清除本帧按下和释放的游戏手柄按键
        for gamepad_id in self.gamepad_button_down:
            self.gamepad_button_down[gamepad_id].clear()
        
        for gamepad_id in self.gamepad_button_up:
            self.gamepad_button_up[gamepad_id].clear()
    
    def is_key_pressed(self, key):
        """
        检查键是否按下
        
        Args:
            key (int): 键码
            
        Returns:
            bool: 是否按下
        """
        return self.key_pressed.get(key, False)
    
    def is_key_down(self, key):
        """
        检查键是否在本帧按下
        
        Args:
            key (int): 键码
            
        Returns:
            bool: 是否在本帧按下
        """
        return self.key_down.get(key, False)
    
    def is_key_up(self, key):
        """
        检查键是否在本帧释放
        
        Args:
            key (int): 键码
            
        Returns:
            bool: 是否在本帧释放
        """
        return self.key_up.get(key, False)
    
    def is_key_pressed_repeat(self, key, repeat_delay=0.5, repeat_interval=0.05):
        """
        检查键是否按下（支持重复）
        
        Args:
            key (int): 键码
            repeat_delay (float): 重复延迟，单位为秒
            repeat_interval (float): 重复间隔，单位为秒
            
        Returns:
            bool: 是否按下
        """
        if not self.is_key_pressed(key):
            return False
        
        if self.is_key_down(key):
            return True
        
        # TODO: 实现重复逻辑
        
        return False
    
    def get_key_pressed_time(self, key):
        """
        获取键按下的时间
        
        Args:
            key (int): 键码
            
        Returns:
            float: 按下的时间，单位为秒，如果未按下则返回0
        """
        # TODO: 实现按键时间跟踪
        
        return 0.0
    
    def is_mouse_button_pressed(self, button):
        """
        检查鼠标按键是否按下
        
        Args:
            button (int): 鼠标按键
            
        Returns:
            bool: 是否按下
        """
        return self.mouse_button_pressed.get(button, False)
    
    def is_mouse_button_down(self, button):
        """
        检查鼠标按键是否在本帧按下
        
        Args:
            button (int): 鼠标按键
            
        Returns:
            bool: 是否在本帧按下
        """
        return self.mouse_button_down.get(button, False)
    
    def is_mouse_button_up(self, button):
        """
        检查鼠标按键是否在本帧释放
        
        Args:
            button (int): 鼠标按键
            
        Returns:
            bool: 是否在本帧释放
        """
        return self.mouse_button_up.get(button, False)
    
    def get_mouse_position(self):
        """
        获取鼠标位置
        
        Returns:
            tuple: (x, y)
        """
        return self.mouse_position
    
    def get_mouse_delta(self):
        """
        获取鼠标移动增量
        
        Returns:
            tuple: (dx, dy)
        """
        return self.mouse_delta
    
    def get_mouse_wheel_move(self):
        """
        获取鼠标滚轮移动
        
        Returns:
            int: 滚轮移动值
        """
        return self.mouse_wheel_move
    
    def is_gamepad_available(self, gamepad_id):
        """
        检查游戏手柄是否可用
        
        Args:
            gamepad_id (int): 游戏手柄ID
            
        Returns:
            bool: 是否可用
        """
        return gamepad_id in self.gamepad_button_pressed
    
    def is_gamepad_button_pressed(self, gamepad_id, button):
        """
        检查游戏手柄按键是否按下
        
        Args:
            gamepad_id (int): 游戏手柄ID
            button (int): 按键
            
        Returns:
            bool: 是否按下
        """
        if gamepad_id not in self.gamepad_button_pressed:
            return False
        
        return self.gamepad_button_pressed[gamepad_id].get(button, False)
    
    def is_gamepad_button_down(self, gamepad_id, button):
        """
        检查游戏手柄按键是否在本帧按下
        
        Args:
            gamepad_id (int): 游戏手柄ID
            button (int): 按键
            
        Returns:
            bool: 是否在本帧按下
        """
        if gamepad_id not in self.gamepad_button_down:
            return False
        
        return self.gamepad_button_down[gamepad_id].get(button, False)
    
    def is_gamepad_button_up(self, gamepad_id, button):
        """
        检查游戏手柄按键是否在本帧释放
        
        Args:
            gamepad_id (int): 游戏手柄ID
            button (int): 按键
            
        Returns:
            bool: 是否在本帧释放
        """
        if gamepad_id not in self.gamepad_button_up:
            return False
        
        return self.gamepad_button_up[gamepad_id].get(button, False)
    
    def get_gamepad_axis_value(self, gamepad_id, axis):
        """
        获取游戏手柄轴的值
        
        Args:
            gamepad_id (int): 游戏手柄ID
            axis (int): 轴
            
        Returns:
            float: 轴的值，范围为-1.0到1.0
        """
        if gamepad_id not in self.gamepad_axis_values:
            return 0.0
        
        return self.gamepad_axis_values[gamepad_id].get(axis, 0.0)
    
    def register_key_callback(self, key, callback):
        """
        注册键盘事件回调
        
        Args:
            key (int): 键码
            callback (function): 回调函数，接受参数(key, pressed)
        """
        if key not in self.key_callbacks:
            self.key_callbacks[key] = []
        
        self.key_callbacks[key].append(callback)
    
    def unregister_key_callback(self, key, callback):
        """
        注销键盘事件回调
        
        Args:
            key (int): 键码
            callback (function): 回调函数
            
        Returns:
            bool: 是否成功注销
        """
        if key not in self.key_callbacks:
            return False
        
        if callback in self.key_callbacks[key]:
            self.key_callbacks[key].remove(callback)
            return True
        
        return False
    
    def register_mouse_callback(self, button, callback):
        """
        注册鼠标事件回调
        
        Args:
            button (int or str): 鼠标按键或事件类型（"motion", "wheel"）
            callback (function): 回调函数，接受参数(button, pressed, position)或(position, delta)或(wheel_move)
        """
        if button not in self.mouse_callbacks:
            self.mouse_callbacks[button] = []
        
        self.mouse_callbacks[button].append(callback)
    
    def unregister_mouse_callback(self, button, callback):
        """
        注销鼠标事件回调
        
        Args:
            button (int or str): 鼠标按键或事件类型（"motion", "wheel"）
            callback (function): 回调函数
            
        Returns:
            bool: 是否成功注销
        """
        if button not in self.mouse_callbacks:
            return False
        
        if callback in self.mouse_callbacks[button]:
            self.mouse_callbacks[button].remove(callback)
            return True
        
        return False
    
    def register_gamepad_callback(self, gamepad_id, button, callback):
        """
        注册游戏手柄事件回调
        
        Args:
            gamepad_id (int): 游戏手柄ID
            button (int or tuple): 按键或轴（"axis", axis_id）
            callback (function): 回调函数，接受参数(gamepad_id, button, pressed)或(gamepad_id, axis, value)
        """
        key = (gamepad_id, button) if not isinstance(button, tuple) else (gamepad_id, button[0], button[1])
        
        if key not in self.gamepad_callbacks:
            self.gamepad_callbacks[key] = []
        
        self.gamepad_callbacks[key].append(callback)
    
    def unregister_gamepad_callback(self, gamepad_id, button, callback):
        """
        注销游戏手柄事件回调
        
        Args:
            gamepad_id (int): 游戏手柄ID
            button (int or tuple): 按键或轴（"axis", axis_id）
            callback (function): 回调函数
            
        Returns:
            bool: 是否成功注销
        """
        key = (gamepad_id, button) if not isinstance(button, tuple) else (gamepad_id, button[0], button[1])
        
        if key not in self.gamepad_callbacks:
            return False
        
        if callback in self.gamepad_callbacks[key]:
            self.gamepad_callbacks[key].remove(callback)
            return True
        
        return False
    
    def shutdown(self):
        """关闭输入系统"""
        # 清空状态
        self.key_pressed.clear()
        self.key_down.clear()
        self.key_up.clear()
        
        self.mouse_button_pressed.clear()
        self.mouse_button_down.clear()
        self.mouse_button_up.clear()
        
        self.gamepad_button_pressed.clear()
        self.gamepad_button_down.clear()
        self.gamepad_button_up.clear()
        self.gamepad_axis_values.clear()
        
        # 清空回调
        self.key_callbacks.clear()
        self.mouse_callbacks.clear()
        self.gamepad_callbacks.clear()
        
        # 关闭游戏手柄
        for joystick in self.gamepads:
            joystick.quit()
        
        self.gamepads.clear()
        
        # 关闭Pygame
        pygame.joystick.quit()
        
        self.initialized = False 