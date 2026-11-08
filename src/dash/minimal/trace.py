"""Box de telemetria: o meu pedal contra o da volta de referencia.

    [ YOU ---  REF ===                                   REF LAP ]
    [ meu traco (fino) sobre a referencia no mesmo ponto (faixa)  ]
    [ -15 s                                                   0  ]

Uma janela so: os ultimos `WINDOW_S` segundos, com o agora na borda
direita. O meu acelerador/freio em linha fina e cheia e, por baixo, o da
referencia no mesmo ponto da pista, numa faixa larga e translucida
(`REF_THICKNESS`, `REF_THROTTLE`/`REF_BRAKE`). Quando eu acompanho a
referencia, a minha linha corre dentro da faixa, e as duas continuam
legiveis -- com a referencia na mesma espessura (antes, tracejada), ela
sumia justamente nesse caso.

Tudo e `ChartItem` do SimHub, que desenha o historico de um valor com o
ponto mais novo na borda direita. Pedal solto desenharia uma linha
permanente na base (o freio, vermelho, a volta inteira): o fundo do box e
cortado na altura da base, e a tira de baixo (`Fill Base`) fica por cima
dos graficos, com a mesma cor e opacidade, entao o fundo continua
uniforme e so o que sai do zero aparece. A linha de 0% da grade vem por
cima dela, neutra.

A referencia e a minha melhor volta da sessao -- a mesma do BestLapTime do
SimHub, entao volta invalida nao conta --, gravada pelo proprio dash: uma
formula so (`RECORDER`, o `Visible` da linha do agora, a cada quadro) guarda
acelerador e freio por trecho da pista (`BINS` trechos
do LapDistPct), troca a referencia quando a volta que acabou de fechar vira
a melhor, e publica os valores do quadro no armazenamento compartilhado,
interpolados entre trechos. Os graficos so leem o publicado.

A volta que fecha fica pendente ate a proxima virada: o BestLapTime pode
mudar segundos depois do LastLapTime, e julgar a volta uma vez so, no
quadro em que o LastLapTime muda, jogava fora toda volta (a referencia
nunca aparecia). Com o IRacingExtraProperties, volta limpa vale pelo proprio
tempo, sem esperar o BestLapTime. Reset para os boxes nao apaga a
referencia; sessao nova (`SessionNum`) apaga.

So da para usar volta gravada inteira: a melhor volta feita antes de o dash
abrir nao tem os pedais, e a referencia aparece na primeira volta limpa (ou
melhor volta) depois disso. Sem referencia, a
camada dela fica escondida e o rotulo mostra "REF LAP --".
"""

from simhub.bindings import js, ncalc
from simhub.model import ChartItem
from simhub.theme import (
    BRAKE, FONT, MINI_SECTOR_EQUAL, MINI_SECTOR_GAIN, MINI_SECTOR_LOSS,
    MINI_SECTOR_NONE, MINI_TRACK, REF_BRAKE, REF_SWATCH, REF_THROTTLE, TEXT,
    TEXT_SECONDARY, THROTTLE, TRACE_BOX_EDGE, TRACE_BOX_FILL, TRACE_GRID,
    TRACE_NOW, rounded,
)
from .. import states
from ..top_bar import DELTA_PROP, DELTA_TEXT, delta_gauge, marker
from ..widgets import LEFT, RIGHT, text
from .base import SKIP_SLOW, TRACE_BOX, Region, group, rect

#: Segundos de historico no box.
WINDOW_S = 15.0
#: Amostras por segundo de um ChartItem com RenderingSkip 1 (~30 Hz, medido
#: no widget de telemetria do dash principal): define quantos pontos cabem
#: em `WINDOW_S`.
SAMPLES_PER_S = 30
POINTS = int(WINDOW_S * SAMPLES_PER_S)

#: Trechos da pista na gravacao da referencia (~13 m numa pista de 5 km).
BINS = 400
#: Fracao minima dos trechos gravados para uma volta valer como referencia.
COVERAGE = 0.97
#: Segundos depois da virada em que a validade lida ainda e da volta velha.
CLEAN_GRACE_S = 1.0

# --- Medidas (relativas ao box) -----------------------------------------------

