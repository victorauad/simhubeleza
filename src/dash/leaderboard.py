"""Leaderboard de classe -- a coluna da direita do dashboard.

E uma unica linha-template que o SimHub repete verticalmente: a camada declara
`Repetitions` e `RepeatTopOffset`, e cada repeticao se identifica por
`repeatindex()`. Dai o padrao que domina as formulas -- o nome da propriedade
do piloto e montado em tempo de execucao a partir do indice da linha.

Todos os dados vem do plugin IRacingExtraProperties, que expoe o grid da classe
do jogador como propriedades numeradas (Driver_00_Name, Driver_01_Name, ...).

Reescrita de desempenho (docs/otimizacao.md, Fase 3): cada formula monta o
prefixo da linha uma vez (`_row`), le cada propriedade uma vez e o gap do
treino sai de `timespantoseconds`, sem passar o tempo por texto. Os itens
das linhas rodam a ~6 Hz (`SKIP_ROW`). O comportamento e o das formulas
originais -- `tools/check_leaderboard.py` roda as duas versoes lado a lado
(as originais ficam em `tools/fixtures/leaderboard_legacy.json`). Diferencas
de proposito, todas no teste: o overflow usa a paleta da tabela principal, e
piloto sem volta no treino mostra N/A em vez de "+-82.9".
"""

from simhub.bindings import js
from simhub.model import OFF, Layer, RectangleItem, TextItem
from simhub.theme import (
    FASTER as THEME_FASTER, FONT, FONT_MONO, PLAYER, SIZE_LABEL,
    SLOWER as THEME_SLOWER, TEXT, TEXT_SECONDARY, TEXT_TERTIARY, TILE_RAISED,
)
from . import layout as grid
from . import states

#: Area util da coluna, e quanto dela sobra para as linhas depois do rodape.
PANEL = grid.RIGHT.inset(left=grid.MARGIN, right=grid.MARGIN)

#: Mesma altura do rodape da esquerda e do OTS -- ver layout.BOTTOM_BAR_HEIGHT.
FOOTER_HEIGHT = grid.BOTTOM_BAR_HEIGHT
BODY = grid.Region(PANEL.x, PANEL.y, PANEL.width,
                   PANEL.height - FOOTER_HEIGHT - 6.0)

#: Altura de cada linha repetida: as 13 linhas do caso cheio tem que caber
#: exatamente no corpo da coluna, entao a altura sai da divisao, nao de um
#: numero escolhido.
ROW_HEIGHT = BODY.height / 13.0

#: Quantas linhas mostrar. Com grid pequeno, ou com o jogador perto do topo,
#: cabe a tabela inteira (13); caso contrario mostra uma janela de 3 ao redor
#: dele. O offset da janela e calculado no binding de Repetitions.
ROWS_FULL, ROWS_WINDOW = 13, 3

PLAYER_NAME = "$prop('DataCorePlugin.GameData.PlayerName')"

PLAYER_POSITION = "$prop('IRacingExtraProperties.iRacing_Player_PositionInClass')"
FIELD_SIZE = "$prop('PlayerClassOpponentsCount')"

BOARD = "IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_"

#: Inicio da janela do overflow, em indice do plugin -- a mesma conta do
#: original. Le `F` (tamanho da classe) e `me` (posicao do jogador).
WINDOW_INDEX = (
    f"var F = {FIELD_SIZE}, me = {PLAYER_POSITION};\r\n"
    "var index = F - me <= 5 ? F - 10 : me - 5;\r\n"
)

#: Quantas linhas renderizar: a tabela inteira (13) com grid pequeno ou o
#: jogador perto do topo; senao o trio da frente, e o overflow assume.
ROWS_EXPRESSION = (
    WINDOW_INDEX
    + f"return (F <= 13 || index < 0 || me <= 11) ? {ROWS_FULL} : {ROWS_WINDOW};"
)

#: O overflow aparece exatamente quando a tabela principal encolhe.
OVERFLOW_VISIBLE = (
    WINDOW_INDEX
    + "return (F <= 13 || index < 0 || me <= 11) ? 0 : 1;"
)

#: Cadencia dos itens das linhas: ~6 Hz. Gap e diferenca de volta mudam no
#: maximo a cada setor; nome e posicao, a cada ultrapassagem.
SKIP_ROW = 9


#: Colunas da linha. Posicao e nome a esquerda, os dois numeros a direita --
#: e a ordem em que se le: quem e, depois quao longe esta.
POSITION_WIDTH = 30.0
GAP_WIDTH = 64.0
DIFF_WIDTH = 78.0
COLUMN_GAP = 8.0

