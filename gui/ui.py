# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: ui
# Time    : 2024-09-09
# Contact : 906629272@qq.com
# Description : 主窗口

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from .widget.titleBar import TitleBar
from .widget.widgetT import RoundButton


class FramelessWindow(QWidget):
    """
    主窗口
    """
    Margins = 5

    def __init__(self, content_widget = None, parent = None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)

        self._pressed = False
        self.direction = set()
        self.gpos = None

        # 窗口布局
        title_bar = TitleBar(self)
        title_bar.windowMoved.connect(self.move)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(title_bar)
        self.main_layout.addWidget(content_widget)
        # 事件过滤器
        self.installEventFilter(self)

    def paintEvent(self, event):
        """
        绘制背景
        :param event:
        :return:
        """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(31, 38, 35))
        painter.drawRect(self.rect())
        painter.end()

    def mousePressEvent(self, event):
        """
        鼠标按下事件(拖动窗口, 缩放窗口)
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self.gpos = event.pos()
            self._pressed = True
            rect = self.geometry()
            side_check = {
                "left": QRect(rect.x(), rect.y(), self.Margins, rect.height()),
                "right": QRect(rect.x() + rect.width() - self.Margins, rect.y(), self.Margins, rect.height()),
                "top": QRect(rect.x(), rect.y(), rect.width(), self.Margins),
                "bottom": QRect(rect.x(), rect.y() + rect.height() - self.Margins, rect.width(), self.Margins)
            }
            self.direction.clear()
            for side, rect in side_check.items():
                if rect.contains(event.globalPos()):
                    self.direction.add(side)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件(结束拖动窗口)
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self._pressed = False
            self.direction.clear()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件(拖动窗口)
        :param event:
        :return:
        """
        if self.isMaximized() or self.isFullScreen():
            self.direction.clear()
            self.setCursor(Qt.ArrowCursor)
            return
        if self._pressed:
            self._resizeWidget(event)
        # 鼠标移动时, 窗口边缘出现缩放手势
        # 左上角
        if event.pos().x() <= self.Margins and event.pos().y() <= self.Margins:
            self.setCursor(Qt.SizeFDiagCursor)
        # 右上角
        elif event.pos().x() >= self.width() - self.Margins and event.pos().y() <= self.Margins:
            self.setCursor(Qt.SizeBDiagCursor)
        # 左下角
        elif event.pos().x() <= self.Margins and event.pos().y() >= self.height() - self.Margins:
            self.setCursor(Qt.SizeBDiagCursor)
        # 右下角
        elif event.pos().x() >= self.width() - self.Margins and event.pos().y() >= self.height() - self.Margins:
            self.setCursor(Qt.SizeFDiagCursor)
        # 左侧
        elif event.pos().x() <= self.Margins:
            self.setCursor(Qt.SizeHorCursor)
        # 右侧
        elif event.pos().x() >= self.width() - self.Margins:
            self.setCursor(Qt.SizeHorCursor)
        # 上部
        elif event.pos().y() <= self.Margins:
            self.setCursor(Qt.SizeVerCursor)
        # 下部
        elif event.pos().y() >= self.height() - self.Margins:
            self.setCursor(Qt.SizeVerCursor)
        # 其他位置
        else:
            self.setCursor(Qt.ArrowCursor)

    def _resizeWidget(self, event):
        """
        窗口缩放事件
        :param event: 鼠标事件
        :return:
        """
        rect = self.geometry()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        # 点击时的坐标与移动时的坐标差值
        mpos = event.pos() - self.gpos
        if "left" in self.direction:
            if rect.width() - mpos.x() > self.minimumWidth():
                x += mpos.x()
                w -= mpos.x()
        if "right" in self.direction:
            w = event.globalX() - rect.x()
        if "top" in self.direction:
            # print(rect.height(), mpos.y(), rect.height() - mpos.y(), self.minimumHeight())
            if rect.height() - mpos.y() > self.minimumHeight():
                y += mpos.y()
                h -= mpos.y()
        if "bottom" in self.direction:
            h = event.globalY() - rect.y()
        self.setGeometry(x, y, w, h)

class LeftWidget(QWidget):
    """
    左侧窗口
    """

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.setFixedWidth(250)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        button = RoundButton(radius = 50, grcolor = (34, 148, 83))
        self.main_layout.addWidget(button)

    def paintEvent(self, event):
        """
        绘制背景
        :param event:
        :return:
        """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(48, 55, 52))
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
        button = RoundButton(radius = 50, grcolor = (17, 101, 154))
        self.main_layout.addWidget(button)

class TestWidget(QWidget):
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
        self.left_widget = LeftWidget()
        self.right_widget = RightWidget()
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)


class MainWindow(FramelessWindow):
    """
    主窗口
    """

    def __init__(self, parent = None):
        test_widget = TestWidget()
        FramelessWindow.__init__(self, content_widget = test_widget, parent = parent)
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
