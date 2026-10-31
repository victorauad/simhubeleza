"""Box de telemetria: o meu pedal contra o da volta de referencia.

    [ VOCE ----  REF - -                               REF. LAP ]
    [ meu traco + referencia      |      referencia a frente    ]
    [ -3 s                        0                       +3 s  ]

A linha do meio e o agora. A metade esquerda mostra os ultimos segundos: o
meu acelerador/freio e, por cima, o da referencia no mesmo ponto da pista.
A metade direita mostra so a referencia, nos proximos segundos.

Tudo e `ChartItem` do SimHub, que desenha o historico de um valor com o
ponto mais novo na borda direita. A metade direita usa isso a favor: o
grafico recebe a referencia no ponto onde eu vou estar daqui a `WINDOW_S`
(posicao atual + velocidade x janela). O ponto mais novo, na borda direita,
e a referencia daqui a `WINDOW_S`; o mais velho, na linha do meio, foi
calculado `WINDOW_S` atras para o ponto onde estou agora. Com velocidade
constante na janela, a metade direita e a referencia a frente.

A referencia e a minha melhor volta da sessao -- a mesma do BestLapTime do
SimHub, entao volta invalida nao conta --, gravada pelo proprio dash: uma
formula so (`RECORDER`, o `Visible` da linha do agora, a cada quadro) guarda
acelerador e freio por trecho da pista (`BINS` trechos do LapDistPct), troca
a referencia quando a volta que acabou de fechar vira a melhor, e publica os
valores do quadro no armazenamento compartilhado, interpolados entre
trechos. Os graficos so leem o publicado. So da para usar volta gravada
inteira: a melhor volta feita antes de o dash abrir nao tem os pedais, e a
referencia aparece na primeira melhor volta depois disso. Sem referencia, a
camada dela fica escondida e o rotulo mostra "REF. LAP --".
"""

from simhub.bindings import js, ncalc
from simhub.model import ChartItem
from simhub.theme import (
    BRAKE, FONT, REF_BRAKE, REF_THROTTLE, TEXT_SECONDARY, THROTTLE,
    TRACE_BOX_EDGE, TRACE_BOX_FILL, TRACE_GRID, TRACE_NOW,
)
from .. import states
from ..widgets import CENTER, LEFT, RIGHT, text
from .base import SKIP_SLOW, TRACE_BOX, Region, group, rect

#: Segundos de cada metade do box.
WINDOW_S = 3.0
#: Amostras por segundo de um ChartItem com RenderingSkip 1 (~30 Hz, medido
#: no widget de telemetria do dash principal). A conta da metade direita
#: depende disso: se o SimHub amostrar em outro ritmo, ajustar aqui.
SAMPLES_PER_S = 30
POINTS = int(WINDOW_S * SAMPLES_PER_S)

#: Trechos da pista na gravacao da referencia (~13 m numa pista de 5 km).
BINS = 400
#: Fracao minima dos trechos gravados para uma volta valer como referencia.
COVERAGE = 0.97

# --- Medidas (relativas ao box) -----------------------------------------------

BOX = TRACE_BOX
PLOT_X, PLOT_RIGHT = BOX.x + 16.0, BOX.x + 642.0
NOW_X = BOX.x + 329.0
PLOT_TOP, PLOT_H = BOX.y + 30.0, 176.0
LEFT_PLOT = Region(PLOT_X, PLOT_TOP, NOW_X - PLOT_X, PLOT_H)
RIGHT_PLOT = Region(NOW_X, PLOT_TOP, PLOT_RIGHT - NOW_X, PLOT_H)
GRID_YS = (PLOT_TOP, PLOT_TOP + PLOT_H / 2, PLOT_TOP + PLOT_H)
NOW_LINE = Region(NOW_X - 0.5, BOX.y + 22.0, 1.0, 190.0)
DOT = 7.0
LEGEND_Y, AXIS_Y = BOX.y + 9.0, BOX.y + 216.0
SIZE_SMALL = 10.0

KEY = "mini_"


def shared(name):
    return f"'{KEY}{name}'"


