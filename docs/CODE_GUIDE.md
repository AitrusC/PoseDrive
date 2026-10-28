# PoseDrive 代码结构说明

> 对应快照：2026-10-21，工作区当前代码（`widgetT.py` 1317 行、总计 2146 行）
> 用途：重写前的模块/函数级底图 —— 每个模块负责什么、每个函数做什么、谁调用它、现在有什么问题。
> 配套文档：[ANALYSIS.md](ANALYSIS.md)（缺陷实测与重写路线）。本文只描述"现在是什么"，不重复论证"为什么坏"。
> 说明：所有行号对应当前快照；**[实测]** 标记的结论来自 Maya 2022 `mayapy` 实际运行。

---

## 1. 先看全局

### 1.1 文件树与职责

```
PoseDrive/
├─ main.py                  入口（当前是坏入口：只 import 不显示）
├─ __init__.py              包入口，转调 test_ui.show_ui_in_maya
├─ test_ui.py               假数据 + 真正的窗口启动函数（事实上的 entry）
├─ test_script.py           第三方 CollapsibleBox 示例（与项目无关）
│
├─ gui/
│  ├─ ui.py                 主窗口、左右分栏、业务回调（直接读写全局 list）
│  ├─ design/*.png          需求设计图（唯一需求来源）
│  ├─ icons/__init__.py     图标路径枚举 IconPath
│  └─ widget/
│     ├─ widgetT.py         控件库：18 个类/函数
│     └─ qss/base.qss       全局样式（48 行）
│
└─ interface/
   ├─ protocol.py           Joint/Pose 抽象协议 + 类型注册器（不生效）
   └─ gui.py                全局 joint_list / pose_list + 4 个 CRUD
```

### 1.2 依赖方向

```
main.py ──> gui.ui ──> gui.widget.widgetT ──> gui.icons
                │
                └──> interface.gui ──> interface.protocol ──> PySide2.QtWidgets
```

关键点：

- `gui.ui` 是唯一同时依赖"界面"和"数据"的模块。
- `interface.protocol` 为了一个返回值类型注解 `QWidget` 而依赖 Qt（`protocol.py:11`），所以"数据层"实际上离不开 Qt。
- **没有任何模块依赖 Maya API**。整个项目只有 `test_ui.py:102` 用 `OpenMayaUI` 取主窗口。

### 1.3 启动方式（现状）

| 方式 | 结果 |
|---|---|
| `python main.py` / `mayapy main.py` | ❌ 只 import，窗口不出现（`showUI()` 是 `pass`） |
| Maya 脚本编辑器 `import PoseDrive; PoseDrive.show_ui_in_maya()` | ✅ 能出窗口，但数据是 `test_ui.py` 里 3 个假关节 + 1 个假姿态 |
| `mayapy test_ui.py` | ✅ 直接起一个 QApplication 显示窗口 |

### 1.4 运行时对象树

```
MainWindow (FramelessWindow)
└─ QVBoxLayout
   ├─ _TitleBar                      30px 高
   │  ├─ QLabel(图标)
   │  ├─ MenuButton ×3（文件/工具/帮助）
   │  ├─ SearchFunctionWidget        ← 全局搜索框（QLineEdit）
   │  └─ RoundButton ×3（最小化/最大化/关闭）
   └─ BodyWidget
      └─ QHBoxLayout
         ├─ ListWidget("骨骼与驱动")  固定宽 250，joint-pose 模式
         │  ├─ 标题 QLabel + IconButton(+)
         │  ├─ IconButton(−)
         │  ├─ SearchLine
         │  └─ _JPlistWidget
         │     └─ _CollapsibleBox ×N
         │        ├─ _ToolButton（关节名，25px）
         │        └─ QScrollArea → _ListItemWidget ×M（姿态行）
         └─ RightWidget
            └─ PoseEditWidget 或 QLabel("请选择一个关节姿态")
               └─ ListWidget("SHAPE列表")  shape 模式
                  └─ _ShapeListWidget → _ListItemWidget ×N
```

---

## 2. 模块详解

### 2.1 `main.py`（9 行）

| 行 | 内容 | 说明 |
|---|---|---|
| 7 | `from gui.ui import showUI` | 绝对导入，要求"PoseDrive 目录本身"在 `sys.path`；不支持 `import PoseDrive.main` |
| 9 | `showUI()` | 模块级调用，没有 `if __name__ == "__main__"` 守卫 |

**作用**：名义入口。**现状**：`showUI()` 是 `pass`，所以运行后什么都不发生。

---

### 2.2 `__init__.py`（31 行）

| 行 | 内容 | 说明 |
|---|---|---|
| 15–18 | `from importlib import reload` | Py2 兼容残留，包内没有配套的 reload 逻辑 |
| 21–27 | `show_ui_in_maya()` | 延迟导入 `test_ui.show_ui_in_maya` 并转调，返回窗口对象 |
| 30 | `__all__ = ["show_ui_in_maya"]` | 对外只暴露这一个函数 |

**作用**：包门面。**现状**：把生产入口委托给测试文件；`test_ui` 被 import 时会往全局列表塞假数据 [实测]。

