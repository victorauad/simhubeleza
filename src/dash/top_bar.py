"""Barra superior: pedais, RPM, delta e os avisos.

Implementa a revisao desenhada no Figma (`LDY1mlry0kX59Nw6ueDj1h`, section
`4317:567`), medida num frame de 1329x132. Toda coordenada aqui esta nas
unidades do desenho e passa por `grid.scaled()` na hora de virar pixel -- uma
constante so (`layout.SCALE`) separa o desenho do painel.

A ordem, em cada lado, do exterior para o centro:

    [4 quadrados de RPM]  [chip de aviso]  [numero do pedal]

e por cima de tudo isso a fileira fina de dez segmentos do pedal. No miolo,
o cartao do delta. O lado direito e o espelho do esquerdo -- o Figma tem os
dois lados desenhados, mas os numeros da direita escapam do container (os
segmentos terminam em 1349 num frame de 1329) e ficam 18px mais baixos, entao
espelhar a esquerda e o que reproduz a intencao.

O pedal enche do centro para fora: no estado de 75% do Figma sao os segmentos
do lado de dentro que estao acesos.
"""

from simhub.bindings import ncalc
from simhub.model import Layer, LinearGaugeItem, RectangleItem, WidgetItem
from simhub.theme import (
    BRAKE, FASTER, FLAG_BLACK, FLAG_BLUE, FLAG_DIRT, FLAG_GREEN,
    FLAG_INCIDENT, FLAG_OVERLAP, FLAG_PROXIMITY, FLAG_WHITE, FLAG_YELLOW,
    SLOWER, SURFACE_RAISED, TEXT, TEXT_DIM, TEXT_ON_LIGHT, THROTTLE, TILE,
    rounded,
)
from . import layout as grid
from .widgets import CENTER, LEFT, RIGHT, segmented_bar, text, tile

#: O painel arredondado da barra -- o frame de 1329x132 do Figma.
PANEL = grid.Region(grid.MARGIN, grid.MARGIN,
                    grid.TOP_BAR_PANEL_WIDTH, grid.TOP_BAR_PANEL_HEIGHT)

PANEL_RADIUS = 3


def box(x, y, width, height):
    """Retangulo do Figma -> regiao em pixels do painel."""
    return grid.Region(PANEL.x + grid.scaled(x), PANEL.y + grid.scaled(y),
                       grid.scaled(width), grid.scaled(height))


def flip(x, width):
    """Reflete uma coordenada do Figma no eixo vertical do frame."""
    return grid.DESIGN_WIDTH - x - width


def side_box(side, x, y, width, height):
    """`box()` do lado pedido: a direita e o espelho da esquerda."""
    return box(x if side is LEFT else flip(x, width), y, width, height)


# --- Medidas do Figma --------------------------------------------------------

LABEL_SIZE = grid.scaled(13.0)
LABEL = (6.0, 5.0, 113.0, 21.0)

PEDAL_BAR = (40.0, 30.0, 471.0, 18.0)
PEDAL_SEGMENTS = 10
PEDAL_GAP = grid.scaled(4.0)
PEDAL_RADIUS = 3

PEDAL_VALUE = (424.0, 58.0, 113.0, 62.0)
PEDAL_VALUE_SIZE = grid.scaled(50.0)

LEDS = (40.0, 71.0, 229.0, 36.0)

CHIP = (275.0, 71.0, 159.0, 36.0)
CHIP_TEXT_INSET = 4.0
CHIP_TEXT_SIZE = grid.scaled(19.0)
CHIP_RADIUS = 3

CARD = (527.0, 28.0, 289.0, 89.0)
CARD_RADIUS = 7
DELTA_LABEL = (511.0, 56.0, 113.0, 21.0)
BEST_LABEL = (721.0, 56.0, 113.0, 21.0)
DELTA_HERO = (589.0, 24.0, 165.0, 62.0)
DELTA_HERO_SIZE = grid.scaled(40.0)

