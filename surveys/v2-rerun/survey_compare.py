"""Compare the key numbers of the surveys; run reproduce.py and rerun.py first.

The v1 scene CSVs are reproduced under work/reproduce, rather than added to the
old committed results. All other inputs are versioned derived results.
"""
import ast
import collections
import csv
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
SUFFIXES = ('results', 'results-v2', 'results-v2-human')


def js(path):
    return json.loads(path.read_text(encoding='utf-8'))


def text(survey, suffix, name):
    return (ROOT / 'surveys' / survey / suffix / name).read_text(encoding='utf-8')


def rows(path):
    with open(path, encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def metric(repos, key):
    values = [r.get(key, 0) for r in repos.values()]
    return {'n': sum(values), 'repos': sum(n > 0 for n in values)}


def occurrences(records, key='repo'):
    c = collections.Counter(r[key] for r in records)
    return {'n': len(records), 'repos': len(c)}


def main():
    facts = []
    def add(label, rule, values, basis):
        facts.append({'label': label, 'rule': rule, 'v1': values[0], 'v2': values[1], 'human': values[2], 'basis': basis})

    scenes = []
    for suffix in SUFFIXES:
        base = ROOT / ('work/reproduce/scene-structures' if suffix == 'results' else 'surveys/scene-structures/' + suffix)
        scripts, uses = rows(base / 'scripts.csv'), rows(base / 'uses.csv')
        multi = {(r['repo'], r['script']) for r in scripts if int(r['n_struct_all']) >= 2}
        scenes.append({
            'multi': occurrences([r for r in scripts if int(r['n_struct_all']) >= 2 and int(r['lit_uses']) > 0]),
            'conflict_all': occurrences([u for u in uses if u['status'].startswith('differs')]),
            'conflict_multi': occurrences([u for u in uses if u['status'].startswith('differs') and (u['repo'], u['script']) in multi]),
            'conflict_down': occurrences([u for u in uses if u['status'].startswith('differs') and u['path'] != '.' and not u['path'].startswith('..')]),
            'missing': occurrences([u for u in uses if u['status'] == 'missing_in_some']),
            'absolute': occurrences([u for u in uses if u['status'] == 'absolute']),
        })
    for key, label, rule in [('multi', '多结构且使用字面路径的脚本', '§7.1'), ('conflict_multi', '多结构脚本中的路径类型差异', '§7.1'),
                             ('conflict_all', '所有脚本中的路径类型差异', '§7.1'), ('conflict_down', '其中向下路径的类型差异', '§7.1'),
                             ('missing', '部分场景缺少目标的路径使用', '§7.2'), ('absolute', '绝对路径使用', '§7.3')]:
        add(label, rule, [s[key] for s in scenes], '零冲突前提失效；不等于同等数量的类型错误' if key.startswith('conflict') else '仍需处理多结构、可选节点和向上访问')

    clones = []
    for suffix in SUFFIXES:
        folder = 'out' if suffix == 'results' else suffix
        base = ROOT / 'surveys/cross-branch-duplication' / folder
        data = js(base / 'summary.json')['repos']
        games = [r for r in data if r['group'] == 'games']
        result = {}
        for key, category in [('cross', 'cross_branch'), ('native', 'same_native_unrelated'), ('chain', 'same_chain')]:
            vals = {r['repo']: {'n': r['exact']['lines'].get(category, 0)} for r in games}
            result[key] = metric(vals, 'n')
            result[key]['per_1k_logical_lines'] = 1000 * result[key]['n'] / sum(r['lloc'] for r in games)
        result['capability'] = metric({r['repo']: r['capability'] for r in games}, 'cross_pairs_sharing_1plus')
        result['components'] = occurrences([r for r in rows(base / 'components.csv') if r['cross_branch_hosts'] == 'True'])
        clones.append(result)
    for key, label in [('cross', '游戏精确跨分支重复行'), ('native', '游戏同原生类重复行'), ('chain', '游戏同继承链重复行'),
                        ('capability', '游戏跨分支且消费共同名字的类对'), ('components', '已用于不同原生父类型的组件脚本')]:
        add(label, '§3.9、§4.1', [c[key] for c in clones], '继承可消除的重复仍更多；机制标签另用样本')
    for window in (3, 8):
        values = []
        for suffix in SUFFIXES:
            base = ROOT / 'surveys/cross-branch-duplication'
            path = base / (f'out_k{window}' if suffix == 'results' else suffix + f'/k{window}') / 'report.txt'
            per = []
            for line in path.read_text(encoding='utf-8').splitlines():
                cells = line.split()
                if len(cells) >= 6 and cells[0] != '--' and cells[1] == 'games' and cells[3].isdigit() and cells[5].isdigit():
                    per.append((int(cells[3]), int(cells[5])))
            n = sum(r[1] for r in per)
            values.append({'n': n, 'repos': sum(r[1] > 0 for r in per),
                           'per_1k_logical_lines': 1000 * n / sum(r[0] for r in per)})
        add(f'游戏跨分支重复行，K={window}', '§3.9、§4.1', values, '窗口敏感性保留，不能只看K=5')

    visibility = []
    for suffix in SUFFIXES:
        records = {}
        for ln in text('member-visibility', suffix, 'vis.txt').splitlines():
            cells = [v.strip() for v in ln.split('|')][1:-1]
            if len(cells) == 8 and cells[2].isdigit():
                records[cells[0]] = dict(lines=int(cells[2]), external=int(cells[3]), subclass=int(cells[4]))
        visibility.append(records)
    for key, label, rule in [('external', '外部使用的成员', '§2.4'), ('subclass', '仅子类使用的成员', '§4.2')]:
        values = [metric(v, key) for v in visibility]
        for value, v in zip(values, visibility):
            value['per_1k_code_lines'] = value['n'] * 1000 / sum(r['lines'] for r in v.values())
        add(label, rule, values, '频率接近；原取舍仍有依据')
    add('仅为引擎按名访问而需增加pub的成员', '§10.4、§10.5',
        [metric(js(ROOT / 'surveys/by-name-access' / suffix / 'by_name_access.json'), 'no_pub') for suffix in SUFFIXES],
        '迁移开销仍明确，纯人写也未消失')
    incidence = [js(ROOT / 'surveys/implementation-coverage' / suffix / 'incidence.json') for suffix in SUFFIXES]
    add('代码中本脚本目标的字面名字', '§10.4', [metric(i, 'self_code_names') for i in incidence], '不再极少，仍可机械发现')

    constants = []
    for suffix in SUFFIXES:
        s = text('constant-expressions', suffix, 'constants.txt')
        total_decls = int(re.search(r"^all \{.*'decls': (\d+)\}", s, re.M)[1])
        table = s.split('## Per repository')[1].split('## Samples')[0]
        per = {m[1]: {'n': int(m[2])} for m in re.finditer(r'^\s*(\S+)\s+(\d+)\s+\d+\s+\d+\s+\d+\s*$', table, re.M)}
        assert metric(per, 'n')['n'] == total_decls, (suffix, metric(per, 'n'), total_decls)
        engine = s.split('## Initializers that compute more than scalars')[1].split('## Per repository')[0]
        refs = []
        for ln in engine.splitlines():
            m = re.match(r'^\s+(.+?)\s+([^/\s]+)/.+?:\d+\s', ln)
            if m and m[1].strip() in ('Color from a hex string', 'math functions returning float', 'operators on engine types'):
                refs.append({'repo': m[2]})
        constants.append({'all': metric(per, 'n'), 'engine': occurrences(refs)})
    add('常量声明', '§4.5', [c['all'] for c in constants], '分层求值仍有对象')
    add('需非标量求值的常量', '§4.5', [c['engine'] for c in constants], '不再只有33处；由引擎求值的需求仍在')

    accessors = [js(ROOT / 'surveys/property-accessors' / suffix / 'automatic.json')['repos'] for suffix in SUFFIXES]
    for key, label, rule in [('getters', 'getter', '§4.4'), ('trivial_getters', '字面只返回自身字段的getter', '§4.4'),
                             ('nontrivial_field_getters', '非平凡且提到本字段的getter候选', '§4.4'),
                             ('nontrivial_other_getters', '非平凡且不提到本字段的getter', '§4.4'),
                             ('await_setters', '含await的setter', '§4.4'), ('await_ready_setters', '含await ready的setter', '§6.5')]:
        add(label, rule, [metric(c, key) for c in accessors], '多数平凡的旧前提失效；现行A不重选' if 'getter' in key else '禁止协程setter的迁移成本仍非零')
    awaits = [js(ROOT / 'surveys/await-signal-results' / suffix / 'metrics.json')['repos'] for suffix in SUFFIXES]
    for key, label in [('awaits', 'await总数'), ('signal_awaits', '信号await'), ('used_signal_results', '使用信号await结果'),
                        ('used_multi_results', '使用多参数信号结果'), ('typed_multi_results', '其中按接收者或self直接解析'),
                        ('used_zero_results', '使用无参数信号结果')]:
        add(label, '§9.6', [metric(c, key) for c in awaits], '仅有签名未知特例的旧前提失效' if key in ('used_multi_results', 'typed_multi_results') else '仍需区分签名与返回值的使用')

    for filename, construct, label, rule in [('remaining.txt', 'engine class constant by its bare name', '裸用引擎常量的文件', '§4.1'),
                                           ('remaining2.txt', 'class with _iter_init', '定义_iter_init的类', '§5.7')]:
        values = []
        for suffix, per in zip(SUFFIXES, incidence):
            s = text('implementation-coverage', suffix, filename)
            first = s.split('== Game repositories')[0]
            m = re.search(re.escape(construct) + r'\s+files\s+(\d+).*?uses\s+(\d+)', first)
            file_key, use_key = ('bare_files', 'bare_uses') if filename == 'remaining.txt' else ('iterator_files', 'iterator_defs')
            value = metric(per, file_key)
            assert value['n'] == int(m[1]), (suffix, construct, value, m[1])
            assert metric(per, use_key)['n'] == int(m[2]), (suffix, construct)
            value['uses'] = int(m[2])
            values.append(value)
        add(label, rule, values, '兼容需求仍在；零值观测不再成立' if '_iter' in construct else '文件比例接近，仍支持兼容')
    for survey, n, rule in [('paper-migration', 880, '§3.2等'), ('paper-migration-2', 905, '§1.2等')]:
        add(survey + '的原始代码行', rule, [{'n': n, 'repos': 2}] * 3, '固定两例，含参考Ring；不是199库的新迁移实验')
    with open(ROOT / 'surveys/pitfalls/results-v2/catalog.tsv', encoding='utf-8', newline='') as fh:
        catalog = list(csv.DictReader(fh, delimiter='\t'))
    add('暗坑清单的固定条目', '§1.3等', [{'n': len(catalog), 'repos': None}] * 3, '与语料无关，只重建固定记录')

    def cell(v):
        s = f"{v['n']:,}〔{v['repos'] if v['repos'] is not None else '不适用'}〕"
        if 'per_1k_logical_lines' in v:
            s += f"；{v['per_1k_logical_lines']:.1f}/千逻辑行"
        if 'per_1k_code_lines' in v:
            s += f"；{v['per_1k_code_lines']:.1f}/千代码行"
        return s
    print('| 指标 | v1：数量〔库数〕 | v2：数量〔库数〕 | 纯人写：数量〔库数〕 | 规则 | 依据判断 |')
    print('|---|---|---|---|---|---|')
    for i, r in enumerate(facts, 1):
        print('| ' + ' | '.join([f'S{i:02} ' + r['label'], cell(r['v1']), cell(r['v2']), cell(r['human']), r['rule'], r['basis']]) + ' |')
    out = ROOT / 'surveys/v2-rerun/results-v2/survey-comparison.json'
    out.write_text(json.dumps(facts, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
