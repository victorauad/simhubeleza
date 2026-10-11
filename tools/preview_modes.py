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
sys.path.insert(0, str(ROOT / "src"))
from simhub.theme import FASTER, SLOWER, TEXT_TERTIARY as NEUTRAL  # noqa: E402
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

#: Avisos da barra superior -- os dez chips de `top_bar.CHIPS`. Cada entrada
#: gera um preview `flag-<slug>.html` com so aquele aviso ligado, os demais
#: desligados: em pista eles sao excludentes, e empilhados de uma vez o chip
#: vira sopa.
FLAGS = {
    "flag-green": "Flag Green",
    "flag-yellow": "Flag Yellow",
    "flag-white": "Flag White",
    "flag-black": "Flag Black",
    "flag-blue": "Flag Blue",
    "flag-dirt": "Flag Dirt",
    "flag-incident": "Flag Incident",
    "flag-overlap": "Flag Overlap",
    "flag-car-left": "Flag Car Left",
    "flag-car-right": "Flag Car Right",
}

#: Estados do RPMLed que so existem sob formula -- o Figma desenha os dois,
#: entao o preview precisa conseguir mostra-los.
LED_STATES = {
    "shift-light": "Shift Light",
    "pit-limiter": "Shift Light2",
}

#: Telemetria de exemplo, igual em todos os previews: sem ela os pedais e o
#: delta saem vazios e a marcha mostra "N". Nome do controle -> campos.
SAMPLE = {
    "Brake Gauge": {"Value": 37.0},
    "Throttle Gauge": {"Value": 72.0},
    "Brake Value": {"Text": "37"},
    "Throttle Value": {"Text": "72"},
    "Progress-Red": {"Value": 0.0},
    "Progress-Green": {"Value": -0.03},
    "Delta-Red": {"Value": 0.0},
    "Delta-Green": {"Value": -0.24},
    "Delta Value": {"Text": "-0.24", "TextColor": "#FF34D27B"},
    "GearText": {"DesignerText": "4"},
    "Speed": {"Text": "218"},
    "Rpm": {"Text": "985"},
    "OTS Gauge": {"Value": 200.0},
}

#: Lap log com uma volta diferente por linha (a mais recente em cima). O
#: render estatico repetiria a mesma linha nove vezes; aqui a camada vira
#: nove copias com os valores escritos. Temperatura e combustivel sao
#: gravados pelo dash por volta; a volta 9 teve reabastecimento (N/A).
#: (numero, tempo, pista, delta, combustivel)
LAP_LOG = [
    ("13", "1:32.90", "31", "+0.42", "2.33"),
    ("12", "1:32.61", "31", "+0.13", "2.31"),
    ("11", "1:32.48", "31", "0.00", "2.30"),
    ("10", "1:32.87", "30", "+0.39", "2.34"),
    ("09", "1:33.21", "30", "+0.73", "N/A"),
    ("08", "1:32.70", "30", "+0.22", "2.29"),
    ("07", "1:33.48", "30", "+1.00", "2.38"),
    ("06", "1:32.95", "29", "+0.47", "2.32"),
    ("05", "1:34.10", "29", "+1.62", "2.41"),
]
LAP_BEST = "11"
LAP_COLUMNS = ("LapNumber", "LapTime", "LapTrackTemp", "LapDelta", "LapFuel")


def expand_lap_log(layer):
    """Troca a camada repetidora do lap log por uma copia por volta."""
    import copy
    rows = []
    for i, values in enumerate(LAP_LOG):
        row = copy.deepcopy(layer)
        row["Repetitions"] = 0
        row["Name"] = f"Lap Data {i + 1}"
        for child in row["Childrens"]:
            column = LAP_COLUMNS.index(child["Name"])
            child["Top"] += i * layer["RepeatTopOffset"]
            child["Text"] = values[column]
            child.pop("Bindings", None)
            if child["Name"] == "LapDelta":
                child["TextColor"] = (NEUTRAL if values[3] == "0.00" else FASTER
                                      if values[3].startswith("-") else SLOWER)
            if values[0] == LAP_BEST and child["Name"] in ("LapNumber", "LapTime"):
                child["TextColor"] = "#FFB56CFF"
        rows.append(row)
    return rows


#: Estados temporarios dos componentes laterais (states.py). Cada um liga
#: os proprios layers e desliga o componente que ele substitui; os layers
#: "Live" (coletores, sempre ligados em pista) so aparecem no estado deles.
STATES = {
    "state-damage": {"Damage"},
    "state-weather": {"Weather", "Weather Live"},
    "state-review": {"Lap Review", "Lap Review Live"},
    "state-new-lap": {"New Lap Info"},
}
STATE_LAYERS = set().union(*STATES.values())

