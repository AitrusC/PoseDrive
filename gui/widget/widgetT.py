# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: widgetT
# Time    : 2024-09-18
# Contact : 906629272@qq.com
# Description : 自定义控件模板

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *

try:
    from ..icons import *
except ImportError:
    pass


def _setLuminance(rgb, uord, percent):
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


def _setOpacity(rgba, uord, percent):
    """
    改变RGBA颜色的透明度（Alpha通道）
    :param rgba: RGBA元组，包含红、绿、蓝和透明度值 (r, g, b, a)
    :param uord: 提高或降低透明度 (True 增加, False 降低)
    :param percent: 提高或降低的百分比 (0~1)
    :return: 改变透明度后的RGBA值
    """
    r, g, b, a = rgba
    if uord:
        ud_a = round(min(255, a * (1 + percent)))  # 增加透明度，最大值为255
    else:
        ud_a = round(max(0, a * (1 - percent)))  # 降低透明度，最小值为0
    return r, g, b, ud_a


class _TitleBar(QWidget):
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

        # 读取窗口样式
        with open(__file__ + "/../qss/base.qss", "rb") as f:
            self.setStyleSheet(f.read().decode("utf-8"))

        # 窗口布局
        title_bar = _TitleBar(self)
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
        painter.setBrush(QColor(48, 55, 52))
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


class RoundButton(QAbstractButton):
    """
    圆形按钮控件
    """
    NORMAL, HOVER, PRESS = range(3)

    def __init__(self, radius = 25, grcolor = None):
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
            background_color = _setLuminance(self._grcolor, True, 0.2)
            background_color = QColor(background_color[0], background_color[1], background_color[2])
        elif self._state == self.PRESS:
            background_color = _setLuminance(self._grcolor, True, 0.35)
            background_color = QColor(background_color[0], background_color[1], background_color[2])
        # 开始绘制
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        # 绘制圆形
        painter.setBrush(background_color)
        painter.drawEllipse(QRectF(QPointF(0, 0), QSizeF(self._radius, self._radius)))
        painter.end()


