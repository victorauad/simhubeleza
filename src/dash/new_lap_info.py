"""New Lap Info: saude do sistema por 5 s a cada volta nova.

Ocupa o lugar dos setores, no rodape da direita, com o mesmo cartao e o
mesmo padrao dos outros rodapes: rotulo em cima, numero embaixo, filetes
entre os campos. Cinco campos, todos com a mesma leitura de cor -- branco
quando esta tudo bem, ambar quando merece atencao, vermelho quando e
problema:

  FPS        `FrameRate` do proprio iRacing (nao depende de RTSS).
  PING MS    `ChanLatency`, em ms.
  NET %      `ChanQuality`, a qualidade do canal com o servidor.
  CPU/GPU    temperaturas do provedor ligado no SimHub (HWiNFO Pro, Aida64
             ou Afterburner) -- nomes em `states.CPU_TEMP`/`GPU_TEMP`.

Offline, ping e rede nao existem: viram N/A, como qualquer valor nulo ou
zero.
"""

from simhub.bindings import js
from simhub.model import Layer
from simhub.theme import (
    AMBER, MONO_ADVANCE, RED, SIZE_LABEL_FOOTER, SIZE_VALUE, TEXT, TEXT_TERTIARY,
)
from . import states
from .widgets import labeled, spread, tile

T = states.TELEMETRY
VALUE_SIZE = SIZE_VALUE
INSET_X, INSET_Y = 14.0, 12.0
MIN_GAP = 16.0

#: (nome, rotulo, exemplo, expressao JS do numero, atencao, problema, alto e
#: ruim). `None` na expressao = propriedade ainda nao configurada.
FIELDS = [
    ("FPS", "FPS", "118", f"num($prop('{T}FrameRate'))", 60, 45, False),
    ("Ping", "Ping ms", "38", f"(num($prop('{T}ChanLatency')) || 0) * 1000",
     100, 200, True),
    ("Net", "Net %", "99",
     f"(function (q) {{ return q != null && q <= 1 ? q * 100 : q; }})"
     f"(num($prop('{T}ChanQuality')))", 90, 70, False),
    ("CPU", "CPU temp", "64",
     None if states.CPU_TEMP is None else f"num($prop('{states.CPU_TEMP}'))",
     80, 90, True),
    ("GPU", "GPU temp", "71",
     None if states.GPU_TEMP is None else f"num($prop('{states.GPU_TEMP}'))",
     80, 87, True),
]


def width(label, sample):
    return (max(len(label) * SIZE_LABEL_FOOTER, len(sample) * VALUE_SIZE)
            * MONO_ADVANCE)


def value_formula(expression):
    if expression is None:
        return js("return 'N/A';")
    return js(states.BASE + f"var v = {expression};\r\n"
              "if (v == null || v == 0) return 'N/A';\r\n"
              "return String(Math.round(v));")


def color_formula(expression, warn, bad, high_is_bad):
    if expression is None:
        return js(f"return '{TEXT_TERTIARY}';")
    cmp_bad = f"v >= {bad}" if high_is_bad else f"v <= {bad}"
    cmp_warn = f"v >= {warn}" if high_is_bad else f"v <= {warn}"
    return js(states.BASE + f"var v = {expression};\r\n"
              f"if (v == null || v == 0) return '{TEXT_TERTIARY}';\r\n"
              f"if ({cmp_bad}) return '{RED}';\r\n"
              f"if ({cmp_warn}) return '{AMBER}';\r\n"
              f"return '{TEXT}';")


def layer(region):
    """O cartao inteiro, em `region` (o rodape da direita)."""
    widths = [width(label, sample) for _, label, sample, *_ in FIELDS]
    cells, rules, gap = spread(region, widths, inset_x=INSET_X,
                               inset_y=INSET_Y, min_gap=MIN_GAP,
                               name="New Lap Info")
    items = [tile(region, name="New Lap Info Tile"), *rules]
    for cell, (name, label, sample, expression, warn, bad, high) in zip(
            cells, FIELDS):
        for item in labeled(
                cell, label, sample, name=f"Sys {name}", size=VALUE_SIZE,
                slack=gap / 2, label_size=SIZE_LABEL_FOOTER,
                bindings={"Text": value_formula(expression),
                          "TextColor": color_formula(expression, warn, bad,
                                                     high)}):
            items.append(states.content(item))

    out = Layer(
        *items,
        name="New Lap Info",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": states.new_lap_visible()},
    )
    return states.gate(out)
