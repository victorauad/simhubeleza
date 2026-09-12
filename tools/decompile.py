"""Converte um .djson feito a mao em codigo-fonte Python do DSL.

Roda uma vez por dashboard. A saida e o ponto de partida da refatoracao: ja
nasce com paridade garantida, porque cada campo que difere do default do tipo
e emitido explicitamente.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from simhub.defaults import DEFAULTS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "referencia-manual"
OUT = ROOT / "src" / "dash" / "generated"

INDENT = "    "

#: Subarvores ja reescritas a mao. O decompilador emite a chamada ao modulo em
#: vez de reexportar a arvore, para que a versao refatorada seja a unica fonte.
EXTRACTED = {
    "Leaderboard": ("from dash.leaderboard import layer as leaderboard", "leaderboard()"),
    "Top Component": ("from dash.top_bar import layer as top_bar", "top_bar()"),
}


def short_type(node):
    return node["$type"].split(",")[0].split(".")[-1]


def literal(value, depth):
    """Repr Python de um valor JSON, quebrando dicts/listas em varias linhas."""
    pad = INDENT * depth
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = [f"{pad}{INDENT}{json.dumps(k)}: {literal(v, depth + 1)},"
                 for k, v in value.items()]
        return "{\n" + "\n".join(lines) + f"\n{pad}}}"
    if isinstance(value, list):
        if not value:
            return "[]"
        lines = [f"{pad}{INDENT}{literal(v, depth + 1)}," for v in value]
        return "[\n" + "\n".join(lines) + f"\n{pad}]"
    return repr(value)


def binding_call(binding, depth):
    """Emite ncalc(...) / js(...) quando o binding tem o shape canonico."""
    formula = binding.get("Formula") or {}
    expression = formula.get("Expression")
    extra = set(binding) - {"Formula", "Mode", "FormatString"}
    known_formula = set(formula) <= {"Expression", "JSExt", "Interpreter"}

    if expression is None or extra or binding.get("Mode") != 2 or not known_formula:
        return literal(binding, depth)

    is_js = formula.get("Interpreter") == 1
    fn = "js" if is_js else "ncalc"
    fmt = binding.get("FormatString")
    args = [repr(expression)]
    if is_js and formula.get("JSExt"):
        args.append(f"jsext={formula['JSExt']!r}")
    if fmt is not None:
        if not is_js:
            return f"formatted({expression!r}, {fmt!r})"
        args.append(f"format_string={fmt!r}")
    return f"{fn}({', '.join(args)})"


def emit(node, depth=1, extracted=None):
    """Gera a chamada de construtor para um no e seus filhos."""
    pad = INDENT * depth
    name = node.get("Name")
    if name in EXTRACTED:
        import_line, call = EXTRACTED[name]
        if extracted is not None:
            extracted.add(import_line)
        return f"{pad}{call}"
    type_name = short_type(node)
    defaults = DEFAULTS[type_name]
    children = node.get("Childrens") or []

    parts = []
    for child in children:
        parts.append(emit(child, depth + 1, extracted) + ",")

    if "Name" in node:
        parts.append(f"{pad}{INDENT}name={node['Name']!r},")

    for key, value in node.items():
        if key in ("$type", "Childrens", "Bindings", "Name"):
            continue
        if key in defaults and defaults[key] == value:
            continue
        parts.append(f"{pad}{INDENT}{key}={literal(value, depth + 1)},")

    for key in defaults:
        if key not in node:
            parts.append(f"{pad}{INDENT}{key}=OFF,")

    bindings = node.get("Bindings")
    if bindings:
        inner = [f"{pad}{INDENT * 2}{json.dumps(target)}: "
                 f"{binding_call(binding, depth + 2)},"
                 for target, binding in bindings.items()]
        parts.append(f"{pad}{INDENT}bindings={{\n" + "\n".join(inner)
                     + f"\n{pad}{INDENT}}},")

    if not parts:
        return f"{pad}{type_name}()"
    return f"{pad}{type_name}(\n" + "\n".join(parts) + f"\n{pad})"


def decompile(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    screens = data.pop("Screens")

    items = []
    screen_shells = []
    for screen in screens:
        screen_items = screen.pop("Items")
        screen_shells.append(screen)
        items.append(screen_items)

    if len(items) != 1:
        raise NotImplementedError(f"{path.name}: esperado 1 tela, achei {len(items)}")

    extracted = set()
    tree = ",\n".join(emit(item, 2, extracted) for item in items[0])
    extra_imports = "".join(line + "\n" for line in sorted(extracted))

    return f'''"""Dashboard {path.stem} -- arvore de controles.

GERADO por tools/decompile.py a partir de referencia-manual/{path.name}.
Ponto de partida da refatoracao; paridade validada por tools/parity.py.
"""

{extra_imports}from simhub.bindings import formatted, js, ncalc
from simhub.model import (
    OFF, ChartItem, GearText, GradientItem, GroupItem, ImageItem,
    Layer, LinearGaugeItem, RectangleItem, TextItem, WidgetItem,
)

#: Campos do dashboard fora da arvore de controles.
SHELL = {literal(data, 0)}

#: Campos da tela fora da lista de itens.
SCREEN = {literal(screen_shells[0], 0)}


def items():
    """Itens de nivel superior da tela."""
    return [
{tree},
    ]
'''


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "__init__.py").write_text("", encoding="utf-8")

    for path in sorted(REF.glob("*.djson")):
        module = path.stem.lower().replace(" ", "_")
        target = OUT / f"{module}.py"
        target.write_text(decompile(path), encoding="utf-8")
        lines = target.read_text(encoding="utf-8").count("\n")
        print(f"{path.name:32s} -> src/dash/generated/{module}.py ({lines} linhas)")


if __name__ == "__main__":
    sys.exit(main())
