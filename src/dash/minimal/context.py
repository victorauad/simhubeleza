"""Painel de contexto: o box de telemetria troca de conteudo por estado.

Um painel opaco cobre o box por cima, so quando ha o que mostrar, e some
sozinho:

  Pit     no pit lane: o limite de velocidade e o combustivel a abastecer.
  Volta   por 5 s depois de fechar uma volta em corrida (fora do pit): o
          numero e o tempo da volta, o delta contra a melhor e o resultado dos
          dez mini-setores.

O painel **cobre** o box e nunca o esconde: o gravador da referencia
(`trace.RECORDER`) vive no `Visible` da linha "Now" e para de gravar se ela for
escondida, entao a camada de telemetria continua visivel por baixo, so coberta.
O fundo e opaco (o do box tem 8% de transparencia, e o traco apareceria
fantasma por baixo).

Pit tem prioridade sobre a volta. Nao depende do dash principal: tudo sai de
propriedades do SimHub (NCalc, e um JS curto para formatar tempos), a ~6 Hz.
"""

from simhub.bindings import js, ncalc
from simhub.theme import (
    FONT, MINI_SECTOR_LOSS, MINI_UNIT, TEXT, TRACE_BOX_EDGE, alpha,
)
from .. import states
from ..widgets import CENTER, LEFT, text
from . import capsule, leds, trace
from .base import SKIP_SLOW, TRACE_BOX, Region, group, rect

BOX = TRACE_BOX
#: Opaco: o fundo do box e a 92%, e por baixo ha os graficos.
PANEL_FILL = alpha("#FF101216", 100)
#: Segundos do painel da volta depois de fechada.
REVIEW_S = 5

PIT = leds.PIT_ROAD
RACE = "[SessionTypeName] = 'Race'"
LAP_CLOSED = f"isincreasing({REVIEW_S * 1000}, [DataCorePlugin.GameData.CompletedLaps])"
REVIEW = f"({RACE} && !{PIT} && {LAP_CLOSED})"

LAST = "$prop('DataCorePlugin.GameData.LastLapTime')"
BEST = "$prop('DataCorePlugin.GameData.BestLapTime')"

#: Delta da volta que fechou contra a melhor da sessao (JS curto). Se a volta
#: e a melhor, o texto e BEST.
DELTA_JS = (
    states.FORMAT
    + f"var l = sec({LAST}), b = sec({BEST});\r\n"
    "if (l == null || b == null) return '--';\r\n"
    "var d = l - b;\r\n"
    "if (Math.abs(d) < 0.0005) return 'BEST';\r\n"
    "return (d > 0 ? '+' : '-') + Math.abs(d).toFixed(2);"
)
DELTA_COLOR_JS = (
    states.FORMAT
    + f"var l = sec({LAST}), b = sec({BEST});\r\n"
    f"return l != null && b != null && l - b > 0.0005 ? '{MINI_SECTOR_LOSS}' : '{TEXT}';"
)
LAP_TIME_JS = states.FORMAT + f"return fmtLap(sec({LAST}));"

#: Limite de velocidade do pit lane, em km/h ("60.00 kph" no YAML do iRacing).
PIT_LIMIT_JS = (
    "var s = String($prop('GameRawData.SessionData.WeekendInfo."
    "TrackPitSpeedLimit') || ''); var v = parseFloat(s);\r\n"
    "if (isNaN(v)) return '--';\r\n"
    "return String(Math.round(/mph/i.test(s) ? v * 1.609344 : v));"
)
FUEL_ADD = ("if([GameRawData.Telemetry.PitSvFuel] > 0, "
            "format([GameRawData.Telemetry.PitSvFuel], '0.0') + ' L', '--')")

SIZE_PRIMARY = capsule.SIZE_READOUT
SIZE_LABEL = capsule.SIZE_READOUT_LABEL
SIZE_SECOND = capsule.SIZE_LAP_VALUE