BOX = TRACE_BOX
PLOT_X, PLOT_RIGHT = BOX.x + 16.0, BOX.x + 642.0
NOW_X = PLOT_RIGHT
PLOT_TOP, PLOT_H = BOX.y + 30.0, 120.0
PLOT = Region(PLOT_X, PLOT_TOP, PLOT_RIGHT - PLOT_X, PLOT_H)
GRID_YS = (PLOT_TOP, PLOT_TOP + PLOT_H / 2, PLOT_TOP + PLOT_H)
NOW_LINE = Region(NOW_X - 0.5, BOX.y + 22.0, 1.0, 190.0)
DOT = 7.0
LEGEND_Y, AXIS_Y = BOX.y + 9.0, BOX.y + 216.0
#: Tira do delta, abaixo dos pedais e no mesmo eixo de tempo: um rotulo e a
#: linha entre -`TRACE_DELTA_S` e +`TRACE_DELTA_S`, com o zero no meio.
DELTA_LABEL_Y = BOX.y + 158.0
STRIP_TOP, STRIP_H = BOX.y + 172.0, 34.0
STRIP = Region(PLOT_X, STRIP_TOP, PLOT_RIGHT - PLOT_X, STRIP_H)
STRIP_YS = (STRIP_TOP, STRIP_TOP + STRIP_H / 2, STRIP_TOP + STRIP_H)
TRACE_DELTA_S = 1.0
#: Rotulos do box no tamanho dos rotulos da capsula (km/h, LAPS...).
SIZE_SMALL = 11.0

#: Espessura das linhas: a minha fina, a referencia uma faixa larga.
LINE_THICKNESS, REF_THICKNESS = 2, 5
#: Onde a tira da base comeca: cobre a faixa da referencia em 0% (meia
#: espessura acima da base, com folga). Valor abaixo de ~2% fica escondido.
BASE_TOP = PLOT_TOP + PLOT_H - (REF_THICKNESS / 2 + 0.5)
#: Abaixo disso o ponto do agora ficaria na tira: some.
DOT_MIN = 2

#: Delta da volta atual contra a referencia, no cabecalho: numero com sinal
#: e uma barra que sai do zero no centro -- para a esquerda ganhando tempo,
#: para a direita perdendo --, na escala de `DELTA_FULL_S`. Verde e vermelho
#: sao dos pedais, entao a barra nao leva matiz: o lado e o sinal ja dizem
#: ganho ou perda (troque `DELTA_GAIN`/`DELTA_LOSS` para colorir).
DELTA_FULL_S = 0.5
DELTA_GAIN = DELTA_LOSS = TEXT
DELTA_CENTER_X = (PLOT_X + PLOT_RIGHT) / 2
DELTA_BAR_HALF, DELTA_BAR_H = 100.0, 4.0
#: Na linha da legenda (centro em `BOX.y + 15.5`): a barra no meio e o
#: numero logo a esquerda dela, alinhado a direita.
DELTA_BAR_Y = BOX.y + 15.5 - DELTA_BAR_H / 2
DELTA_VALUE = Region(DELTA_CENTER_X - DELTA_BAR_HALF - 70.0, BOX.y + 6.0,
                     62.0, 19.0)
SIZE_DELTA = 16.0

#: Mini-setores: a volta dividida em `SECTORS` trechos iguais do LapDistPct.
#: O gravador guarda o tempo em cada fronteira e, ao fechar um setor,
#: publica o delta dele contra a referencia (`mini_sd0` ... `mini_sd9`, em
#: segundos; `SECTOR_NONE_VALUE` = sem dado).
SECTORS = 10
SECTOR_NONE_VALUE = 99
#: Diferenca (s) abaixo da qual o setor conta como igual a referencia.
SECTOR_EQUAL_S = 0.02

KEY = "mini_"


def shared(name):
    return f"'{KEY}{name}'"


