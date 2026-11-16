"""Build the 35-row count comparison from the three committed result sets.

Usage: python surveys/v2-rerun/compare.py
Writes comparison.json and prints a Markdown table. Human verdicts live in the
write-up; numeric records are never inferred from a hand-labelled v1 conclusion.
"""
import collections
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'surveys/corpus-counts'))
import counts as C

TITLES = ['null', '前缀!与not', 'Autoload.x = self登记', '@abstract', '剩余参数', '含await的lambda',
          'lambda命名、默认值与捕获', '协程方法作为实参', 'assert及消息', 'is_instance_valid',
          '静态变量与初始化', 'PREDELETE', '线程与线程池', 'create_timer参数', 'parent与owner',
          '自身free、换脚本及queue_free', 'pop_at/back/front', '_get与_set', '普通引号跨行', '@tool',
          'preload脚本与类级用法', 'enum用法', '内部类', '排版主要指标', '给下方节点成员赋值',
          '跨文件类级访问', '_init参数', '新增关键字作名字', '加载依赖环', 'String下标赋值候选',
          '###文档候选', '失败可查询的API', '弱引用', 'autoload名作类型', '对象边界API']


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def statistic(repos, keys):
    if isinstance(keys, str):
        keys = [keys]
    values = [sum(row.get(k, 0) for k in keys) for row in repos.values()]
    return {'n': sum(values), 'repos': sum(v > 0 for v in values)}


