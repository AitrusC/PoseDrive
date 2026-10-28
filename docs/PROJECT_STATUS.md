# PoseDrive 项目现状与模块结构

> 快照时间：2026-10-19
> 仓库：`C:\Users\jeff\Documents\maya\scripts\PoseDrive`
> 远端：https://github.com/AitrusC/PoseDrive.git（分支 `master`）
> 用途：重写前的现状盘点，记录"有什么、在哪、什么状态、哪些能留"。

---

## 0. 一句话

一个 Maya 内的**姿态驱动（pose-driven）/ 骨骼 SDK 搭建工具**的 UI 原型。
外壳（无边框窗口 + 自绘控件 + 协议注册）已经成形，**业务层只有测试替身，入口为空，未接 Maya**。

**能跑的部分**：`test_ui.py`（需 PySide2）按代码路径可以启动窗口，左栏能增删假关节、展开假 pose（本机无 PySide2，未实机验证）。
**不能跑的部分**：`main.py` 什么也不做；`showUI()` 是 `pass`；没有任何真实的 Maya 驱动逻辑。

---

## 1. 快照信息

| 项 | 值 |
|---|---|
| 代码量 | 12 个 `.py`，约 2066 行；QSS 51 行 |
| 最大文件 | `gui/widget/widgetT.py`（1310 行，占 63%） |
| 目标环境 | Maya + PySide2 + Python 3.10（见 `.idea/misc.xml`） |
| 本地环境 | Python 3.14，**未安装 PySide2**，因此本机无法直接运行 |
| 最后提交 | `649c993` 2024-10-12 "窗口基本框架1.2（UI设计）" |
| 提交总数 | 9（2024-09-08 ~ 2024-10-12，实际开发约 5 周） |
| 未提交改动 | 约 1700 行新增；`interface/` 两个核心文件**只存在于工作区** |
| 测试 | 无自动化测试，只有 2 个手工脚本 |
| 文档 | `README.md` 仅一行"重写一下"；需求仅有一张设计图 |

---

## 2. 目录结构

```
PoseDrive/
├─ main.py                      # 入口：from gui.ui import showUI; showUI()
├─ __init__.py                  # 包标记，仅 from importlib import reload
├─ README.md                    # 一行："重写一下"
├─ __init__.pyc                 # Python 2 遗留物（未跟踪）
│
├─ gui/
│  ├─ __init__.py               # 空
│  ├─ ui.py                     # 主窗口、左右分栏、UI ↔ interface 桥接
│  ├─ design/
│  │  └─ 图形基础及功能设计.png    # 唯一的需求文档（目标 UI）
│  ├─ icons/
│  │  ├─ __init__.py            # IconPath 枚举（7 个图标路径）
│  │  ├─ titleBar.png           # 已提交
│  │  ├─ plus.png               # ┐
│  │  ├─ delete.png             # │
│  │  ├─ joint.png              # ├ 均未提交（untracked）
│  │  ├─ blendShape.png         # │
│  │  ├─ up_arrow.png           # │
│  │  └─ down_arrow.png         # ┘
│  └─ widget/
│     ├─ __init__.py            # 空
│     ├─ widgetT.py             # 控件库：17 个类/函数，1310 行
│     └─ qss/
│        └─ base.qss            # 全局样式（51 行）
│
├─ interface/
│  ├─ __init__.py               # 空
│  ├─ protocol.py               # JointProtocol / PoseProtocol + 类型注册器
│  └─ gui.py                    # 门面：全局 joint_list / pose_list + CRUD
│
├─ test_ui.py                   # 手工冒烟：假协议实现 + MainWindow 启动
├─ test_script.py               # 网上 CollapsibleBox 示例（参考用，可删）
└─ .idea/                       # PyCharm 配置（未跟踪，含失效的外部路径）
```

---

## 3. 模块总览

