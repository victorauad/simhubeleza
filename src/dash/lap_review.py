"""Lap Review: a volta que acabou de fechar, por 5 s, em corrida.

Ocupa o lugar do grafico de telemetria. Duas faixas, por prioridade:

  P1  em cima, maior: minha ultima volta com o delta para a minha melhor,
      a media do stint e as voltas do stint.
  P2  embaixo, tabela: os 3 a frente e os 3 atras na classe -- ultima
      volta, delta dela para a MINHA melhor volta, e a media do stint deles.

Media do stint
--------------

Nenhum plugin entrega pronta, entao ela e acumulada volta a volta. Como
filho de layer escondida nao e avaliado, os campos de media (e o de voltas
do stint) moram fora do layer do estado, sempre visiveis, e se apagam
sozinhos (texto vazio) fora do Lap Review -- sao os "coletores".

  minha     soma as voltas que nao encostaram no pit; zera ao entrar no pit.
  outros    varre o leaderboard da classe a cada 2 s e soma, por nome, cada
            volta nova que nao passe de 107% da melhor do piloto (corta
            volta de entrada/saida de box e volta com incidente). Zera
            quando `LapsSinceLastPit` do piloto volta para tras (se o plugin
            tiver esse campo; sem ele, a media e da corrida inteira).
"""

from simhub.bindings import js
from simhub.model import Layer, RectangleItem
from simhub.theme import (
    FASTER, FONT, MONO_ADVANCE, PLAYER, SIZE_LABEL, SLOWER, TEXT,
    TEXT_SECONDARY, TEXT_TERTIARY, WEIGHT_VALUE, alpha,
)
from . import layout as grid
from . import states
from .widgets import RIGHT, caption, separators, text

GAME = "DataCorePlugin.GameData."
BOARD = "IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_"
PLAYER_POSITION = "IRacingExtraProperties.iRacing_Player_PositionInClass"

INSET_X = 14.0
INSET_TOP, INSET_BOTTOM = 6.0, 6.0
P1_SIZE = 26.0
DELTA_SIZE = 21.0
ROW_SIZE = 16.0
HEADER_HEIGHT = 12.0
BAND_GAP = 5.0
#: Respiro entre os 3 da frente e os 3 de tras -- onde fica o filete ambar
#: que marca o jogador.
SPLIT_GAP = 3.0
COLUMN_GAP = 12.0
P1_MIN_GAP = 16.0
#: Varredura do leaderboard pelos coletores dos outros pilotos (ms).
SCAN_MS = 2000
#: Volta acima disso (fracao da melhor do piloto) nao entra na media.
OUTLIER = 1.07

AHEAD = (-3, -2, -1)
BEHIND = (1, 2, 3)

SAMPLES = {
    -3: ("P2", "Tomoki Nojiri", "1:22.4", "-0.1", "1:22.7"),
    -2: ("P3", "Ritomo Miyata", "1:22.5", "+0.1", "1:22.9"),
    -1: ("P4", "Nirei Fukuzumi", "1:22.9", "+0.5", "1:22.9"),
    1: ("P6", "Sho Tsuboi", "1:22.6", "+0.2", "1:23.0"),
    2: ("P7", "Ren Sato", "1:23.3", "+0.8", "1:23.1"),
    3: ("P8", "Kakunoshin Ohta", "1:23.0", "+0.5", "1:23.3"),
}


def mono(chars, size):
    return chars * size * MONO_ADVANCE


# --- JS ------------------------------------------------------------------

#: Piloto `k` posicoes do jogador na classe (negativo = a frente). Define
#: `pos` e `d(campo)`; `pos` fica 0 quando a posicao nao existe.
def slot(k):
    return (
        f"var P = num($prop('{PLAYER_POSITION}')) || 0;\r\n"
        f"var pos = P + ({k});\r\n"
        "var pad = function (j) { return (j < 10 ? '0' : '') + j; };\r\n"
        f"var d = function (f) {{ return $prop('{BOARD}' + pad(pos - 1) + "
        "'_' + f); };\r\n"
        "if (P < 1 || pos < 1 || !d('Name')) pos = 0;\r\n"
    )