POSITION_X = BODY.x
NAME_X = POSITION_X + POSITION_WIDTH + COLUMN_GAP
GAP_X = BODY.right - GAP_WIDTH
DIFF_X = GAP_X - DIFF_WIDTH - COLUMN_GAP
NAME_WIDTH = DIFF_X - NAME_X - COLUMN_GAP

ROW_TEXT_SIZE = 17.0
ROW_INSET = 3.0

TEXT_GRAY = TEXT_SECONDARY
ROW_BG = TILE_RAISED
#: Linha do jogador: ambar translucido sob nome ambar (canvas Grafite).
ROW_BG_PLAYER = "#38F4A73A"
DISCONNECTED = TEXT_TERTIARY
FASTER = THEME_FASTER
SLOWER = THEME_SLOWER


def row_top(index=0):
    """Topo da linha `index` dentro do corpo da coluna."""
    return BODY.y + ROW_HEIGHT * index


def row_text(name, left, width, size, text, align, **fields):
    """TextItem de uma coluna da linha. Numeros em Arame Mono, que ja e
    monoespacada -- so o nome vai em Funnel Sans (`font=FONT`)."""
    font = fields.pop("font", FONT_MONO)
    if font == FONT_MONO:
        fields.pop("UseMonospacedText", None)
    return TextItem(
        name=name,
        IsTextItem=True,
        Font=font,
        FontSize=size,
        Text=text,
        TextColor=fields.pop("color", TEXT_GRAY),
        HorizontalAlignment=align,
        VerticalAlignment=1,
        CharWidth=fields.pop("char_width", 16.0),
        SpecialChars=fields.pop("special_chars", ",:;"),
        BackgroundColor="#00FFFFFF",
        Height=fields.pop("height", ROW_HEIGHT),
        Left=left,
        Top=fields.pop("top", row_top()),
        Visible=True,
        BlinkPhasisInverted=False,
        Width=width,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        **fields,
    )


def _row(overflow):
    """Prelúdio JS da linha: `r` (repeticao), `i` (indice do plugin), `P`
    (prefixo das propriedades) e `d(campo)`. No overflow, tambem `F`, `me`
    e `index` (inicio da janela)."""
    head = WINDOW_INDEX + "var i = repeatindex() - 1 + index;\r\n" if overflow \
        else "var i = repeatindex() - 1;\r\n"
    return (
        head
        + f"var P = '{BOARD}' + (i >= 0 && i < 10 ? '0' : '') + i + '_';\r\n"
        "var d = function (f) { return $prop(P + f); };\r\n"
    )


def row_js(overflow, body, **options):
    return js(_row(overflow) + body, **options)


def _is_player():
    return f"d('Name') == {PLAYER_NAME}"


#: Diferenca da ultima volta do jogador para a do piloto da linha
#: (negativa = o outro foi mais rapido).
LAST_DIFF = ("var diff = timespantoseconds($prop('LastLapTime')) - "
             "timespantoseconds(d('LastLapTime'));\r\n")

#: Posicao do jogador na classe (no overflow ja vem lida em `me`).
def _me(overflow):
    return "" if overflow else f"var me = {PLAYER_POSITION};\r\n"


#: Melhor volta em centesimos, como o original lia (minutos da hora, segundos
#: e centesimos truncados), mas sem formatar o tempo em texto.
CENTIS = ("var cs = function (v) { var s = timespantoseconds(v); "
          "if (s == null || isNaN(s)) return 0; "
          "return Math.floor((s % 3600) * 100 + 1e-6); };\r\n")


#: Gap do SimHub reescrito no padrao do dash: segundos em s.f, acima de um
#: minuto em m:ss.f; o que nao e numero (voltas de diferenca, "1L") passa
#: como veio.
GAP = (states.FMT_TIME
       + "var gap = function (v) { if (v == null) return v; "
       "var t = String(v).trim(); "
       "var m = /^([+-]?)(?:(\\d+):)?(\\d+(?:\\.\\d+)?)$/.exec(t); "
       "if (!m) return t; "
       "var s = (m[2] ? Number(m[2]) * 60 : 0) + Number(m[3]); "
       "return m[1] + fmtTime(s); };\r\n")


