"""Area de alerta: um lugar so para avisar, e so quando ha o que fazer.

O slot e o cabecalho do OTS ("OTS READY", 16 px, na capsula). Quando ha um
aviso, ele toma o lugar do cabecalho -- os segundos e a barra do OTS ficam --
e o de maior prioridade ganha: bandeira, depois pit, depois combustivel,
depois informacao (o brake bias, por 2 s). Sem aviso, volta o OTS. Texto de
duas ou tres palavras: o aviso nao pode pedir leitura.

O LED de status (`leds.py`) pinta a mesma bandeira; aqui ela ganha a
instrucao em palavras. Nada pisca nem anima: a regra que as referencias
sustentam e o aviso condicional (some sozinho quando a condicao acaba).

Tudo NCalc com constante, avaliado a ~6 Hz (`SKIP_SLOW`).
"""

from simhub.bindings import ncalc
from simhub.theme import (
    ALERT, AMBER, BIAS, FLAG_BLUE, FLAG_DIRT, FLAG_RED, FLAG_SLOW_CAR,
    FLAG_WHITE, FLAG_YELLOW, FONT, LIMITER, ORANGE, TEXT,
)
from ..widgets import LEFT, text
from . import capsule, leds
from .base import SKIP_SLOW, group

#: Combustivel acabando: menos de `LOW_FUEL_LAPS` voltas no tanque.
LOW_FUEL_LAPS = 2

REMAINING = "[DataCorePlugin.Computed.Fuel_RemainingLaps]"
FUEL_SHORT = f"({capsule.HAS_TARGET} && {capsule.FUEL} < {capsule.NEEDED})"
FUEL_LOW = (f"({capsule.FUEL_PER_LAP} > 0 && {REMAINING} > 0 && "
            f"{REMAINING} < {LOW_FUEL_LAPS})")

#: (condicao, texto NCalc, cor), da prioridade mais alta para a mais baixa.
#: O texto pode ser uma expressao; literais vao entre aspas simples.
ALERTS = [
    # Bandeiras que param ou punem.
    (leds.COND_RED, "'RED FLAG'", FLAG_RED),
    (leds.COND_BLACK, "'BLACK FLAG'", FLAG_WHITE),
    (leds.COND_REPAIR, "'REPAIR'", ORANGE),
    # Pit: limitador faltando ou acima do limite, ou esquecido ligado.
    (leds.PIT_ALERT,
     f"if({leds.LIMITER_ON} && {leds.PIT_SPEEDING}, 'SLOW DOWN', 'LIMITER')",
     ALERT),
    (leds.LIMITER_LEFT_ON, "'LIMITER ON'", LIMITER),
    # Bandeiras de pista.
    (leds.COND_YELLOW, "'YELLOW'", FLAG_YELLOW),
    (leds.COND_BLUE, "'BLUE FLAG'", FLAG_BLUE),
    (leds.COND_SLOW_CAR, "'SLOW CAR'", FLAG_SLOW_CAR),
    # Combustivel.
    (FUEL_SHORT, "'FUEL SHORT'", ORANGE),
    (FUEL_LOW, "'LOW FUEL'", AMBER),
    (leds.COND_DEBRIS, "'DEBRIS'", FLAG_DIRT),
    # Fim e ultima volta.
    (leds.COND_CHECKERED, "'CHECKERED'", TEXT),
    (leds.COND_WHITE, "'LAST LAP'", FLAG_WHITE),
    # Informacao: o brake bias mudou ha pouco.
    (capsule.BIAS_CHANGED, "'BB ' + format([BrakeBias], '0.0')", BIAS),
]

#: Sem aviso o slot e do OTS.
ACTIVE = "(" + " || ".join(f"({cond})" for cond, _, _ in ALERTS) + ")"


def _cascade(pick, otherwise):
    expression = otherwise
    for entry in reversed(ALERTS):
        expression = f"if({entry[0]}, {pick(entry)}, {expression})"
    return expression


TEXT_FORMULA = _cascade(lambda e: e[1], "''")
COLOR_FORMULA = _cascade(lambda e: f"'{e[2]}'", f"'{TEXT}'")


def layer():
    """O aviso no slot do cabecalho do OTS. Nasce escondido: so existe com
    aviso, e escondido nao avalia a cadeia de texto e cor."""
    item = text(
        *capsule.frame(capsule.OTS_HEADER), "BB 54.5", name="Alert",
        size=capsule.SIZE_OTS_HEADER, color=TEXT, align=LEFT, font=FONT,
        bindings={"Text": ncalc(TEXT_FORMULA), "TextColor": ncalc(COLOR_FORMULA)})
    item["RenderingSkip"] = SKIP_SLOW
    layer = group(
        "Alert", item,
        bindings={"Visible": ncalc(f"if({ACTIVE}, 1, 0)")}, skip=SKIP_SLOW)
    layer["Visible"] = False
    return layer
