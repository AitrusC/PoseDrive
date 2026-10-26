# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: test_ui
# Time    : 2024-09-09
# Contact : 906629272@qq.com

import sys
import uuid

from PySide2.QtWidgets import QApplication, QLabel, QWidget

try:
    # 包内导入：Maya 里 import PoseDrive / import PoseDrive.test_ui
    from .gui.icons import *
    from .gui.ui import MainWindow
    from .interface.protocol import JointProtocol, registerJointType, PoseProtocol, registerPoseType
    from .interface.gui import joint_list, pose_list
except (ImportError, ValueError):
    # 脚本方式运行：mayapy test_ui.py
    from gui.icons import *
    from gui.ui import MainWindow
    from interface.protocol import JointProtocol, registerJointType, PoseProtocol, registerPoseType
    from interface.gui import joint_list, pose_list


@registerJointType
class TestJointProtocol(JointProtocol):
    type_name = "test_joint"
    icon_path = IconPath.JOINT_PATH.value

    def __init__(self):
        self._name = uuid.uuid4().hex[:8]

    @classmethod
    def create(cls):
        return TestJointProtocol()

    def destroy(self):
        pass

    def info(self):
        return "TestJointProtocol"

    def view(self):
        return QLabel("TestJointProtocol")

    def dump(self):
        return self._name

    @classmethod
    def load(cls, data):
        joint = TestJointProtocol()
        joint._name = data
        return joint

    def name(self):
        return self._name


@registerPoseType
class TestPoseProtocol(PoseProtocol):
    type_name = "test_pose"
    icon_path = IconPath.BLENDSHAPE_PATH.value

    def __init__(self):
        self._name = uuid.uuid4().hex[:8]

    @classmethod
    def create(cls):
        return TestPoseProtocol()

    def driveAttribute(self):
        pass

    def destroy(self):
        pass

    def name(self):
        return self._name

    def info(self):
        return self._name

    def view(self):
        return QLabel("TestPoseProtocol")

    def dump(self):
        return self._name

    def load(self, data):
        pose = TestPoseProtocol()
        pose._name = data
        return pose


def get_host_app():
    """
    获取 Maya 主窗口；不在 Maya 里时返回 None
    :return: QWidget | None
    """
    try:
        from maya import OpenMayaUI as omui
        from shiboken2 import wrapInstance
        ptr = omui.MQtUtil.mainWindow()
        if ptr:
            return wrapInstance(int(ptr), QWidget)
    except Exception:
        pass

    app = QApplication.activeWindow()
    while app is not None:
        try:
            parent = app.parent()
        except AttributeError:
            break
        if parent is None:
            break
        app = parent
    return app


class ShowUIInMaya(MainWindow):
    def __init__(self, parent = None):
        if parent is None:
            parent = get_host_app()
        MainWindow.__init__(self, parent)


_ui = None


def show_ui_in_maya():
    """
    在 Maya 内显示窗口；重复调用会先关闭旧窗口
    :return: ShowUIInMaya
    """
    global _ui
    if _ui is not None:
        try:
            _ui.close()
            _ui.deleteLater()
        except RuntimeError:
            pass
        _ui = None
    _ui = ShowUIInMaya()
    _ui.show()
    _ui.raise_()
    _ui.activateWindow()
    return _ui


joint_list.append(TestJointProtocol())
joint_list.append(TestJointProtocol())
joint_list.append(TestJointProtocol())

pose_list.append(TestPoseProtocol())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