RECORDER = js(
    f"var S = '{states.SHARED}', N = {BINS};\r\n"
    "var r = root;\r\n"
    "var sec = function (v) { var x = Number(timespantoseconds(v)); "
    "return x > 0 ? x : 0; };\r\n"
    "var lap = Number($prop('DataCorePlugin.GameData.CurrentLap')) || 0;\r\n"
    "var pct = Number($prop('GameRawData.Telemetry.LapDistPct'));\r\n"
    "var now = Number($prop('GameRawData.Telemetry.SessionTime'));\r\n"
    "var best = sec($prop('DataCorePlugin.GameData.BestLapTime'));\r\n"
    "var last = sec($prop('DataCorePlugin.GameData.LastLapTime'));\r\n"
    "var fresh = function () { return { t: [], b: [], n: 0 }; };\r\n"
    # Sessao nova (a volta voltou para tras): comeca do zero.
    "if (r.cur == null || lap < r.lap) { r.cur = fresh(); r.ref = null; "
    "r.refT = 0; r.pend = null; r.lap = lap; r.bin = -1; r.ok = false; "
    "r.t0 = null; r.len = null; r.seen = last; }\r\n"
    # A sessao zerou a melhor volta: a referencia antiga nao vale mais.
    "if (best <= 0) { r.ref = null; r.refT = 0; }\r\n"
    "if (!(pct >= 0 && pct <= 1)) return true;\r\n"
    # Virou a volta: a que acabou fica pendente ate o iRacing publicar o
    # tempo dela. A primeira volta depois de carregar o dash nunca vale (nao
    # foi gravada inteira).
    "if (lap == r.lap + 1) {\r\n"
    f"\tr.pend = r.ok && r.t0 != null && r.cur.n >= N * {COVERAGE} "
    "? { c: r.cur, t: now - r.t0, last0: r.seen, until: now + 10 } : null;\r\n"
    "\tr.cur = fresh(); r.ok = true; r.t0 = now;\r\n"
    "} else if (lap != r.lap) { r.cur = fresh(); r.ok = false; r.t0 = null; "
    "r.pend = null; }\r\n"
    "r.lap = lap;\r\n"
    # O LastLapTime ja e o da volta pendente quando mudou desde a virada (ou
    # ja bate com o tempo medido). Ela vira referencia se for a melhor da
    # sessao: o mesmo criterio do jogo, que nao conta volta invalida.
    "var p = r.pend;\r\n"
    "if (p) {\r\n"
    "\tif (last > 0 && (last != p.last0 || Math.abs(last - p.t) < 0.05)) {\r\n"
    "\t\tif (best > 0 && Math.abs(last - best) < 0.002) { r.ref = p.c; r.refT = best; }\r\n"
    "\t\tr.pend = null;\r\n"
    "\t} else if (now > p.until) r.pend = null;\r\n"
    "}\r\n"
    "r.seen = last;\r\n"
    "var bin = Math.min(N - 1, Math.floor(pct * N));\r\n"
    "var thr = Number($prop('DataCorePlugin.GameData.Throttle')) || 0;\r\n"
    "var brk = Number($prop('DataCorePlugin.GameData.Brake')) || 0;\r\n"
    # A linha de chegada pode virar o LapDistPct um quadro antes ou depois
    # da volta: o salto de ~1 para ~0 nao invalida nada. Salto de verdade
    # (reset, reboque) deixa a volta incompleta.
    "var wrap = r.bin > N * 0.9 && bin < N * 0.1;\r\n"
    "var from = bin;\r\n"
    "if (r.bin >= 0 && !wrap) {\r\n"
    "\tif (bin > r.bin + 20 || bin < r.bin - 5) r.ok = false;\r\n"
    "\telse if (bin > r.bin) from = r.bin + 1;\r\n"
    "}\r\n"
    "var c = r.cur;\r\n"
    "for (var i = from; i <= bin; i++) { if (c.t[i] == null) c.n++; "
    "c.t[i] = thr; c.b[i] = brk; }\r\n"
    "r.bin = bin;\r\n"
    f"if (!{states.HAS_SHARED}) return true;\r\n"
    "var ref = r.ref;\r\n"
    f"setsharedvalue(S, {shared('ok')}, ref ? 1 : 0);\r\n"
    f"setsharedvalue(S, {shared('best')}, ref ? r.refT : 0);\r\n"
    "if (ref) {\r\n"
    # Valor no ponto `q` (0..1) interpolado entre os centros dos trechos:
    # sem isso o grafico vira escada, e a leitura a frente treme a cada
    # trecho que o arredondamento pula.
    "\tvar at = function (arr, q) { var x = q * N - 0.5, i = Math.floor(x), f = x - i; "
    "var a = arr[(i + N) % N], b = arr[(i + 1) % N]; "
    "if (a == null) a = b; if (b == null) b = a; "
    "return a == null ? 0 : a + (b - a) * f; };\r\n"
    "\tif (r.len == null) r.len = (parseFloat("
    "$prop('GameRawData.SessionData.WeekendInfo.TrackLength')) || 0) * 1000;\r\n"
    "\tvar v = (Number($prop('DataCorePlugin.GameData.SpeedKmh')) || 0) / 3.6;\r\n"
    f"\tvar qa = (pct + (r.len > 0 ? v * {WINDOW_S} / r.len : 0)) % 1;\r\n"
    f"\tsetsharedvalue(S, {shared('thr')}, at(ref.t, pct));\r\n"
    f"\tsetsharedvalue(S, {shared('brk')}, at(ref.b, pct));\r\n"
    f"\tsetsharedvalue(S, {shared('thr_ahead')}, at(ref.t, qa));\r\n"
    f"\tsetsharedvalue(S, {shared('brk_ahead')}, at(ref.b, qa));\r\n"
    "}\r\n"
    "return true;"
)

