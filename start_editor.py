#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PyCraft 编辑器快速启动脚本
"""

import sys
import os
import subprocess
import platform
import time
import traceback
from PyQt5.QtWidgets import QApplication, QSplashScreen, QProgressBar, QLabel
from PyQt5.QtGui import QPixmap, QImage, QPainter, QLinearGradient, QColor, QFont, QPen, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve, QPoint

def create_splash_image(width=650, height=420):
    """创建高级深色系启动画面图像"""
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
    
    # 在底部留出空间给进度条
    
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

class EnhancedSplashScreen(QSplashScreen):
    """增强型启动画面，带有进度条和更好的消息显示"""
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, pixmap.height() - 50, pixmap.width() - 100, 10)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid rgba(100, 100, 150, 100);
                border-radius: 5px;
                background-color: rgba(30, 30, 45, 100);
                padding: 1px;
            }
            
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                              stop:0 rgba(120, 120, 200, 180), 
                                              stop:1 rgba(160, 140, 220, 180));
                border-radius: 4px;
            }
        """)
        
        # 创建状态标签
        self.status_label = QLabel(self)
        self.status_label.setGeometry(50, pixmap.height() - 80, pixmap.width() - 100, 30)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: rgba(200, 200, 230, 200);
            background-color: transparent;
            font-size: 12px;
            font-family: Arial;
        """)
        
        self.progress_value = 0
        self.fade_opacity = 1.0

    def progress(self, value, message=""):
        """设置进度和消息"""
        self.progress_value = value
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
        
        QApplication.processEvents()

def check_dependencies():
    """检查依赖项是否已安装"""
    required_packages = ["PyQt5", "OpenGL", "numpy", "pybullet", "pygame"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(splash=None):
    """安装依赖项"""
    try:
        if splash:
            splash.progress(20, "正在安装必要的Python包...")
        
        result = subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        if splash:
            splash.progress(90, "依赖项安装成功！")
        
        time.sleep(1)
        return True
    except subprocess.CalledProcessError as e:
        if splash:
            splash.progress(100, f"依赖项安装失败: {str(e)}")
        
        print("=" * 50)
        print(f"依赖项安装失败: {str(e)}")
        print("请尝试手动运行: pip install -r requirements.txt")
        print("=" * 50)
        time.sleep(2)
        return False

def check_editor_file():
    """检查编辑器主文件是否存在"""
    return os.path.exists("editor_main.py")

def main():
    """主函数"""
    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)
        
        # 创建并显示深色系启动画面
        splash_pixmap = create_splash_image()
        splash = EnhancedSplashScreen(splash_pixmap)
        splash.show()
        splash.progress(0, "正在启动 PyCraft 编辑器...")
        app.processEvents()
        
        # 检查Python版本
        splash.progress(5, "检查Python环境...")
        if sys.version_info < (3, 6):
            splash.progress(100, "错误: PyCraft 需要 Python 3.6 或更高版本")
            app.processEvents()
            time.sleep(3)
            return 1
        
        # 检查编辑器主文件
        splash.progress(10, "检查编辑器文件...")
        if not check_editor_file():
            splash.progress(100, "错误: 找不到编辑器主文件 (editor_main.py)")
            app.processEvents()
            time.sleep(3)
            return 1
        
        # 检查依赖项
        splash.progress(15, "检查依赖项...")
        missing_packages = check_dependencies()
        if missing_packages:
            splash.progress(18, f"缺少依赖项: {', '.join(missing_packages)}，正在安装...")
            app.processEvents()
            
            # 使用QTimer来允许Qt事件循环处理一段时间
            timer = QTimer()
            timer.singleShot(1000, lambda: None)
            app.processEvents()
            
            # 安装依赖项
            if not install_dependencies(splash):
                return 1
            
            # 重新检查，确保依赖项已正确安装
            missing_packages = check_dependencies()
            if missing_packages:
                splash.progress(100, "依赖项安装后仍有问题，请检查Python环境。")
                app.processEvents()
                time.sleep(3)
                return 1
        
        # 更新进度
        for i in range(30, 100, 5):
            splash.progress(i, "正在加载编辑器组件...")
            time.sleep(0.05)  # 稍微延迟，让动画更流畅
        
        # 构建命令行参数
        args = [sys.executable, "editor_main.py"]
        
        # 传递所有额外的命令行参数
        if len(sys.argv) > 1:
            args.extend(sys.argv[1:])
        
        splash.progress(100, "准备完成，正在启动编辑器...")
        
        # 给启动画面一点额外的显示时间，以便用户可以欣赏它
        QTimer.singleShot(800, lambda: None)
        app.processEvents()
        
        # 启动编辑器
        try:
            # 关闭启动画面
            splash.close()
            
            # 启动编辑器进程
            if platform.system() == "Windows":
                # 在Windows上使用subprocess.CREATE_NO_WINDOW标志隐藏控制台窗口
                try:
                    return subprocess.call(args, creationflags=subprocess.CREATE_NO_WINDOW)
                except AttributeError:
                    # 如果CREATE_NO_WINDOW不可用，尝试使用STARTUPINFO
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    return subprocess.call(args, startupinfo=startupinfo)
            else:
                return subprocess.call(args)
        except Exception as e:
            error_msg = f"启动编辑器时出错: {e}\n{traceback.format_exc()}"
            print("=" * 50)
            print(error_msg)
            print("请确保文件 editor_main.py 存在并且可执行。")
            print("=" * 50)
            
            # 如果用户在Windows上，可以显示一个错误窗口
            if platform.system() == "Windows":
                from PyQt5.QtWidgets import QMessageBox
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("PyCraft 启动错误")
                error_dialog.setText("启动编辑器时发生错误")
                error_dialog.setDetailedText(error_msg)
                error_dialog.setStandardButtons(QMessageBox.Ok)
                error_dialog.exec_()
            else:
                input("按Enter键退出...")
            
            return 1
    except Exception as e:
        error_msg = f"未处理的异常: {e}\n{traceback.format_exc()}"
        print("=" * 50)
        print(error_msg)
        print("=" * 50)
        
        try:
            # 如果用户在Windows上，并且PyQt5可用，显示一个错误窗口
            if platform.system() == "Windows":
                from PyQt5.QtWidgets import QMessageBox
                error_dialog = QMessageBox()
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("PyCraft 启动错误")
                error_dialog.setText("启动过程中发生异常")
                error_dialog.setDetailedText(error_msg)
                error_dialog.setStandardButtons(QMessageBox.Ok)
                error_dialog.exec_()
        except:
            input("按Enter键退出...")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())