| 模块 | 行数 | 角色 | 对外接口 | 状态 |
|---|---:|---|---|---|
| `main.py` | 9 | 入口 | — | ⛔ 空实现（import 时无窗口） |
| `__init__.py` | 10 | 包标记 | `reload` | ⚪ 无实际作用 |
| `gui/ui.py` | 199 | 主窗口与页面 | `MainWindow`, `showUI` | 🟡 布局骨架 |
| `gui/widget/widgetT.py` | 1310 | 控件库 | `FramelessWindow`, `ListWidget` | 🟢 可复用，有缺陷 |
| `gui/widget/qss/base.qss` | 51 | 主题 | — | 🟢 可用（硬编码字体） |
| `gui/icons/__init__.py` | 28 | 资源枚举 | `IconPath` | 🟢 可用（大小写 bug） |
| `interface/protocol.py` | 182 | 抽象层 | 2 个协议 + 2 个注册装饰器 | 🟡 骨架，约束不生效 |
| `interface/gui.py` | 72 | 数据门面 | 4 个 CRUD 函数 + 2 个全局 list | 🟡 可用，无归属关系 |
| `test_ui.py` | 120 | 手工测试 | `show_ui_in_maya()` | 🟡 仅冒烟 |
| `test_script.py` | 122 | 遗留 demo | — | ⚪ 建议删除 |

---

## 4. 模块详解

### 4.1 入口层

**`main.py`（9 行）**

```python
from gui.ui import showUI
showUI()
```

- 绝对导入 `gui.ui`，要求 **PoseDrive 目录本身**在 `sys.path`（Maya 的 scripts 路径满足），但不支持 `import PoseDrive.main`。
- 模块级调用，无 `if __name__ == "__main__"` 守卫。
- `showUI()` 是 `pass` → 实际效果：**导入 PySide2 后立刻退出，不弹窗**。

**`__init__.py`（10 行）**

- 只有 `try: from importlib import reload / except ImportError: pass`，无版本号、无子模块导出。
- 设计意图应是"Maya 内 reload 热更新"，但没有配套的 reload 逻辑。

---

### 4.2 `gui/ui.py` — 主窗口与页面

| 类 | 行 | 职责 | 现状 |
|---|---|---|---|
| `PoseEditWidget` | 19–56 | 右侧 pose 编辑区 | 只有 `QLabel("关节姿态")`、`X:`、`Y:` 和 SHAPE 列表；`pose` 参数**完全未使用** |
| `RightWidget` | 59–94 | 右侧容器 | `setItem(None)` 显示占位文案；`clear()` 假定所有 item 都是 widget |
| `BodyWidget` | 97–175 | 左右分栏 + 业务回调 | **直接读写全局 `joint_list` / `pose_list`**；初始化时 `joint_list[0]` 会 IndexError |
| `MainWindow` | 180–191 | 无边框主窗 | 1080×720 固定初始尺寸，无明显扩展点 |
| `showUI` | 194–199 | 启动函数 | **空函数体 `pass`** |

**尺寸与布局**

- 左栏 `ListWidget` 固定宽 250；右侧 `RightWidget` 扩张。
- 右栏 `main_layout` 设置了 `Qt.AlignCenter`，子控件可能被压成 sizeHint 而不是铺满（需实机确认）。

**业务逻辑（`BodyWidget`）**

| 回调 | 触发 | 行为 |
|---|---|---|
| `addJointAndPose(key)` | 左栏 "+" | `key` 有值 → `addPose("test_pose")`；否则 `addJoint("test_joint")`。类型名写死 |
| `destroyJointAndPose(key)` | 左栏 "−" | `key[1]` → `removePose`；否则 `removeJoint`。不级联、不提示 |
| `setPose(key)` | 点击 pose 行 | 仅 `print`，**没有更新右侧面板**（与设计不符） |

**初始化硬编码**

```python
self.left_widget.jplist_widget.updateItems([... for i in joint_list])
self.left_widget.jplist_widget.updateChildItems(
    joint_list[0].name(), [... for i in pose_list])   # 空列表即崩溃
self.right_widget.setItem(1)                          # 传了个 int
```

---

### 4.3 `gui/widget/widgetT.py` — 控件库

17 个类/函数挤在一个文件里。`__all__` 只导出 `FramelessWindow` 和 `ListWidget`，其余靠模块内互相引用。

