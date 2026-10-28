# PoseDrive 项目分析

> 分析时间：2026-10-21
> 最近复核：2026-10-28（`40a80e9「重启」` 已提交全部工作区代码；源码自上次分析未变，实测结论继续有效）
> 分析对象：工作区 `C:\Users\jeff\Documents\maya\scripts\PoseDrive`
> 范围说明：本项目为**全新项目**，不复用 V1（`UVDriveJoint`，2023）的代码或逻辑；V1 只作为设计图右侧旧截图的出处，不参与架构决策。
> 验证环境：Maya 2022 mayapy（Python 3.7.7 / PySide2 5.15.2 / Qt 5.15.2），离屏跑通 UI
> 说明：本文结论分两类 —— **[实测]** 表示用 mayapy 真正把代码跑起来观察到的行为；**[源码]** 表示静态阅读得出，未运行验证。

---

## 0. 结论速览

**这是一个"有壳无核"的新项目。**

当前工作区只完成了 UI 外壳：

| 维度 | 现状 |
|---|---|
| 视觉外壳 | 🟡 约 60%：无边框窗、自绘按钮、折叠列表、搜索窗、假菜单 |
| 数据模型 | 🔴 0：两个全局 list，无归属、无主键、无通知、无持久化 |
| Maya 业务 | 🔴 0：全项目 0 处 `maya.cmds` / `OpenMaya` 调用 |
| 入口 | 🔴 `showUI()` 是 `pass`，能用的入口藏在 `test_ui.py` 里 |
| 测试 / 工程化 | 🔴 0：无测试、无 `.gitignore`、`__pycache__` 已入库 |
| 整体 | **约 12%** |

用 Maya 2022 的 `mayapy` 实跑，窗口能起来，但 §3 的 14 条问题里有 4 条是阻断级：空数据首次运行 `IndexError`、折叠面板动画从未初始化、刷新关节列表后姿态全部丢失、窗口边缘无法缩放。

**存档风险已解除，但仓库卫生没收尾**：2026-10-26 的 `40a80e9「重启」` 把 1828 行改动全部提交了（含整个 `interface/` 层），代码不会再丢；但至今没有 `.gitignore`，`docs/`、6 张图标仍未跟踪，`__pycache__/*.pyc` 仍在索引里（见 §3.3）。

**建议路线**：保留视觉外壳，换掉列表与数据层，业务层从零设计，分 4 步走（见 §7）。

---

## 1. 这个项目想做什么（从设计图反推）

### 1.1 产品定义

这是一个 Maya 内的**姿态驱动 / 骨骼修型工具**：给骨架的每个关节定义若干"姿态"，每个姿态带一个二维坐标和一组驱动绑定，关节运动时由驱动（SDK 等）带出形变。

领域概念可以归纳成 5 个：

| 概念 | 含义 |
|---|---|
| Joint | 关节 / 骨骼，pose 的宿主 |
| Pose | 姿态：二维坐标 + 名称 + 图标 |
| Driver | 驱动绑定：把 pose 映射到目标属性（blendShape 权重 / 骨骼变换 / 控制器偏移） |
| Mirror | 左右镜像 |
| Project | 工程，序列化单元 |

`interface/protocol.py` 里已经有 Joint / Pose 两个协议和注册器，说明原设计想支持"可注册的关节 / 姿态类型"。这个方向可以保留，但当前实现没有约束力（§4.2）。

> 设计图右侧是旧工具截图，只作为**功能清单**参考；其具体实现（ADV 专用节点结构、场景名当数据库、Py2 代码）本项目不复用，见 §6.3。

### 1.2 设计图的五个区域（`gui/design/图形基础及功能设计.png`，2560×1440）

| 区域 | 内容 | 语义 |
|---|---|---|
| 顶部 | 菜单栏、全局搜索、加/删图标、左栏搜索 | 工程与命令入口 |
| 左栏 | 骨骼名称列表，展开显示该骨骼的姿态；上方"添加/删除骨骼姿势"；搜索姿势 | Joint → Pose 树 |
| 中部 | "显示当前所选姿势的旋转二维平面图" + 一个"网格编辑"滑动开关 | **核心交互**：2D 姿态编辑器 |
| 右上 | "显示所选姿势的旋转属性，以及驱动类型" | Pose 的属性面板 |
| 底部 | "该区域显示右侧所选骨骼或所选姿势所连接的 blendShape 或骨骼"，带添加/删除 | 驱动目标绑定 |

