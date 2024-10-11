# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: test_ui
# Time    : 2024-09-09
# Contact : 906629272@qq.com

import sys
from PySide2.QtWidgets import QApplication, QVBoxLayout, QWidget
from gui.ui import MainWindow

class TestUI(QWidget):
    def __init__(self, parent=None):
        super(TestUI, self).__init__(parent)
        layout = QVBoxLayout()
        self.left_widget = LeftWidget()
        layout.addWidget(self.left_widget)
        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())