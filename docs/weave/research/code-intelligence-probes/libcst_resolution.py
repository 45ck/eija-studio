# Probe (not a test): run from the worktree root with a venv holding tree-sitter==0.26.0, tree-sitter-python==0.25.0, tree-sitter-typescript==0.23.2, tree-sitter-javascript==0.25.0, tree-sitter-html==0.23.2, tree-sitter-css==0.25.0, tree-sitter-json==0.24.8, tree-sitter-markdown==0.5.1, libcst==1.9.0.
# Output is quoted in docs/weave/research/code-intelligence-and-analysis.md (measured 2026-09-29, Windows 11, Python 3.12.10).
import libcst as cst, libcst.metadata as md
from libcst.metadata import FullyQualifiedNameProvider, FilePathProvider
src = '''
from .models import Workflow as W
try:
    import tomllib as toml
except ImportError:
    import tomli as toml

class A:
    def f(self):
        return W(), toml.loads("")
    def g(self):
        return self.f()

def h(x):
    return x.f()
'''
import pathlib
root = pathlib.Path('.tmp/pkgroot').resolve(); (root/'eija_studio'/'domain').mkdir(parents=True, exist_ok=True)
p = root/'eija_studio'/'domain'/'impact.py'; p.write_text(src, encoding='utf-8', newline='\n')
repo = md.FullRepoManager(str(root), [str(p)], {FullyQualifiedNameProvider})
wrapper = repo.get_metadata_wrapper_for_path(str(p))
fq = wrapper.resolve(FullyQualifiedNameProvider)
for node, names in sorted(fq.items(), key=lambda kv: kv[0].__class__.__name__):
    if isinstance(node, (cst.Call, cst.ClassDef, cst.FunctionDef)):
        tgt = node.func if isinstance(node, cst.Call) else node.name
        print(type(node).__name__, getattr(tgt,'value', getattr(tgt,'attr',tgt)).__class__.__name__, sorted((n.name, n.source.name) for n in names))