---

### 2.3 `interface/protocol.py`（182 行）——抽象层

**职责**：定义 Joint / Pose 必须实现的方法，并提供类型注册（供 UI 按名字创建实例）。

#### 注册器

| 行 | 符号 | 作用 | 问题 |
|---|---|---|---|
| 14 | `pose_types = []` | 模块级可变列表 | 无重复检测、无注销 |
| 15 | `joint_types = []` | 同上 | 同上 |
| 17–19 | `registerPoseType(cls)` | 装饰器：`append` 后原样返回类 | 不校验 `type_name` |
| 22–24 | `registerJointType(cls)` | 同上 | 同上 |

#### `JointProtocol`（27–96）

| 行 | 成员 | 类型 | 作用 |
|---|---|---|---|
| 31 | `type_name = "unimplemented"` | 类属性 | 注册与查找的键 |
| 32 | `icon_path = None` | 类属性 | UI 图标路径 |
| 34–41 | `create()` | `@classmethod` | 工厂；无参数，拿不到 Maya 节点 |
| 43–50 | `destroy()` | `@abstractmethod` | 销毁关节 |
| 52–59 | `name()` | `@abstractmethod` | 名称（被当作主键） |
| 61–68 | `info()` | `@abstractmethod` | 文本信息（无调用点） |
| 70–77 | `view()` | `@abstractmethod` | 返回 `QWidget`（无调用点） |
| 79–86 | `dump()` | `@abstractmethod` | 序列化（无调用点） |
| 88–96 | `load(data)` | `@abstractmethod` | 反序列化；与 `create()` 的类/实例语义不一致 |

#### `PoseProtocol`（99–177）

成员与 `JointProtocol` 基本一致，额外多一个：

| 行 | 成员 | 作用 |
|---|---|---|
| 115–122 | `driveAttribute()` | 声明"获取驱动属性"，返回 `str`；**没有 getter/setter，无法真正驱动任何东西**；无调用点 |

**关键事实**：两个类都继承 `object` 而不是 `abc.ABC`，`@abstractmethod` 不会生效 —— 缺全部方法的子类可以直接实例化 [实测]。

---

### 2.4 `interface/gui.py`（72 行）——数据门面

**职责**：维护两张全局表，提供按"类型名"创建、按"名称"删除的 CRUD。

| 行 | 符号 | 签名 | 作用 | 问题 |
|---|---|---|---|---|
| 13 | `pose_list` | `list` | 全局姿态表 | 与 joint 无关联 |
| 14 | `joint_list` | `list` | 全局关节表 | 无主键、可重名 |
| 16–21 | `addJoint(type_name)` | `str -> JointProtocol` | 查类型 → `create()` → append | 类型不存在抛 `LookupError` |
| 23–28 | `_findJoint(name)` | `str -> Joint` | 线性查名字 | 重名取第一个；改名断链 |
| 30–34 | `removeJoint(name)` | `str -> None` | 查找 → `destroy()` → 移除 | **不级联删除 pose** |
| 36–41 | `_findJointType(type_name)` | `str -> type` | 按 `type_name` 查注册表 | 无缓存 |
| 43–48 | `_findPoseType(type_name)` | `str -> type` | 同上 | 同上 |
| 50–55 | `addPose(type_name)` | `str -> PoseProtocol` | 查类型 → `create()` → append | **不接收 joint 参数** |
| 57–62 | `_findPose(name)` | `str -> Pose` | 线性查名字 | 同上 |
| 64–68 | `removePose(name)` | `str -> None` | 查找 → `destroy()` → 移除 | 命名打错（`pose_nane`）；类型注释写成 `set` |

**作用**：所有业务数据的唯一入口。**现状**：两表平级、无归属、无通知，UI 只能全量重刷。

---

### 2.5 `gui/ui.py`（200 行）——主窗口与业务回调

#### `PoseEditWidget`（21–58）——右侧"编辑面板"（占位）

| 行 | 方法 | 作用 |
|---|---|---|
| 26–58 | `__init__(pose, parent=None)` | 建一个 `QVBoxLayout`；放 `QLabel("关节姿态")`、`X:`、`Y:`；再放一个 `ListWidget("SHAPE列表")` 并调 `addShapeList()` |

**问题**：`pose` 参数**完全没被使用**；`X:`/`Y:` 只是文本标签，没有输入控件。

#### `RightWidget`（61–95）——右侧容器

| 行 | 方法 | 作用 | 问题 |
|---|---|---|---|
| 66–73 | `__init__` | 建布局并立刻 `setItem(None)` | 布局设了 `AlignCenter` |
| 75–81 | `clear()` | 遍历布局项 `deleteLater()` | 延迟生效，新旧控件会并存 [实测] |
| 83–95 | `setItem(pose)` | 真值 → `PoseEditWidget(pose)`；假值 → 占位 `QLabel` | 调用方传过 `1`（int） |

#### `BodyWidget`（98–176）——左右分栏 + 业务回调

