# petrichor-corpus

[English](README.md)

本仓库收存 [Petrichor](https://github.com/YYF233333/Petrichor) 设计的依据。Petrichor 是一门面向 Godot 4 的静态类型脚本语言，沿用 GDScript 的写法。能由真实代码回答的设计问题，先在真实的 Godot 4 项目上调查。这里的每份调查是一篇报告，加上复现它的脚本和结果。[决策索引](decisions.zh.md)从规范的每条规则通往它的依据，也可反向查找。

## 调查

报告用中文写成，每篇末尾附复现命令。

- [脚本会见到不止一种场景结构吗？](surveys/scene-structures.md)
- [原生基类不同造成了多少代码重复？](surveys/cross-branch-duplication.md)
- [引擎、GDScript 和 C# 桥接的暗坑](surveys/pitfalls.md)
- [真实的 Godot 4 项目怎样使用属性的 getter 和 setter？](surveys/property-accessors.md)
- [await 多参数信号的结果有多常被使用？](surveys/await-signal-results.md)
- [脚本成员在哪里被使用：本文件、子类、其他脚本？](surveys/member-visibility.md)
- [引擎按名字访问的成员](surveys/by-name-access.md)
- [按现行设计迁移真实代码的成本](surveys/paper-migration-2.md)
- [按 v0.1 规范迁移真实代码的成本](surveys/paper-migration.md)
- [计算真实代码中的常量需要什么？](surveys/constant-expressions.md)
- [真实代码用到而实现尚不支持的写法有哪些？](surveys/implementation-coverage.md)
- [语料中的零散计数](surveys/corpus-counts.md)

## 语料

`corpus/v1.json` 把 20 个 Godot 4 仓库固定在各自的提交上。每个仓库属于一组：game、plugin、demos 或 tool。

`corpus/v2.json` 固定了 200 个 Godot 4 仓库，保留 v1 的全部 20 个仓库（`Ring` 权重为 `reference`）。清单记录分组、许可证、星数、创建日期、作者归属、权重和排除的生成路径。每仓库最多计 20,000 行第一方代码，按清单中的种子 `20261115` 抽取。选取规则与统计见 [`selection/selection.md`](selection/selection.md)。

用 Python 3.11 和 git 拉取语料：

```
python fetch.py       # 拉取 v1
python fetch.py v2    # 拉取 v2
```

克隆是浅克隆，不取历史文件内容，只检出部分文件。检出的只有 `.gd`、`.tscn`、`.tres` 等文本文件。克隆放在 `corpus/v1/` 或 `corpus/v2/`，git 忽略这些目录。

## 重跑

有些脚本还要读引擎的 API 描述。先下载一次：

```
curl -sSfL --create-dirs -o inputs/extension_api-4-7.json https://raw.githubusercontent.com/godotengine/godot-cpp/8070599885b6df675fcad033dd032ce44be2b850/gdextension/extension_api-4-7.json
```

`python reproduce.py` 重跑由这些输入即可复现已提交结果的调查。有任何不同就失败，CI 在每次推送时运行它。每篇报告的“复现”一节列出各自的命令。有些调查需要语料以外的输入，那一节写明了：

- 某个提交的 Godot 源码检出；
- GitHub 检索，其结果随时间变化。

CI 还读取 Godot 固定提交 `469659e0617345149cd1eaec2e643d61d130aa6a` 的类参考。
检出位置是 `inputs/godot-docs/`，只取 `doc/classes/`。
固定提交的模块派生元数据补齐其余类。
若已有检出，设置 `GODOT_REFERENCE` 指向它。
再把 `GODOT_REVISION` 设为上述提交。
脚本只读 Git 对象，不改检出。

获取 v2 后，重跑全部自动调查和纯人写子集：

```
python fetch.py v2 --jobs 4
python rerun.py v2
python rerun.py v2 --human-only
```

派生结果写入各调查的 `results-v2/` 和 `results-v2-human/`。
原始提取留在 `work/rerun/`。
若已有结果不同，脚本拒绝覆盖。
纸面迁移账本仍固定于原来的两个项目。
访问器类别先给机械指标，重新阅读样本后再作判断。

## 方法

- 调查在固定版本的语料上进行。扩大语料时另立新清单，旧清单保留。
- 脚本读取语料清单，所以旧脚本不经修改就能在任何版本的语料上运行。
- 换新版本的语料时，所有数字都完整重跑。只有数字移到所支持决定的阈值附近时，才重新阅读代码。
- 靠阅读代码作出的判断采用抽样：每项最多 50 处，用随结果记录的固定随机种子抽取。结论写成比例。v1 上已做的全量阅读保持原样。
- 调查记录它评估的设计。Petrichor 的设计改变后，数据不变，由决策索引指向现行规则。

## 许可

语料中的代码属于其作者，适用各自的许可证。本仓库只保存清单、脚本、导出的结果和简短摘录。引用语料代码时，用固定提交上的 GitHub 链接。

`surveys/paper-migration*/migrated/` 中是两个项目的改写。Kenney FPS 起步工程的改写沿用其许可证，见 `migrated/fps/LICENSE.md`。Ring 的改写经原作者同意，以 MIT 许可证发布。其余内容都以 [MIT 许可证](LICENSE)发布。
