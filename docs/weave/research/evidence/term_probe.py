"""Throwaway measurement probe for docs/weave/research/ubiquitous-language-ontology-and-dsls.md.

Question: how many ARCHITECTURE.md ubiquitous-language terms appear as contiguous identifier words?
Run from the repository root (measured at commit ddc43b9, Python 3.12, Windows 11):
    PYTHONUTF8=1 python docs/weave/research/evidence/term_probe.py
Read-only. Not a gate and not part of the kernel. Splitting rule: camelCase / snake_case / kebab-case,
acronym runs kept together, lowercase. Sorted output; no clock, no environment input.
"""
import ast, re, sys, json, collections, pathlib
root = pathlib.Path('.')
def split(name):
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
    name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', name)
    return [w.lower() for w in re.split(r'[_\W]+|\s+', name) if w]
arch = (root/'docs/architecture/ARCHITECTURE.md').read_text(encoding='utf-8')
terms = re.findall(r'^\*\*([^*]+?):\*\*', arch, re.M)
def idents(paths):
    out = collections.Counter()
    for p in paths:
        t = ast.parse(p.read_text(encoding='utf-8'))
        for n in ast.walk(t):
            names = []
            if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)): names.append(n.name)
            if isinstance(n, ast.arg): names.append(n.arg)
            if isinstance(n, ast.Name): names.append(n.id)
            if isinstance(n, ast.Attribute): names.append(n.attr)
            if isinstance(n, ast.keyword) and n.arg: names.append(n.arg)
            if isinstance(n, ast.alias): names.append(n.asname or n.name.split('.')[-1])
            for x in names: out[x]+=1
    return out
src = sorted((root/'src').rglob('*.py')); tst = sorted((root/'tests').rglob('*.py'))
I_src, I_tst = idents(src), idents(tst)
def seq_in(words, toks):
    k=len(words)
    return any(toks[i:i+k]==words for i in range(len(toks)-k+1))
ui = ' '.join(p.read_text(encoding='utf-8') for p in sorted((root/'src/eija_studio/resources').rglob('*')) if p.suffix in ('.html','.js','.css'))
print('files: src py', len(src), 'tests py', len(tst))
print('distinct identifiers src', len(I_src), 'tests', len(I_tst))
allw = collections.Counter()
for k,c in I_src.items():
    for w in split(k): allw[w]+=c
print('distinct words src', len(allw))
rows=[]
for t in terms:
    words = split(t.replace('-',' '))
    def cnt(I):
        return sum(c for k,c in I.items() if seq_in(words, split(k)))
    docs = len(re.findall(re.escape(t), arch, re.I))
    uihit = len(re.findall(r'\b'+r'[ _-]?'.join(words)+r'\b', ui, re.I))
    rows.append((t, ' '.join(words), cnt(I_src), cnt(I_tst), uihit))
print('term | words | src-ident-uses | test-ident-uses | ui-text-hits')
for r in rows: print(' | '.join(map(str,r)))
gl = set(w for t in terms for w in split(t))
print('top non-glossary words in src identifiers:')
stop = set('self cls str int bool none true false list dict tuple set any type object args kwargs return'.split())
for w,c in sorted(allw.items(), key=lambda x:(-x[1],x[0])):
    if w not in gl and w not in stop and len(w)>2:
        pass
top=[(w,c) for w,c in sorted(allw.items(), key=lambda x:(-x[1],x[0])) if w not in gl and w not in stop and len(w)>2][:45]
print(top)
print('--- head-word probe (class/def names only, src)')
cls = collections.defaultdict(list)
for p in src:
    t = ast.parse(p.read_text(encoding='utf-8'))
    for n in ast.walk(t):
        if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)):
            for w in split(n.name): cls[w].append(n.name)
for h in ['receipt','instance','workflow','decision','intent','authority','packet','selection','meaning','preview','candidate','review','effect','baseline','case']:
    v = sorted(set(cls.get(h,[])))
    print(h, len(v), v[:10])