def parse_counts(suffix):
    base = ROOT / 'surveys' / 'corpus-counts' / suffix
    metrics = load(base / 'metrics.json')
    repos = metrics['repos']
    rows = {}
    def row(number, fields):
        rows[number] = {label: statistic(repos, keys) for label, keys in fields}
    row(1, [('null', ['null_compare', 'null_other']), ('比较', 'null_compare')])
    row(2, [('!', 'bang'), ('not', 'not')])
    lines = (base / 'autoload_self.txt').read_text(encoding='utf-8').splitlines()
    counts = collections.Counter(ln.split('/')[0] for ln in lines if '/' in ln and not ln.startswith('total '))
    direct = collections.Counter()
    corpus = ROOT / 'corpus' / ('v1' if suffix == 'results' else 'v2')
    for line in lines:
        match = re.match(r'([^/]+)/(.+?):(\d+) ', line)
        if not match:
            continue
        name, path, number = match.groups()
        tokens = [t for t in C.G.tokenize((corpus / name / path).read_text(encoding='utf-8', errors='replace')) if t.k != 'NL']
        ready = []
        for index, token in enumerate(tokens[:-1]):
            if token.v == 'func' and tokens[index + 1].v == '_ready':
                start, end = C.func_body(tokens, index)
                if start < end:
                    ready.append((tokens[start].line, tokens[end - 1].line))
        direct[name] += any(start <= int(number) <= end for start, end in ready)
    rows[3] = {'登记候选': statistic({r: {'n': n} for r, n in counts.items()}, 'n'),
               '词法位于_ready': statistic({r: {'n': n} for r, n in direct.items()}, 'n')}
    row(4, [('类', 'abstract_class'), ('方法', 'abstract_func')])
    row(5, [('剩余参数', 'rest')])
    row(6, [('lambda', 'lambda'), ('含await', 'lambda_await')])
    row(7, [('命名', 'lambda_named'), ('默认值', 'lambda_default'), ('捕获赋值', 'lambda_capture_assign'), ('经捕获成员赋值', 'lambda_capture_member')])
    row(8, [('作值', 'coroutine_value'), ('connect', 'coroutine_connect')])
    row(9, [('assert', 'assert'), ('含await', 'assert_await'), ('消息含调用', 'assert_message_call')])
    row(10, [('有效性检查', 'is_instance_valid')])
    row(11, [('static var', 'static_var'), ('无初值的其他类型', 'static_var_other'), ('静态初始化', 'static_init')])
    row(12, [('PREDELETE', 'predelete')])
    row(13, [('Thread.new', 'thread_new'), ('线程池', 'worker_pool')])
    row(14, [('timer', 'create_timer'), ('仅传时间', 'create_timer_time_only')])
    row(15, [('parent', 'parent'), ('parent判空', 'parent_tested'), ('owner访问成员', 'owner_member'), ('owner判空', 'owner_tested')])
    row(16, [('free自身', 'free_self'), ('换脚本', 'set_script_self'), ('信号处理函数free', 'free_in_handler'), ('queue_free', 'queue_free')])
    row(17, [('pop_at', 'pop_at'), ('pop_back', 'pop_back'), ('pop_front', 'pop_front')])
    row(18, [('_get', '_get'), ('_set', '_set')])
    sites = metrics['sites'].get('string with a line break', [])
    cs = collections.Counter(s.split('/')[0] for s in sites)
    rows[19] = {'跨行字符串': statistic({r: {'n': n} for r, n in cs.items()}, 'n')}
    row(20, [('@tool文件', ['tool_game', 'tool_plugin', 'tool_tool', 'tool_demos', 'tool_demo']), ('编辑器API', 'tool_editor_api')])
    row(21, [('preload脚本', 'preload_gd'), ('常量', 'preload_gd_const'), ('常量作类型', 'alias_type')])
    row(22, [('enum', 'enum'), ('无0值', 'enum_without_zero'), ('as转换', 'enum_as'), ('作Dictionary', 'enum_dict')])
    text = (base / 'inner_classes.txt').read_text(encoding='utf-8').split('PER REPOSITORY:')[1].split('DETAIL')[0]
    inner = {}
    for match in re.finditer(r'^\s+(\S+)\s+(?:game|plugin|tool|demos?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$', text, re.M):
        inner[match[1]] = {'files': int(match[3]), 'classes': int(match[4]), 'other': int(match[6])}
    rows[23] = {title: statistic(inner, key) for title, key in [('内部类', 'classes'), ('所在文件', 'files'), ('跨文件使用', 'other')]}
    layout = load(base / 'layout.json')
    rows[24] = {}
    for title, group, key in [('制表符', 'files', 'tabs'), ('空格', 'files', 'spaces'), ('超过100列', 'code_lines', '>100'), ('顶层空两行', 'blank_before_top', '2')]:
        rows[24][title] = statistic({r: {'n': c.get(group, {}).get(key, 0)} for r, c in layout.items()}, 'n')
    ancestor = {}
    for m in re.finditer(r'^(\S+)\s+(\d+)/(\d+)\s+(\d+)/(\d+)\s+(\d+)/(\d+)\s+(\d+)/(\d+)\s+', (base / 'ancestor_assignments.txt').read_text(encoding='utf-8'), re.M):
        a = list(map(int, m.groups()[1:])); ancestor[m[1]] = dict(same=sum(a[:2]), sub=sum(a[2:4]), no_init=sum(a[4:6]))
    rows[25] = {label: statistic(ancestor, key) for label, key in [('本场景成员', 'same'), ('子场景内部成员', 'sub'), ('无初值', 'no_init')]}
    classes = {}
    for m in re.finditer(r'^(\S+): (\d+) of (\d+) classes would break(?: \(([^)]*)\))?;([^\n]*)', (base / 'class_level_access.txt').read_text(encoding='utf-8'), re.M):
        classes[m[1]] = {'breaking': int(m[2]), 'classes': int(m[3])}
        for short in ('static', 'type', 'const', 'unnamed'):
            hit = re.search(rf'\b{short} (\d+)', m[4] or '')
            classes[m[1]][f'by_{short}'] = int(hit[1]) if hit else 0
        for key in ('static method', 'enum, constant or inner class as a type', 'in a constant expression'):
            hit = re.search(re.escape(key) + r' (\d+)', m[5]); classes[m[1]][key] = int(hit[1]) if hit else 0
    rows[26] = {label: statistic(classes, key) for label, key in [
        ('受影响类', 'breaking'), ('静态类', 'by_static'), ('类型类', 'by_type'),
        ('未命名', 'by_unnamed'), ('静态调用', 'static method'),
        ('作类型', 'enum, constant or inner class as a type'), ('常量式', 'in a constant expression')]}
    metadata = load(ROOT / 'corpus' / ('v1.json' if suffix == 'results' else 'v2.json'))
    games = {r['name'] for r in metadata['repos'] if r['group'] == 'game'}
    game_classes = {name: value for name, value in classes.items() if name in games}
    rows[26]['游戏类'] = statistic(game_classes, 'breaking')
    rows[26]['游戏静态类'] = statistic(game_classes, 'by_static')
    rows[26]['游戏具名类'] = statistic(game_classes, 'classes')
    init = load(base / 'init_params.json')
    rows[27] = {'Node': statistic(init, ['Node, some required', 'Node, all with defaults']), 'Resource': statistic(init, ['Resource, some required', 'Resource, all with defaults'])}
    row(28, [('名字冲突', ['keyword_after_dot', 'keyword_elsewhere'])])
    cycles = collections.defaultdict(collections.Counter)
    for m in re.finditer(r'^(script|scene) cycle: (\S+) ', (base / 'preload_cycles.txt').read_text(encoding='utf-8'), re.M):
        cycles[m[2]][m[1]] += 1
    rows[29] = {label: statistic(cycles, key) for label, key in [('脚本环', 'script'), ('资源环', 'scene')]}
    strings = collections.Counter()
    for m in re.finditer(r'^(\S+?)/.+:\d+ \(', (base / 'string_index.txt').read_text(encoding='utf-8'), re.M):
        strings[m[1]] += 1
    rows[30] = {'String下标赋值候选': statistic({r: {'n': n} for r, n in strings.items()}, 'n')}
    row(31, [('文档块', 'doc_block'), ('仅###', 'doc_block_hashes'), ('混写', 'doc_block_mixed')])
    rows[32] = {}
    for m in re.finditer(r'^(FileAccess.open|DirAccess.open|FileAccess.get_file_as_string)\s+(\d+)\s+(\d+)\s+', (base / 'null_failures.txt').read_text(encoding='utf-8'), re.M):
        rows[32][m[1]] = {'n': int(m[2]), 'repos': int(m[3])}
    weak = collections.defaultdict(collections.Counter)
    for m in re.finditer(r'^(\S+?)/.+:\d+ \([^)]*\): (.+)$', (base / 'weak_refs.txt').read_text(encoding='utf-8'), re.M):
        weak[m[1]][m[2]] += 1
    rows[33] = {k: statistic(weak, k) for k in ('weakref(', 'WeakRef', '.get_ref(')}
    rows[33]['游戏weakref('] = statistic({name: value for name, value in weak.items() if name in games}, 'weakref(')
    types = {}
    text = (base / 'autoload_types.txt').read_text(encoding='utf-8').split('== type uses per repository')[1].split('== all type uses')[0]
    for m in re.finditer(r'^\s+(\S+) \[[^]]+\]: (\d+) ', text, re.M):
        types[m[1]] = {'n': int(m[2])}
    rows[34] = {'autoload类型': statistic(types, 'n')}
    engine = load(base / 'engine_objects.json')
    rows[35] = {title: statistic(engine, key) for title, key in [('返回对象', 'calls'), ('对象属性', 'reads'), ('信号连接', 'connections'), ('虚函数覆盖', 'overrides')]}
    return rows, sum(r.get('lines', 0) for r in repos.values())