右侧贴的是 V1 老面板截图，按钮依次为：创建骨骼（含 Wrist/Elbow/Shoulder/Ankle/Knee/Hip/Finger 与 ALL）、创建定位的 Locator、添加额外的 Locator、加载驱动骨骼（+Y/−Y/+Z/−Z 方向）、选择骨骼点击创建、选择 Locator 点击添加属性、单个骨骼约束、镜像 Locator R>>L、构建驱动、构建驱动系统、单个关节添加驱动属性（添加/移除）、加载驱动属性调整 SDK、选择控制器点击调整 SDK/移除 SDK、镜像 SDK R>>L / L>>R、选择驱动的骨骼。

旧截图里的按钮按"能力"读，例如：创建骨骼 / 定位 locator、构建驱动、单个骨骼约束、镜像 locator 与镜像 SDK、调整与移除 SDK、选择驱动骨骼。这些是**需求候选项**，每一项都要在本项目里重新定义接口与行为，不能从截图推断实现。

当前 UI 现状：只有 Joint / Pose 两个概念的**空壳**；Driver、Mirror、Project 完全没有。

---

## 2. 代码现状

### 2.1 规模

| 文件 | 行数 | 角色 | 状态 |
|---|---:|---|---|
| `gui/widget/widgetT.py` | 1317 | 控件库（18 个类/函数） | 🟡 能画，有 6 处结构性问题 |
| `gui/ui.py` | 200 | 主窗口、左右分栏、业务回调 | 🟡 布局骨架，业务是假的 |
| `interface/protocol.py` | 182 | Joint/Pose 协议 + 注册器 | 🔴 契约不生效，无调用点 |
| `test_ui.py` | 162 | 手工冒烟 + **真正的入口** `show_ui_in_maya` | 🟡 假数据夹在入口里 |
| `test_script.py` | 130 | 第三方 CollapsibleBox 示例 | ⚪ 可删 |
| `interface/gui.py` | 72 | 全局 list + 4 个 CRUD | 🔴 无归属关系 |
| `__init__.py` | 31 | 包入口 | 🟡 转调 test_ui |
| `gui/icons/__init__.py` | 28 | 图标路径枚举 | 🟡 大小写 bug |
| `main.py` | 9 | 入口 | 🔴 什么都不做 |
| 其它 3 个 `__init__.py` | 15 | 空 | ⚪ |

合计 **2146 行**，其中 `widgetT.py` 占 61%。QSS 48 行。

### 2.2 三个决定性事实

1. **没有一行 Maya 逻辑**。`grep` 全项目：只有 `test_ui.py:102` 用 `OpenMayaUI` 取主窗口，其余 0 处 `maya.cmds`、`OpenMaya`、`setDrivenKeyframe`、`blendShape`、`pymel`。也就是说这个项目目前只是"长得像 Maya 工具"的 Qt 界面。
2. **入口是空的**。`gui/ui.py:195` 的 `showUI()` 函数体是 `pass`；`main.py` 调它，所以 `python main.py` 只会 import 完就退出。真正能用的是 `PoseDrive.show_ui_in_maya()`，而它定义在 `test_ui.py` 里 —— **生产入口藏在测试文件里**，且 import 时会往全局列表塞 3 个假关节 + 1 个假姿态（[实测] import 后 `joint_list=3, pose_list=1`）。
3. **没有测试、没有 `.gitignore`、没有 `requirements.txt`**，且 `__pycache__/*.pyc` 已被 git 跟踪。

### 2.3 图形入口与运行方式

- Maya 2022 的 `Documents/maya/scripts/userSetup.py` 里把 `Documents/maya/scripts` 加进了 `sys.path`，所以脚本编辑器里 `import PoseDrive` 可用（[实测] 等价路径 import 成功）。
- 正确启动方式应写成：`import PoseDrive; PoseDrive.show_ui_in_maya()`。

---

