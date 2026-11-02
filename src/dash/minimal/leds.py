"""LEDs de RPM: dois arcos espelhados, um em cada ponta da capsula.

Nove LEDs por lado acompanham a curvatura, de baixo para cima. Os limiares
sao os do iRacing, por carro: o primeiro LED acende no SLFirstRPM, o ultimo
no SLLastRPM, e a partir do SLBlinkRPM todos ficam roxos e piscam (trocar a
marcha). Entre o primeiro e o ultimo os limiares se apertam (`RHYTHM`): os
primeiros LEDs acendem espacados e os ultimos em sequencia rapida, e e essa
aceleracao que da o tempo da troca.

O passo 0 e o LED de status, nos dois lados. Sem bandeira ele e so o
primeiro da rampa; com bandeira (ou pit limiter) fica sempre aceso na cor
dela, mesmo com o RPM baixo.

Cada LED aceso e uma comparacao NCalc com os limiares do carro -- nenhum JS.
Camadas, de baixo para cima: trilho apagado (sem formula), rampa, troca
(uma camada so com `Visible`, filhos piscando sozinhos) e o status.
"""

from math import cos, radians, sin

from simhub.bindings import ncalc
from simhub.theme import (
    FLAG_BLACK, FLAG_BLUE, FLAG_GREEN, FLAG_WHITE, FLAG_YELLOW, LIMITER,
    MINI_RPM_RAMP, MINI_SHIFT, MINI_TRACK, STATUS_RING,
)
from .base import ARC_LEFT_X, ARC_RIGHT_X, ARC_Y, Region, group, rect

STEPS = 9
#: Raio do arco dos LEDs e o meio-angulo coberto, em torno do eixo
#: horizontal de cada ponta.
ARC_RADIUS = 100.0
ARC_SPAN = 70.0
LED_W, LED_H = 24.0, 10.0
LED_RADIUS = LED_H / 2

#: Quanto os limiares se apertam no fim: 1.0 e linear; maior, mais rapido o
#: fim da sequencia.
RHYTHM = 1.6

#: Pisca da troca e do pit limiter, em ms por fase.
BLINK_MS = 120.0

SL = "GameRawData.Telemetry.PlayerCarSL"
FIRST, LAST, BLINK = (f"[{SL}{name}RPM]" for name in ("First", "Last", "Blink"))
#: Carro sem shift lights no iRacing: os limiares vem zerados e nada acende.
HAS_SL = f"{LAST} > 0"


def fraction(step):
    """Posicao do passo na sequencia, de 0 (primeiro) a 1 (ultimo)."""
    return step / (STEPS - 1)


def threshold(step):
    """RPM que acende o passo, ja com o aperto do ritmo."""
    k = 1.0 - (1.0 - fraction(step)) ** RHYTHM
    return f"{FIRST} + ({LAST} - {FIRST}) * {k:.4f}"


def ramp_color(step):
    """Verde no comeco, amarelo no meio, vermelho no fim."""
    f = fraction(step)
    green, yellow, red = MINI_RPM_RAMP
    return green if f < 0.45 else yellow if f < 0.75 else red


def positions(step):
    """Caixa e rotacao do passo nos dois lados (esquerdo, direito).

    O passo 0 fica embaixo; o LED e uma pilula tangente ao arco.
    """
    deg = -ARC_SPAN + 2 * ARC_SPAN * fraction(step)
    a = radians(deg)
    dx, y = ARC_RADIUS * cos(a), ARC_Y - ARC_RADIUS * sin(a)
    # A pilula e simetrica: basta a rotacao modulo 180.
    return [
        (Region(cx - LED_W / 2, y - LED_H / 2, LED_W, LED_H), round(rot % 180, 1))
        for cx, rot in ((ARC_LEFT_X - dx, deg - 90), (ARC_RIGHT_X + dx, -90 - deg))
    ]


def led(name, region, rotation, color, **kwargs):
    return rect(name, region, color, radius=LED_RADIUS, Rotation=rotation,
                **kwargs)


def each(prefix, steps, make):
    """Um item por passo e por lado."""
    return [make(f"{prefix} {step}{side}", region, rotation, step)
            for step in steps
            for side, (region, rotation) in zip("LR", positions(step))]


# --- Bandeiras ---------------------------------------------------------------

def flag(name):
    return f"[{name}]='True'"


#: Prioridade do LED de status, da mais alta para a mais baixa.
FLAGS = [
    ("[PitLimiterOn]", LIMITER),
    (flag("Flag_Black"), FLAG_BLACK),
    (flag("Flag_Yellow"), FLAG_YELLOW),
    (flag("Flag_Blue"), FLAG_BLUE),
    (flag("Flag_White"), FLAG_WHITE),
    (flag("Flag_Green"), FLAG_GREEN),
]
FLAGGED = " || ".join(condition for condition, _ in FLAGS)


def status_color():
    """Cor do status: a da bandeira de maior prioridade, ou o verde da rampa."""
    expression = f"'{ramp_color(0)}'"
    for condition, color in reversed(FLAGS):
        expression = f"if({condition}, '{color}', {expression})"
    return expression


#: Aceso com bandeira, ou como primeiro da rampa -- ate a troca, quando some
#: para o roxo aparecer no lugar.
STATUS_VISIBLE = (f"if(({FLAGGED}) || ({HAS_SL} && [Rpms] >= {FIRST} "
                  f"&& [Rpms] < {BLINK}), 1, 0)")


def layer():
    track = each("Off", range(STEPS),
                 lambda name, region, rot, step: led(name, region, rot, MINI_TRACK))
    lit = each("Rpm", range(1, STEPS),
               lambda name, region, rot, step: led(
                   name, region, rot, ramp_color(step), visible=False,
                   bindings={"Visible": ncalc(
                       f"if({HAS_SL} && [Rpms] >= {threshold(step)}, 1, 0)")}))
    shift = each("Shift", range(STEPS),
                 lambda name, region, rot, step: led(
                     name, region, rot, MINI_SHIFT,
                     BlinkEnabled=True, BlinkDelay=BLINK_MS))
    status = each("Status", [0],
                  lambda name, region, rot, step: led(
                      name, region, rot, ramp_color(0), visible=False,
                      BlinkDelay=BLINK_MS,
                      bindings={"Visible": ncalc(STATUS_VISIBLE),
                                "BackgroundColor": ncalc(status_color()),
                                "BlinkEnabled": ncalc("[PitLimiterOn]")}))
    # Bandeira preta: o LED quase some no fundo, entao ganha um aro claro.
    ring = each("Black Ring", [0],
                lambda name, region, rot, step: led(
                    name, region, rot, "#00FFFFFF", border=STATUS_RING,
                    thickness=1, visible=False,
                    bindings={"Visible": ncalc(f"if({flag('Flag_Black')}, 1, 0)")}))

    return group(
        "RPM LEDs",
        group("Track", *track),
        group("Ramp", *lit),
        group("Shift", *shift, bindings={"Visible": ncalc(
            f"if({HAS_SL} && [Rpms] >= {BLINK}, 1, 0)")}),
        group("Status", *status, *ring),
    )