| 行 | 方法 | 作用 | 问题 |
|---|---|---|---|
| 103–128 | `__init__` | 建左栏 `ListWidget("骨骼与驱动")` + `addJointPoseList()`；连接 3 个信号；用全局 `joint_list` 刷新列表；**无条件访问 `joint_list[0]`**；建 `RightWidget` 并 `setItem(1)` | 空数据即 `IndexError` [实测]；`setItem(1)` 是占位残留 |
| 130–147 | `addJointAndPose(key)` | `key` 真：`addPose("test_pose")` + 刷新该关节子项；`key` 假：`addJoint("test_joint")` + 刷新全部关节 | 类型名写死；两分支的 `print` 文案与实际动作相反 |
| 149–155 | `setPose(key)` | 只 `print("setPose", key)` | **右侧面板完全不更新** [实测] |
| 157–176 | `destroyJointAndPose(key)` | `key[1]` 真：删 pose；否则删 joint | 删除目标取决于隐藏的选中态；删关节不级联 [实测] |

#### `MainWindow`（181–192）

| 行 | 方法 | 作用 |
|---|---|---|
| 186–192 | `__init__(parent=None)` | 先 `BodyWidget()`，再 `FramelessWindow.__init__(content_widget=..., parent=...)`；设 1080×720、最小尺寸、objectName |

**注意**：`body_widget` 是局部变量，**没有保存成属性**，外部拿不到（`hasattr(w, "body_widget") == False` [实测]）。

#### `showUI`（195–200）

```python
def showUI():
    """窗口显示"""
    pass
```

**作用**：应该启动窗口，实际是空函数。

**另外**：第 14–18 行从 `interface.gui` 导入了 `pose_types`、`joint_types`，但全文未使用。

---

### 2.6 `gui/widget/widgetT.py`（1317 行）——控件库

18 个类/函数。`__all__` 只导出 `FramelessWindow` 和 `ListWidget`（`1303`），其余靠模块内引用。

#### 2.6.1 工具函数

| 行 | 函数 | 签名 | 作用 | 使用者 |
|---|---|---|---|---|
| 18–41 | `_setLuminance(rgb, uord, percent)` | `(r,g,b), bool, 0~1 -> (r,g,b)` | RGB→YUV 调亮度再转回 | `RoundButton.paintEvent` |
| 44–57 | `_setOpacity(rgba, uord, percent)` | `(r,g,b,a), bool, 0~1 -> rgba` | 只改 alpha 通道 | `IconButton.paintEvent` |

#### 2.6.2 `_TitleBar(QWidget)`（60–205）——自绘标题栏

| 行 | 方法 | 作用 | 备注 |
|---|---|---|---|
| 66–110 | `__init__(parent=None)` | 固定高 30；左侧图标；3 个 `RoundButton`（最小化/最大化/关闭）；3 个 `MenuButton`（文件/工具/帮助，各挂 `Option1/2/3`）；`SearchFunctionWidget` | 菜单项是 `print` 假回调 |
| 112–120 | `__toggleMaxState()` | 最大化 ↔ 还原 | 私有 |
| 122–130 | `mouseDoubleClickEvent(event)` | 双击标题栏切换最大化 | |
| 132–144 | `mousePressEvent(event)` | 在可拖拽区按下：记录全局起点与窗口位置 | |
| 146–169 | `mouseMoveEvent(event)` | 超过拖动阈值后：优先 `windowHandle().startSystemMove()`；不支持则手动 `move()`；最大化时放弃拖动 | Qt ≥5.15 走系统原生 |
| 171–178 | `mouseReleaseEvent(event)` | 清拖动状态 | |
| 180–205 | `_isDragRegion(pos)` | 判断点是否在可拖拽区（排除四边 5px 与标题栏外） | 右侧搜索框覆盖的区域会先收到事件 |

**调用关系**：三个圆按钮的 `clicked` 分别连到 `showMinimized` / `__toggleMaxState` / `close`。

#### 2.6.3 `FramelessWindow(QWidget)`（208–350）——无边框主窗

| 行 | 方法 | 作用 | 备注 |
|---|---|---|---|
| 214–235 | `__init__(content_widget=None, parent=None)` | 加 `FramelessWindowHint` 与 `Window` 两个 flag；读 QSS（`__file__ + "/../qss/base.qss"`）；建 `_TitleBar` + 内容控件 | 路径用字符串拼接 |
| 237–247 | `paintEvent(event)` | 填充深色背景 `QColor(48,55,52)` | 与 QSS 两套颜色 |
| 249–264 | `_edge_at(pos)` | 用局部坐标判断命中哪条边，返回 `Qt.Edges` | 逻辑正确，但事件到不了 |
| 266–286 | `mousePressEvent(event)` | 命中边 → `startSystemResize()`，失败则记录锚点转手动缩放；否则 accept | **被子控件挡住，收不到事件** [实测] |
| 288–313 | `mouseMoveEvent(event)` | 手动缩放 + 按边设置缩放光标 | 同上 |
| 315–331 | `_fallback_resize(event)` | 锚点法手动缩放（以按下时的 geometry 为基准） | 无累计漂移 |
| 333–341 | `mouseReleaseEvent(event)` | 清缩放状态 | |
| 343–350 | `leaveEvent(event)` | 恢复箭头光标 | |