def formulas(overflow):
    """Bindings de cada coluna da linha: {(controle, alvo): binding}."""
    o = overflow
    # Overflow: o original nao foi restilizado; agora segue a paleta da
    # tabela principal (cores mapeadas no teste de equivalencia).
    return {
        ("DriverPosition", "Text"): row_js(
            o, "var v = d('PositionInClass');\r\nreturn v != 0 ? v : '';",
            jsext=3, format_string=""),
        ("DriverPosition", "TextColor"): row_js(
            o, f"return {_is_player()} ? '{PLAYER}' : '{TEXT_TERTIARY}';",
            jsext=3),
        ("DriverPosition", "Opacity"): row_js(
            o, "return d('IsConnected') == false ? 70 : 100;"),
        ("DriverContainer", "Visible"): row_js(
            o, ("if (index < 0) return 0;\r\n" if o else "")
            + "return d('Name') != '' ? 1 : 0;", jsext=3),
        ("DriverContainer", "BackgroundColor"): row_js(
            o, f"return {_is_player()} ? '{ROW_BG_PLAYER}' : '{ROW_BG}';"),
        ("DriverName", "Text"): row_js(
            o, "return d('PositionInClass') != 0 ? d('Name') : '';" if o
            else "return d('Name');", jsext=3, format_string=""),
        ("DriverName", "TextColor"): row_js(
            o, f"if ({_is_player()}) return '{PLAYER}';\r\n"
            f"if (d('IsConnected') == false) return '{DISCONNECTED}';\r\n"
            f"return '{TEXT}';", jsext=3),
        ("LastLapDifference", "Text"): row_js(
            o, _me(o)
            + "if (i + 1 == me && me != 0) return '';\r\n"
            + LAST_DIFF
            + "if (diff < 0) { var a = Math.abs(diff); "
            "return '-' + format(a, a >= 100 ? '0' : '0.0') + ' '; }\r\n"
            "return '+' + format(diff, diff >= 100 ? '0' : '0.0') + ' ';",
            jsext=3, format_string="mm\\:ss\\.ff"),
        ("LastLapDifference", "Visible"): row_js(
            o, "if ($prop('GameRawData.Telemetry.Lap') <= 2) return 0;\r\n"
            "if (d('LastLapTime') == '00:00:00' || "
            "$prop('DataCorePlugin.GameRawData.Telemetry.LapBestLap') == 0 || "
            + ("d('Name') == ''" if o else "d('PositionInClass') == 0")
            + ") return 0;\r\nreturn 1;", jsext=3),
        ("LastLapDifference", "TextColor"): row_js(
            o, ("if (i + 1 == me) return 'White';\r\n" if o else "")
            + LAST_DIFF
            + f"return diff < 0 ? '{FASTER}' : '{SLOWER}';", jsext=3),
        ("Gap", "Text"): row_js(
            o, GAP + "return d('PositionInClass') != 0 ? gap(d('GapToLeaderString')) : '';"
            if o else
            GAP + f"if ({states.SESSION_TYPE} == 'Race') "
            "return d('PositionInClass') != 0 ? gap(d('GapToLeaderString')) : '';\r\n"
            "if (repeatindex() == 1) return ' 0.0';\r\n"
            + CENTIS
            + "var mine = cs(d('BestLapTime'));\r\n"
            f"var lead = cs($prop('{BOARD}00_BestLapTime'));\r\n"
            # Sem volta (dele ou do lider): falta dado, vira N/A.
            "if (mine == 0 || lead == 0) return null;\r\n"
            "return '+' + format((mine - lead) / 100, '0.0');",
            jsext=3, format_string="0.0"),
        ("Gap", "TextColor"): row_js(
            o, f"if ({_is_player()}) return 'White';\r\n"
            f"if (d('IsConnected') == false && {states.SESSION_TYPE} == 'Race') "
            f"return '{DISCONNECTED}';\r\nreturn 'Gray';", jsext=3),
        ("Gap", "Visible"): row_js(
            o, "return d('Name') != '' ? 1 : 0;", jsext=3),
        ("DriverName", "Visible"): row_js(
            o, "return d('Name') != '' ? 1 : 0;"),
    }


def _bind(controls, overflow):
    """Cola os bindings da linha nos controles e aplica a cadencia."""
    table = formulas(overflow)
    for control in controls:
        name = control["Name"]
        bindings = {target: binding for (owner, target), binding in table.items()
                    if owner == name}
        if overflow and name == "DriverName":
            bindings.pop("Visible", None)   # o original nao tinha
        control["Bindings"] = bindings
        control["RenderingSkip"] = SKIP_ROW
    return controls