| # | 类 / 函数 | 行 | 基类 | 职责 | 备注 |
|---|---|---|---:|---|---|
| 1 | `_setLuminance` | 18–41 | — | RGB→YUV 调亮度 | 手写位运算，非必需 |
| 2 | `_setOpacity` | 44–57 | — | 调 alpha | 正常 |
| 3 | `_TitleBar` | 60–197 | `QWidget` | 自绘标题栏：图标、菜单、搜索、三色圆按钮、拖拽 | 拖拽用全局坐标，嵌 Maya 后可错位 |
| 4 | `FramelessWindow` | 200–337 | `QWidget` | 无边框主窗：QSS 加载、标题栏、边缘缩放 | **缩放逻辑有累计漂移 bug**；边缘被 body 盖住 |
| 5 | `RoundButton` | 340–440 | `QAbstractButton` | 圆形按钮（用 `radius` 当直径） | 无图标、无 tooltip |
| 6 | `IconButton` | 443–530 | `QAbstractButton` | 图标按钮 + 半透明悬停/按下 | 缩放不保持宽高比 |
| 7 | `SearchLine` | 533–548 | `QLineEdit` | 搜索输入框 | 高度写死 20 |
| 8 | `_ToolButton` | 551–585 | `QPushButton` | 折叠组头（可 check） | 自定义 `doubleClicked(bool)`，语义混乱 |
| 9 | `_CollapsibleBox` | 588–720 | `QWidget` | 折叠分组 + 高度动画 | 只有双击才动；`content_area.destroy()` 有风险 |
| 10 | `_ListItemWidget` | 723–816 | `QWidget` | 自绘列表行（25px） | 无选中态、无省略号 |
| 11 | `_EButtonGroup` | 819–860 | `QButtonGroup` | 可取消选中的互斥组 | 与 Qt 自身 check 状态双轨 |
| 12 | `_JPlistWidget` | 863–929 | `QScrollArea` | 关节 + 姿势树 | 按显示文本找组，重名/改名即错 |
| 13 | `_ShapeListWidget` | 932–981 | `QScrollArea` | 扁平列表（pose / 搜索结果） | 复用度高 |
| 14 | `ListWidget` | 984–1093 | `QWidget` | 左栏组合面板（标题 + 加/删 + 搜索 + 列表） | 两套 mode 混在一个类里 |
| 15 | `_MenuWidget` | 1096–1107 | `QMenu` | 空壳 | 只为了套 QSS |
| 16 | `MenuButton` | 1109–1170 | `QAbstractButton` | 菜单按钮 | 每次点击重建 QMenu |
| 17 | `SearchFunctionWidget` | 1173–1215 | `SearchLine` | 全局搜索入口 | 数据写死 10 条 |
| 18 | `SearchFunctionWindow` | 1218–1293 | `QWidget` | 搜索弹窗 | `focusChanged` 重复连接 |

> 表内 18 项（含 2 个工具函数）。

**内部依赖关系**

```
FramelessWindow ──> _TitleBar ──> RoundButton / MenuButton / SearchFunctionWidget
        │                              └──> _MenuWidget
        └──> ListWidget ──> _JPlistWidget ──> _CollapsibleBox ──> _ToolButton
                        │                              └──> _ListItemWidget
                        └──> _ShapeListWidget ──> _ListItemWidget
                        └──> _EButtonGroup
```

**已确认的缺陷（重写前必须处理）**

1. `_CollapsibleBox` 只在 `doubleClicked` 时播放动画，单击只改 QSS 颜色（`widgetT.py:613`、`648-656`）。
2. 动画方向取自 `_double_click` 布尔标记，不是按钮的 `checked`（`widgetT.py:568-577`）。
3. `content_area.destroy()` 调的是 Qt 原生窗口销毁 API，不是清布局（`widgetT.py:665`）。
4. 列表刷新用 `deleteLater` 后立刻重建，旧控件仍占布局，按文本匹配会命中旧项（`widgetT.py:714-720`、`926-929`）。
5. 缩放：left/top 每次都用"相对按下点的总位移"叠加当前坐标 → 漂移（`widgetT.py:324-334`）。
6. 边缘检测用 `geometry()`（父坐标）比 `globalPos()`（全局坐标），有 parent 时失效（`widgetT.py:251-261`）。
7. `installEventFilter(self)` 没有对应 `eventFilter()`，空操作（`widgetT.py:228`）。
8. QSS 路径用字符串拼接 `__file__ + "/../qss/base.qss"`（`widgetT.py:215`）。

