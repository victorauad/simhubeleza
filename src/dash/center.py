"""Centro: marcha, velocidade e RPM.

E o bloco que o piloto olha de relance, entao a marcha domina -- ocupa quase
toda a altura e e o unico elemento em fonte propria. Velocidade e RPM ficam no
topo, em colunas opostas, cada uma com seu rotulo em cima no padrao das
referencias: rotulo pequeno cinza, numero grande embaixo.
"""

from simhub.bindings import formatted
from simhub.model import GearText, Layer
from simhub.theme import (
    CORNER_RADIUS_TILE, CYAN, FONT_GEAR, GUTTER, PADDING, SIZE_GEAR,
    SIZE_LABEL, SIZE_VALUE, TEXT, TEXT_SECONDARY, WEIGHT_VALUE,
)
from . import layout as grid
from . import ots
from .widgets import CENTER, LEFT, RIGHT, caption, text, tile

PANEL = grid.CENTER.inset(left=grid.MARGIN, right=grid.MARGIN, bottom=GUTTER)

HEADER_HEIGHT = 72.0


def readout(region, label, sample, expression, format_string, *, name, align):
    """Rotulo em cima, numero embaixo, ancorado na borda da coluna."""
    return [
        caption(region.x, region.y, region.width, label,
                name=f"{name} Label", size=SIZE_LABEL, align=align),
        text(region.x, region.y + SIZE_LABEL + 4.0, region.width,
             region.height - SIZE_LABEL - 4.0, sample,
             name=name, size=SIZE_VALUE, color=TEXT, weight=WEIGHT_VALUE,
             align=align, mono=True, char_width=22.0,
             bindings={"Text": formatted(expression, format_string)}),
    ]


def header(region):
    """Velocidade a esquerda, RPM a direita, marcha entre as duas."""
    inner = region.inset(left=PADDING, right=PADDING)
    width = inner.width * 0.4
    speed = grid.Region(inner.x, inner.y, width, inner.height)
    rpm = grid.Region(inner.right - width, inner.y, width, inner.height)
    return [
        # A unidade entra no rotulo, nao ao lado do numero: os dois valores
        # sao monoespacados e alinhados nas bordas opostas da coluna, entao
        # uma unidade colada neles brigaria com a marcha logo abaixo. O RPM
        # segue dividido por 10 como no original -- o rotulo e que passa a
        # dizer isso.
        *readout(speed, "Spd km/h", "000", "[SpeedKmh]", "000",
                 name="Speed", align=LEFT),
        *readout(rpm, "Rpm x10", "000", "[Rpms]/10", "000",
                 name="Rpm", align=RIGHT),
    ]


def gear(region):
    """A marcha. Unico elemento em Audiowide -- e o que se le sem focar."""
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
    top, rest = PANEL.inset(top=PADDING).split_top(HEADER_HEIGHT)

    return Layer(
        tile(PANEL, name="Center Tile", radius=CORNER_RADIUS_TILE),
        Layer(
            *header(top),
            gear(rest),
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