#: Dentro do Weather, icones e setas sao excludentes por formula; no preview
#: fica um icone e um punhado de setas, como em pista.
WEATHER_ICON = "Weather WxPartlySun"
WEATHER_TRENDS = {"Weather Air TrendUp", "Weather Track TrendUp",
                  "Weather Humidity TrendDown"}


def weather_pick(name):
    """None se o controle nao e icone/seta do Weather; senao, se aparece."""
    if name.startswith("Weather Wx"):
        return name == WEATHER_ICON
    if name.startswith("Weather ") and name.endswith(("TrendUp", "TrendDown")):
        return name in WEATHER_TRENDS
    return None
LEFT_STATES = {"Damage", "Weather", "Lap Review"}

#: Controles que so aparecem em situacao especifica (volta invalidada) e,
#: com `--conditional show`, poluiriam todo preview.
HIDDEN = {"Invalid Lap"}

MODE_LAYERS = {"Standings", "Practice", "Relative"}
BANNER_NAMES = set(FLAGS.values())
LED_LAYERS = set(LED_STATES.values())


def render(mode, visible, repetitions, out_dir, work, flag=None, led=None,
           state=None):
    shutil.rmtree(work, ignore_errors=True)
    shutil.copytree(BUILD, work)
    path = work / "iRacing_Dashboard_00.djson"
    data = json.loads(path.read_text(encoding="utf-8"))

    def walk(node, in_alerts=False):
        name = node.get("Name")
        if name in SAMPLE:
            node.update(SAMPLE[name])
        # Gemeos "N/A" (dash/fallback.py) so aparecem sem dado; o preview
        # mostra os campos com dado de exemplo.
        if name in HIDDEN or (name or "").endswith(" N/A"):
            node["Visible"] = False
            node.pop("Bindings", None)
        if name in MODE_LAYERS:
            node["Visible"] = name in visible
        on = STATES.get(state, set())
        if name in STATE_LAYERS:
            node["Visible"] = name in on
            node.pop("Bindings", None) if name in on else None
        pick = weather_pick(name or "")
        if pick is not None:
            node["Visible"] = pick
            node.pop("Bindings", None)
        if name == "Telemetry":
            node["Visible"] = not (on & LEFT_STATES)
        if name == "Sectors":
            node["Visible"] = "New Lap Info" not in on
        if name in repetitions:
            node["Repetitions"] = repetitions[name]
            if repetitions[name] == 0:
                node["Visible"] = False
        # Cada aviso e uma pilula mais o rotulo "<nome> Label"; o rotulo
        # segue a pilula. O contorno do chip vazio fica sempre.
        banner = name[:-len(" Label")] if (name or "").endswith(" Label") else name
        if name in ("Alerrts", "Alerrts2") and flag is not None:
            node["Visible"] = True
        elif name == "Chip Slot":
            node["Visible"] = True
        elif banner in BANNER_NAMES and flag is not None:
            node["Visible"] = banner == flag
        elif banner in BANNER_NAMES or in_alerts:
            node["Visible"] = False
            node.pop("Bindings", None)
        if mode == "practice" and node.get("Childrens"):
            out = []
            for child in node["Childrens"]:
                out += (expand_lap_log(child) if child.get("Name") == "Lap Data"
                        else [child])
            node["Childrens"] = out
        for child in (node.get("Childrens") or []):
            walk(child, in_alerts or name in ("Alerrts", "Alerrts2"))

    for screen in data.get("Screens", []):
        for item in screen["Items"]:
            walk(item)
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")

    if led:
        force_led(work, led)

    target = out_dir / f"{mode}.html"
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "preview.py"), str(work),
         "--bare", "--conditional", "show", "-o", str(target)],
        check=True, stdout=subprocess.DEVNULL)
    return target


def force_led(work, layer_name):
    """Liga uma camada de alerta dentro dos dois arquivos do RPMLed.

    As camadas de shift light e pit limiter vivem no widget, nao na arvore
    principal, e so aparecem sob formula -- entao o preview as liga a mao nos
    dois .djson (o normal e o espelhado).
    """
    for filename in ("RPMLed.djson", "RPMLedMirrored.djson"):
        path = work / filename
        data = json.loads(path.read_text(encoding="utf-8"))

        def walk(node):
            if node.get("Name") == layer_name:
                node["Visible"] = True
                node.pop("Bindings", None)
            for child in (node.get("Childrens") or []):
                walk(child)

        for screen in data.get("Screens", []):
            for item in screen["Items"]:
                walk(item)
        path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")


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
    for slug in STATES:
        target = render(slug, base_visible, base_repetitions, out_dir, work,
                        state=slug)
        print(f"{slug:20} -> {target}")
    for slug, layer_name in LED_STATES.items():
        target = render(slug, base_visible, base_repetitions, out_dir, work,
                        led=layer_name)
        print(f"{slug:20} -> {target}")
    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