---

### 4.4 资源与样式

**`gui/icons/__init__.py`**

- `IconPath(Enum)`，7 个路径：`titleBar / delete / plus / joint / blendShape / up_arrow / down_arrow`。
- 问题：枚举里写 `titlebar.png`，实际文件是 `titleBar.png` → **大小写敏感系统（Linux/Mac Maya）上取不到图标**。
- `up_arrow.png` / `down_arrow.png` 已准备但**代码里从未使用**（折叠箭头本应使用它们）。

**`gui/widget/qss/base.qss`**

- 全局 `QWidget { background: transparent; font: bold 10pt "Microsoft YaHei"; color: ... }`。
- 针对 `SearchLine`、`_JPlistWidget`、`_ShapeListWidget`、`_ToolButton`、`_MenuWidget` 的样式。
- 问题：字体写死 Windows 字体；颜色与 `paintEvent` 里的硬编码色值（`QColor(48,55,52)`、`55,62,59`、`69,76,73` 等）两套并存。

---

### 4.5 `interface/protocol.py` — 协议层

**注册器**

```python
pose_types = []
joint_types = []
registerPoseType(cls)   # 装饰器，append 后原样返回
registerJointType(cls)
```

- 模块级可变列表；无重复检测、无 `type_name` 校验、无注销。

**`JointProtocol`（27–96）**

| 成员 | 类型 | 说明 |
|---|---|---|
| `type_name` | 类属性 `"unimplemented"` | 注册与查找的键 |
| `icon_path` | 类属性 | UI 图标 |
| `create()` | `@classmethod` | 工厂 |
| `destroy()` | `@abstractmethod` | 销毁 |
| `name()` | `@abstractmethod` | 名称 |
| `info()` | `@abstractmethod` | 文本信息 |
| `view()` | `@abstractmethod` | 返回 `QWidget` |
| `dump()` | `@abstractmethod` | 序列化 |
| `load(data)` | `@abstractmethod` | 反序列化 |

**`PoseProtocol`（99–177）**

同上，额外多一个 `driveAttribute()`（"获取驱动属性，用于驱动其他属性"），是"pose 驱动骨骼/blendShape"这一核心能力的抽象入口。

**问题**

- 继承 `object` 而非 `ABCMeta`，`@abstractmethod` **不生效**，漏实现不会报错。
- `create` 是类方法，`load` 在测试实现里一处当类方法、一处当实例方法，契约不一致。
- 为了一行类型注释 `from PySide2.QtWidgets import QWidget`，核心层被 Qt 绑死，无法 headless 单测。
- `info/view/dump/load/driveAttribute` 在全项目**没有任何调用点**。

---

### 4.6 `interface/gui.py` — 数据门面

**公开接口**

| 名称 | 签名 | 说明 |
|---|---|---|
| `pose_list` | `list[PoseProtocol]` | 全局 pose 表 |
| `joint_list` | `list[JointProtocol]` | 全局 joint 表 |
| `addJoint(type_name)` | → `JointProtocol` | 按类型名创建并 append |
| `removeJoint(name)` | → `None` | 按名称查找、`destroy`、移除 |
| `addPose(type_name)` | → `PoseProtocol` | 同上 |
| `removePose(name)` | → `None` | 同上 |

内部还有 `_findJoint / _findPose / _findJointType / _findPoseType`。

**关键设计缺口**

```
joint_list ──┐
             ├── 两个互不相关的全局列表
pose_list  ──┘
```

- **Joint 与 Pose 之间没有归属关系**：`addPose` 不接收 joint，UI 只能把整个 `pose_list` 渲染给当前关节。
- 用 `name()` 做主键：可重名、改名断链。
- 删除关节不级联删除其 pose → 悬空对象。
- 没有文档/工程对象、没有保存/加载、没有变更通知（全靠 UI 手动刷新）。
- 异常直接 `LookupError` 抛出，没有面向用户的错误处理。

---

### 4.7 测试与遗留脚本

**`test_ui.py`（120 行）**

