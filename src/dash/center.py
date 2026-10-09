"""Centro: marcha, velocidade e RPM.

E o bloco que o piloto olha de relance, entao a marcha domina: um disco no
meio da coluna, com a marcha centrada dentro, e um brilho por tras que muda de
cor com o estado do carro. Velocidade e RPM ficam no topo, em colunas opostas,
cada uma com seu rotulo em cima: rotulo pequeno cinza, numero grande embaixo.

Sem tile de fundo, como no canvas: o disco e o proprio bloco.
"""

from simhub.bindings import formatted, ncalc
from simhub.model import OFF, GearText, Layer, RectangleItem
from simhub.theme import (
    FONT_GEAR, GLOW_IDLE, GLOW_LIMITER, GLOW_OTS_ACTIVE, GLOW_OTS_COOLDOWN,
    GLOW_SHIFT, GUTTER, PADDING, SEPARATOR, SIZE_GEAR, SIZE_LABEL, SIZE_VALUE,
    TEXT, WEIGHT_VALUE, rounded,
)
from . import layout as grid
from . import ots
from .widgets import CENTER, LEFT, RIGHT, caption, text

PANEL = grid.CENTER.inset(left=grid.MARGIN, right=grid.MARGIN, bottom=GUTTER)

HEADER_HEIGHT = 72.0

#: Disco da marcha, o anel escuro em volta dele e o brilho por tras.
DISC = 190.0
RING = 6.0
GLOW = 290.0
GLOW_BLUR = 40.0
DISC_COLOR = "#FF101215"
RING_COLOR = "#FF0E1013"
RING_EDGE = "#FF2A2F35"
DIVIDER = "#FF3A4048"

#: Cor do brilho, por prioridade: limite de RPM (roxo) > push to pass ativo
#: (verde) > push to pass carregando (vermelho) > pit limiter (ciano) >
#: repouso (ambar).
GLOW_COLOR = (
    "if([Rpms] > [GameRawData.Telemetry.PlayerCarSLBlinkRPM], '%s',\n"
    "if([DahlDesign.SF23.OTActive], '%s',\n"
    "if([DahlDesign.SF23.OTCooldownActive], '%s',\n"
    "if([PitLimiterOn], '%s', '%s'))))"
    % (GLOW_SHIFT, GLOW_OTS_ACTIVE, GLOW_OTS_COOLDOWN, GLOW_LIMITER, GLOW_IDLE)
)


def readout(region, label, sample, expression, format_string, *, name, align):
    """Rotulo em cima, numero embaixo, ancorado na borda da coluna."""
    return [
        caption(region.x, region.y, region.width, label,
                name=f"{name} Label", size=SIZE_LABEL, align=align),
        text(region.x, region.y + SIZE_LABEL + 4.0, region.width,
             region.height - SIZE_LABEL - 4.0, sample,
             name=name, size=SIZE_VALUE, color=TEXT, weight=WEIGHT_VALUE,
             align=align,
             bindings={"Text": formatted(expression, format_string)}),
    ]


def header(region):
    """Velocidade a esquerda, RPM a direita, marcha entre as duas."""
    inner = region.inset(left=PADDING, right=PADDING)
    width = inner.width * 0.4
    speed = grid.Region(inner.x, inner.y, width, inner.height)
    rpm = grid.Region(inner.right - width, inner.y, width, inner.height)
    return [
        *readout(speed, "Spd", "000", "[SpeedKmh]", "000",
                 name="Speed", align=LEFT),
        *readout(rpm, "Rpm", "000", "[Rpms]/10", "000",
                 name="Rpm", align=RIGHT),
    ]


def circle(name, cx, cy, diameter, color, *, border=None, blur=None,
           bindings=None):
    """Retangulo com raio de meio lado: um circulo centrado em (cx, cy)."""
    return RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(border, 1, radius=diameter / 2),
        BlurRadius=blur if blur else OFF,
        Left=cx - diameter / 2, Top=cy - diameter / 2,
        Width=diameter, Height=diameter,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def divider(region):
    """Filete sob o cabecalho, so nas pontas: o miolo fica livre para o
    brilho da marcha."""
    span = region.width * 0.35
    return [
        RectangleItem(
            name=f"Divider {index + 1}",
            IsRectangleItem=True,
            BackgroundColor=DIVIDER,
            Left=x, Top=region.bottom, Width=span, Height=1.0,
            Opacity=60.0,
            Visible=True,
            BlinkPhasisInverted=False,
            RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        )
        for index, x in enumerate((region.x, region.right - span))
    ]


def disc(region):
    """Brilho, anel e disco, centrados no espaco abaixo do cabecalho."""
    cx = region.x + region.width / 2
    cy = region.y + region.height / 2
    return [
        circle("Gear Glow", cx, cy, GLOW, GLOW_IDLE, blur=GLOW_BLUR,
               bindings={"BackgroundColor": ncalc(GLOW_COLOR)}),
        circle("Gear Ring", cx, cy, DISC + RING * 2 + 2, RING_COLOR,
               border=RING_EDGE),
        circle("Gear Disc", cx, cy, DISC, DISC_COLOR, border=SEPARATOR),
    ], grid.Region(cx - DISC / 2, cy - DISC / 2, DISC, DISC)


def gear(region):
    """A marcha, centrada no disco -- e o que se le sem focar."""
    return GearText(
        name="GearText",
        GearBlinkText=False,
        GearBlinkDelay=100,
        TextColor=TEXT,
        BackgroundColor="#00FFFFFF",
        GearBackgoundColor="#00FFFFFF",
        IgnoreNeutralGear=False,
        GearBlinkBackgroundColor="#FFFF4500",
        GearBlinkBackground=False,
        GearTextColor=TEXT,
        GearBlinkTextColor="#FFFF00FF",
        DesignerText="N",
        NoDataText="N",
        IsTextItem=True,
        Font=FONT_GEAR,
        FontWeight="Bold",
        FontSize=SIZE_GEAR,
        HorizontalAlignment=CENTER,
        VerticalAlignment=CENTER,
        Left=region.x, Top=region.y,
        Width=region.width, Height=region.height,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def layer():
    """A coluna central inteira, com a faixa do OTS logo abaixo."""
    top, rest = PANEL.inset(top=PADDING).split_top(HEADER_HEIGHT - PADDING)
    backdrop, gear_box = disc(rest)

    return Layer(
        Layer(
            *backdrop,
            *header(top),
            *divider(top),
            gear(gear_box),
            name="Speed & Gear",
            Group=True, Repetitions=0, Visible=True,
            BlinkPhasisInverted=False, RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        ots.layer(),
        name="Center Component",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
