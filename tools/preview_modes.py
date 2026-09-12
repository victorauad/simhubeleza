"""Gera um preview por modo da coluna direita.

A coluna troca de modo em sessao, e cada modo so aparece sob condicoes que o
render estatico nao tem como reproduzir. Entao aqui cada modo e forcado: uma
copia do build com as camadas ligadas a mao e as repeticoes de linha que
aquele caso produz na pista.

Duas coisas ficam explicitas de proposito:

- Os avisos de bandeira sao excludentes em pista. Mostrados todos de uma vez,
  eles se empilham e a barra superior fica ilegivel -- entao o preview mostra
  a barra em repouso.
- `--conditional show` e necessario: as linhas do relative e do leaderboard so
  existem sob binding de Visible, e sem isso a coluna sai vazia.

Uso:  python3 tools/preview_modes.py [PASTA_DE_SAIDA]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build" / "iRacing_Dashboard_00"

#: modo -> (camadas visiveis, repeticoes por camada repetidora)
MODES = {
    "relative": ({"Relative"},
                 {"Driver Ahead Repeat": 3, "Driver Behind Repeat": 3}),
    "standings": ({"Standings"},
                  {"Leaderboard": 13, "Leaderboard Overflow": 0}),
    "window": ({"Standings"},
               {"Leaderboard": 3, "Leaderboard Overflow": 7}),
    "practice": ({"Practice"}, {"Lap Data": 9}),
}

#: Bandeiras/avisos da barra superior -- ver `top_bar.BANNER_NAMES`. Cada
#: entrada gera um preview `flag-<slug>.html` com so aquele aviso ligado, os
#: demais desligados -- sem isso os seis se empilham (sao excludentes em
#: pista) e a barra some da leitura.
FLAGS = {
    "flag-off-track": "Incident",
    "flag-clipping": "Clipping",
    "flag-input-overlap": "Overlaping",
    "flag-green": "Green Flag",
    "flag-yellow": "Yellow Flag",
    "flag-white": "White Flag",
}

MODE_LAYERS = {"Standings", "Practice", "Relative"}
BANNER_NAMES = set(FLAGS.values())


def render(mode, visible, repetitions, out_dir, work, flag=None):
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(BUILD, work)
    path = work / "iRacing_Dashboard_00.djson"
    data = json.loads(path.read_text(encoding="utf-8"))

    def walk(node, in_alerts=False):
        name = node.get("Name")
        if name in MODE_LAYERS:
            node["Visible"] = name in visible
        if name in repetitions:
            node["Repetitions"] = repetitions[name]
            if repetitions[name] == 0:
                node["Visible"] = False
        if name == "Alerrts" and flag is not None:
            node["Visible"] = True
        elif name in BANNER_NAMES and flag is not None:
            node["Visible"] = name == flag
        elif in_alerts:
            node["Visible"] = False
            node.pop("Bindings", None)
        for child in (node.get("Childrens") or []):
            walk(child, in_alerts or name == "Alerrts")

    for screen in data.get("Screens", []):
        for item in screen["Items"]:
            walk(item)
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")

    target = out_dir / f"{mode}.html"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "preview.py"), str(work),
         "--bare", "--conditional", "show", "-o", str(target)],
        check=True, stdout=subprocess.DEVNULL)
    return target


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    out_dir = Path(argv[0]) if argv else ROOT / "build" / "modes"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = out_dir / "_work"
    for mode, (visible, repetitions) in MODES.items():
        target = render(mode, visible, repetitions, out_dir, work)
        print(f"{mode:10} -> {target}")
    # As bandeiras usam o modo relative como base (a barra superior nao muda
    # entre modos da coluna direita).
    base_visible, base_repetitions = MODES["relative"]
    for slug, banner in FLAGS.items():
        target = render(slug, base_visible, base_repetitions, out_dir, work,
                        flag=banner)
        print(f"{slug:20} -> {target}")
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
