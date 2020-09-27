import sys
import json

classes = [
"",
"add",
"and",
"call",
"cmov",
"cmp",
"div",
"jmp",
# "jmp.cond",
"lea",
"leave",
"mov",
"mul",
"neg",
"nop",
"not",
"or",
"pop",
"push",
"rep",
"ret",
"set",
"shift",
"sse",
"sub",
"test",
"xchg",
"xor",
]

classifier = dict(zip(classes, [0] * len(classes)))

def classify(op):
    for i in ('ss', 'ssl', 'ps', 'pd', 'sw', 'sb', 'wd', 'sd', 'db', 'dd', 'bw', 'dq', 'gb', 'gw', 'gtd', 'xub'):
        if op.endswith(i):
            return 'sse'
    for i in ('psub', 'vp'):
        if op.startswith(i):
            return 'sse'
    if op.startswith('mov') or op.startswith('lod'):
        return 'mov'
    if op.startswith('add') or op.startswith('adc') or op.startswith('xadd'):
        return 'add'
    if op == 'lea':
        return op
    if op == 'jmp' or op.startswith('ljmp'):
        return 'jmp'
    if op.startswith('leave'):
        return 'leave'
    if op.startswith('nop'):
        return 'nop'
    if op.startswith('j'):
        return 'jmp'  # used to be jmp.cond
    if op.startswith('cmov'):
        return 'cmov'
    if op.startswith('and'):
        return 'and'
    if op.startswith('call') or op.startswith('lcall'):
        return 'call'
    if op.startswith('cmp') or op.startswith('sca'):
        return 'cmp'
    if op.startswith('div') or op.startswith('idiv'):
        return 'div'
    if op.startswith('mul') or op.startswith('imul'):
        return 'mul'
    if op.startswith('neg'):
        return 'neg'
    if op.startswith('or'):
        return 'or'
    if op.startswith('not'):
        return 'not'
    if op.startswith('pop'):
        return 'pop'
    if op.startswith('push'):
        return 'push'
    if op.startswith('rep') or op.startswith('loop'):
        return 'rep'
    if op.startswith('ret') or op.startswith('lret') or op.endswith('ret'):
        return 'ret'
    if op.startswith('sub') or op.startswith('sbb') or op.startswith('dec'):
        return 'sub'
    if op.startswith('bt') or op.startswith('clt') or op.startswith('set') or op in ['cwtl']:
        return 'set'
    if op.startswith('sh'):
        return 'shift'
    for i in set(['sar', 'sal', 'rcr', 'rcl', 'ror', 'rol', 'bsr']):
        if op.startswith(i):
            return 'shift'
    if op.startswith('xchg') or op == 'bswap':
        return 'xchg'
    if op.startswith('xor'):
        return 'xor'
    if op.startswith('test'):
        return 'test'
    if op.startswith('enter'):
        return ''
    if op in ['cs', 'ds', 'es', 'gs'] or op.startswith('data'):
        return ''
    if op.startswith('f') or op.startswith('int'):
        return ''
    if op in set(['lock', 'hlt', 'icebp', 'in', 'out', 'sahf', 'lahf', 'xlat', 'bnd', 'clc', 'cld', 'cli', 'rdtsc', 'cmc', 'verr']):
        return ''
    if op.startswith('rex') or op.startswith('st') or op.startswith('inc') or op.startswith('ins') or op.startswith('outs'):
        return ''
    print op
    raise ValueError()

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    tup = line.split()
    if len(tup) != 2:
        continue
    tup[1] = classify(tup[1])
    classifier[tup[1]] = classifier.get(tup[1], 0) + int(tup[0])

del classifier['']

total = float(sum(classifier.values()))
distribution = {}
for k, num in classifier.items():
    distribution[k] = num / total
json_file = sys.argv[1]
with open(json_file, 'w') as f:
    json.dump({'num': classifier, 'ratio': distribution}, f, indent=2)
# for k in sorted(classifier):
    # if classifier[k] == 0.0:
    #     print str(0.0001) + ', '
    # else:
    #     print str(classifier[k]/total)+', '
