"""LEDs de RPM: dois arcos espelhados, um em cada ponta da capsula.

Nove LEDs por lado acompanham a curvatura, de baixo para cima. Os limiares
sao os do iRacing, por carro: o primeiro LED acende no SLFirstRPM, o ultimo
no SLLastRPM, cada um na cor do seu passo (verde, amarelo, vermelho).
Entre o primeiro e o ultimo os limiares se apertam (`RHYTHM`): os primeiros
LEDs acendem espacados e os ultimos em sequencia rapida, e e essa
aceleracao que da o tempo da troca.

Acima do SLBlinkRPM -- o mesmo ponto em que o brilho da marcha do dash
principal fica roxo -- a rampa inteira sai e os 18 LEDs piscam em roxo,
juntos: aceso roxo, apagado, aceso roxo. O pisca nao usa o `BlinkEnabled`
de cada LED (cada um com o seu relogio, e a rampa aparecendo por baixo na
fase apagada): uma camada so liga e desliga os 18, pelo relogio da sessao
(`SHIFT_PHASE`).

O passo 0 e o LED de status, nos dois lados. Sem bandeira ele e so o
primeiro da rampa; com bandeira fica sempre aceso na cor dela, mesmo com o
RPM baixo -- menos na troca, quando pisca em roxo com os outros. O pit
limiter tem prioridade sobre tudo e desliga o pisca da troca.

O limiter cruza duas coisas, o limitador ligado e estar no pit lane, e o
pisca passa a dizer erro, nao estado normal:

    limitador  pit lane   status
    ligado     dentro     ciano fixo (certo, nada a fazer)
    desligado  dentro     laranja piscando (em movimento: ligue o limitador)
    ligado     fora       ciano piscando (esqueceu ligado: perde tempo)
    ligado     dentro, acima do limite (`DahlDesign.PitSpeeding`): laranja
               piscando

Cada LED aceso e uma comparacao NCalc com os limiares do carro -- nenhum JS.
Camadas, de baixo para cima: trilho apagado (sem formula), rampa (escondida
na troca), troca e o status.
"""

from math import cos, radians, sin

