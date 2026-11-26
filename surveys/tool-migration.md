# 调查：迁移工具在三个游戏中留下了什么

**2026-11-24** · 关联：[迁移工具的设计](https://github.com/YYF233333/Petrichor/blob/bbdd797b2d4a55100e96d18984af9ba7e6497d86/docs/architecture.md#66-迁移工具)（Petrichor 提交 `bbdd797` 的架构 §6.6）、[语言规范](https://github.com/YYF233333/Petrichor/blob/bbdd797b2d4a55100e96d18984af9ba7e6497d86/docs/language-spec.zh.md)（同一提交）、[第二次纸面迁移](paper-migration-2.md)

Petrichor 的迁移工具 `pet migrate` 把 Godot 项目的 GDScript 文件转为本语言。
它推断没写的类型，循环应用保持含义的快速修复，再报告留下的编译错误。
本文用它的预演 `pet migrate --dry-run` 迁移 corpus v1 的三个游戏。
问题有两个：留下多少错误；每个错误因为什么留下。
原因主要分三类：
- 工具的设计有意留给人的；
- 等待未定设计问题的；
- 级联的，即一个有错误的声明在每处使用时再报一次。

工具每前进一步，就重跑本调查一次。
文中的章节号（§）指上面所链提交的规范和架构。

## 素材

| 项目 | 提交 | 许可 | 迁移的脚本 | 第一方行数 |
|---|---|---|---:|---:|
| [KenneyNL/Starter-Kit-FPS](https://github.com/KenneyNL/Starter-Kit-FPS) | `185fd23` | MIT | 7 | 451 |
| [guladam/deck_builder_tutorial](https://github.com/guladam/deck_builder_tutorial) | `91b408b` | MIT | 116 | 4,701 |
| [P1X-in/tanks-of-freedom-ii](https://github.com/P1X-in/tanks-of-freedom-ii) | `dbe629e` | MIT | 292 | 24,361 |
| **合计** | | | **415** | **29,513** |

下文简称 FPS、deck 和 tanks。
提交是 [corpus v1 清单](../corpus/v1.json)中固定的提交。
行数沿用[场景结构调查](scene-structures.md#语料)的口径，即第一方 `.gd` 文件的物理行数。
第一方规则取自共用的 [`gdcorpus`](cross-branch-duplication/gdcorpus.py)。
deck 另有 6 个脚本模板，工具不迁移它们，所以不计它们的 129 行。

corpus 的克隆只检出文本文件，没有图片、音频和模型。
所以有些错误只是找不到资源，下文单独计数。
用带资源的完整克隆核对的结果，见“缺少的资源”一节。

## 方法

1. **构建。** Petrichor 提交 `bbdd797` 构建的编辑器库和 `pet` 命令。
2. **引擎。** Godot 4.7.2（提交 `ed1daf0`）的编辑器。
3. **迁移。** `measure.py` 复制语料中的克隆，放入 Petrichor 插件，用 Godot 导入一次。
   - 然后在副本中运行 `pet migrate --dry-run`，保存报告。
   - 预演与真正的迁移走同一条路径，只是不写入（§6.6）。
4. **归类。** `summarize.py` 从报告中取出总计行、各类修复的数目和留下的错误。
   - 报错文字中的名字、类型、路径和数字换成占位符，得到模板。
   - 错误的原因由模板定出。
   - 撤回的槽位在报告中各有一条提示，写明撤回的原因。槽位上的错误按这条提示归类。
   - 归类规则是读过这些错误和所在代码后定的。每个错误按规则机械地归类，没有逐个阅读。

## 结果

### 总体

| | FPS | deck | tanks | 合计 |
|---|---:|---:|---:|---:|
| 迁移的脚本 | 7 | 116 | 292 | 415 |
| 写下的类型 | 6 | 7 | 1,555 | 1,568 |
| 撤回的槽位 | 4 | 0 | 711 | 715 |
| 应用的修复 | 11 | 567 | 1,335 | 1,913 |
| 留下的错误 | 10 | 184 | 2,893 | 3,087 |
| 其中缺少资源 | 0 | 19 | 15 | 34 |
| 每百行的错误 | 2.2 | 3.9 | 11.9 | 10.5 |
| 不计缺少资源 | 2.2 | 3.5 | 11.8 | 10.3 |

FPS 和 deck 的原文大多写了类型，推断只写下 6 个和 7 个。
tanks 几乎没写类型。推断为它写下 1,555 个类型，撤回 711 个。
三个游戏留下的错误中，tanks 占 94%。

### 各步的变化

下表是工具每一步完成时留下的错误，用的是同样的做法和同样导入的副本。
本文在 `bbdd797` 上用新导入的副本重跑，三个数都不变。

| Petrichor 提交 | 这一步 | FPS | deck | tanks |
|---|---|---:|---:|---:|
| `6298e28` | 没有推断的工具 | 27 | 276 | — |
| `f947094` | 不迁移脚本模板；推断关闭 | 27 | 274 | 5,971 |
| `1435228` | 类型推断 | 14 | 263 | 3,550 |
| `c8b4af1` | 收窄撤回的范围；由场景定型的成员；`int` 并入 `float` | 14 | 263 | 3,461 |
| `9c6c5fe` | 接收者出错的调用；没给值的导出写成 `T?`；跨行字符串；autoload 的路径 | 10 | 199 | 3,478 |
| `04d78c6` | `Variant` 的流入不作证据；沿覆盖链补 `async` | 10 | 201 | 3,158 |
| `89a3ff1` | 其他文件读取的 preload 常量；`Variant` 操作数 | 10 | 197 | 3,103 |
| `bbdd797` | 无类型容器的元素；显式的 `null`；转为 packed array | 10 | 184 | 2,893 |
| `9f88bc6` | 只当类型用的 preload 常量；用常量给没有 `class_name` 的类指名 | 10 | 180 | 2,684 |
| `944bf3f` | GDScript 隐式的 `null`；`instantiate()` 处报出的导出；别处声明的错误不撤回槽位；调用的实参不牵连目标 | 9 | 151 | 2,575 |
| `e80c61a` | 循环变量逐个检查元素；含 `await` 的 setter 补 `async`；读出资源文件存的导出值；写宽了的声明改窄，其余写 `as`；祖先在 `_ready` 中的赋值 | 13 | 114 | 2,574 |
| `e4e1a18` | 枚举值作下标；`match` 补 `_: pass`；导出场景写成 `PackedScene[T]`；`float` 进入 `int` | 13 | 100 | 2,569 |
| `a0fea52` | `Array[PackedScene[T]]`；去掉字面量上多余的 `as`；两个根不同的场景取共同基类 | 13 | 98 | 2,566 |
| `edbb11e` | 空数组字面量转为 packed array；经 `T?` 读出后照常检查；值不合时只撤回给出其类型的槽位；`Array[Array]` 的内层类型 | 13 | 88 | 2,517 |
| `fbe4eda` | `emit(null)` 的信号参数写成 `T?`；静态代码中裸写的 `new()` 补上类名 | 13 | 86 | 2,517 |
| `2414062` | `@late`，不再看祖先的赋值；packed array 位置上的数组字面量；`Array(r)`；写宽了的类型取读取处都接受的最宽类 | 13 | 86 | 2,517 |
| `dc96890` | 每处读取都已解包的成员写成 `@late`；`Object` 上按名调用和赋值；`addons/` 下的插件不迁移；场景转为更宽的 `PackedScene` 时留下的导出和 setter 在 `await` 之后才存值的导出写成 `T?` | 11 | 86 | 2,517 |
| `e83317d` | 代码判空的值写成 `T?`；不转换的 `as` 写回原值；`Variant` 上取下标、`in`、条件和迭代出错只牵连给它类型的槽位；期望 enum 处的 `int` 写成 `E(x)`；沿用基类补上的 `preload` 常量；字面量定不出元素类型的变量写成无类型容器；赋了别的类型的局部变量写成 `Variant`；`@owner(T)` | 11 | 86 | 2,505 |

`bbdd797` 之后的十行只重跑了预演，下文各表仍是 `bbdd797` 的。
隐式的 `null` 那一步让更多成员写成 `T?`：deck 应用的修复从 567 个增到 888 个，其中 `.unwrap()` 从 98 个增到 376 个，`Make the type T?` 从 30 个增到 66 个。
`e80c61a` 起工具读出资源文件存的值。稀疏克隆缺图片和模型，这些值读作 `Resource`，所以 FPS 多出 4 个、deck 多出 46 个缺少资源的错误。带资源的 deck 从 70 个降到 55 个，`e4e1a18` 降到 41 个，`a0fea52` 降到 39 个，`edbb11e` 降到 29 个，`fbe4eda` 降到 27 个，`2414062`、`dc96890` 和 `e83317d` 仍是 27 个。

工具出现之前，三个游戏只把 `.gd` 改名为 `.pet`，用 v0.2.1 的 `pet check` 检查。
当时的错误是 69、1,150 和 4,663 个。
那次没有推断和修复，是另一种测量，只作起点。

### 修复

| 修复 | FPS | deck | tanks |
|---|---:|---:|---:|
| `Make it pub` | 5 | 324 | 854 |
| `Write async func` | 0 | 7 | 143 |
| `Reach the autoload by its name` | 0 | 0 | 125 |
| `Write .unwrap()` | 2 | 98 | 111 |
| `Write the truth test` | 2 | 101 | 7 |
| `Write .detach()` | 0 | 4 | 62 |
| `Make the type T?` | 2 | 30 | 2 |
| `Use the method or signal itself` | 0 | 0 | 20 |
| `Write is_instance_valid()` | 0 | 1 | 5 |
| `Write the int arguments as float` | 0 | 1 | 4 |
| `Convert to the packed array` | 0 | 1 | 2 |
| **合计** | **11** | **567** | **1,335** |

修复的名字照录报告。
补 `pub` 占全部修复的 62%。
报告中的 `Write the type` 是写下的类型，不计入修复。

### 留下的错误按原因

括号中是结果文件 `cause` 列的值。

| 原因 | FPS | deck | tanks | 例子 |
|---|---:|---:|---:|---|
| **设计上留给人** | **4** | **21** | **1,448** | |
| 从 `Variant` 转换（`variant`） | 0 | 13 | 794 | [tanks `board.gd:198`](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/board/board.gd#L198) |
| 静态类型缺少所访问的成员（`missing-member`） | 0 | 8 | 98 | [deck `damage_effect.gd:13`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/effects/damage_effect.gd#L13) |
| 槽位：所试的类型通不过检查（`slot-unchecked`） | 4 | 0 | 407 | [FPS `enemy.gd:30`](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/enemy.gd#L30) |
| 槽位：没有流入（`slot-no-inflow`） | 0 | 0 | 149 | [tanks `abilities.gd:59`](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/abilities/abilities.gd#L59) |
| **等待未定问题** | **2** | **98** | **340** | |
| 没有 `class_name` 的类（`no-class-name`） | 0 | 0 | 339 | [tanks `board.gd:76`](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/board/board.gd#L76) |
| 写了类型之处的隐式向下转换（`downcast`） | 0 | 60 | 1 | [deck `sound_player.gd:11`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/global/sound_player.gd#L11) |
| GDScript 隐式的 `null`（`implicit-null`） | 0 | 26 | 0 | [deck `character_stats.gd:17`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/custom_resources/character_stats.gd#L17) |
| 含 `await` 的 setter（`setter-await`） | 0 | 12 | 0 | [deck `mana_ui.gd:16`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/mana_ui.gd#L16) |
| `Object?` 上的按名调用（`object-none`） | 2 | 0 | 0 | [FPS `enemy.gd:68`](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/enemy.gd#L68) |
| **级联**（`cascade`） | **1** | **4** | **1,000** | [tanks `active.gd:1`](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/abilities/hero/active/active.gd#L1) |
| **工具尚未做的改写** | **1** | **21** | **16** | |
| 没补上的 `.unwrap()`（`unwrap`） | 0 | 10 | 3 | [deck `run.gd:156`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/run/run.gd#L156) |
| GDScript 的隐式转换（`conversion`） | 0 | 2 | 13 | [tanks `hero.gd:39`](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/tiles/units/heroes/hero.gd#L39) |
| 导出的场景写成 `PackedScene[T]`（`exported-scene`） | 1 | 3 | 0 | [deck `battle_stats.gd:8`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/custom_resources/battle_stats.gd#L8) |
| 导出改为 `T?` 之后的 setter（`setter-parameter`） | 0 | 4 | 0 | [deck `gold_ui.gd:13`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/gold_ui.gd#L13) |
| 字面量 `null` 流入类型为 `T` 的位置（`null-literal`） | 0 | 2 | 0 | [deck `card_rewards.gd:29`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/card_rewards.gd#L29) |
| **本语言的规则**（`rule`） | **0** | **12** | **72** | [deck `battle.gd:54`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/battle/battle.gd#L54) |
| **信号与函数的参数不符**（`signature`） | **2** | **9** | **2** | [FPS `player.gd:277`](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/player.gd#L277) |
| **缺少的资源**（`missing-resource`） | **0** | **19** | **15** | [deck `battle_reward.gd:6`](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/battle_reward/battle_reward.gd#L6) |
| **合计** | **10** | **184** | **2,893** | |

迁移保持行号，所以例子的行号就是原文的行号。

### 设计上留给人

架构 §6.6 把以下几种留作编译错误，由人选择写法。

**从 `Variant` 转换。**
值是 `Variant` 时，转成什么类型要人判断，工具不写转换（§6.6）。
规范也要求 `Variant` 赋给带类型的位置时显式转换或经 `is` 收窄（规范 §3.14）。
tanks 的 794 个中，取下标 454 个，调用方法 195 个，读属性 29 个。
例如 tanks 遍历无类型的数组 `match_setup.setup`，元素上取下标 `player_setup["side"]`（[board.gd:197-198](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/board/board.gd#L197-L198)）。

**静态类型缺少所访问的成员。**
值的类型是缺这个成员的具体类时，工具先由场景找更准的类型。
找不到时留作编译错误，选项是按名访问或转成具体类（§6.6）。
例如 deck 的 `target` 来自 `Array[Node]`，判断 `target is Enemy or target is Player` 之后调用 `take_damage()`（[damage_effect.gd:8-13](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/effects/damage_effect.gd#L8-L13)）。
多数这类值的类型是原作者写的 `Node`。
例如 tanks 把 `$"/root/Settings"` 存进类型为 `Node` 的成员，再调用 `get_option()`（[relay.gd:16](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scripts/services/relay.gd#L16)、[relay.gd:49](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scripts/services/relay.gd#L49)）。

**撤回的槽位。**
推断写下的类型通不过检查时撤回，槽位留作编译错误（§6.6）。
没有流入的槽位试 `Variant`，通不过时同样撤回。
参数、成员和局部变量在声明处报一个错误，返回值在每个 `return` 处报一个。
- 所试的类型通不过检查：FPS 的 `damage(amount)` 收到 `int` 和 `float`，函数体中有分辨二者的使用，所以 `int` 不并入 `float`（[enemy.gd:30](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/enemy.gd#L30)）。
- tanks 的这类提示有 382 条，其中 287 个槽位只收到 `Variant`。只有 `Variant` 流入的槽位算作没有流入（§6.6），但提示把它们写作通不过检查。
- 没有流入：项目中没有值流入这个槽位，如 tanks 的 `can_intimidate_crew(source)`（[abilities.gd:59](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/abilities/abilities.gd#L59)）。

### 等待未定问题

以下错误的去留取决于尚未决定的设计。
这里只说明问题，不讨论答案。

**没有 `class_name` 的类。**
文件写不出没有名字的类型，这样的槽位留作编译错误（§6.6）。
tanks 的 292 个脚本中只有 15 个有 `class_name`。
其余的类只能经路径引用，如 `extends "res://…"` 和 `preload()`。
- 203 个错误在其他文件读取由场景定型的成员之处，如 `map.camera` 被读 72 次，`ui.picker` 43 次，`ui.radial` 33 次（[board.gd:76](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/board/board.gd#L76)）。
- 136 个在撤回的槽位上，如 `_init(_board)` 的参数（[abilities.gd:4](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/abilities/abilities.gd#L4)）。

Petrichor 的待办中记有一种改写：给这些文件起名（[BACKLOG](https://github.com/YYF233333/Petrichor/blob/bbdd797b2d4a55100e96d18984af9ba7e6497d86/BACKLOG.md)）。

**写了类型之处的隐式向下转换。**
原作者在循环变量、属性或参数上写了较窄的类型，值的静态类型却较宽。
原文照常运行，本语言要求显式转换（规范 §3.14）。
迁移怎样处理这些位置尚未决定。
deck 的 60 个是：
- 带类型的循环变量遍历 `get_children()`，44 个，如 `for player: AudioStreamPlayer in get_children()`（[sound_player.gd:11](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/global/sound_player.gd#L11)）；
- 类型为 `Texture` 的导出赋给 `Texture2D` 的属性，12 个，如 `icon.texture = card.icon`（[card_visuals.gd:18](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/card_visuals.gd#L18)）；
- `create_instance()` 返回的 `Resource` 赋给具体的 resource 类，2 个；
- `get_first_node_in_group()` 的 `Node?` 赋给 `Node2D`，1 个；
- 信号参数 `Node` 传给参数为 `RelicUI` 的函数，1 个。

tanks 的 1 个只在稀疏克隆中出现。

**GDScript 隐式的 `null`。**
GDScript 给没有初始值的变量 `null`。
推断目前不把这个 `null` 算作流入（[BACKLOG](https://github.com/YYF233333/Petrichor/blob/bbdd797b2d4a55100e96d18984af9ba7e6497d86/BACKLOG.md)）。
算作流入时，`_ready` 中赋值的成员成为 `T?`，`int` 计数器成为 `int?`。
不算时成为 `T` 和 `int`，类型为 `T` 的成员就必须赋值（规范 §6.2）。
- tanks 有 128 个没写类型、也没有初始值的变量留作错误。它们已按提示计入其他原因，这里不重复计数。
- deck 的 26 个都是写了类型 `T`、没有初始值的变量。
  - resource 的成员由之后调用的方法赋值，12 个，如 `create_instance()` 给 `var deck: CardPile` 赋值（[character_stats.gd:17](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/custom_resources/character_stats.gd#L17)）；
  - 节点的成员和导出在 `instantiate()` 之后才赋值，12 个，如 [hand.gd:11-15](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/hand.gd#L11-L15)；
  - 局部变量 `var left_neighbour: Room`，2 个（[map_generator.gd:103](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/map/map_generator.gd#L103)）。

就绪后才非空的成员，是架构 §5 列出的冻结之前要定的设计之一。

**含 `await` 的 setter。**
deck 有 12 处在 setter 中 `await ready`，如 [mana_ui.gd:15-16](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/mana_ui.gd#L15-L16)。
setter 不能是协程，所以工具不补 `async`（规范 §4.4）。
现行规范的写法是先存值，在 `is_node_ready()` 为真时同步，再在 `_ready` 中同步一次（规范 §6.5）。
第一版之后 setter 是否自己等待就绪，是未定问题（[BACKLOG](https://github.com/YYF233333/Petrichor/blob/bbdd797b2d4a55100e96d18984af9ba7e6497d86/BACKLOG.md)）。

**`Object?` 上的按名调用。**
FPS 的 `get_collider()` 的结果是 `Object?`。
原文先 `has_method("damage")`，再直接调用 `collider.damage(5)`（[enemy.gd:54](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/enemy.gd#L54)、[enemy.gd:68](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/enemy.gd#L68)）。
工具给前一处补了 `.unwrap()`，后一处留作错误。
值的类型是 `Object` 时，工具把不用返回值的调用改为 `call("名字", ...)`（§6.6）。
值是 `Object?` 时怎样按名访问，尚未决定。
玩家开枪处是同样的写法（[player.gd:204-205](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/player.gd#L204-L205)）。

**其他文件读取 `preload` 的类型。**
规范按资源的内容为 `preload` 定型，而其他文件的检查不读资源（[BACKLOG](https://github.com/YYF233333/Petrichor/blob/bbdd797b2d4a55100e96d18984af9ba7e6497d86/BACKLOG.md)）。
这三个游戏没有因此留下的错误。
deck 在四处读取另一文件中以 `preload` 初始化的三个常量，工具写下了它们的类型。
例如 `card_ui.BASE_STYLEBOX`（[card_base_state.gd:13](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/card_ui/card_states/card_base_state.gd#L13)）。

### 级联

一个声明有错误时，每处使用它的地方再报一个错误。
tanks 的 1,000 个是：
- 使用或覆盖有错误的成员和函数，724 个；
- 继承有错误的基类脚本，157 个，如 [active.gd:1](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/abilities/hero/active/active.gd#L1)；
- 使用返回值撤回了的函数的值，119 个。函数因此没有返回值（[board.gd:146](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/board/board.gd#L146)）。

前两种指向 138 个声明。
最多的是 `base_outcome.gd` 的 `var board`，引出 129 个（[base_outcome.gd:2](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/board/logic/scripting/outcomes/base_outcome.gd#L2)）。
它是没有流入的槽位。
tanks 有错误的文件是 270 个，其中 56 个只有级联的错误。

### 工具尚未做的改写

以下错误有确定的改写，工具还没有做。

**没补上的 `.unwrap()`。**
原文没判空就使用的值，工具补 `.unwrap()`，与 GDScript 在同一处出错（§6.6）。
有些这样的位置没有补上。
例如 `reward_scene` 是 `as BattleReward` 的结果。
第 153、154 行写属性时补了，第 156、157 行调用方法时没有补（[run.gd:152-157](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/run/run.gd#L152-L157)）。

**GDScript 的隐式转换。**
以下赋值 GDScript 隐式转换，规范要求写出转换（规范 §3.14）：
- `int` 赋给 enum，7 个，如 `cast_shadow = 0`（[hero.gd:39](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/tiles/units/heroes/hero.gd#L39)）；
- `float` 赋给 `int`，7 个；
- `[]` 赋给类型为 `PackedStringArray` 的变量，1 个（[card_pile.gd:56](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/custom_resources/card_pile.gd#L56)）。

非空的数组转 packed array 已有修复，这一处是空字面量。

**导出的场景写成 `PackedScene[T]`。**
规范要求导出的场景写出根节点的类型（规范 §7.4）。
工具只在实例缺少所访问的成员时这样改写（§6.6）。
其余的导出留作错误，如 deck 的 `@export var enemies: PackedScene`（[battle_stats.gd:8](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/custom_resources/battle_stats.gd#L8)）和 FPS 的武器模型（[weapon.gd:5](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/scripts/weapon.gd#L5)）。

**导出改为 `T?` 之后的 setter。**
场景没给值的导出，工具改为 `T?`（§6.6）。
它的 setter 的参数仍是 `T`，于是不再合乎 setter 的签名（[gold_ui.gd:4](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/gold_ui.gd#L4)、[gold_ui.gd:13](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/gold_ui.gd#L13)）。

**字面量 `null` 流入类型为 `T` 的位置。**
字面量 `null` 赋给类型为 `T` 的变量或从 `-> T` 返回时，工具把类型改为 `T?`（§6.6）。
以下两处不在其中：
- 作为信号的实参，如 `card_reward_selected.emit(null)`（[card_rewards.gd:29](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/ui/card_rewards.gd#L29)）；
- 赋给另一个对象带 setter 的成员，如 `enemy.current_action = null`（[enemy_handler.gd:32](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/enemy/enemy_handler.gd#L32)）。

### 本语言的规则

以下写法原文能运行，本语言的规则拒绝，要由人改写。
tanks 的 72 个是：
- 容器字面量按元素定型，51 个。
  - 含 `null`、元素类型不同或嵌套的空字面量定不出类型，48 个，如 `bind([1, null])`（[board.gd:167](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/board/board.gd#L167)）；
  - 导出的初始值 `["first", "second"]` 定出 `Array[String]`，场景保存的却是 `float`，3 个（[setting_option_rotating.gd:19](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/ui/menu/settings/setting_option_rotating.gd#L19)）；
- 节点路径在某个使用脚本的场景中不存在，8 个，如 `base_ground.tscn` 没有 `$"mesh"`（[tile.gd:35](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/tiles/tile.gd#L35)）；
- 把类型为 `String` 的值与 `null` 比较，6 个；
- 局部变量改存另一种类型的值，3 个，如 `new_step_no = int(new_step_no)`（[base_edit_action.gd:63-65](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/map_editor/story/stories/types/base_edit_action.gd#L63-L65)）；
- 其余 4 个：两个函数并非每条路径都返回值，`%` 用于 `float`，`is String`。

deck 的 12 个是：
- `match` 没有处理 enum 的全部值，5 个（[battle.gd:54](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/battle/battle.gd#L54)）；
- enum 用作下标，2 个；
- 信号连接到 `unbind()` 返回的 `Callable`，2 个；
- 其余 3 个：含 `null` 的字面量、`[] as Array[Room]`、不经类名调用 `new()`。

### 信号与函数的参数不符

13 个中，9 个是原文中信号的声明、发射和连接彼此不符：
- FPS 的 `signal health_updated` 没有参数，发射时却带一个，所连的函数也接收一个（[player.gd:35](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/player.gd#L35)、[player.gd:277](https://github.com/KenneyNL/Starter-Kit-FPS/blob/185fd2326d74a5cf858cffc616f87cf9696f9cc0/objects/player.gd#L277)）。[第二次纸面迁移](paper-migration-2.md#收益)也报出了这一处；
- deck 的 `card_tooltip_requested(card: Card)` 发射时带两个值，所连的函数也接收两个（[events.gd:9](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/global/events.gd#L9)、[card_ui.gd:66](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/card_ui/card_ui.gd#L66)）；
- deck 连接时用 `bind()` 或 `unbind()` 的结果，`is_connected()` 或 `disconnect()` 时却用原来的方法（[exposed.gd:24-25](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/statuses/exposed.gd#L24-L25)、[wooden_sword.gd:19](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/relics/wooden_sword.gd#L19)）；
- tanks 的 `step_move_requested` 声明两个参数，发射时带三个（[story.gd:9](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/map_editor/story/stories/story.gd#L9)、[story.gd:166](https://github.com/P1X-in/tanks-of-freedom-ii/blob/dbe629ea05691599dde4fd65ab9a13b78a4ccfe1/scenes/map_editor/story/stories/story.gd#L166)）。

其余 4 个来自 deck 对带默认参数的函数调用 `bind()`，如 `show_current_view.bind("Deck")`（[run.gd:148](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/run/run.gd#L148)）。
规范去掉末尾的参数为它定型，而引擎把绑定的实参放在调用方的实参之后（`core/variant/callable_bind.cpp:141-150`，Godot `ed1daf0`）。
所以原文能运行，本语言却拒绝（[BACKLOG](https://github.com/YYF233333/Petrichor/blob/bbdd797b2d4a55100e96d18984af9ba7e6497d86/BACKLOG.md)）。

### 缺少的资源

deck 的 19 个是：
- `preload` 找不到图片，8 个（[battle_reward.gd:6](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/battle_reward/battle_reward.gd#L6)）；
- 场景为导出保存的音频和图片找不到，读出的值只是 `Resource`，11 个。

tanks 的 15 个都是 `preload` 找不到音频。

在同样的提交上用带资源的完整克隆重跑，三个游戏留下 10、171 和 2,875 个错误。
差别不只是这 34 个：
- FPS 的错误相同，修复少一个 `Make the type T?`；
- deck 少了这 19 个，又多了 6 个。图片存在时，`[preload("res://art/….png"), Vector2.ONE]` 的两个元素类型不同，字面量定不出类型（[map_room.gd:9](https://github.com/guladam/deck_builder_tutorial/blob/91b408bc660e9b7389892dd4242a4d76e5bc9e77/scenes/map/map_room.gd#L9)）；
- tanks 少了这 15 个，另少 3 个：两个参数从音频得到流入，一处证书资源有了类型。

## 结论

- 三个游戏共留下 3,087 个错误，每百行 10.5 个，tanks 占 94%。
- 设计上留给人的有 1,473 个，占 48%，其中从 `Variant` 转换 807 个。
- 级联有 1,005 个，占 33%，几乎都在 tanks。它们指向 138 个声明和返回值撤回了的函数。
- 等待未定问题的有 440 个，占 14%。其中没有 `class_name` 的类 339 个，隐式向下转换 61 个，隐式的 `null` 26 个。
- 工具尚未做的改写有 38 个，本语言的规则 84 个，信号与函数的参数不符 13 个，缺少的资源 34 个。
- 信号与函数的参数不符中，9 个是原文的缺陷。

## 局限

- **只有三个游戏。** tanks 的数字主导合计。它几乎没写类型，FPS 和 deck 大多写了。
- **归类是机械的。** 原因按报错文字定出，规则由阅读定。新出现的报错文字须补规则，否则归入 `other`。
- **撤回的原因只到提示为止。** 所试的类型为什么通不过检查，本文不再细分。其中有的源于向下转换、隐式转换和隐式的 `null`。
- **级联只计报告中的错误。** 修好源头的声明后，被它挡住的错误可能出现。
- **每百行的分母** 是迁移的第一方文件的物理行，含空行和注释。

## 复现

本调查需要语料以外的两样输入，所以 `reproduce.py` 不运行它：
- Godot 4.7 的编辑器，本文用 4.7.2（提交 `ed1daf0`）；
- Petrichor 的构建，排成插件的样子：`petrichor.gdextension` 旁有 `bin/`，内有编辑器库和 `pet`。在 Petrichor 仓库中用 `scons` 构建后，`tests/engine/project` 就是这样，本文用提交 `bbdd797`。发布包中的 `addons/petrichor` 也是这样。

```
python fetch.py
python surveys/tool-migration/measure.py <godot> <petrichor> corpus/v1
python surveys/tool-migration/summarize.py corpus/v1 work/tool-migration <Petrichor 提交>
```

`measure.py` 把副本和报告放在 `work/tool-migration/`，git 忽略这个目录。
副本只导入一次，之后重跑只换插件的文件。
tanks 的预演约 75 秒。
`summarize.py` 把结果写入 [`tool-migration/results/`](tool-migration/results/)：
- `summary.tsv`：每个游戏的总计行、行数和每百行的错误；
- `fixes.tsv`：各类修复的数目；
- `templates.tsv`：按原因和模板计数，附第一个位置；
- `causes.tsv`：按原因计数；
- `errors-<游戏>.tsv`：每个留下的错误的文件、行、原因和模板。

工具前进一步后，用新的构建运行这两条命令，并在“各步的变化”中加一行。

带资源的核对用完整克隆。
在一个空目录中，按 v1 清单的提交完整克隆这三个仓库。
再以这个目录代替 `corpus/v1`，运行这两个脚本。