RECORDER = js(
    f"var S = '{states.SHARED}', N = {BINS}, NS = {SECTORS}, "
    f"NONE = {SECTOR_NONE_VALUE};\r\n"
    "var r = root;\r\n"
    "var sec = function (v) { var x = Number(timespantoseconds(v)); "
    "return x > 0 ? x : 0; };\r\n"
    "var lap = Number($prop('GameRawData.Telemetry.Lap')) || 0;\r\n"
    "var sess = $prop('GameRawData.Telemetry.SessionNum');\r\n"
    "var pct = Number($prop('GameRawData.Telemetry.LapDistPct'));\r\n"
    "var now = Number($prop('GameRawData.Telemetry.SessionTime'));\r\n"
    "var best = sec($prop('DataCorePlugin.GameData.BestLapTime'));\r\n"
    "var last = sec($prop('DataCorePlugin.GameData.LastLapTime'));\r\n"
    f"var cl = $prop('{states.LAP_CLEAN}');\r\n"
    "var fresh = function () { return { t: [], b: [], n: 0, "
    "seen: false, dirty: false, s: [], tot: null }; };\r\n"
    # Delta dos mini-setores publicado: tudo "sem dado" ate haver setor fechado.
    "var clr = function () { r.sd = []; for (var i = 0; i < NS; i++) "
    "r.sd.push(NONE); r.sdDirty = true; };\r\n"
    # Tempo de um setor (k) de uma volta: das fronteiras guardadas; o ultimo
    # fecha no tempo total da volta.
    "var secT = function (c, k) { var a = k == 0 ? 0 : c.s[k], "
    "b = k == NS - 1 ? c.tot : c.s[k + 1]; "
    "return a == null || b == null ? null : b - a; };\r\n"
    # Setor k fechado: o delta dele contra a referencia. O setor 0 comeca uma
    # volta nova, entao apaga o resultado da volta anterior.
    "var sdone = function (c, k) { if (k == 0) clr(); var x = r.ref; "
    "if (!x || x === c) return; var u = secT(c, k), v = secT(x, k); "
    "if (u == null || v == null) return; r.sd[k] = u - v; r.sdDirty = true; };\r\n"
    # Sessao nova (ou dash recem-carregado): comeca do zero.
    "if (r.cur == null || sess != r.sess) { r.cur = fresh(); r.ref = null; "
    "r.refT = 0; r.pend = null; r.lap = lap; r.bin = -1; r.ok = false; "
    "r.t0 = null; r.seen = last; r.sess = sess; r.best = best; "
    "r.pp = null; r.pn = null; clr(); }\r\n"
    # A volta voltou para tras (reset, garagem): perde so a volta em curso;
    # a referencia continua sendo a melhor da sessao.
    "if (lap < r.lap) { r.cur = fresh(); r.ok = false; r.t0 = null; "
    "r.pend = null; r.lap = lap; r.bin = -1; clr(); }\r\n"
    # A sessao zerou a melhor volta: a referencia antiga nao vale mais.
    "if (best <= 0 && r.best > 0) { r.ref = null; r.refT = 0; clr(); }\r\n"
    "r.best = best;\r\n"
    "if (!(pct >= 0 && pct <= 1)) return true;\r\n"
    # Virou a volta: a que acabou fica pendente ate o SimHub mostrar que ela
    # e a melhor. A primeira volta depois de carregar o dash nunca vale (nao
    # foi gravada inteira).
    "if (lap == r.lap + 1) {\r\n"
    "\tif (r.ok && r.t0 != null) { r.cur.tot = now - r.t0; sdone(r.cur, NS - 1); }\r\n"
    f"\tr.pend = r.ok && r.t0 != null && r.cur.n >= N * {COVERAGE} "
    "? { c: r.cur, t: now - r.t0, last0: r.seen, off: 0, "
    "clean: r.cur.seen ? !r.cur.dirty : null } : null;\r\n"
    "\tr.cur = fresh(); r.ok = true; r.t0 = now;\r\n"
    "} else if (lap != r.lap) { r.cur = fresh(); r.ok = false; r.t0 = null; "
    "r.pend = null; clr(); }\r\n"
    "r.lap = lap;\r\n"
    # Volta limpa (IRacingExtraProperties): suja no primeiro falso. Logo
    # depois da virada a propriedade ainda traz a volta que acabou.
    f"if (cl != null && cl !== '' && r.t0 != null && now - r.t0 > {CLEAN_GRACE_S:g}) "
    "{ r.cur.seen = true; if (!(cl === true || cl === 1 || "
    "String(cl).toUpperCase() === 'TRUE')) r.cur.dirty = true; }\r\n"
    # Referencia pronta para leitura: trecho sem gravacao copia o vizinho.
    "var dense = function (c) { for (var i = 0; i < N; i++) { "
    "var j = i; while (c.t[j] == null && j > 0) j--; "
    "if (c.t[j] == null) { j = i; while (c.t[j] == null && j < N - 1) j++; } "
    "if (j != i) { c.t[i] = c.t[j]; c.b[i] = c.b[j]; } } return c; };\r\n"
    # A volta pendente vira referencia se for a melhor da sessao. O tempo
    # oficial dela e o LastLapTime quando ele muda desde a virada (ou ja bate
    # com o tempo medido). O BestLapTime pode chegar depois do LastLapTime:
    # a volta espera por ele ate a proxima virada, em vez de ser julgada uma
    # vez so. Volta invalida nao vira best (o mesmo criterio do jogo). Sem o
    # tempo oficial, vale o medido (com folga de quadro). Volta limpa pelo
    # IRacingExtraProperties vale pelo proprio tempo oficial, sem esperar o
    # BestLapTime.
    "var p = r.pend;\r\n"
    "if (p) {\r\n"
    "\tif (!p.off && last > 0 && (last != p.last0 || Math.abs(last - p.t) < 0.05)) "
    "p.off = last;\r\n"
    "\tvar better = function (x) { return !r.ref || x < r.refT - 0.0005; };\r\n"
    "\tvar hit = best > 0 && (p.off ? Math.abs(best - p.off) < 0.002 "
    ": Math.abs(best - p.t) < 0.05);\r\n"
    "\tif (hit && better(best)) { r.ref = dense(p.c); r.refT = best; r.pend = null; }\r\n"
    "\telse if (p.off && p.clean === true) { if (better(p.off)) "
    "{ r.ref = dense(p.c); r.refT = p.off; } r.pend = null; }\r\n"
    "}\r\n"
    "r.seen = last;\r\n"
    "var bin = Math.min(N - 1, Math.floor(pct * N));\r\n"
    "var thr = Number($prop('DataCorePlugin.GameData.Throttle')) || 0;\r\n"
    "var brk = Number($prop('DataCorePlugin.GameData.Brake')) || 0;\r\n"
    # A linha de chegada pode virar o LapDistPct um quadro antes ou depois
    # da volta: o salto de ~1 para ~0 nao invalida nada. Salto de verdade
    # (reset, reboque) deixa a volta incompleta.
    # Quadro da virada do LapDistPct ainda na volta velha: nao grava (o
    # trecho 0 da volta que acabou guardaria o fim dela).
    "var wrap = r.bin > N * 0.9 && bin < N * 0.1;\r\n"
    "var from = bin;\r\n"
    "if (r.bin >= 0 && !wrap) {\r\n"
    "\tif (bin > r.bin + 20 || bin < r.bin - 5) { r.ok = false; clr(); }\r\n"
    "\telse if (bin > r.bin) from = r.bin + 1;\r\n"
    "}\r\n"
    "var c = r.cur;\r\n"
    "if (!wrap) for (var i = from; i <= bin; i++) { if (c.t[i] == null) c.n++; "
    "c.t[i] = thr; c.b[i] = brk; }\r\n"
    "r.bin = bin;\r\n"
    # Fronteiras dos mini-setores: o tempo de cruzar cada uma, interpolado
    # entre os dois quadros, desde o inicio da volta; fechar um setor publica
    # o delta dele. Salto de posicao (mais de 20% da volta num quadro) nao conta.
    "var pp = r.pp, pn = r.pn;\r\n"
    "r.pp = pct; r.pn = now;\r\n"
    "if (r.ok && r.t0 != null && !wrap && pp != null && pct > pp && pct - pp < 0.2) "
    "for (var k = 1; k < NS; k++) { var bd = k / NS; if (pp < bd && bd <= pct) { "
    "c.s[k] = pn + (now - pn) * (bd - pp) / (pct - pp) - r.t0; sdone(c, k - 1); } }\r\n"
    f"if (!{states.HAS_SHARED}) return true;\r\n"
    "if (r.sdDirty) { for (var j = 0; j < NS; j++) "
    f"setsharedvalue(S, '{KEY}sd' + j, r.sd[j]); r.sdDirty = false; }}\r\n"
    "var ref = r.ref;\r\n"
    f"setsharedvalue(S, {shared('ok')}, ref ? 1 : 0);\r\n"
    f"setsharedvalue(S, {shared('best')}, ref ? r.refT : 0);\r\n"
    "if (ref) {\r\n"
    # Valor no ponto `q` (0..1) interpolado entre os centros dos trechos:
    # sem isso o grafico vira escada.
    "\tvar at = function (arr, q) { var x = q * N - 0.5, i = Math.floor(x), f = x - i; "
    "var a = arr[(i + N) % N], b = arr[(i + 1) % N]; "
    "if (a == null) a = b; if (b == null) b = a; "
    "return a == null ? 0 : a + (b - a) * f; };\r\n"
    f"\tsetsharedvalue(S, {shared('thr')}, at(ref.t, pct));\r\n"
    f"\tsetsharedvalue(S, {shared('brk')}, at(ref.b, pct));\r\n"
    "}\r\n"
    "return true;"
)