## 3. 实测发现的问题

用 Maya 2022 的 `mayapy`（PySide2 5.15.2，`QT_QPA_PLATFORM=offscreen`）构造 `MainWindow`、用 `QTest` 模拟点击，逐条验证。以下都是真实运行结果，不是猜测。

### 3.1 阻断级：现在这个 UI 不能当产品用

**① 首次运行必崩。**
`BodyWidget.__init__` 无条件访问 `joint_list[0]`（`gui/ui.py:119`）。空数据下：

```
[实测] BodyWidget with empty data -> RAISED IndexError: list index out of range
```

现在不崩，纯粹因为 `test_ui.py:152-156` 在 import 时塞了假数据。去掉测试数据即崩。

**② 折叠面板的动画从未初始化。**
`_CollapsibleBox` 的高度动画值只在 `setContentLayout()` 里设置，而 `_JPlistWidget.updateItems`（建关节列表时）只 `addJointItem()`，**不调用** `setContentLayout`。结果是：除第一个被 `updateChildItems` 碰过的面板外，其它关节双击后毫无反应。stderr 直接报：

```
QPropertyAnimation::updateState (minimumHeight, _CollapsibleBox, ): starting an animation without end value
QPropertyAnimation::updateState (maximumHeight, _CollapsibleBox, ): starting an animation without end value
```

[实测] 动画状态始终 `Stopped`，`content_area.maximumHeight()` 始终 0。

**③ 刷新关节列表 = 丢掉所有姿态。**
`_JPlistWidget.updateItems` 会销毁并重建全部 `_CollapsibleBox`，但新面板是空的，不会重新填充子项。而 `BodyWidget.addJointAndPose` 的"添加关节"分支正是走这条路。所以**加一个关节，其它关节下已显示的所有姿态全部消失**。

```
[实测] boxes before refresh: 3
[实测] immediately after refresh: 6      # 旧的还在，新的已建
[实测] after flush(DeferredDelete): 3    # 旧的才真正消失，但子项没了
[实测] 刷新后第一个面板的 pose items: 0
```

**④ 窗口边缘不能缩放。**
`FramelessWindow` 在 `mousePressEvent` 里做边缘命中（`widgetT.py:266-286`），但布局 0 边距，`BodyWidget` 铺满了整个客户区。命中测试：

```
[实测] point (2,300)      -> child: BodyWidget
[实测] point (1078,400)   -> child: BodyWidget
[实测] point (400,718)    -> child: BodyWidget
```

鼠标事件全部落在子控件上，`FramelessWindow` 永远收不到，缩放逻辑和边缘光标形同虚设。同理，标题栏里 `(400,15)` 命中的是 `SearchFunctionWidget` —— 点那里是打开搜索，不是拖窗。

### 3.2 功能级：语义错、交互断

**⑤ 点姿态，右侧面板不动。**
`BodyWidget.setPose` 只有一句 `print("setPose", key)`（`gui/ui.py:155`）。

```
[实测] setPose ['7722a815', 'e8942947']
[实测] right panel labels: ['请选择一个关节姿态', 'Y:', '关节姿态', 'X:', 'SHAPE列表']   # 前后完全一样
```

而且右侧同时存在"请选择一个关节姿态"占位文案和 `PoseEditWidget` —— 因为 `BodyWidget.__init__` 里 `self.right_widget.setItem(1)` 传了个 `int` 当 pose（`gui/ui.py:126`），`if pose:` 成立就渲染了编辑面板。

**⑥ "−" 按钮删的到底是关节还是姿态，取决于看不见的选中态。**
`ListWidget._sendDeleteJointSignal` 把 `[当前关节, 当前姿态]` 发给 `BodyWidget.destroyJointAndPose`，后者用 `if key[1]` 判断。只要用户没点过姿态行，`key[1]` 就是 `None` → 走删关节分支：

```
[实测] 选关节 → [+] 加姿态（poses 1→2）
[实测] 直接点 [−] → 打印 "removeChildPose"，实际删掉的是关节，poses 仍然是 2
```

**⑦ 删关节不级联，姿态变悬空对象。**
`interface/gui.py:30 removeJoint` 只 `destroy()` 关节本身。`pose_list` 是全局的，姿态不知道自己属于谁：

