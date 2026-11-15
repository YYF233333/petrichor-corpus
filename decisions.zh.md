# 决策索引

本索引把语言规范中有语料依据的规则与调查对应起来。规则链接到主仓库中的现行规范，依据链接到本仓库的调查。决定提交是主仓库中写下该规则的提交。每份调查记录它所评估的设计，现行规则可能与调查当时所测的不同。

原有数字仍对应原调查。v2 链接补充新观测与反例。规则和决定提交保持原样。

## 1. 概述

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§1.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#12-与-gdscript-的关系) 可还原规则 | [第二次纸面迁移](surveys/paper-migration-2.md)：230 处修改中 197 处是机械的 | [bd35e33](https://github.com/YYF233333/Petrichor/commit/bd35e33f9bab4b507db0667e58392176feea5da3) |
| [§1.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#13-交付形态) 以 GDExtension 交付 | [暗坑清单](surveys/pitfalls.md)：没有只有引擎模块能修复的条目 | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 2. 词法与表层语法

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§2.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#21-文件与类) `preload` 脚本得到它的类 | [语料计数](surveys/corpus-counts.md)：以字面量路径 `preload` 的 `.gd` 文件；[v2计数](surveys/v2-rerun.md#零散计数) | [5d646d0](https://github.com/YYF233333/Petrichor/commit/5d646d0b346f0931449ddc673c7fa73697ba8acb) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) 新增的关键字是上下文关键字 | [语料计数](surveys/corpus-counts.md)：新增的关键字用作名字；[v2计数](surveys/v2-rerun.md#零散计数) | [78bd106](https://github.com/YYF233333/Petrichor/commit/78bd10678d78572a7b57034b28cb988ed8845970) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) `null` 是 `None` 的别名 | [语料计数](surveys/corpus-counts.md)：`null` 字面量；[v2计数](surveys/v2-rerun.md#零散计数) | [4cbbb67](https://github.com/YYF233333/Petrichor/commit/4cbbb67fc6cd92bdc6e4da09ed99c155999abe9a) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) 前缀 `!` 是逻辑非 | [语料计数](surveys/corpus-counts.md)：前缀 `!` 与 `not`；[v2计数](surveys/v2-rerun.md#零散计数) | [e2113f5](https://github.com/YYF233333/Petrichor/commit/e2113f51239f4e2f5364d01fab757805ab43c856) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) 单引号和双引号字符串不能跨行 | [语料计数](surveys/corpus-counts.md)：引号中含换行的字符串；[v2计数](surveys/v2-rerun.md#零散计数) | [200838a](https://github.com/YYF233333/Petrichor/commit/200838ab84e3eb5665060ff5d51942d55b9e968a) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) 以 `###` 开头的注释不是文档 | [语料计数](surveys/corpus-counts.md)：紧贴声明上方的 `##` 注释；[v2计数](surveys/v2-rerun.md#零散计数) | [c99af6f](https://github.com/YYF233333/Petrichor/commit/c99af6f5f137fdbc6ca2b9b652014652fea53e4d) |
| [§2.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#23-注解) `@tool` 属于第一版，规则【待定】 | [语料计数](surveys/corpus-counts.md)：含 `@tool` 的文件；[v2计数](surveys/v2-rerun.md#零散计数) | [2dc083f](https://github.com/YYF233333/Petrichor/commit/2dc083f834468786be400fe61a4bdc0cfac1259f) |
| [§2.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#24-声明的写法) `pub` 是关键字，不用 `@public` 注解 | [成员可见性调查](surveys/member-visibility.md)：`pub` 每千行至少 22 个；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [6d181d3](https://github.com/YYF233333/Petrichor/commit/6d181d366ce2ddd655ae90966d514da9e73a5e6b) |

## 3. 类型

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§3.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#32-数值) 没有窄整数类型 | [第一次纸面迁移](surveys/paper-migration.md)：`int`／`float` 不是类型，成本最大 | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§3.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#33-对象与可空) 经 `T?` 读到已释放的对象时为 `None` | [语料计数](surveys/corpus-counts.md)：`is_instance_valid(...)`；[暗坑清单](surveys/pitfalls.md)：G-07、G-08；[v2计数](surveys/v2-rerun.md#零散计数) | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |
| [§3.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#33-对象与可空) 方法运行中自身被释放后，访问成员是程序错误；自身上的 `free()`、`set_script()` 不报编译错误 | [语料计数](surveys/corpus-counts.md)：在自身上的 `free()` 与 `set_script(...)`；[v2计数](surveys/v2-rerun.md#零散计数) | [c700ebd](https://github.com/YYF233333/Petrichor/commit/c700ebd919161c5d0ebb24710f707c04ca044202) |
| [§3.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#34-option) 没有 `!`、`??`、`?.` 运算符 | [语料计数](surveys/corpus-counts.md)：前缀 `!` 与 `not`；[v2计数](surveys/v2-rerun.md#零散计数) | [5a10b25](https://github.com/YYF233333/Petrichor/commit/5a10b2505910c41390679f6cfbca82330cb3a356) |
| [§3.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#37-enum) `int` 只能显式转为 enum；enum 名作带类型的 Dictionary；没有值 0 的 enum 必须赋值 | [语料计数](surveys/corpus-counts.md)：不带载荷的 enum；[v2计数](surveys/v2-rerun.md#零散计数) | [aa1fea0](https://github.com/YYF233333/Petrichor/commit/aa1fea0061380e44e0712382e1d8592eacff7919) |
| [§3.8](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#38-容器) `pop_at(i)` 返回 `T`，越界是程序错误 | [语料计数](surveys/corpus-counts.md)：`pop_at`、`pop_back` 与 `pop_front`；[v2计数](surveys/v2-rerun.md#零散计数) | [a2d12e3](https://github.com/YYF233333/Petrichor/commit/a2d12e3d9e35e599141ed102784843c38a46966f) |
| [§3.9](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#39-接口) 名义接口表达不同引擎基类的共同能力；第一版没有带状态的 mixin | [跨分支重复调查](surveys/cross-branch-duplication.md)：353 行中 185 行可用组合或静态函数消除；[第一次纸面迁移](surveys/paper-migration.md)：Brick 与 Enemy 的共同能力（C-trait）；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§3.9](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#39-接口) 继承来的引擎属性可满足接口的属性要求 | [第二次纸面迁移](surveys/paper-migration-2.md)：owner 要求（S14） | [d17283a](https://github.com/YYF233333/Petrichor/commit/d17283a39bce2e1172e79bad5c3996ad41955138) |
| [§3.11](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#311-函数类型与-callable) 给捕获的变量赋值是编译错误；lambda 参数不带默认值 | [语料计数](surveys/corpus-counts.md)：命名的、带默认值的、给捕获赋值的 lambda；[v2计数](surveys/v2-rerun.md#零散计数) | [d449489](https://github.com/YYF233333/Petrichor/commit/d449489ec33b936dfed5936a35a7ae1676a462ad) |
| [§3.11](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#311-函数类型与-callable) 引擎调用的位置接受 `async` 函数 | [语料计数](surveys/corpus-counts.md)：作为值使用的协程方法；[v2计数](surveys/v2-rerun.md#零散计数) | [6d66a0f](https://github.com/YYF233333/Petrichor/commit/6d66a0fc6448380829cfb782df2ac98e68141b39) |
| [§3.12](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#312-弱引用) 【已知限制】第一版没有带类型的弱引用 | [语料计数](surveys/corpus-counts.md)：弱引用；[v2计数](surveys/v2-rerun.md#零散计数) | [43c5a04](https://github.com/YYF233333/Petrichor/commit/43c5a04b2d5b49d560726cc8b48b1b784042589a) |

## 4. 声明

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§4.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#41-类与继承) 带状态的共同基类用 `@abstract` | [语料计数](surveys/corpus-counts.md)：`@abstract` 类和方法；[跨分支重复调查](surveys/cross-branch-duplication.md)：继承本可消除的重复；[v2计数](surveys/v2-rerun.md#零散计数)；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [2357608](https://github.com/YYF233333/Petrichor/commit/2357608268e4cc7520cc5e3a88cad4fe27c2b0f1) |
| [§4.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#41-类与继承) 裸名可指所继承引擎类的常量 | [实现覆盖调查](surveys/implementation-coverage.md)：4.9% 的文件以裸名使用引擎类的常量；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [9f1f1a3](https://github.com/YYF233333/Petrichor/commit/9f1f1a390474c848c22000c36c4e0bd1e36fd2b1) |
| [§4.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#41-类与继承) 内部类的写法与名字查找 | [语料计数](surveys/corpus-counts.md)：内部类；[v2计数](surveys/v2-rerun.md#零散计数) | [99cdaf5](https://github.com/YYF233333/Petrichor/commit/99cdaf527908700eea7209a84d19b08c5b6668ef) |
| [§4.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#42-可见性) 子类可读写、调用和覆盖不带 `pub` 的成员 | [成员可见性调查](surveys/member-visibility.md)：只被子类使用的成员；[第二次纸面迁移](surveys/paper-migration-2.md)：102 处 `pub` 中有 29 处只为子类；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [09e9d16](https://github.com/YYF233333/Petrichor/commit/09e9d16c9eb4797b8c15604f74297e7f4ff27c41) |
| [§4.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#44-属性访问器) setter 和 getter 不能是协程 | [属性访问器调查](surveys/property-accessors.md)：30 个 setter 含 `await`；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§4.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#45-常量) 编译器求出标量常量，引擎类型等在类加载时求值 | [常量表达式调查](surveys/constant-expressions.md)：3,094 个常量中需引擎求值的 33 个；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [63a88c4](https://github.com/YYF233333/Petrichor/commit/63a88c436da7fd6d489f150ac8b772e2f59b58b0) |
| [§4.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#46-函数) 覆盖时可省略参数和返回类型 | [第二次纸面迁移](surveys/paper-migration-2.md)：引擎虚函数覆盖处的 6 处标注（S5） | [ed5f607](https://github.com/YYF233333/Petrichor/commit/ed5f60765b3e71e5bfc29408e2403d951b978628) |
| [§4.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#46-函数) 剩余参数，可写元素类型 | [语料计数](surveys/corpus-counts.md)：剩余参数 `...args`；[v2计数](surveys/v2-rerun.md#零散计数) | [2357608](https://github.com/YYF233333/Petrichor/commit/2357608268e4cc7520cc5e3a88cad4fe27c2b0f1) |
| [§4.8](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#48-静态成员) 静态成员沿用 GDScript 的写法和时机；无默认值的类型须有初始化式 | [语料计数](surveys/corpus-counts.md)：`static var` 与 `_static_init`；[v2计数](surveys/v2-rerun.md#零散计数) | [13a47dd](https://github.com/YYF233333/Petrichor/commit/13a47dd1b74d59a9429aa9288b053f19c6b947b8) |

## 5. 表达式与语句

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§5.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#51-运算) 给 String 的字符赋值是编译错误 | [语料计数](surveys/corpus-counts.md)：给 String 的字符赋值；[v2计数](surveys/v2-rerun.md#零散计数) | [fec61d5](https://github.com/YYF233333/Petrichor/commit/fec61d59145ac09d5836977b4e41afcf39f3c3d3) |
| [§5.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#53-转换) 必须成功的向下转型写作 `(x as T).unwrap()` | [第二次纸面迁移](surveys/paper-migration-2.md)：16 处 `(x as T).unwrap()` | [2a08bde](https://github.com/YYF233333/Petrichor/commit/2a08bdeca439283cf9a0c22c3dbead9bbb458995) |
| [§5.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#54-收窄) 局部变量和参数收窄，成员变量不收窄 | [第一次纸面迁移](surveys/paper-migration.md)：`is` 之后使用成员（C-is）；[第二次纸面迁移](surveys/paper-migration-2.md)：因成员不收窄而新增的局部变量 | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§5.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#57-循环) 类定义 `_iter_init`、`_iter_next`、`_iter_get` 时可遍历其对象 | [实现覆盖调查](surveys/implementation-coverage.md)：定义 `_iter_init` 的类为 0；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [f7de513](https://github.com/YYF233333/Petrichor/commit/f7de513616434963849f8515f031b61e08f8844d) |

## 6. 初始化与生命周期

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§6.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#62-必须赋值的成员) `Node` 和 `Resource` 的 `_init` 可带参数；经无参途径附加有必填参数的脚本是程序错误 | [语料计数](surveys/corpus-counts.md)：自身的 `_init` 带参数的脚本；[暗坑清单](surveys/pitfalls.md)：G-02；[v2计数](surveys/v2-rerun.md#零散计数) | [57aa767](https://github.com/YYF233333/Petrichor/commit/57aa767c919481e5f533fde92274fb354af559fb) |
| [§6.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#62-必须赋值的成员) autoload 引用场景节点的成员写作 `T?` | [语料计数](surveys/corpus-counts.md)：在 `_ready` 中把节点登记到 autoload 成员上；[第二次纸面迁移](surveys/paper-migration-2.md)：autoload 持有场景节点的引用；[v2计数](surveys/v2-rerun.md#零散计数) | [c36ac66](https://github.com/YYF233333/Petrichor/commit/c36ac6636e4d347f948d9ab072bf05b8c4e916f2) |
| [§6.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#63-onready) `@onready` 沿用 GDScript 的时机，直接误用报编译错误 | [暗坑清单](surveys/pitfalls.md)：G-04 | [2b5f53f](https://github.com/YYF233333/Petrichor/commit/2b5f53fefaebeb60a6e655364b5f4eed22182c12) |
| [§6.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#64-就绪顺序) 子节点先于父节点就绪；读到父节点未初始化的成员是程序错误 | [暗坑清单](surveys/pitfalls.md)：G-03、G-05 | [2b5f53f](https://github.com/YYF233333/Petrichor/commit/2b5f53fefaebeb60a6e655364b5f4eed22182c12) |
| [§6.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#64-就绪顺序) 由祖先赋值的必须赋值成员在 owner 发出 `ready` 时检查 | [语料计数](surveys/corpus-counts.md)：节点的脚本给下方节点的脚本成员赋值；[v2计数](surveys/v2-rerun.md#零散计数) | [c36ac66](https://github.com/YYF233333/Petrichor/commit/c36ac6636e4d347f948d9ab072bf05b8c4e916f2) |
| [§6.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#65-就绪前的-setter) setter 立即执行，其中写 `await ready` 报编译错误 | [属性访问器调查](surveys/property-accessors.md)：25 个 setter 用 `await ready`；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [568c9f8](https://github.com/YYF233333/Petrichor/commit/568c9f89688ae5e9a1a322f2d0f3022803e51b1d) |
| [§6.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#66-析构) 析构不新增语法 | [语料计数](surveys/corpus-counts.md)：`NOTIFICATION_PREDELETE`；[暗坑清单](surveys/pitfalls.md)：G-09；[v2计数](surveys/v2-rerun.md#零散计数) | [7cceff9](https://github.com/YYF233333/Petrichor/commit/7cceff994a49bca44857bbfbd38d6844e313d841) |
| [§6.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#67-引用环与泄漏) 对明显的引用环和泄漏给出警告 | [暗坑清单](surveys/pitfalls.md)：G-10 | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |

## 7. 场景模型

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§7.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#71-节点定型) 按脚本所在的全部场景结构为 `$X` 定型 | [场景结构调查](surveys/scene-structures.md)：字面路径在不同结构中从未指向不同类型；[第一次纸面迁移](surveys/paper-migration.md)：`$X` 没有期望类型时为 Node（C-scene）；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§7.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#72-场景之间结构不同的情况) 模板场景缺的节点按使用方式检查；可选节点用 `get_node_or_null` | [场景结构调查](surveys/scene-structures.md)：缺失集中在可选节点和模板场景；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [af3e112](https://github.com/YYF233333/Petrichor/commit/af3e112f40a9f64977808f78d6523f96af7ddf85) |
| [§7.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#73-向上访问) `/root/X` 改用 autoload 名；父节点和 owner 用 `@parent(T)`、`@owner(T)` 声明 | [场景结构调查](surveys/scene-structures.md)：挂载场景子树之外的访问；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§7.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#73-向上访问) 未声明时 `get_parent()` 和 `owner` 为 `Node?` | [语料计数](surveys/corpus-counts.md)：自身的 `get_parent()` 与 `owner`；[v2计数](surveys/v2-rerun.md#零散计数) | [d7ed2c9](https://github.com/YYF233333/Petrichor/commit/d7ed2c94dd0f32e39fbcd58cc2f3fb8d906bfb26) |
| [§7.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#73-向上访问) `@owner(T)` 在每次读取时检查，不在移动节点时检查 | [第二次纸面迁移](surveys/paper-migration-2.md)：DeathComponent 移出 owner 的子树 | [d17283a](https://github.com/YYF233333/Petrichor/commit/d17283a39bce2e1172e79bad5c3996ad41955138) |
| [§7.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#75-必须赋值的导出) 必须赋值的导出按场景的使用方式检查 | [第二次纸面迁移](surveys/paper-migration-2.md)：子场景中必须赋值的导出成员（S6） | [ee3e425](https://github.com/YYF233333/Petrichor/commit/ee3e42540cbf032e01eecb61088f70f643187f8c) |
| [§7.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#76-资源共享) 写已知共享的资源时给出警告 | [暗坑清单](surveys/pitfalls.md)：G-19、G-20 | [7cceff9](https://github.com/YYF233333/Petrichor/commit/7cceff994a49bca44857bbfbd38d6844e313d841) |
| [§7.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#76-资源共享) `preload`、导出场景与资源之间的引用环是编译错误 | [语料计数](surveys/corpus-counts.md)：加载成环；[暗坑清单](surveys/pitfalls.md)：G-34；[v2计数](surveys/v2-rerun.md#零散计数) | [7cceff9](https://github.com/YYF233333/Petrichor/commit/7cceff994a49bca44857bbfbd38d6844e313d841) |

## 8. 错误

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§8.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#83-断言) `assert` 在 release 构建中移除 | [语料计数](surveys/corpus-counts.md)：`assert(...)` 语句；[v2计数](surveys/v2-rerun.md#零散计数) | [804b059](https://github.com/YYF233333/Petrichor/commit/804b0599ad3891f55ae965fa33ff075f8404b8bb) |
| [§8.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#83-断言) 断言的消息只在失败时求值 | [语料计数](surveys/corpus-counts.md)：`assert(...)` 语句的消息；[v2计数](surveys/v2-rerun.md#零散计数) | [545908b](https://github.com/YYF233333/Petrichor/commit/545908ba3b4380665471bd466c02eab909a3fd6a) |

## 9. 协程

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§9.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#91-async-与-task) 含 `await` 的 lambda 也写 `async func` | [语料计数](surveys/corpus-counts.md)：含 await 的 lambda；[v2计数](surveys/v2-rerun.md#零散计数) | [6d66a0f](https://github.com/YYF233333/Petrichor/commit/6d66a0fc6448380829cfb782df2ac98e68141b39) |
| [§9.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#95-组合与重入) `Task.delay` 按引擎的默认值计时，不需要节点在树中 | [语料计数](surveys/corpus-counts.md)：`create_timer(...)` 的调用；[v2计数](surveys/v2-rerun.md#零散计数) | [4877578](https://github.com/YYF233333/Petrichor/commit/48775782ef2ca38c2856a9a0e003d4a68bc3d178) |
| [§9.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#95-组合与重入) 重入无自动策略，经句柄取消旧调用 | [暗坑清单](surveys/pitfalls.md)：G-12、G-13 | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |
| [§9.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#96-await-信号) 多参信号只能作语句 `await` | [await 信号结果调查](surveys/await-signal-results.md)：1,356 个 await 中只有 1 个使用多参数信号的结果；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [f7c4e94](https://github.com/YYF233333/Petrichor/commit/f7c4e942b352dca3fa0d9da4fffc79703f7292cb) |
| [§9.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#96-await-信号) 签名未知的 `Signal` 作值 `await` 得 `Variant` | [await 信号结果调查](surveys/await-signal-results.md)：唯一的使用是签名未知的 C# 信号；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [f7371c1](https://github.com/YYF233333/Petrichor/commit/f7371c1c05a5bea125d0e55b084e6dd51f355936) |
| [§9.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#97-对象释放与挂起的协程) 所属对象释放时协程静默取消；被等待对象释放时等待方报程序错误 | [暗坑清单](surveys/pitfalls.md)：G-11 | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |
| [§9.8](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#98-跨语言-await) 跨语言 `await` 两个方向都支持 | [第一次纸面迁移](surveys/paper-migration.md)：跨语言协程（A7） | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 10. 引擎边界

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§10.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#102-引擎-api-中对象的可空性) 按高频 API 审核引擎 API 中对象的可空性 | [语料计数](surveys/corpus-counts.md)：对象经过的引擎 API；[第一次纸面迁移](surveys/paper-migration.md)：只在出错时返回 null 的接口（A2）；[v2计数](surveys/v2-rerun.md#零散计数) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) 引擎已导出的约束直接使用 | [第一次纸面迁移](surveys/paper-migration.md)：`RequiredResult` 标注（A1） | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) `Variant` 数学工具函数按同类型实参返回该类型 | [第一次纸面迁移](surveys/paper-migration.md)：Variant 数学工具函数（A3） | [f7c4e94](https://github.com/YYF233333/Petrichor/commit/f7c4e942b352dca3fa0d9da4fffc79703f7292cb) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) 以字面量类名过滤的引擎 API 按该类定型 | [第二次纸面迁移](surveys/paper-migration-2.md)：`find_children` 等的向下转型 | [2a08bde](https://github.com/YYF233333/Petrichor/commit/2a08bdeca439283cf9a0c22c3dbead9bbb458995) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) 另加返回 `Result` 的 `try_` 版本，原 API 不变 | [语料计数](surveys/corpus-counts.md)：失败时返回空值的引擎 API；[v2计数](surveys/v2-rerun.md#零散计数) | [8e6a7d7](https://github.com/YYF233333/Petrichor/commit/8e6a7d7cf83ad8097b5eca1b8c57fa395395f9ed) |
| [§10.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#104-字符串形式的成员名) 指向不带 `pub` 的成员的字面量名字报编译错误 | [按名访问调查](surveys/by-name-access.md)：代码中指向本脚本的字面量名字；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [e49da5b](https://github.com/YYF233333/Petrichor/commit/e49da5b354204bce6f42541134b73e7e5d200bd6) |
| [§10.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#105-反射暴露的成员) 按名反射只能访问 `pub` 成员；引擎按名访问的成员须带 `pub` | [按名访问调查](surveys/by-name-access.md)：严格可见性下要补的 `pub`；[v2专项复跑](surveys/v2-rerun.md#专项调查) | [e49da5b](https://github.com/YYF233333/Petrichor/commit/e49da5b354204bce6f42541134b73e7e5d200bd6) |
| [§10.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#105-反射暴露的成员) 读写引擎属性不经 `_get`、`_set` | [语料计数](surveys/corpus-counts.md)：名为 `_get`、`_set` 的方法；[v2计数](surveys/v2-rerun.md#零散计数) | [d3d551d](https://github.com/YYF233333/Petrichor/commit/d3d551d29c4c1b5441117333a6a12524d0c3b4aa) |

## 11. 与 GDScript 和 C# 共存

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§11.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#111-其他语言的类的静态视图) 经反射看到其他语言的类和 autoload | [第一次纸面迁移](surveys/paper-migration.md)：GDScript 类和 autoload 的静态视图（A6） | [f7c4e94](https://github.com/YYF233333/Petrichor/commit/f7c4e942b352dca3fa0d9da4fffc79703f7292cb) |
| [§11.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#111-其他语言的类的静态视图) autoload 名可写在类型中 | [语料计数](surveys/corpus-counts.md)：写在类型中的 autoload 名；[v2计数](surveys/v2-rerun.md#零散计数) | [7453c75](https://github.com/YYF233333/Petrichor/commit/7453c758d5bae3d0454947c05195612e94f437df) |
| [§11.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#112-继承) 本语言的类不能继承 GDScript 类 | [暗坑清单](surveys/pitfalls.md)：C-17 | [83a737a](https://github.com/YYF233333/Petrichor/commit/83a737a2e8b5d9d2e521085575c5d5cbd3f172a5) |
| [§11.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#112-继承) GDScript 不能继承本语言的类，迁移时连带其子类 | [第二次纸面迁移](surveys/paper-migration-2.md)：Brick 和 Enemy 的 GDScript 子类 | [7f7b9ea](https://github.com/YYF233333/Petrichor/commit/7f7b9ea3dcc96883dfc520cdbc66cc596e96526b) |
| [§11.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#113-跨语言调用与消息) 【已知限制】GDScript 不能调用本语言的静态方法，也不能把其 enum 等用于类型 | [语料计数](surveys/corpus-counts.md)：跨文件的类级访问；[v2计数](surveys/v2-rerun.md#零散计数) | [056b281](https://github.com/YYF233333/Petrichor/commit/056b281605c1cb159aa3a635ff89b25e0c45190e) |
| [§11.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#113-跨语言调用与消息) 与 C# 之间的消息用 struct，按字段名编为 Dictionary | [第一次纸面迁移](surveys/paper-migration.md)：消息字段的转换（A8） | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 12. 运行时

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§12.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#123-线程) 【已知限制】第一版不新增线程 API | [语料计数](surveys/corpus-counts.md)：`Thread.new` 与 `WorkerThreadPool`；[v2计数](surveys/v2-rerun.md#零散计数) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 13. 工具链

| 规则 | 依据 | 决定提交 |
|---|---|---|
| [§13.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#132-第一版的工具) 格式化的排版规则 | [语料计数](surveys/corpus-counts.md)：排版习惯；[v2计数](surveys/v2-rerun.md#零散计数) | [d3f34e1](https://github.com/YYF233333/Petrichor/commit/d3f34e121fe7a17b3851231e4996f17148108510) |
| [§13.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#134-迁移) 迁移类前列出对它做类级访问的 GDScript 文件，并提供一并迁移 | [语料计数](surveys/corpus-counts.md)：跨文件的类级访问；[v2计数](surveys/v2-rerun.md#零散计数) | [87726d5](https://github.com/YYF233333/Petrichor/commit/87726d5e83f57d6da8f7c5c149459e0bc0f7c773) |