class IconButton(QAbstractButton):
    """
    图标按钮控件
    """

    def __init__(self, icon_path, icon_size, margin = 5, hover_color = (0, 0, 0, 20), parent = None):
        """
        初始化图标按钮控件
        :param icon_path: 图标路径
        :param icon_size: 图标大小
        :param margin: 图标边距
        :param hover_color: 鼠标悬停颜色(默认透明度10)
        :param parent:
        """
        QAbstractButton.__init__(self, parent)
        self._hover = False
        self._pressed = False
        self.icon_path = icon_path
        self.icon_size = icon_size
        self.margin = margin
        self.hover_color = hover_color

        self.setFixedSize(QSize(icon_size + margin * 2, icon_size + margin * 2))

        self.icon = QPixmap(icon_path)
        self.icon = self.icon.scaled(icon_size, icon_size)

    def mousePressEvent(self, event):
        """
        鼠标按下事件
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self.update()
        QAbstractButton.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self._pressed = False
            self.update()
        QAbstractButton.mouseReleaseEvent(self, event)

    def enterEvent(self, event):
        """
        鼠标进入控件事件
        :param event:
        :return:
        """
        self._hover = True
        self.update()
        QAbstractButton.enterEvent(self, event)

    def leaveEvent(self, event):
        """
        鼠标离开控件事件
        :param event:
        :return:
        """
        self._hover = False
        self.update()
        QAbstractButton.leaveEvent(self, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        hover_color = QColor(self.hover_color[0], self.hover_color[1], self.hover_color[2], self.hover_color[3])
        pressed_color = _setOpacity(self.hover_color, True, 0.5)
        pressed_color = QColor(pressed_color[0], pressed_color[1], pressed_color[2], pressed_color[3])
        # if self.rect().contains(self.mapFromGlobal(QCursor.pos())):
        #     painter.setPen(Qt.NoPen)
        #     painter.setBrush(self.hover_color)
        #     painter.drawRect(self.rect())
        if self._pressed:
            painter.setPen(Qt.NoPen)
            painter.setBrush(pressed_color)
            painter.drawRect(self.rect())
        elif self._hover:
            painter.setPen(Qt.NoPen)
            painter.setBrush(hover_color)
            painter.drawRect(self.rect())
        painter.drawPixmap(self.rect().adjusted(self.margin, self.margin, -self.margin, -self.margin), self.icon)
        painter.end()


class SearchLine(QLineEdit):
    """
    搜索框控件
    """

    def __init__(self, placeholder_text = "joint ro pose name...", parent = None):
        """
        初始化搜索框控件
        :param placeholder_text: 提示文字
        :param parent:
        """
        QLineEdit.__init__(self, parent)
        self.setPlaceholderText(placeholder_text)
        self.setFixedHeight(20)
        self.setAlignment(Qt.AlignCenter)


class _TreeWidget(QWidget):
    """
    树形控件
    """

    def __init__(self, parent = None):
        """
        初始化树形控件
        :param parent:
        """
        QWidget.__init__(self, parent)
        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(0)
        self.tree_widget.setRootIsDecorated(False)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.tree_widget)

    def getTreeWidget(self):
        """
        获取树形控件
        :return: 树形控件
        """
        return self.tree_widget

    def addRootItem(self, text):
        """
        添加根节点
        :param text: 文本
        :return: 根节点
        """
        root_item = _RootTreeWidgetItem(self.tree_widget)
        root_item.setText(0, text)
        self.tree_widget.addTopLevelItem(root_item)
        return root_item

    def addRootChildItem(self, root_item, text, icon_path = None):
        """
        添加根子节点
        :param root_item: 根节点
        :param text: 文本
        :param icon_path: 图标路径
        :return: 子节点
        """
        child = root_item.addCustomItem(root_item, text, icon_path)
        return child

    def getRootItems(self):
        """
        获取根节点
        :return: 根节点列表
        """
        return [self.tree_widget.topLevelItem(i) for i in range(self.tree_widget.topLevelItemCount())]


class _RootTreeWidgetItem(QTreeWidgetItem):
    """
    根节点树形控件项
    """

    def __init__(self, text, parent = None):
        """
        初始化根节点树形控件项
        :param text: 文本
        :param parent:
        """
        QTreeWidgetItem.__init__(self, parent)
        self.setTextAlignment(0, Qt.AlignCenter)
        self.setSizeHint(0, QSize(0, 25))

    def addCustomItem(self, parent, text, icon_path = None):
        """
        添加子节点
        :param parent: 父节点
        :param text: 文本
        :param icon_path: 图标路径
        :return:
        """
        item = _ChildTreeWidgetItem(parent)
        item.setText(0, text)
        if icon_path:
            item.setIcon(0, QIcon(icon_path))
        self.addChild(item)
        return item


class _ChildTreeWidgetItem(QTreeWidgetItem):
    """
    子节点树形控件项
    """

    def __init__(self, text, parent = None):
        """
        初始化子节点树形控件项
        :param text: 文本
        :param parent:
        """
        QTreeWidgetItem.__init__(self, parent)
        self.setBackgroundColor(0, QColor(63, 70, 68))
        self.setSizeHint(0, QSize(0, 20))


class _ToolButton(QPushButton):
    """
    工具按钮控件
    """
    doubleClicked = Signal(bool)

    def __init__(self, parent = None):
        """
        初始化工具按钮控件
        :param parent: 父控件
        """
        QPushButton.__init__(self, parent)
        self._double_click = False
        self.setMouseTracking(True)
        self.setCheckable(True)
        self.setFixedHeight(25)

    def mouseDoubleClickEvent(self, event):
        """
        鼠标双击事件
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self._double_click = not self._double_click
            self.doubleClicked.emit(self._double_click)
        QPushButton.mouseDoubleClickEvent(self, event)

    def setDoubleClicked(self, double_clicked):
        """
        设置是否双击
        :param double_clicked:
        :return:
        """
        self._double_click = double_clicked