```
[实测] removed '0aefe282'; poses 2 -> 2
```

**⑧ 同一个姿态会同时显示在多个关节下。**
因为 UI 每次渲染子项都直接喂整个 `pose_list`（`gui/ui.py:138-141`）：

```
[实测] joint0 poses: ['3df5a74b']
[实测] joint1 poses: []            # 初始只给第一个关节填了
[实测] 在 joint1 上点 [+] 后: ['3df5a74b', 'db3a0ece']   # joint0 的姿态跑到 joint1 底下了
```

**⑨ 搜索、菜单、全局搜索都是摆设。**
`left.search_line` 的 `textChanged` 信号连接数为 0（[实测]），输入 `zzz` 列表毫无变化；标题栏"文件/工具/帮助"三个菜单项是 `Option1/2/3` 的 `print`；全局搜索硬编码 10 条假数据（`widgetT.py:1208-1219`）。

**⑩ 右侧 `clear()` 是延迟生效的，新旧控件会并存。**
`RightWidget.clear()` 用 `deleteLater()`，在同一轮事件循环内旧控件仍在布局里：

```
[实测] after setItem(None): 占位 label = 2，PoseEditWidget = 1
[实测] after flush:         占位 label = 1，PoseEditWidget = 0
```

**⑪ 列表重建期间旧控件仍在布局里，而代码用显示文本当主键。**
`_CollapsibleBox.updateItems` 先 `deleteLater` 再 `addItem`，实测 `item_layout.count()` 在刷新后是 `3`（1 旧 + 2 新），不是 2；`_JPlistWidget.updateChildItems` 又是按 `toggle_button.text()` 找面板（`widgetT.py:934-937`）。重名、改名、或刷新时序一错，就会改到"即将被销毁"的那个控件上，动画高度也按含旧项的值计算。

### 3.3 工程质量

**⑫ "协议"约束不生效。**
`JointProtocol` 继承 `object` 而不是 `abc.ABC`，`@abstractmethod` 形同注释：

```
[实测] subclass without any method instantiated -> <Incomplete object>, type_name = unimplemented
[实测] JointProtocol.__abstractmethods__ present: False
```

而且 `protocol.py` 为了一个返回值类型注解开 `from PySide2.QtWidgets import QWidget`，核心层被 Qt 绑死，无法 headless 测试。

**⑬ 存档已完成，卫生没收尾。**
2026-10-26 的 `40a80e9「重启」` 一次性提交了 13 个文件、1828 行新增 / 457 行删除，`interface/` 两个核心文件与 +1188 行的 `widgetT.py` 都进了版本库 —— **最大的丢失风险已经解除**。

剩下的问题：`git status` 仍有 26 项，其中 `gui/widget/__pycache__/*.pyc` 处于已暂存状态（`A`/`AM`），下次 `git add -A` 会把 pyc 一起提交；`docs/`、`.idea/`、6 张图标仍未跟踪；没有 `.gitignore`。

**⑭ 其它卫生问题**

- `gui/widget/__pycache__/*.pyc` 已被 git 跟踪；根目录有 `__init__.pyc`；没有 `.gitignore`。
- `gui/icons/__init__.py:16` 写 `titlebar.png`，实际文件是 `titleBar.png` —— Windows 上碰巧能跑，macOS/Linux 的 Maya 上图标丢失。
- `base.qss` 把字体写死 `"Microsoft YaHei"`，同时 `paintEvent` 里又硬编码了一套颜色，两套主题并存。
- 9 处调试 `print`（含 `widgetT.py:1308` 的 `__main__` 测试块）。
- 图标 `up_arrow.png`/`down_arrow.png` 从未被使用。
- `gui/ui.py` 的 import 列表里有 `pose_types`/`joint_types` 等 4 个从未使用的名字。

### 3.4 旧文档需要修正的地方

`docs/PROJECT_STATUS.md`（2026-10-19）整体仍有参考价值，但下面几条已被后续改动修复或过时：

