# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: protocol
# Time    : 2024-11-03
# Contact : 906629272@qq.com
"""
定义POSE与SHAPE的通信协议
"""

from abc import abstractmethod
from PySide2.QtWidgets import QWidget


pose_types = []
joint_types = []

def registerPoseType(cls):
    pose_types.append(cls)
    return cls


def registerJointType(cls):
    joint_types.append(cls)
    return cls


class JointProtocol(object):
    """
    关节的增删改查协议
    """
    type_name = "unimplemented" # type: str
    icon_path = None # type: None|str

    @classmethod
    def create(cls):
        # type: () -> JointProtocol
        """
        创建关节
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def destroy(self):
        # type: () -> None
        """
        销毁关节
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def name(self):
        # type: () -> str
        """
        获取关节名称
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def info(self):
        # type: () -> str
        """
        获取关节信息并展示
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def view(self):
        # type: () -> QWidget
        """
        展示关节
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def dump(self):
        # type: () -> str
        """
        序列化关节信息
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def load(self, data):
        # type: (str) -> JointProtocol
        """
        反序列化关节信息
        :param data:
        :return:
        """
        raise NotImplementedError()


class PoseProtocol(object):
    """
    Pose的增删改查协议
    """
    type_name = "unimplemented" # type: str
    icon_path = None # type: None|str

    @classmethod
    def create(cls):
        # type: () -> PoseProtocol
        """
        创建pose
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def driveAttribute(self):
        # type: () -> str
        """
        获取驱动属性，用于驱动其他属性
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def destroy(self):
        # type: () -> None
        """
        销毁pose
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def name(self):
        # type: () -> str
        """
        获取pose名称
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def info(self):
        # type: () -> str
        """
        获取pose信息并展示
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def view(self):
        # type: () -> QWidget
        """
        展示pose
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def dump(self):
        # type: () -> str
        """
        序列化pose信息
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def load(self, data):
        # type: (str) -> PoseProtocol
        """
        反序列化pose信息
        :param data:
        :return:
        """
        raise NotImplementedError()


__all__ = ["PoseProtocol", "registerPoseType", "pose_types", "JointProtocol", "registerJointType", "joint_types"]


