"""Leaderboard de classe -- a coluna da direita do dashboard.

E uma unica linha-template que o SimHub repete verticalmente: a camada declara
`Repetitions` e `RepeatTopOffset`, e cada repeticao se identifica por
`repeatindex()`. Dai o padrao que domina as formulas -- o nome da propriedade
do piloto e montado em tempo de execucao a partir do indice da linha.

Todos os dados vem do plugin IRacingExtraProperties, que expoe o grid da classe
do jogador como propriedades numeradas (Driver_00_Name, Driver_01_Name, ...).
"""

from simhub.bindings import js
from simhub.model import OFF, Layer, RectangleItem, TextItem
from simhub.theme import (
    FONT, PADDING, PLAYER, SIZE_LABEL, TEXT, TEXT_SECONDARY, TEXT_TERTIARY,
    TILE_RAISED,
)
from . import layout as grid
from .generated.formulas import binding as original

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

#: Quantas linhas renderizar. O trecho comentado e a versao anterior da regra,
#: preservada pelo autor original.
ROWS_EXPRESSION = f"""//if([iRacingExtraProperties.iRacing_Player_PositionInClass] <= 11, 13, 3)

var index;
if ({FIELD_SIZE} - {PLAYER_POSITION} <= 5) {{
\tindex = {FIELD_SIZE} - 10;
}} else {{
\tindex = {PLAYER_POSITION} - 5;
}}
/**/

if ({FIELD_SIZE} <= 13 || index < 0 || {PLAYER_POSITION} <= 11) {{

\treturn {ROWS_FULL};
\t
}} else {{

\treturn {ROWS_WINDOW};
\t
}}"""

#: Colunas da linha. Posicao e nome a esquerda, os dois numeros a direita --
#: e a ordem em que se le: quem e, depois quao longe esta.
POSITION_WIDTH = 30.0
GAP_WIDTH = 56.0
DIFF_WIDTH = 70.0
COLUMN_GAP = 8.0

POSITION_X = BODY.x
NAME_X = POSITION_X + POSITION_WIDTH + COLUMN_GAP
#: A ultima coluna fica afastada da borda do painel pelo mesmo respiro que
#: as outras usam por dentro.
GAP_X = BODY.right - GAP_WIDTH - PADDING
DIFF_X = GAP_X - DIFF_WIDTH - COLUMN_GAP
NAME_WIDTH = DIFF_X - NAME_X - COLUMN_GAP

#: A fonte acompanha a altura da linha (que depende de quantas cabem no
#: corpo da coluna) em vez de um tamanho fixo -- 17px estourava a caixa
#: sempre que a linha ficava mais baixa que o desenhado originalmente.
ROW_TEXT_SIZE = min(17.0, ROW_HEIGHT * 0.72)
ROW_INSET = 3.0

#: Largura de glifo das colunas numericas. Sai do tamanho da fonte: com o
#: 14.0 fixo de antes, a fonte menor deixava os digitos esparramados
#: ("1 0 . 1"). Ponto e virgula ocupam menos que um digito.
ROW_CHAR_WIDTH = ROW_TEXT_SIZE * 0.62
ROW_SPECIAL_WIDTH = ROW_TEXT_SIZE * 0.36

TEXT_GRAY = TEXT_SECONDARY
ROW_BG = TILE_RAISED
ROW_BG_PLAYER = "White"
DISCONNECTED = TEXT_TERTIARY
FASTER = "#8800FF7F"
SLOWER = "#88FF6347"


def row_top(index=0):
    """Topo da linha `index` dentro do corpo da coluna."""
    return BODY.y + ROW_HEIGHT * index


def driver(field, sep=""):
    """Propriedade do piloto na linha corrente.

    `sep` existe so para reproduzir a diferenca de espacamento que o editor
    gravou em algumas formulas; nao tem efeito nenhum na avaliacao.
    """
    return (
        "$prop('IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_' + "
        f"format((repeatindex() - 1), '00'){sep} + '_{field}')"
    )


def is_player():
    return f"{driver('Name')} == {PLAYER_NAME}"


def has_driver():
    return f"if ({driver('Name')} != '') return 1; else return 0;"