#### 2.6.4 `RoundButton(QAbstractButton)`（353–453）——圆形按钮

| 行 | 方法 | 作用 |
|---|---|---|
| 359–371 | `__init__(radius=25, grcolor=None)` | 固定尺寸 `radius × radius`（把"半径"当直径用） |
| 373–378 | `sizeHint()` | 返回 `radius × radius` |
| 380–387 | `set_state(enum)` | 切 `NORMAL/HOVER/PRESS` 并重绘 |
| 389–397 | `mousePressEvent` | 左键 → `PRESS` |
| 399–412 | `mouseReleaseEvent` | 在按钮内 → `HOVER`，否则 `NORMAL` |
| 414–430 | `enterEvent` / `leaveEvent` | 切 `HOVER` / `NORMAL` |
| 432–453 | `paintEvent` | 用 `_setLuminance` 提亮 20%/35% 画圆 |

**使用者**：`_TitleBar` 的三个窗控按钮。

#### 2.6.5 `IconButton(QAbstractButton)`（456–543）——图标按钮

| 行 | 方法 | 作用 |
|---|---|---|
| 461–481 | `__init__(icon_path, icon_size, margin=5, hover_color=(0,0,0,20), parent=None)` | 固定 `icon_size + margin*2`；预加载并缩放图标 |
| 483–503 | `mousePressEvent` / `mouseReleaseEvent` | 维护 `_pressed` |
| 505–523 | `enterEvent` / `leaveEvent` | 维护 `_hover` |
| 525–543 | `paintEvent` | 半透明悬停/按下底色 + 贴图 |

**使用者**：左栏的 `+` / `−`。

#### 2.6.6 `SearchLine(QLineEdit)`（546–561）

| 行 | 方法 | 作用 |
|---|---|---|
| 551–561 | `__init__(placeholder_text="搜索...", parent=None)` | 高 20、居中、设 placeholder |

**使用者**：`ListWidget` 的左栏搜索、`SearchFunctionWidget` 的基类、`SearchFunctionWindow` 的输入框。

#### 2.6.7 `_ToolButton(QPushButton)`（564–598）——折叠组头

| 行 | 方法 | 作用 | 问题 |
|---|---|---|---|
| 568 | `doubleClicked = Signal(bool)` | 自定义"双击"信号 | 与 Qt 自身 `clicked` 双轨 |
| 570–579 | `__init__(parent=None)` | 可 check、固定高 25 | |
| 581–590 | `mouseDoubleClickEvent(event)` | 翻转 `_double_click` 并 emit | 状态与 `isChecked()` 无关 |
| 592–598 | `setDoubleClicked(bool)` | 设置标记 | 全项目无调用 |

#### 2.6.8 `_CollapsibleBox(QWidget)`（601–728）——折叠面板

| 行 | 方法 | 作用 | 问题 |
|---|---|---|---|
| 610 | `item_clicked = Signal(str)` | 子项点击时带 `key` 发出 | |
| 612–659 | `__init__(title="", icon_path=None, parent=None, animation_duration=300)` | 组头 + 0 高度的 `QScrollArea`；三组并行动画（自身 min/max 高度 + 内容 max 高度）；建立 `item_layout` | 动画值要等 `setContentLayout` 才设置 |
| 661–669 | `on_pressed(checked)` | 按 `_double_click` 决定动画方向并启动 | 只由**双击**触发 |
| 671–696 | `setContentLayout(layout=None)` | `content_area.destroy()` → `setLayout(layout)` → 算折叠/展开高度 → 写入动画起止值 | `destroy()` 会销毁窗口与子对象；每次刷新都调用 |
| 698–709 | `addItem(key, name, icon_path=None)` | 新建 `_ListItemWidget`，`clicked` → emit `item_clicked(key)` | |
| 711–720 | `updateItems(item)` | `clearItems()` → 逐条 `addItem` → `setContentLayout()` | 刷新时旧项仍在布局里 |
| 722–728 | `clearItems()` | 对布局项 `deleteLater()` | 延迟生效 |

**被谁用**：`_JPlistWidget.addJointItem`。**谁调用它的方法**：`_JPlistWidget.updateChildItems` → `updateItems`。

#### 2.6.9 `_ListItemWidget(QWidget)`（731–824）——列表行

| 行 | 方法 | 作用 |
|---|---|---|
| 736 | `clicked = Signal()` | 行被点击 |
| 738–757 | `__init__(text, icon_path=None, parent=None)` | 固定高 25；左图标 + 文本 |
| 761–768 | `setState(enum)` | 切 `NORMAL/HOVER/PRESS` |
| 770–789 | `mousePressEvent` / `mouseReleaseEvent` | 按下变 `PRESS`；在行内释放 → `HOVER` + `clicked.emit()` |
| 791–807 | `enterEvent` / `leaveEvent` | 切状态 |
| 809–824 | `paintEvent` | 用三种硬编码底色画矩形（无选中态、无省略号） |

**使用者**：`_CollapsibleBox.addItem`、`_ShapeListWidget.addPoseItem`。

#### 2.6.10 `_EButtonGroup(QButtonGroup)`（827–868）

