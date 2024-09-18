# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: titleBar
# Time    : 2024-09-12
# Contact : 906629272@qq.com
# Description : 标题栏控件

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from ..Icon import *
from .widgetT import RoundButton


class TitleBar(QWidget):
    """
    标题栏控件
    """
    Margins = 5
    # 移动窗口信号
    windowMoved = Signal(QPoint)

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(30)
        self.setMouseTracking(True)
        self.get_parent = parent
        self.Pos_offset = None
        self.is_drag = False
        # 左侧图标
        self.icon_label = QLabel()
        self.icon_label.setPixmap(QIcon(IconPath.TITLEBAR_PATH.value).pixmap(20, 20))
        self.icon_label.setMouseTracking(True)
        # 最大化按钮
        self.max_button = RoundButton(radius = 20, grcolor = (17, 101, 154))
        self.max_button.clicked.connect(self.__toggleMaxState)
        # 最小化按钮
        self.min_button = RoundButton(radius = 20, grcolor = (34, 148, 83))
        self.min_button.clicked.connect(self.get_parent.showMinimized)
        # 关闭按钮
        self.close_button = RoundButton(radius = 20, grcolor = (165, 45, 45))
        self.close_button.clicked.connect(self.get_parent.close)
        # 布局
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 0, 5, 0)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addStretch(0)
        self.main_layout.addWidget(self.min_button)
        self.main_layout.addWidget(self.max_button)
        self.main_layout.addWidget(self.close_button)

    def __toggleMaxState(self):
        """
        切换最大化状态
        :return:
        """
        if self.get_parent.isMaximized():
            self.get_parent.showNormal()
        else:
            self.get_parent.showMaximized()

    def mouseDoubleClickEvent(self, event):
        """
        双击标题栏最大化窗口
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self.__toggleMaxState()

    def mousePressEvent(self, event):
        """
        鼠标按下事件,拖拽窗口
        :param event:
        :return:
        """
        # 当鼠标处于标题栏区域时，开始拖拽窗口
        if event.button() == Qt.LeftButton and self._isDragRegion(event.pos()):
            self.is_drag = True
            self.Pos_offset = event.pos()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件,拖拽窗口
        :param event:
        :return:
        """
        if event.buttons() == Qt.LeftButton and self.is_drag and self.Pos_offset:
            # 计算窗口移动距离
            self.windowMoved.emit(self.mapToGlobal(event.pos() - self.Pos_offset))
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件,结束拖拽窗口
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton and self._isDragRegion(event.pos()):
            self.is_drag = False
            self.Pos_offset = None
            event.accept()
        else:
            event.ignore()

    def _isDragRegion(self, pos):
        """
        判断鼠标是否在可拖拽区域
        :param pos:
        :return:
        """
        # 当鼠标处于左侧边缘时，不可拖拽
        if pos.x() <= self.Margins:
            return False
        # 当鼠标处于右侧边缘时，不可拖拽
        if pos.x() >= self.width() - self.Margins:
            return False
        # 当鼠标处于左上角时，不可拖拽
        if pos.x() <= self.Margins and pos.y() <= self.Margins:
            return False
        # 当鼠标处于右上角时，不可拖拽
        if pos.x() >= self.width() - self.Margins and pos.y() <= self.Margins:
            return False
        # 当鼠标处于上方时，不可拖拽
        if pos.y() <= self.Margins:
            return False
        # 当鼠标超过下方时，不可拖拽
        if pos.y() > self.height():
            return False
        # 当鼠标处于标题栏区域时，可拖拽
        return True

