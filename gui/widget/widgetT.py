# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: widgetT
# Time    : 2024-09-18
# Contact : 906629272@qq.com
# Description : 自定义控件模板

from PySide2.QtCore import *
from PySide2.QtGui import *
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

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setObjectName("titleBar")
        self.setFixedHeight(30)
        self.setMouseTracking(True)
        self.get_parent = parent
        self._drag_armed = False
        self._drag_press_global = QPoint()
        self._drag_window_pos = QPoint()
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
        self.main_layout.setContentsMargins(5, 5, 5, 0)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setSpacing(2)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addSpacing(3)
        # 菜单按钮
        for i in ["文件", "工具", "帮助"]:
            menu_button = MenuButton(i)
            menu_button.addOption("Option1", func = lambda: print("Option1"))
            menu_button.addOption("Option2", IconPath.BLENDSHAPE_PATH.value, func = lambda: print("Option2"))
            menu_button.addOption("Option3", IconPath.BLENDSHAPE_PATH.value, func = lambda: print("Option3"))
            self.main_layout.addWidget(menu_button)

        self.main_layout.addWidget(SearchFunctionWidget(self))
        self.main_layout.addStretch(0)
        self.main_layout.addWidget(self.min_button)
        self.main_layout.addSpacing(2)
        self.main_layout.addWidget(self.max_button)
        self.main_layout.addSpacing(2)
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
            self._drag_armed = False
            self.__toggleMaxState()

    def mousePressEvent(self, event):
        """
        鼠标按下事件：记录拖动起点，超过阈值后再交给系统原生移动
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton and self._isDragRegion(event.pos()):
            self._drag_armed = True
            self._drag_press_global = event.globalPos()
            self._drag_window_pos = self.get_parent.pos()
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件：超过拖动阈值后启动系统原生移动（支持 Snap、跨屏、最大化还原）
        :param event:
        :return:
        """
        if self._drag_armed and (event.buttons() & Qt.LeftButton):
            moved = (event.globalPos() - self._drag_press_global).manhattanLength()
            if moved >= QApplication.startDragDistance():
                handle = self.get_parent.windowHandle()
                started = False
                if handle is not None and hasattr(handle, "startSystemMove"):
                    started = handle.startSystemMove()
                if started:
                    self._drag_armed = False
                elif self.get_parent.isMaximized():
                    # Qt < 5.15 无法原生还原最大化窗口，直接放弃拖动，避免尺寸错乱
                    self._drag_armed = False
                else:
                    # Qt < 5.15（如 Maya 2020）回退到手动移动
                    self.get_parent.move(self._drag_window_pos + event.globalPos() - self._drag_press_global)
            event.accept()
            return
        event.ignore()

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件：结束拖动准备
        :param event:
        :return:
        """
        self._drag_armed = False
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
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Window)
        self._resize_edges = 0
        self._resize_press_global = QPoint()
        self._resize_geom = None
        if content_widget is None:
            content_widget = QWidget()

        # 读取窗口样式
        with open(__file__ + "/../qss/base.qss", "rb") as f:
            self.setStyleSheet(f.read().decode("utf-8"))

        # 窗口布局
        title_bar = _TitleBar(self)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(title_bar)
        self.main_layout.addWidget(content_widget)

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

    def _edge_at(self, pos):
        """
        判断窗口内坐标命中的缩放边
        :param pos:
        :return: Qt.Edges
        """
        edges = Qt.Edges()
        if pos.x() <= self.Margins:
            edges |= Qt.LeftEdge
        if pos.x() >= self.width() - self.Margins:
            edges |= Qt.RightEdge
        if pos.y() <= self.Margins:
            edges |= Qt.TopEdge
        if pos.y() >= self.height() - self.Margins:
            edges |= Qt.BottomEdge
        return edges

    def mousePressEvent(self, event):
        """
        鼠标按下事件：边缘缩放交给系统原生处理
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton and not (self.isMaximized() or self.isFullScreen()):
            edges = self._edge_at(event.pos())
            handle = self.windowHandle()
            if int(edges) and handle is not None:
                if hasattr(handle, "startSystemResize") and handle.startSystemResize(edges):
                    event.accept()
                    return
                # Qt < 5.15（如 Maya 2020）回退到手动缩放
                self._resize_edges = int(edges)
                self._resize_press_global = event.globalPos()
                self._resize_geom = QRect(self.geometry())
                event.accept()
                return
        # 消费掉落在窗口空白处的事件，避免继续传给 Maya 主窗口
        event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标移动事件：只负责边缘光标，缩放由系统接管
        :param event:
        :return:
        """
        if self.isMaximized() or self.isFullScreen():
            self.setCursor(Qt.ArrowCursor)
            return
        if self._resize_edges and (event.buttons() & Qt.LeftButton) and self._resize_geom is not None:
            self._fallback_resize(event)
        edges = self._edge_at(event.pos())
        left = bool(edges & Qt.LeftEdge)
        right = bool(edges & Qt.RightEdge)
        top = bool(edges & Qt.TopEdge)
        bottom = bool(edges & Qt.BottomEdge)
        if (left and top) or (right and bottom):
            self.setCursor(Qt.SizeFDiagCursor)
        elif (right and top) or (left and bottom):
            self.setCursor(Qt.SizeBDiagCursor)
        elif left or right:
            self.setCursor(Qt.SizeHorCursor)
        elif top or bottom:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def _fallback_resize(self, event):
        """
        Qt < 5.15 的手动缩放兜底（锚点法，避免累计误差）
        :param event:
        :return:
        """
        delta = event.globalPos() - self._resize_press_global
        rect = QRect(self._resize_geom)
        if self._resize_edges & int(Qt.LeftEdge):
            rect.setLeft(min(rect.left() + delta.x(), rect.right() - self.minimumWidth()))
        if self._resize_edges & int(Qt.RightEdge):
            rect.setRight(max(rect.right() + delta.x(), rect.left() + self.minimumWidth()))
        if self._resize_edges & int(Qt.TopEdge):
            rect.setTop(min(rect.top() + delta.y(), rect.bottom() - self.minimumHeight()))
        if self._resize_edges & int(Qt.BottomEdge):
            rect.setBottom(max(rect.bottom() + delta.y(), rect.top() + self.minimumHeight()))
        self.setGeometry(rect)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件：清理手动缩放状态
        :param event:
        :return:
        """
        self._resize_edges = 0
        self._resize_geom = None
        event.accept()

    def leaveEvent(self, event):
        """
        鼠标离开窗口时恢复默认光标
        :param event:
        :return:
        """
        self.setCursor(Qt.ArrowCursor)
        QWidget.leaveEvent(self, event)


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

    def __init__(self, placeholder_text = u"搜索...", parent = None):
        """
        初始化搜索框控件
        :param placeholder_text: 提示文字
        :param parent:
        """
        QLineEdit.__init__(self, parent)
        self.setMouseTracking(True)
        self.setPlaceholderText(placeholder_text)
        self.setFixedHeight(20)
        self.setAlignment(Qt.AlignCenter)


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
    item_clicked = Signal(str)

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
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_area)
        self.setLayout(self.main_layout)

        self.item_layout = QVBoxLayout()
        self.item_layout.setAlignment(Qt.AlignTop)
        self.item_layout.setContentsMargins(0, 0, 0, 0)
        self.item_layout.setSpacing(2)
        # self.setContentLayout(self.item_layout)
        # for i in range(10):
        #     self.addItem(_ListItemWidget(f"item {i}", icon_path = IconPath.DELETE_PATH.value))

    @Slot()
    def on_pressed(self, checked):
        """
        播放动画
        :return:
        """
        direction = QAbstractAnimation.Forward if checked else QAbstractAnimation.Backward
        self.toggle_animation.setDirection(direction)
        self.toggle_animation.start()

    def setContentLayout(self, layout = None):
        """
        添加布局
        :param layout: 布局
        :return:
        """
        # 销毁QScrollArea的子部件
        self.content_area.destroy()
        # 添加布局
        self.content_area.setLayout(layout)
        # 计算折叠和展开时的高度
        # 计算折叠时的高度(总高度减去内容高度)
        collapsed_height = (self.sizeHint().height() - self.content_area.maximumHeight())
        # 计算内容区域的高度
        content_height = layout.sizeHint().height()
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

    def addItem(self, key, name, icon_path = None):
        """
        添加子项
        :param key: 键
        :param name: 名称
        :param icon_path: 图标路径
        :return:
        """
        item = _ListItemWidget(name, icon_path)
        item.clicked.connect(lambda: self.item_clicked.emit(key))
        self.item_layout.addWidget(item)
        # self.setContentLayout(self.item_layout)

    def updateItems(self, item):
        """
        更新子项
        :param item: 子项
        :return:
        """
        self.clearItems()
        for key, name, icon_path in item:
            self.addItem(key, name, icon_path)
        self.setContentLayout(self.item_layout)

    def clearItems(self):
        """
        清空子项
        :return:
        """
        for i in range(self.item_layout.count()):
            self.item_layout.itemAt(i).widget().deleteLater()