def row_formula(k, body):
    """Conteudo de uma linha da tabela (dentro do layer do estado)."""
    return js(states.BASE + states.FORMAT + slot(k)
              + "if (pos == 0) return '';\r\n" + body)


MY_BEST = f"sec($prop('{GAME}BestLapTime'))"

#: Coletor do proprio jogador: voltas do stint e media das voltas limpas.
MINE = (
    f"var last = sec($prop('{GAME}LastLapTime'));\r\n"
    "var me = root.me;\r\n"
    "if (me == null || lap < me.lap) { me = root.me = { lap: lap, "
    "last: last, pit: onPit, dirty: onPit, laps: 0, sum: 0, n: 0, "
    "pending: null }; }\r\n"
    # Entrou no pit: comeca um stint novo.
    "if (onPit && !me.pit) { me.laps = 0; me.sum = 0; me.n = 0; }\r\n"
    "if (onPit) me.dirty = true;\r\n"
    # Fechou volta: conta no stint e marca se ela entra na media (o tempo
    # pode chegar um pouco depois da troca de volta).
    "var done = lapDone(me);\r\n"
    "if (lap > me.lap) { if (!onPit && done) me.laps += 1; "
    "me.pending = !me.dirty; me.dirty = onPit; }\r\n"
    "if (last != null && last !== me.last) { "
    "if (me.pending) { me.sum += last; me.n += 1; } "
    "me.pending = null; me.last = last; }\r\n"
    "me.lap = lap; me.pit = onPit;\r\n"
)


def collector_mine(body):
    return js(states.left_prelude() + states.FORMAT + MINE
              + "if (state != 'review') return '';\r\n" + body)


#: Coletor dos outros: media do stint por nome de piloto.
OTHERS = (
    "var pad2 = function (j) { return (j < 10 ? '0' : '') + j; };\r\n"
    "var cars = root.cars || (root.cars = {});\r\n"
    f"if (root.t == null || now - root.t > {SCAN_MS}) {{ root.t = now;\r\n"
    "\tfor (var j = 0; j < 64; j++) {\r\n"
    f"\t\tvar pre = '{BOARD}' + pad2(j) + '_';\r\n"
    "\t\tvar nm = $prop(pre + 'Name'); if (!nm) break;\r\n"
    "\t\tvar v = sec($prop(pre + 'LastLapTime'));\r\n"
    "\t\tvar b = sec($prop(pre + 'BestLapTime'));\r\n"
    "\t\tvar lsp = num($prop(pre + 'LapsSinceLastPit'));\r\n"
    "\t\tvar c = cars[nm];\r\n"
    "\t\tif (c == null) { cars[nm] = { last: v, lsp: lsp, sum: 0, n: 0 }; "
    "continue; }\r\n"
    "\t\tif (lsp != null && c.lsp != null && lsp < c.lsp) "
    "{ c.sum = 0; c.n = 0; }\r\n"
    "\t\tc.lsp = lsp;\r\n"
    "\t\tif (v != null && v !== c.last) { "
    f"if (b == null || v <= b * {OUTLIER}) {{ c.sum += v; c.n += 1; }} "
    "c.last = v; }\r\n"
    "\t}\r\n"
    "}\r\n"
)


def collector_other(k):
    return js(states.left_prelude() + states.FORMAT + OTHERS + slot(k)
              + "if (state != 'review' || pos == 0) return '';\r\n"
              "var c = cars[d('Name')];\r\n"
              "return fmtLap(c && c.n ? c.sum / c.n : null);")


# --- Layout --------------------------------------------------------------

def p1_widths():
    lap = mono(8, P1_SIZE)
    delta = mono(6, DELTA_SIZE)
    return (lap + 8.0 + delta,
            max(mono(9, SIZE_LABEL), lap),
            max(mono(10, SIZE_LABEL), mono(2, P1_SIZE)))


