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