from simhub.bindings import ncalc
from simhub.theme import (
    ALERT, FLAG_BLACK, FLAG_BLUE, FLAG_DIRT, FLAG_GREEN, FLAG_RED,
    FLAG_SLOW_CAR, FLAG_WHITE, FLAG_YELLOW, LIMITER, MINI_RPM_RAMP, MINI_SHIFT,
    MINI_TRACK, STATUS_RING,
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

LIMITER_ON = "[PitLimiterOn]"

#: Hora de trocar a marcha: o mesmo criterio do brilho da marcha do dash
#: principal (`center.GLOW_COLOR`). Com o pit limiter, o ciano dele manda.
SHIFTING = f"({HAS_SL} && [Rpms] > {BLINK} && !{LIMITER_ON})"

#: Fase do pisca da troca, igual para os 18 LEDs: o relogio da sessao em
#: fatias de `BLINK_MS`, aceso nas pares.
SHIFT_PHASE = (f"Floor([GameRawData.Telemetry.SessionTime] * "
               f"{1000.0 / BLINK_MS:.4f}) % 2 = 0")


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


# --- Pit limiter -------------------------------------------------------------

PIT_ROAD = "isnull([GameRawData.Telemetry.OnPitRoad], false)"
PIT_SPEEDING = "isnull([DahlDesign.PitSpeeding], false)"
#: Parado no box nao e erro: o aviso so vale com o carro andando.
MOVING = "[SpeedKmh] > 10"
#: No pit lane andando sem o limitador, ou acima do limite com ele.
PIT_ALERT = f"({PIT_ROAD} && {MOVING} && (!{LIMITER_ON} || {PIT_SPEEDING}))"
#: Limitador ligado fora do pit lane: esquecido.
LIMITER_LEFT_ON = f"({LIMITER_ON} && !{PIT_ROAD})"
#: O LED pisca so em erro; o ciano fixo e o limitador certo no pit lane.
STATUS_BLINK = f"if({PIT_ALERT} || {LIMITER_LEFT_ON}, 1, 0)"


# --- Bandeiras ---------------------------------------------------------------

def flag(name):
    return f"[{name}]='True'"


def raw_flag(bit):
    """Bit de `SessionFlags` ja separado pelo SimHub em booleano."""
    return f"isnull([GameRawData.Telemetry.SessionFlagsDetails.Is{bit}], false)"


#: As condicoes das bandeiras: o LED de status e a area de alerta
#: (`alerts.py`) leem as mesmas.
COND_RED = raw_flag("red")
COND_BLACK = flag("Flag_Black")
COND_REPAIR = raw_flag("repair")
COND_YELLOW = flag("Flag_Yellow")
COND_BLUE = flag("Flag_Blue")
COND_SLOW_CAR = ("(isnull([IRacingExtraProperties.iRacing_SlowCarAhead], false) || "
                 "isnull([IRacingExtraProperties.iRacing_StoppedCarAhead], false))")
COND_DEBRIS = raw_flag("debris")
COND_WHITE = flag("Flag_White")
COND_CHECKERED = flag("Flag_Checkered")
COND_GREEN = flag("Flag_Green")

#: Prioridade do LED de status, da mais alta para a mais baixa.
FLAGS = [
    (PIT_ALERT, ALERT),
    (LIMITER_ON, LIMITER),
    (COND_RED, FLAG_RED),
    (COND_BLACK, FLAG_BLACK),
    (COND_REPAIR, ALERT),
    (COND_YELLOW, FLAG_YELLOW),
    (COND_BLUE, FLAG_BLUE),
    (COND_SLOW_CAR, FLAG_SLOW_CAR),
    (COND_DEBRIS, FLAG_DIRT),
    (COND_WHITE, FLAG_WHITE),
    (COND_CHECKERED, STATUS_RING),
    (COND_GREEN, FLAG_GREEN),
]
FLAGGED = " || ".join(condition for condition, _ in FLAGS)


def status_color():
    """Cor do status: a da bandeira de maior prioridade, ou o verde da rampa."""
    expression = f"'{ramp_color(0)}'"
    for condition, color in reversed(FLAGS):
        expression = f"if({condition}, '{color}', {expression})"
    return expression


#: Aceso com bandeira, ou como primeiro da rampa -- ate a troca, quando some
#: para piscar em roxo com os outros. O limitador e o aviso do pit acendem
#: sempre.
STATUS_VISIBLE = (f"if({LIMITER_ON} || {PIT_ALERT} || (!{SHIFTING} && (({FLAGGED}) || "
                  f"({HAS_SL} && [Rpms] >= {FIRST}))), 1, 0)")


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
                     name, region, rot, MINI_SHIFT))
    status = each("Status", [0],
                  lambda name, region, rot, step: led(
                      name, region, rot, ramp_color(0), visible=False,
                      BlinkDelay=BLINK_MS,
                      bindings={"Visible": ncalc(STATUS_VISIBLE),
                                "BackgroundColor": ncalc(status_color()),
                                "BlinkEnabled": ncalc(STATUS_BLINK)}))
    # Bandeira preta: o LED quase some no fundo, entao ganha um aro claro.
    ring = each("Black Ring", [0],
                lambda name, region, rot, step: led(
                    name, region, rot, "#00FFFFFF", border=STATUS_RING,
                    thickness=1, visible=False,
                    bindings={"Visible": ncalc(
                        f"if({flag('Flag_Black')} && !{SHIFTING}, 1, 0)")}))

    return group(
        "RPM LEDs",
        group("Track", *track),
        # Na troca a rampa sai inteira: na fase apagada do pisca, os LEDs
        # ficam apagados, e nao nas cores da rampa.
        group("Ramp", *lit, bindings={"Visible": ncalc(
            f"if({SHIFTING}, 0, 1)")}),
        group("Shift", *shift, bindings={"Visible": ncalc(
            f"if({SHIFTING} && {SHIFT_PHASE}, 1, 0)")}),
        group("Status", *status, *ring),
    )