def table_columns(inner):
    """POS, nome, LAST, VS BEST, STINT AVG."""
    pos_w = mono(3, ROW_SIZE)
    lap_w = mono(8, ROW_SIZE)
    delta_w = mono(6, ROW_SIZE)
    name_w = inner.width - pos_w - 2 * lap_w - delta_w - 4 * COLUMN_GAP
    out, x = [], inner.x
    for w in (pos_w, name_w, lap_w, delta_w, lap_w):
        out.append(grid.Region(x, inner.y, w, inner.height))
        x += w + COLUMN_GAP
    return out


def regions(region):
    inner = region.inset(top=INSET_TOP, bottom=INSET_BOTTOM,
                         left=INSET_X, right=INSET_X)
    band_h = SIZE_LABEL + 6.0 + P1_SIZE * 1.15
    band, rest = inner.split_top(band_h, gutter=BAND_GAP)
    header, table = rest.split_top(HEADER_HEIGHT)
    row_h = (table.height - SPLIT_GAP) / 6
    assert row_h >= ROW_SIZE * 1.15, f"lap review: linha de {row_h:.1f}"
    return inner, band, header, table, row_h


def row_top(table, row_h, k):
    index = k + 3 if k < 0 else k + 2
    return table.y + row_h * index + (SPLIT_GAP if k > 0 else 0.0)