| 行 | 方法 | 作用 |
|---|---|---|
| 832–841 | `__init__` | `setExclusive(False)`，自己维护 `current_checked_button`，连接 `buttonClicked` |
| 843–858 | `on_button_clicked(button)` | 再点已选按钮 → 取消选中；否则取消旧的、选中新的 |
| 860–868 | `removeButton(button)` | 移除时同步清空当前记录 |

**用途**：让关节组头"可全不选"。**使用者**：`_JPlistWidget`。

#### 2.6.11 `_JPlistWidget(QScrollArea)`（871–937）——关节 + 姿态树

| 行 | 方法 | 作用 | 问题 |
|---|---|---|---|
| 875 | `joint_pressed = Signal(str)` | 组头被点（带关节 key） | |
| 876 | `item_clicked = Signal(list)` | 子项被点（`[joint_key, pose_key]`） | |
| 878–892 | `__init__(parent=None)` | 滚动区 + 顶部对齐的 VBox + `_EButtonGroup` | |
| 894–906 | `addJointItem(key, joint_name, icon_path=None)` | 建 `_CollapsibleBox`，加入按钮组；`toggle_button.clicked` → `joint_pressed`；`item_clicked` → 包成 `[key, x]` 转发 | |
| 908–916 | `updateItems(item)` | `clearItems()` → 逐条 `addJointItem` | **新面板不带子项**，导致刷新丢姿态 [实测] |
| 918–925 | `clearItems()` | 移除按钮 + `deleteLater()` 每个面板 | 假定布局项都是 `_CollapsibleBox` |
| 927–937 | `updateChildItems(key, item)` | 用 `toggle_button.text() == key` 找面板 → `updateItems(item)` | **按显示文本匹配**，重名/改名即错；只填第一个匹配 |

#### 2.6.12 `_ShapeListWidget(QScrollArea)`（940–989）——扁平列表

| 行 | 方法 | 作用 |
|---|---|---|
| 944 | `on_pressed = Signal(str)` | 行被点击 |
| 946–959 | `__init__(parent=None)` | 滚动区 + 顶部对齐 VBox |
| 961–971 | `addPoseItem(key, pose_name, icon_path=None)` | 建 `_ListItemWidget`，`clicked` → `on_pressed(key)` |
| 973–981 | `updateItems(item)` | `clearItems()` → 逐条添加 |
| 983–989 | `clearItems()` | `deleteLater()` |

**使用者**：`ListWidget.addShapeList`（右侧 SHAPE 列表）、`SearchFunctionWindow`（搜索结果）。

#### 2.6.13 `ListWidget(QWidget)`（992–1100）——左栏组合面板（双模式）

| 行 | 方法 | 作用 | 问题 |
|---|---|---|---|
| 994–999 | 6 个信号 | `on_pressed(str)`、`on_joint_pressed(list)`、`add_click()`、`delete_click(str)`、`add_joint_click(str)`、`delete_joint_click(list)` | 两套模式共用 |
| 1001–1024 | `__init__(title, parent=None)` | 标题行（`QLabel` + 伸缩 + `+` / `−`）+ 搜索框 | `_add_button` / `_delete_button` 的连接在模式方法里才建立 |
| 1026–1037 | `addShapeList()` | shape 模式：`+` → `add_click`；`−` → `delete_click(_now_item_key)`；建 `_ShapeListWidget` 并连接 `on_pressed` | 这两个信号**在项目里没有接收者** |
| 1039–1052 | `addJointPoseList()` | joint-pose 模式：`+` → `add_joint_click(_now_joint_key)`；`−` → `_sendDeleteJointSignal`；连接组头/子项点击 | |
| 1054–1060 | `_setNowJointChildKey(key)` | 解包 `[joint, pose]` 存到两个字段 | |
| 1062–1069 | `_sendDeleteJointSignal()` | 发 `[joint, pose]` 后**清空两个字段** | 导致删除目标依赖历史选中 |
| 1071–1080 | `_setNowJointKey(key)` | 点同一个组头则取消选中 | |
| 1082–1088 | `_setNowItemKey(key)` | shape 模式记录当前项 | |
| 1090–1100 | `paintEvent(event)` | 画背景 `QColor(69,76,73)` | |

**模式区别**：同一类被实例化两次，靠"调用了哪个 `add*List()`"决定存在哪些属性（`jplist_widget` vs `poselist_widget`），外部用 `hasattr` 区分。

#### 2.6.14 `_MenuWidget(QMenu)`（1103–1113）

空壳，只为让 QSS 的 `_MenuWidget` 选择器生效。

#### 2.6.15 `MenuButton(QAbstractButton)`（1116–1177）

| 行 | 方法 | 作用 |
|---|---|---|
| 1121–1138 | `__init__(text, parent=None)` | 文本按钮，`clicked` → `showMenu` |
| 1140–1148 | `addOption(text, icon_path=None, func=None)` | 追加到 `_options` |
| 1150–1164 | `showMenu()` | **每次点击新建** `_MenuWidget`，逐项加 `QAction`，`exec_()` 到按钮下方 |
| 1166–1177 | `paintEvent(event)` | 鼠标悬停时画底色 |

