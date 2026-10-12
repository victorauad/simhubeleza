"""Coluna direita: quem esta em volta, e o contexto da pista no rodape.

A coluna troca de modo conforme a sessao. Sao tres, empilhados no mesmo
espaco e ligados/desligados por formula (nao mais so pela ferramenta de
preview):

  Standings  a tabela da classe (com a janela de overflow quando o jogador
             esta longe do topo) -- em leaderboard.py. Aparece fora de pista,
             e por 4s toda vez que uma volta e completada.
  Relative   os tres carros na frente, o jogador e os tres atras. O modo
             padrao -- aparece sempre que os outros dois nao se aplicam.
  Practice   o log das voltas, so em treino offline -- ocupa a secao
             inteira, sem dividir espaco com o relative.

Standings e Relative usam a mesma grade de colunas e a mesma altura de linha,
entao trocar entre os dois nao reposiciona a leitura: a posicao continua na
esquerda, os tempos na direita.

O rodape e fixo em qualquer modo: os setores contra a melhor volta -- que
dao lugar ao New Lap Info por alguns segundos a cada volta nova.
"""

from simhub.bindings import formatted, js, ncalc
from simhub.model import OFF, Layer, RectangleItem, TextItem
from simhub.theme import (
    BACKGROUND, CORNER_RADIUS, CORNER_RADIUS_TILE, CYAN, FASTER, FONT, GUTTER,
    SLOWER,
    MONO_ADVANCE, PADDING, PLAYER, SIZE_LABEL, SIZE_VALUE_SM, TEXT, TEXT_SECONDARY,
    TEXT_TERTIARY, TILE, TILE_RAISED, WEIGHT_VALUE, rounded,
)
from . import layout as grid
from . import leaderboard, new_lap_info, sectors, states
from .generated.formulas import FORMULAS, binding as original
from .widgets import CENTER, LEFT, RIGHT, caption, separators, text, tile

PANEL = leaderboard.PANEL
BODY = leaderboard.BODY

#: Linha do jogador: ambar translucido com filete ambar, como no canvas.
PLAYER_ROW = leaderboard.ROW_BG_PLAYER
PLAYER_ROW_EDGE = "#8CF4A73A"

#: Condicoes que decidem qual modo aparece.
#:
#: `[SessionTypeName]` nao existe. O tipo da sessao vem de
#: `states.SESSION_TYPE` (o publicado pela maquina de estados, ou
#: `GameRawData.CurrentSessionInfo.SessionType` lido na hora). NCalc nao indexa propriedade
#: dinamicamente, entao a checagem so existe em JS -- por tabela, os dois
#: formulas que a incorporam tambem. "Offline Testing" e a string do treino
#: livre solo, conferida na API do SimHub em 2026-10-11.
#:
#: Preambulo comum: calcula `inPractice` a partir da sessao atual. Os tres
#: formulas que precisam da condicao (o proprio modo Practice, e as duas
#: negacoes em Standings/Relative) prefixam este texto e so trocam o
#: `return` final.
_SESSION_TYPE_LOOKUP = (
    f"\tvar inPractice = {states.SESSION_TYPE} == 'Offline Testing';\r\n"
)
IN_PRACTICE_JS = _SESSION_TYPE_LOOKUP + "\treturn inPractice;"

#: Quando o Standings toma o lugar do Relative -- so tres situacoes:
#:   - garagem: `IsInGarage`, ou fora do carro (`IsOnTrack` falso) sem
#:     replay rodando -- em replay o iRacing tambem da `IsOnTrack` falso;
#:   - esperando no grid: `SessionState` 1 GetInCar ou 2 Warmup (numero ou
#:     nome do enum);
#:   - 5 s depois de completar cada volta (`Lap` sobe com o carro na pista
#:     ou em replay).
#: Fora disso, Relative. Booleanos normalizados por `states.BASE` (`yes`).
STANDINGS_TIME = 5.0
_STANDINGS_CHECK = (
    states.BASE
    + f"var replay = yes($prop('{states.TELEMETRY}IsReplayPlaying'));\r\n"
    f"var garage = yes($prop('{states.TELEMETRY}IsInGarage')) || "
    "(!onTrack && !replay);\r\n"
    f"var ss = $prop('{states.TELEMETRY}SessionState');\r\n"
    "var ssn = num(ss);\r\n"
    "var grid = ssn === 1 || ssn === 2 || "
    "(ssn == null && ss != null && /^(GetInCar|Warmup)$/i.test(String(ss)));\r\n"
    "var sl = root.sl;\r\n"
    "if (sl == null) { sl = root.sl = { lap: lap, until: 0 }; }\r\n"
    f"if (lapDone(sl) && (onTrack || replay)) sl.until = now + {int(STANDINGS_TIME * 1000)};\r\n"
    "sl.lap = lap;\r\n"
    "var standings = garage || grid || now < sl.until;\r\n"
)
SHOW_STANDINGS_JS = (
    _SESSION_TYPE_LOOKUP + _STANDINGS_CHECK
    + "return !inPractice && standings;"
)
SHOW_RELATIVE_JS = (
    _SESSION_TYPE_LOOKUP + _STANDINGS_CHECK
    + "return !inPractice && !standings;"
)

