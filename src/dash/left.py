"""Coluna esquerda: telemetria do carro e o contexto da sessao.

O wireframe pede "telemetria em cima, embaixo todas as infos". Dai as tres
faixas: o grafico de entradas ocupa o topo, uma linha de tiles traz o que o
piloto ajusta ou consome durante a volta (bias, combustivel, condicoes da
pista) e o rodape
guarda o que so se consulta entre voltas (voltas, incidentes, SoF, tempo).

A hierarquia e a das referencias: rotulo em caixa alta cinza em cima, numero
grande embaixo, unidade pequena colada nele.
"""

from simhub.bindings import formatted, js, ncalc
from simhub.model import ImageItem, Layer, RectangleItem
from simhub.theme import (
    BIAS, BIAS_DOWN, BIAS_UP, CYAN, GUTTER, ORANGE, PADDING, SIZE_LABEL,
    SIZE_VALUE_SM, TEXT, TEXT_TERTIARY, TILE, MONO_ADVANCE,
)
from . import layout as grid
from .widgets import LEFT, caption, separators, tile, value_unit

PANEL = grid.LEFT.inset(left=grid.MARGIN, right=grid.MARGIN)

#: Resolucao nativa do widget de telemetria (Telemetry.djson).
CHART_NATIVE = (607.0, 250.0)

CHART_HEIGHT = PANEL.width * CHART_NATIVE[1] / CHART_NATIVE[0]

#: O rodape tem altura fixa, compartilhada com o OTS e o rodape da direita --
#: os tres formam uma barra inferior unica. Quem absorve o que sobra e a linha
#: de stats, nao o rodape; do contrario mudar a altura da barra superior
#: desalinha as tres faixas de baixo.
FOOTER_HEIGHT = grid.BOTTOM_BAR_HEIGHT
STATS_HEIGHT = PANEL.height - CHART_HEIGHT - FOOTER_HEIGHT - GUTTER * 2

#: Linha de stats depois do bias: combustivel e condicoes da pista. O
#: exemplo tem o formato do valor real e define a largura da celula; o
#: ultimo campo e o espaco extra no rotulo (em caracteres) -- o do vento
#: abriga a seta da direcao.
STATS_FIELDS = [
    ("Fuel Target", "FPL target", "2.30",
     "[DataCorePlugin.Computed.Fuel_LastLapConsumption]", "0.00", 0.0),
    ("Fuel Last", "FPL last", "2.30",
     "[DataCorePlugin.Computed.Fuel_LitersPerLap]", "0.00", 0.0),
    ("Wind", "Wind", "32", "[GameRawData.Telemetry.WindVel]*3.6", "00", 4.5),
    ("Track", "Track", "00", "[GameRawData.Telemetry.TrackTemp]", "00", 0.0),
    ("Air", "Air", "00", "[AirTemperature]", "00", 0.0),
    ("Rain", "Rain", "00",
     "format([GameRawData.Telemetry.Precipitation] * 100, 'NA')", None, 0.0),
]

#: Rodape: a sessao, mais a hora e o grip que vieram do rodape da direita
#: (hoje dos setores).
FOOTER_FIELDS = [
    ("Laps", "Laps", "00", "[CompletedLaps]", "00", None),
    ("Left", "Left", "00", "[RemainingLaps]", "00", None),
    ("Inc", "Inc", "00",
     "[GameRawData.Telemetry.PlayerCarMyIncidentCount]", "00", ORANGE),
    ("SoF", "SoF", "34",
     "[IRacingExtraProperties.iRacing_Class_SoF]/100", "00", None),
    ("Time", "Time", "00:00", "[SessionTimeLeft]", "mm\\.ss", CYAN),
    ("Hour", "Hour", "00:00", "[DataCorePlugin.CurrentDateTime]", "HH:mm", CYAN),
    ("Grip", "Grip", "00",
     "[GameRawData.CurrentSessionInfo.SessionTrackRubberState]", None, None),
]

#: Recuo das pontas das duas fileiras e o piso do respiro entre campos.
FOOTER_INSET = 10.0
ROW_MIN_GAP = 11.0

#: O bias e o dado mais consultado da linha de stats: numero maior que os
#: outros.
BIAS_SIZE = 38.0
STAT_SIZE = 28.0

#: Respiro interno dos cartoes da coluna (o mesmo dos cartoes do canvas).
CARD_INSET = 12.0

#: Brilho do brake bias quando o valor muda: verde se subiu, vermelho se
#: desceu, segurando a cor por um quarto do tempo e voltando ao ambar.
BIAS_FLASH_MS = 1600
BIAS_HOLD = 0.25
BIAS_FLASH_BG_ALPHA = 0x29     # ~16%: o fundo so tinge, o numero e que brilha


