"""Coluna direita: quem esta em volta, e o contexto da pista no rodape.

A coluna troca de modo conforme a sessao. Sao quatro, empilhados no mesmo
espaco e ligados/desligados pelo SimHub:

  Standings  a tabela da classe (com a janela de overflow quando o jogador
             esta longe do topo) -- em leaderboard.py
  Relative   os dois carros na frente, o jogador e os dois atras
  Practice   o log das ultimas voltas, para treino

Todos usam a mesma grade de colunas e a mesma altura de linha, entao trocar de
modo nao reposiciona a leitura: a posicao continua na esquerda, os tempos na
direita.

O rodape e fixo em qualquer modo -- hora, pista, ar, grip e chuva.
"""

from simhub.bindings import formatted, ncalc
from simhub.model import OFF, Layer, RectangleItem, TextItem
from simhub.theme import (
    BACKGROUND, CORNER_RADIUS, CYAN, FONT, GUTTER, PADDING, PLAYER, SIZE_LABEL,
    SIZE_VALUE_SM, TEXT, TEXT_SECONDARY, TILE_RAISED, WEIGHT_VALUE,
)
from . import layout as grid
from . import leaderboard
from .generated.formulas import FORMULAS, binding as original
from .widgets import CENTER, LEFT, RIGHT, caption, text, tile

PANEL = leaderboard.PANEL
BODY = leaderboard.BODY

#: Altura de linha do relative. Mais alta que a do leaderboard porque sao so
#: cinco linhas e cada uma carrega mais campos.
REL_ROW = 44.0
REL_ROWS = 5

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


ME_INDEX = 2


def rel_text(name, left, width, sample, *, align, size=SIZE_LABEL + 5.0,
             color=TEXT_SECONDARY, top, bindings=None, mono=False):
    return text(left, top, width, REL_ROW, sample, name=name, size=size,
                color=color, align=align, mono=mono,
                char_width=14.0 if mono else None, bindings=bindings)


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
                 color=accent,
                 bindings={"Text": at("Position", "Text"),
                           "Visible": at("Position", "Visible")}),
        rel_text("Car Number", NUM_X, NUM_W, "28", align=CENTER, top=top,
                 color=accent,
                 bindings={"Text": at("Car Number", "Text")}
                 if not me else {"Text": at("Car Number", "Text")}),
        rel_text("Name", NAME_X, NAME_W, "Lorem ipsum", align=LEFT, top=top,
                 color=TEXT if me else TEXT_SECONDARY,
                 bindings={"Text": at("Name", "Text")} if not me else None),
        rel_text("Last Lap", LAP_X, LAP_W, "0:00.00", align=RIGHT, top=top,
                 mono=True,
                 bindings={"Text": at("Last Lap", "Text"),
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
    """Os dois carros a frente, o jogador, e os dois atras."""
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
    )


#: Log de voltas: seis linhas, na metade direita do corpo.
LOG_ROWS = 6
LOG_ROW = 33.0


def practice():
    """Modo de treino: as ultimas voltas, com a melhor destacada."""
    width = 200.0
    area = grid.Region(BODY.right - width, BODY.y + PADDING, width,
                       LOG_ROW * (LOG_ROWS + 1))
    header, rows = area.split_top(LOG_ROW)

    def at(node, target, **extra):
        return original(f"Practice/Lap Data/{node}", target, **extra)

    return Layer(
        tile(area, name="Log Tile", color=TILE_RAISED, radius=CORNER_RADIUS),
        caption(header.x + PADDING, header.y + PADDING, header.width,
                "Lap log", name="Log Title"),
        Layer(
            text(rows.x + PADDING, rows.y, 40.0, LOG_ROW, "00",
                 name="LapNumber", size=SIZE_LABEL + 4.0, align=RIGHT,
                 color=TEXT_SECONDARY,
                 bindings={"Text": at("LapNumber", "Text"),
                           "TextColor": at("LapNumber", "TextColor")}),
            text(rows.x + PADDING + 48.0, rows.y,
                 rows.width - PADDING * 2 - 48.0, LOG_ROW, "0:00.00",
                 name="LapTime", size=SIZE_LABEL + 4.0, align=RIGHT,
                 color=TEXT, mono=True, char_width=14.0,
                 bindings={"Text": at("LapTime", "Text"),
                           "TextColor": at("LapTime", "TextColor")}),
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
    )


def footer():
    """Condicoes da pista. Igual ao rodape da esquerda, para as duas colunas
    terminarem na mesma linha e com o mesmo peso."""
    region = grid.Region(PANEL.x, BODY.bottom + GUTTER, PANEL.width,
                         leaderboard.FOOTER_HEIGHT)
    cells = region.columns(5, gutter=GUTTER)
    fields = [
        ("Hour", "Hour", "00:00", "[DataCorePlugin.CurrentDateTime]", "HH:mm", CYAN),
        ("Track", "Track", "00", "[GameRawData.Telemetry.TrackTemp]", "00", None),
        ("Air", "Air", "00", "[AirTemperature]", "00", None),
        ("Grip", "Grip", "00",
         "[GameRawData.CurrentSessionInfo.SessionTrackRubberState]", None, None),
        ("Rain", "Rain", "00",
         "format([GameRawData.Telemetry.Precipitation] * 100, 'NA')", None, None),
    ]
    items = []
    for cell, (name, label, sample, expression, fmt, color) in zip(cells, fields):
        inner = cell.inset(left=PADDING, right=PADDING)
        label_height = SIZE_LABEL + 6.0
        body = grid.Region(inner.x, inner.y + label_height + 2.0,
                           inner.width, inner.height - label_height - 8.0)
        items += [
            tile(cell, name=f"{name} Tile"),
            caption(inner.x, inner.y + PADDING * 0.75, inner.width, label,
                    name=f"{name} Label"),
            text(body.x, body.y, body.width, body.height, sample, name=name,
                 size=SIZE_VALUE_SM, color=color or TEXT, weight=WEIGHT_VALUE,
                 align=RIGHT,
                 bindings={"Text": formatted(expression, fmt) if fmt
                           else ncalc(expression)}),
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
        footer(),
        leaderboard.standings(),
        relative(),
        practice(),
        name="Right Component",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