#: Altura de linha do relative -- sete linhas (3 a frente, eu, 3 atras) no
#: mesmo corpo que antes cabia cinco (2+1+2), com folga de sobra.
REL_ROWS = 7
REL_ROW = BODY.height / REL_ROWS

#: Tamanho do texto das linhas. Com o dash reduzido na frente do volante o
#: relative e lido de relance; 22 px ocupa ~54% da linha (40.7 px) e ainda
#: deixa o filete do cartao respirando.
REL_SIZE = 22.0

#: Colunas, da esquerda para a direita. Larguras medidas pelo avanco da
#: Arame Mono (0.6 em) no REL_SIZE: posicao "18." e numero "128" com 3
#: caracteres, volta "0:00.00" com 7, gap "122.2" com 5.
_GLYPH = REL_SIZE * MONO_ADVANCE
POS_X, POS_W = BODY.x, 3 * _GLYPH + 6.0
NUM_X, NUM_W = POS_X + POS_W + 4.0, 3 * _GLYPH + 4.0
NAME_X = NUM_X + NUM_W + 8.0
BAR_X, BAR_W = BODY.right - 8.0, 8.0
GAP_W = 5 * _GLYPH + 2.0
GAP_X = BAR_X - 4.0 - GAP_W
LAP_W = 7 * _GLYPH + 4.0
LAP_X = GAP_X - 8.0 - LAP_W
NAME_W = LAP_X - NAME_X - 8.0


def rel_top(index):
    """Topo da linha `index` do relative (0 = primeira, 2 = o jogador)."""
    block = REL_ROW * REL_ROWS
    return BODY.y + (BODY.height - block) / 2 + REL_ROW * index


ME_INDEX = 3


def rel_text(name, left, width, sample, *, align, size=REL_SIZE,
             color=TEXT_SECONDARY, top, bindings=None, mono=False, font=None):
    extra = {"font": font} if font else {}
    return text(left, top, width, REL_ROW, sample, name=name, size=size,
                color=color, align=align, mono=mono,
                char_width=14.0 if mono else None, bindings=bindings, **extra)


#: Volta do relative em segundos: o plugin entrega "mm:ss.fff" em texto (ou
#: um TimeSpan, no caso do jogador); zero ou vazio vira N/A no `fmtLap`.
LAP_PARSE = (
    "var lapsec = function (v) { if (typeof v === 'string') { "
    "var m = /^(\\d+):(\\d+(?:\\.\\d+)?)$/.exec(v.trim()); "
    "if (m) { var s = Number(m[1]) * 60 + Number(m[2]); "
    "return s > 0 ? s : null; } } return sec(v); };\r\n"
)


