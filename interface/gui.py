# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: gui
# Time    : 2024-11-04
# Contact : 906629272@qq.com
"""
UI交互功能封装
"""

from .protocol import JointProtocol, joint_types, PoseProtocol, pose_types


pose_list = [] # type: list[PoseProtocol]
joint_list = [] # type: list[JointProtocol]

def addJoint(joint_type_name):
    # type: (str) -> JointProtocol
    joint_type = _findJointType(joint_type_name)
    joint = joint_type.create()
    joint_list.append(joint)
    return joint

def _findJoint(joint_name):
    # type: (str) -> JointProtocol
    for joint in joint_list:
        if joint.name() == joint_name:
            return joint
    raise LookupError("Joint not found: {}".format(joint_name))

def removeJoint(joint_nane):
    # type: (str) -> None
    joint = _findJoint(joint_nane)
    joint.destroy()
    joint_list.remove(joint)

def _findJointType(joint_type_name):
    # type: (str) -> JointProtocol
    for joint_type in joint_types:
        if joint_type.type_name == joint_type_name:
            return joint_type
    raise LookupError("Joint type not found: {}".format(joint_type_name))

def _findPoseType(pose_type_name):
    # type: (str) -> PoseProtocol
    for pose_type in pose_types:
        if pose_type.type_name == pose_type_name:
            return pose_type
    raise LookupError("Pose type not found: {}".format(pose_type_name))

def addPose(pose_type_name):
    # type: (str) -> PoseProtocol
    pose_type = _findPoseType(pose_type_name)
    pose = pose_type.create()
    pose_list.append(pose)
    return pose

def _findPose(pose_name):
    # type: (str) -> PoseProtocol
    for pose in pose_list:
        if pose.name() == pose_name:
            return pose
    raise LookupError("Pose not found: {}".format(pose_name))

def removePose(pose_nane):
    # type: (set) -> None
    pose = _findPose(pose_nane)
    pose.destroy()
    pose_list.remove(pose)


__all__ = ["addPose", "pose_list", "pose_types", "addJoint", "joint_types", "joint_list", "removePose", "removeJoint"]