- `TestJointProtocol` / `TestPoseProtocol`：用 `uuid4().hex[:8]` 当名字的假实现，`destroy/info/driveAttribute` 空转。
- `get_host_app()`：从 `QApplication.activeWindow()` 向上爬 `.parent()` 猜 Maya 主窗（不可靠）。
- `ShowUIInMaya.__init__(self, parent=get_host_app())`：默认参数在**导入时**求值。
- 模块级往 `joint_list` 塞 3 个假关节、`pose_list` 塞 1 个假 pose —— 这是 `BodyWidget` 不崩的唯一原因。
- `if __name__ == "__main__"` 时正常启动 QApplication。

**`test_script.py`（122 行）**

- 网上流传的 `CollapsibleBox` 示例，`_CollapsibleBox` 的原型。与项目无关，可删。
- 但它用的 `lay = self.content_area.layout(); del lay` 比现在的 `destroy()` 更安全，说明现在的写法是退化。

---

### 4.8 其它

- **`.idea/`**：`PoseDrive.iml` 引用了 `../../2024/devkitBase/.../pymel/.../pyi`（**路径已不存在**），并 exclude 了一个不存在的 `V1` 目录。
- **`gui/design/图形基础及功能设计.png`**：唯一的需求描述，包含五个区域与旧版工具截图。

---

## 5. 对象图与数据流

### 5.1 控件树

```
MainWindow (FramelessWindow)
└─ QVBoxLayout
   ├─ _TitleBar
   │  ├─ icon QLabel
   │  ├─ MenuButton ×3（文件/工具/帮助）
   │  ├─ SearchFunctionWidget
   │  └─ RoundButton ×3（min/max/close）
   └─ BodyWidget
      └─ QHBoxLayout
         ├─ ListWidget（固定 250）
         │  ├─ 标题行（QLabel + IconButton 加/删）
         │  ├─ SearchLine
         │  └─ _JPlistWidget（或 _ShapeListWidget）
         │     └─ _CollapsibleBox ×N
         │        ├─ _ToolButton（关节名）
         │        └─ QScrollArea → _ListItemWidget ×M（pose）
         └─ RightWidget
            └─ PoseEditWidget（占位）或 QLabel（"请选择一个关节姿态"）
```

### 5.2 信号表

| 发出者 | 信号 | 载荷 | 接收者 | 结果 |
|---|---|---|---|---|
| `_TitleBar` | `windowMoved` | `QPoint` | `FramelessWindow.move` | 拖拽移动 |
| `_ListItemWidget` | `clicked` | — | `_CollapsibleBox.item_clicked` | 转成 `key` |
| `_CollapsibleBox` | `item_clicked` | `str` | `_JPlistWidget.item_clicked` | 包成 `[joint, pose]` |
| `_JPlistWidget` | `joint_pressed` | `str` | `ListWidget._setNowJointKey` | 记录当前关节 |
| `_JPlistWidget` | `item_clicked` | `list` | `ListWidget` / `BodyWidget` | 记录子项 + `setPose` |
| `_JPlistWidget` | `item_clicked` | `list` | `BodyWidget.setPose` | **仅 print** |
| `_ShapeListWidget` | `on_pressed` | `str` | `ListWidget` | 记录当前项 |
| `ListWidget` | `add_joint_click` | `str\|None` | `BodyWidget.addJointAndPose` | 加关节或加 pose |
| `ListWidget` | `delete_joint_click` | `list` | `BodyWidget.destroyJointAndPose` | 删关节或删 pose |
| `ListWidget` | `on_pressed` / `add_click` / `delete_click` | — | 仅 `addShapeList` 模式内部 | 右侧 SHAPE 列表用（未接业务） |
| `SearchFunctionWindow` | `selected` | `str` | 无 | 无人监听 |
| `_ToolButton` | `doubleClicked` | `bool` | `_CollapsibleBox.on_pressed` | 展开/收起 |

### 5.3 关键交互链

**添加**

```
"+" 点击
 → ListWidget.add_joint_click(当前关节名 or None)
 → BodyWidget.addJointAndPose
    ├─ 有选中关节：addPose("test_pose") → updateChildItems(该关节, 全部 pose)
    └─ 无选中关节：addJoint("test_joint") → updateItems(全部关节)
```

**删除**

```
"−" 点击
 → ListWidget._sendDeleteJointSignal
 → delete_joint_click([joint, pose])
 → BodyWidget.destroyJointAndPose
    ├─ pose 存在：removePose(pose) → 刷新该关节子项
    └─ 否则：removeJoint(joint) → 刷新关节列表
```

