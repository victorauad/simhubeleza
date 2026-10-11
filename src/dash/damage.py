"""Damage: o estado do carro, por 3 s no botao ou 5 s a cada dano novo.

Ocupa o lugar do grafico de telemetria. O iRacing nao entrega dano por peca
no SDK (o widget Car Damage dele e so UI), entao este e o "opcao A" de
`docs/estados.md` -- so o que e dado real:

  carro     visto de cima, montado com retangulos. Carroceria pintada pela
            gravidade geral (verde, amarelo, laranja, vermelho, como o
            widget do iRacing); a tampa do motor fica vermelha com aviso de
            motor; cockpit em branco (nao danifica) e rodas neutras (sem
            dado).
  gravidade pelo tempo total de reparo (`PitRepairLeft` + `PitOptRepairLeft`).
  REPAIR    reparo obrigatorio e opcional, em m:ss.
  motor     agua, pressao de oleo, temperatura de oleo e pressao de
            combustivel, acesos pelo `EngineWarnings`.
"""

from simhub.bindings import js
from simhub.model import Layer, RectangleItem
from simhub.theme import (
    GREEN, ORANGE, RED, SEPARATOR, SIZE_VALUE, SURFACE_RAISED, TEXT,
    TEXT_SECONDARY, TEXT_TERTIARY, YELLOW, rounded,
)
from . import layout as grid
from . import states
from .widgets import CENTER, labeled, separators, text

T = states.TELEMETRY

INSET_X, INSET_Y = 14.0, 10.0
#: Gravidade pelo tempo total de reparo (s): ate MINOR e leve, ate
#: MODERATE e medio, acima e grave.
MINOR, MODERATE = 15.0, 60.0
LEVELS = (("No damage", GREEN), ("Minor", YELLOW),
          ("Moderate", ORANGE), ("Severe", RED))
ENGINE = (states.WARN_WATER | states.WARN_OIL_P | states.WARN_OIL_T
          | states.WARN_FUEL_P)
CHIPS = (("Water", states.WARN_WATER), ("Oil P", states.WARN_OIL_P),
         ("Oil T", states.WARN_OIL_T), ("Fuel P", states.WARN_FUEL_P))

#: Silhueta de um formula visto de cima, nariz para cima, numa caixa de
#: 88 x 170. (nome, x, y, largura, altura, papel, raio).
CAR_BOX = (88.0, 170.0)
PARTS = [
    ("Front Wing", 4, 0, 80, 9, "body", 2),
    ("Nose", 38, 9, 12, 44, "body", 3),
    ("Wheel FL", 0, 20, 16, 30, "wheel", 4),
    ("Wheel FR", 72, 20, 16, 30, "wheel", 4),
    ("Sidepod L", 14, 66, 17, 50, "body", 4),
    ("Sidepod R", 57, 66, 17, 50, "body", 4),
    ("Tub", 31, 53, 26, 52, "tub", 6),
    ("Engine", 33, 105, 22, 38, "engine", 4),
    ("Wheel RL", 0, 116, 18, 36, "wheel", 4),
    ("Wheel RR", 70, 116, 18, 36, "wheel", 4),
    ("Rear Wing", 12, 156, 64, 14, "body", 2),
]
SAMPLE_LEVEL = 2
SAMPLE_WARN = states.WARN_OIL_T

DATA = (
    f"var mand = num($prop('{T}PitRepairLeft')) || 0;\r\n"
    f"var opt = num($prop('{T}PitOptRepairLeft')) || 0;\r\n"
    f"var warn = flags($prop('{T}EngineWarnings'));\r\n"
    "var total = mand + opt;\r\n"
    f"var level = total <= 0 ? ((warn & {ENGINE}) ? 1 : 0) : total < {MINOR} "
    f"? 1 : total < {MODERATE} ? 2 : 3;\r\n"
    f"var colors = {[c for _, c in LEVELS]!r};\r\n"
    "var mss = function (s) { s = Math.round(s); var r = s % 60; "
    "return Math.floor(s / 60) + ':' + (r < 10 ? '0' : '') + r; };\r\n"
)


