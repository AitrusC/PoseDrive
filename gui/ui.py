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
from .preview_data import JointPosePreviewData


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
        while self.main_layout.count():
            widget = self.main_layout.takeAt(0).widget()
            widget.hide()
            widget.deleteLater()

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
    """UI 预览：只操作注入的测试数据，不访问 Maya 场景。"""

    def __init__(self, parent=None, data=None):
        QWidget.__init__(self, parent)
        self.data = data if data is not None else JointPosePreviewData()
        self.setMouseTracking(True)
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.left_widget = ListWidget(u"骨骼与驱动")
        self.left_widget.addJointPoseList()
        self.left_widget.add_joint_click.connect(self.addJointCollection)
        self.left_widget.add_pose_click.connect(self.addPoseToCollection)
        self.left_widget.delete_joint_click.connect(self.removeSelectedItem)
        self.left_widget.selection_changed.connect(self.setPose)
        self.left_widget._add_button.setEnabled(self.data.joint_factory is not None)
        self.left_widget.setFixedWidth(250)
        self.left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.right_widget = RightWidget(self)
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.right_widget)
        self.refreshCollections()

    def _syncCollectionHeaders(self):
        listing = self.left_widget.jplist_widget
        listing.updateItems(self.data.jointRows())
        for box in listing._items_by_key.values():
            box.add_pose_button.setEnabled(self.data.pose_factory is not None)

    def refreshCollections(self):
        """手动修改测试数据后可刷新；保留仍然有效的选择及展开状态。"""
        self._syncCollectionHeaders()
        listing = self.left_widget.jplist_widget
        for key in self.data.joints:
            listing.updateChildItems(key, self.data.poseRows(key))
        joint_key = self.left_widget._now_joint_key
        pose_key = self.left_widget._now_joint_child_key
        if joint_key not in self.data.joints:
            joint_key, pose_key = None, None
        elif pose_key not in self.data.joints[joint_key]["poses"]:
            pose_key = None
        self.left_widget.setSelection(joint_key, pose_key)

    def addJointCollection(self):
        key = self.data.addJoint()
        if key is not None:
            self._syncCollectionHeaders()
            self.left_widget.setSelection(key)
            listing = self.left_widget.jplist_widget
            listing.ensureWidgetVisible(listing._items_by_key[key])

    def addPoseToCollection(self, joint_key):
        pose_key = self.data.addPose(joint_key)
        if pose_key is None:
            return
        listing = self.left_widget.jplist_widget
        listing.updateChildItems(joint_key, self.data.poseRows(joint_key))
        listing._items_by_key[joint_key].setExpanded(True)
        self.left_widget.setSelection(joint_key, pose_key)

    def setPose(self, selection):
        self.right_widget.setItem(self.data.pose(*selection))

    def removeSelectedItem(self, selection):
        joint_key, pose_key = selection
        self.data.remove(joint_key, pose_key)
        if joint_key in self.data.joints:
            self.left_widget.jplist_widget.updateChildItems(
                joint_key, self.data.poseRows(joint_key))
            self.left_widget.setSelection(joint_key)
        else:
            self._syncCollectionHeaders()
            self.left_widget.setSelection()


class MainWindow(FramelessWindow):
    """
    主窗口
    """

    def __init__(self, parent = None, data = None):
        body_widget = BodyWidget(data=data)
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
