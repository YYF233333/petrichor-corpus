# 语料 v2 的选取

2026-11-15 选取 200 个仓库，写入 [`corpus/v2.json`](../corpus/v2.json)。
新入选仓库钉在当时默认分支的 HEAD。
v1 的 20 个仓库保留各自的 v1 提交。
`python -I selection/select.py` 从 `selection/cache/` 和 [`labels.tsv`](labels.tsv) 离线复现结果。
删掉 `selection/cache/` 后重跑，会按 GitHub 现状重新检索（HEAD 会移动）。
[`candidates.tsv`](candidates.tsv) 列出全部 2,707 个候选和落选原因。

## 规则

候选来自 GitHub 搜索 `language:GDScript fork:false`，按星数分段检索，下限 20 星。
为避免单次查询触及 1,000 条上限，脚本预留了按 `created` 和星数递归细分查询的机制。
本次检索不限推送日期，老而稳定的项目同样可见。
`corpus/v1.json` 的 20 个仓库另行加入。

依次检查：

1. 不是 fork 或镜像，也不是由模板仓库创建（API `templateRepository`）。
2. 默认分支有 `project.godot` 时，至少一个写着 `config_version=5`。
3. 没有 `project.godot` 时，须是带 `addons/*/plugin.cfg` 或根目录 `plugin.cfg` 的插件仓库。
   其第一方 `.gd` 代码须含 Godot 4 语法（如 `@export`、`@onready`、`@tool`、`await`、`super`），且不含 Godot 3 语法（`export var`、`onready var`、`yield(`、`tool`、`remote func` 等）。
4. 排除 [`labels.tsv`](labels.tsv) 标出的生成代码后，第一方 `.gd` 估计不少于 100 行。
5. 不少于 20 星。
6. 不是近似重复：按星数从高到低，第一方 `.gd` 字节有一半与已入选仓库的 blob 相同则落选。

第一方的判定：

- `config_version` 不是 5 的工程里的 `.gd` 不算。
- `addons/<名>/` 默认是第三方。
- 名字包含仓库名或 owner 名的 addon 算第一方。
- `plugin.cfg` 的 `author` 是 owner 的 addon 也算第一方。
- 没有 `project.godot` 且按名字与作者仍未匹配时，带 `plugin.cfg` 的非测试 addon 算第一方。
- 以 `.` 开头的目录不算。
- `labels.tsv` 的 `generated` 列记入 `exclude`，不计入第一方。

行数按 blob 字节数除以 34.4 估计（在 v1 上实测：10,020,320 字节对 291,043 行）。

## 人工判读与作者归属

通过前六条且排重后的 1,548 个候选（扣除 `generated` 后剩余 1,546 个满足 100 行下限），逐一阅读其 README、描述、目录树和最多 3 个第一方 `.gd` 文件，记录在 [`labels.tsv`](labels.tsv)：

