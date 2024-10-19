# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: ui
# Time    : 2024-09-09
# Contact : 906629272@qq.com
# Description : 主窗口

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from .icons import IconPath
from .widget.widgetT import FramelessWindow, IconButton, SearchLine, JPlistWidget


class LeftWidget(QWidget):
    """
    左侧窗口
    """

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.setFixedWidth(250)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        # 读取窗口样式(子类化QWidget后使用QSS不能生效, 需在自定义Widget中重写paintEvent函数以确保QSS的正确应用)
        # with open(__file__ + "/../qss/leftWidget.qss", "rb") as f:
        #     self.setStyleSheet(f.read().decode("utf-8"))
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setAlignment(Qt.AlignCenter)

        h_layout = QHBoxLayout(self)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(QLabel("JointsPose"))
        h_layout.addStretch(0)
        h_layout.addWidget(IconButton(IconPath.PLUS_PATH.value, 20))
        h_layout.addWidget(IconButton(IconPath.DELETE_PATH.value, 20))
        self.main_layout.addLayout(h_layout)
        self.main_layout.setSpacing(2)

        self.search_line = SearchLine(parent = self)
        self.joint_pose_list = JPlistWidget(self)
        self.main_layout.addWidget(self.search_line)
        self.main_layout.addWidget(self.joint_pose_list)

    def paintEvent(self, event):
        """
        绘制背景
        :param event:
        :return:
        """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(69, 76, 73))
        painter.drawRect(self.rect())
        painter.end()


class RightWidget(QWidget):
    """
    右侧窗口
    """

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        button = QLabel("右侧窗口")
        button.setMouseTracking(True)
        self.main_layout.addWidget(button)


class BodyWidget(QWidget):
    """
    测试窗口
    """

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        # self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.left_widget = LeftWidget(self)
        self.right_widget = RightWidget(self)
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)


class MainWindow(FramelessWindow):
    """
    主窗口
    """

    def __init__(self, parent = None):
        body_widget = BodyWidget()
        FramelessWindow.__init__(self, content_widget = body_widget, parent = parent)
        self.min_size = QSize(1080, 720)
        self.setObjectName("PoseDriveUI")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Window)
        self.resize(1080, 720)
        self.setMinimumSize(self.min_size)


def showUI():
    """
    窗口显示
    :return:
    """
    pass