| 旧结论 | 现状 |
|---|---|
| "缩放逻辑有累计漂移 bug" | 已改为锚点法 `_fallback_resize`（`widgetT.py:315-331`），并有 `startSystemResize` 优先分支；漂移问题已修 |
| "`installEventFilter(self)` 没有 eventFilter" | 代码里已不存在 |
| "`get_host_app()` 不可靠" | 已改为 `MQtUtil.mainWindow()` + `shiboken2.wrapInstance` |
| "`ShowUIInMaya(parent=get_host_app())` 默认值导入时求值" | 已改为 `parent=None` 再在函数内求值 |
| "widgetT 1310 行" | 现 1317 行 |

同时它漏掉了我这次实测出来的 6 个更严重的问题（①②③④⑤⑥⑦⑧⑨⑩⑪ 中的多数）。

---

## 4. 架构层面的三个根本问题

### 4.1 没有模型层

```
joint_list = []      # 全局，模块级
pose_list  = []      # 全局，模块级，与 joint 无任何关联
```

- 没有主键，用 `name()` 当键 —— 可重名、改名即断链。
- 没有归属，Joint 不知道自己的 Pose；删除不级联。
- 没有变更通知，UI 靠手写 `updateItems` 全量重刷 —— 而全量重刷又触发 §3.1③ 的丢子项问题。
- 没有持久化，`dump/load` 全项目 0 调用。

### 4.2 抽象层是空契约

`protocol.py` 定义 `create/destroy/name/info/view/dump/load/driveAttribute`，但：

- 不继承 `ABCMeta` → 不强制实现；
- `create()` 无参数，拿不到 Maya 节点，无法表达"绑定到某个场景对象"；
- `view()` 返回 `QWidget` → 抽象层反向依赖 UI 层；
- `driveAttribute()` 返回 `str`，没有 getter/setter、没有值域、没有驱动目标，无法驱动任何东西；
- 全项目 **0 个调用点**，唯一实现是 `test_ui.py` 里的两个 uuid 假类。

也就是说：想用"可注册类型"避免写死具体骨架，这个方向是对的，但现在的实现没有任何约束力。

### 4.3 UI 与业务双向直连

`BodyWidget` 直接 import 并读写全局 `list`（`gui/ui.py:14-18`），控件之间用"显示文本"当 ID 传递（`updateChildItems` 按 text 匹配、`_now_joint_child_key` 存名字）。任何真实的模型层都无法从这种耦合里长出来。

---

## 5. 设计图 vs 实现

| # | 功能 | 设计图 | 现状 | 判定 |
|---|---|---|---|---|
| 1 | 无边框窗 / 标题栏 / 拖动 | ✓ | `FramelessWindow`（拖动仅标题栏空白处可用） | 🟡 |
| 2 | 左栏关节列表 | ✓ | `_JPlistWidget` + 折叠面板 | 🟡 |
| 3 | 展开显示该关节的姿态 | ✓ | 会丢子项、会串姿态 | 🔴 |
| 4 | 添加/删除关节、姿态 | ✓ | 能点，删除语义错、不级联 | 🔴 |
| 5 | 左栏搜索姿势 | ✓ | 无任何过滤逻辑 | 🔴 |
| 6 | 全局搜索 | ✓ | 假数据 10 条，无接收者 | 🔴 |
| 7 | 菜单栏 | ✓ | Option1/2/3 | 🔴 |
| 8 | 中部 2D 旋转编辑器 | ✓ | 不存在 | 🔴 |
| 9 | 网格编辑开关 | ✓ | 不存在 | 🔴 |
| 10 | 右侧旋转属性 + 驱动类型 | ✓ | 一张占位 QLabel | 🔴 |
| 11 | 底部 blendShape / 骨骼关联 | ✓ | 不存在 | 🔴 |
| 12 | 姿态 → 驱动落盘（SDK/约束） | 核心 | 不存在 | 🔴 |
| 13 | 保存 / 加载 | 隐含 | 不存在 | 🔴 |
| 14 | 撤销 / 重做 | 隐含 | 不存在 | 🔴 |
| 15 | 镜像（locator / 驱动） | 旧截图有 | 不存在 | 🔴 |
| 16 | 旧版"骨骼创建"能力 | 图注要求 | 未开始；按新设计实现，不复用 V1 代码 | 🔴 |