#### 2.6.16 `SearchFunctionWidget(SearchLine)`（1180–1222）——全局搜索入口

| 行 | 方法 | 作用 |
|---|---|---|
| 1185–1192 | `__init__(parent=None)` | 用占位文本 `"SearchFunction"`，水平扩展 |
| 1194–1201 | `mousePressEvent(event)` | 左键 → `showSearchWindow()`（覆盖了输入框的默认行为） |
| 1203–1222 | `showSearchWindow()` | 用 **10 条硬编码选项** 建 `SearchFunctionWindow`，移动到搜索框下方，宽度对齐 |

#### 2.6.17 `SearchFunctionWindow(QWidget)`（1225–1300）——搜索弹窗

| 行 | 方法 | 作用 | 问题 |
|---|---|---|---|
| 1229 | `selected = Signal(str)` | 选中结果 | 项目内无接收者 |
| 1230–1249 | `__init__(options, parent=None)` | 无边框窗；输入框 + `_ShapeListWidget`；`textChanged` → `search`；行点击 → 关闭并 emit | |
| 1251–1261 | `search(text)` | 空串清空列表，否则按子串过滤后 `updateItems` | 只在 10 条假数据里过滤 |
| 1263–1269 | `listItemClicked(item)` | 关闭窗口 | 参数未用 |
| 1271–1278 | `showEvent(event)` | 聚焦输入框；**每次 show 都 connect 一次** `focusChanged` | 连接会累积 |
| 1280–1288 | `focusChanged(old, now)` | 焦点离开窗口 → 关闭 | |
| 1290–1300 | `paintEvent(event)` | 画背景 |

---

### 2.7 `gui/icons/__init__.py`（28 行）

`IconPath(Enum)`，7 个成员，值都是 `os.path.join(os.path.dirname(__file__), '<file>.png')`：

| 成员 | 行 | 文件名 | 使用者 |
|---|---|---|---|
| `TITLEBAR_PATH` | 16 | `titlebar.png` | `_TitleBar` 图标 |
| `DELETE_PATH` | 18 | `delete.png` | 左栏 `−` |
| `PLUS_PATH` | 20 | `plus.png` | 左栏 `+`、搜索假数据 |
| `JOINT_PATH` | 22 | `joint.png` | `TestJointProtocol.icon_path` |
| `BLENDSHAPE_PATH` | 24 | `blendShape.png` | `TestPoseProtocol.icon_path`、菜单项 |
| `UP_ARROW_PATH` | 26 | `up_arrow.png` | **无** |
| `DOWN_ARROW_PATH` | 28 | `down_arrow.png` | **无** |

**问题**：`titlebar.png` 与磁盘上的 `titleBar.png` 大小写不一致（Windows 可跑，Linux/macOS 丢图标）；`up/down_arrow` 从未使用。

---

### 2.8 `gui/widget/qss/base.qss`（48 行）

| 选择器 | 作用 |
|---|---|
| `QWidget` | 全局透明背景、`bold 10pt "Microsoft YaHei"`、文字色 `rgb(196,203,207)` |
| `SearchLine` | 搜索框底色 `rgb(58,65,63)` |
| `_JPlistWidget` / `_ShapeListWidget` | 去边框、去 padding |
| `_ToolButton` 及 `:hover/:pressed/:checked` | 组头配色 |
| `_MenuWidget` / `::item::selected` | 菜单配色（`::item::selected` 写法有误，应为 `::item:selected`） |

**注意**：QSS 的类名选择器匹配的是 Qt metaobject 里的类名（PySide 会把 Python 类名写进 metaobject），所以自定义类名能命中；但**一旦改类名、拆类或换成别的类，样式会静默失效**（不会报错）。`QWidget` 选择器则作用于所有控件，容易误伤。

---

### 2.9 `test_ui.py`（162 行）——假数据 + 事实上的入口

| 行 | 符号 | 作用 |
|---|---|---|
| 26–57 | `TestJointProtocol` | `@registerJointType`；`type_name="test_joint"`；名字用 `uuid4().hex[:8]`；`destroy/info/view/dump` 都是空转；`load` 是类方法 |
| 60–93 | `TestPoseProtocol` | `@registerPoseType`；`type_name="test_pose"`；同上（`driveAttribute` 空转） |
| 96–119 | `get_host_app()` | 先试 `OpenMayaUI.MQtUtil.mainWindow()` + `shiboken2.wrapInstance`；失败则从 `QApplication.activeWindow()` 向上爬 parent |
| 122–126 | `ShowUIInMaya(MainWindow)` | 默认 parent 为 `get_host_app()`（函数内求值） |
| 129 | `_ui` | 模块级单例 |
| 132–149 | `show_ui_in_maya()` | 关闭旧窗口 → 新建 → `show/raise_/activateWindow` → 返回窗口 |
| 152–156 | 模块级 seed | **import 就往 `joint_list` 塞 3 个、`pose_list` 塞 1 个** |
| 158–162 | `__main__` | 起 QApplication 显示 `MainWindow` |

**问题**：生产入口在测试文件里；import 即污染全局数据；`TestPoseProtocol.load` 是实例方法而 `TestJointProtocol.load` 是类方法（契约不一致）。

