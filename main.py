#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 游戏引擎主入口
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.core.application import Application
from editor.editor_app import EditorApp


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PyCraft 游戏引擎')
    parser.add_argument('--editor', action='store_true', help='启动编辑器模式')
    parser.add_argument('--project', type=str, help='要打开的项目路径')
    parser.add_argument('--scene', type=str, help='要加载的场景文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--fullscreen', action='store_true', help='全屏模式')
    parser.add_argument('--resolution', type=str, default='1280x720', help='分辨率，格式为 宽x高')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 解析分辨率
    width, height = map(int, args.resolution.split('x'))
    
    if args.editor:
        # 创建编辑器应用程序实例
        app = EditorApp(
            width=width,
            height=height,
            debug=args.debug
        )
        
        # 如果指定了项目，打开项目
        if args.project:
            app.open_project(args.project)
        
        # 如果指定了场景，加载场景
        if args.scene:
            app.load_scene(args.scene)
        
        # 运行编辑器
        return app.run()
    else:
        # 创建游戏应用程序实例
        app = Application(
            width=width,
            height=height,
            fullscreen=args.fullscreen,
            debug=args.debug
        )
        
        # 如果指定了场景，加载场景
        if args.scene:
            app.load_scene(args.scene)
        
        # 运行游戏
        return app.run()


if __name__ == "__main__":
    # 如果没有参数，默认启动编辑器
    if len(sys.argv) == 1:
        sys.argv.append('--editor')
    
    sys.exit(main())
