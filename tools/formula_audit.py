"""Audita as formulas entre o dashboard original e o redesenhado.

O redesign muda layout e estilo, nao a telemetria. Entao a garantia que
interessa nao e mais a paridade estrutural (que diverge de proposito), e sim:
**nenhuma formula do original pode desaparecer**.

A comparacao e por texto normalizado da expressao, nao por controle: um campo
pode mudar de posicao, tamanho, cor ou ate de nome e ainda assim preservar a
logica. Some quando some de verdade.

Uso:  python3 tools/formula_audit.py [--new PASTA] [--old PASTA]
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash.fallback import unwrap  # noqa: E402
from dash.states import SESSION_TYPE_JS  # noqa: E402

#: Propriedades do original que nao existem no SimHub, trocadas de proposito
#: pelo caminho certo (conferido na API local -- docs/propriedades.txt).
PROPERTY_FIXES = [
    (re.compile(r"\$prop\((['\"])SessionTypeName\1\)"), SESSION_TYPE_JS),
]


def fixed(expression):
    """Forma de comparacao do original com as propriedades corrigidas.

    Sem nenhum espaco fora de literais: o `normalize` apara espaco so nas
    pontas de cada trecho entre literais, entao trocar uma propriedade muda
    onde os trechos comecam e deixa sobra de espaco diferente dos dois lados.
    """
    for pattern, replacement in PROPERTY_FIXES:
        expression = pattern.sub(lambda _: replacement, expression)
    return squeeze(expression)


def squeeze(expression):
    parts = re.split(r"('[^']*'|\"[^\"]*\")", expression)
    return "".join(p if i % 2 else re.sub(r"\s+", "", p)
                   for i, p in enumerate(parts))


def normalize(expression):
    """Colapsa espacos fora de literais de string.

    Em NCalc e JavaScript o espacamento nao e semantico, mas dentro de aspas
    ele e -- ' 0.0' nao e '0.0'. Entao literais sao preservados intactos.
    """
    parts = re.split(r"('[^']*'|\"[^\"]*\")", expression)
    for i, part in enumerate(parts):
        if i % 2 == 0:
            parts[i] = re.sub(r"\s+", " ", part).strip()
    return "".join(parts).strip()


#: Nomes de cor CSS e hex ARGB que aparecem em formulas de cor.
COLOR_LITERAL = re.compile(
    r"'(#[0-9A-Fa-f]{6,8}|transparent|darkcyan|lawngreen|darkgray|dimgray|red|"
    r"orange|gold|limegreen|yellow|white|black|green|cyan|magenta|springgreen|"
    r"tomato|darkorange|gray)'", re.IGNORECASE)


def colorless(expression):
    """A mesma expressao com os literais de cor apagados.

    Serve para separar duas coisas que o diff cru confunde: logica que sumiu
    (regressao) e logica intacta cuja cor mudou (o redesign fazendo seu
    trabalho). So a primeira e problema.
    """
    return COLOR_LITERAL.sub("'~'", expression)


def collect(folder):
    """Mapeia expressao normalizada -> onde ela aparece."""
    found = defaultdict(list)
    for path in sorted(Path(folder).glob("*.djson")):
        def walk(node, trail):
            label = node.get("Name") or node["$type"].split(",")[0].split(".")[-1]
            here = f"{trail}/{label}"
            for target, binding in (node.get("Bindings") or {}).items():
                expression = (binding.get("Formula") or {}).get("Expression")
                if expression:
                    # O envelope de N/A (dash/fallback.py) nao e logica nova.
                    expression = unwrap(expression)
                    found[normalize(expression)].append(f"{path.stem}{here}.{target}")
            for child in (node.get("Childrens") or []):
                walk(child, here)

        data = json.loads(path.read_text(encoding="utf-8"))
        for screen in data.get("Screens", []):
            for item in screen["Items"]:
                walk(item, "")
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", default=str(ROOT / "referencia-manual"))
    parser.add_argument("--new", default=str(ROOT / "build" / "iRacing_Dashboard_00"))
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="lista tambem as formulas adicionadas")
    args = parser.parse_args(argv)

    old, new = collect(args.old), collect(args.new)
    removed = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))

    print(f"original:    {len(old)} formulas distintas")
    print(f"redesenhado: {len(new)} formulas distintas")
    print()

    # Separa as que so trocaram de cor: mesma cascata de decisoes, paleta nova.
    new_by_shape = {colorless(e): e for e in new}
    restyled = [e for e in removed if colorless(e) in new_by_shape]
    removed = [e for e in removed if colorless(e) not in new_by_shape]
    # E as que so trocaram uma propriedade inexistente pela certa.
    new_squeezed = {squeeze(colorless(e)) for e in new}
    corrected = [e for e in removed if colorless(fixed(e)) in new_squeezed]
    removed = [e for e in removed if e not in corrected]
    restyled_shapes = {colorless(x) for x in restyled}
    corrected_shapes = {colorless(fixed(x)) for x in corrected}
    added = [e for e in added if colorless(e) not in restyled_shapes
             and squeeze(colorless(e)) not in corrected_shapes]

    if corrected:
        print(f"CORRIGIDAS ({len(corrected)}) -- propriedade inexistente trocada "
              "pela certa (PROPERTY_FIXES):")
        for expression in corrected:
            print(f"  {', '.join(old[expression][:3])}")
        print()

    if restyled:
        print(f"RESTILIZADAS ({len(restyled)}) -- mesma logica, cores novas:")
        for expression in restyled:
            print(f"  {', '.join(old[expression][:3])}")
        print()

    if removed:
        print(f"REMOVIDAS ({len(removed)}) -- logica do original que sumiu:")
        for expression in removed:
            where = ", ".join(old[expression][:3])
            print(f"\n  em {where}")
            print(f"    {expression[:220]}")
        print()
    else:
        print("Nenhuma formula do original desapareceu.")

    if added:
        print(f"\nADICIONADAS ({len(added)})")
        if args.verbose:
            for expression in added:
                print(f"\n  em {', '.join(new[expression][:3])}")
                print(f"    {expression[:220]}")
        else:
            print("  (use -v para listar)")

    return 1 if removed else 0


if __name__ == "__main__":
    sys.exit(main())