REF_READY = js(f"return {states.HAS_SHARED} && "
               f"getsharedvalueordefault('{states.SHARED}', {shared('ok')}, 0) == 1;")


def ref_value(name):
    return js("return Number(getsharedvalueordefault("
              f"'{states.SHARED}', {shared(name)}, 0)) || 0;")


def chart(name, region, color, binding, thickness=LINE_THICKNESS,
          low=0.0, high=100.0):
    return ChartItem(
        name=name,
        ChartSuspended=False, ChartEnabled=True,
        CurrentValue=0.0, Minimum=low, Maximum=high,
        UseMinimum=True, UseMaximum=True,
        LineColor=color, LineTickness=thickness, PointsCount=float(POINTS),
        BackgroundColor="#00FFFFFF",
        Left=region.x, Top=region.y, Width=region.width, Height=region.height,
        Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=1, MinimumRefreshIntervalMS=10.0,
        bindings={"CurrentValue": binding},
    )


def dot(name, prop, color):
    """O valor de agora, na linha do agora (borda direita)."""
    item = rect(name, Region(NOW_X - DOT / 2, PLOT_TOP + PLOT_H - DOT / 2,
                             DOT, DOT), color, radius=DOT / 2)
    item["Bindings"] = {
        "Top": ncalc(
            f"{PLOT_TOP + PLOT_H - DOT / 2:g} - [{prop}] * {PLOT_H / 100:g}"),
        "Visible": ncalc(f"if([{prop}] >= {DOT_MIN}, 1, 0)"),
    }
    return item


