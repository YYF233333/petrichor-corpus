# 调查：迁移再转回的文件与原文差在哪里

**2026-11-27** · 关联：[迁移工具的设计](https://github.com/YYF233333/Petrichor/blob/08a6a2f/docs/architecture.md#66-迁移工具)（Petrichor 提交 `08a6a2f` 的架构 §6.6）、[迁移工具在三个游戏中留下了什么](tool-migration.md)

Petrichor 0.3 的迁移工具是双向的。
`pet migrate` 把 GDScript 转为本语言，`pet migrate --reverse` 再转回 GDScript。
0.3 的验收之一：corpus 中能迁移的文件迁移再转回后，与原文只差已知的改写（架构 §5 第 11 步）。
本文在 corpus v1 上逐个文件检查这一条。
问题有三个：
- 多少文件能转回；
- 转回的文件与原文差在哪里；
- 哪些差异是反向转换的缺陷。

## 素材

corpus v1 的 20 个仓库中，`config_version=5` 的 Godot 4 项目共 157 个。
其中 `godot-demo-projects` 占 139 个，其余仓库各一个。
有脚本迁移的项目 146 个。
提交是 [corpus v1 清单](../corpus/v1.json)中固定的提交。
克隆只检出文本文件，所以缺资源的错误照样留下（[tool-migration](tool-migration.md#缺少的资源)）。

## 方法

1. **构建。** Petrichor 构建的编辑器库和 `pet`，提交见下文。
2. **引擎。** Godot 4.7.2（提交 `ed1daf0`）的优化 dev 编辑器。
3. **往返。** `round-trip/measure.py` 复用 `tool-migration/measure.py` 的准备步骤，每个项目复制、放入插件并导入一次。
   - 然后在新副本中依次运行 `pet migrate --allow-dirty` 和 `pet migrate --reverse --allow-dirty`，保存两份报告。
   - 两条命令都不给路径，即整个项目。`res://addons/` 下的插件不迁移（§6.6）。
4. **比较。** `round-trip/summarize.py` 把每个转回的文件与语料中的原文比较。
   - 字节相同的算相同。
   - 其余的先在两边施加 §6.6 列出的已知改写：三引号、`_: pass`、autoload 的名字、`return null`。
   - 之后仍不同的部分按行取差异块，每块再按词法单元取差异，按规则命名。规则见脚本中的 `RULES`。
5. **拒绝的原因。** 由反向报告读出：编译错误、所在继承树中有文件留下、对留下文件的类级访问。

构建分两批：
- `godot-demo-projects` 的 139 个项目和另外 6 个仓库用 `ecc023f` 的构建，后 20 个已含 `549b18b` 中复核的修复；
- 其余 12 个项目用 `549b18b` 加上 `08a6a2f` 的反向修复重跑。

两批的反向转换只差 `549b18b` 和 `08a6a2f` 的修复。
它们只改复核与拒绝：复核不再误报 `extends "b.pet"`，另拒绝三种 GDScript 不接受的写法。
前者在第一批中没有报出缺陷。
后三种从 GDScript 迁来的代码写不出，因为原文在 GDScript 中能编译。
两批的正向迁移另差 `49b6da7` 一处：转为带类型 `Array` 的 `as` 写回原数组，第一批没有重跑。
第一次全部运行用时 23 分钟，三个项目并行。

## 结果

### 总体

| | 文件 |
|---|---:|
| 迁移的 | 1,755 |
| 未转回的 | 1,232 |
| 转回的 | 523 |
| 其中与原文相同 | 346 |
| 其中只差已知改写 | 113 |
| 其中另有差异 | 64 |

转回的文件中，88% 与原文相同或只差已知改写。
只差已知改写的 113 个中，所差的都是本次补进 §6.6 的五种和 `49b6da7` 加入的一种（见下文）。
原有四种已知改写在转回的文件中没有单独出现，它们所在的文件都另有差异或未转回。

主要项目：

| 项目 | 迁移 | 转回 | 相同 | 只差已知改写 | 另有差异 |
|---|---:|---:|---:|---:|---:|
| godot-tiny-mmo | 405 | 76 | 61 | 11 | 4 |
| tanks-of-freedom-ii | 292 | 28 | 5 | 18 | 5 |
| Pixelorama | 203 | 14 | 13 | 0 | 1 |
| deck_builder_tutorial | 116 | 85 | 39 | 33 | 13 |
| godot-open-rts | 110 | 10 | 8 | 1 | 1 |
| Ring | 66 | 29 | 18 | 8 | 3 |

每个项目的数字在 [`round-trip/results/summary.tsv`](round-trip/results/summary.tsv)。

### 未转回的原因

| 原因 | 文件 |
|---|---:|
| 迁移留下的编译错误 | 692 |
| 继承树中有文件留下 | 528 |
| 对留下文件的类级访问 | 12 |

反向转换拒绝有编译错误的文件（§6.6）。
迁移留下的错误由 [tool-migration](tool-migration.md) 调查，本文不再细分。
没有文件因为用到 GDScript 没有的特性或“尚未转换”的写法留下：迁移不写下这些写法。
反向的复核没有报出缺陷。

### 差异按规则

一块差异可以同时符合几条规则，表中按组合计数。
“已知”一列标出 `08a6a2f` 的 §6.6 中的已知改写：本次补进的五种，以及 `49b6da7` 加入的带类型 `Array` 的 `as`。

| 规则 | 已知 | 差异块 | 文件 | 例子 |
|---|---|---:|---:|---|
| 真值判断写成比较 | 是 | 131 | 81 | `if direction:` 转回 `if direction != 0:` |
| 推断写下的类型 | 是 | 81 | 50 | `func update_score(score):` 转回 `func update_score(score: int):` |
| 隐式向下转换写下的 `as` | 否 | 67 | 43 | `var texture_rect: TextureRect = get_parent()` 转回 `= (get_parent() as TextureRect)` |
| 修复写下的转换 | 是 | 25 | 19 | `ceil(v)` 转回 `int(ceil(v))` |
| `as` 与真值判断 | 否 | 10 | 8 | `while get_child_count():` 转回 `!= 0`，下一行补上 `as Label` |
| `as` 外加的括号 | 否 | 7 | 5 | `return ResourceLoader.load(SAVE_PATH) as SaveGame` 转回 `return (… as SaveGame)` |
| 补上的 `preload` 常量 | 否 | 7 | 7 | 补上 `const Mob = preload("res://mob.pet")` |
| 真值判断与类型 | 是 | 5 | 5 | |
| 改用方法或信号本身 | 是 | 4 | 3 | `emit_signal("buy_pressed", id)` 转回 `buy_pressed.emit(id)` |
| `preload` 常量与类型 | 否 | 2 | 2 | |
| `as` 与类型 | 否 | 1 | 1 | |
| 带类型 `Array` 的 `as` 写回原数组，与类型 | 是 | 8 | 1 | `for drop_tres in (drop_tres_pool as Array[Drop_Info]):` 转回 `for drop_tres: Drop_Info in drop_tres_pool:` |
| 带类型 `Array` 的 `as` 写回原数组 | 是 | 2 | 1 | `for level_name in (level_name_pool as Array[String]):` 转回 `for level_name in level_name_pool:` |
| 改窄的类型 | 是 | 1 | 1 | `-> Resource` 转回 `-> CharacterStats` |
| 其他 | 否 | 1 | 1 | `call_deferred("init_level")` 转回 `init_level.call_deferred()` |

例子取自 [`round-trip/results/rules.tsv`](round-trip/results/rules.tsv) 的第一处。
“其他”的一处是改用方法本身，只是词法单元对齐不同。

## 发现

### 补进已知改写的五种

这五种是迁移的修复，转回后仍是含义相同的 GDScript。
反向转换只读 `.pet` 文件，不读迁移的记录（§6.6）。
所以它分不出哪些写法是迁移补上的，也就不改回原样。
- **推断写下的类型。** 它们都经检查器核验，GDScript 照样接受。
- **改窄的类型。** 理由同上。
- **真值判断写成的比较、`is_empty()` 和 `is_instance_valid()`。** GDScript 的真值是 `is_zero()` 的反面，对象按存活判断，与 `!= null` 相同（Godot `ed1daf0` 的 `core/variant/variant.cpp:878-953`、`core/variant/variant_op.cpp:1120-1122`）。
- **修复写下的转换。** 如 `int(x)`、`float(x)`、packed array 的构造，以及写成 `6.0` 的 `6`。
- **改用方法或信号本身。** 如 `call_deferred()` 和 `emit()` 的新写法。

Petrichor 在 `549b18b` 中把它们写进 §6.6 的已知改写。

### 留待决定的两种

**隐式向下转换写下的 `as`。**
迁移在写了类型的位置把较宽的值写成 `(x as T).unwrap()`（§6.6）。
转回时去掉 `.unwrap()`，留下 `(x as T)`。
原文在调试构建中给类不符的赋值报错，转回后得 `null`（`modules/gdscript/gdscript_vm.cpp:1533-1625`）。
所以它不只是写法不同，出错时的行为也不同。
涉及 `as` 的差异块共 85 个，是数量最多的未知差异。
例如 [Pixelorama `RowColumnLines.gd:15`](https://github.com/Orama-Interactive/Pixelorama/blob/38a8b03eafc56a2815c42ff53ef3f61db7cf432b/src/UI/Dialogs/HelperScripts/RowColumnLines.gd#L15)。
一种反向规则：值进入类型为 `T` 的位置时，把 `(x as T).unwrap()` 写回 `x`，GDScript 在该处照常检查。

**补上的 `preload` 常量。**
迁移给没有 `class_name` 的类补上 `preload` 常量，用来写类型（§6.6）。
转回后常量留下，GDScript 在类加载时就载入它所指的脚本。
所指文件留在本语言时，常量指向 `.pet` 文件，如 [dodge_the_creeps `main.gd`](https://github.com/godotengine/godot-demo-projects/blob/b761b4cd5718a7118f2c95eb55f181d0a5f004f1/2d/dodge_the_creeps/main.gd)。
共 9 个文件。

### 反向转换的缺陷

本次运行没有报出反向转换的缺陷：复核没有报错，转回的文件没有含义不同的改写。
同一批的语言测试差分运行另找到四处缺陷，已在 `549b18b` 中修复（Petrichor 的 BACKLOG 记有差分运行的结果）。
`08a6a2f` 收窄了其中一处拒绝：`549b18b` 曾误拒 Ring 的一个文件。

## 结论

- 1,755 个迁移的文件中，523 个转回，其余 1,232 个都因迁移留下的编译错误或其继承树留下。
- 转回的 523 个中，346 个与原文相同，113 个只差已知改写，64 个另有差异。
- 另有的差异是两种迁移修复：隐式向下转换写下的 `as` 和补上的 `preload` 常量。前者在出错时改变行为，两者都待定反向规则。
- 本次比较没有发现反向转换写错含义的地方。

## 局限

- **转回的比例取决于迁移。** 有编译错误的文件不转回，所以本文只比较了迁移干净的 30% 文件。
- **规则是机械的。** 差异块按词法单元的模式归类，模式由阅读定。新出现的差异须补规则，否则归入“其他”。
- **`godot-demo-projects` 占项目数的大半。** 它的项目都很小。

## 复现

本调查需要语料以外的两样输入，所以 `reproduce.py` 不运行它：
- Godot 4.7 的编辑器，本文用 4.7.2（提交 `ed1daf0`）；
- Petrichor 的构建，排成插件的样子，同 [tool-migration](tool-migration.md#复现)。本文的两批构建见“方法”。

```
python fetch.py
python surveys/round-trip/measure.py <godot> <petrichor> corpus/v1 --jobs 3
python surveys/round-trip/summarize.py corpus/v1 work/round-trip <Petrichor 提交>
```

`measure.py` 把导入过的副本放在 `work/round-trip/imported/`，每次运行从它复制到 `work/round-trip/run/`。
`summarize.py` 把结果写入 [`round-trip/results/`](round-trip/results/)：
- `summary.tsv`：每个项目迁移、转回、相同、只差已知改写、另有差异和未转回的文件数；
- `refused.tsv`：未转回的原因；
- `rules.tsv`：差异按规则的计数和第一处例子；
- `files.tsv`：每个转回的文件的结果。
