# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: widgetT
# Time    : 2024-09-18
# Contact : 906629272@qq.com
# Description : 自定义控件模板

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *


def setLuminance(rgb, uord, percent):
    """
    将rgb转为yuv改变y值来提高或降低原rgb的明度
    :param rgb: rgb数值
    :param uord: 提高或降低(T or F)
    :param percent: 提高或降低多少(0~1)
    :return:
    """
    r, g, b = rgb
    y = ((66 * r + 129 * g + 25 * b + 128) >> 8) + 16
    u = ((-38 * r - 74 * g + 112 * b + 128) >> 8) + 128
    v = ((112 * r - 94 * g - 18 * b + 128) >> 8) + 128
    if uord:
        ud_y = round(min(235, y * (1 + percent)))
    else:
        ud_y = round(max(16, y * (1 - percent)))
    c = ud_y - 16
    d = u - 128
    e = v - 128
    ud_r = min(255, max(0, (298 * c + 409 * e + 128) >> 8))
    ud_g = min(255, max(0, (298 * c - 100 * d - 208 * e + 128) >> 8))
    ud_b = min(255, max(0, (298 * c + 516 * d + 128) >> 8))
    outcolor = (ud_r, ud_g, ud_b)
    return outcolor


class RoundButton(QAbstractButton):
    """
    圆形按钮控件
    """
    NORMAL, HOVER, PRESS = range(3)

    def __init__(self, radius=25, grcolor=None):
        """
        初始化圆形按钮控件
        :param parent:
        :param radius: 半径,默认25
        :param grcolor: 颜色(r,g,b)
        """
        QAbstractButton.__init__(self)
        self._radius = radius
        self._grcolor = grcolor
        self._state = self.NORMAL
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self._radius, self._radius)

    def sizeHint(self):
        """
        返回控件大小
        :return:
        """
        return QSize(self._radius, self._radius)

    def set_state(self, enum):
        """
        获取控制事件更新控件状态
        :param enum:
        :return:
        """
        self._state = enum
        self.update()

    def mousePressEvent(self, event):
        """
        鼠标按下事件
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self.set_state(self.PRESS)
            QAbstractButton.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件
        :param event:
        :return:
        """
        #
        if self.rect().contains(event.pos()):
            self.set_state(self.HOVER)
        else:
            self.set_state(self.NORMAL)
        # if event.button() == Qt.LeftButton:
        #     self.clicked.emit()
        QAbstractButton.mouseReleaseEvent(self, event)

    def enterEvent(self, event):
        """
        鼠标进入控件事件
        :param event:
        :return:
        """
        self.set_state(self.HOVER)
        QAbstractButton.enterEvent(self, event)

    def leaveEvent(self, event):
        """
        鼠标离开控件事件
        :param event:
        :return:
        """
        self.set_state(self.NORMAL)
        QAbstractButton.leaveEvent(self, event)

    def paintEvent(self, event):
        """
        绘制控件
        :param event:
        :return:
        """
        # 设置颜色
        background_color = QColor(self._grcolor[0], self._grcolor[1], self._grcolor[2])
        if self._state == self.HOVER:
            background_color = setLuminance(self._grcolor, True, 0.2)
            background_color = QColor(background_color[0], background_color[1], background_color[2])
        elif self._state == self.PRESS:
            background_color = setLuminance(self._grcolor, True, 0.35)
            background_color = QColor(background_color[0], background_color[1], background_color[2])
        # 开始绘制
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        # 绘制圆形
        painter.setBrush(background_color)
        painter.drawEllipse(QRectF(QPointF(0, 0), QSizeF(self._radius, self._radius)))
        painter.end()

if __name__ == '__main__':
    test = setLuminance((31, 38, 35), True, 0.5)
    print(test)