def label(x, width, content, align, *, y=LEGEND_Y, font=FONT):
    # 14 px de altura (como os rotulos da capsula), 1 px acima para o centro
    # do texto continuar na altura das amostras da legenda.
    return text(x, y - 1.0, width, 14.0, content, name=content.strip(),
                size=SIZE_SMALL, color=TEXT_SECONDARY, align=align, font=font)


def ref_label():
    """Qual volta e a referencia: o tempo dela, ou "--" enquanto nao ha."""
    item = label(PLOT_RIGHT - 140.0, 140.0, "REF LAP 1:36.1", RIGHT)
    item["Bindings"] = {"Text": js(
        states.FMT_TIME
        + f"var s = {states.HAS_SHARED} ? Number(getsharedvalueordefault("
        f"'{states.SHARED}', {shared('best')}, 0)) : 0;\r\n"
        "return 'REF LAP ' + (s > 0 ? fmtTime(s) : '--');",
        format_string="")}
    item["RenderingSkip"] = SKIP_SLOW
    return item


def legend():
    swatch_y = LEGEND_Y + 5.0
    band = REF_THICKNESS
    return [
        rect("Me Swatch", Region(PLOT_X, swatch_y, 14.0, 2.0), TEXT_SECONDARY),
        label(PLOT_X + 20.0, 40.0, "YOU", LEFT),
        rect("Ref Swatch", Region(PLOT_X + 60.0, swatch_y + 1.0 - band / 2,
                                  14.0, band), REF_SWATCH, radius=1),
        label(PLOT_X + 80.0, 30.0, "REF", LEFT),
        ref_label(),
    ]