def rel_row(prefix, name, top, *, repetitions=None, offset=None,
            visible_from=None, me=False):
    """Uma linha do relative -- repetida para frente e para tras do jogador.

    `prefix` e o caminho da formula no original; `me` marca a linha do proprio
    jogador, que nao repete e ganha o destaque de cor.
    """
    def at(node, target, **extra):
        return original(f"{prefix}/{node}", target, **extra)

    side = "Ahead" if "Ahead" in prefix else "Behind"
    lap_prop = ("$prop('LastLapTime')" if me else
                f"$prop('IRacingExtraProperties.RLB_{side}_LastLapTime_0'"
                "+repeatindex())")
    gap_prop = (f"$prop('IRacingExtraProperties.RLB_{side}_RelativeGapToPlayer_0'"
                "+repeatindex())")
    accent = PLAYER if me else TEXT_SECONDARY
    items = [
        RectangleItem(
            name="Row",
            IsRectangleItem=True,
            BackgroundColor=PLAYER_ROW if me else TILE_RAISED,
            BorderStyle=rounded(PLAYER_ROW_EDGE if me else None, 1,
                                radius=(2, 8, 2, 8)),
            Left=BODY.x, Top=top + 3.0,
            Width=BODY.width, Height=REL_ROW - 6.0,
            Visible=True, BlinkPhasisInverted=False,
            RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
        ),
        rel_text("Position", POS_X, POS_W, "18.", align=RIGHT, top=top,
                 color=accent,
                 bindings={"Text": at("Position", "Text"),
                           "Visible": at("Position", "Visible")}),
        rel_text("Car Number", NUM_X, NUM_W, "28", align=CENTER, top=top,
                 color=accent,
                 bindings={"Text": at("Car Number", "Text")}
                 if not me else {"Text": at("Car Number", "Text")}),
        rel_text("Name", NAME_X, NAME_W,
                 "Victor Auad" if me else "Lorem ipsum", align=LEFT, top=top,
                 color=PLAYER if me else TEXT, font=FONT,
                 bindings={"Text": at("Name", "Text")} if not me else None),
        rel_text("Last Lap", LAP_X, LAP_W, "0:00.0", align=RIGHT, top=top,
                 mono=True,
                 bindings={"Text": js(states.FORMAT + LAP_PARSE
                                      + f"return fmtLap(lapsec({lap_prop}));",
                                      jsext=3, format_string=""),
                           "Visible": at("Last Lap", "Visible")}),
    ]

    if me:
        items.append(
            rel_text("Name2", GAP_X, GAP_W, "-180", align=RIGHT, top=top,
                     bindings={"Text": at("Name2", "Text"),
                               "TextColor": at("Name2", "TextColor")}))
    else:
        items.append(
            rel_text("Gap", GAP_X, GAP_W, "22.2", align=RIGHT, top=top,
                     mono=True, color=TEXT,
                     bindings={"Text": js(
                         f"var g = parseFloat({gap_prop});\r\n"
                         "if (g == null || isNaN(g)) return 'N/A';\r\n"
                         "return g.toFixed(1);", jsext=3, format_string=""),
                               "Visible": at("Gap", "Visible")}))
        items.append(RectangleItem(
            name="Gap Color",
            IsRectangleItem=True,
            BackgroundColor=CYAN,
            BorderStyle={"RadiusTopLeft": 3, "RadiusTopRight": 3,
                         "RadiusBottomLeft": 3, "RadiusBottomRight": 3},
            Left=BAR_X, Top=top + 11.0, Width=BAR_W, Height=REL_ROW - 22.0,
            Visible=True, BlinkPhasisInverted=False,
            RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
            bindings={"BackgroundColor": at("Gap Color", "BackgroundColor"),
                      "Visible": at("Gap Color", "Visible")},
        ))

    if not me:
        # Veu escuro por cima da linha inteira quando o carro esta no box:
        # some com a linha sem tirar ela do lugar, entao a ordem da pista
        # continua legivel de relance.
        veil = {"Visible": at("IsInPit", "Visible")}
        if f"{prefix}/IsInPit.FontSize" in FORMULAS:
            veil["FontSize"] = at("IsInPit", "FontSize")
        items.append(text(BODY.x, top + 3.0, BODY.width, REL_ROW - 6.0, "",
                          name="IsInPit", size=30.0, align=LEFT,
                          opacity=55.0, bindings=veil))
        items[-1]["BackgroundColor"] = BACKGROUND
        items[-1]["Visible"] = False
        items[-1]["BorderStyle"] = {
            "BorderColor": "#00FFFFFF",
            "RadiusTopLeft": CORNER_RADIUS, "RadiusTopRight": CORNER_RADIUS,
            "RadiusBottomLeft": CORNER_RADIUS,
            "RadiusBottomRight": CORNER_RADIUS,
        }

    layer_bindings = {"Visible": original(prefix, "Visible")}
    return Layer(
        *items,
        name=name,
        Group=True,
        Repetitions=repetitions if repetitions is not None else 0,
        PrepareRepetitions=True if repetitions else OFF,
        RepeatTopOffset=offset if offset is not None else 0.0,
        Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
        bindings=layer_bindings,
    )


