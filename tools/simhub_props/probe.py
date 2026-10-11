# uso: probe.py <pasta do SimHub> <pasta de trabalho>
import os, re, sys, urllib.request, urllib.parse, json, concurrent.futures as cf

def get(name):
    try:
        r = urllib.request.urlopen('http://localhost:8888/api/GetProperty/' + urllib.parse.quote(name, safe='.'), timeout=5)
        return r.status, r.read().decode('utf-8', 'replace')
    except Exception as e:
        return 0, str(e)

names = [l.strip() for l in open(os.path.join(sys.argv[1], 'RSC.iRacingExtraProperties.txt'), encoding='utf-8', errors='replace') if l.strip()]
# families: replace each 2-digit group with NN, keep first sample
fams = {}
for n in names:
    k = re.sub(r'(?<=_)\d\d(?=_|$)', 'NN', n)
    fams.setdefault(k, n)
extra = [
 'PersistantTrackerPlugin.DriverAhead_NN_Gap', 'PersistantTrackerPlugin.DriverBehind_NN_Gap',
 'PersistantTrackerPlugin.PreviousLap_NN',
]
for e in extra: fams.setdefault(e, e.replace('NN', '00'))

def probe(pat):
    n = pat.count('NN')
    res = []
    if n == 0:
        s, v = get(pat); return pat, s, v[:60], None
    # vary only the first NN, others fixed to sample digits
    sample = fams[pat]
    found = []
    for i in range(0, 80):
        nm = pat.replace('NN', '%02d' % i, 1)
        # fill remaining NN with sample's later groups or 01
        rest = re.findall(r'(?<=_)\d\d(?=_|$)', sample)
        for d in rest[1:]:
            nm = nm.replace('NN', d, 1)
        nm = nm.replace('NN', '01')
        s, v = get(nm)
        if s == 200: found.append(i)
    return pat, None, None, found

out = []
with cf.ThreadPoolExecutor(8) as ex:
    for pat, s, v, found in ex.map(probe, list(fams.keys())):
        if found is None:
            out.append('%s\t%s\t%s' % (pat, s, v.replace('\t', ' ').replace('\n', ' ')))
        else:
            rng = ('%d..%d' % (min(found), max(found))) if found else 'none(204)'
            out.append('%s\tRANGE\t%s\t%d hits' % (pat, rng, len(found)))
open(os.path.join(sys.argv[2], 'probe_rsc.tsv'), 'w', encoding='utf-8').write('\n'.join(sorted(out)))
print(len(out))