**完成度估算：UI 外壳 ~60%，整个项目 ~12%。**

---

## 6. 资产盘点：什么该留、什么该扔

### 6.1 可以从工作区保留（改写后复用）

| 资产 | 评价 |
|---|---|
| 视觉规范：深色配色、圆角、三色窗控、图标风格、`base.qss` | 有辨识度，值得保留；但要把 QSS 与 `paintEvent` 的硬编码颜色统一成一份调色板常量 |
| `FramelessWindow` 的**方向** | 已经改用 `startSystemMove`/`startSystemResize` + 锚点法兜底，思路正确；只需修边缘命中（§3.1④） |
| `RoundButton` / `IconButton` / `_ListItemWidget` 的绘制与状态机 | 代码干净，可直接搬 |
| `_CollapsibleBox` 的动画方案 | 方案可用，但要改成"单击 + `isChecked()` 驱动"，并去掉 `content_area.destroy()` |
| `IconPath` 枚举 | 保留，修大小写 |
| `interface/protocol.py` 的**类型注册概念** | 保留概念，重写实现 |

### 6.2 必须重写

| 旧 | 新 | 原因 |
|---|---|---|
| 全局 `joint_list`/`pose_list` | `core.Project` → `Joint.poses` → `Pose.drivers` | 归属、主键、通知、级联、序列化都缺 |
| 手搭控件列表 + 文本主键 | `QAbstractItemModel` + `QTreeView` + delegate | 现在 6 个 bug 里有 4 个来自"widget-per-row + deleteLater + 按文本找" |
| `ListWidget` 双模式 | `JointTreePanel` + `ShapeListPanel` | 同一个类被用成两种模式，靠 `hasattr` 区分 |
| `SearchFunctionWindow` | `QSortFilterProxyModel` + 真实命令索引 | 现在与业务零连接 |
| `MenuButton` 的假菜单 | `QAction` + 命令表 | 菜单本来就该是命令入口 |
| `test_ui.py` 当入口 | `app.py` / `entry.py`，`test_ui.py` 只做演示 | 生产入口不应 import 测试数据 |
| `RightWidget.setItem(1)` | 明确的 `set_pose(pose)`，`None` 表示无选中 | 传 int 是明显的占位残留 |

### 6.3 关于 V1（已决定不复用）

V1 `UVDriveJoint`（2023）保存在 git `313f0b0`，是上一代独立工具，**本项目不复用它的代码或逻辑**。它当时的做法是"球面 UV → `dU`/`dV` → SDK"，且写死 ADV 骨架、用场景节点名当数据库、代码是 Py2 + PySide —— 这些都与本项目的目标不符。

这个决定带来三个直接后果，排期时要算进去：

1. **`maya/` 层没有可继承的实现**：SDK（`setDrivenKeyframe`）、约束 / 矩阵网络、姿态坐标求值、镜像、权重迁移，全部从零设计。
2. **设计图右侧的旧截图只提供"功能清单"**，不提供实现细节；每一项都要重新定义接口。
3. **§5 里"旧截图有"的能力（镜像、撤销、驱动系统构建）等同于未实现**，不能按"已有"估算工作量。

好处是不会被旧实现绑架：不必继承 ADV 硬编码，也不必绕开旧的数据组织方式。

> 如果日后需要考古，`git show 313f0b0:V1/` 仍可查阅；但不要把其中的实现当作设计依据。

### 6.4 建议删除

- `test_script.py`（第三方 demo）、`_MenuWidget`、`MenuButton` 里的 `Option1/2/3`、9 处 `print`、`widgetT.py` 注释掉的死代码。
- 所有 `__pycache__`、`__init__.pyc`、`.idea.bak/`。
- `gui/icons/` 里从未使用的 `up_arrow.png`/`down_arrow.png`（或真正用起来）。

---

## 7. 重写路线

原则：**先存档，再立模型，最后做界面**。不要在旧控件库里继续打补丁 —— §3 里 6 个 UI bug 有 4 个源于同一套"widget-per-row + deleteLater + 文本主键"的设计，逐个修的成本高于换模型/视图。

### Phase 0：存档（已完成，剩收尾）