class _ListItemWidget(QWidget):
    """
    列表项控件
    """
    NORMAL, HOVER, PRESS = range(3)
    clicked = Signal()

    def __init__(self, text, icon_path = None, parent = None):
        """
        初始化列表项控件
        :param text:
        :param icon_path:
        :param parent:
        """
        QWidget.__init__(self, parent)
        self.setFixedHeight(25)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        if icon_path:
            icon_label = QLabel(self)
            icon_label.setPixmap(QPixmap(icon_path))
            self.main_layout.addWidget(icon_label)
        self.text_label = QLabel(text, self)
        self.main_layout.addWidget(self.text_label)

        self._state = self.NORMAL

    def setState(self, enum):
        """
        设置状态
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
            self.setState(self.PRESS)

    def mouseReleaseEvent(self, event):
        """
        鼠标释放事件
        :param event:
        :return:
        """
        if self.rect().contains(event.pos()):
            self.setState(self.HOVER)
            self.clicked.emit()
        else:
            self.setState(self.NORMAL)

    def enterEvent(self, event):
        """
        鼠标进入事件
        :param event:
        :return:
        """
        self.setState(self.HOVER)
        QWidget.enterEvent(self, event)

    def leaveEvent(self, event):
        """
        鼠标离开事件
        :param event:
        :return:
        """
        self.setState(self.NORMAL)
        QWidget.leaveEvent(self, event)

    def paintEvent(self, event):
        """
        绘制控件
        :param event:
        :return:
        """
        background_color = QColor(55, 62, 59)
        if self._state == self.HOVER:
            background_color = QColor(58, 70, 63)
        elif self._state == self.PRESS:
            background_color = QColor(51, 63, 56)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(background_color)
        painter.drawRect(self.rect())
        painter.end()


class _EButtonGroup(QButtonGroup):
    """
    保持独占模式下也能使得所有按钮处于未选中状态
    """

    def __init__(self, parent = None):
        """
        初始化按钮组
        :param parent:
        """
        QButtonGroup.__init__(self, parent)
        self.setExclusive(False)
        # 记录当前选中的按钮
        self.current_checked_button = None
        self.buttonClicked.connect(self.on_button_clicked)

    def on_button_clicked(self, button):
        """
        按钮点击事件
        :param button:
        :return:
        """
        # 如果点击的按钮是当前选中的按钮，取消选中
        if button == self.current_checked_button:
            button.setChecked(False)
            self.current_checked_button = None
        else:
            # 否则，取消先前按钮的选中状态并设置当前按钮为选中
            if self.current_checked_button:
                self.current_checked_button.setChecked(False)
            self.current_checked_button = button
            button.setChecked(True)

    def removeButton(self, button):
        """
        移除按钮
        :param button:
        :return:
        """
        if button == self.current_checked_button:
            self.current_checked_button = None
        QButtonGroup.removeButton(self, button)


class _JPlistWidget(QScrollArea):
    """
    骨骼与POSE列表控件
    """
    joint_pressed = Signal(str)
    item_clicked = Signal(list)

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
        self.button_group = _EButtonGroup(self)

    def addJointItem(self, key, joint_name, icon_path = None):
        """
        添加骨骼项
        :param key: 第几项
        :param joint_name: 骨骼名称
        :param icon_path: 图标路径
        :return:
        """
        item = _CollapsibleBox(joint_name, icon_path)
        self.button_group.addButton(item.toggle_button)
        item.toggle_button.clicked.connect(lambda: self.joint_pressed.emit(key))
        item.item_clicked.connect(lambda x: self.item_clicked.emit([key, x]))
        self.main_layout.addWidget(item)

    def updateItems(self, item):
        """
        更新项
        :param item: 项
        :return:
        """
        self.clearItems()
        for key, joint_name, icon_path in item:
            self.addJointItem(key, joint_name, icon_path)

    def clearItems(self):
        """
        清空项
        :return:
        """
        for i in range(self.main_layout.count()):
            self.button_group.removeButton(self.main_layout.itemAt(i).widget().toggle_button)
            self.main_layout.itemAt(i).widget().deleteLater()

    def updateChildItems(self, key, item):
        """
        更新子项
        :param key: 第几项
        :param item: 子项
        :return:
        """
        for i in range(self.main_layout.count()):
            if self.main_layout.itemAt(i).widget().toggle_button.text() == key:
                self.main_layout.itemAt(i).widget().updateItems(item)
                break


class _ShapeListWidget(QScrollArea):
    """
        SHAPE列表控件
    """
    on_pressed = Signal(str)

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

    def addPoseItem(self, key, pose_name, icon_path = None):
        """
        添加骨骼项
        :param key: 第几项
        :param pose_name: 名称
        :param icon_path: 图标路径
        :return:
        """
        item = _ListItemWidget(pose_name, icon_path)
        item.clicked.connect(lambda: self.on_pressed.emit(key))
        self.main_layout.addWidget(item)

    def updateItems(self, item):
        """
        更新项
        :param item: 项
        :return:
        """
        self.clearItems()
        for key, joint_name, icon_path in item:
            self.addPoseItem(key, joint_name, icon_path)

    def clearItems(self):
        """
        清空项
        :return:
        """
        for i in range(self.main_layout.count()):
            self.main_layout.itemAt(i).widget().deleteLater()


class ListWidget(QWidget):

    on_pressed = Signal(str)
    on_joint_pressed = Signal(list)
    add_click = Signal()
    delete_click = Signal(str)
    add_joint_click = Signal(str)
    delete_joint_click = Signal(list)

    def __init__(self, title, parent = None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        # 读取窗口样式(子类化QWidget后使用QSS不能生效, 需在自定义Widget中重写paintEvent函数以确保QSS的正确应用)
        # with open(__file__ + "/../qss/leftWidget.qss", "rb") as f:
        #     self.setStyleSheet(f.read().decode("utf-8"))
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setAlignment(Qt.AlignCenter)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setAlignment(Qt.AlignCenter)
        h_layout.addWidget(QLabel(title))
        h_layout.addStretch(0)
        self._add_button = IconButton(IconPath.PLUS_PATH.value, 20)
        self._delete_button = IconButton(IconPath.DELETE_PATH.value, 20)
        h_layout.addWidget(self._add_button)
        h_layout.addWidget(self._delete_button)
        self.main_layout.addLayout(h_layout)
        self.main_layout.setSpacing(2)

        self.search_line = SearchLine(parent = self)
        self.main_layout.addWidget(self.search_line)

    def addShapeList(self):
        """
        添加POSE列表
        :return:
        """
        self._add_button.clicked.connect(self.add_click.emit)
        self._delete_button.clicked.connect(lambda: self.delete_click.emit(self._now_item_key))
        self._now_item_key = None
        self.poselist_widget = _ShapeListWidget(self)
        self.main_layout.addWidget(self.poselist_widget)
        self.poselist_widget.on_pressed.connect(self._setNowItemKey)
        self.poselist_widget.on_pressed.connect(self.on_pressed.emit)

    def addJointPoseList(self):
        """
        添加骨骼与POSE列表
        :return:
        """
        self._add_button.clicked.connect(lambda : self.add_joint_click.emit(self._now_joint_key))
        self._delete_button.clicked.connect(self._sendDeleteJointSignal)
        self._now_joint_key = None
        self._now_joint_child_key = None
        self.jplist_widget = _JPlistWidget(self)
        self.main_layout.addWidget(self.jplist_widget)
        self.jplist_widget.joint_pressed.connect(self._setNowJointKey)
        self.jplist_widget.item_clicked.connect(self._setNowJointChildKey)
        self.jplist_widget.item_clicked.connect(self.on_joint_pressed.emit)

    def _setNowJointChildKey(self, key):
        """
        设置当前子骨骼
        :param key:
        :return:
        """
        self._now_joint_key, self._now_joint_child_key = key

    def _sendDeleteJointSignal(self):
        """
        发送删除骨骼信号
        :return:
        """
        self.delete_joint_click.emit([self._now_joint_key, self._now_joint_child_key])
        self._now_joint_key = None
        self._now_joint_child_key = None

    def _setNowJointKey(self, key):
        """
        设置当前骨骼
        :param key:
        :return:
        """
        if self._now_joint_key == key:
            self._now_joint_key = None
        else:
            self._now_joint_key = key

    def _setNowItemKey(self, key):
        """
        设置当前项
        :param key:
        :return:
        """
        self._now_item_key = key

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


class _MenuWidget(QMenu):
    """
    菜单控件
    """

    def __init__(self, parent = None):
        """
        初始化菜单控件
        :param parent:
        """
        QMenu.__init__(self, parent)


class MenuButton(QAbstractButton):
    """
    菜单控件
    """

    def __init__(self, text, parent = None):
        """
        初始化菜单控件
        :param text: 文本
        :param parent:
        """
        QAbstractButton.__init__(self, parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 0, 5, 0)
        self.text_label = QLabel(text, self)
        self.text_label.setMouseTracking(True)
        self.main_layout.addWidget(self.text_label)

        self.clicked.connect(self.showMenu)

        self._options = []

    def addOption(self, text, icon_path = None, func = None):
        """
        添加选项
        :param text: 文本
        :param icon_path: 图标路径
        :param func: 回调函数
        :return:
        """
        self._options.append((text, icon_path, func))

    def showMenu(self):
        """
        显示菜单
        :return:
        """
        menu = _MenuWidget(self)
        for text, icon_path, func in self._options:
            if icon_path:
                action = QAction(QIcon(icon_path), text, self)
            else:
                action = QAction(text, self)
            if func:
                action.triggered.connect(func)
            menu.addAction(action)
        menu.exec_(self.mapToGlobal(QPoint(0, self.height())))

    def paintEvent(self, event):
        """
        绘制背景
        :param event:
        :return:
        """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        if self.rect().contains(self.mapFromGlobal(QCursor.pos())):
            painter.setBrush(QColor(37, 44, 42))
            painter.drawRect(self.rect())
        painter.end()


class SearchFunctionWidget(SearchLine):
    """
    搜索控件
    """

    def __init__(self, parent = None):
        """
        初始化搜索控件
        :param parent:
        """
        SearchLine.__init__(self, "SearchFunction", parent)
        # self.resize(600, 30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def mousePressEvent(self, event):
        """
        鼠标按下事件
        :param event:
        :return:
        """
        if event.button() == Qt.LeftButton:
            self.showSearchWindow()

    def showSearchWindow(self):
        """
        显示搜索窗口
        :return:
        """
        search_window = SearchFunctionWindow([
            ("1", u"1骨骼列表", IconPath.PLUS_PATH.value),
            ("2", u"2POSE列表", IconPath.PLUS_PATH.value),
            ("3", u"3工具列表", IconPath.PLUS_PATH.value),
            ("4", u"4设置列表", IconPath.PLUS_PATH.value),
            ("5", u"5帮助列表", IconPath.PLUS_PATH.value),
            ("6", u"6关于列表", IconPath.PLUS_PATH.value),
            ("7", u"7测试列表", IconPath.PLUS_PATH.value),
            ("8", u"8测试列表", IconPath.PLUS_PATH.value),
            ("9", u"9测试列表", IconPath.PLUS_PATH.value),
            ("10", u"10测试列表", IconPath.PLUS_PATH.value),
        ], self)
        search_window.move(self.mapToGlobal(QPoint(0, 0)))
        search_window.setFixedWidth(self.width())
        search_window.show()


class SearchFunctionWindow(QWidget):
    """
    搜索窗口
    """
    selected = Signal(str)
    def __init__(self, options, parent = None):
        """
        初始化搜索窗口
        :param options: 项列表
        :param parent:
        """
        QWidget.__init__(self, parent)
        self.options = options
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.search_line = SearchLine("SearchFunction", self)
        self.main_layout.addWidget(self.search_line)
        self.list_widget = _ShapeListWidget(self)
        self.search_line.textChanged.connect(self.search)
        self.list_widget.on_pressed.connect(self.listItemClicked)
        self.list_widget.on_pressed.connect(self.selected.emit)
        self.main_layout.addWidget(self.list_widget)
        self.main_layout.addStretch(0)

    def search(self, text):
        """
        搜索
        :param text: 文本
        :return:
        """
        if text.strip() == "":
            items = []
        else:
            items = [(key, name, icon_path) for key, name, icon_path in self.options if text in name]
        self.list_widget.updateItems(items)

    def listItemClicked(self, item):
        """
        列表项点击事件
        :param item: 项
        :return:
        """
        self.close()

    def showEvent(self, event):
        """
        显示事件
        :param event:
        :return:
        """
        self.search_line.setFocus()
        QApplication.instance().focusChanged.connect(self.focusChanged)

    def focusChanged(self, old, now):
        """
        焦点变化事件
        :param old: 旧焦点
        :param now: 新焦点
        :return:
        """
        if now is None or not self.isAncestorOf(now):
            self.close()

    def paintEvent(self, event):
        """
        绘制背景
        :param event:
        :return:
        """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(58, 65, 63))
        painter.drawRect(self.rect())
        painter.end()


__all__ = ['FramelessWindow', 'ListWidget']

if __name__ == '__main__':
    test = _setLuminance((55, 62, 59), False, 0.05)
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
