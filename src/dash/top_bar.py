"""Barra superior: acelerador, freio, delta, RPM e alertas.

E a faixa que o piloto le em movimento, sem tirar os olhos da pista, entao
carrega o que muda mais rapido -- e o que muda mais rapido e a entrada do
piloto, nao o RPM (o motor tem sua propria barra de LEDs nas pontas do
volante/cockpit; aqui ela e so um apoio). Por isso acelerador e freio levam o
lugar de maior peso visual -- numero grande, barra alta -- e o RPM fica menor,
abaixo deles.

Simetria proposital: freio a esquerda, acelerador a direita, delta no meio.
Cada lado tem a mesma estrutura -- valor e barra do pedal em cima (dominante),
LEDs de RPM embaixo (apoio).
"""

from simhub.bindings import ncalc
from simhub.model import Layer, LinearGaugeItem, RectangleItem, WidgetItem
from simhub.theme import (
    ALERT, BACKGROUND, BRAKE, CORNER_RADIUS_TILE, FASTER, FLAG_GREEN,
    FLAG_WHITE, FLAG_YELLOW, FONT_MONO, PADDING, SIZE_LABEL, SIZE_VALUE,
    SLOWER, TEXT, TEXT_SECONDARY, THROTTLE, TILE, TILE_RAISED, alpha, rounded,
)

from . import layout as grid
from .widgets import CENTER, LEFT, RIGHT, caption, ramp, segmented_bar, text, tile

PANEL = grid.TOP_BAR.inset(top=grid.MARGIN, left=grid.MARGIN,
                           right=grid.MARGIN, bottom=4.0)

#: Largura das zonas laterais; o delta ocupa o miolo.
SIDE_WIDTH = 470.0

#: RPMLed em apoio: menos da metade do tamanho nativo, encostado no rodape da
#: zona -- o RPM cede o lugar de destaque para o pedal.
LED_SCALE = 0.45
LED_WIDTH, LED_HEIGHT = 333.0 * LED_SCALE, 49.0 * LED_SCALE

INPUT_SEGMENTS = 14
#: Peso grafico do pedal: numero e barra bem maiores que o RPM de apoio --
#: era o inverso antes do redesign (LEDs grandes em cima, pedal pequeno embaixo).
PEDAL_VALUE_SIZE = 32.0
PEDAL_VALUE_HEIGHT = 36.0
BAR_HEIGHT = 16.0


def zone(side):
    """Zona lateral, ancorada na borda externa do painel."""
    if side is LEFT:
        return grid.Region(PANEL.x + 8.0, PANEL.y, SIDE_WIDTH, PANEL.height)
    return grid.Region(PANEL.right - SIDE_WIDTH - 8.0, PANEL.y,
                       SIDE_WIDTH, PANEL.height)


def leds(side):
    """Widget RPMLed, em apoio no rodape da zona.

    A instancia direita usa o arquivo espelhado -- mesma logica, vermelho na
    ponta oposta -- para que os dois LEDs apontem para dentro do dash.
    """
    area = zone(side)
    return WidgetItem(
        name="RPMLed" if side is LEFT else "RPMLed2",
        FileName="RPMLed.djson" if side is LEFT else "RPMLedMirrored.djson",
        AutoSize=True,
        AutoSizeScale=1.0,
        InitialScreenIndex=0,
        FreezePageChanges=True,
        EnableScreenRolesAndActivation=True,
        NextScreenCommand=0,
        PreviousScreenCommand=0,
        BackgroundColor="#00FFFFFF",
        Left=area.x + (area.width - LED_WIDTH) / 2,
        Top=area.bottom - LED_HEIGHT - 4.0,
        Width=LED_WIDTH, Height=LED_HEIGHT,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def pedal(side, label, prop, color):
    """Entrada do piloto: rotulo, valor grande e barra alta -- o elemento
    dominante da zona, no lugar que o RPM ocupava antes do redesign.

    A barra do freio acende de fora para dentro e a do acelerador de dentro
    para fora, entao as duas crescem em direcao a borda do painel -- o
    movimento fica simetrico no canto do olho.
    """
    area = zone(side)
    inner_side = RIGHT if side is LEFT else LEFT
    label_width = 110.0
    value_width = 120.0

    # Rotulo na borda externa, valor voltado para o centro do painel -- igual
    # ao padrao anterior, so que agora em escala bem maior.
    if side is LEFT:
        label_x, value_x = area.x, area.right - value_width
    else:
        label_x, value_x = area.right - label_width, area.x

    # Rotulo, valor e barra empilhados no topo da zona; os LEDs de RPM ficam
    # encostados no rodape, entao a pilha do pedal tem folga ate ali.
    label_y = area.y + 4.0
    value_y = label_y + SIZE_LABEL + 4.0
    bar_y = value_y + PEDAL_VALUE_HEIGHT + 3.0
    bar = grid.Region(area.x, bar_y, area.width, BAR_HEIGHT)

    return [
        caption(label_x, label_y, label_width, label,
                name=f"{label} Label", color=TEXT_SECONDARY,
                align=LEFT if side is LEFT else RIGHT),
        text(value_x, value_y, value_width, PEDAL_VALUE_HEIGHT, "00",
             name=f"{label} Value", size=PEDAL_VALUE_SIZE, color=color,
             font=FONT_MONO, mono=True, align=inner_side,
             bindings={
                 "Text": ncalc(f"if([{prop}]=100,'00',[{prop}])"),
                 "Visible": ncalc(f"if([{prop}]<1,0,1)"),
             }),
        *segmented_bar(bar, f"[{prop}]", count=INPUT_SEGMENTS,
                       colors=ramp(INPUT_SEGMENTS, [color, color, alpha(color, 100)]),
                       name=f"{label} Bar", reverse=(side is LEFT)),
    ]


#: Cartao do delta: uma superficie propria dentro da barra, no padrao das
#: referencias (cada complication vive no proprio tile arredondado).
DELTA_CARD = grid.Region(grid.CENTER.x + 8.0, PANEL.y + 4.0,
                         grid.CENTER.width - 16.0, PANEL.height - 8.0)
DELTA_INNER = DELTA_CARD.inset(top=PADDING, bottom=PADDING,
                               left=PADDING, right=PADDING)

#: Formula do delta: sinal explicito e duas casas, para o numero nao "pular"
#: de largura enquanto o piloto anda.
DELTA_PROP = "[DataCorePlugin.GameData.NewData.DeltaToSessionBest]"
DELTA_TEXT = (
    f"if({DELTA_PROP} < 0, '-' + format(abs({DELTA_PROP}), '0.00'), \r\n\r\n"
    f"if({DELTA_PROP} >= 100, '+' + format({DELTA_PROP}, '0.00'), "
    f"'+' + format({DELTA_PROP}, '0.00')))"
)

DELTA_HERO_SIZE = 34.0
DELTA_HERO_HEIGHT = 40.0
DELTA_BAR_HEIGHT = 10.0
DELTA_PROGRESS_HEIGHT = 4.0
DELTA_GAP = 4.0


def delta_gauge(name, x, y, width, height, color, maximum, value, *,
                alignment, paw, radius, opacity=None, prop="DeltaToSessionBest"):
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
        Minimum=0.0, Maximum=maximum, Value=value, Steps=0.0, PAW=paw,
        BackgroundColor="#00FFFFFF",
        BorderStyle=radius,
        Left=x, Top=y, Width=width, Height=height,
        Opacity=100.0 if opacity is None else opacity,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Value": ncalc(f"[{prop}]")},
    )