- [x] 提交 1828 行改动 → `40a80e9「重启」`（2026-10-26）
- [ ] 加 `.gitignore`（`__pycache__/`、`*.pyc`、`.idea/`、`.idea.bak/`）
- [ ] `git rm -r --cached` 掉已跟踪的 pyc，并清掉索引里暂存的 `A`/`AM` 条目
- [ ] `git add docs/ gui/icons/*.png`，让分析与图标入库
- [ ] 打 tag `v0.2-prototype`
- [ ] 给 `313f0b0` 打 `v0.1-legacy`（只打标签，不恢复代码）

**验收**：`git status` 干净；`git ls-files` 里没有 `.pyc`；`docs/` 与 6 张图标已被跟踪。

### Phase 1：骨架 + 模型（1–2 天）

```
PoseDrive/
├─ app.py                  # 唯一入口：show() / close()，含 __main__ 守卫
├─ compat/qt.py            # PySide2 → PySide6 兼容（为 Maya 2025+ 留路）
├─ core/                   # 纯 Python，不 import Qt
│  ├─ model.py             # Project / Joint / Pose / Driver
│  ├─ registry.py          # TypeRegistry（带校验、可枚举）
│  └─ events.py            # 变更通知（简单回调即可，先不上 Qt signal）
├─ maya/
│  ├─ host.py              # MQtUtil / shiboken2、窗口生命周期
│  ├─ rig.py               # 姿态 → 目标（blendShape / 骨骼）的写入与回滚
│  └─ sdk.py               # setDrivenKeyframe 封装
└─ gui/
   ├─ window.py
   ├─ panels/
   └─ widgets/             # 从 widgetT 拆出来的基础控件
```

- `core.model` 建议形状：

```python
class Pose:
    id: str                     # uuid4，稳定主键
    name: str
    uv: tuple[float, float]     # 二维姿态坐标，归一化到 0..1
    drivers: list[Driver]

class Joint:
    id: str
    name: str
    node: str | None            # Maya 节点（可空，纯数据也能用）
    icon: IconPath
    poses: list[Pose]           # ★ 归属关系在这里

class Project:
    version: int                # schema 版本，为迁移留口
    joints: list[Joint]
```

- 用 `pytest` + 一个内存 fake 的 registry 覆盖模型（headless，不需要 Qt）。
- `gui/ui.py` 的 `showUI()` 改为真正构造 `MainWindow` 并 `show()`；`main.py` 加 `if __name__ == "__main__"`。

**验收**：`mayapy -c "import PoseDrive; PoseDrive.show()"` 能出窗口且 `joint_list` 为空时**不崩**；`pytest` 全绿。

### Phase 2：真实列表（2–3 天）

- `JointTreeModel(QAbstractItemModel)` + `QTreeView`，Joint 为顶层、Pose 为子项；选中态、重命名、拖拽留接口。
- 增删改查走 `Project` 的方法，UI 只发命令、听通知。
- 删除关节时级联删除其 pose（模型层保证），加确认对话框。
- 用 `QSortFilterProxyModel` 做左栏搜索。
- 保留折叠外观时，用 `QTreeView.setExpanded` + delegate，不要再用 `_CollapsibleBox` 包 `QScrollArea`。

**验收**：加关节/加姿态/删姿态/删关节后，树与模型一致；空工程可启动；搜索能过滤。

### Phase 3：核心业务（2 周，本项目真正的价值；全部从零设计）

1. **先定驱动模型**（落在 `core`）：Pose 的二维坐标怎么求值、Driver 怎么描述（目标属性 + 键值对 + 权重）、一个 pose 对应一条还是多条驱动。这一步决定后面所有接口，建议先用一页纸写清楚再动代码。
2. `PosePad(QWidget)`：QPainter 画 2D 盘 + 当前姿态点，`mouseMoveEvent` 输出 `(u, v)`，支持拖拽、吸附、网格开关。这是设计图的中心区域。
3. `maya/sdk.py`：按 §8-4 选定的方案落 `setDrivenKeyframe` —— driver 属性、driven 通道、neutral 键、可撤销。
4. `maya/rig.py`：姿态 → 目标（blendShape 权重 / 骨骼变换 / 控制器偏移）的写入与回滚；每个操作包 `cmds.undoInfo(ock/cck)`。
5. 右侧属性面板：显示所选 pose 的坐标、驱动类型、绑定的目标。
6. 底部关联面板：把 pose 连到 blendShape target 或骨骼，支持添加 / 移除。
7. 镜像：先只做单轴 R→L 的坐标与驱动镜像，范围可控。
8. 首次拿一个真实角色跑通：选关节 → 建 4 个姿态 → 每个姿态驱动一个 blendShape → 旋转关节能看到形变。

