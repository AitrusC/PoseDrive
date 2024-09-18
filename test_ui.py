# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: test_ui
# Time    : 2024-09-09
# Contact : 906629272@qq.com

import sys
from PySide2.QtWidgets import QApplication
from gui.ui import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())