def delta():
    """Delta para a melhor volta da sessao -- redesenhado como uma
    complication propria: rotulo em caixa alta, numero-heroi, e a mesma barra
    bidirecional do original (cresce do centro para fora, vermelho para
    atraso e verde para vantagem) com a barra de consistencia por baixo.
    """
    def corners(tl, tr, bl, br):
        return {"RadiusTopLeft": tl, "RadiusTopRight": tr,
                "RadiusBottomLeft": bl, "RadiusBottomRight": br}

    inner = DELTA_INNER
    half = inner.width / 2

    label_y = inner.y
    hero_y = label_y + SIZE_LABEL + 2.0
    bar_y = hero_y + DELTA_HERO_HEIGHT + DELTA_GAP
    progress_y = bar_y + DELTA_BAR_HEIGHT + DELTA_GAP * 0.5

    progress = "PersistantTrackerPlugin.SessionBestLiveDeltaProgressSeconds"
    return Layer(
        tile(DELTA_CARD, name="Delta Card", color=TILE_RAISED,
             radius=CORNER_RADIUS_TILE),
        caption(inner.x, label_y, inner.width, "Delta", name="Delta Label",
                align=CENTER),
        text(inner.x, hero_y, inner.width, DELTA_HERO_HEIGHT, "-0.43",
             name="Delta Value", size=DELTA_HERO_SIZE, color=TEXT,
             weight="ExtraBold", font=FONT_MONO, mono=True, align=CENTER,
             char_width=22.0, special_chars=".", special_chars_width=13.0,
             bindings={
                 "Text": ncalc(DELTA_TEXT),
                 "TextColor": ncalc(f"if({DELTA_PROP} < 0, 'SpringGreen', 'Tomato')"),
             }),
        delta_gauge("Delta-Red", inner.x, bar_y, half, DELTA_BAR_HEIGHT,
                    SLOWER, 0.5, 0.5, alignment=2, paw=half,
                    radius=corners(10, 1, 1, 1)),
        delta_gauge("Delta-Green", inner.x + half, bar_y, half, DELTA_BAR_HEIGHT,
                    FASTER, -0.5, -0.25, alignment=0, paw=half,
                    radius=corners(1, 10, 1, 1)),
        delta_gauge("Progress-Red", inner.x, progress_y, half,
                    DELTA_PROGRESS_HEIGHT, SLOWER, 0.1, 0.1, alignment=2,
                    paw=half, radius=corners(1, 1, 10, 1), opacity=80.0,
                    prop=progress),
        delta_gauge("Progress-Green", inner.x + half, progress_y, half,
                    DELTA_PROGRESS_HEIGHT, FASTER, -1.0, -0.1, alignment=0,
                    paw=half, radius=corners(1, 1, 1, 10), opacity=80.0,
                    prop=progress),
        RectangleItem(
            name="Invalid Lap",
            IsRectangleItem=True,
            BackgroundColor=SLOWER,
            BorderStyle=rounded(radius=2),
            Left=inner.x + 1.0, Top=hero_y, Width=10.0, Height=DELTA_HERO_HEIGHT,
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


#: Nomes dos banners, na ordem em que `alerts()` os declara -- usado pelo
#: preview de modos para forcar um de cada vez (ferramenta de revisao, sem
#: efeito no dashboard real).
BANNER_NAMES = ["Incident", "Clipping", "Overlaping", "Green Flag",
               "Yellow Flag", "White Flag"]


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