def relative():
    """Os tres carros a frente, o jogador, e os tres atras."""
    # Repetitions conta as copias extras: 2 = a linha base + 2 = 3 carros.
    return Layer(
        rel_row("Relative/Driver Ahead Repeat", "Driver Ahead Repeat",
                rel_top(ME_INDEX - 1), repetitions=2, offset=-REL_ROW),
        rel_row("Relative/Me", "Me", rel_top(ME_INDEX), me=True),
        rel_row("Relative/Driver Behind Repeat", "Driver Behind Repeat",
                rel_top(ME_INDEX + 1), repetitions=2, offset=REL_ROW),
        name="Relative",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": js(SHOW_RELATIVE_JS)},
    )


#: Log de voltas: agora ocupa a secao inteira que o relative usa (so aparece
#: em treino offline, entao nao precisa dividir espaco com ele) -- cabem mais
#: linhas e mais colunas: numero, tempo, temperatura da pista, delta para a
#: melhor volta e consumo de combustivel.
LOG_HEADER_HEIGHT = 26.0
LOG_ROWS = 9
LOG_ROW = (BODY.height - LOG_HEADER_HEIGHT) / LOG_ROWS

#: Corpo do log: o dash fica reduzido na frente do volante, entao os numeros
#: vao ao maior tamanho que a linha (~29 px) comporta, perto do relative.
LOG_SIZE = 20.0
LOG_HEADER_SIZE = SIZE_LABEL + 1.5

#: Colunas do log, da esquerda para a direita. Numero e tempo repetem as
#: formulas extraidas do original (`Practice/Lap Data/...`); temperatura,
#: delta e combustivel sao novas. O combustivel e calculado pelo proprio dash
#: (`FUEL_LOG_JS`): o `PersistantTrackerPlugin` nao tem consumo por volta.
LOG_NUM_W = 40.0
LOG_TIME_W = 92.0
LOG_TRACK_W = 76.0
LOG_DELTA_W = 90.0
LOG_FUEL_W = 90.0


#: Guarda comum: sem volta suficiente ainda, a linha fica em branco -- mesma
#: condicao usada por `Practice/Lap Data/LapNumber.Text` no original.
LAP_INVALID = "(($prop('GameRawData.Telemetry.Lap') - repeatindex()) < 1)"


#: Consumo por volta, medido pelo proprio dash: o `PersistantTrackerPlugin`
#: so guarda tempo e delta das voltas anteriores (`PreviousLap_NN_FuelConsumed`
#: nao existe -- conferido na API do SimHub). A cada virada de `Lap` guarda
#: (combustivel no inicio da volta - combustivel agora) para a volta que
#: acabou. Nao conta a volta em andamento quando o dash abre, nem volta com
#: reabastecimento (o tanque subiu em algum momento) ou que pulou contagem.
#: A atualizacao e chaveada pelo numero da volta, entao da no mesmo se o
#: `root` for compartilhado entre as repeticoes da linha ou um por repeticao.
#: Sem medida, a linha mais recente cai no `Fuel_LastLapConsumption`; sem
#: nenhuma das duas a volta mostra N/A (null -> envelope do fallback.py).
#: Vazio so na linha de uma volta que ainda nao existe.
FUEL_LOG_JS = (
    "var lap = Number($prop('GameRawData.Telemetry.Lap')) || 0;\r\n"
    "var fuel = Number($prop('GameRawData.Telemetry.FuelLevel'));\r\n"
    "var ok = $prop('GameRawData.Telemetry.FuelLevel') != null && !isNaN(fuel);\r\n"
    "var h = root.h || (root.h = {});\r\n"
    "if (root.lap != null && lap < root.lap) { h = root.h = {}; root.start = null; }\r\n"
    "if (ok) { if (root.prev != null && fuel > root.prev + 0.05) root.dirty = true; "
    "root.prev = fuel; }\r\n"
    "if (root.lap != null && lap > root.lap) {\r\n"
    "\tvar used = root.start == null || !ok ? null : root.start - fuel;\r\n"
    "\tif (lap == root.lap + 1 && !root.dirty && used > 0) h[root.lap] = used;\r\n"
    "\troot.start = ok ? fuel : null; root.dirty = false;\r\n"
    "}\r\n"
    "root.lap = lap;\r\n"
    "var n = lap - repeatindex();\r\n"
    "if (n < 1) return '';\r\n"
    "var v = h[n];\r\n"
    "if (v == null && repeatindex() == 1) "
    "v = Number($prop('DataCorePlugin.Computed.Fuel_LastLapConsumption'));\r\n"
    "return (v == null || isNaN(v) || v <= 0) ? null : v;"
)