def formula(body):
    return js(states.BASE + states.FLAGS + DATA + body)


def part_color(role):
    if role == "body":
        return formula("return colors[level];")
    if role == "engine":
        return formula(f"return (warn & {ENGINE}) ? '{RED}' : colors[level];")
    return None


def rect(name, region, color, *, radius=3, border=None, bindings=None):
    return RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(border, 1, radius=radius),
        Left=region.x, Top=region.y,
        Width=region.width, Height=region.height,
        Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def car(box):
    """Os retangulos do carro, escalados para caber em `box`."""
    scale = min(box.width / CAR_BOX[0], box.height / CAR_BOX[1])
    ox = box.x + (box.width - CAR_BOX[0] * scale) / 2
    oy = box.y + (box.height - CAR_BOX[1] * scale) / 2
    sample = LEVELS[SAMPLE_LEVEL][1]
    out = []
    for name, x, y, w, h, role, radius in PARTS:
        region = grid.Region(ox + x * scale, oy + y * scale,
                             w * scale, h * scale)
        color = {"body": sample, "engine": RED, "tub": TEXT_SECONDARY,
                 "wheel": SURFACE_RAISED}[role]
        binding = part_color(role)
        out.append(rect(f"Car {name}", region, color, radius=radius,
                        bindings={"BackgroundColor": binding} if binding
                        else None))
    return out


def layer(region):
    inner = region.inset(top=INSET_Y, bottom=INSET_Y,
                         left=INSET_X, right=INSET_X)
    car_w = CAR_BOX[0] * inner.height / CAR_BOX[1]
    car_box = grid.Region(inner.x + 4.0, inner.y, car_w, inner.height)
    gutter = 28.0
    info = inner.inset(left=car_w + 4.0 + gutter)
    top, rest = info.split_top(62.0, gutter=6.0)
    times, chips = rest.split_top(rest.height - 30.0, gutter=6.0)
    repair, optional = times.columns(2, gutter=16.0)

    level_name, level_color = LEVELS[SAMPLE_LEVEL]
    items = [
        *separators([inner, grid.Region(info.x - gutter / 2, region.y, 0,
                                        region.height)],
                    region, name="Damage Separator"),
        *car(car_box),
        *labeled(top, "Damage", level_name.upper(), name="Damage Level",
                 size=SIZE_VALUE, color=level_color, bindings={
                     "Text": formula(
                         f"return {[n.upper() for n, _ in LEVELS]!r}[level];"),
                     "TextColor": formula("return colors[level];"),
                 }),
        *labeled(repair, "Repair", "0:38", name="Damage Repair", size=30.0,
                 bindings={"Text": formula("return mss(mand);"),
                           "TextColor": formula(
                               f"return mand > 0 ? '{TEXT}' : '{TEXT_TERTIARY}';")}),
        *labeled(optional, "Optional", "0:12", name="Damage Optional",
                 size=30.0,
                 bindings={"Text": formula("return mss(opt);"),
                           "TextColor": formula(
                               f"return opt > 0 ? '{TEXT}' : '{TEXT_TERTIARY}';")}),
    ]
    for cell, (label, bit) in zip(chips.columns(len(CHIPS), gutter=8.0),
                                  CHIPS):
        lit = bool(SAMPLE_WARN & bit)
        items += [
            rect(f"Engine {label}", cell, RED if lit else "#00000000",
                 radius=(2, 6, 2, 6), border=SEPARATOR,
                 bindings={"BackgroundColor": formula(
                     f"return (warn & {bit}) ? '{RED}' : '#00000000';")}),
            text(cell.x, cell.y, cell.width, cell.height, label.upper(),
                 name=f"Engine {label} Label", size=12.0, align=CENTER,
                 color=TEXT if lit else TEXT_TERTIARY,
                 bindings={"TextColor": formula(
                     f"return (warn & {bit}) ? '{TEXT}' : '{TEXT_TERTIARY}';")}),
        ]

    shown = Layer(
        *(states.content(item) for item in items),
        name="Damage",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": states.showing("damage")},
    )
    return states.gate(shown)