def row_text(name, left, width, size, text, align, **fields):
    """TextItem de uma coluna da linha."""
    return TextItem(
        name=name,
        IsTextItem=True,
        Font=FONT,
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


def position():
    """Posicao na classe. Laranja para o jogador, apagada se desconectado."""
    return row_text(
        "DriverPosition", POSITION_X, POSITION_WIDTH, ROW_TEXT_SIZE, "00", align=1,
        bindings={
            "Text": js(f"""if ({driver('PositionInClass')} != 0) {{

\treturn {driver('PositionInClass')};

}} else {{

\treturn '';
\t
}}""", jsext=3, format_string=""),
            "TextColor": js(f"""if ({is_player()}) {{

\treturn 'DarkOrange';
\t
}} else {{

\treturn 'Gray';
\t
}}""", jsext=3),
            "Opacity": js(f"""if ({driver('IsConnected')} == false) {{

\treturn 70;
\t
}} else {{

\treturn 100;
\t
}}"""),
        },
    )


def container():
    """Faixa de fundo da linha; fica branca na linha do jogador."""
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
        Top=row_top() + ROW_INSET, Width=NAME_WIDTH + 8.0,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={
            "Visible": js(has_driver(), jsext=3),
            "BackgroundColor": js(f"""if ({is_player()}) {{

\treturn '{ROW_BG_PLAYER}';
\t
}} else {{

\treturn '{ROW_BG}';
\t
}}"""),
        },
    )


def name():
    """Nome do piloto, alinhado a esquerda."""
    return row_text(
        "DriverName", NAME_X, NAME_WIDTH, ROW_TEXT_SIZE, "DRIVER NAME", align=0,
        bindings={
            "Text": js(f"return {driver('Name')};", jsext=3, format_string=""),
            "TextColor": js(f"""if ({is_player()}) {{

\treturn 'Black';
\t
}} else if ({driver('IsConnected')} == false) {{

\treturn '{DISCONNECTED}';
\t
}} else {{

\treturn 'Gray';
\t
}}""", jsext=3),
            "Visible": js(has_driver()),
        },
    )


def last_lap_difference():
    """Diferenca entre a ultima volta do jogador e a do piloto da linha.

    Verde quando o outro foi mais rapido, vermelho quando mais lento. Some nas
    duas primeiras voltas, quando ainda nao ha tempo valido para comparar.
    """
    faster = (f"timespantoseconds($prop('LastLapTime')) - "
              f"timespantoseconds({driver('LastLapTime')})")
    return row_text(
        "LastLapDifference", DIFF_X, DIFF_WIDTH, ROW_TEXT_SIZE, "-0.00", align=2,
        color=FASTER,
        UseMonospacedText=True,
        char_width=ROW_CHAR_WIDTH,
        SpecialCharsWidth=ROW_SPECIAL_WIDTH,
        special_chars=".,",
        BorderStyle={
            "RadiusTopLeft": 5, "RadiusTopRight": 5,
            "RadiusBottomLeft": 5, "RadiusBottomRight": 5,
        },
        bindings={
            "Text": js(f"""var lapdiff;

if (repeatindex() == $prop('iRacingExtraProperties.iRacing_Player_PositionInClass') && $prop('iRacingExtraProperties.iRacing_Player_PositionInClass') != 0) {{

\treturn '';
\t
}} else if ({faster} < 0) {{

\tlapdiff = Math.abs({faster});
\t
\tif (lapdiff >= 100) {{
\t\t
\t\treturn '-' + format(lapdiff, '0') + ' ';
\t\t
\t}} else {{
\t
\t\treturn '-' + format(lapdiff, '0.0') + ' ';
\t
\t}}
\t\t
}} else {{

\tlapdiff = {faster};
\t
\tif (lapdiff >= 100) {{
\t\t
\t\treturn '+' + format(lapdiff, '0') + ' ';
\t\t
\t}} else {{
\t
\t\treturn '+' + format(lapdiff, '0.00') + ' ';
\t
\t}}
\t\t
}}""", jsext=3, format_string="mm\\:ss\\.ff"),
            "Visible": js(f"""if ($prop("GameRawData.Telemetry.Lap") <= 2) {{

\treturn 0;
\t
}} else if ({driver('LastLapTime')} == '00:00:00' || $prop('DataCorePlugin.GameRawData.Telemetry.LapBestLap') == 0 || {driver('PositionInClass')} == 0) {{

\treturn 0;
\t
}} else {{

\treturn 1;
\t
}}""", jsext=3),
            "TextColor": js(f"""if ({faster} < 0) {{
\t
\treturn '{FASTER}';
\t
}} else {{
\t
\treturn '{SLOWER}';
\t\t
}}""", jsext=3),
        },
    )


def _best_lap_seconds(prop_expression):
    """Converte um BestLapTime em segundos somando mm, ss e centesimos.

    O plugin entrega o tempo como texto, entao a conversao e feita a mao com
    format() em vez de timespantoseconds().
    """
    return (
        f"(parseInt(format({prop_expression}, 'mm') * 60) + "
        f"parseInt(format({prop_expression}, 'ss')) + "
        f"parseFloat(format({prop_expression}, 'ff') * 0.01))"
    )


