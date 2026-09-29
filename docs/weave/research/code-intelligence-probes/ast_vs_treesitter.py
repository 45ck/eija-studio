# Probe (not a test): run from the worktree root with a venv holding tree-sitter==0.26.0, tree-sitter-python==0.25.0, tree-sitter-typescript==0.23.2, tree-sitter-javascript==0.25.0, tree-sitter-html==0.23.2, tree-sitter-css==0.25.0, tree-sitter-json==0.24.8, tree-sitter-markdown==0.5.1, libcst==1.9.0.
# Output is quoted in docs/weave/research/code-intelligence-and-analysis.md (measured 2026-09-29, Windows 11, Python 3.12.10).
import ast, time, pathlib, hashlib
from tree_sitter import Language, Parser
import tree_sitter_python as tsp
P = Parser(Language(tsp.language()))
files = sorted(pathlib.Path('src').rglob('*.py'), key=lambda p: p.as_posix())
def ts_defs(b):
    t = P.parse(b); out=[]
    def w(n, prefix):
        for c in n.children:
            if c.type in ('function_definition','class_definition'):
                nm = c.child_by_field_name('name').text.decode()
                q = prefix+[nm]; out.append('.'.join(q)); w(c.child_by_field_name('body'), q)
            elif c.type == 'decorated_definition':
                w(c, prefix)
            elif c.type in ('if_statement','try_statement','block','else_clause','elif_clause','except_clause','with_statement','for_statement','while_statement'):
                w(c, prefix)
    w(t.root_node, []); return out
def ast_defs(src):
    out=[]
    def w(body, prefix):
        for n in body:
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                q=prefix+[n.name]; out.append('.'.join(q)); w(n.body,q)
            else:
                for f in ('body','orelse','finalbody'):
                    if isinstance(getattr(n,f,None), list): w(getattr(n,f), prefix)
                for h in getattr(n,'handlers',[]): w(h.body,prefix)
    w(ast.parse(src).body, []); return out
tot_a=tot_t=0; mism=[]
t0=time.perf_counter(); A={}; 
for f in files: A[f]=ast_defs(f.read_bytes().decode('utf-8'))
ta=time.perf_counter()-t0
t0=time.perf_counter(); T={}
for f in files: T[f]=ts_defs(f.read_bytes())
tt=time.perf_counter()-t0
for f in files:
    if sorted(A[f])!=sorted(T[f]): mism.append(f.as_posix())
print(len(files),'files; ast defs',sum(map(len,A.values())),'ts defs',sum(map(len,T.values())),'mismatching files',mism, f'ast {ta*1000:.0f} ms ts {tt*1000:.0f} ms')
