"""Push-to-pass do SF23: estado e segundos restantes.

O dado e um so -- quanto de overtake resta e se da para usar agora -- entao a
faixa nao se divide em tiles: estado a esquerda, segundos a direita, e uma
barra fina no rodape mostrando o quanto sobrou sem exigir leitura de numero.

As formulas de estado sao as do original; so os literais de cor mudaram, para
a paleta das referencias. Nomes CSS em vez de hex porque sao os que o SimHub
resolve com certeza em formula de cor -- e os escolhidos ficam a menos de um
por cento das cores da paleta.
"""

from simhub.bindings import formatted, ncalc
from simhub.model import LinearGaugeItem, Layer
from simhub.theme import (
    CORNER_RADIUS_TILE, FONT, PADDING, SIZE_LABEL, SIZE_VALUE, TEXT_SECONDARY,
    TRACK, WEIGHT_VALUE,
)
from . import layout as grid
from .widgets import LEFT, RIGHT, caption, text, tile

PANEL = grid.OTS.inset(left=grid.MARGIN, right=grid.MARGIN, bottom=grid.MARGIN)

#: Capacidade do sistema, em segundos. Define a escala da barra.
CAPACITY = 200.0
BAR_HEIGHT = 8.0

#: Cada estado do sistema, na ordem em que o original testa: box, pronto,
#: ativo, esfriando, indisponivel.
READY = "limegreen"
ACTIVE = "gold"
COOLDOWN = "orange"
BLOCKED = "dimgray"


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
    """Barra do quanto resta. Mantem o gauge do original, so mais fina."""
    return LinearGaugeItem(
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
        BackgroundColor=TRACK,
        BorderStyle={
            "BorderColor": "#00FFFFFF",
            "BorderTop": 1, "BorderBottom": 1,
            "BorderLeft": 1, "BorderRight": 1,
            "RadiusTopLeft": 4, "RadiusTopRight": 4,
            "RadiusBottomLeft": 4, "RadiusBottomRight": 4,
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
    )


def layer():
    """A faixa do push-to-pass inteira."""
    inner = PANEL.inset(left=PADDING, right=PADDING)
    body = grid.Region(inner.x, inner.y + PADDING,
                       inner.width, PANEL.height - BAR_HEIGHT - PADDING * 2.5)
    track = grid.Region(inner.x, PANEL.bottom - BAR_HEIGHT - PADDING,
                        inner.width, BAR_HEIGHT)

    return Layer(
        tile(PANEL, name="OTS Tile", radius=CORNER_RADIUS_TILE),
        caption(inner.x, inner.y + 4.0, inner.width, "Push to pass",
                name="OTS Caption", size=SIZE_LABEL),
        text(body.x, body.y + SIZE_LABEL, body.width * 0.55, body.height - SIZE_LABEL,
             "READY", name="Status", size=SIZE_VALUE, weight=WEIGHT_VALUE,
             align=LEFT, bindings={"Text": ncalc(LABEL), "TextColor": ncalc(COLOR)}),
        text(body.x + body.width * 0.55, body.y + SIZE_LABEL,
             body.width * 0.45, body.height - SIZE_LABEL,
             "200", name="OTS Left", size=SIZE_VALUE, weight=WEIGHT_VALUE,
             align=RIGHT, mono=True, char_width=24.0,
             bindings={
                 "Text": formatted("[DahlDesign.SF23.OTTimeLeft]", "000"),
                 "TextColor": ncalc(COLOR),
             }),
        bar(track),
        name="OTS",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
