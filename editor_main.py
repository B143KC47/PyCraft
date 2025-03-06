#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器入口文件
"""

import sys
import os
import argparse
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QImage, QPainter, QLinearGradient, QColor, QFont
from PyQt5.QtCore import Qt, QTimer

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from editor.editor_app import EditorApp


def create_splash_image():
    """创建启动画面图像"""
    # 创建一个渐变背景的图像
    width, height = 600, 400
    image = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 创建渐变背景
    gradient = QLinearGradient(0, 0, 0, height)
    gradient.setColorAt(0, QColor(40, 40, 60))
    gradient.setColorAt(1, QColor(20, 20, 30))
    
    # 绘制圆角矩形背景
    painter.setBrush(gradient)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, width, height, 15, 15)
    
    # 绘制标题
    painter.setFont(QFont("Arial", 28, QFont.Bold))
    painter.setPen(QColor(230, 230, 250))
    painter.drawText(width/2 - 100, height/2 - 40, "PyCraft")
    
    # 绘制副标题
    painter.setFont(QFont("Arial", 16))
    painter.setPen(QColor(180, 180, 200))
    painter.drawText(width/2 - 150, height/2 + 10, "创新的3D游戏开发平台")
    
    # 绘制版本号
    painter.setFont(QFont("Arial", 10))
    painter.setPen(QColor(150, 150, 170))
    painter.drawText(width/2 - 30, height - 20, "v0.1.0")
    
    painter.end()
    return QPixmap.fromImage(image)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='PyCraft 编辑器')
    parser.add_argument('--project', type=str, help='要打开的项目路径')
    parser.add_argument('--scene', type=str, help='要加载的场景文件路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--fullscreen', action='store_true', help='全屏模式')
    parser.add_argument('--resolution', type=str, default='1280x720', help='分辨率，格式为 宽x高')
    return parser.parse_args()


def main():
    """主函数"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 显示启动画面
    splash_pixmap = create_splash_image()
    splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
    splash.setFont(QFont("Arial", 10))
    splash.show()
    splash.showMessage(
        "初始化编辑器环境...", 
        Qt.AlignBottom | Qt.AlignHCenter, 
        Qt.white
    )
    app.processEvents()
    
    # 解析命令行参数
    args = parse_arguments()
    
    # 解析分辨率
    try:
        width, height = map(int, args.resolution.split('x'))
    except:
        width, height = 1280, 720
        print(f"警告: 无效的分辨率格式 '{args.resolution}'，使用默认值 1280x720")
    
    # 显示加载消息
    splash.showMessage(
        "加载编辑器组件...", 
        Qt.AlignBottom | Qt.AlignHCenter, 
        Qt.white
    )
    app.processEvents()
    
    # 延迟一段时间以显示启动画面
    timer = QTimer()
    timer.singleShot(1500, lambda: None)
    app.processEvents()
    
    # 创建编辑器应用程序实例
    editor_app = EditorApp(
        width=width,
        height=height,
        debug=args.debug
    )
    
    # 如果指定了项目，打开项目
    if args.project:
        splash.showMessage(
            f"正在打开项目: {os.path.basename(args.project)}...", 
            Qt.AlignBottom | Qt.AlignHCenter, 
            Qt.white
        )
        app.processEvents()
        editor_app.open_project(args.project)
    
    # 如果指定了场景，加载场景
    if args.scene:
        splash.showMessage(
            f"正在加载场景: {os.path.basename(args.scene)}...", 
            Qt.AlignBottom | Qt.AlignHCenter, 
            Qt.white
        )
        app.processEvents()
        editor_app.load_scene(args.scene)
    
    # 关闭启动画面，显示主窗口
    splash.finish(editor_app.main_window)
    
    # 运行编辑器
    return editor_app.run()


if __name__ == "__main__":
    sys.exit(main())