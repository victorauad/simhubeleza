"""Medidas e primitivas do dash minimal.

Todas as medidas vem do canvas de design (Dash Minimal -- Capsula), em
pixels do dash. A origem e o canto superior esquerdo da capsula; o box da
telemetria pende dela, encostado no trecho reto da borda de baixo.
"""

from simhub.model import Layer, RectangleItem
from simhub.theme import rounded
from ..layout import Region

WIDTH, HEIGHT = 900.0, 480.0

#: A capsula: as pontas sao semicirculos de raio igual a meia altura.
CAPSULE = Region(0.0, 0.0, 900.0, 240.0)
RADIUS = CAPSULE.height / 2

#: Centros dos semicirculos das pontas -- os arcos de LED giram em torno deles.
ARC_LEFT_X = CAPSULE.x + RADIUS
ARC_RIGHT_X = CAPSULE.right - RADIUS
ARC_Y = CAPSULE.y + RADIUS

#: O box da telemetria vai de onde a curvatura comeca de um lado ate onde
#: comeca do outro, e sobe 1 px para cobrir a borda da capsula.
TRACE_BOX = Region(ARC_LEFT_X, CAPSULE.bottom - 1.0,
                   ARC_RIGHT_X - ARC_LEFT_X, 240.0)

#: Cadencia dos campos lentos (avalia 1 a cada n+1 quadros): ~6 Hz para o
#: que muda a cada volta ou posicao, ~2 Hz para nomes.
SKIP_SLOW = 9
SKIP_NAMES = 29


def rect(name, region, color, *, radius=0, border=None, thickness=1,
         bindings=None, visible=True, **extra):
    """Retangulo do SimHub ocupando `region`."""
    return RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(border, thickness, radius=radius),
        Left=region.x, Top=region.y,
        Width=region.width, Height=region.height,
        Visible=visible,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
        **extra,
    )


def group(name, *children, bindings=None, skip=0):
    """Camada agrupadora: com `Visible` em formula, os filhos escondidos nao
    sao avaliados."""
    return Layer(
        *children,
        name=name,
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=skip, MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )

