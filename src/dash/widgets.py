"""Componentes reutilizaveis, na linguagem visual das referencias.

O SimHub so oferece retangulos, textos e gauges. Os padroes das complications
do watchOS -- tile, valor colado a unidade, rotulo em caixa alta, barra
segmentada -- sao montados aqui uma vez e reusados pelas regioes.
"""

from simhub.model import OFF, RectangleItem, TextItem
from simhub.theme import (
    CORNER_RADIUS_TILE, FONT, SIZE_LABEL, SIZE_UNIT, SIZE_VALUE, TEXT,
    TEXT_SECONDARY, TILE, TRACK, WEIGHT_LABEL, WEIGHT_UNIT, WEIGHT_VALUE,
    rounded,
)

LEFT, CENTER, RIGHT = 0, 1, 2


def optional(value):
    """None significa "campo ausente", nao "campo com valor nulo"."""
    return OFF if value is None else value


def tile(region, name=None, color=TILE, radius=CORNER_RADIUS_TILE,
         border=None, opacity=None, bindings=None):
    """Superficie de fundo de um bloco de dados."""
    return RectangleItem(
        name=name or "Tile",
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(border, radius=radius),
        Left=region.x, Top=region.y,
        Width=region.width, Height=region.height,
        Opacity=optional(opacity),
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def text(x, y, width, height, content, *, name=None, size=SIZE_VALUE,
         color=TEXT, weight=None, align=LEFT, valign=CENTER, font=FONT,
         mono=False, char_width=None, special_chars=None,
         special_chars_width=None, opacity=None, bindings=None):
    """TextItem com os defaults do design system."""
    return TextItem(
        name=name or "Text",
        IsTextItem=True,
        Font=font,
        FontWeight=optional(weight),
        FontSize=size,
        Text=content,
        TextColor=color,
        HorizontalAlignment=align,
        VerticalAlignment=valign,
        UseMonospacedText=True if mono else OFF,
        CharWidth=optional(char_width),
        SpecialChars=optional(special_chars),
        SpecialCharsWidth=optional(special_chars_width),
        BackgroundColor="#00FFFFFF",
        Left=x, Top=y, Width=width, Height=height,
        Opacity=optional(opacity),
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def caption(x, y, width, content, *, name=None, color=TEXT_SECONDARY,
            size=SIZE_LABEL, align=LEFT, height=16.0, bindings=None):
    """Rotulo em caixa alta. Nomeia o dado sem competir com ele."""
    return text(x, y, width, height, content.upper(), name=name or "Caption",
                size=size, color=color, weight=WEIGHT_LABEL, align=align,
                bindings=bindings)


def value_unit(region, value, unit, *, name="Value", unit_width=None,
               value_size=SIZE_VALUE, unit_size=SIZE_UNIT, color=TEXT,
               unit_color=TEXT_SECONDARY, mono=False, align=RIGHT,
               value_bindings=None, unit_bindings=None):
    """O par numero grande + unidade pequena: a assinatura das referencias.

    Por padrao (`align=RIGHT`) o valor fica alinhado a direita e a unidade a
    esquerda, encostados no meio, entao o par continua colado qualquer que
    seja o comprimento do numero -- o SimHub nao mede texto para posicionar.

    Com `align=LEFT` o par cola na borda esquerda da regiao, como o rotulo
    acima dele -- e o padrao das referencias (valor sempre alinhado com o
    rotulo, nunca "flutuando" pra direita conforme o numero de digitos muda).
    """
    unit_width = unit_width if unit_width is not None else len(unit) * unit_size * 0.62
    value_width = region.width - unit_width

    baseline = region.y + (region.height - value_size) * 0.5
    unit_drop = (value_size - unit_size) * 0.62

    if align is LEFT:
        # O valor cola na esquerda; a unidade, sem como saber a largura real
        # do numero (o SimHub nao mede texto), fica ancorada logo depois de
        # uma largura de valor generosa o bastante para o maior caso comum.
        return [
            text(region.x, region.y, value_width, region.height, value,
                 name=name, size=value_size, color=color, weight=WEIGHT_VALUE,
                 align=LEFT, mono=mono, bindings=value_bindings),
            text(region.x + value_width, baseline + unit_drop,
                 unit_width, unit_size * 1.4, unit,
                 name=f"{name} Unit", size=unit_size, color=unit_color,
                 weight=WEIGHT_UNIT, align=LEFT, valign=CENTER,
                 bindings=unit_bindings),
        ]

    return [
        text(region.x, region.y, value_width, region.height, value,
             name=name, size=value_size, color=color, weight=WEIGHT_VALUE,
             align=RIGHT, mono=mono, bindings=value_bindings),
        text(region.x + value_width + 2.0, baseline + unit_drop,
             unit_width, unit_size * 1.4, unit,
             name=f"{name} Unit", size=unit_size, color=unit_color,
             weight=WEIGHT_UNIT, align=LEFT, valign=CENTER,
             bindings=unit_bindings),
    ]


def segmented_bar(region, value_expression, *, count=12, minimum=0.0,
                  maximum=100.0, colors=None, color=None, gap=3.0,
                  radius=2, name="Bar", track=TRACK, reverse=False):
    """Barra de segmentos que acendem conforme o valor sobe.

    Cada segmento tem seu proprio limiar, entao a barra e so um conjunto de
    retangulos com binding de Visible -- o SimHub nao precisa de gauge para
    isso, e assim cada faixa pode ter cor propria.

    `colors` da uma cor por segmento (progressao verde -> amarelo -> vermelho);
    `color` usa uma unica cor. `reverse` acende da direita para a esquerda.
    """
    span = (region.width - gap * (count - 1)) / count
    step = (maximum - minimum) / count
    style = rounded(radius=radius)

    def segment_x(index):
        position = (count - 1 - index) if reverse else index
        return region.x + (span + gap) * position

    def rect(index, fill, bindings=None):
        return RectangleItem(
            name=f"{name} {index + 1}",
            IsRectangleItem=True,
            BackgroundColor=fill,
            BorderStyle=style,
            Left=segment_x(index), Top=region.y,
            Width=span, Height=region.height,
            Visible=True,
            BlinkPhasisInverted=False,
            RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
            bindings=bindings,
        )

    from simhub.bindings import ncalc

    items = [rect(i, track) for i in range(count)]
    for index in range(count):
        threshold = minimum + step * (index + 1)
        fill = colors[index] if colors else color
        items.append(rect(index, fill, bindings={
            "Visible": ncalc(f"if({value_expression} >= {threshold:g}, 1, 0)"),
        }))
    return items


def ramp(count, stops):
    """Distribui uma lista de cores por `count` segmentos, em blocos iguais.

    Usado para a progressao das barras: os primeiros segmentos em verde, os do
    meio em amarelo, os ultimos em vermelho.
    """
    out = []
    for index in range(count):
        position = int(index * len(stops) / count)
        out.append(stops[min(position, len(stops) - 1)])
    return out