def layer(region):
    """Devolve (layer do estado, layer dos coletores)."""
    inner, band, header, table, row_h = regions(region)
    widths = p1_widths()
    gap = (band.width - sum(widths)) / 2
    assert gap >= P1_MIN_GAP, f"lap review: P1 nao cabe ({gap:.1f})"
    cells, x = [], band.x
    for w in widths:
        cells.append(grid.Region(x, band.y, w, band.height))
        x += w + gap
    last, avg, laps = cells
    label_h = SIZE_LABEL + 6.0
    value_y = band.y + label_h
    value_h = band.height - label_h
    rules = separators(
        [grid.Region(c.x - gap / 2, band.y, 0, band.height) for c in cells],
        band, name="Review Separator", inset=2.0)

    lap_w = mono(8, P1_SIZE)
    items = [
        *rules,
        caption(last.x, band.y, last.width, "Last", name="Review Last Label"),
        text(last.x, value_y, lap_w + 4.0, value_h, "1:22.8",
             name="Review Last", size=P1_SIZE, weight=WEIGHT_VALUE,
             bindings={"Text": js(states.FORMAT + "return fmtLap(sec("
                                  f"$prop('{GAME}LastLapTime')));")}),
        text(last.x + lap_w + 8.0, value_y, mono(6, DELTA_SIZE) + 4.0,
             value_h, "+0.7", name="Review Last Delta", size=DELTA_SIZE,
             color=SLOWER, weight=WEIGHT_VALUE,
             bindings={
                 "Text": js(states.FORMAT
                            + f"var l = sec($prop('{GAME}LastLapTime'));"
                            f" var b = {MY_BEST};\r\n"
                            "return fmtDelta(l == null || b == null ? null "
                            ": l - b);"),
                 "TextColor": js(states.FORMAT
                                 + f"var l = sec($prop('{GAME}LastLapTime'));"
                                 f" var b = {MY_BEST};\r\n"
                                 + states.color_delta(
                                     "l == null || b == null ? null : l - b",
                                     FASTER, SLOWER, TEXT_TERTIARY)),
             }),
        caption(avg.x, band.y, avg.width, "Stint avg",
                name="Review Avg Label"),
        caption(laps.x, band.y, laps.width, "Stint laps",
                name="Review Laps Label"),
    ]

    pos_c, name_c, last_c, delta_c, avg_c = table_columns(table)
    items += [
        caption(last_c.x, header.y, last_c.width, "Last",
                name="Review Col Last", align=RIGHT, height=HEADER_HEIGHT),
        caption(delta_c.x - 20.0, header.y, delta_c.width + 20.0, "Vs best",
                name="Review Col Delta", align=RIGHT, height=HEADER_HEIGHT),
        caption(avg_c.x, header.y, avg_c.width, "Stint avg",
                name="Review Col Avg", align=RIGHT, height=HEADER_HEIGHT),
        # O jogador fica entre os dois grupos: um filete ambar.
        RectangleItem(
            name="Review Player Mark",
            IsRectangleItem=True,
            BackgroundColor=alpha(PLAYER, 60),
            Left=table.x, Top=row_top(table, row_h, 1) - SPLIT_GAP / 2 - 0.5,
            Width=table.width, Height=1.0,
            Visible=True, BlinkPhasisInverted=False,
            RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
        ),
    ]

    name_chars = int(name_c.width / (ROW_SIZE * 0.5))
    for k in AHEAD + BEHIND:
        top = row_top(table, row_h, k)
        pos_s, name_s, last_s, delta_s, _ = SAMPLES[k]
        delta_expr = ("(function () { var l = sec(d('LastLapTime')); "
                      f"var b = {MY_BEST}; return l == null || b == null "
                      "? null : l - b; })()")
        items += [
            text(pos_c.x, top, pos_c.width, row_h, pos_s,
                 name=f"Review {k:+d} Pos", size=ROW_SIZE,
                 color=TEXT_SECONDARY,
                 bindings={"Text": row_formula(k, "return 'P' + pos;")}),
            text(name_c.x, top, name_c.width, row_h, name_s,
                 name=f"Review {k:+d} Name", size=ROW_SIZE, font=FONT,
                 bindings={"Text": row_formula(
                     k, f"var s = String(d('Name')); return s.length > "
                     f"{name_chars} ? s.substring(0, {name_chars - 1}) + '.' "
                     ": s;")}),
            text(last_c.x, top, last_c.width, row_h, last_s,
                 name=f"Review {k:+d} Last", size=ROW_SIZE, align=RIGHT,
                 bindings={"Text": row_formula(
                     k, "return fmtLap(sec(d('LastLapTime')));")}),
            text(delta_c.x - 8.0, top, delta_c.width + 8.0, row_h, delta_s,
                 name=f"Review {k:+d} Delta", size=ROW_SIZE, align=RIGHT,
                 color=FASTER if delta_s.startswith("-") else SLOWER,
                 bindings={
                     "Text": row_formula(k, f"return fmtDelta({delta_expr});"),
                     "TextColor": row_formula(k, states.color_delta(
                         delta_expr, FASTER, SLOWER, TEXT_TERTIARY)),
                 }),
        ]
    shown = Layer(
        *(states.content(item) for item in items),
        name="Lap Review",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": states.showing("review")},
    )

    live = [
        text(avg.x, value_y, avg.width + gap / 2, value_h, "1:22.9",
             name="Review Stint Avg", size=P1_SIZE, weight=WEIGHT_VALUE,
             color=TEXT, bindings={"Text": collector_mine(
                 "return fmtLap(me.n ? me.sum / me.n : null);")}),
        text(laps.x, value_y, laps.width, value_h, "14",
             name="Review Stint Laps", size=P1_SIZE, weight=WEIGHT_VALUE,
             bindings={"Text": collector_mine(
                 "return me.laps ? String(me.laps) : 'N/A';")}),
    ]
    for k in AHEAD + BEHIND:
        top = row_top(table, row_h, k)
        live.append(text(avg_c.x, top, avg_c.width, row_h, SAMPLES[k][4],
                         name=f"Review {k:+d} Avg", size=ROW_SIZE,
                         color=TEXT_SECONDARY, align=RIGHT,
                         bindings={"Text": collector_other(k)}))
    collectors = Layer(
        *(states.gate(item) for item in live),
        name="Lap Review Live",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )
    return states.gate(shown), collectors
