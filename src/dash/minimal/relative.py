"""Mini relativo: os 2 carros a frente, o jogador e os 2 atras.

Colunas: posicao, sobrenome (negrito), ultima volta (m:ss.f) e distancia
relativa em segundos (negrito, sem sinal: a linha ja diz quem esta a frente).
O bloco tem a altura do algarismo da marcha -- o topo da primeira linha e a
base da ultima alinham com ele.

Os dados sao os do relative do dash principal (IRacingExtraProperties,
`RLB_Ahead_*` / `RLB_Behind_*`, 01 = o carro mais perto). Cada linha e uma
camada com `Visible` na existencia do carro, entao uma linha vazia nao
avalia nada.
"""

from simhub.bindings import formatted, js, ncalc
from simhub.theme import FONT, PLAYER, TEXT, TEXT_SECONDARY
from .. import states
from ..right import LAP_PARSE
from ..widgets import LEFT, RIGHT, text
from .base import SKIP_NAMES, SKIP_SLOW, group

BLOCK_X, BLOCK_Y, BLOCK_H = 150.0, 74.0, 130.0
ROWS = 5
ROW_H = 18.0
ROW_PITCH = (BLOCK_H - ROW_H) / (ROWS - 1)
SIZE = 16.0

#: (x, largura, alinhamento) de cada coluna.
POS = (150.0, 20.0, LEFT)
NAME = (178.0, 84.0, LEFT)
LAP = (270.0, 58.0, RIGHT)
GAP = (336.0, 40.0, RIGHT)

#: Velocidade de atualizacao do gap: muda o tempo todo, mas so no decimo.
SKIP_GAP = 2

LAST_NAME = ("var p = String({value} || '').trim().split(/\\s+/); "
             "return p[p.length - 1];")


def cell(column, top, sample, *, name, color, bold=False, font=None,
         binding=None, skip=0):
    x, width, align = column
    extra = {"font": font} if font else {}
    item = text(x, top, width, ROW_H, sample, name=name, size=SIZE,
                color=color, weight="Bold" if bold else None, align=align,
                bindings={"Text": binding}, **extra)
    item["RenderingSkip"] = skip
    return item


def car_row(side, index, row):
    """Linha de outro carro. `side` e 'Ahead' ou 'Behind'."""
    def prop(field):
        return f"IRacingExtraProperties.RLB_{side}_{field}_0{index}"

    top = BLOCK_Y + ROW_PITCH * row
    return group(
        f"{side} {index}",
        cell(POS, top, "5", name="Position", color=TEXT_SECONDARY,
             binding=js(f"return String($prop('{prop('PositionInClass')}'))"
                        ".replace(/[^0-9]/g, '');", jsext=3, format_string=""),
             skip=SKIP_SLOW),
        cell(NAME, top, "Moreau", name="Name", color=TEXT, bold=True, font=FONT,
             binding=js(LAST_NAME.format(value=f"$prop('{prop('Name')}')"),
                        jsext=3, format_string=""),
             skip=SKIP_NAMES),
        cell(LAP, top, "1:36.8", name="Last Lap", color=TEXT_SECONDARY,
             binding=js(states.FORMAT + LAP_PARSE
                        + f"return fmtLap(lapsec($prop('{prop('LastLapTime')}')));",
                        jsext=3, format_string=""),
             skip=SKIP_SLOW),
        cell(GAP, top, "0.7", name="Gap", color=TEXT, bold=True,
             binding=js(f"var g = parseFloat($prop('{prop('RelativeGapToPlayer')}'));\r\n"
                        "if (isNaN(g)) return 'N/A';\r\n"
                        "return Math.abs(g).toFixed(1);", jsext=3, format_string=""),
             skip=SKIP_GAP),
        bindings={"Visible": ncalc(f"isnull([{prop('Name')}],'')!=''")},
    )


def me_row(row):
    top = BLOCK_Y + ROW_PITCH * row
    return group(
        "Player",
        cell(POS, top, "7", name="Position", color=PLAYER,
             binding=formatted(
                 "[IRacingExtraProperties.iRacing_Player_PositionInClass]", "0"),
             skip=SKIP_SLOW),
        cell(NAME, top, "Auad", name="Name", color=PLAYER, bold=True, font=FONT,
             binding=js(LAST_NAME.format(
                 value="$prop('DataCorePlugin.GameData.PlayerName')"),
                 jsext=3, format_string=""),
             skip=SKIP_NAMES),
        cell(LAP, top, "1:36.1", name="Last Lap", color=PLAYER,
             binding=js(states.FORMAT + LAP_PARSE
                        + "return fmtLap(lapsec($prop('LastLapTime')));",
                        jsext=3, format_string=""),
             skip=SKIP_SLOW),
        bindings={"Visible": ncalc(
            "[DataCorePlugin.GameRunning] && !isnull([PlayerName])")},
    )


def layer():
    return group(
        "Relative",
        car_row("Ahead", 2, 0),
        car_row("Ahead", 1, 1),
        me_row(2),
        car_row("Behind", 1, 3),
        car_row("Behind", 2, 4),
    )