---

### 2.10 `test_script.py`（130 行）

第三方 `CollapsibleBox` 示例（`QToolButton` + `QParallelAnimationGroup` + `QScrollArea`），是 `_CollapsibleBox` 的原型。与项目无 import 关系，`__main__` 里是自己搭的 10 个折叠框 demo。

---

## 3. 信号连接总表

| 发出者 | 信号 | 载荷 | 接收者 | 实际效果 |
|---|---|---|---|---|
| `RoundButton`(min) | `clicked` | — | `_TitleBar.get_parent.showMinimized` | 最小化 |
| `RoundButton`(max) | `clicked` | — | `_TitleBar.__toggleMaxState` | 最大化切换 |
| `RoundButton`(close) | `clicked` | — | `_TitleBar.get_parent.close` | 关闭 |
| `MenuButton` | `clicked` | — | `MenuButton.showMenu` | 弹菜单 |
| `SearchFunctionWidget` | `mousePressEvent` | — | `showSearchWindow` | 开搜索窗 |
| `SearchFunctionWindow.search_line` | `textChanged` | `str` | `SearchFunctionWindow.search` | 过滤假数据 |
| `SearchFunctionWindow.list_widget` | `on_pressed` | `str` | `listItemClicked` + `selected.emit` | 关窗 |
| `_ToolButton` | `doubleClicked(bool)` | bool | `_CollapsibleBox.on_pressed` | 播放折叠动画 |
| `_ToolButton` | `clicked` | — | `_JPlistWidget.joint_pressed.emit(key)` | 记录当前关节 |
| `_ListItemWidget`(pose) | `clicked` | — | `_CollapsibleBox.item_clicked.emit(key)` | 转成 key |
| `_CollapsibleBox` | `item_clicked(str)` | pose key | `_JPlistWidget.item_clicked.emit([joint, pose])` | 包成二元组 |
| `_JPlistWidget` | `joint_pressed(str)` | joint key | `ListWidget._setNowJointKey` | 选中/取消关节 |
| `_JPlistWidget` | `item_clicked(list)` | `[joint, pose]` | `ListWidget._setNowJointChildKey` | 记录子项 |
| `_JPlistWidget` | `item_clicked(list)` | `[joint, pose]` | `ListWidget.on_joint_pressed.emit` → `BodyWidget.setPose` | 仅 print |
| `ListWidget._add_button`(joint 模式) | `clicked` | — | `add_joint_click.emit(_now_joint_key)` | 加关节或加姿态 |
| `ListWidget._delete_button`(joint 模式) | `clicked` | — | `_sendDeleteJointSignal` → `delete_joint_click` | 删关节或删姿态 |
| `ListWidget._add_button`(shape 模式) | `clicked` | — | `add_click.emit` | **无接收者** |
| `ListWidget._delete_button`(shape 模式) | `clicked` | — | `delete_click.emit(_now_item_key)` | **无接收者** |
| `_ShapeListWidget` | `on_pressed(str)` | key | `ListWidget._setNowItemKey` + `ListWidget.on_pressed` | **无接收者**（shape 模式） |
| `SearchFunctionWindow` | `selected(str)` | key | 无 | **无人监听** |

---

## 4. 四条关键调用链

### 4.1 启动

```
PoseDrive.show_ui_in_maya()
 → test_ui.show_ui_in_maya()
    → ShowUIInMaya()                 # parent = Maya 主窗
       → MainWindow.__init__
          → BodyWidget()
             → ListWidget.addJointPoseList()
             → jplist_widget.updateItems(所有关节)
             → jplist_widget.updateChildItems(joint_list[0].name(), 所有姿态)
             → RightWidget.setItem(1)
 → show / raise_ / activateWindow
```

### 4.2 添加

```
点击左栏 "+"
 → ListWidget._add_button.clicked
 → add_joint_click.emit(_now_joint_key)
 → BodyWidget.addJointAndPose(key)
    ├─ key 有值：addPose("test_pose") → updateChildItems(key, 整个 pose_list)
    └─ key 为空：addJoint("test_joint") → updateItems(整个 joint_list)
```

### 4.3 删除

```
点击左栏 "−"
 → ListWidget._delete_button.clicked
 → _sendDeleteJointSignal()
 → delete_joint_click.emit([_now_joint_key, _now_joint_child_key])
 → BodyWidget.destroyJointAndPose([joint, pose])
    ├─ pose 有值：removePose(pose) → updateChildItems(joint, 整个 pose_list)
    └─ pose 为空：removeJoint(joint) → updateItems(整个 joint_list)
 → 清空两个选中字段
```

### 4.4 选中

```
点击姿态行
 → _ListItemWidget.clicked
 → _CollapsibleBox.item_clicked(key)
 → _JPlistWidget.item_clicked([joint, pose])
 → ListWidget._setNowJointChildKey / on_joint_pressed
 → BodyWidget.setPose([joint, pose])   # 只 print
```

---

## 5. 数据流与状态归属

