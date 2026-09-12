"""Coluna esquerda: telemetria do carro e o contexto da sessao.

O wireframe pede "telemetria em cima, embaixo todas as infos". Dai as tres
faixas: o grafico de entradas ocupa o topo, uma linha de tiles traz o que o
piloto ajusta ou consome durante a volta (bias, combustivel, vento) e o rodape
guarda o que so se consulta entre voltas (voltas, incidentes, SoF, tempo).

A hierarquia e a das referencias: rotulo em caixa alta cinza em cima, numero
grande embaixo, unidade pequena colada nele.
"""

from simhub.bindings import formatted, ncalc
from simhub.model import ImageItem, Layer, TextItem
from simhub.theme import (
    BACKGROUND, CORNER_RADIUS_TILE, CYAN, FONT_MONO, GUTTER, ORANGE, PADDING,
    SIZE_LABEL, SIZE_LABEL_SM, SIZE_UNIT, SIZE_VALUE, SIZE_VALUE_SM, TEXT,
    TEXT_SECONDARY, TILE, rounded,
)
from . import layout as grid
from .widgets import CENTER, LEFT, RIGHT, caption, optional, text, tile, value_unit

PANEL = grid.LEFT.inset(left=grid.MARGIN, right=grid.MARGIN)

#: Resolucao nativa do widget de telemetria (Telemetry.djson).
CHART_NATIVE = (607.0, 250.0)

CHART_HEIGHT = PANEL.width * CHART_NATIVE[1] / CHART_NATIVE[0]
STATS_HEIGHT = 96.0

#: A primeira coluna da linha de stats carrega o bias, que e o dado mais
#: consultado ali, entao ganha mais largura que as outras tres.
BIAS_WIDTH = 160.0


def chart():
    """Widget de telemetria, escalado para a largura exata do painel."""
    from simhub.model import WidgetItem

    return WidgetItem(
        name="Telemetry",
        FileName="Telemetry.djson",
        AutoSize=True,
        AutoSizeScale=PANEL.width / CHART_NATIVE[0],
        InitialScreenIndex=0,
        FreezePageChanges=True,
        EnableScreenRolesAndActivation=True,
        NextScreenCommand=0,
        PreviousScreenCommand=0,
        BackgroundColor="#00FFFFFF",
        Left=PANEL.x, Top=PANEL.y,
        Width=PANEL.width, Height=CHART_HEIGHT,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def stat(region, label, value, expression, unit=None, *, name,
         format_string=None, value_size=SIZE_VALUE, unit_color=TEXT_SECONDARY,
         color=TEXT, extra=()):
    """Um tile: rotulo em cima, valor grande embaixo."""
    inner = region.inset(left=PADDING, right=PADDING)
    label_height = SIZE_LABEL + 6.0
    body = grid.Region(inner.x, inner.y + label_height + 2.0,
                       inner.width, inner.height - label_height - 8.0)
    binding = (formatted(expression, format_string) if format_string
               else ncalc(expression))
    return [
        tile(region, name=f"{name} Tile"),
        caption(inner.x, inner.y + PADDING * 0.75, inner.width, label,
                name=f"{name} Label", size=SIZE_LABEL),
        *value_unit(body, value, unit or "", name=name,
                    value_size=value_size, unit_color=unit_color, color=color,
                    unit_width=0.0 if not unit else None,
                    value_bindings={"Text": binding}),
        *extra,
    ]


def wind_arrow(region):
    """Seta que gira com a direcao do vento, encostada no rotulo.

    Fica na linha do rotulo, nao na do valor: a direcao qualifica o "WIND", e
    assim nao disputa espaco com o numero.
    """
    size = 18.0
    return ImageItem(
        name="Wind Arrow",
        Image="PositionGain",
        AutoSize=False,
        BackgroundColor="#00FFFFFF",
        Left=region.right - size - PADDING,
        Top=region.y + PADDING * 0.75 - 1.0,
        Width=size, Height=size,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={
            "Rotation": ncalc(
                "format(180 + ([GameRawData.Telemetry.WindDir] * (180/3.14)), '0')"),
        },
    )


def stats_row(region):
    """Bias, combustivel e vento: o que muda ao longo da volta."""
    rest = (region.width - BIAS_WIDTH - GUTTER * 3) / 3
    columns = []
    x = region.x
    for width in (BIAS_WIDTH, rest, rest, rest):
        columns.append(grid.Region(x, region.y, width, region.height))
        x += width + GUTTER
    bias, target, last, wind = columns

    return [
        *stat(bias, "Brake bias", "55.6", "[BrakeBias]", "%",
              name="Brake Bias", format_string="0.0"),
        *stat(target, "FPL target", "2.30",
              "[DataCorePlugin.Computed.Fuel_LastLapConsumption]", "L",
              name="Fuel Target", format_string="0.00",
              value_size=SIZE_VALUE_SM),
        *stat(last, "FPL last", "2.30",
              "[DataCorePlugin.Computed.Fuel_LitersPerLap]", "L",
              name="Fuel Last", format_string="0.00",
              value_size=SIZE_VALUE_SM),
        *stat(wind, "Wind", "32", "[GameRawData.Telemetry.WindVel]*3.6",
              "km/h", name="Wind", format_string="00",
              value_size=SIZE_VALUE_SM,
              extra=[wind_arrow(wind)]),
    ]


def footer_row(region):
    """Contexto da sessao: consultado entre voltas, nao dentro delas."""
    cells = region.columns(5, gutter=GUTTER)
    fields = [
        ("Laps", "Laps", "00", "[CompletedLaps]", "00", None),
        ("Left", "Left", "00", "[RemainingLaps]", "00", None),
        ("Inc", "Inc", "00",
         "[GameRawData.Telemetry.PlayerCarMyIncidentCount]", "00", ORANGE),
        ("SoF", "SoF", "34",
         "[IRacingExtraProperties.iRacing_Class_SoF]/100", "00", None),
        ("Time", "Time", "00:00", "[SessionTimeLeft]", "mm\\.ss", CYAN),
    ]
    items = []
    for cell, (name, label, sample, expression, fmt, color) in zip(cells, fields):
        items += stat(cell, label, sample, expression, name=name,
                      format_string=fmt, value_size=SIZE_VALUE_SM,
                      color=color or TEXT)
    return items


def layer():
    """A coluna esquerda inteira."""
    top, rest = PANEL.split_top(CHART_HEIGHT, gutter=GUTTER)
    stats, footer = rest.split_top(STATS_HEIGHT, gutter=GUTTER)

    return Layer(
        chart(),
        Layer(
            *stats_row(stats),
            name="Car",
            Group=True, Repetitions=0, Visible=True,
            BlinkPhasisInverted=False, RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        Layer(
            *footer_row(footer),
            name="Session",
            Group=True, Repetitions=0, Visible=True,
            BlinkPhasisInverted=False, RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        name="Left Component2",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