def delta_readout():
    """O delta contra a referencia (a melhor volta da sessao: o mesmo
    `DeltaToSessionBest` do dash principal, entao sem gravar nada). So existe
    com referencia, como o resto do box."""
    track = Region(DELTA_CENTER_X - DELTA_BAR_HALF, DELTA_BAR_Y,
                   2 * DELTA_BAR_HALF, DELTA_BAR_H)
    left = Region(track.x, track.y, DELTA_BAR_HALF, DELTA_BAR_H)
    right = Region(DELTA_CENTER_X, track.y, DELTA_BAR_HALF, DELTA_BAR_H)
    zero = Region(DELTA_CENTER_X - 0.5, DELTA_BAR_Y - 2.0, 1.0,
                  DELTA_BAR_H + 4.0)
    value = text(*(getattr(DELTA_VALUE, a) for a in
                   ("x", "y", "width", "height")), "-0.23", name="Delta Value",
                 size=SIZE_DELTA, color=TEXT, align=RIGHT,
                 bindings={"Text": ncalc(DELTA_TEXT)})
    return group(
        "Delta",
        value,
        rect("Delta Track", track, MINI_TRACK, radius=2),
        # Mesma construcao do trilho fino do dash principal: o gauge da
        # direita tem escala negativa e enche com o delta negativo.
        delta_gauge("Delta Slower", left, DELTA_LOSS, DELTA_FULL_S,
                    DELTA_FULL_S, alignment=2,
                    radius=rounded(radius=(2, 0, 0, 2))),
        delta_gauge("Delta Faster", right, DELTA_GAIN, -DELTA_FULL_S,
                    -DELTA_FULL_S / 2, alignment=0,
                    radius=rounded(radius=(0, 2, 2, 0))),
        marker("Delta Zero", zero, TEXT),
        bindings={"Visible": REF_READY},
    )


def delta_strip():
    """O delta nos ultimos `WINDOW_S` segundos, alinhado no tempo com os
    pedais: assim se ve em que frenagem a linha desceu. Sobe quando estou
    mais rapido que a referencia (o delta e negativo) e desce quando perco
    tempo; o valor e limitado a `TRACE_DELTA_S` para nao sair da tira. Neutro
    como a barra do cabecalho. Some junto com a referencia."""
    lines = [rect(f"Delta Grid {i}", Region(PLOT_X, y, PLOT_RIGHT - PLOT_X, 1.0),
                  TRACE_GRID) for i, y in enumerate(STRIP_YS)]
    limit = f"{TRACE_DELTA_S:g}"
    trace = chart(
        "Delta Trace", STRIP, TEXT,
        ncalc(f"-Max(-{limit}, Min({limit}, {DELTA_PROP}))"),
        low=-TRACE_DELTA_S, high=TRACE_DELTA_S)
    return group(
        "Delta Trace",
        *lines, trace,
        label(PLOT_X, 120.0, f"DELTA ±{limit} s", LEFT, y=DELTA_LABEL_Y),
        bindings={"Visible": REF_READY},
    )


#: Faixa dos mini-setores na linha do eixo, entre "-15 s" e "0": o rotulo e
#: um bloco por setor.
SECTOR_LABEL_X = PLOT_X + 100.0
SECTOR_X0, SECTOR_W, SECTOR_GAP, SECTOR_H = PLOT_X + 170.0, 32.0, 4.0, 8.0
SECTOR_Y = AXIS_Y + 2.0


def sector_color(index):
    """Cor do bloco: o delta publicado pelo gravador para o setor."""
    return js(
        f"var d = {states.HAS_SHARED} ? Number(getsharedvalueordefault("
        f"'{states.SHARED}', '{KEY}sd{index}', {SECTOR_NONE_VALUE})) "
        f": {SECTOR_NONE_VALUE};\r\n"
        f"if (!(d < {SECTOR_NONE_VALUE})) return '{MINI_SECTOR_NONE}';\r\n"
        f"return d < -{SECTOR_EQUAL_S:g} ? '{MINI_SECTOR_GAIN}' : "
        f"d > {SECTOR_EQUAL_S:g} ? '{MINI_SECTOR_LOSS}' : '{MINI_SECTOR_EQUAL}';",
        format_string="")