def main():
    sets = [parse_counts(s) for s in ('results', 'results-v2', 'results-v2-human')]
    source = (ROOT / 'surveys/corpus-counts.md').read_text(encoding='utf-8')
    labels = [ln.split('|')[1:4] for ln in source.splitlines() if ln.startswith('| ')][1:1 + len(TITLES)]
    result = {}
    basis = {7: '旧零值前提失效；见样本', 13: '线程用途更广；推迟依据减弱',
             14: '默认参数覆盖率下降；见复核', 16: '安全特例前提失效；规则未改',
             18: '不拦截引擎属性的全称前提失效', 19: '不再几乎全是测试；仍可机械改写',
             20: '现行已纳入@tool；需求更广', 25: '跨子场景写入均有初值；必填检查依据仍在',
             28: '更支持上下文关键字；旧零值失效', 29: '加载环的迁移代价见复核',
             30: '样本3/50为字符替换；旧无替换前提失效', 31: '纯###均为标题的前提失效',
             33: '游戏零使用的前提失效；优先级待复核'}
    print('| 计数 | v1：数量〔仓库数〕 | v2：数量〔仓库数〕 | v2纯人写：数量〔仓库数〕 | 用于 | 依据判断 |')
    print('|---|---|---|---|---|---|')
    for n, (label, _, rule) in enumerate(labels, 1):
        if n == 3:
            label = '`Autoload.x = self` 登记（原脚本口径）'
        if n == 20:
            rule = '§2.3：现行第一版已有@tool，规则【待定】'
        records = [s[0][n] for s in sets]
        verdict = basis.get(n, '仍有直接使用依据；不由频次证明语义')
        result[n] = {'label': label.strip(), 'rule': rule.strip(), 'v1': records[0], 'v2': records[1], 'human': records[2], 'basis': verdict}
        cells = ['；'.join(f'{k} {v["n"]:,}〔{v["repos"]}〕' for k, v in record.items()) for record in records]
        used = re.sub(r'（脚本见.*?）', '', rule.strip())
        if n == 35:
            used = '§10.2：按高频API审核对象可空性'
        print('| ' + ' | '.join([f'C{n:02} {TITLES[n-1]}', *cells, used, verdict]) + ' |')
    result['code_lines'] = [s[1] for s in sets]
    out = ROOT / 'surveys/v2-rerun/results-v2/comparison.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1, sort_keys=False) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