**验收**：在真实场景里完成"建姿态 → 绑驱动 → 形变正确 → 撤销回退"。

### Phase 4：工程化（3–5 天）

- JSON 工程文件（带 `version` 与迁移函数）+ 自动保存。
- `pytest` + `pytest-qt`（offscreen）回归；把本文 §3.1/§3.2 的 11 条问题各写成一个测试。
- 打包：`.mod` + 用户脚本目录 + 货架按钮。
- （可选）Maya 2025+ 的 PySide6 兼容验证。

---

## 8. 需要你拍板的 6 件事

1. **目标 Maya 版本**：本机装了 2020（Py2.7 / PySide2 5.12.5）和 2022（Py3.7 / PySide2 5.15.2）。建议以 **2022 为主**，2020 兼容作为加分项；2025+ 需要 `compat/qt.py`。若只服务自己，直接 2022 就好，别背 PySide6 的包袱。
2. **窗口形态**：独立浮动窗（现状，`Qt.Window` + Maya 主窗为 parent）还是可停靠面板（`workspaceControl`）？做绑定工具通常停靠更实用，但浮动窗更适合现在的自绘皮肤。
3. **Pose 的归属**：是"关节的属性"（删关节即删姿态，简单）还是"可复用资源"（同一姿态可被多个关节引用，需要多对多）？这决定模型是树还是图。**建议先做树**，需要复用时再引入引用计数。
4. **驱动落盘方式**：SDK（`setDrivenKeyframe`，直观可编辑）、约束、还是自定义节点（性能好但不可读）？建议 **SDK 优先，留驱动类型的扩展点**。
   同时要定 **二维姿态的求值方式**：两条 1D 曲线混合（实现简单，但双轴同时变化时混合不精确），还是每个 Pose 一个独立标量 / 真正的二维驱动节点（精确，但要自己管求值）。这直接决定 `core.model.Pose` 存 `(u, v)` 还是标量。
5. **是否保留"类型注册"的设想**：如果只有你一个人用、只服务一种绑定，`protocol` 可以直接删掉，用具体的 `SDKJoint`/`SDKPose` 类更省事。如果打算做成能给别人接的工具，就按 §7 Phase 1 重写注册器。**建议先删，留接口位置**。
6. **姿态怎么产生**：是"把关节摆到目标姿态后点一下捕获"（贴近绑定师习惯，2D 坐标只是记录结果），还是"直接在 2D 盘里拖出姿态"（2D 盘是主要输入）？设计图的措辞是"**显示**当前所选姿势的旋转二维平面图"，倾向捕获式；但这决定 `PosePad` 是只读回显还是可拖拽输入，必须在 Phase 3 前定。

---

## 9. 附：如何复现本文的实测结论

分析用的探针脚本不在仓库内（放在 `%TEMP%\posdrive_probe\`，未纳入版本管理）。复现方式：

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
$env:QT_QPA_FONTDIR   = "C:\Windows\Fonts"
& "C:\Program Files\Autodesk\Maya2022\bin\mayapy.exe" probe.py
```

其中 `probe.py` 的关键三步：

```python
sys.path.insert(0, r"C:\Users\jeff\Documents\maya\scripts")   # 让 import PoseDrive 生效
import PoseDrive.test_ui                                       # 触发假数据注入
w = PoseDrive.gui.ui.MainWindow(); w.show()
# 之后用 QTest.mouseClick / QTest.mouseDClick 模拟点击，观察模型计数与控件树
```

如果需要，我可以把这套探针整理成 `tests/ui_smoke_test.py`，直接在 Phase 4 里当回归基线用。