def gap():
    """Gap para o lider.

    Em corrida usa o gap pronto do plugin; fora dela compara a melhor volta do
    piloto com a do lider da classe (Driver_00).
    """
    leader_best = "$prop('IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_00_BestLapTime')"
    return row_text(
        "Gap", GAP_X, GAP_WIDTH, ROW_TEXT_SIZE, "00.0", align=2,
        color=FASTER,
        UseMonospacedText=True,
        char_width=ROW_CHAR_WIDTH,
        SpecialCharsWidth=ROW_SPECIAL_WIDTH,
        special_chars=".,",
        bindings={
            "Text": js(f"""if ($prop('SessionTypeName') == 'Race') {{

\tif ({driver('PositionInClass')} != 0) {{
\t\t
\t\tif ({driver('GapToLeaderString', sep=' ')} == '0.0' && repeatindex() == 1) {{
\t\t
\t\t\treturn '0.0';
\t\t\t
\t\t}} else {{
\t\t
\t\t\treturn {driver('GapToLeaderString', sep=' ')};
\t\t
\t\t}}
\t\t
\t}} else {{
\t
\t\treturn '';
\t\t
\t}}
\t
}} else {{

\tif(repeatindex() == 1) {{

\t\treturn ' 0.0';
\t
\t}} else {{

\t\treturn '+' +
\t\t
\t\tformat(({_best_lap_seconds(driver('BestLapTime'))} - 
\t
\t\t{_best_lap_seconds(leader_best)}), '0.0');
\t\t
\t}}
\t
}}""", jsext=3, format_string="0.0"),
            "TextColor": js(f"""if ({is_player()}) {{

\treturn 'White';
\t
}} else if ($prop("SessionTypeName") == 'Race' && {driver('IsConnected')} == false) {{

\treturn '{DISCONNECTED}';
\t
}} else {{

\treturn 'Gray';
\t
}}""", jsext=3),
            "Visible": js(has_driver(), jsext=3),
        },
    )


def layer():
    """A camada repetidora, com a linha-template dentro."""
    return Layer(
        position(), container(), name(), last_lap_difference(), gap(),
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

    Mesma linha, mesma grade de colunas; o que muda e o indice, que aqui e
    calculado a partir da posicao do jogador. Essas formulas vem verbatim do
    original (`tools/dump_formulas.py`) -- sao trinta linhas de aritmetica de
    indice que nao ganham nada em serem reescritas.
    """
    def at(node, target, **extra):
        return original(f"Leaderboard Overflow/{node}", target, **extra)

    top = row_top(OVERFLOW_START)
    return Layer(
        row_text("DriverPosition", POSITION_X, POSITION_WIDTH, ROW_TEXT_SIZE,
                 "00", align=1, top=top,
                 bindings={
                     "Text": at("DriverPosition", "Text"),
                     "TextColor": at("DriverPosition", "TextColor"),
                     "Opacity": at("DriverPosition", "Opacity"),
                 }),
        RectangleItem(
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
            bindings={
                "Visible": at("DriverContainer", "Visible"),
                "BackgroundColor": at("DriverContainer", "BackgroundColor"),
            },
        ),
        row_text("DriverName", NAME_X, NAME_WIDTH, ROW_TEXT_SIZE,
                 "DRIVER NAME", align=0, top=top,
                 bindings={
                     "Text": at("DriverName", "Text"),
                     "TextColor": at("DriverName", "TextColor"),
                 }),
        row_text("LastLapDifference", DIFF_X, DIFF_WIDTH, ROW_TEXT_SIZE,
                 "-0.00", align=2, top=top, color=FASTER,
                 UseMonospacedText=True, char_width=ROW_CHAR_WIDTH,
                 SpecialCharsWidth=ROW_SPECIAL_WIDTH, special_chars=".,",
                 bindings={
                     "Text": at("LastLapDifference", "Text"),
                     "Visible": at("LastLapDifference", "Visible"),
                     "TextColor": at("LastLapDifference", "TextColor"),
                 }),
        row_text("Gap", GAP_X, GAP_WIDTH, ROW_TEXT_SIZE, "00.0", align=2,
                 top=top, color=FASTER,
                 UseMonospacedText=True, char_width=ROW_CHAR_WIDTH,
                 SpecialCharsWidth=ROW_SPECIAL_WIDTH, special_chars=".,",
                 bindings={
                     "Text": at("Gap", "Text"),
                     "TextColor": at("Gap", "TextColor"),
                     "Visible": at("Gap", "Visible"),
                 }),
        name="Leaderboard Overflow",
        Group=True,
        Repetitions=OVERFLOW_ROWS,
        PrepareRepetitions=True,
        RepeatTopOffset=ROW_HEIGHT,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": original("Leaderboard Overflow", "Visible")},
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