#: Temperatura da pista por volta, gravada pelo proprio dash: o SimHub nao
#: guarda historico dela (so o `PersistantTrackerPlugin` tem `PreviousLap_*`
#: para tempo e delta). A ultima leitura valida de cada volta fica para ela
#: na virada de `Lap`. Voltas de antes do dash abrir mostram N/A; a linha
#: mais recente, ainda sem gravacao, cai na leitura atual. Chaveada pelo
#: numero da volta, como o `FUEL_LOG_JS`.
TRACK_LOG_JS = (
    "var lap = Number($prop('GameRawData.Telemetry.Lap')) || 0;\r\n"
    "var temp = Number($prop('GameRawData.Telemetry.TrackTemp'));\r\n"
    "var ok = $prop('GameRawData.Telemetry.TrackTemp') != null && !isNaN(temp);\r\n"
    "var h = root.h || (root.h = {});\r\n"
    "if (root.lap != null && lap < root.lap) { h = root.h = {}; root.temp = null; }\r\n"
    "if (root.lap != null && lap > root.lap && root.temp != null) h[root.lap] = root.temp;\r\n"
    "if (ok) root.temp = temp;\r\n"
    "root.lap = lap;\r\n"
    "var n = lap - repeatindex();\r\n"
    "if (n < 1) return '';\r\n"
    "var v = h[n];\r\n"
    "if (v == null && repeatindex() == 1 && ok) v = temp;\r\n"
    "return (v == null || isNaN(v)) ? null : v;"
)


def lap_js(body, format_string=None):
    """Formula JS de uma coluna nova do log: `body` e o codigo dentro do
    `else` (a guarda de volta invalida ja fica por fora)."""
    expression = (
        f"if ({LAP_INVALID}) {{\r\n\r\n\treturn '';\r\n\t\r\n}} else {{\r\n\r\n"
        f"{body}\r\n\t\r\n}}"
    )
    return js(expression, jsext=3, format_string=format_string)


