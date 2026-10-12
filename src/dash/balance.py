"""Balanco: barra de sub/sobre-esterco, no rodape da coluna central.

O iRacing nao entrega slip angle de pneu, entao o angulo de cada eixo e
estimado com o modelo de bicicleta (dois eixos), a partir da velocidade do
carro no proprio referencial, da taxa de guinada e do angulo do volante:

    alfa_dianteiro = delta - atan((vy + a*r) / vx)
    alfa_traseiro  =       - atan((vy - b*r) / vx)

com delta = volante / relacao de direcao, e a, b as distancias do centro de
gravidade aos eixos. O balanco e |alfa_d| - |alfa_t|: positivo quando a
frente escorrega mais (sub-esterco), negativo quando a traseira escorrega
mais (sobre-esterco). A barra sai do centro: sub para a esquerda, sobre para
a direita.

As constantes do SF23 abaixo sao estimativas -- ajuste na pista. Uma relacao
de direcao errada desloca o zero: com o carro neutro numa curva longa, a
barra deve ficar perto do meio.
"""

from simhub.bindings import js
from simhub.model import Layer, LinearGaugeItem
from simhub.theme import CYAN, RED, SIZE_LABEL, SURFACE_RAISED, TEXT, TEXT_SECONDARY, rounded
from . import layout as grid
from .top_bar import halves, marker
from .widgets import LEFT, RIGHT, text, tile

#: Distancia entre eixos (m) e fracao do peso no eixo traseiro.
WHEELBASE = 3.115
REAR_WEIGHT = 0.55
#: Graus no volante por grau na roda.
STEERING_RATIO = 11.0
#: Abaixo disso (m/s, ~36 km/h) a conta fica instavel: barra zerada.
MIN_SPEED = 10.0
#: Fundo de escala de cada lado, em graus de diferenca de slip.
FULL_SCALE = 3.0
#: Suavizacao exponencial por avaliacao (0 = congela, 1 = cru).
SMOOTHING = 0.25

UNDER = CYAN
OVER = RED

BAR_HEIGHT = 5.0
LABEL_WIDTH = 40.0
LABEL_GAP = 8.0
MARKER_WIDTH, MARKER_OVERHANG = 2.0, 3.0

TELEMETRY = "DataCorePlugin.GameRawData.Telemetry."


def formula(key, sign):
    """JS do balanco suavizado, recortado para um lado: `sign` 1 devolve o
    sub-esterco, -1 o sobre-esterco (sempre positivo, para o gauge).

    Cada gauge guarda o proprio estado em `root`, separado por `key`, para
    que as duas avaliacoes por quadro nao suavizem duas vezes o mesmo valor.
    """
    a = WHEELBASE * REAR_WEIGHT
    b = WHEELBASE - a
    return js(
        f"var vx = $prop('{TELEMETRY}VelocityX');\r\n"
        f"var vy = $prop('{TELEMETRY}VelocityY');\r\n"
        f"var r = $prop('{TELEMETRY}YawRate');\r\n"
        f"var sw = $prop('{TELEMETRY}SteeringWheelAngle');\r\n"
        f"var k = '{key}';\r\n"
        f"var bal = 0;\r\n"
        f"if (vx != null && vx > {MIN_SPEED}) {{\r\n"
        f"\tvar af = sw / {STEERING_RATIO} - Math.atan((vy + {a:.4f} * r) / vx);\r\n"
        f"\tvar ar = -Math.atan((vy - {b:.4f} * r) / vx);\r\n"
        f"\tbal = (Math.abs(af) - Math.abs(ar)) * 180 / Math.PI;\r\n"
        f"}}\r\n"
        f"if (root[k] == null) {{ root[k] = 0; }}\r\n"
        f"root[k] += (bal - root[k]) * {SMOOTHING};\r\n"
        f"return Math.max(0, {sign} * root[k]);"
    )


def gauge(name, area, color, key, sign, *, alignment, radius, sample):
    return LinearGaugeItem(
        name=name,
        IsLinearGauge=True,
        GaugeOrientation=0,
        GaugeAlignment=alignment,
        AutoSize=False,
        GaugeColor=color,
        AlternateGaugeColor=color,
        UseAlternateStyle=False,
        Minimum=0.0, Maximum=FULL_SCALE, Value=sample, Steps=0.0,
        PAW=area.width,
        BackgroundColor="#00FFFFFF",
        BorderStyle=radius,
        Left=area.x, Top=area.y, Width=area.width, Height=area.height,
        Opacity=100.0,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Value": formula(key, sign)},
    )


def layer(region):
    """Rotulo UNDER, barra que sai do centro, rotulo OVER."""
    label_left = grid.Region(region.x, region.y, LABEL_WIDTH, region.height)
    label_right = grid.Region(region.right - LABEL_WIDTH, region.y,
                              LABEL_WIDTH, region.height)
    bar = grid.Region(label_left.right + LABEL_GAP,
                      region.y + (region.height - BAR_HEIGHT) / 2,
                      region.width - (LABEL_WIDTH + LABEL_GAP) * 2, BAR_HEIGHT)
    under, over = halves(bar)
    center = bar.x + bar.width / 2
    zero = grid.Region(center - MARKER_WIDTH / 2, bar.y - MARKER_OVERHANG,
                       MARKER_WIDTH, bar.height + MARKER_OVERHANG * 2)
    radius = BAR_HEIGHT / 2

    return Layer(
        text(label_left.x, label_left.y, label_left.width, label_left.height,
             "UNDER", name="Under Label", size=SIZE_LABEL,
             color=TEXT_SECONDARY, align=LEFT),
        text(label_right.x, label_right.y, label_right.width,
             label_right.height, "OVER", name="Over Label", size=SIZE_LABEL,
             color=TEXT_SECONDARY, align=RIGHT),
        tile(bar, name="Balance Track", color=SURFACE_RAISED, radius=radius),
        gauge("Balance-Under", under, UNDER, "bal_under", 1, alignment=2,
              radius=rounded(radius=(radius, 0, 0, radius)), sample=1.2),
        gauge("Balance-Over", over, OVER, "bal_over", -1, alignment=0,
              radius=rounded(radius=(0, radius, radius, 0)), sample=0.0),
        marker("Balance Zero", zero, TEXT),
        name="Balance",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
