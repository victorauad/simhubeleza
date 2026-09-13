"""Deriva defaults por tipo de controle a partir dos .djson feitos a mao.

Um campo so vira default quando aparece em TODAS as instancias daquele tipo;
o valor escolhido e o mais frequente. Assim o decompilador pode omitir campos
sem risco de introduzir ou perder chaves na reconstrucao.
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REF = Path(__file__).resolve().parent.parent / "referencia-manual"
OUT = Path(__file__).resolve().parent.parent / "src" / "simhub" / "defaults.py"

# Chaves estruturais: nunca viram default, sao tratadas a parte pelo DSL.
STRUCTURAL = {"$type", "Childrens", "Bindings", "Name"}


def short_type(node):
    return node["$type"].split(",")[0].split(".")[-1]


def walk(node, out):
    out.append(node)
    for child in node.get("Childrens") or []:
        walk(child, out)


def collect_nodes():
    nodes = []
    for path in sorted(REF.glob("*.djson")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for screen in data.get("Screens", []):
            for item in screen["Items"]:
                walk(item, nodes)
    return nodes


def derive(nodes):
    by_type = defaultdict(list)
    for node in nodes:
        by_type[short_type(node)].append(node)

    defaults = {}
    for type_name, instances in sorted(by_type.items()):
        common = set(instances[0])
        for inst in instances[1:]:
            common &= set(inst)
        common -= STRUCTURAL

        fields = {}
        for key in sorted(common):
            values = Counter(json.dumps(i[key], sort_keys=True) for i in instances)
            fields[key] = json.loads(values.most_common(1)[0][0])
        defaults[type_name] = fields

    # O "$type" completo nao e derivavel do nome curto: alguns controles vivem
    # em sub-namespaces (GearText fica em ...Models.BuiltIn).
    types = {name: insts[0]["$type"] for name, insts in by_type.items()}
    return defaults, by_type, types


def main():
    nodes = collect_nodes()
    defaults, by_type, types = derive(nodes)

    def pyliteral(obj):
        text = json.dumps(obj, indent=4, sort_keys=True, ensure_ascii=False)
        return (text.replace(": true", ": True").replace(": false", ": False")
                    .replace(": null", ": None"))

    OUT.write_text(
        '"""Defaults e nomes de tipo dos controles.\n\n'
        "GERADO por tools/derive_defaults.py -- nao editar a mao.\n"
        'Um campo so entra em DEFAULTS se aparece em todas as instancias do tipo.\n"""\n\n'
        "#: Nome curto -> \"$type\" completo gravado pelo SimHub.\n"
        "TYPES = " + pyliteral(types) + "\n\n"
        "DEFAULTS = " + pyliteral(defaults) + "\n",
        encoding="utf-8",
    )

    for type_name in sorted(by_type):
        print(f"{len(by_type[type_name]):4d} {type_name:18s} "
              f"{len(defaults[type_name])} campos default")
    print(f"\n-> {OUT.relative_to(OUT.parent.parent.parent)}")


if __name__ == "__main__":
    sys.exit(main())