REF_READY = js(f"return {states.HAS_SHARED} && "
               f"getsharedvalueordefault('{states.SHARED}', {shared('ok')}, 0) == 1;")


def ref_value(name):
    return js("return Number(getsharedvalueordefault("
              f"'{states.SHARED}', {shared(name)}, 0)) || 0;")


def chart(name, region, color, binding):
    return ChartItem(
        name=name,
        ChartSuspended=False, ChartEnabled=True,
        CurrentValue=0.0, Minimum=0.0, Maximum=100.0,
        UseMinimum=True, UseMaximum=True,
        LineColor=color, LineTickness=2, PointsCount=float(POINTS),
        BackgroundColor="#00FFFFFF",
        Left=region.x, Top=region.y, Width=region.width, Height=region.height,
        Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=1, MinimumRefreshIntervalMS=10.0,
        bindings={"CurrentValue": binding},
    )


def dot(name, prop, color):
    """O valor de agora, na linha do meio."""
    item = rect(name, Region(NOW_X - DOT / 2, PLOT_TOP + PLOT_H - DOT / 2,
                             DOT, DOT), color, radius=DOT / 2)
    item["Bindings"] = {"Top": ncalc(
        f"{PLOT_TOP + PLOT_H - DOT / 2:g} - [{prop}] * {PLOT_H / 100:g}")}
    return item


def label(x, width, content, align, *, y=LEGEND_Y, font=FONT):
    return text(x, y, width, 12.0, content, name=content.strip(),
                size=SIZE_SMALL, color=TEXT_SECONDARY, align=align, font=font)


def ref_label():
    """Qual volta e a referencia: o tempo dela, ou "--" enquanto nao ha."""
    item = label(PLOT_RIGHT - 140.0, 140.0, "REF. LAP 1:36.1", RIGHT)
    item["Bindings"] = {"Text": js(
        states.FMT_TIME
        + f"var s = {states.HAS_SHARED} ? Number(getsharedvalueordefault("
        f"'{states.SHARED}', {shared('best')}, 0)) : 0;\r\n"
        "return 'REF. LAP ' + (s > 0 ? fmtTime(s) : '--');",
        format_string="")}
    item["RenderingSkip"] = SKIP_SLOW
    return item


def legend():
    swatch_y = LEGEND_Y + 5.0
    dashes = [rect(f"Ref Swatch {i}", Region(PLOT_X + 60.0 + 5.0 * i, swatch_y,
                                             4.0, 2.0), TEXT_SECONDARY)
              for i in range(3)]
    return [
        rect("Me Swatch", Region(PLOT_X, swatch_y, 14.0, 2.0), TEXT_SECONDARY),
        label(PLOT_X + 20.0, 40.0, "VOCÊ", LEFT),
        *dashes,
        label(PLOT_X + 80.0, 30.0, "REF", LEFT),
        ref_label(),
    ]


def axis():
    mono = "Arame Mono"
    return [
        label(PLOT_X, 60.0, "-3 s", LEFT, y=AXIS_Y, font=mono),
        label(NOW_X - 30.0, 60.0, "0", CENTER, y=AXIS_Y, font=mono),
        label(PLOT_RIGHT - 60.0, 60.0, "+3 s", RIGHT, y=AXIS_Y, font=mono),
    ]


def layer():
    box = rect("Trace Box", BOX, TRACE_BOX_FILL, radius=(0, 0, 14, 14),
               border=TRACE_BOX_EDGE, thickness=1)
    box["BorderStyle"]["BorderTop"] = 0
    grid_lines = [rect(f"Grid {i}", Region(PLOT_X, y, PLOT_RIGHT - PLOT_X, 1.0),
                       TRACE_GRID) for i, y in enumerate(GRID_YS)]
    now = rect("Now", NOW_LINE, TRACE_NOW, bindings={"Visible": RECORDER})
    # A cada quadro: os graficos amostram a ~30 Hz e precisam sempre do
    # valor do quadro, nao de um publicado no quadro anterior.
    now["RenderingSkip"] = 0

    return group(
        "Telemetry",
        box, *grid_lines,
        group(
            "Reference",
            chart("Ref Throttle", LEFT_PLOT, REF_THROTTLE, ref_value("thr")),
            chart("Ref Brake", LEFT_PLOT, REF_BRAKE, ref_value("brk")),
            chart("Ref Throttle Ahead", RIGHT_PLOT, REF_THROTTLE,
                  ref_value("thr_ahead")),
            chart("Ref Brake Ahead", RIGHT_PLOT, REF_BRAKE,
                  ref_value("brk_ahead")),
            bindings={"Visible": REF_READY},
        ),
        chart("Throttle", LEFT_PLOT, THROTTLE, ncalc("[Throttle]")),
        chart("Brake", LEFT_PLOT, BRAKE, ncalc("[Brake]")),
        now,
        dot("Throttle Now", "Throttle", THROTTLE),
        dot("Brake Now", "Brake", BRAKE),
        *legend(), *axis(),
    )
