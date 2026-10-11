"""Setores: o rodape da direita, contra a melhor volta da sessao.

Duas tabelas lado a lado, no mesmo cartao dos outros rodapes:

  setores  o setor atual em cima (destacado, tempo e delta vivos), e os dois
           anteriores embaixo -- os que sao da volta passada ficam apagados.
           Funciona com qualquer numero de setores: a fileira gira, nao lista.
  voltas   LAST (com o delta), BEST e OPT (soma dos melhores setores).

A referencia e a melhor volta da sessao, a mesma do delta da barra de cima:
o SimHub so guarda tempos por setor dela (nao ha setores da melhor volta de
todos os tempos).

Regras de exibicao: valor nulo ou zero vira "N/A"; tempo de setor acima de
99 s vira "OFF" (o delta continua); delta acima de 99 s tambem vira "OFF".

O delta do setor atual e o delta ao vivo da volta menos o valor que ele
tinha quando o setor comecou, guardado em `root` -- comeca em zero a cada
setor e anda com a pilotagem. Os setores completos sao tempo do setor menos
o mesmo setor da melhor volta, sem estado.
"""

from simhub.bindings import js, ncalc
from simhub.model import Layer, RectangleItem
from simhub.theme import (
    FASTER, MONO_ADVANCE, PLAYER, SIZE_LABEL, SLOWER, TEXT, TEXT_SECONDARY,
    TEXT_TERTIARY, TILE_RAISED, WEIGHT_VALUE, rounded,
)
from . import layout as grid
from .widgets import LEFT, RIGHT, caption, separators, text, tile

VALUE_SIZE = 21.0
INSET_X = 12.0
INSET_Y = 10.0
ROWS = 3
#: Respiro entre colunas de uma tabela; entre as duas tabelas e o dobro,
#: com o filete no meio.
MIN_GAP = 11.0

#: Quantos quadros pular entre avaliacoes (RenderingSkip). O setor atual
#: anda a ~20 Hz; o resto so muda na troca de setor ou de volta (~6 Hz).
SKIP_LIVE = 2
SKIP_SLOW = 9

NA, OFF_TEXT = "N/A", "OFF"
LIMIT = 99.0

GAME = "DataCorePlugin.GameData."
LIVE_DELTA = "PersistantTrackerPlugin.SessionBestLiveDeltaSeconds"

#: Ajudantes comuns a todas as formulas JS do componente. `sec` normaliza
#: TimeSpan/numero/nulo em segundos (zero conta como nulo); os `fmt` aplicam
#: as regras de N/A e OFF.
PRELUDE = (
    "var sec = function (v) { if (v == null) return null; "
    "var s = typeof v === 'number' ? v : timespantoseconds(v); "
    "return (s == null || s == 0 || isNaN(s)) ? null : s; };\r\n"
    f"var n = $prop('{GAME}SectorsCount') || 3;\r\n"
    f"var i = $prop('{GAME}CurrentSectorIndex') || 0;\r\n"
    "var fmtSector = function (s) { if (s == null) return 'N/A'; "
    f"if (s > {LIMIT}) return 'OFF'; return s.toFixed(3); }};\r\n"
    "var fmtDelta = function (d, p) { if (d == null) return 'N/A'; "
    "var r = Number(d.toFixed(p)); if (r == 0) return 'N/A'; "
    f"if (Math.abs(r) > {LIMIT}) return 'OFF'; "
    "return (r > 0 ? '+' : '') + r.toFixed(p); };\r\n"
    "var colorDelta = function (d, p) { if (d == null) return 'na'; "
    "var r = Number(d.toFixed(p)); "
    f"if (r == 0 || Math.abs(r) > {LIMIT}) return 'na'; "
    "return r < 0 ? 'fast' : 'slow'; };\r\n"
    "var fmtLap = function (s) { if (s == null) return 'N/A'; "
    "var ms = Math.round(s * 1000); var m = Math.floor(ms / 60000); "
    "var r = (ms - m * 60000) / 1000; "
    "return m + ':' + (r < 10 ? '0' : '') + r.toFixed(3); };\r\n"
    # Setor completo `r` posicoes atras do atual: da volta atual se ainda
    # cabe nela, senao da volta passada.
    "var back = function (r) { var k = i - r; "
    "return k >= 1 ? { s: k, t: sec(currentlapgetsectortime(k, false)) } "
    ": { s: n + k, t: sec(lastlapgetsectortime(n + k, false)) }; };\r\n"
    "var sectorDelta = function (b) { "
    "var best = sec(sessionbestlapgetsectortime(b.s, false)); "
    "return (b.t == null || best == null) ? null : b.t - best; };\r\n"
)