#: As duas metades da barra do delta e as duas da barra de consistencia. O
#: ponto de corte (672.06) e o centro do cartao.
DELTA_BAR_LEFT = (533.0, 80.0, 135.72, 18.13)
DELTA_BAR_RIGHT = (672.06, 80.0, 137.94, 18.13)
PROGRESS_LEFT = (533.0, 103.47, 135.72, 8.53)
PROGRESS_RIGHT = (672.06, 103.47, 137.94, 8.53)

TICK_LEFT = (533.0, 35.0, 9.0, 40.0)
TICK_RIGHT = (800.0, 35.0, 9.0, 40.0)


def leds(side):
    """Widget RPMLed: os quatro quadrados na ponta externa.

    A instancia direita usa o arquivo espelhado -- mesma logica, vermelho na
    ponta oposta -- para que os dois apontem o vermelho para fora do dash,
    como no Figma.
    """
    from . import rpmled

    area = side_box(side, *LEDS)
    return WidgetItem(
        name="RPMLed" if side is LEFT else "RPMLed2",
        FileName="RPMLed.djson" if side is LEFT else "RPMLedMirrored.djson",
        AutoSize=True,
        AutoSizeScale=area.width / rpmled.WIDTH,
        InitialScreenIndex=0,
        FreezePageChanges=True,
        EnableScreenRolesAndActivation=True,
        NextScreenCommand=0,
        PreviousScreenCommand=0,
        BackgroundColor="#00FFFFFF",
        Left=area.x, Top=area.y,
        Width=area.width, Height=area.height,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def pedal(side, label, prop, color):
    """Entrada do piloto: rotulo na borda externa, fileira fina de dez
    segmentos, e o numero grande encostado no cartao do delta.

    A barra enche do centro para fora nos dois lados, entao o movimento e
    simetrico no canto do olho.
    """
    label_area = side_box(side, *LABEL)
    bar = side_box(side, *PEDAL_BAR)
    value = side_box(side, *PEDAL_VALUE)

    return [
        text(label_area.x, label_area.y, label_area.width, label_area.height,
             label.upper(), name=f"{label} Label", size=LABEL_SIZE,
             color=TEXT_DIM, weight="Bold",
             align=LEFT if side is LEFT else RIGHT),
        *segmented_bar(bar, f"[{prop}]", count=PEDAL_SEGMENTS, color=color,
                       gap=PEDAL_GAP, radius=PEDAL_RADIUS, track=SURFACE_RAISED,
                       name=f"{label} Bar", reverse=(side is LEFT)),
        # Sem binding de Visible: o Figma mostra "00" tambem com o pedal solto.
        text(value.x, value.y, value.width, value.height, "00",
             name=f"{label} Value", size=PEDAL_VALUE_SIZE, color=color,
             weight="Bold", align=CENTER, mono=True,
             char_width=grid.scaled(30.0),
             bindings={"Text": ncalc(f"if([{prop}]=100,'00',[{prop}])")}),
    ]


# --- Chip de aviso -----------------------------------------------------------
#
# Os dez avisos do Figma vivem no mesmo chip, dentro da fileira de LEDs e
# espelhado nos dois lados. Cada um e (nome, rotulo, fundo, cor do texto,
# formula) -- formula None fica declarado e desligado, por nao haver
# propriedade conhecida que o acione.
#
# A ordem importa: irmaos posteriores desenham por cima, entao a lista vai do
# aviso menos urgente para o mais urgente. Se dois acenderem juntos (bandeira
# amarela e carro do lado, por exemplo), o de baixo da lista e o que aparece.

FLAG_PROP = "GameRawData.Telemetry.CarLeftRight"


def flag(name):
    """Bandeira do SimHub -- as propriedades vem como texto 'True'/'False'."""
    return f"if([{name}]='True',1,0)"


#: iRacing expoe a proximidade como enum: 2 carro a esquerda, 3 a direita,
#: 4 dos dois lados, 5 dois carros a esquerda, 6 dois a direita.
def proximity(*values):
    return " || ".join(f"[{FLAG_PROP}]={value}" for value in values)


CHIPS = [
    ("Flag Dirt", "DIRT", FLAG_DIRT, TEXT_ON_LIGHT, None),
    ("Flag Incident", "INCIDENT", FLAG_INCIDENT, TEXT, None),
    ("Flag Overlap", "OVERLAP", FLAG_OVERLAP, TEXT_ON_LIGHT,
     "if([Throttle]>5 && [Brake]>5,1,0)"),
    ("Flag Car Left", "LEFT", FLAG_PROXIMITY, TEXT_ON_LIGHT,
     f"if({proximity(2, 4, 5)},1,0)"),
    ("Flag Car Right", "RIGHT", FLAG_PROXIMITY, TEXT_ON_LIGHT,
     f"if({proximity(3, 4, 6)},1,0)"),
    ("Flag Blue", "BLUE", FLAG_BLUE, TEXT, flag("Flag_Blue")),
    ("Flag Green", "GREEN", FLAG_GREEN, TEXT_ON_LIGHT, flag("Flag_Green")),
    ("Flag White", "WHITE", FLAG_WHITE, TEXT_ON_LIGHT, flag("Flag_White")),
    ("Flag Black", "BLACK", FLAG_BLACK, TEXT, flag("Flag_Black")),
    ("Flag Yellow", "YLW FLAG", FLAG_YELLOW, TEXT_ON_LIGHT,
     flag("Flag_Yellow")),
]

#: Nomes dos chips, na ordem em que aparecem -- consumido pelo preview de
#: modos, que forca um de cada vez.
CHIP_NAMES = [name for name, *_ in CHIPS]


def chip(side, name, label, background, color, formula):
    """Um estado do chip de aviso: pilula colorida com o rotulo dentro."""
    area = side_box(side, *CHIP)
    inset = grid.scaled(CHIP_TEXT_INSET)
    bindings = None
    if formula:
        condition = ncalc(formula)
        bindings = {"Visible": condition, "BlinkEnabled": condition}

    pill = RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=background,
        BorderStyle=rounded(radius=CHIP_RADIUS),
        Left=area.x, Top=area.y, Width=area.width, Height=area.height,
        Visible=bool(formula),
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )
    caption = text(area.x + inset, area.y + inset,
                   area.width - inset * 2, area.height - inset * 2, label,
                   name=f"{name} Label", size=CHIP_TEXT_SIZE, color=color,
                   weight="Bold", align=CENTER, bindings=bindings)
    caption["Visible"] = bool(formula)
    return [pill, caption]


