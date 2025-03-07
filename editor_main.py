#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器入口文件
"""

import sys
import os
import argparse
import logging
import traceback
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QImage, QPainter, QLinearGradient, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QTimer

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('editor.log', 'w', 'utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('PyCraft')

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from editor.editor_app import EditorApp
except Exception as e:
    logger.error(f"导入编辑器应用程序时出错: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)


def create_splash_image():
    """创建深色系启动画面图像"""
    # 创建一个渐变背景的图像
    width, height = 650, 420
    image = QImage(width, height, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 创建深色梯度背景
    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0, QColor(20, 20, 30))      # 深蓝黑色
    gradient.setColorAt(0.4, QColor(30, 30, 45))    # 深蓝紫色
    gradient.setColorAt(0.8, QColor(25, 25, 40))    # 中间色调
    gradient.setColorAt(1, QColor(15, 15, 25))      # 暗黑色
    
    # 绘制圆角矩形背景
    painter.setBrush(gradient)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, width, height, 20, 20)
    
    # 添加微妙的网格图案
    pen = QPen(QColor(60, 60, 90, 15))
    pen.setWidth(1)
    painter.setPen(pen)
    
    # 绘制水平线
    for y in range(0, height, 20):
        painter.drawLine(0, y, width, y)
    
    # 绘制垂直线
    for x in range(0, width, 20):
        painter.drawLine(x, 0, x, height)
    
    # 添加装饰性几何图形 - 左上角光效
    radial_gradient = QLinearGradient(0, 0, 150, 150)
    radial_gradient.setColorAt(0, QColor(80, 80, 150, 30))
    radial_gradient.setColorAt(1, QColor(40, 40, 100, 0))
    painter.setBrush(radial_gradient)
    painter.drawEllipse(0, 0, 150, 150)
    
    # 添加右下角装饰
    radial_gradient2 = QLinearGradient(width, height, width-100, height-100)
    radial_gradient2.setColorAt(0, QColor(100, 60, 150, 20))
    radial_gradient2.setColorAt(1, QColor(60, 40, 100, 0))
    painter.setBrush(radial_gradient2)
    painter.drawEllipse(width-150, height-150, 150, 150)
    
    # 绘制标题
    title_font = QFont("Arial", 38, QFont.Bold)
    title_font.setLetterSpacing(QFont.AbsoluteSpacing, 2)
    painter.setFont(title_font)
    
    # 绘制标题阴影
    painter.setPen(QColor(0, 0, 30, 100))
    painter.drawText(int(width/2 - 105 + 2), int(height/2 - 70 + 2), "PyCraft")
    
    # 绘制标题
    painter.setPen(QColor(210, 210, 255))  # 亮淡蓝色
    painter.drawText(int(width/2 - 105), int(height/2 - 70), "PyCraft")
    
    # 绘制副标题
    subtitle_font = QFont("Arial", 16)
    subtitle_font.setLetterSpacing(QFont.AbsoluteSpacing, 1)
    painter.setFont(subtitle_font)
    
    # 绘制副标题阴影
    painter.setPen(QColor(0, 0, 30, 100))
    painter.drawText(int(width/2 - 155 + 1), int(height/2 - 10 + 1), "创新的3D游戏开发平台")
    
    # 绘制副标题
    painter.setPen(QColor(170, 170, 220))  # 淡紫色
    painter.drawText(int(width/2 - 155), int(height/2 - 10), "创新的3D游戏开发平台")
    
    # 绘制分隔线
    pen = QPen(QColor(100, 100, 180, 60))
    pen.setWidth(1)
    painter.setPen(pen)
    painter.drawLine(int(width/2 - 150), int(height/2 + 20), int(width/2 + 150), int(height/2 + 20))
    
    # 绘制版本号
    painter.setFont(QFont("Arial", 10))
    painter.setPen(QColor(140, 140, 190))  # 浅灰紫色
    painter.drawText(int(width - 70), int(height - 25), "v0.1.0")
    
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
    try:
        logger.info("正在启动编辑器...")
        
        # 创建QApplication实例
        app = QApplication(sys.argv)
        logger.info("QApplication 已创建")
        
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
        logger.info("启动画面已显示")
        
        # 解析命令行参数
        args = parse_arguments()
        logger.info(f"命令行参数: {args}")
        
        # 解析分辨率
        try:
            width, height = map(int, args.resolution.split('x'))
        except:
            width, height = 1280, 720
            logger.warning(f"无效的分辨率格式 '{args.resolution}'，使用默认值 1280x720")
        
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
        
        try:
            # 创建编辑器应用程序实例
            logger.info("正在创建编辑器应用程序实例...")
            editor_app = EditorApp(
                width=width,
                height=height,
                debug=args.debug
            )
            logger.info("编辑器应用程序实例已创建")
            
            # 如果指定了项目，打开项目
            if args.project:
                splash.showMessage(
                    f"正在打开项目: {os.path.basename(args.project)}...", 
                    Qt.AlignBottom | Qt.AlignHCenter, 
                    Qt.white
                )
                app.processEvents()
                editor_app.open_project(args.project)
                logger.info(f"已打开项目: {args.project}")
            
            # 如果指定了场景，加载场景
            if args.scene:
                splash.showMessage(
                    f"正在加载场景: {os.path.basename(args.scene)}...", 
                    Qt.AlignBottom | Qt.AlignHCenter, 
                    Qt.white
                )
                app.processEvents()
                editor_app.load_scene(args.scene)
                logger.info(f"已加载场景: {args.scene}")
            
            # 关闭启动画面，显示主窗口
            splash.finish(editor_app.main_window)
            logger.info("编辑器启动完成，显示主窗口")
            
            # 运行编辑器
            return editor_app.run()
            
        except Exception as e:
            logger.error(f"创建或运行编辑器应用程序时出错: {e}")
            logger.error(traceback.format_exc())
            raise
            
    except Exception as e:
        logger.error(f"编辑器启动失败: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.error(f"未处理的异常: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)