class _CollapsibleBox(QWidget):
    """
    折叠控件
            + 折叠控件
                ||
            - 折叠控件
            |- 控件01
            |- 控件02
    """

    def __init__(self, title = "", icon_path = None, parent = None, animation_duration = 300):
        """
        初始化
        :param title: 标题
        :param parent: 父对象
        :param animation_duration: 动画时间
        """
        QWidget.__init__(self, parent)
        self.animation_duration = animation_duration
        # 创建QToolButton用于激活下拉，双击下拉时激活折叠动画
        self.toggle_button = _ToolButton(title)
        if icon_path:
            self.toggle_button.setIcon(QIcon(icon_path))
        # 点击激活self.on_pressed
        self.toggle_button.doubleClicked.connect(self.on_pressed)
        # 并行动画容器组。在它启动时将启动组内所有动画，即并行运行所有动画。当持续时间最长的动画结束时，动画组结束。
        self.toggle_animation = QParallelAnimationGroup()
        # QScrollArea滚动控件
        self.content_area = QScrollArea(maximumHeight = 0, minimumHeight = 0)
        # 设置水平与垂直大小调整策略，QSizePolicy类用于描述一个窗口小部件如何在布局中调整自己的大小。
        # QSizePolicy.Expanding 用于指示窗口小部件在布局中有能力并且愿意扩展以填充可用空间。
        # QSizePolicy.Fixed 用于指示窗口小部件应该保持其固定大小，不应进行任何扩展或收缩。
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # 取消边框
        self.content_area.setFrameShape(QFrame.NoFrame)
        # 设置动画QPropertyAnimation(QObject target, QByteArray propertyName, QObject parent)
        # target为准备进行动画动作的对象，可以不填，不填时动画对象创建后要使用setTargetObject来设置动作对象；
        # propertyName为动作对象变更的属性，可以不填，不填时动画对象创建并设置动画动作的对象要使用setPropertyName来设置变更的属性.
        # parent为动作对象的父对象，可以不填，不填默认为None。
        # 将动画添加到动画组中，分别控制控件最小高度、最大高度和内容区域最大高度
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.content_area, b"maximumHeight"))
        # 构建布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)
        self.setLayout(self.main_layout)

        item_layout = QVBoxLayout()
        item_layout.setAlignment(Qt.AlignTop)
        item_layout.setContentsMargins(0, 0, 0, 0)
        for i in range(10):
            item_layout.addWidget(_ListItemWidget(f"item {i}", icon_path = IconPath.DELETE_PATH.value))
        self.setContentLayout(item_layout)

    @Slot()
    def on_pressed(self, checked):
        """
        播放动画
        :return:
        """
        direction = QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward
        self.toggle_animation.setDirection(direction)
        self.toggle_animation.start()

    def setContentLayout(self, content_layout):
        """
        添加布局
        :param content_layout: 布局
        :return:
        """
        # 销毁QScrollArea的子部件
        self.content_area.destroy()
        # 添加布局
        self.content_area.setLayout(content_layout)
        # 计算折叠和展开时的高度
        collapsed_height = (self.sizeHint().height() - self.content_area.maximumHeight())
        content_height = content_layout.sizeHint().height()
        # 更新动画的开始值和结束值
        for i in range(self.toggle_animation.animationCount()):
            # 设置动画值
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(self.animation_duration)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)
        content_animation = self.toggle_animation.animationAt(self.toggle_animation.animationCount() - 1)
        content_animation.setDuration(self.animation_duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


class _ListItemWidget(QWidget):
    """
    列表项控件
    """

    def __init__(self, text, icon_path = None, parent = None):
        """
        初始化列表项控件
        :param text:
        :param icon_path:
        :param parent:
        """
        QWidget.__init__(self, parent)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)

        if icon_path:
            icon_label = QLabel(self)
            icon_label.setPixmap(QPixmap(icon_path))
            self.main_layout.addWidget(icon_label)
        self.text_label = QLabel(text, self)
        self.main_layout.addWidget(self.text_label)


class JPlistWidget(QScrollArea):
    """
    骨骼与POSE列表控件
    """

    def __init__(self, parent = None):
        """
        初始化骨骼与POSE列表控件
        :param parent:
        """
        QScrollArea.__init__(self, parent)
        self.setWidgetResizable(True)

        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(2)
        self.setWidget(self.main_widget)
        for i in range(10):
            self.main_layout.addWidget(_CollapsibleBox("骨骼列表", icon_path = IconPath.PLUS_PATH.value))


__all__ = ['FramelessWindow', 'RoundButton', 'IconButton', 'SearchLine', 'JPlistWidget']

if __name__ == '__main__':
    test = _setLuminance((73, 117, 104), False, 0.1)
    test_o = _setOpacity((48, 55, 52, 10), False, 0.1)
    print(test, test_o)
    # app = QApplication([])
    #
    # w = QWidget()
    # layout = QVBoxLayout(w)
    # layout.setAlignment(Qt.AlignCenter)
    # layout.addWidget(ToolButton())
    # w.show()
    #
    # app.exec_()
