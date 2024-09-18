# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: test_script
# Time    : 2024-09-10
# Contact : 906629272@qq.com

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
import sys

class Window(QWidget):
    move_Flag = False
    Window_Width = 1000
    Window_Length = 1000
    Window_Title = "Hello"
    def __init__(self):
        # 窗体
        super().__init__()
        self.setup_ui()
        self.show()

    def setup_ui(self):
        self.setWindowTitle(self.Window_Title)
        self.Title_Button()
        self.resize(self.Window_Width, self.Window_Length)
        self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setWindowIcon(QIcon("43.png"))
        self.setWindowOpacity(0.9)


    # 标题按钮
    def Title_Button(self):
        # 关闭按钮
        self.close_button = MyPushButton(self)
        self.close_button.setText("关闭")
        self.close_button.clicked.connect(self.close)

        # 最大化按钮

        self.maximize_button = MyPushButton(self)
        self.maximize_button.setText("最大化")

        # 最大化按钮方法
        def maximize_method():
            if window.isMaximized():
                self.showNormal()
                self.maximize_button.setText("最大化")
            else:
                self.showMaximized()
                self.maximize_button.setText("恢复")

        self.maximize_button.clicked.connect(maximize_method)

        # 最小化按钮

        self.minimize_button = MyPushButton(self)
        self.minimize_button.setText("最小化")
        self.minimize_button.clicked.connect(self.showMinimized)

    def resizeEvent(self,evt):

        self.close_button_x = self.width() - MyPushButton.btn_width - MyPushButton.side_margin
        self.close_button.move(self.close_button_x, MyPushButton.top_margin)

        self.maximize_button_x = self.close_button_x - MyPushButton.btn_width - MyPushButton.side_margin
        self.maximize_button.move(self.maximize_button_x, MyPushButton.top_margin)

        self.minimize_button_x = self.maximize_button_x - MyPushButton.btn_width - MyPushButton.side_margin
        self.minimize_button.move(self.minimize_button_x, MyPushButton.top_margin)

# 窗口移动
    def mousePressEvent(self,evt):
        # if evt.x() <= self.minimize_button_x and evt.y() <= (MyPushButton.bottom_margin + MyPushButton.btn_height):
        if evt.x() <= self.minimize_button_x and evt.y() <= 60:

            if evt.button() == Qt.LeftButton:
                self.move_Flag = True
                self.window_origin_x = self.x()
                self.window_origin_y = self.y()
                self.mouse_origin_x = evt.globalX()
                self.mouse_origin_y = evt.globalY()
    def mouseMoveEvent(self, evt):
        if self.move_Flag:
            self.mouse_des_x = evt.globalX()
            self.mouse_des_y = evt.globalY()
            self.window_des_x = self.window_origin_x + self.mouse_des_x - self.mouse_origin_x
            self.window_des_y = self.window_origin_y + self.mouse_des_y - self.mouse_origin_y

            # 按照向量移动窗口
            self.move(self.window_des_x,self.window_des_y)

    def mouseReleaseEvent(self,evt):
        self.move_Flag = False


class MyPushButton(QPushButton):
    btn_width = 160
    btn_height = 50
    top_margin = 20
    side_margin = 10
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.resize(self.btn_width,self.btn_height)
        self.show()


class CollapsibleBox(QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)

        self.toggle_button = QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QParallelAnimationGroup(self)

        self.content_area = QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.content_area.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.content_area.setFrameShape(QFrame.NoFrame)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @Slot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            Qt.DownArrow if not checked else Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QAbstractAnimation.Forward
            if not checked
            else QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
            self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(500)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(500)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


if __name__ == "__main__":
    import sys
    import random

    app = QApplication(sys.argv)

    w = QMainWindow()
    w.setCentralWidget(QWidget())
    dock = QDockWidget("Dock Widget")
    dock.setFeatures(QDockWidget.DockWidgetVerticalTitleBar)  # 禁止拖动
    dock.setTitleBarWidget(QWidget())  # 隐藏标题栏
    w.addDockWidget(Qt.LeftDockWidgetArea, dock)
    scroll = QScrollArea()
    dock.setWidget(scroll)
    content = QWidget()
    scroll.setWidget(content)
    scroll.setWidgetResizable(True)
    vlay = QVBoxLayout(content)
    for i in range(10):
        box = CollapsibleBox("Collapsible Box Header-{}".format(i))
        vlay.addWidget(box)
        lay = QVBoxLayout()
        for j in range(8):
            label = QLabel("{}".format(j))
            color = QColor(*[random.randint(0, 255) for _ in range(3)])
            label.setStyleSheet(
                "background-color: {}; color : white;".format(color.name())
            )
            label.setAlignment(Qt.AlignCenter)
            lay.addWidget(label)

        box.setContentLayout(lay)
    vlay.addStretch()
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())