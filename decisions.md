# Decision index

This index maps the rules of the language spec that rest on corpus evidence to the surveys behind them. Rules link to the current spec in the main repository. Evidence links to the surveys in this repository. The decision commit is the main-repository commit that wrote the rule down. Each survey records the design it evaluated, so a current rule may differ from what a survey tested.

## 1. Overview

| Rule | Evidence | Decided in |
|---|---|---|
| [§1.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#12-与-gdscript-的关系) The reversibility rule | [Second paper migration](surveys/paper-migration-2.md): 197 of the 230 changes are mechanical | [bd35e33](https://github.com/YYF233333/Petrichor/commit/bd35e33f9bab4b507db0667e58392176feea5da3) |
| [§1.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#13-交付形态) Delivered as a GDExtension | [Pitfalls catalog](surveys/pitfalls.md): no entry that only an engine module can fix | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 2. Lexical and surface syntax

| Rule | Evidence | Decided in |
|---|---|---|
| [§2.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#21-文件与类) Preloading a script gives its class | [Corpus counts](surveys/corpus-counts.md): `.gd` files preloaded by a literal path | [5d646d0](https://github.com/YYF233333/Petrichor/commit/5d646d0b346f0931449ddc673c7fa73697ba8acb) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) The added keywords are contextual | [Corpus counts](surveys/corpus-counts.md): the added keywords used as names | [78bd106](https://github.com/YYF233333/Petrichor/commit/78bd10678d78572a7b57034b28cb988ed8845970) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) `null` is an alias of `None` | [Corpus counts](surveys/corpus-counts.md): `null` literals | [4cbbb67](https://github.com/YYF233333/Petrichor/commit/4cbbb67fc6cd92bdc6e4da09ed99c155999abe9a) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) Prefix `!` is logical not | [Corpus counts](surveys/corpus-counts.md): prefix `!` and `not` | [e2113f5](https://github.com/YYF233333/Petrichor/commit/e2113f51239f4e2f5364d01fab757805ab43c856) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) Strings in single or double quotes cannot span lines | [Corpus counts](surveys/corpus-counts.md): quoted strings containing line breaks | [200838a](https://github.com/YYF233333/Petrichor/commit/200838ab84e3eb5665060ff5d51942d55b9e968a) |
| [§2.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#22-词法) Comments starting with `###` are not documentation | [Corpus counts](surveys/corpus-counts.md): `##` comments right above declarations | [c99af6f](https://github.com/YYF233333/Petrichor/commit/c99af6f5f137fdbc6ca2b9b652014652fea53e4d) |
| [§2.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#23-注解) `@tool` is in the first version; its rules are [Open] | [Corpus counts](surveys/corpus-counts.md): files with `@tool` | [2dc083f](https://github.com/YYF233333/Petrichor/commit/2dc083f834468786be400fe61a4bdc0cfac1259f) |
| [§2.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#24-声明的写法) `pub` is a keyword, not a `@public` annotation | [Member visibility survey](surveys/member-visibility.md): at least 22 `pub` per thousand lines | [6d181d3](https://github.com/YYF233333/Petrichor/commit/6d181d366ce2ddd655ae90966d514da9e73a5e6b) |

## 3. Types

| Rule | Evidence | Decided in |
|---|---|---|
| [§3.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#32-数值) No narrow integer types | [First paper migration](surveys/paper-migration.md): `int`/`float` not being types, the largest cost | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§3.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#33-对象与可空) A freed object read through `T?` is `None` | [Corpus counts](surveys/corpus-counts.md): `is_instance_valid(...)`; [Pitfalls catalog](surveys/pitfalls.md): G-07, G-08 | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |
| [§3.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#33-对象与可空) Accessing members after `self` is freed mid-method is a program error; `free()` and `set_script()` on self are no compile error | [Corpus counts](surveys/corpus-counts.md): `free()` and `set_script(...)` on self | [c700ebd](https://github.com/YYF233333/Petrichor/commit/c700ebd919161c5d0ebb24710f707c04ca044202) |
| [§3.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#34-option) No `!`, `??` or `?.` operators | [Corpus counts](surveys/corpus-counts.md): prefix `!` and `not` | [5a10b25](https://github.com/YYF233333/Petrichor/commit/5a10b2505910c41390679f6cfbca82330cb3a356) |
| [§3.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#37-enum) An `int` converts to an enum only explicitly; an enum's name is a typed Dictionary; an enum without the value 0 must be assigned | [Corpus counts](surveys/corpus-counts.md): enums without payloads | [aa1fea0](https://github.com/YYF233333/Petrichor/commit/aa1fea0061380e44e0712382e1d8592eacff7919) |
| [§3.8](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#38-容器) `pop_at(i)` returns `T`; out of range is a program error | [Corpus counts](surveys/corpus-counts.md): `pop_at`, `pop_back` and `pop_front` | [a2d12e3](https://github.com/YYF233333/Petrichor/commit/a2d12e3d9e35e599141ed102784843c38a46966f) |
| [§3.9](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#39-接口) Nominal interfaces express abilities shared across engine base classes; no stateful mixins in the first version | [Cross-branch duplication survey](surveys/cross-branch-duplication.md): 185 of 353 lines removable by composition or static functions; [First paper migration](surveys/paper-migration.md): shared abilities of Brick and Enemy (C-trait) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§3.9](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#39-接口) Inherited engine properties can meet an interface's property requirements | [Second paper migration](surveys/paper-migration-2.md): owner requirements (S14) | [d17283a](https://github.com/YYF233333/Petrichor/commit/d17283a39bce2e1172e79bad5c3996ad41955138) |
| [§3.11](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#311-函数类型与-callable) Assigning a captured variable is a compile error; lambda parameters take no default values | [Corpus counts](surveys/corpus-counts.md): named lambdas, defaults and assigned captures | [d449489](https://github.com/YYF233333/Petrichor/commit/d449489ec33b936dfed5936a35a7ae1676a462ad) |
| [§3.11](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#311-函数类型与-callable) Places the engine calls accept `async` functions | [Corpus counts](surveys/corpus-counts.md): coroutine methods used as values | [6d66a0f](https://github.com/YYF233333/Petrichor/commit/6d66a0fc6448380829cfb782df2ac98e68141b39) |
| [§3.12](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#312-弱引用) [Known limitation] No typed weak references in the first version | [Corpus counts](surveys/corpus-counts.md): weak references | [43c5a04](https://github.com/YYF233333/Petrichor/commit/43c5a04b2d5b49d560726cc8b48b1b784042589a) |

## 4. Declarations

| Rule | Evidence | Decided in |
|---|---|---|
| [§4.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#41-类与继承) A common base class with state uses `@abstract` | [Corpus counts](surveys/corpus-counts.md): `@abstract` classes and methods; [Cross-branch duplication survey](surveys/cross-branch-duplication.md): duplication that inheritance could remove | [2357608](https://github.com/YYF233333/Petrichor/commit/2357608268e4cc7520cc5e3a88cad4fe27c2b0f1) |
| [§4.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#41-类与继承) Bare names reach the constants of the extended engine class | [Implementation coverage survey](surveys/implementation-coverage.md): 4.9% of files use engine class constants by bare name | [9f1f1a3](https://github.com/YYF233333/Petrichor/commit/9f1f1a390474c848c22000c36c4e0bd1e36fd2b1) |
| [§4.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#41-类与继承) Spelling and name lookup of inner classes | [Corpus counts](surveys/corpus-counts.md): inner classes | [99cdaf5](https://github.com/YYF233333/Petrichor/commit/99cdaf527908700eea7209a84d19b08c5b6668ef) |
| [§4.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#42-可见性) Subclasses can read, write, call and override members without `pub` | [Member visibility survey](surveys/member-visibility.md): members used only by subclasses; [Second paper migration](surveys/paper-migration-2.md): 29 of 102 `pub` only for subclasses | [09e9d16](https://github.com/YYF233333/Petrichor/commit/09e9d16c9eb4797b8c15604f74297e7f4ff27c41) |
| [§4.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#44-属性访问器) Setters and getters cannot be coroutines | [Property accessor survey](surveys/property-accessors.md): 30 setters contain `await` | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§4.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#45-常量) The compiler computes scalar constants; engine types and the like are computed at class load | [Constant expressions survey](surveys/constant-expressions.md): 33 of 3,094 constants need the engine | [63a88c4](https://github.com/YYF233333/Petrichor/commit/63a88c436da7fd6d489f150ac8b772e2f59b58b0) |
| [§4.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#46-函数) Overrides may omit parameter and return types | [Second paper migration](surveys/paper-migration-2.md): 6 annotations on engine virtual overrides (S5) | [ed5f607](https://github.com/YYF233333/Petrichor/commit/ed5f60765b3e71e5bfc29408e2403d951b978628) |
| [§4.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#46-函数) Rest parameters, with an optional element type | [Corpus counts](surveys/corpus-counts.md): rest parameters `...args` | [2357608](https://github.com/YYF233333/Petrichor/commit/2357608268e4cc7520cc5e3a88cad4fe27c2b0f1) |
| [§4.8](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#48-静态成员) Static members keep GDScript's spelling and timing; a type without a default value needs an initializer | [Corpus counts](surveys/corpus-counts.md): `static var` and `_static_init` | [13a47dd](https://github.com/YYF233333/Petrichor/commit/13a47dd1b74d59a9429aa9288b053f19c6b947b8) |

## 5. Expressions and statements

| Rule | Evidence | Decided in |
|---|---|---|
| [§5.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#51-运算) Assigning to a character of a String is a compile error | [Corpus counts](surveys/corpus-counts.md): assignments to a String's characters | [fec61d5](https://github.com/YYF233333/Petrichor/commit/fec61d59145ac09d5836977b4e41afcf39f3c3d3) |
| [§5.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#53-转换) A downcast that must succeed is written `(x as T).unwrap()` | [Second paper migration](surveys/paper-migration-2.md): 16 `(x as T).unwrap()` | [2a08bde](https://github.com/YYF233333/Petrichor/commit/2a08bdeca439283cf9a0c22c3dbead9bbb458995) |
| [§5.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#54-收窄) Locals and parameters narrow; member variables do not | [First paper migration](surveys/paper-migration.md): members used after `is` (C-is); [Second paper migration](surveys/paper-migration-2.md): locals added because members do not narrow | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§5.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#57-循环) Objects are iterable when their class defines `_iter_init`, `_iter_next` and `_iter_get` | [Implementation coverage survey](surveys/implementation-coverage.md): no class defines `_iter_init` | [f7de513](https://github.com/YYF233333/Petrichor/commit/f7de513616434963849f8515f031b61e08f8844d) |

## 6. Initialization and lifecycle

| Rule | Evidence | Decided in |
|---|---|---|
| [§6.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#62-必须赋值的成员) `_init` of `Node` and `Resource` may take parameters; attaching a script with required parameters without arguments is a program error | [Corpus counts](surveys/corpus-counts.md): scripts whose own `_init` takes parameters; [Pitfalls catalog](surveys/pitfalls.md): G-02 | [57aa767](https://github.com/YYF233333/Petrichor/commit/57aa767c919481e5f533fde92274fb354af559fb) |
| [§6.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#62-必须赋值的成员) An autoload's members referring to scene nodes are written `T?` | [Corpus counts](surveys/corpus-counts.md): registering a node on an autoload member in `_ready`; [Second paper migration](surveys/paper-migration-2.md): an autoload holding references to scene nodes | [c36ac66](https://github.com/YYF233333/Petrichor/commit/c36ac6636e4d347f948d9ab072bf05b8c4e916f2) |
| [§6.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#63-onready) `@onready` keeps GDScript's timing; direct misuse is a compile error | [Pitfalls catalog](surveys/pitfalls.md): G-04 | [2b5f53f](https://github.com/YYF233333/Petrichor/commit/2b5f53fefaebeb60a6e655364b5f4eed22182c12) |
| [§6.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#64-就绪顺序) Children are ready before their parent; reading a parent's uninitialized member is a program error | [Pitfalls catalog](surveys/pitfalls.md): G-03, G-05 | [2b5f53f](https://github.com/YYF233333/Petrichor/commit/2b5f53fefaebeb60a6e655364b5f4eed22182c12) |
| [§6.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#64-就绪顺序) Must-assign members assigned by ancestors are checked when the owner emits `ready` | [Corpus counts](surveys/corpus-counts.md): scripts assigning script members of nodes below them | [c36ac66](https://github.com/YYF233333/Petrichor/commit/c36ac6636e4d347f948d9ab072bf05b8c4e916f2) |
| [§6.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#65-就绪前的-setter) Setters run at once; `await ready` in a setter is a compile error | [Property accessor survey](surveys/property-accessors.md): 25 setters use `await ready` | [568c9f8](https://github.com/YYF233333/Petrichor/commit/568c9f89688ae5e9a1a322f2d0f3022803e51b1d) |
| [§6.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#66-析构) No new destructor syntax | [Corpus counts](surveys/corpus-counts.md): `NOTIFICATION_PREDELETE`; [Pitfalls catalog](surveys/pitfalls.md): G-09 | [7cceff9](https://github.com/YYF233333/Petrichor/commit/7cceff994a49bca44857bbfbd38d6844e313d841) |
| [§6.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#67-引用环与泄漏) Warnings for evident reference cycles and leaks | [Pitfalls catalog](surveys/pitfalls.md): G-10 | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |

## 7. Scene model

| Rule | Evidence | Decided in |
|---|---|---|
| [§7.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#71-节点定型) `$X` is typed from every scene structure of the script | [Scene structure survey](surveys/scene-structures.md): literal paths never point to different types across structures; [First paper migration](surveys/paper-migration.md): `$X` is Node without an expected type (C-scene) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§7.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#72-场景之间结构不同的情况) Nodes missing from template scenes are checked by usage; optional nodes use `get_node_or_null` | [Scene structure survey](surveys/scene-structures.md): missing nodes concentrate on optional nodes and template scenes | [af3e112](https://github.com/YYF233333/Petrichor/commit/af3e112f40a9f64977808f78d6523f96af7ddf85) |
| [§7.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#73-向上访问) `/root/X` becomes the autoload's name; parent and owner are declared with `@parent(T)` and `@owner(T)` | [Scene structure survey](surveys/scene-structures.md): access outside the attached scene's subtree | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§7.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#73-向上访问) Without a declaration, `get_parent()` and `owner` are `Node?` | [Corpus counts](surveys/corpus-counts.md): `get_parent()` and `owner` on self | [d7ed2c9](https://github.com/YYF233333/Petrichor/commit/d7ed2c94dd0f32e39fbcd58cc2f3fb8d906bfb26) |
| [§7.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#73-向上访问) `@owner(T)` is checked on every read, not when nodes move | [Second paper migration](surveys/paper-migration-2.md): DeathComponent leaving its owner's subtree | [d17283a](https://github.com/YYF233333/Petrichor/commit/d17283a39bce2e1172e79bad5c3996ad41955138) |
| [§7.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#75-必须赋值的导出) Required exports are checked by how each scene is used | [Second paper migration](surveys/paper-migration-2.md): required exports in sub-scenes (S6) | [ee3e425](https://github.com/YYF233333/Petrichor/commit/ee3e42540cbf032e01eecb61088f70f643187f8c) |
| [§7.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#76-资源共享) Writing to a known shared resource gives a warning | [Pitfalls catalog](surveys/pitfalls.md): G-19, G-20 | [7cceff9](https://github.com/YYF233333/Petrichor/commit/7cceff994a49bca44857bbfbd38d6844e313d841) |
| [§7.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#76-资源共享) Reference cycles among `preload`, exported scenes and resources are compile errors | [Corpus counts](surveys/corpus-counts.md): load cycles; [Pitfalls catalog](surveys/pitfalls.md): G-34 | [7cceff9](https://github.com/YYF233333/Petrichor/commit/7cceff994a49bca44857bbfbd38d6844e313d841) |

## 8. Errors

| Rule | Evidence | Decided in |
|---|---|---|
| [§8.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#83-断言) `assert` is removed in release builds | [Corpus counts](surveys/corpus-counts.md): `assert(...)` statements | [804b059](https://github.com/YYF233333/Petrichor/commit/804b0599ad3891f55ae965fa33ff075f8404b8bb) |
| [§8.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#83-断言) An assertion's message is evaluated only on failure | [Corpus counts](surveys/corpus-counts.md): messages of `assert(...)` statements | [545908b](https://github.com/YYF233333/Petrichor/commit/545908ba3b4380665471bd466c02eab909a3fd6a) |

## 9. Coroutines

| Rule | Evidence | Decided in |
|---|---|---|
| [§9.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#91-async-与-task) Lambdas containing `await` are also written `async func` | [Corpus counts](surveys/corpus-counts.md): lambdas containing await | [6d66a0f](https://github.com/YYF233333/Petrichor/commit/6d66a0fc6448380829cfb782df2ac98e68141b39) |
| [§9.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#95-组合与重入) `Task.delay` times with the engine's defaults and needs no node in the tree | [Corpus counts](surveys/corpus-counts.md): calls of `create_timer(...)` | [4877578](https://github.com/YYF233333/Petrichor/commit/48775782ef2ca38c2856a9a0e003d4a68bc3d178) |
| [§9.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#95-组合与重入) No automatic re-entry policy; cancel the old call through its handle | [Pitfalls catalog](surveys/pitfalls.md): G-12, G-13 | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |
| [§9.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#96-await-信号) A signal with several parameters can be awaited only as a statement | [Await signal results survey](surveys/await-signal-results.md): 1 of 1,356 awaits uses a multi-parameter signal's result | [f7c4e94](https://github.com/YYF233333/Petrichor/commit/f7c4e942b352dca3fa0d9da4fffc79703f7292cb) |
| [§9.6](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#96-await-信号) Awaiting a `Signal` of unknown signature as a value gives `Variant` | [Await signal results survey](surveys/await-signal-results.md): the one use is a C# signal of unknown signature | [f7371c1](https://github.com/YYF233333/Petrichor/commit/f7371c1c05a5bea125d0e55b084e6dd51f355936) |
| [§9.7](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#97-对象释放与挂起的协程) A coroutine is cancelled silently when its object is freed; the awaiter of a freed object gets a program error | [Pitfalls catalog](surveys/pitfalls.md): G-11 | [ce32d4a](https://github.com/YYF233333/Petrichor/commit/ce32d4ae40b32709ac1613bbb6f0e1e3e1f1b75c) |
| [§9.8](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#98-跨语言-await) Cross-language `await` works in both directions | [First paper migration](surveys/paper-migration.md): cross-language coroutines (A7) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 10. Engine boundary

| Rule | Evidence | Decided in |
|---|---|---|
| [§10.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#102-引擎-api-中对象的可空性) The nullability of objects in engine APIs is audited, most used APIs first | [Corpus counts](surveys/corpus-counts.md): engine APIs that objects pass through; [First paper migration](surveys/paper-migration.md): APIs returning null only on error (A2) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) Constraints the engine exports are used directly | [First paper migration](surveys/paper-migration.md): `RequiredResult` annotations (A1) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) `Variant` math utilities return the type of arguments of the same type | [First paper migration](surveys/paper-migration.md): Variant math utilities (A3) | [f7c4e94](https://github.com/YYF233333/Petrichor/commit/f7c4e942b352dca3fa0d9da4fffc79703f7292cb) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) Engine APIs filtering by a literal class name are typed by that class | [Second paper migration](surveys/paper-migration-2.md): downcasts after `find_children` and the like | [2a08bde](https://github.com/YYF233333/Petrichor/commit/2a08bdeca439283cf9a0c22c3dbead9bbb458995) |
| [§10.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#103-绑定元数据) `try_` versions returning `Result` are added; the original API stays | [Corpus counts](surveys/corpus-counts.md): engine APIs that return null on failure | [8e6a7d7](https://github.com/YYF233333/Petrichor/commit/8e6a7d7cf83ad8097b5eca1b8c57fa395395f9ed) |
| [§10.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#104-字符串形式的成员名) A literal name of a member without `pub` is a compile error | [By-name access survey](surveys/by-name-access.md): literal names in code that target the script itself | [e49da5b](https://github.com/YYF233333/Petrichor/commit/e49da5b354204bce6f42541134b73e7e5d200bd6) |
| [§10.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#105-反射暴露的成员) By-name reflection reaches only `pub` members; members the engine accesses by name need `pub` | [By-name access survey](surveys/by-name-access.md): `pub` to add under strict visibility | [e49da5b](https://github.com/YYF233333/Petrichor/commit/e49da5b354204bce6f42541134b73e7e5d200bd6) |
| [§10.5](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#105-反射暴露的成员) Reading and writing engine properties does not go through `_get` and `_set` | [Corpus counts](surveys/corpus-counts.md): methods named `_get` and `_set` | [d3d551d](https://github.com/YYF233333/Petrichor/commit/d3d551d29c4c1b5441117333a6a12524d0c3b4aa) |

## 11. Coexisting with GDScript and C#

| Rule | Evidence | Decided in |
|---|---|---|
| [§11.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#111-其他语言的类的静态视图) Classes of other languages and autoloads are seen through reflection | [First paper migration](surveys/paper-migration.md): static view of GDScript classes and autoloads (A6) | [f7c4e94](https://github.com/YYF233333/Petrichor/commit/f7c4e942b352dca3fa0d9da4fffc79703f7292cb) |
| [§11.1](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#111-其他语言的类的静态视图) An autoload's name can be written in a type | [Corpus counts](surveys/corpus-counts.md): autoload names written in types | [7453c75](https://github.com/YYF233333/Petrichor/commit/7453c758d5bae3d0454947c05195612e94f437df) |
| [§11.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#112-继承) Classes of this language cannot extend GDScript classes | [Pitfalls catalog](surveys/pitfalls.md): C-17 | [83a737a](https://github.com/YYF233333/Petrichor/commit/83a737a2e8b5d9d2e521085575c5d5cbd3f172a5) |
| [§11.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#112-继承) GDScript cannot extend classes of this language; migration takes the subclasses along | [Second paper migration](surveys/paper-migration-2.md): GDScript subclasses of Brick and Enemy | [7f7b9ea](https://github.com/YYF233333/Petrichor/commit/7f7b9ea3dcc96883dfc520cdbc66cc596e96526b) |
| [§11.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#113-跨语言调用与消息) [Known limitation] GDScript cannot call static methods of this language or use its enums and the like in types | [Corpus counts](surveys/corpus-counts.md): cross-file class-level access | [056b281](https://github.com/YYF233333/Petrichor/commit/056b281605c1cb159aa3a635ff89b25e0c45190e) |
| [§11.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#113-跨语言调用与消息) Messages with C# are structs, encoded as Dictionaries by field name | [First paper migration](surveys/paper-migration.md): converting message fields (A8) | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 12. Runtime

| Rule | Evidence | Decided in |
|---|---|---|
| [§12.3](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#123-线程) [Known limitation] No new thread API in the first version | [Corpus counts](surveys/corpus-counts.md): `Thread.new` and `WorkerThreadPool` | [2583958](https://github.com/YYF233333/Petrichor/commit/25839586eb6c58331333e63a48ea85791897ecca) |

## 13. Toolchain

| Rule | Evidence | Decided in |
|---|---|---|
| [§13.2](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#132-第一版的工具) Layout rules of the formatter | [Corpus counts](surveys/corpus-counts.md): layout habits | [d3f34e1](https://github.com/YYF233333/Petrichor/commit/d3f34e121fe7a17b3851231e4996f17148108510) |
| [§13.4](https://github.com/YYF233333/Petrichor/blob/main/docs/language-spec.zh.md#134-迁移) Migrating a class lists the GDScript files making class-level access to it and offers to migrate them along | [Corpus counts](surveys/corpus-counts.md): cross-file class-level access | [87726d5](https://github.com/YYF233333/Petrichor/commit/87726d5e83f57d6da8f7c5c149459e0bc0f7c773) |