def bias_flash(prefix, rest, up, down, alpha=None):
    """Formula JS: a cor do brake bias, com o brilho de mudanca.

    Guarda o ultimo valor em `root` (que o SimHub preserva entre avaliacoes)
    e, quando ele muda, marca a hora e a direcao. Por `BIAS_FLASH_MS` a cor
    sai do verde/vermelho e volta para `rest`. `alpha`, se dado, troca a
    opacidade das cores de brilho (para o fundo); `rest` ja vem pronta.
    `prefix` separa as chaves de cada formula em `root`.
    """
    def rgb(color):
        return [int(color[i:i + 2], 16) for i in (3, 5, 7)]

    a_flash = alpha if alpha is not None else 0xFF
    a_rest = int(rest[1:3], 16)
    return js(
        f"var v = $prop('BrakeBias');\r\n"
        f"var k = '{prefix}';\r\n"
        f"if (root[k + 'v'] == null) {{ root[k + 'v'] = v; root[k + 't'] = 0; root[k + 'd'] = 0; }}\r\n"
        f"if (v != root[k + 'v']) {{\r\n"
        f"\troot[k + 'd'] = v > root[k + 'v'] ? 1 : -1;\r\n"
        f"\troot[k + 't'] = Date.now();\r\n"
        f"\troot[k + 'v'] = v;\r\n"
        f"}}\r\n"
        f"var t = (Date.now() - root[k + 't']) / {BIAS_FLASH_MS};\r\n"
        f"if (root[k + 'd'] == 0 || t >= 1) {{ return '{rest}'; }}\r\n"
        f"var f = t < {BIAS_HOLD} ? 1 : 1 - (t - {BIAS_HOLD}) / {1 - BIAS_HOLD};\r\n"
        f"var from = root[k + 'd'] > 0 ? {rgb(up)} : {rgb(down)};\r\n"
        f"var to = {rgb(rest)};\r\n"
        f"var a = Math.round({a_rest} + ({a_flash} - {a_rest}) * f);\r\n"
        f"var hex = function (n) {{ var s = Math.round(n).toString(16).toUpperCase(); return s.length < 2 ? '0' + s : s; }};\r\n"
        f"var c = '#' + hex(a);\r\n"
        f"for (var i = 0; i < 3; i++) {{ c += hex(to[i] + (from[i] - to[i]) * f); }}\r\n"
        f"return c;"
    )


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
         format_string=None, value_size=STAT_SIZE, unit_color=TEXT_TERTIARY,
         color=TEXT, extra=(), align=LEFT, color_binding=None):
    """Rotulo em cima, valor grande embaixo -- alinhados na mesma borda.

    Varios `stat()` dividem um unico cartao de fundo, separados por
    filetes: o cartao e desenhado por quem monta a fileira.
    """
    label_height = SIZE_LABEL + 6.0
    body = grid.Region(region.x, region.y + label_height,
                       region.width, region.height - label_height)
    binding = (formatted(expression, format_string) if format_string
               else ncalc(expression))
    bindings = {"Text": binding}
    if color_binding:
        bindings["TextColor"] = color_binding
    return [
        caption(region.x, region.y, region.width, label,
                name=f"{name} Label", size=SIZE_LABEL, align=align),
        *value_unit(body, value, unit or "", name=name,
                    value_size=value_size, unit_color=unit_color, color=color,
                    unit_width=0.0 if not unit else None, align=align,
                    value_bindings=bindings),
        *extra,
    ]