```
interface.gui.joint_list ──┐
                           ├── 全局、模块级、平级、无归属
interface.gui.pose_list  ──┘
        ▲                        ▲
        │ 读                     │ 写
   BodyWidget.addJointAndPose / destroyJointAndPose
        │
        ▼
   控件树（每次操作后全量重建）
```

- **唯一真相**：`interface.gui` 的两个列表 + 场景里不存在的 Maya 节点（本项目还没有）。
- **UI 状态**：`ListWidget._now_joint_key` / `_now_joint_child_key` / `_now_item_key`，以及 `_ToolButton._double_click`。
- **没有的东西**：主键、Joint→Pose 归属、变更通知、撤销栈、持久化。

---

## 6. 函数级快速索引

| 文件 | 符号 | 行 | 一句话 |
|---|---|---:|---|
| `main.py` | 模块体 | 7–9 | 导入 `showUI` 并调用（空实现） |
| `__init__.py` | `show_ui_in_maya` | 21 | 转调 `test_ui` |
| `test_ui.py` | `TestJointProtocol` | 26 | 假关节实现（uuid 名） |
| | `TestPoseProtocol` | 60 | 假姿态实现 |
| | `get_host_app` | 96 | 取 Maya 主窗口 |
| | `ShowUIInMaya` | 122 | 带 parent 的 MainWindow |
| | `show_ui_in_maya` | 132 | 单例打开/重建窗口 |
| `gui/ui.py` | `PoseEditWidget` | 21 | 右侧占位面板 |
| | `RightWidget.clear/setItem` | 75/83 | 右栏清空与切换 |
| | `BodyWidget.addJointAndPose` | 130 | 加关节/加姿态 |
| | `BodyWidget.setPose` | 149 | 打印选中（不更新 UI） |
| | `BodyWidget.destroyJointAndPose` | 157 | 删关节/删姿态 |
| | `MainWindow` | 181 | 1080×720 无边框主窗 |
| | `showUI` | 195 | 空函数 |
| `interface/protocol.py` | `registerPoseType/JointType` | 17/22 | 注册装饰器 |
| | `JointProtocol` | 27 | 关节契约（7 个方法） |
| | `PoseProtocol` | 99 | 姿态契约（8 个方法） |
| `interface/gui.py` | `addJoint/removeJoint` | 16/30 | 全局表 CRUD |
| | `addPose/removePose` | 50/64 | 同上 |
| `gui/widget/widgetT.py` | `_setLuminance/_setOpacity` | 18/44 | 颜色工具 |
| | `_TitleBar` | 60 | 标题栏 + 拖动 |
| | `FramelessWindow` | 208 | 无边框窗 + 缩放 |
| | `RoundButton` / `IconButton` | 353/456 | 自绘按钮 |
| | `SearchLine` | 546 | 搜索输入框 |
| | `_ToolButton` | 564 | 折叠组头 |
| | `_CollapsibleBox` | 601 | 折叠面板 |
| | `_ListItemWidget` | 731 | 列表行 |
| | `_EButtonGroup` | 827 | 可全不选按钮组 |
| | `_JPlistWidget` | 871 | 关节/姿态树 |
| | `_ShapeListWidget` | 940 | 扁平列表 |
| | `ListWidget` | 992 | 左栏组合（双模式） |
| | `_MenuWidget` / `MenuButton` | 1103/1116 | 菜单 |
| | `SearchFunctionWidget` | 1180 | 全局搜索入口 |
| | `SearchFunctionWindow` | 1225 | 搜索弹窗 |

---

## 7. 重写时每个模块的去向

| 现有模块 | 去向 | 理由 |
|---|---|---|
| `main.py` / `__init__.py` | 重写为 `app.py` + 包门面 | 入口必须真的 `show()`，且有 `__main__` 守卫 |
| `test_ui.py` | 拆成 `tests/` 与 `dev_demo.py` | 生产入口不能依赖测试假数据 |
| `gui/ui.py` | 拆成 `window.py` + `panels/*` | 业务回调不该和窗口构造混在一起 |
| `widgetT.py` 的按钮/行绘制 | 保留到 `gui/widgets/` | 视觉资产，代码干净 |
| `widgetT.py` 的 `_CollapsibleBox` | 丢弃，改用 `QTreeView` | widget-per-row + deleteLater 是 4 个 bug 的根源 |
| `_JPlistWidget` / `_ShapeListWidget` / `ListWidget` | 丢弃，改用 `QAbstractItemModel` + `QTreeView` | 文本主键、双模式、刷新丢项都出在这里 |
| `SearchFunctionWindow` | 重写为 `QSortFilterProxyModel` | 现在与业务零连接 |
| `MenuButton` / `_MenuWidget` | 重写为 `QAction` + 命令表 | 菜单应是命令入口 |
| `interface/protocol.py` | 保留概念，重写实现 | 不继承 ABC、无 Maya 绑定、无调用点 |
| `interface/gui.py` | 完全丢弃 | 换成 `core.Project / Joint / Pose` |
| `icons` / `base.qss` | 保留，修大小写与字体 | 资源可用 |
| `design/*.png` | 保留 | 唯一验收标准 |
| `test_script.py` | 删除 | 第三方 demo |
