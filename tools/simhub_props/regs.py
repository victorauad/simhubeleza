# uso: regs.py <pasta de trabalho>  (le calls.tsv, imprime regs.txt)
import os, re, sys, collections
rows = collections.OrderedDict()
pat = re.compile(r'(PluginManager|IPluginExtensions|PluginBase)\.(AttachDelegate|AddProperty|AttachProperty|SetPropertyValue)<([^>]*)>\(([^)]*)\)')
for line in open(os.path.join(sys.argv[1], 'calls.tsv'), encoding='utf-8', errors='replace'):
    p = line.rstrip('\n').split('\t')
    if len(p) < 4: continue
    dll, meth, callee, segs = p
    m = pat.search(callee)
    if not m: continue
    if dll in ('SimHub.Plugins.dll',) and ('::AttachDelegate' in meth or '::SetPropertyValue' in meth or '::AddProperty' in meth) and 'PluginManager' in meth: continue
    kind, gen = m.group(2), m.group(3)
    gen = gen.split(',')[-1] if 'IPluginExtensions' in m.group(1) else gen
    toks = re.findall(r'"((?:[^"\\]|\\.)*)"|<(Concat|Format)>', segs)
    strs = [a for a, b in toks if not b]
    dyn = any(b for a, b in toks)
    cls = meth.split('::')[0]
    rows.setdefault((dll, cls.split('.')[-1]), []).append((kind, gen, dyn, strs, meth.split('::')[1]))
for (dll, cls), items in rows.items():
    print('##', dll, cls)
    seen = set()
    for kind, gen, dyn, strs, mname in items:
        key = (kind, gen, dyn, tuple(strs))
        if key in seen: continue
        seen.add(key)
        print('	'.join(['', kind, gen, 'DYN' if dyn else '', ' | '.join(strs)[:400], mname]))