def position(top=None):
    """Posicao na classe. Ambar para o jogador, apagada se desconectado."""
    return row_text(
        "DriverPosition", POSITION_X, POSITION_WIDTH, ROW_TEXT_SIZE, "00",
        align=1, top=row_top() if top is None else top)


def container(top=None):
    """Faixa de fundo da linha; fica ambar na linha do jogador."""
    top = row_top() if top is None else top
    return RectangleItem(
        name="DriverContainer",
        IsRectangleItem=True,
        BackgroundColor=ROW_BG,
        BorderStyle={
            "BorderColor": "#FF00BFFF",
            "RadiusTopLeft": 5, "RadiusTopRight": 5,
            "RadiusBottomLeft": 5, "RadiusBottomRight": 5,
        },
        Height=ROW_HEIGHT - ROW_INSET * 2, Left=NAME_X - 4.0,
        Top=top + ROW_INSET, Width=NAME_WIDTH + 8.0,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def name(top=None):
    """Nome do piloto, alinhado a esquerda."""
    return row_text(
        "DriverName", NAME_X, NAME_WIDTH, ROW_TEXT_SIZE, "DRIVER NAME", align=0,
        font=FONT, top=row_top() if top is None else top)


def last_lap_difference(top=None):
    """Diferenca entre a ultima volta do jogador e a do piloto da linha.

    Verde quando o outro foi mais rapido, vermelho quando mais lento. Some nas
    duas primeiras voltas, quando ainda nao ha tempo valido para comparar.
    """
    return row_text(
        "LastLapDifference", DIFF_X, DIFF_WIDTH, ROW_TEXT_SIZE, "-0.0", align=2,
        color=FASTER,
        UseMonospacedText=True,
        char_width=14.0,
        SpecialCharsWidth=8.0,
        special_chars=".,",
        BorderStyle={
            "RadiusTopLeft": 5, "RadiusTopRight": 5,
            "RadiusBottomLeft": 5, "RadiusBottomRight": 5,
        },
        top=row_top() if top is None else top,
    )


def gap(top=None):
    """Gap para o lider.

    Em corrida usa o gap pronto do plugin; fora dela compara a melhor volta do
    piloto com a do lider da classe (Driver_00).
    """
    return row_text(
        "Gap", GAP_X, GAP_WIDTH, ROW_TEXT_SIZE, "00.0", align=2,
        color=FASTER,
        UseMonospacedText=True,
        char_width=14.0,
        SpecialCharsWidth=8.0,
        special_chars=".,",
        top=row_top() if top is None else top,
    )


def row(overflow=False, top=None):
    """Os controles de uma linha, com os bindings."""
    return _bind([position(top), container(top), name(top),
                  last_lap_difference(top), gap(top)], overflow)


def layer():
    """A camada repetidora, com a linha-template dentro."""
    return Layer(
        *row(),
        name="Leaderboard",
        Group=True,
        Repetitions=2,
        PrepareRepetitions=True,
        RepeatTopOffset=ROW_HEIGHT,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Repetitions": js(ROWS_EXPRESSION)},
    )


#: Onde a janela do overflow comeca. Quando o jogador esta longe do topo, a
#: camada principal mostra so o trio da frente e o overflow assume dali para
#: baixo, com a janela centrada nele -- 3 + 7 = as 10 linhas do caso apertado.
OVERFLOW_START = ROWS_WINDOW
OVERFLOW_ROWS = 7


def overflow_layer():
    """A janela em volta do jogador, quando ele nao cabe na tabela cheia.

    Mesma linha, mesma grade de colunas; o que muda e o indice, calculado a
    partir da posicao do jogador (`WINDOW_INDEX`).
    """
    return Layer(
        *row(overflow=True, top=row_top(OVERFLOW_START)),
        name="Leaderboard Overflow",
        Group=True,
        Repetitions=OVERFLOW_ROWS,
        PrepareRepetitions=True,
        RepeatTopOffset=ROW_HEIGHT,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": js(OVERFLOW_VISIBLE)},
    )


def standings(visible=None):
    """A tabela da classe. `visible` e o binding que decide quando ela
    aparece -- ver `right.SHOW_STANDINGS`; sem ele, fica sempre desligada
    (usado pela ferramenta de preview, que liga cada modo a mao)."""
    return Layer(
        layer(), overflow_layer(),
        name="Standings",
        Group=True, Repetitions=0, Visible=False,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": visible} if visible else None,
    )