- `group`：`game`、`plugin`、`tool` 或 `demo`。
- `complete`：`yes` 为完整可运行的项目或插件；`no` 为骨架、教程片段、素材堆砌或非代码仓库。
- `authorship`：`human`、`mixed` 或 `agent`。
  脚本先收集创建日期、2025-01-01 之前提交占比、活跃周均提交数、智能体指令文件（`CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、`.cursor/`、`.cursorrules`、`.windsurfrules`、`.github/copilot-instructions.md`）和最近 100 次提交的 `Co-Authored-By` 署名，再结合代码风格判读。
- `generated`：应排除的生成代码或大型数据表路径模式。
- `reason`：一行简短证据。

## 名额与上限

选取 200 个仓库时遵循以下条件：

- 保留 `corpus/v1.json` 全部 20 个仓库。其中 `YYF233333/Ring` 记为 `weight: reference`，其余 19 个记为 `normal`。
- 剔除 `complete = no` 的候选（共 28 个）。
- `game` 占不少于 60%（无论计入还是排除 `Ring`，均取至少 120 个 `normal` 游戏，即总共 121 个 `game`）。
- 其余名额按星数从高到低、同星先取创建早者补足 200 个。
- `human` 仓库占总数不少于一半，且截断后的估算行数占不少于一半。

清单的名字只占一个目录。
仅在仓库名重合时加 `owner__` 前缀。
`first_party_addons` 保存选择阶段的插件归属。
这些字段由离线缓存重放，不重新判断作者。

调查时每仓库最多计 20,000 行第一方代码，按文件以固定随机种子 `20261115` 抽取，记录在清单的 `line_cap` 与 `line_cap_seed`。

## 结果

| 组 | 仓库 | 原始估算行数 | 截断后估算行数 | 新入选最低星数 |
|---|---|---|---|---|
| game | 121 | 964,091 | 654,437 | 73 |
| plugin | 54 | 728,535 | 487,394 | 643 |
| tool | 18 | 369,118 | 227,555 | 698 |
| demo | 7 | 37,740 | 31,498 | 783 |
| 合计（含 Ring） | 200 | 2,099,484 | 1,400,884 | — |
| 合计（`weight: normal`） | 199 | 2,096,852 | 1,398,252 | — |

| 作者归属 | 仓库 | 占比 | 原始估算行数 | 截断后估算行数 | 截断后占比 |
|---|---|---|---|---|---|
| human | 186 | 93.0% | 1,586,187 | 1,169,145 | 83.5% |
| mixed | 9 | 4.5% | 253,262 | 150,211 | 10.7% |
| agent | 5 | 2.5% | 260,035 | 81,528 | 5.8% |

排除 `Ring` 后的 199 个 `normal` 仓库中，`human` 占 185 个（93.0%），截断后行数占 83.4%。

无 `project.godot` 的插件仓库共判读 229 个，入选 10 个：
`phantom-camera`、`gdmaim`、`script-ide`、`unidot_importer`、`func_godot_plugin`、`Qodot`、`better-terrain`、`GodotFirebase`、`godot-debug-menu` 和 `godot-mcp-pro`。

许可证：MIT 134 个，GPL 与 AGPL 13 个，其他已识别开源许可证 12 个（CC0-1.0 4 个、MPL-2.0 3 个、Unlicense 2 个、ISC 1 个、BSD-2-Clause 1 个、Apache-2.0 1 个）。
41 个在清单中记为 `license: null`，仅作统计来源（其中 19 个无许可证文件，22 个 GitHub 返回 `NOASSERTION`）。

落选原因：无 Godot 4 工程 705 个，无 `project.godot` 或 `plugin.cfg` 203 个，不足 100 行 113 个，插件使用 Godot 3 语法 107 个，插件缺少 Godot 4 语法特征 1 个，由模板创建 15 个，近似重复 17 个，判读为不完整 28 个，超出名额 1,318 个。

## 规模分布

每仓库原始估算行数的中位数是 3,638，四分位是 1,151 和 11,808，90% 分位是 29,687。
原始行数在 1,000 行以下的入选仓库有 44 个（含 v1 的 4 个 Kenney 起步工程）。
2025 年以后创建的仓库占 34 个，占截断后行数的 24.0%（原始行数 29.9%）。

截断前最大的五个仓库占全部原始行数的 18.9%（396,718 / 2,099,484）。
按每仓库 20,000 行上限截断后，最大的五个仓库各计 20,000 行，合计占截断后总行数的 7.14%（100,000 / 1,400,884；排除 `Ring` 为 7.15%）：

| 仓库 | 组 | 归属 | 原始估算行数 | 截断后行数 | 截断后占比 |
|---|---|---|---|---|---|
| hi-godot/godot-ai | plugin | agent | 144,828 | 20,000 | 1.43% |
| EIRTeam/Project-Heartbeat | game | human | 64,837 | 20,000 | 1.43% |
| max99x/wutw-public | game | human | 63,434 | 20,000 | 1.43% |
| mirror-engine/the-mirror | tool | human | 62,972 | 20,000 | 1.43% |
| SlayHorizon/godot-tiny-mmo | game | human | 60,647 | 20,000 | 1.43% |

测试路径（`test/`、`tests/`、`test_*.gd` 等）占选中原始行数的 10.8%。
`labels.tsv` 中的 `generated` 模式在入选仓库中跳过了约 9,162 行生成代码。
入选仓库之间字节相同的 `.gd` blob 仅占 0.07%（约 1,382 行）。

## 规则看不见的

- 主语言不是 GDScript 的 Godot 工程搜不到，例如以 C#、C++ 或着色器为主的仓库。
- `addons/` 以外夹带的第三方库（如 `Pixelorama` 中的 `ObjParse.gd`）未做逐一剥离，仍算第一方。
- 人工判读只看了 README、目录树和最多 3 个 `.gd` 文件，未全量阅读每个仓库，可能漏掉深层目录中的生成文件或部分文件混入的 AI 代码。
- 没有 `CLAUDE.md`、`AGENTS.md` 或 `Co-Authored-By` 署名的 2025 年后仓库，若作者未在代码或 README 中留下痕迹，仍会判为 `human`。
- 根目录带 `plugin.cfg` 的插件仓库（如 `V-Sekai/unidot_importer`）纳入了无 `project.godot` 插件的判断，因为部分成熟插件以仓库根目录直接作为插件目录发布。
- 星数仍偏向插件与工具类仓库；`game` 组以 73 星截断，而 `plugin`、`tool`、`demo` 门槛在 643 到 783 星之间。
- 由模板创建的仓库一律排除（含部分独立项目），v1 仓库除外。
- 仓库行数是按 34.4 字节/行估算，单个仓库的精确行数须以实际检出计算为准。
