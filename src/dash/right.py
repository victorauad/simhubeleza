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

O rodape e fixo em qualquer modo -- hora, pista, ar, grip e chuva.
"""

from simhub.bindings import formatted, js, ncalc
from simhub.model import OFF, Layer, RectangleItem, TextItem
from simhub.theme import (
    BACKGROUND, CORNER_RADIUS, CORNER_RADIUS_TILE, CYAN, FONT, GUTTER,
    PADDING, PLAYER, SIZE_LABEL, SIZE_VALUE_SM, TEXT, TEXT_SECONDARY,
    TEXT_TERTIARY, TILE, TILE_RAISED, WEIGHT_VALUE,
)
from . import layout as grid
from . import leaderboard
from .generated.formulas import FORMULAS, binding as original
from .widgets import CENTER, LEFT, RIGHT, caption, text, tile, value_unit

PANEL = leaderboard.PANEL
BODY = leaderboard.BODY

#: Condicoes que decidem qual modo aparece.
#:
#: `[SessionTypeName]` nao existe -- nao aparece no dump de
#: `SampleSessionData.json` nem em `SampleTelemetry.json`, nem foi usada uma
#: vez sequer no dashboard original. O caminho real, confirmado no dump:
#: `SessionInfo.CurrentSessionNum` (indice da sessao atual) mais
#: `SessionInfo.Sessions0<n>.SessionType` (o texto, por sessao do fim de
#: semana). NCalc nao indexa propriedade dinamicamente, entao a checagem so
#: existe em JS -- por tabela, os dois formulas que a incorporam tambem.
#: A string exata de uma sessao de treino livre solo ("Offline Testing")
#: segue sem confirmacao: nenhum dos dois dumps recebidos era desse tipo de
#: sessao.
#:
#: `[GameRawData.Telemetry.IsOnTrack]` e `[...LapCurrentLapTime]` estao
#: confirmados no dump de telemetria (existem, tipos batem).
#:
#: Preambulo comum: calcula `inPractice` a partir da sessao atual. Os tres
#: formulas que precisam da condicao (o proprio modo Practice, e as duas
#: negacoes em Standings/Relative) prefixam este texto e so trocam o
#: `return` final.
_SESSION_TYPE_LOOKUP = (
    "\tvar n = $prop('SessionInfo.CurrentSessionNum') + 1;\r\n"
    "\tvar inPractice = $prop('SessionInfo.Sessions0' + n + '.SessionType') "
    "== 'Offline Testing';\r\n"
)
IN_PRACTICE_JS = _SESSION_TYPE_LOOKUP + "\treturn inPractice;"

NOT_ON_TRACK = ("!([DataCorePlugin.GameRunning] && "
               "[GameRawData.Telemetry.IsOnTrack]='TRUE')")
NOT_ON_TRACK_JS = ("!($prop('DataCorePlugin.GameRunning') && "
                   "$prop('GameRawData.Telemetry.IsOnTrack') == 'TRUE')")
#: Verdadeiro nos primeiros 4s de cada volta -- o instante em que a anterior
#: acabou de ser completada.
JUST_COMPLETED_LAP_JS = (
    "$prop('GameRawData.Telemetry.LapCurrentLapTime') >= 0 && "
    "$prop('GameRawData.Telemetry.LapCurrentLapTime') < 4"
)
_STANDINGS_OR_JUST_LAPPED = f"(({NOT_ON_TRACK_JS}) || ({JUST_COMPLETED_LAP_JS}))"
SHOW_STANDINGS_JS = (
    _SESSION_TYPE_LOOKUP
    + f"\treturn !inPractice && {_STANDINGS_OR_JUST_LAPPED};"
)
SHOW_RELATIVE_JS = (
    _SESSION_TYPE_LOOKUP
    + f"\treturn !inPractice && !{_STANDINGS_OR_JUST_LAPPED};"
)

#: Altura de linha do relative -- sete linhas (3 a frente, eu, 3 atras) no
#: mesmo corpo que antes cabia cinco (2+1+2), com folga de sobra.
REL_ROWS = 7
REL_ROW = BODY.height / REL_ROWS

#: Colunas, da esquerda para a direita.
POS_X, POS_W = BODY.x, 40.0
NUM_X, NUM_W = BODY.x + 44.0, 40.0
NAME_X = BODY.x + 90.0
BAR_X, BAR_W = BODY.right - 8.0, 8.0
GAP_X, GAP_W = BODY.right - 76.0, 62.0
LAP_X, LAP_W = BODY.right - 166.0, 84.0
NAME_W = LAP_X - NAME_X - 8.0


def rel_top(index):
    """Topo da linha `index` do relative (0 = primeira, 2 = o jogador)."""
    block = REL_ROW * REL_ROWS
    return BODY.y + (BODY.height - block) / 2 + REL_ROW * index


ME_INDEX = 3


#: Formato unico do tempo de volta no relative. O original tinha um por
#: linha -- vazio nos carros a frente, `m\.ss\.ff` nos de tras e
#: `mm\:ss\.fff` na do jogador -- e cada linha aparecia diferente.
REL_LAP_FORMAT = "m\\:ss\\.fff"

#: Os digitos ficam monoespacados (colunas de numero nao "dancam" a cada
#: atualizacao), mas a largura sai do tamanho da fonte em vez de um 14.0
#: fixo, que a espalhava. Ponto e dois-pontos ocupam menos que um digito.
REL_TEXT_SIZE = SIZE_LABEL + 5.0
REL_CHAR_WIDTH = REL_TEXT_SIZE * 0.58
REL_SPECIAL_CHARS = ".:,"
REL_SPECIAL_WIDTH = REL_TEXT_SIZE * 0.32


def rel_text(name, left, width, sample, *, align, size=REL_TEXT_SIZE,
             color=TEXT_SECONDARY, top, bindings=None, mono=False):
    return text(left, top, width, REL_ROW, sample, name=name, size=size,
                color=color, align=align, mono=mono,
                char_width=size * 0.58 if mono else None,
                special_chars=REL_SPECIAL_CHARS if mono else None,
                special_chars_width=REL_SPECIAL_WIDTH if mono else None,
                bindings=bindings)


def rel_row(prefix, name, top, *, repetitions=None, offset=None,
            visible_from=None, me=False):
    """Uma linha do relative -- repetida para frente e para tras do jogador.

    `prefix` e o caminho da formula no original; `me` marca a linha do proprio
    jogador, que nao repete e ganha o destaque de cor.
    """
    def at(node, target, **extra):
        return original(f"{prefix}/{node}", target, **extra)

    accent = PLAYER if me else TEXT_SECONDARY
    items = [
        RectangleItem(
            name="Row",
            IsRectangleItem=True,
            BackgroundColor=TILE_RAISED,
            BorderStyle={
                "RadiusTopLeft": CORNER_RADIUS, "RadiusTopRight": CORNER_RADIUS,
                "RadiusBottomLeft": CORNER_RADIUS,
                "RadiusBottomRight": CORNER_RADIUS,
            },
            Left=BODY.x, Top=top + 3.0,
            Width=BODY.width, Height=REL_ROW - 6.0,
            Visible=True, BlinkPhasisInverted=False,
            RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
        ),
        rel_text("Position", POS_X, POS_W, "18.", align=RIGHT, top=top,
                 color=accent, mono=True,
                 bindings={"Text": at("Position", "Text"),
                           "Visible": at("Position", "Visible")}),
        rel_text("Car Number", NUM_X, NUM_W, "28", align=CENTER, top=top,
                 color=accent, mono=True,
                 bindings={"Text": at("Car Number", "Text")}),
        # O nome fica com espacamento proporcional: monoespacado, nome de
        # piloto vira uma fileira de letras esparramadas.
        rel_text("Name", NAME_X, NAME_W, "Player Name", align=LEFT, top=top,
                 color=TEXT if me else TEXT_SECONDARY,
                 bindings={"Text": at("Name", "Text")} if not me
                 else {"Text": ncalc("[DataCorePlugin.GameData.PlayerName]")}),
        # A linha do jogador vinha de `toshorttime()`, que ja devolve texto
        # pronto e ignorava o formato -- lendo `[LastLapTime]` cru as tres
        # variacoes de linha passam pelo mesmo `REL_LAP_FORMAT`.
        rel_text("Last Lap", LAP_X, LAP_W, "0:00.000", align=RIGHT, top=top,
                 mono=True,
                 bindings={
                     "Text": formatted("[LastLapTime]", REL_LAP_FORMAT) if me
                     else at("Last Lap", "Text", format_string=REL_LAP_FORMAT),
                     "Visible": at("Last Lap", "Visible"),
                 }),
    ]

    if me:
        items.append(
            rel_text("Name2", GAP_X, GAP_W, "-180", align=RIGHT, top=top,
                     mono=True,
                     bindings={"Text": at("Name2", "Text"),
                               "TextColor": at("Name2", "TextColor")}))
    else:
        items.append(
            rel_text("Gap", GAP_X, GAP_W, "22.2", align=RIGHT, top=top,
                     mono=True, color=TEXT,
                     bindings={"Text": at("Gap", "Text"),
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
    return Layer(
        rel_row("Relative/Driver Ahead Repeat", "Driver Ahead Repeat",
                rel_top(ME_INDEX - 1), repetitions=3, offset=-REL_ROW),
        rel_row("Relative/Me", "Me", rel_top(ME_INDEX), me=True),
        rel_row("Relative/Driver Behind Repeat", "Driver Behind Repeat",
                rel_top(ME_INDEX + 1), repetitions=3, offset=REL_ROW),
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

#: Colunas do log, da esquerda para a direita. Numero e tempo repetem as
#: formulas extraidas do original (`Practice/Lap Data/...`); temperatura,
#: delta e combustivel sao novas -- ver ESTADO.md para a pendencia de
#: validar `PersistantTrackerPlugin.PreviousLap_XX_FuelConsumed`, que nao
#: aparece em nenhum outro lugar do projeto.
LOG_NUM_W = 40.0
LOG_TIME_W = 92.0
LOG_TRACK_W = 76.0
LOG_DELTA_W = 90.0
LOG_FUEL_W = 90.0


#: Guarda comum: sem volta suficiente ainda, a linha fica em branco -- mesma
#: condicao usada por `Practice/Lap Data/LapNumber.Text` no original.
LAP_INVALID = "(($prop('GameRawData.Telemetry.Lap') - repeatindex()) < 1)"


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

    delta_body = (
        "\tvar d = $prop('PersistantTrackerPlugin.PreviousLap_0' + "
        "(repeatindex() - 1) + '_DeltaToSessionBest');\r\n"
        "\tif (d < 0) { return '-' + format(Math.abs(d), '0.00'); }\r\n"
        "\telse { return '+' + format(d, '0.00'); }"
    )
    delta_color_body = (
        "\tvar d = $prop('PersistantTrackerPlugin.PreviousLap_0' + "
        "(repeatindex() - 1) + '_DeltaToSessionBest');\r\n"
        "\tif (d < 0) { return 'SpringGreen'; } else { return 'Tomato'; }"
    )
    #: Temperatura de pista: o SimHub nao guarda um historico por volta dessa
    #: variavel (so o `PersistantTrackerPlugin` tem `PreviousLap_XX_*` para
    #: tempo e delta) -- entao so a volta mais recente mostra a leitura
    #: atual; as demais ficam em branco em vez de repetir um valor errado.
    track_body = (
        "\tif (repeatindex() == 1) { return $prop('GameRawData.Telemetry.TrackTemp'); }\r\n"
        "\telse { return ''; }"
    )
    #: Combustivel por volta: propriedade nao confirmada (ver ESTADO.md).
    fuel_body = (
        "\treturn $prop('PersistantTrackerPlugin.PreviousLap_0' + "
        "(repeatindex() - 1) + '_FuelConsumed');"
    )

    return Layer(
        tile(area, name="Log Tile", color=TILE, radius=CORNER_RADIUS_TILE),
        *(caption(x, header.y + 4.0, w, label, name=f"Log {label} Header",
                  align=align)
          for label, w, x, align in columns),
        Layer(
            text(num_x, rows.y, LOG_NUM_W, LOG_ROW, "00",
                 name="LapNumber", size=SIZE_LABEL + 3.0, align=RIGHT,
                 color=TEXT_SECONDARY,
                 bindings={"Text": at("LapNumber", "Text"),
                           "TextColor": at("LapNumber", "TextColor")}),
            text(time_x, rows.y, LOG_TIME_W, LOG_ROW, "0:00.00",
                 name="LapTime", size=SIZE_LABEL + 3.0, align=RIGHT,
                 color=TEXT, mono=True, char_width=14.0,
                 bindings={"Text": at("LapTime", "Text"),
                           "TextColor": at("LapTime", "TextColor")}),
            text(track_x, rows.y, LOG_TRACK_W, LOG_ROW, "32",
                 name="LapTrackTemp", size=SIZE_LABEL + 3.0, align=RIGHT,
                 color=TEXT_TERTIARY,
                 bindings={"Text": lap_js(track_body, "00")}),
            text(delta_x, rows.y, LOG_DELTA_W, LOG_ROW, "-0.12",
                 name="LapDelta", size=SIZE_LABEL + 3.0, align=RIGHT,
                 color=TEXT, mono=True, char_width=14.0,
                 bindings={"Text": lap_js(delta_body),
                           "TextColor": lap_js(delta_color_body)}),
            text(fuel_x, rows.y, LOG_FUEL_W, LOG_ROW, "2.30",
                 name="LapFuel", size=SIZE_LABEL + 3.0, align=RIGHT,
                 color=TEXT_SECONDARY,
                 bindings={"Text": lap_js(fuel_body, "0.00")}),
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


#: `SessionTrackRubberState` chega como frase do iRacing -- "moderately low
#: usage", "carry over" (confirmado nos dumps de propriedades do usuario) --
#: e cortava no card do rodape. Vira um codigo 1..6, do mais emborrachado
#: (mais grip) ao mais limpo; "carry over" nao e um nivel, e heranca da
#: sessao anterior, entao mostra "CO".
#:
#: O casamento e por palavra-chave, em JS: NCalc nao tem funcoes de string, e
#: a ordem importa -- "moderately low usage" tambem contem "low usage", entao
#: o teste mais especifico vem primeiro. String desconhecida cai em "--", o
#: que deixa visivel no teste ao vivo que faltou um valor na tabela.
GRIP_PROP = "GameRawData.CurrentSessionInfo.SessionTrackRubberState"
GRIP_LEVELS = [
    ("carry over", "'CO'"),
    ("maximum", "'1'"),
    ("extensive", "'2'"),
    ("moderately low", "'4'"),
    ("moderate", "'3'"),
    ("high usage", "'2'"),
    ("very low", "'5'"),
    ("low usage", "'5'"),
    ("clean", "'6'"),
]
GRIP_EXPRESSION_JS = (
    f"\tvar state = ($prop('{GRIP_PROP}') + '').toLowerCase();\r\n"
    + "".join(
        f"\tif (state.indexOf('{needle}') >= 0) return {code};\r\n"
        for needle, code in GRIP_LEVELS
    )
    + "\treturn '--';"
)

#: A chuva usava `'NA'` como *format string* do NCalc (que espera um padrao
#: numerico como `'00'`), entao sempre imprimia o literal "NA" em vez do
#: valor real. Sem dado de chuva (`Precipitation` negativo) mostra "--".
RAIN_PROP = "[GameRawData.Telemetry.Precipitation]"
RAIN_EXPRESSION = (
    f"if({RAIN_PROP} < 0, '--', format({RAIN_PROP} * 100, '00'))"
)


def footer():
    """Condicoes da pista. Um unico cartao, igual ao rodape da esquerda e ao
    OTS -- as tres faixas formam uma barra inferior continua."""
    region = grid.Region(PANEL.x, BODY.bottom + GUTTER, PANEL.width,
                         leaderboard.FOOTER_HEIGHT)
    inner = region.inset(left=PADDING, right=PADDING)
    # Hour e o unico campo de cinco glifos da fileira -- ver FOOTER_WEIGHTS
    # na coluna esquerda, que resolve o mesmo problema do outro lado.
    cells = inner.columns(5, gutter=GUTTER, weights=(1.4, 1.0, 1.0, 1.0, 1.0))
    #: (nome, rotulo, amostra, expressao, formato, cor, unidade). A unidade
    #: entra pelo mesmo `value_unit()` da coluna esquerda, entao a distancia
    #: do numero ate ela e a mesma dos dois lados do dash.
    fields = [
        ("Hour", "Hour", "00:00", "[DataCorePlugin.CurrentDateTime]", "HH:mm",
         CYAN, ""),
        ("Track", "Track", "00", "[GameRawData.Telemetry.TrackTemp]", "00",
         None, "°C"),
        ("Air", "Air", "00", "[AirTemperature]", "00", None, "°C"),
        ("Grip", "Grip", "0", GRIP_EXPRESSION_JS, None, None, ""),
        ("Rain", "Rain", "00", RAIN_EXPRESSION, None, None, "%"),
    ]
    items = [tile(region, name="Footer Tile")]
    for cell, spec in zip(cells, fields):
        name, label, sample, expression, fmt, color, unit = spec
        cell_inner = cell.inset(left=PADDING, right=PADDING)
        label_height = SIZE_LABEL + 6.0
        body = grid.Region(cell_inner.x, cell_inner.y + label_height + 2.0,
                           cell_inner.width, cell_inner.height - label_height - 8.0)
        if name == "Grip":
            binding = js(expression, jsext=3)
        elif fmt:
            binding = formatted(expression, fmt)
        else:
            binding = ncalc(expression)
        items += [
            caption(cell_inner.x, cell_inner.y + PADDING * 0.75,
                    cell_inner.width, label, name=f"{name} Label"),
            *value_unit(body, sample, unit, name=name,
                        value_size=SIZE_VALUE_SM, color=color or TEXT,
                        align=LEFT, value_bindings={"Text": binding}),
        ]
    return Layer(
        *items,
        name="Data",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def layer():
    """A coluna direita inteira, com os modos empilhados."""
    return Layer(
        tile(PANEL, name="Background", color=TILE),
        footer(),
        leaderboard.standings(visible=js(SHOW_STANDINGS_JS)),
        relative(),
        practice(),
        name="Right Component",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
