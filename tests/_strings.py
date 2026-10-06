"""Raccoglie i testi traducibili della libreria (il primo argomento di ogni
tr("...") in st_language/ e i nomi delle figure), per controllare che i
cataloghi in st_language/locales/ li traducano tutti."""

import ast
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def library_strings():
    out = set()
    for path in sorted(glob.glob(os.path.join(ROOT, "st_language", "*.py"))):
        tree = ast.parse(open(path, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "tr" \
                    and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                out.add(node.args[0].value)
    from st_language.notation import _NOTE_VALUES
    out |= {name for _beats, *names in _NOTE_VALUES for name in names}
    return sorted(s for s in out if s.strip())