def sectors():
    """O resultado de cada mini-setor da volta contra a referencia: claro
    ganhei, laranja perdi, cinza igual, apagado ainda sem dado. Na volta
    seguinte o resultado antigo fica ate o setor 0 fechar."""
    # Cor de exemplo (o preview nao avalia a formula).
    sample = (MINI_SECTOR_GAIN, MINI_SECTOR_GAIN, MINI_SECTOR_EQUAL,
              MINI_SECTOR_LOSS, MINI_SECTOR_GAIN, MINI_SECTOR_GAIN,
              MINI_SECTOR_LOSS, MINI_SECTOR_NONE, MINI_SECTOR_NONE,
              MINI_SECTOR_NONE)
    blocks = []
    for i in range(SECTORS):
        block = rect(f"Sector {i + 1}",
                     Region(SECTOR_X0 + i * (SECTOR_W + SECTOR_GAP), SECTOR_Y,
                            SECTOR_W, SECTOR_H),
                     sample[i % len(sample)], radius=2,
                     bindings={"BackgroundColor": sector_color(i)})
        block["RenderingSkip"] = SKIP_SLOW
        blocks.append(block)
    return group(
        "Sectors",
        label(SECTOR_LABEL_X, 62.0, "SECTORS", LEFT, y=AXIS_Y),
        *blocks,
        bindings={"Visible": REF_READY},
    )


def axis():
    mono = "Arame Mono"
    return [
        label(PLOT_X, 60.0, f"-{WINDOW_S:g} s", LEFT, y=AXIS_Y, font=mono),
        label(PLOT_RIGHT - 60.0, 60.0, "0", RIGHT, y=AXIS_Y, font=mono),
    ]


def background():
    """O fundo do box em duas pecas com a mesma cor, cortado na base do
    grafico. Devolve (corpo, base): o corpo vai por baixo dos graficos e a
    base por cima, escondendo o pedal solto."""
    body = rect("Fill", Region(BOX.x, BOX.y, BOX.width, BASE_TOP - BOX.y),
                TRACE_BOX_FILL)
    base = rect("Fill Base", Region(BOX.x, BASE_TOP, BOX.width,
                                    BOX.bottom - BASE_TOP),
                TRACE_BOX_FILL, radius=(0, 0, 14, 14))
    return body, base


def layer():
    # So a borda: o preenchimento vem de `background()`.
    edge = rect("Trace Box", BOX, "#00000000", radius=(0, 0, 14, 14),
                border=TRACE_BOX_EDGE, thickness=1)
    edge["BorderStyle"]["BorderTop"] = 0
    body, base = background()
    grid_lines = [rect(f"Grid {i}", Region(PLOT_X, y, PLOT_RIGHT - PLOT_X, 1.0),
                       TRACE_GRID) for i, y in enumerate(GRID_YS)]
    now = rect("Now", NOW_LINE, TRACE_NOW, bindings={"Visible": RECORDER})
    # A cada quadro: os graficos amostram a ~30 Hz e precisam sempre do
    # valor do quadro, nao de um publicado no quadro anterior.
    now["RenderingSkip"] = 0

    return group(
        "Telemetry",
        body,
        group(
            "Reference",
            chart("Ref Throttle", PLOT, REF_THROTTLE, ref_value("thr"),
                  thickness=REF_THICKNESS),
            chart("Ref Brake", PLOT, REF_BRAKE, ref_value("brk"),
                  thickness=REF_THICKNESS),
            bindings={"Visible": REF_READY},
        ),
        chart("Throttle", PLOT, THROTTLE, ncalc("[Throttle]")),
        chart("Brake", PLOT, BRAKE, ncalc("[Brake]")),
        base, edge, *grid_lines,
        now,
        dot("Throttle Now", "Throttle", THROTTLE),
        dot("Brake Now", "Brake", BRAKE),
        *legend(), *axis(), delta_readout(), delta_strip(), sectors(),
    )