def _js(source):
    return js(source, jsext=3, format_string="")


def readout(name, x, y, width, sample, binding, label, *, size=SIZE_PRIMARY,
            color=TEXT, color_binding=None):
    """Numero em cima, rotulo embaixo (como km/h e rpm na capsula)."""
    bindings = {"Text": binding}
    if color_binding:
        bindings["TextColor"] = color_binding
    value = text(x, y, width, size, sample, name=name, size=size, color=color,
                 align=CENTER, bindings=bindings)
    value["RenderingSkip"] = SKIP_SLOW
    return [
        value,
        text(x, y + size + 6.0, width, 14.0, label, name=f"{name} Label",
             size=SIZE_LABEL, color=MINI_UNIT, align=CENTER, font=FONT),
    ]


def title(content, *, binding=None):
    item = text(BOX.x + 24.0, BOX.y + 18.0, 200.0, 14.0, content,
                name="Context Title", size=SIZE_LABEL, color=MINI_UNIT,
                align=LEFT, font=FONT, bindings={"Text": binding} if binding else None)
    return item


def pit_panel():
    left = BOX.x + BOX.width * 0.25 - 110.0
    right = BOX.x + BOX.width * 0.75 - 110.0
    top = BOX.y + 84.0
    group_ = group(
        "Pit Panel",
        title("PIT LANE"),
        *readout("Pit Limit", left, top, 220.0, "60", _js(PIT_LIMIT_JS),
                 "LIMIT KM/H"),
        *readout("Fuel Add", right, top, 220.0, "12.5 L", ncalc(FUEL_ADD),
                 "FUEL ADD"),
        bindings={"Visible": ncalc(f"if({PIT}, 1, 0)")}, skip=SKIP_SLOW)
    return group_


def review_panel():
    center = BOX.x + BOX.width / 2
    sectors = []
    for i in range(trace.SECTORS):
        block = rect(f"Review Sector {i + 1}",
                     Region(center - 190.0 + i * 38.0, BOX.y + 176.0, 34.0, 12.0),
                     MINI_UNIT, radius=2,
                     bindings={"BackgroundColor": trace.sector_color(i)})
        block["RenderingSkip"] = SKIP_SLOW
        sectors.append(block)
    return group(
        "Review Panel",
        title("LAP", binding=ncalc(
            "'LAP ' + format([DataCorePlugin.GameData.CompletedLaps], '0')")),
        *readout("Review Time", center - 260.0, BOX.y + 62.0, 240.0, "1:36.8",
                 _js(LAP_TIME_JS), "LAST LAP"),
        *readout("Review Delta", center + 20.0, BOX.y + 62.0, 240.0, "+0.23",
                 _js(DELTA_JS), "VS BEST", color_binding=_js(DELTA_COLOR_JS)),
        text(center - 190.0, BOX.y + 156.0, 120.0, 14.0, "SECTORS",
             name="Review Sectors Label", size=SIZE_LABEL,
             color=MINI_UNIT, align=LEFT, font=FONT),
        *sectors,
        bindings={"Visible": ncalc(f"if({REVIEW} && !{PIT}, 1, 0)")},
        skip=SKIP_SLOW)


def layer():
    """O painel por cima do box. Nasce escondido: so existe no pit ou logo
    depois de uma volta de corrida."""
    base = rect("Context Fill", BOX, PANEL_FILL, radius=(0, 0, 14, 14),
                border=TRACE_BOX_EDGE, thickness=1)
    base["BorderStyle"]["BorderTop"] = 0
    review, pit = review_panel(), pit_panel()
    review["Visible"] = pit["Visible"] = False
    panel = group(
        "Context", base, review, pit,
        bindings={"Visible": ncalc(f"if({PIT} || {REVIEW}, 1, 0)")},
        skip=SKIP_SLOW)
    panel["Visible"] = False
    return panel
