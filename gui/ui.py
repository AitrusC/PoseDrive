# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: ui
# Time    : 2024-09-09
# Contact : 906629272@qq.com

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class MainWindow(QWidget):
    """
    主窗口
    """

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setObjectName("PoseDriveUI")
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Window)
        self.resize(1080, 720)
        self.setMinimumSize(1080, 720)


def showUI():
    """
    窗口显示
    :return:
    """
    pass