def wind_arrow(region):
    """Seta que gira com a direcao do vento, encostada no rotulo.

    Fica na linha do rotulo, nao na do valor: a direcao qualifica o "WIND", e
    assim nao disputa espaco com o numero.
    """
    size = 14.0
    return ImageItem(
        name="Wind Arrow",
        Image="PositionGain",
        AutoSize=False,
        BackgroundColor="#00FFFFFF",
        Left=region.right - size,
        Top=region.y - 2.0,
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


def fitted(region, widths, *, inset, min_gap):
    """Celulas da largura do proprio conteudo, com o que sobra repartido em
    respiros iguais entre elas e o filete no meio de cada respiro.

    Devolve as celulas, as posicoes dos filetes (para `separators`) e o
    respiro, que tambem serve de folga para a caixa do valor: o SimHub nao
    mede texto, e um valor maior que o exemplo nao deve quebrar linha.
    """
    inner = region.inset(top=CARD_INSET, bottom=CARD_INSET,
                         left=inset, right=inset)
    gap = (inner.width - sum(widths)) / (len(widths) - 1)
    assert gap >= min_gap, f"fileira nao cabe: respiro de {gap:.1f}"
    columns, x = [], inner.x
    for width in widths:
        columns.append(grid.Region(x, inner.y, width, inner.height))
        x += width + gap
    rules = [grid.Region(cell.x - gap / 2, region.y, 0.0, region.height)
             for cell in columns]
    return columns, rules, gap


def content_width(label, sample, size, extra=0.0):
    """Largura de um campo: o rotulo ou o valor, o que for maior."""
    return max(len(label) * SIZE_LABEL + extra, len(sample) * size) * MONO_ADVANCE


def stats_row(region):
    """O que muda ao longo da volta: bias, combustivel e as condicoes da
    pista (vento, asfalto, ar, chuva).

    Sem unidades -- o rotulo ja diz o que e, e a largura que elas ocupavam e
    o que permite trazer as condicoes da pista para ca.
    """
    widths = [content_width("Brake bias", "55.6", BIAS_SIZE),
              *(content_width(label, sample, STAT_SIZE, extra)
                for _, label, sample, *_, extra in STATS_FIELDS)]
    columns, rules, gap = fitted(region, widths, inset=FOOTER_INSET,
                                 min_gap=ROW_MIN_GAP)
    boxes = [grid.Region(c.x, c.y, c.width + gap / 2, c.height) for c in columns]
    bias = boxes[0]
    value_box = grid.Region(bias.x - 2.0, bias.bottom - BIAS_SIZE * 0.85,
                            4 * BIAS_SIZE * 0.6 + 4.0, BIAS_SIZE * 0.85)
    flash_bg = BIAS_FLASH_BG_ALPHA

    items = [
        tile(region, name="Car Tile"),
        *separators(rules, region),
        # Fundo do brilho, atras do numero: so tinge enquanto ele brilha.
        RectangleItem(
            name="Brake Bias Flash",
            IsRectangleItem=True,
            BackgroundColor="#00000000",
            BorderStyle={"RadiusTopLeft": 3, "RadiusTopRight": 8,
                         "RadiusBottomLeft": 8, "RadiusBottomRight": 3},
            Left=value_box.x, Top=value_box.y,
            Width=value_box.width, Height=value_box.height,
            Visible=True,
            BlinkPhasisInverted=False,
            RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
            bindings={"BackgroundColor": bias_flash(
                "biasBg", "#00F4A73A", BIAS_UP, BIAS_DOWN, alpha=flash_bg)},
        ),
        *stat(bias, "Brake bias", "55.6", "[BrakeBias]",
              name="Brake Bias", format_string="0.0", value_size=BIAS_SIZE,
              color=BIAS,
              color_binding=bias_flash("biasText", BIAS, BIAS_UP, BIAS_DOWN)),
    ]
    for cell, box, (name, label, sample, expression, fmt, extra) in zip(
            columns[1:], boxes[1:], STATS_FIELDS):
        items += stat(box, label, sample, expression, name=name,
                      format_string=fmt,
                      extra=[wind_arrow(cell)] if extra else ())
    return items


def footer_row(region):
    """Contexto da sessao: consultado entre voltas, nao dentro delas.

    Um unico cartao, com os campos separados por filetes -- no mesmo
    tratamento do OTS e do rodape da direita. As tres faixas inferiores
    formam assim uma barra inferior unica.
    """
    widths = [content_width(label, sample, SIZE_VALUE_SM)
              for _, label, sample, *_ in FOOTER_FIELDS]
    columns, rules, gap = fitted(region, widths, inset=FOOTER_INSET,
                                 min_gap=ROW_MIN_GAP)
    items = [tile(region, name="Footer Tile"), *separators(rules, region)]
    for cell, (name, label, sample, expression, fmt, color) in zip(
            columns, FOOTER_FIELDS):
        box = grid.Region(cell.x, cell.y, cell.width + gap / 2, cell.height)
        items += stat(box, label, sample, expression, name=name,
                      format_string=fmt, value_size=SIZE_VALUE_SM,
                      color=color or TEXT)
    return items


def layer():
    """A coluna esquerda inteira."""
    _, rest = PANEL.split_top(CHART_HEIGHT, gutter=GUTTER)
    stats, footer = rest.split_top(STATS_HEIGHT, gutter=GUTTER)

    chart_area = grid.Region(PANEL.x, PANEL.y, PANEL.width, CHART_HEIGHT)
    return Layer(
        # Tres cartoes, sem fundo de coluna: grafico, ajustes e sessao.
        tile(chart_area, name="Chart Tile", color=TILE),
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