**选中**

```
点击 pose 行
 → item_clicked([joint, pose])
 → ListWidget._setNowJointChildKey + BodyWidget.setPose
 → print("setPose", ...)   # 右侧面板未更新
```

---

## 6. 功能状态矩阵（对照设计图）

| # | 功能 | 设计图要求 | 代码现状 | 状态 |
|---|---|---|---:|---|
| 1 | 无边框窗口 / 标题栏 / 拖拽 | ✓ | `FramelessWindow` + `_TitleBar` | 🟢 可用（缩放有 bug） |
| 2 | 左栏关节列表 | ✓ | `_JPlistWidget` + `_CollapsibleBox` | 🟡 结构在，数据假 |
| 3 | 关节展开显示 pose | ✓ | `updateChildItems` | 🟡 所有关节共用全局 pose |
| 4 | 添加/删除关节、pose | ✓ | "+"/"−" | 🟡 无命名、类型写死 |
| 5 | 左栏搜索姿势 | ✓ | `SearchLine` | 🔴 无过滤逻辑 |
| 6 | 全局搜索弹窗 | ✓ | `SearchFunctionWindow` | 🟡 框架在，数据硬编码 |
| 7 | 菜单栏 | ✓ | `MenuButton` ×3 | 🟡 假菜单（print 回调） |
| 8 | 中间 2D 旋转编辑器 | ✓ | — | 🔴 未实现 |
| 9 | 右侧旋转属性 + 驱动类型 | ✓ | 占位 QLabel | 🔴 未实现 |
| 10 | 底部 blendShape / 骨骼关联 | ✓ | — | 🔴 未实现 |
| 11 | 网格编辑开关 | ✓ | — | 🔴 未实现 |
| 12 | 数据保存 / 加载 | 隐含 | 只有未调用的 `dump/load` | 🔴 未实现 |
| 13 | Maya 实际驱动 | 核心 | — | 🔴 未实现 |
| 14 | 撤销 / 重做 | 隐含 | — | 🔴 未实现 |
| 15 | 镜像（R→L / L→R） | 旧版有 | — | 🔴 未实现 |

**估算完成度**：UI 外壳约 60%，整项目约 15%。

---

## 7. 仓库状态（重写前必须清理）

| 类别 | 内容 |
|---|---|
| 已跟踪垃圾 | `gui/Icon/__pycache__/__init__.cpython-310.pyc`、`gui/widget/__pycache__/__init__.cpython-310.pyc`、`gui/widget/__pycache__/titleBar.cpython-310.pyc` |
| 已跟踪但工作区已删 | `gui/widget/titleBar.py`（140 行，已并入 `widgetT.py`）、`gui/Icon/__init__.py` |
| 未跟踪 | `.idea/`、`__init__.pyc`、全部 `__pycache__/`、**6/7 张图标** |
| 半途的改名 | `gui/Icon` → `gui/icons` 只 staged 了一半（`RM` 状态） |
| 缺失 | `.gitignore`、`requirements.txt`、`LICENSE`、README 内容、测试配置、Maya 模块文件（`.mod`）、货架脚本 |
| 提交风险 | `interface/protocol.py`、`interface/gui.py` 与 widgetT 的大改**尚未提交**，一次误操作就会丢 |

**结论**：先把工作区提交/打 tag 存档，再开始重写；不要在新分支上直接删旧代码。

---

## 8. 重写取舍

### 8.1 可以直接留（清理后移植）

- `FramelessWindow` / `_TitleBar` 的**整体思路**（自绘标题栏、拖拽、三色按钮）。
- `RoundButton`、`IconButton`、`_ListItemWidget`、`_EButtonGroup` 的绘制与状态机。
- `_CollapsibleBox` 的动画方案（改用单击 + `checked` 驱动）。
- `base.qss` 的配色体系（抽成常量/QSS 变量）。
- `interfaces/protocol.py` 的**类型注册**思路 —— 保留概念，重写实现。
- 设计图作为唯一验收标准。

### 8.2 必须重写