def script(body):
    return js(PRELUDE + body)


def color_script(body, places):
    """Formula de cor de um delta: `body` define `d`."""
    return script(
        f"{body}\r\nvar c = colorDelta(d, {places});\r\n"
        f"return c == 'fast' ? '{FASTER}' : c == 'slow' ? '{SLOWER}' "
        f": '{TEXT_TERTIARY}';"
    )


#: Delta do setor atual: delta ao vivo menos o que ele era na entrada do
#: setor. A troca de setor zera a base.
LIVE_DELTA_BODY = (
    f"var live = $prop('{LIVE_DELTA}');\r\n"
    "if (root.i !== i) { root.i = i; root.base = live == null ? 0 : live; }\r\n"
    "var d = live == null ? null : live - root.base;"
)

#: Tempo do setor atual: tempo da volta menos o acumulado dos setores ja
#: fechados.
LIVE_TIME_BODY = (
    f"var lap = sec($prop('{GAME}CurrentLapTime'));\r\n"
    "var done = i > 1 ? sec(currentlapgetsectortime(i - 1, true)) : 0;\r\n"
    "var t = (lap == null || i < 1) ? null : lap - (done || 0);\r\n"
    "return fmtSector(t);"
)

#: Ultima volta contra a melhor.
LAST_DELTA_BODY = (
    f"var last = sec($prop('{GAME}LastLapTime'));\r\n"
    f"var best = sec($prop('{GAME}BestLapTime'));\r\n"
    "var d = (last == null || best == null) ? null : last - best;"
)

OPT_BODY = (
    "var total = 0;\r\n"
    "for (var k = 1; k <= n; k++) { var b = sec(bestsectortime(k, false)); "
    "if (b == null) return 'N/A'; total += b; }\r\n"
    "return fmtLap(total);"
)


def sector_number(r):
    """NCalc: o numero do setor `r` posicoes atras do atual."""
    index = f"[{GAME}CurrentSectorIndex]"
    return (f"if({index} - {r} >= 1, {index} - {r}, "
            f"[{GAME}SectorsCount] + {index} - {r})")


def previous_lap(r):
    """NCalc: verdadeiro quando o setor `r` atras e da volta passada."""
    return f"[{GAME}CurrentSectorIndex] - {r} < 1"


def widths():
    """Larguras das colunas: rotulo, tempo, delta -- setores e voltas."""
    glyph = VALUE_SIZE * MONO_ADVANCE
    label = SIZE_LABEL * MONO_ADVANCE
    return ((3 * label, 6 * glyph, 6 * glyph),
            (4 * label, 8 * glyph, 6 * glyph))


def columns(inner):
    """As seis colunas e a posicao do filete entre as duas tabelas."""
    sector_w, lap_w = widths()
    spans = (*sector_w, *lap_w)
    # Cinco respiros: quatro entre colunas de uma tabela e um duplo entre as
    # tabelas.
    gap = (inner.width - sum(spans)) / 6
    assert gap >= MIN_GAP, f"setores nao cabem: respiro de {gap:.1f}"
    out, x = [], inner.x
    for index, span in enumerate(spans):
        out.append(grid.Region(x, inner.y, span, inner.height))
        x += span + (gap * 2 if index == 2 else gap)
    rule = out[2].right + gap
    return out, rule, gap


def value(region, row, sample, name, *, bindings, color=TEXT, skip):
    item = text(region.x, row.y, region.width, row.height, sample,
                name=name, size=VALUE_SIZE, color=color, weight=WEIGHT_VALUE,
                align=RIGHT, bindings=bindings)
    item["RenderingSkip"] = skip
    return item


def label(region, row, content, name, *, color=TEXT_SECONDARY, bindings=None,
          skip=SKIP_SLOW):
    item = caption(region.x, row.y, region.width, content, name=name,
                   color=color, height=row.height, bindings=bindings)
    item["RenderingSkip"] = skip
    return item


