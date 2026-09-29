# Probe (not a test): run from the worktree root with a venv holding tree-sitter==0.26.0, tree-sitter-python==0.25.0, tree-sitter-typescript==0.23.2, tree-sitter-javascript==0.25.0, tree-sitter-html==0.23.2, tree-sitter-css==0.25.0, tree-sitter-json==0.24.8, tree-sitter-markdown==0.5.1, libcst==1.9.0.
# Output is quoted in docs/weave/research/code-intelligence-and-analysis.md (measured 2026-09-29, Windows 11, Python 3.12.10).
import ast
import hashlib

import tree_sitter_css as tsc
import tree_sitter_html as tsh
import tree_sitter_javascript as tsj
import tree_sitter_json as tsjson
import tree_sitter_markdown as tsm
import tree_sitter_python as tsp
import tree_sitter_typescript as tst
from tree_sitter import Language, Parser

L = {
 'python': Language(tsp.language()),
 'typescript': Language(tst.language_typescript()),
 'tsx': Language(tst.language_tsx()),
 'javascript': Language(tsj.language()),
 'html': Language(tsh.language()),
 'css': Language(tsc.language()),
 'json': Language(tsjson.language()),
 'markdown': Language(tsm.language()),
}
print('ABI versions:', {k: v.abi_version for k,v in L.items()})
def walk(n, depth=0):
    yield n, depth
    for c in n.children: yield from walk(c, depth+1)
def digest(lang, src: bytes):
    p = Parser(L[lang]); t = p.parse(src)
    h = hashlib.sha256()
    cnt = 0
    for n, d in walk(t.root_node):
        h.update(f"{d}:{n.type}:{n.start_byte}:{n.end_byte}\n".encode()); cnt += 1
    return h.hexdigest()[:12], cnt, t.root_node.has_error
samples = {
 'python': "class A:\n    def f(self, x: int) -> int:\n        return x\n\ndef g():\n    pass\n",
 'typescript': "export interface I { a: number }\nexport class C implements I { a = 1; m(): void {} }\nexport function f(x: string): string { return x }\n",
 'html': "<!doctype html><html><body><div id=\"app\" class=\"a b\"><button data-testid=\"go\">Go</button></div></body></html>\n",
 'css': ".a > .b:hover { color: red } #x { margin: 0 } @media (min-width: 1px) { .c { top: 0 } }\n",
 'json': '{"b": 1, "a": [1,2,{"c": null}]}\n',
 'markdown': "# Title\n\nSome text with [link](x.md)\n\n## Sub\n\n- item\n\n```python\nx=1\n```\n",
}
for lang, s in samples.items():
    b = s.encode()
    a = digest(lang, b); a2 = digest(lang, b)
    crlf = digest(lang, s.replace("\n", "\r\n").encode())
    print(f"{lang:11s} run1={a} run2={a2} same={a==a2}  LF-vs-CRLF same_tree_positions={a[0]==crlf[0]} nodes {a[1]} vs {crlf[1]}")
# error recovery
bad = b"class A:\n    def f(self, x:\n        return x\n\ndef g():\n    pass\n"
p = Parser(L['python']); t = p.parse(bad)
defs = [n.child_by_field_name('name').text.decode() for n,_ in walk(t.root_node) if n.type in ('function_definition','class_definition') and n.child_by_field_name('name')]
print('broken python: has_error=', t.root_node.has_error, 'defs recovered=', defs)
try:
    ast.parse(bad.decode())
except SyntaxError as e: print('ast.parse on same: SyntaxError', e.msg)
# non-ascii offsets
src = "def f():\n    s = 'héllo😀'; return zz\n"
tree = ast.parse(src)
ret = tree.body[0].body[1]
nm = ret.value
print('ast col_offset (UTF-8 bytes) of zz:', nm.col_offset)
tt = Parser(L['python']).parse(src.encode())
ident = next(n for n,_ in walk(tt.root_node) if n.type=='identifier' and n.text==b'zz')
line = src.split('\n')[1]
print('tree-sitter start_point (byte col):', ident.start_point, ' python str index:', line.index('zz'), ' utf16 col:', len(line[:line.index('zz')].encode('utf-16-le'))//2)