| 旧 | 新 |
|---|---|
| `interface/gui.py` 全局 list | `core.Project` 对象：`Joint` 持有 `poses`，UUID 主键，信号通知 |
| `_JPlistWidget` 手搭控件 | `QAbstractItemModel` + `QTreeView` + delegate |
| `FramelessWindow` 自写缩放 | `windowHandle().startSystemMove()/startSystemResize()` |
| `ListWidget` 双模式 | 拆成 `JointTreePanel` 与 `ShapeListPanel` |
| `SearchFunctionWindow` 假数据 | `QSortFilterProxyModel` + 真实命令索引 |
| `get_host_app()` | `maya.OpenMayaUI.MQtUtil.mainWindow()` + `shiboken2.wrapInstance` |
| `dump/load` 空声明 | JSON + schema 版本号 + 自动保存 |
| 写死的 `test_*` | 真实注册的类型；UI 不再依赖测试数据 |

### 8.3 建议删除

- `test_script.py`（第三方 demo）。
- `gui/widget/titleBar.py` 的残留索引、所有 `__pycache__`、根目录 `__init__.pyc`。
- `_MenuWidget`（空壳）、`MenuButton` 里的假选项、5 处调试 `print`。
- 注释掉的大段代码（`widgetT.py` 中约 40 行）。
- Python 2 风格 `# type:` 注释 → 改为 PEP 484 注解。

### 8.4 建议的新结构

```
PoseDrive/
├─ main.py                 # 入口，带 __main__ 守卫
├─ compat/qt.py            # PySide6 → PySide2 兼容层（为 Maya 2025 留路）
├─ core/                   # 纯 Python，不 import Qt
│  ├─ model.py             # Joint / Pose / DriverBinding
│  ├─ project.py           # Project 聚合 + 信号
│  ├─ registry.py          # TypeRegistry
│  ├─ serializer.py        # JSON + 版本迁移
│  └─ commands.py          # 可撤销命令
├─ maya/
│  ├─ host.py              # MQtUtil / shiboken 集成、窗口生命周期
│  └─ rig.py               # 约束 / SDK / blendShape 实际写入
├─ gui/
│  ├─ window.py            # 无边框主窗
│  ├─ panels/              # joint_tree / shape_list / rotation_editor / driver_panel
│  ├─ models/              # QAbstractItemModel
│  ├─ widgets/             # 从 widgetT.py 拆出的基础控件
│  └─ qss/
└─ tests/
```

### 8.5 迁移顺序（建议）

1. **存档**：提交当前工作区，打 `v0.1-prototype` tag。
2. **清仓库**：`.gitignore`、删 pyc、删 `test_script.py`、补 README。
3. **立骨架**：`compat/qt.py`、`core/model.py`、`maya/host.py`、可运行的 `showUI()`。
4. **换列表**：`QAbstractItemModel` + `QTreeView`，把关节/pose 的增删接上真实模型。
5. **补核心**：2D 旋转编辑 → 驱动绑定 → `maya/rig.py` 落盘。
6. **工程化**：pytest + `pytest-qt`（offscreen）、JSON 读写、撤销栈、打包 `.mod`。

---

## 9. 重写前需要定的事

1. **目标 Maya 版本**：2020–2024 用 PySide2，2025 用 PySide6 —— 决定 `compat/qt.py` 的取舍。
2. **窗口形态**：独立浮动窗（当前做法）还是可停靠面板（`workspaceControl`）？
3. **数据归属**：pose 是"关节的属性"还是"独立资源可复用"？这决定 `core/model.py` 是树还是图。
4. **驱动落盘方式**：`setDrivenKeyframe`（SDK）、约束、还是自定义节点？决定 `maya/rig.py` 的接口。
5. **旧版 V1 代码是否还在**：设计图右侧的旧工具若可找到，可直接复用其骨骼/Locator/SDK 逻辑。
6. **是否需要多语言**：当前全中文硬编码，若只面向个人可不管。

---

## 附：已知但未在上文展开的问题

- 本地 Python 3.14 + 无 PySide2，无法在本机运行/截图验证；所有结论均来自源码静态分析与 Git 状态。
- 窗口缩放、坐标换算类问题需在 Maya 实机确认具体表现。
- `gui/ui.py` 中 `RightWidget` 的 `AlignCenter` 是否导致子面板不铺满，需实机确认。
