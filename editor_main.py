#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器主入口
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from editor.editor_app import EditorApp


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PyCraft 游戏引擎编辑器')
    parser.add_argument('--project', type=str, help='要打开的项目路径')
    parser.add_argument('--scene', type=str, help='要加载的场景文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--resolution', type=str, default='1920x1080', help='分辨率，格式为 宽x高')
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 解析分辨率
    width, height = map(int, args.resolution.split('x'))
    
    # 创建编辑器应用程序实例
    editor = EditorApp(
        width=width,
        height=height,
        debug=args.debug
    )
    
    # 如果指定了项目，打开项目
    if args.project:
        editor.open_project(args.project)
    
    # 如果指定了场景，加载场景
    if args.scene:
        editor.load_scene(args.scene)
    
    # 运行编辑器
    editor.run()


if __name__ == "__main__":
    main() 