def chips(side):
    """Os dez avisos empilhados no mesmo lugar, um visivel por vez."""
    return Layer(
        *(item for spec in CHIPS for item in chip(side, *spec)),
        name="Alerrts" if side is LEFT else "Alerrts2",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )


# --- Delta -------------------------------------------------------------------

#: Formula do delta: sinal explicito e duas casas, para o numero nao "pular"
#: de largura enquanto o piloto anda.
DELTA_PROP = "[DataCorePlugin.GameData.NewData.DeltaToSessionBest]"
DELTA_TEXT = (
    f"if({DELTA_PROP} < 0, '-' + format(abs({DELTA_PROP}), '0.00'), \r\n\r\n"
    f"if({DELTA_PROP} >= 100, '+' + format({DELTA_PROP}, '0.00'), "
    f"'+' + format({DELTA_PROP}, '0.00')))"
)

PROGRESS_PROP = "PersistantTrackerPlugin.SessionBestLiveDeltaProgressSeconds"


def delta_gauge(name, area, color, maximum, value, *, alignment, radius,
                opacity=None, prop="DeltaToSessionBest"):
    """Uma das barras do delta: cresce do centro para fora, verde quando esta
    mais rapido e vermelho quando mais lento."""
    return LinearGaugeItem(
        name=name,
        IsLinearGauge=True,
        GaugeOrientation=0,
        GaugeAlignment=alignment,
        AutoSize=False,
        GaugeColor=color,
        AlternateGaugeColor=color,
        UseAlternateStyle=False,
        Minimum=0.0, Maximum=maximum, Value=value, Steps=0.0,
        PAW=area.width,
        BackgroundColor="#00FFFFFF",
        BorderStyle=radius,
        Left=area.x, Top=area.y, Width=area.width, Height=area.height,
        Opacity=100.0 if opacity is None else opacity,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Value": ncalc(f"[{prop}]")},
    )


def tick(name, spec, color, bindings=None, visible=True):
    """Marcador vertical nas bordas internas do cartao."""
    area = box(*spec)
    item = RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(radius=2),
        Left=area.x, Top=area.y, Width=area.width, Height=area.height,
        Visible=visible,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )
    return item


def delta():
    """O cartao do delta: rotulos DELTA e BEST, numero-heroi, barra
    bidirecional e a barra de consistencia por baixo."""
    def corners(tl, tr, bl, br):
        return {"RadiusTopLeft": tl, "RadiusTopRight": tr,
                "RadiusBottomLeft": bl, "RadiusBottomRight": br}

    card = box(*CARD)
    label = box(*DELTA_LABEL)
    best = box(*BEST_LABEL)
    hero = box(*DELTA_HERO)

    return Layer(
        tile(card, name="Delta Card", color=SURFACE_RAISED,
             radius=CARD_RADIUS),
        text(label.x, label.y, label.width, label.height, "DELTA",
             name="Delta Label", size=LABEL_SIZE, color=TEXT_DIM,
             weight="Bold", align=CENTER),
        text(best.x, best.y, best.width, best.height, "BEST",
             name="Best Label", size=LABEL_SIZE, color=TEXT_DIM,
             weight="Bold", align=CENTER),
        text(hero.x, hero.y, hero.width, hero.height, "+0.00",
             name="Delta Value", size=DELTA_HERO_SIZE, color=TEXT,
             weight="Bold", align=CENTER, mono=True,
             char_width=grid.scaled(24.0), special_chars=".",
             special_chars_width=grid.scaled(11.0),
             bindings={
                 "Text": ncalc(DELTA_TEXT),
                 "TextColor": ncalc(f"if({DELTA_PROP} < 0, 'SpringGreen', 'Tomato')"),
             }),
        delta_gauge("Delta-Red", box(*DELTA_BAR_LEFT), SLOWER, 0.5, 0.5,
                    alignment=2, radius=corners(6, 1, 1, 1)),
        delta_gauge("Delta-Green", box(*DELTA_BAR_RIGHT), FASTER, -0.5, -0.25,
                    alignment=0, radius=corners(1, 6, 1, 1)),
        delta_gauge("Progress-Red", box(*PROGRESS_LEFT), SLOWER, 0.1, 0.1,
                    alignment=2, radius=corners(1, 1, 6, 1), opacity=80.0,
                    prop=PROGRESS_PROP),
        delta_gauge("Progress-Green", box(*PROGRESS_RIGHT), FASTER, -1.0, -0.1,
                    alignment=0, radius=corners(1, 1, 1, 6), opacity=80.0,
                    prop=PROGRESS_PROP),
        # Os dois marcadores das bordas do cartao. O da esquerda ganha uma
        # segunda passagem em vermelho: e o aviso de volta invalidada.
        tick("Tick Left", TICK_LEFT, TEXT_DIM),
        tick("Tick Right", TICK_RIGHT, TEXT_DIM),
        tick("Invalid Lap", TICK_LEFT, SLOWER, visible=False, bindings={
            "Visible": ncalc("if([LastLapTime] < [BestLapTime] && "
                             "timespantoseconds([LastLapTime]) != 0, 1, 0)")}),
        name="Delta",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )


def layer():
    """A barra superior inteira."""
    return Layer(
        tile(PANEL, name="Background", color=TILE, radius=PANEL_RADIUS),
        Layer(
            leds(LEFT), leds(RIGHT),
            name="LEDs",
            Group=True, Repetitions=0, Visible=True,
            BlinkPhasisInverted=False, RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        Layer(
            *pedal(LEFT, "Brake", "Brake", BRAKE),
            *pedal(RIGHT, "Throttle", "Throttle", THROTTLE),
            name="Gas & Brake",
            Group=True, Repetitions=0, Visible=True,
            BlinkPhasisInverted=False, RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        delta(),
        chips(LEFT), chips(RIGHT),
        name="Top Component",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
