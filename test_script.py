from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class CustomButton(QAbstractButton):
    doubleClicked = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置按钮为可切换
        self.setCheckable(True)

        # 按钮状态颜色
        self.colors = {
            "normal": QColor(220, 220, 220),
            "hover": QColor(200, 200, 200),
            "pressed": QColor(150, 150, 150),
            "selected": QColor(100, 150, 200)
        }

        # 鼠标追踪
        self.setMouseTracking(True)

    def setColor(self, state, color):
        """设置不同状态的颜色"""
        if state in self.colors:
            self.colors[state] = QColor(color)

    def sizeHint(self):
        """返回按钮的推荐大小"""
        return QSize(100, 40)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            # 按钮的选中状态会自动处理
            self.clicked.emit()
            self.update()

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == Qt.LeftButton:
            self.doubleClicked.emit()

    def enterEvent(self, event):
        """鼠标进入事件"""
        self.update()

    def leaveEvent(self, event):
        """鼠标离开事件"""
        self.update()

    def paintEvent(self, event):
        """绘制按钮"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 获取当前状态颜色
        if self.isDown():
            bg_color = self.colors["pressed"]
        elif self.underMouse():
            bg_color = self.colors["hover"]
        elif self.isChecked():
            bg_color = self.colors["selected"]
        else:
            bg_color = self.colors["normal"]

        # 绘制背景
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # 绘制图标
        if not self.icon().isNull():
            icon_size = self.height() - 10
            icon_rect = QRect(5, (self.height() - icon_size) // 2, icon_size, icon_size)
            self.icon().paint(painter, icon_rect)

        # 绘制文字
        painter.setPen(Qt.black)
        font = QFont()
        font.setPointSize(12)
        painter.setFont(font)

        text_x = self.height()  # 让文字在图标右侧
        painter.drawText(QRect(text_x, 0, self.width() - text_x, self.height()), Qt.AlignVCenter, self.text())

        painter.end()


app = QApplication([])

window = QWidget()
layout = QVBoxLayout()

# 创建自定义按钮
button = CustomButton(text="Click Me", icon=QIcon("C:/Users/AhriLi/Documents/maya/scripts/PoseDrive/gui/icons/plus.png"))

# 设置颜色
button.setColor("normal", QColor(240, 240, 240))
button.setColor("hover", QColor(200, 200, 200))
button.setColor("pressed", QColor(150, 150, 150))
button.setColor("selected", QColor(100, 150, 255))

# 连接信号
button.clicked.connect(lambda: print("Button clicked!"))
button.doubleClicked.connect(lambda: print("Button double-clicked!"))

layout.addWidget(button)
window.setLayout(layout)
window.show()

app.exec_()