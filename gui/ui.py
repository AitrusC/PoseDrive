# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: ui
# Time    : 2024-09-09
# Contact : 906629272@qq.com
# Description : 主窗口

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from .widget.widgetT import FramelessWindow, ListWidget
try:
    from ..interface.gui import addPose, pose_list, pose_types, addJoint, joint_types, joint_list, removeJoint, removePose
except (ImportError, ValueError):
    # 作为顶层包运行（如 mayapy test_ui.py / main.py）时，.. 会超出顶层包，
    # Python 3.7+ 抛的是 ValueError 而不是 ImportError，这里一并兜底。
    from interface.gui import addPose, pose_list, pose_types, addJoint, joint_types, joint_list, removeJoint, removePose


class PoseEditWidget(QWidget):
    """
    编辑窗口
    """

    def __init__(self, pose, parent = None):
        """
        初始化
        :param pose: 关节姿态
        :param parent:
        """
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setSpacing(0)

        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(5)

        v_layout = QVBoxLayout()
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(5)
        v_layout.addWidget(QLabel("关节姿态"))
        v_layout.addWidget(QLabel("X:"))

        h_layout.addWidget(QLabel("Y:"))
        h_layout.addLayout(v_layout)
        self.main_layout.addLayout(h_layout)

        self.main_layout.addStretch(0)
        self.pose_list_edit = ListWidget(u"SHAPE列表")
        self.pose_list_edit.setFixedHeight(240)
        self.pose_list_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.pose_list_edit.addShapeList()
        self.main_layout.addWidget(self.pose_list_edit)


class RightWidget(QWidget):
    """
    右侧窗口
    """

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.setItem(None)

    def clear(self):
        """
        清空右侧窗口
        :return:
        """
        for i in range(self.main_layout.count()):
            self.main_layout.itemAt(i).widget().deleteLater()

    def setItem(self, pose):
        """
        设置右侧窗口显示内容
        :param pose:
        :return:
        """
        self.clear()
        if pose:
            self.main_layout.addWidget(PoseEditWidget(pose))
        else:
            select_item_label = QLabel("请选择一个关节姿态")
            select_item_label.setMouseTracking(True)
            self.main_layout.addWidget(select_item_label)


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
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.left_widget = ListWidget(u"骨骼与驱动")
        self.left_widget.addJointPoseList()
        self.left_widget.add_joint_click.connect(self.addJointAndPose)
        self.left_widget.delete_joint_click.connect(self.destroyJointAndPose)
        self.left_widget.on_joint_pressed.connect(self.setPose)
        self.left_widget.jplist_widget.updateItems(
            [(i.name(), i.name(), i.icon_path) for i in joint_list]
            )
        self.left_widget.jplist_widget.updateChildItems(
            joint_list[0].name(),
            [(i.name(), i.name(), i.icon_path) for i in pose_list]
        )
        self.left_widget.setFixedWidth(250)
        self.left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.right_widget = RightWidget(self)
        # 测试
        self.right_widget.setItem(1)
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)

    def addJointAndPose(self, key):
        """
        添加关节姿态
        :return:
        """
        if key:
            print("addChildPose", key)
            addPose("test_pose")
            self.left_widget.jplist_widget.updateChildItems(
                key,
                [(i.name(), i.name(), i.icon_path) for i in pose_list]
            )
        else:
            print("addPose")
            addJoint("test_joint")
            self.left_widget.jplist_widget.updateItems(
                [(i.name(), i.name(), i.icon_path) for i in joint_list]
            )

    def setPose(self, key):
        """
        设置关节姿态
        :param key:
        :return:
        """
        print("setPose", key)

    def destroyJointAndPose(self, key):
        """
        添加子骨骼
        :param key:
        :return:
        """
        if key[1]:
            print("destroyChildPose", key[0], key[1])
            removePose(key[1])
            self.left_widget.jplist_widget.updateChildItems(
                key[0],
                [(i.name(), i.name(), i.icon_path) for i in pose_list]
            )
        else:
            if key[0]:
                print("removeChildPose", key[0])
                removeJoint(key[0])
                self.left_widget.jplist_widget.updateItems(
                    [(i.name(), i.name(), i.icon_path) for i in joint_list]
                )




class MainWindow(FramelessWindow):
    """
    主窗口
    """

    def __init__(self, parent = None):
        body_widget = BodyWidget()
        FramelessWindow.__init__(self, content_widget = body_widget, parent = parent)
        self.min_size = QSize(1080, 720)
        self.setObjectName("PoseDriveUI")
        self.resize(1080, 720)
        self.setMinimumSize(self.min_size)


def showUI():
    """
    窗口显示
    :return:
    """
    pass