def practice():
    """Modo de treino: o log de voltas, com a melhor destacada."""
    area = BODY
    header, rows = area.split_top(LOG_HEADER_HEIGHT)

    def at(node, target, **extra):
        return original(f"Practice/Lap Data/{node}", target, **extra)

    inner = area.inset(left=PADDING, right=PADDING)
    num_x = inner.x
    time_x = num_x + LOG_NUM_W + GUTTER
    track_x = time_x + LOG_TIME_W + GUTTER
    delta_x = track_x + LOG_TRACK_W + GUTTER
    fuel_x = delta_x + LOG_DELTA_W + GUTTER

    columns = [
        ("#", LOG_NUM_W, num_x, RIGHT),
        ("Time", LOG_TIME_W, time_x, RIGHT),
        ("Track", LOG_TRACK_W, track_x, RIGHT),
        ("Delta", LOG_DELTA_W, delta_x, RIGHT),
        ("Fuel", LOG_FUEL_W, fuel_x, RIGHT),
    ]

    #: Delta zero (a propria melhor volta) fica sem sinal e em cinza:
    #: nem ganhou nem perdeu.
    delta_body = (
        "\tvar d = $prop('PersistantTrackerPlugin.PreviousLap_0' + "
        "(repeatindex() - 1) + '_DeltaToSessionBest');\r\n"
        "\tif (d == null || isNaN(d)) { return null; }\r\n"
        "\tif (Math.abs(d) < 0.05) { return '0.0'; }\r\n"
        "\tif (d < 0) { return '-' + format(Math.abs(d), '0.0'); }\r\n"
        "\telse { return '+' + format(d, '0.0'); }"
    )
    delta_color_body = (
        "\tvar d = $prop('PersistantTrackerPlugin.PreviousLap_0' + "
        "(repeatindex() - 1) + '_DeltaToSessionBest');\r\n"
        f"\tif (Math.abs(d) < 0.05) {{ return '{TEXT_TERTIARY}'; }}\r\n"
        f"\tif (d < 0) {{ return '{FASTER}'; }} else {{ return '{SLOWER}'; }}"
    )
    return Layer(
        tile(area, name="Log Tile", color=TILE, radius=CORNER_RADIUS_TILE),
        *(caption(x, header.y + 4.0, w, label, name=f"Log {label} Header",
                  align=align, size=LOG_HEADER_SIZE)
          for label, w, x, align in columns),
        Layer(
            text(num_x, rows.y, LOG_NUM_W, LOG_ROW, "00",
                 name="LapNumber", size=LOG_SIZE, align=RIGHT,
                 color=TEXT_SECONDARY,
                 bindings={"Text": at("LapNumber", "Text"),
                           "TextColor": at("LapNumber", "TextColor")}),
            text(time_x, rows.y, LOG_TIME_W, LOG_ROW, "0:00.0",
                 name="LapTime", size=LOG_SIZE, align=RIGHT,
                 color=TEXT, mono=True, char_width=14.0,
                 bindings={"Text": js(
                     states.FORMAT
                     + "if (($prop('GameRawData.Telemetry.Lap') - repeatindex())"
                     " < 1) return '';\r\n"
                     "return fmtLap(sec($prop('PersistantTrackerPlugin."
                     "PreviousLap_0' + (repeatindex() - 1))));",
                     jsext=3, format_string=""),
                           "TextColor": at("LapTime", "TextColor")}),
            text(track_x, rows.y, LOG_TRACK_W, LOG_ROW, "32",
                 name="LapTrackTemp", size=LOG_SIZE, align=RIGHT,
                 color=TEXT_TERTIARY,
                 bindings={"Text": js(TRACK_LOG_JS, jsext=3,
                                      format_string="00")}),
            text(delta_x, rows.y, LOG_DELTA_W, LOG_ROW, "-0.1",
                 name="LapDelta", size=LOG_SIZE, align=RIGHT,
                 color=TEXT, mono=True, char_width=14.0,
                 bindings={"Text": lap_js(delta_body),
                           "TextColor": lap_js(delta_color_body)}),
            text(fuel_x, rows.y, LOG_FUEL_W, LOG_ROW, "2.30",
                 name="LapFuel", size=LOG_SIZE, align=RIGHT,
                 color=TEXT_SECONDARY,
                 bindings={"Text": js(FUEL_LOG_JS, jsext=3,
                                           format_string="0.00")}),
            name="Lap Data",
            Group=True, Repetitions=LOG_ROWS, PrepareRepetitions=True,
            RepeatTopOffset=LOG_ROW,
            Visible=True, BlinkPhasisInverted=False,
            RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
        ),
        name="Practice",
        Group=True, Repetitions=0, Visible=False,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": js(IN_PRACTICE_JS)},
    )


def footer():
    """Setores contra a melhor volta. Um unico cartao, igual ao rodape da
    esquerda e ao OTS -- as tres faixas formam uma barra inferior continua.
    As condicoes da pista que moravam aqui foram para a coluna esquerda."""
    region = grid.Region(PANEL.x, BODY.bottom + GUTTER, PANEL.width,
                         leaderboard.FOOTER_HEIGHT)
    # Nos primeiros segundos de cada volta o New Lap Info toma o lugar dos
    # setores (states.py decide; os dois leem o mesmo gatilho).
    timing = sectors.layer(region)
    timing["Bindings"] = {"Visible": states.sectors_visible()}
    return [states.gate(timing), new_lap_info.layer(region)]


def layer():
    """A coluna direita inteira, com os modos empilhados."""
    return Layer(
        # O corpo (tabela, relative ou log) e o rodape sao dois tiles, como
        # no canvas -- a coluna em si nao tem fundo.
        tile(BODY, name="Background", color=TILE),
        *footer(),
        leaderboard.standings(visible=js(SHOW_STANDINGS_JS)),
        relative(),
        practice(),
        name="Right Component",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
