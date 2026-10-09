"""Push-to-pass do SF23: estado e segundos restantes.

O dado e um so -- quanto de overtake resta e se da para usar agora -- entao a
faixa nao se divide em tiles: estado a esquerda, segundos a direita, e uma
barra fina no rodape mostrando o quanto sobrou sem exigir leitura de numero.

As formulas de estado sao as do original; so os literais de cor mudaram, para
a paleta Grafite: verde pronto, roxo piscando enquanto ativo, vermelho
carregando. Hex #AARRGGBB na formula, como o original ja faz em outras cores.

A barra e um pente, como as da barra superior: trilho, gauge e uma mascara
(`OtsComb`, gerada por `tools/make_combs.py`).
"""

from simhub.bindings import formatted, ncalc
from simhub.model import ImageItem, LinearGaugeItem, Layer
from simhub.theme import (
    CORNER_RADIUS_TILE, OTS_ACTIVE, OTS_BLOCKED, OTS_COOLDOWN, OTS_READY,
    SIZE_LABEL, SIZE_VALUE_SM, TRACK, WEIGHT_VALUE,
)
from . import layout as grid
from .widgets import LEFT, RIGHT, caption, text, tile

PANEL = grid.OTS.inset(left=grid.MARGIN, right=grid.MARGIN)

#: Respiro interno, como no canvas: 14 em cima, 12 nos lados e embaixo.
INNER = PANEL.inset(top=14.0, left=12.0, right=12.0, bottom=12.0)

#: Capacidade do sistema, em segundos. Define a escala da barra.
CAPACITY = 200.0
BAR_HEIGHT = 9.0

#: Pente da barra -- a mascara sai destas medidas.
COMB_AREA = grid.Region(INNER.x, INNER.bottom - BAR_HEIGHT,
                        INNER.width, BAR_HEIGHT)
COMB_IMAGE = "OtsComb"
IMAGES = (COMB_IMAGE,)

#: Cada estado do sistema, na ordem em que o original testa: box, pronto,
#: ativo, esfriando, indisponivel.
READY = OTS_READY
ACTIVE = OTS_ACTIVE
COOLDOWN = OTS_COOLDOWN
BLOCKED = OTS_BLOCKED

#: Pisca o estado enquanto o overtake esta ativo.
ACTIVE_BLINK = "if([DahlDesign.SF23.OTActive], 1, 0)"


def state_formula(box, ready, active, cooldown, blocked, fallback):
    """Cascata de estados do OTS, identica a do original."""
    return ("if([DahlDesign.PitBoxPosition] > 0, '%s',\n"
            "if([DahlDesign.SF23.OTAllowed] && ![DahlDesign.SF23.OTActive], '%s',\n"
            "if([DahlDesign.SF23.OTActive], '%s',\n"
            "if([DahlDesign.SF23.OTCooldownActive], '%s',\n"
            "if(![DahlDesign.SF23.OTAllowed], '%s',\n"
            "'%s')))))" % (box, ready, active, cooldown, blocked, fallback))


#: Cor do estado -- usada pelo texto, pelo numero e pela barra, para os tres
#: mudarem juntos e o estado ser legivel pela cor antes da palavra.
COLOR = state_formula("transparent", READY, ACTIVE, COOLDOWN, BLOCKED, BLOCKED)

#: A palavra do estado. 'transparent' no box some com o texto, como no original.
LABEL = state_formula("PITLANE", "READY", "ACTIVE", "COOL", "N/A", BLOCKED)


def bar(region):
    """Barra do quanto resta: o gauge do original, recortado em pente."""
    return [
        tile(region, name="OTS Track", color=TRACK, radius=0),
        LinearGaugeItem(
            name="OTS Gauge",
            IsLinearGauge=True,
            GaugeOrientation=0,
            GaugeAlignment=0,
            AutoSize=False,
            GaugeColor=READY,
            AlternateGaugeColor=ACTIVE,
            UseAlternateStyle=False,
            Minimum=0.0, Maximum=CAPACITY, Value=CAPACITY, Steps=0.0,
            PAW=region.width,
            BackgroundColor="#00FFFFFF",
            BorderStyle={
                "RadiusTopLeft": 0, "RadiusTopRight": 0,
                "RadiusBottomLeft": 0, "RadiusBottomRight": 0,
            },
            Left=region.x, Top=region.y,
            Width=region.width, Height=region.height,
            Visible=True,
            BlinkPhasisInverted=False,
            RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
            bindings={
                "Value": ncalc("[DahlDesign.SF23.OTTimeLeft]"),
                "GaugeColor": ncalc(COLOR),
            },
        ),
        ImageItem(
            name="OTS Comb",
            Image=COMB_IMAGE,
            AutoSize=False,
            BackgroundColor="#00FFFFFF",
            Left=region.x, Top=region.y,
            Width=region.width, Height=region.height,
            Visible=True,
            BlinkPhasisInverted=False,
            RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
    ]


def layer():
    """A faixa do push-to-pass inteira."""
    value_top = INNER.y + SIZE_LABEL + 6.0
    value = grid.Region(INNER.x, value_top, INNER.width,
                        COMB_AREA.y - 6.0 - value_top)
    half = value.width / 2

    return Layer(
        tile(PANEL, name="OTS Tile", radius=CORNER_RADIUS_TILE),
        caption(INNER.x, INNER.y, half, "Push to pass",
                name="OTS Caption", size=SIZE_LABEL),
        caption(INNER.x + half, INNER.y, half, "S left",
                name="OTS Left Caption", size=SIZE_LABEL, align=RIGHT),
        text(value.x, value.y, half, value.height,
             "READY", name="Status", size=SIZE_VALUE_SM, weight=WEIGHT_VALUE,
             align=LEFT, bindings={
                 "Text": ncalc(LABEL),
                 "TextColor": ncalc(COLOR),
                 "BlinkEnabled": ncalc(ACTIVE_BLINK),
             }),
        text(value.x + half, value.y, half, value.height,
             "200", name="OTS Left", size=SIZE_VALUE_SM, weight=WEIGHT_VALUE,
             align=RIGHT,
             bindings={
                 "Text": formatted("[DahlDesign.SF23.OTTimeLeft]", "000"),
             }),
        *bar(COMB_AREA),
        name="OTS",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
