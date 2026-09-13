"""Extrai as formulas do dashboard original para um modulo Python.

Algumas regioes carregam formulas de trinta linhas de JavaScript -- a janela
do leaderboard, o relative, o log de voltas. Reescrever isso a mao no
redesign seria copiar texto com risco de errar um caractere; e reproduzi-lo
dentro do codigo de layout tornaria o layout ilegivel.

Entao as expressoes ficam num modulo gerado, enderecadas pelo caminho do
controle no original, e os modulos de layout so as referenciam. O texto e
byte a byte o do original -- e o que garante que a telemetria nao mude.

Uso:  python3 tools/dump_formulas.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "referencia-manual" / "iRacing_Dashboard_00.djson"
TARGET = ROOT / "src" / "dash" / "generated" / "formulas.py"

#: So as regioes cujo layout e reescrito a mao precisam disso.
WANTED = ("Leaderboard Overflow", "Relative", "Practice")


def collect():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    out = {}

    def walk(node, trail, inside):
        label = node.get("Name") or node["$type"].split(",")[0].split(".")[-1]
        if label in WANTED and not inside:
            # A raiz da regiao zera o caminho: as chaves ficam curtas e
            # independentes de onde a regiao estava pendurada no original.
            here, inside = label, True
        else:
            here = f"{trail}/{label}" if trail else label
        if inside:
            for target, binding in (node.get("Bindings") or {}).items():
                formula = binding.get("Formula") or {}
                entry = {"Expression": formula.get("Expression", "")}
                if formula.get("Interpreter") is not None:
                    entry["Interpreter"] = formula["Interpreter"]
                if formula.get("JSExt") is not None:
                    entry["JSExt"] = formula["JSExt"]
                if binding.get("FormatString") is not None:
                    entry["FormatString"] = binding["FormatString"]
                out[f"{here}.{target}"] = entry
        for child in (node.get("Childrens") or []):
            walk(child, here, inside)

    for screen in data.get("Screens", []):
        for item in screen["Items"]:
            walk(item, "", False)
    return out


def main():
    formulas = collect()
    lines = [
        '"""Formulas do dashboard original, extraidas por tools/dump_formulas.py.',
        "",
        "NAO EDITE A MAO. O valor deste modulo e ser copia fiel do original:",
        "os modulos de layout referenciam estas expressoes para restilizar a",
        "regiao sem tocar na telemetria.",
        '"""',
        "",
        "FORMULAS = {",
    ]
    for key in sorted(formulas):
        lines.append(f"    {key!r}: {formulas[key]!r},")
    lines += [
        "}",
        "",
        "",
        "def binding(path, target, format_string=None):",
        '    """Binding pronto para um controle, com a formula do original."""',
        "    entry = dict(FORMULAS[f'{path}.{target}'])",
        "    out = {'Formula': {}, 'Mode': 2}",
        "    if 'JSExt' in entry:",
        "        out['Formula']['JSExt'] = entry.pop('JSExt')",
        "    if 'Interpreter' in entry:",
        "        out['Formula']['Interpreter'] = entry.pop('Interpreter')",
        "    out['Formula']['Expression'] = entry.pop('Expression')",
        "    if 'FormatString' in entry:",
        "        out['FormatString'] = entry.pop('FormatString')",
        "    if format_string is not None:",
        "        out['FormatString'] = format_string",
        "    return out",
        "",
    ]
    TARGET.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(formulas)} formulas -> {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
