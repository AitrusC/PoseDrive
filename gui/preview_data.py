# -*- coding: utf-8 -*-
"""UI 预览数据；不访问 Maya，也不调用业务对象的 create/destroy。"""
import uuid


class JointPosePreviewData(object):
    """测试对象只需提供 name() 和 icon_path，工厂由 test_ui 注入。"""

    def __init__(self, joint_factory=None, pose_factory=None):
        self.joints = {}
        self.joint_factory = joint_factory
        self.pose_factory = pose_factory

    def addJoint(self, item=None):
        if item is None:
            if self.joint_factory is None:
                return None
            item = self.joint_factory()
        key = uuid.uuid4().hex
        self.joints[key] = {"item": item, "poses": {}}
        return key

    def addPose(self, joint_key, item=None):
        joint = self.joints.get(joint_key)
        if joint is None:
            return None
        if item is None:
            if self.pose_factory is None:
                return None
            item = self.pose_factory()
        key = uuid.uuid4().hex
        joint["poses"][key] = item
        return key

    def remove(self, joint_key, pose_key=None):
        joint = self.joints.get(joint_key)
        if joint is None:
            return
        if pose_key is None:
            del self.joints[joint_key]
        else:
            joint["poses"].pop(pose_key, None)

    def pose(self, joint_key, pose_key):
        joint = self.joints.get(joint_key)
        return joint["poses"].get(pose_key) if joint else None

    def jointRows(self):
        return [(key, group["item"].name(), group["item"].icon_path)
                for key, group in self.joints.items()]

    def poseRows(self, joint_key):
        return [(key, item.name(), item.icon_path)
                for key, item in self.joints[joint_key]["poses"].items()]
