# coding=utf-8
# @FileName      :__init__
# @Time          :2024/9/8 19:20
# @Author        :AhrIlI
# @Contact       :906629272@qq.com
"""
PoseDrive：Maya 姿态驱动工具。

Maya 脚本编辑器里这样用：

    import PoseDrive
    PoseDrive.show_ui_in_maya()
"""

try:
    from importlib import reload
except ImportError:
    pass


def show_ui_in_maya():
    """
    在 Maya 中打开主窗口（当前使用 test_ui 里的演示实现）
    :return: ShowUIInMaya
    """
    from .test_ui import show_ui_in_maya as _show_ui_in_maya
    return _show_ui_in_maya()


__all__ = ["show_ui_in_maya"]