def layer(region):
    """O cartao inteiro, em `region` (o rodape da direita)."""
    inner = region.inset(top=INSET_Y, bottom=INSET_Y,
                         left=INSET_X, right=INSET_X)
    cols, rule, gap = columns(inner)
    s_label, s_time, s_delta, l_label, l_time, l_delta = cols
    rows = inner.rows(ROWS)
    dim = f"'{TEXT_TERTIARY}'"

    items = [
        tile(region, name="Sectors Tile"),
        # `separators` pula a primeira celula (nao ha filete antes dela).
        *separators([inner, grid.Region(rule, region.y, 0.0, region.height)],
                    region, name="Sectors Separator"),
        # Destaque do setor atual: a linha de cima da tabela de setores.
        RectangleItem(
            name="Current Sector Row",
            IsRectangleItem=True,
            BackgroundColor=TILE_RAISED,
            BorderStyle=rounded(radius=3),
            Left=s_label.x - gap / 2, Top=rows[0].y,
            Width=s_delta.right - s_label.x + gap, Height=rows[0].height,
            Visible=True,
            BlinkPhasisInverted=False,
            RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        # Setor atual.
        label(s_label.inset(left=4.0), rows[0], "S2", "Sector Now Label",
              color=PLAYER, bindings={"Text": ncalc(
                  f"'S' + format([{GAME}CurrentSectorIndex], '0')")}),
        value(s_time, rows[0], "22.752", "Sector Now Time",
              bindings={"Text": script(LIVE_TIME_BODY)}, skip=SKIP_LIVE),
        value(s_delta, rows[0], "+1.72", "Sector Now Delta", color=SLOWER,
              bindings={"Text": script(LIVE_DELTA_BODY + "\r\nreturn fmtDelta(d, 2);"),
                        "TextColor": color_script(LIVE_DELTA_BODY, 2)},
              skip=SKIP_LIVE),
    ]

    # Os dois setores anteriores: apagados quando sao da volta passada.
    samples = (("S1", "13.795", "+1.41", SLOWER),
               ("S3", "11.181", "-0.64", FASTER))
    for r, row, (num, time_sample, delta_sample, delta_color) in zip(
            (1, 2), rows[1:], samples):
        body = f"var d = sectorDelta(back({r}));"
        tone = ncalc(f"if({previous_lap(r)}, {dim}, '{TEXT}')")
        items += [
            label(s_label.inset(left=4.0), rows[r], num, f"Sector {r} Label",
                  bindings={"Text": ncalc(
                      f"'S' + format({sector_number(r)}, '0')"),
                      "TextColor": ncalc(
                      f"if({previous_lap(r)}, {dim}, '{TEXT_SECONDARY}')")}),
            value(s_time, row, time_sample, f"Sector {r} Time",
                  bindings={"Text": script(f"return fmtSector(back({r}).t);"),
                            "TextColor": tone},
                  skip=SKIP_SLOW),
            value(s_delta, row, delta_sample, f"Sector {r} Delta",
                  color=delta_color,
                  bindings={"Text": script(body + "\r\nreturn fmtDelta(d, 2);"),
                            "TextColor": color_script(body, 2)},
                  skip=SKIP_SLOW),
        ]

    # Voltas.
    items += [
        label(l_label, rows[0], "Last", "Last Label"),
        value(l_time, rows[0], "1:22.821", "Last Lap",
              bindings={"Text": script(
                  f"return fmtLap(sec($prop('{GAME}LastLapTime')));")},
              skip=SKIP_SLOW),
        value(l_delta, rows[0], "+0.722", "Last Delta", color=SLOWER,
              bindings={"Text": script(LAST_DELTA_BODY + "\r\nreturn fmtDelta(d, 3);"),
                        "TextColor": color_script(LAST_DELTA_BODY, 3)},
              skip=SKIP_SLOW),
        label(l_label, rows[1], "Best", "Best Label"),
        value(l_time, rows[1], "1:22.099", "Best Lap",
              bindings={"Text": script(
                  f"return fmtLap(sec($prop('{GAME}BestLapTime')));")},
              skip=SKIP_SLOW),
        label(l_label, rows[2], "Opt", "Opt Label"),
        value(l_time, rows[2], "1:21.910", "Optimal Lap",
              bindings={"Text": script(OPT_BODY)}, skip=SKIP_SLOW),
    ]

    return Layer(
        *items,
        name="Sectors",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )
