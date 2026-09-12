"""Barra superior: RPM, entradas do piloto, delta e alertas.

E a faixa que o piloto le em movimento, sem tirar os olhos da pista, entao
carrega o que muda mais rapido. O wireframe da a ela 1280x116.

Simetria proposital: freio a esquerda, acelerador a direita, delta no meio.
Cada lado tem a mesma estrutura -- barra de LEDs de RPM em cima, barra
segmentada da entrada embaixo, com o valor numerico voltado para o centro.
"""

from simhub.bindings import ncalc
from simhub.model import OFF, Layer, LinearGaugeItem, RectangleItem, WidgetItem
from simhub.theme import (
    ALERT, BACKGROUND, BRAKE, CORNER_RADIUS_TILE, FASTER, FLAG_GREEN,
    FLAG_WHITE, FLAG_YELLOW, FONT, FONT_MONO, RPM_HIGH, RPM_LOW, RPM_MID,
    SIZE_HERO, SIZE_LABEL, SIZE_VALUE, SLOWER, TEXT, TEXT_ON_LIGHT,
    TEXT_SECONDARY, THROTTLE, TILE, alpha, rounded,
)
from . import layout as grid
from .widgets import CENTER, LEFT, RIGHT, caption, ramp, segmented_bar, text, tile

PANEL = grid.TOP_BAR.inset(top=grid.MARGIN, left=grid.MARGIN,
                           right=grid.MARGIN, bottom=4.0)

#: Largura das zonas laterais; o delta ocupa o miolo.
SIDE_WIDTH = 470.0
LED_WIDTH, LED_HEIGHT = 333.0, 49.0

INPUT_SEGMENTS = 14
BAR_HEIGHT = 13.0


def zone(side):
    """Zona lateral, ancorada na borda externa do painel."""
    if side is LEFT:
        return grid.Region(PANEL.x + 8.0, PANEL.y, SIDE_WIDTH, PANEL.height)
    return grid.Region(PANEL.right - SIDE_WIDTH - 8.0, PANEL.y,
                       SIDE_WIDTH, PANEL.height)


def leds(side):
    """Widget RPMLed, centralizado na zona."""
    area = zone(side)
    return WidgetItem(
        name="RPMLed" if side is LEFT else "RPMLed2",
        FileName="RPMLed.djson",
        AutoSize=True,
        AutoSizeScale=1.0,
        InitialScreenIndex=0,
        FreezePageChanges=True,
        EnableScreenRolesAndActivation=True,
        NextScreenCommand=0,
        PreviousScreenCommand=0,
        BackgroundColor="#00FFFFFF",
        Left=area.x + (area.width - LED_WIDTH) / 2,
        Top=area.y + 6.0,
        Width=LED_WIDTH, Height=LED_HEIGHT,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def pedal(side, label, prop, color):
    """Entrada do piloto: rotulo, valor e barra segmentada.

    A barra do freio acende de fora para dentro e a do acelerador de dentro
    para fora, entao as duas crescem em direcao a borda do painel -- o
    movimento fica simetrico no canto do olho.
    """
    area = zone(side)
    inner_side = RIGHT if side is LEFT else LEFT
    bar = grid.Region(area.x, area.y + 64.0, area.width, BAR_HEIGHT)
    label_width = 90.0
    value_width = 86.0

    # Rotulo na borda externa, valor voltado para o centro do painel.
    if side is LEFT:
        label_x, value_x = area.x, area.right - value_width
    else:
        label_x, value_x = area.right - label_width, area.x

    return [
        caption(label_x, area.y + 84.0, label_width, label,
                name=f"{label} Label", color=TEXT_SECONDARY,
                align=LEFT if side is LEFT else RIGHT),
        text(value_x, area.y + 80.0, value_width, 26.0, "00",
             name=f"{label} Value", size=SIZE_LABEL + 9.0, color=color,
             font=FONT_MONO, mono=True, align=inner_side,
             bindings={
                 "Text": ncalc(f"if([{prop}]=100,'00',[{prop}])"),
                 "Visible": ncalc(f"if([{prop}]<1,0,1)"),
             }),
        *segmented_bar(bar, f"[{prop}]", count=INPUT_SEGMENTS,
                       colors=ramp(INPUT_SEGMENTS, [color, color, alpha(color, 100)]),
                       name=f"{label} Bar", reverse=(side is LEFT)),
    ]


DELTA = grid.Region(grid.CENTER.x, PANEL.y, grid.CENTER.width, PANEL.height)

#: Formula do delta: sinal explicito e duas casas, para o numero nao "pular"
#: de largura enquanto o piloto anda.
DELTA_PROP = "[DataCorePlugin.GameData.NewData.DeltaToSessionBest]"
DELTA_TEXT = (
    f"if({DELTA_PROP} < 0, '-' + format(abs({DELTA_PROP}), '0.00'), \r\n\r\n"
    f"if({DELTA_PROP} >= 100, '+' + format({DELTA_PROP}, '0.00'), "
    f"'+' + format({DELTA_PROP}, '0.00')))"
)


def delta_gauge(name, x, y, color, maximum, value, *, alignment, paw, radius,
                opacity=None, prop="DeltaToSessionBest"):
    """Uma das quatro barras finas do delta.

    Geometria preservada do original: ela ja comunica bem -- cresce do centro
    para fora, verde quando esta mais rapido e vermelho quando mais lento. O
    redesign troca so a cor, agora vinda da paleta.
    """
    return LinearGaugeItem(
        name=name,
        IsLinearGauge=True,
        GaugeOrientation=0,
        GaugeAlignment=alignment,
        AutoSize=False,
        GaugeColor=color,
        AlternateGaugeColor=color,
        UseAlternateStyle=False,
        Minimum=0.0, Maximum=maximum, Value=value, Steps=0.0, PAW=paw,
        BackgroundColor="#00FFFFFF",
        BorderStyle=radius,
        Left=x, Top=y, Width=145.0, Height=9.0,
        Opacity=OFF if opacity is None else opacity,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Value": ncalc(f"[{prop}]")},
    )


def delta():
    """Delta para a melhor volta da sessao, com barra de progresso embaixo."""
    def corners(tl, tr, bl, br):
        return {"RadiusTopLeft": tl, "RadiusTopRight": tr,
                "RadiusBottomLeft": bl, "RadiusBottomRight": br}

    progress = "PersistantTrackerPlugin.SessionBestLiveDeltaProgressSeconds"
    return Layer(
        delta_gauge("Delta-Red", 494.0, 15.0, SLOWER, 0.5, 0.5,
                    alignment=2, paw=145.0, radius=corners(10, 1, 1, 1)),
        delta_gauge("Delta-Green", 642.0, 15.0, FASTER, -0.5, -0.25,
                    alignment=0, paw=72.0, radius=corners(1, 10, 1, 1)),
        delta_gauge("Progress-Red", 494.0, 90.0, SLOWER, 0.1, 0.1,
                    alignment=2, paw=145.0, radius=corners(1, 1, 10, 1),
                    opacity=80.0, prop=progress),
        delta_gauge("Progress-Green", 642.0, 90.0, FASTER, -1.0, -0.1,
                    alignment=0, paw=14.0, radius=corners(1, 1, 1, 10),
                    opacity=80.0, prop=progress),
        text(536.0, 21.0, 200.0, 72.0, "-0.43",
             name="Delta Value", size=SIZE_HERO, color=TEXT, weight="ExtraBold",
             font=FONT_MONO, mono=True, align=CENTER,
             char_width=37.0, special_chars=".", special_chars_width=21.0,
             bindings={
                 "Text": ncalc(DELTA_TEXT),
                 "TextColor": ncalc(f"if({DELTA_PROP} < 0, 'SpringGreen', 'Tomato')"),
             }),
        RectangleItem(
            name="Invalid Lap",
            IsRectangleItem=True,
            BackgroundColor=SLOWER,
            BorderStyle=rounded(radius=2),
            Left=495.0, Top=32.0, Width=15.0, Height=50.0,
            Opacity=85.0,
            Visible=True,
            BlinkPhasisInverted=False,
            RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
            bindings={"Visible": ncalc(
                "if([LastLapTime] < [BestLapTime] && "
                "timespantoseconds([LastLapTime]) != 0, 1, 0)")},
        ),
        name="Delta",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )


def banner(name, label, background, color, flag=None):
    """Aviso que cobre a zona esquerda: bandeira, incidente ou clipping."""
    area = zone(LEFT)
    bindings = None
    if flag:
        condition = ncalc(f"if([{flag}]='True',1,0)")
        bindings = {"Visible": condition, "BlinkEnabled": condition}
    item = text(area.x + 10.0, area.y + 14.0, area.width - 20.0, 58.0, label,
                name=name, size=SIZE_VALUE + 6.0, color=color, weight="Bold",
                align=CENTER, bindings=bindings)
    # Sem formula que os acione, os avisos ficam desligados -- do contrario
    # cobririam a barra permanentemente.
    item["Visible"] = bool(flag)
    return item


def alerts():
    """Avisos, empilhados na mesma caixa -- so um aparece por vez."""
    return Layer(
        banner("Incident", "OFF-TRACK", BACKGROUND, ALERT),
        banner("Clipping", "CLIPPING", BACKGROUND, "#FFBF5AF2"),
        banner("Overlaping", "INPUT OVP", BACKGROUND, FLAG_YELLOW),
        banner("Green Flag", "GREEN FLAG", BACKGROUND, FLAG_GREEN, flag="Flag_Green"),
        banner("Yellow Flag", "FLAG AHEAD", BACKGROUND, FLAG_YELLOW, flag="Flag_Yellow"),
        banner("White Flag", "LAST LAP", BACKGROUND, FLAG_WHITE, flag="Flag_White"),
        name="Alerrts",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )


def layer():
    """A barra superior inteira."""
    return Layer(
        tile(PANEL, name="Background", color=TILE, radius=CORNER_RADIUS_TILE),
        Layer(
            *pedal(LEFT, "Brake", "Brake", BRAKE),
            *pedal(RIGHT, "Throttle", "Throttle", THROTTLE),
            name="Gas & Brake",
            Group=True, Repetitions=0, Visible=True,
            BlinkPhasisInverted=False, RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        Layer(
            leds(LEFT), leds(RIGHT),
            name="LEDs",
            Group=True, Repetitions=0, Visible=True,
            BlinkPhasisInverted=False, RenderingSkip=0,
            MinimumRefreshIntervalMS=0.0,
        ),
        delta(),
        alerts(),
        name="Top Component",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )
