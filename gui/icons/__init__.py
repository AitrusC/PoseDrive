# -*- coding: UTF-8 -*-
# Author  : AitrusC
# FileName: __init__
# Time    : 2024-09-12
# Contact : 906629272@qq.com

import os
from enum import Enum


class IconPath(Enum):
    """
    包含所有图标路径的枚举类
    """
    # 标题栏图标路径
    TITLEBAR_PATH = os.path.join(os.path.dirname(__file__), 'titlebar.png')
    # 删除图标路径
    DELETE_PATH = os.path.join(os.path.dirname(__file__), 'delete.png')
    # 添加图标路径
    PLUS_PATH = os.path.join(os.path.dirname(__file__), 'plus.png')
    # 关节图标路径
    JOINT_PATH = os.path.join(os.path.dirname(__file__), 'joint.png')
    # blendShape图标路径
    BLENDSHAPE_PATH = os.path.join(os.path.dirname(__file__), 'blendShape.png')
    # 上箭头图标路径
    UP_ARROW_PATH = os.path.join(os.path.dirname(__file__), 'up_arrow.png')
    # 下箭头图标路径
    DOWN_ARROW_PATH = os.path.join(os.path.dirname(__file__), 'down_arrow.png')
