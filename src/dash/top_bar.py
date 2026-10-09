"""Barra superior: pedais, RPM, delta e os avisos.

Implementa o refino do canvas de design (referencia Grafite), medido ja em
pixels do dash. Duas linhas de mesma altura correm da borda do painel ate o
cartao do delta, que fica no centro ocupando as duas:

    [pente do freio .............. ][00]  [ DELTA ]  [00][ .......... pente do acelerador]
    [4 LEDs de RPM][chip de aviso    ]    [ cartao ]    [    chip de aviso][4 LEDs de RPM]

O lado direito e o espelho do esquerdo (`side_box`). O pedal enche do centro
para fora nos dois lados, entao o movimento e simetrico no canto do olho.
"""

from simhub.bindings import ncalc
from simhub.model import (
    ImageItem, Layer, LinearGaugeItem, RectangleItem, WidgetItem,
)
from simhub.theme import (
    BRAKE, CORNER_RADIUS_CHIP, CORNER_RADIUS_PANEL, CORNER_RADIUS_TILE,
    FASTER, FLAG_BLACK, FLAG_BLUE, FLAG_DIRT, FLAG_GREEN, FLAG_INCIDENT,
    FLAG_OVERLAP, FLAG_PROXIMITY, FLAG_WHITE, FLAG_YELLOW, PANEL as PANEL_COLOR,
    SIZE_HERO, SIZE_LABEL, SLOWER, SURFACE_RAISED, TEXT, TEXT_DIM,
    TEXT_ON_LIGHT, THROTTLE, TILE, rounded,
)
from . import layout as grid
from .widgets import CENTER, LEFT, RIGHT, text, tile

#: O painel da barra, com a mesma margem de todo o resto do dash.
PANEL = grid.Region(grid.MARGIN, grid.MARGIN,
                    grid.TOP_BAR_PANEL_WIDTH, grid.TOP_BAR_PANEL_HEIGHT)

#: Respiro interno do painel e a altura comum das duas linhas.
INSET = 12.0
ROW_HEIGHT = 38.16
ROW_PEDALS = PANEL.y + INSET
ROW_RPM = PANEL.bottom - INSET - ROW_HEIGHT


def flip(x, width):
    """Reflete uma coordenada x no eixo vertical do dash."""
    return grid.WIDTH - x - width


def side_box(side, x, y, width, height):
    """Regiao do lado pedido; a direita e o espelho da esquerda."""
    return grid.Region(x if side is LEFT else flip(x, width), y, width, height)


# --- Medidas (pixels do dash, lado esquerdo) ---------------------------------

#: Cartao do delta, centrado no dash e com a altura das duas linhas juntas.
CARD_WIDTH = 275.8
CARD = grid.Region((grid.WIDTH - CARD_WIDTH) / 2, ROW_PEDALS,
                   CARD_WIDTH, ROW_RPM + ROW_HEIGHT - ROW_PEDALS)

#: Numero do pedal, encostado no cartao. A Arame Mono tem altura de
#: maiuscula de 0.7 em: em 52 o numero ocupa ~36 dos 38 da linha.
PEDAL_VALUE_WIDTH = 82.0
PEDAL_VALUE_GAP = 9.5
PEDAL_VALUE = (CARD.x - PEDAL_VALUE_GAP - PEDAL_VALUE_WIDTH, ROW_PEDALS,
               PEDAL_VALUE_WIDTH, ROW_HEIGHT)
PEDAL_VALUE_SIZE = 52.0

#: Pente do pedal: da borda interna do painel ate o numero.
PEDAL_BAR = (PANEL.x + INSET, ROW_PEDALS,
             PEDAL_VALUE[0] - 6.0 - (PANEL.x + INSET), ROW_HEIGHT)

#: Mascaras de pente (100 dentes, 1 por ponto percentual) que vao por cima
#: do gauge de cada pedal, do OTS e da barra grossa do delta. Geradas por
#: `tools/make_combs.py` a partir das medidas daqui -- mudou a barra,
#: rode o script de novo.
PEDAL_COMB = {LEFT: "PedalCombLeft", RIGHT: "PedalCombRight"}
DELTA_COMB = "DeltaComb"

#: Quatro LEDs de RPM na ponta externa da linha de baixo; o chip de aviso
#: preenche o resto ate o cartao.
LEDS = (PANEL.x + INSET, ROW_RPM, 228.45, ROW_HEIGHT)
CHIP_GAP = 7.65
CHIP = (LEDS[0] + LEDS[2] + CHIP_GAP, ROW_RPM,
        PEDAL_VALUE[0] + PEDAL_VALUE_WIDTH - (LEDS[0] + LEDS[2] + CHIP_GAP),
        ROW_HEIGHT)
CHIP_TEXT_SIZE = 17.0
CHIP_SLOT_BORDER = "#FF1E2227"

#: Miolo do cartao: rotulos e numero em cima; pente do delta progress e
#: trilho fino do delta absoluto embaixo, alinhados ao rodape.
CARD_INNER = CARD.inset(INSET, INSET, INSET, INSET)
DELTA_ROW = grid.Region(CARD_INNER.x, CARD_INNER.y, CARD_INNER.width, 42.0)
CARD_LABEL_WIDTH = 54.0
THIN_HEIGHT = 3.0
COMB_HEIGHT = 9.0
COMB_GAP = 5.0
THIN_BAR = grid.Region(CARD_INNER.x, CARD_INNER.bottom - THIN_HEIGHT,
                       CARD_INNER.width, THIN_HEIGHT)
COMB = grid.Region(CARD_INNER.x, THIN_BAR.y - COMB_GAP - COMB_HEIGHT,
                   CARD_INNER.width, COMB_HEIGHT)
#: Folga no meio do pente, onde fica o marcador do zero.
COMB_CENTER_GAP = 4.8
MARKER_WIDTH, MARKER_OVERHANG = 2.0, 3.0


def halves(region, gap=0.0):
    """As metades esquerda e direita de uma barra, com `gap` no meio."""
    half = (region.width - gap) / 2
    return (grid.Region(region.x, region.y, half, region.height),
            grid.Region(region.x + half + gap, region.y, half, region.height))


#: Imagens que esta regiao acrescenta ao Images[] do dashboard.
IMAGES = (*PEDAL_COMB.values(), DELTA_COMB)


def leds(side):
    """Widget RPMLed: os quatro LEDs na ponta externa.

    A instancia direita usa o arquivo espelhado -- mesma logica, o LED mais
    claro na ponta oposta -- para que os dois clareiem para fora do dash.
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


def comb_mask(name, image, area):
    """Mascara de pente por cima de um gauge: opaca na cor do fundo, vazada
    nos dentes. So o que esta dentro dos dentes aparece."""
    return ImageItem(
        name=name,
        Image=image,
        AutoSize=False,
        BackgroundColor="#00FFFFFF",
        Left=area.x, Top=area.y, Width=area.width, Height=area.height,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def pedal(side, label, prop, color):
    """Entrada do piloto: pente de 100 dentes (1 por ponto percentual; o da
    dezena e um marcador baixo e escuro, que nao acende) e o numero grande
    encostado no cartao do delta.

    A barra e um gauge continuo entre um trilho e uma mascara: o trilho
    pinta os dentes apagados, o gauge os acesos, e a mascara -- opaca na cor
    do painel, vazada nos dentes -- recorta os dois. Sao tres controles por
    lado, em vez de um retangulo com formula por dente.
    """
    bar = side_box(side, *PEDAL_BAR)
    value = side_box(side, *PEDAL_VALUE)

    return [
        tile(bar, name=f"{label} Track", color=SURFACE_RAISED, radius=0),
        delta_gauge(f"{label} Gauge", bar, color, 100.0, 0.0,
                    alignment=2 if side is LEFT else 0,
                    radius=rounded(radius=0), prop=prop),
        comb_mask(f"{label} Comb", PEDAL_COMB[side], bar),
        # Some com o pedal solto (0) e mostra "00" com ele no fundo (100),
        # para o numero nunca passar de dois digitos.
        text(value.x, value.y, value.width, value.height, "00",
             name=f"{label} Value", size=PEDAL_VALUE_SIZE, color=color,
             weight="Bold", align=CENTER,
             bindings={"Text": ncalc(f"if([{prop}]=100,'00',[{prop}])"),
                       "Visible": ncalc(f"if([{prop}]<1,0,1)")}),
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
    inset = 4.0
    bindings = None
    if formula:
        condition = ncalc(formula)
        bindings = {"Visible": condition, "BlinkEnabled": condition}

    pill = RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=background,
        BorderStyle=rounded(radius=CORNER_RADIUS_CHIP),
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


def chip_slot(side):
    """O lugar do chip quando nao ha aviso: so o contorno, para a linha
    manter o ritmo mesmo vazia."""
    return tile(side_box(side, *CHIP), name="Chip Slot", color="#00FFFFFF",
                radius=CORNER_RADIUS_CHIP, border=CHIP_SLOT_BORDER,
                thickness=1)


def chips(side):
    """Os dez avisos empilhados no mesmo lugar, um visivel por vez."""
    return Layer(
        chip_slot(side),
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


def marker(name, area, color, bindings=None, visible=True):
    """Marcador vertical do zero, no meio do pente."""
    return RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(radius=1),
        Left=area.x, Top=area.y, Width=area.width, Height=area.height,
        Visible=visible,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def delta():
    """O cartao do delta, no mesmo tile do resto do dash: rotulos DELTA e
    BEST nas pontas, numero no meio, e por baixo o pente do delta progress
    e o trilho fino do delta absoluto."""
    label_left = grid.Region(DELTA_ROW.x, DELTA_ROW.y,
                             CARD_LABEL_WIDTH, DELTA_ROW.height)
    label_right = grid.Region(DELTA_ROW.right - CARD_LABEL_WIDTH, DELTA_ROW.y,
                              CARD_LABEL_WIDTH, DELTA_ROW.height)
    hero = DELTA_ROW.inset(left=CARD_LABEL_WIDTH, right=CARD_LABEL_WIDTH)
    comb_left, comb_right = halves(COMB, COMB_CENTER_GAP)
    thin_left, thin_right = halves(THIN_BAR)
    center = CARD.x + CARD.width / 2
    zero = grid.Region(center - MARKER_WIDTH / 2, COMB.y - MARKER_OVERHANG,
                       MARKER_WIDTH, COMB.height + MARKER_OVERHANG * 2)

    return Layer(
        tile(CARD, name="Delta Card", color=TILE, radius=CORNER_RADIUS_TILE),
        text(label_left.x, label_left.y, label_left.width, label_left.height,
             "DELTA", name="Delta Label", size=SIZE_LABEL, color=TEXT_DIM,
             align=LEFT),
        text(label_right.x, label_right.y, label_right.width,
             label_right.height, "BEST", name="Best Label", size=SIZE_LABEL,
             color=TEXT_DIM, align=RIGHT),
        text(hero.x, hero.y, hero.width, hero.height, "+0.00",
             name="Delta Value", size=SIZE_HERO, color=TEXT,
             weight="Bold", align=CENTER,
             bindings={
                 "Text": ncalc(DELTA_TEXT),
                 "TextColor": ncalc(f"if({DELTA_PROP} < 0, '{FASTER}', '{SLOWER}')"),
             }),
        # Pente: delta progress (escala de 0.1 s), saindo do zero no meio.
        # Trilho fino: delta absoluto (escala de 0.5 s). Cada gauge leva a
        # escala da propria fonte de dado.
        tile(COMB, name="Progress Track", color=SURFACE_RAISED, radius=0),
        delta_gauge("Progress-Red", comb_left, SLOWER, 0.1, 0.1,
                    alignment=2, radius=rounded(radius=0),
                    prop=PROGRESS_PROP),
        delta_gauge("Progress-Green", comb_right, FASTER, -1.0, -0.1,
                    alignment=0, radius=rounded(radius=0),
                    prop=PROGRESS_PROP),
        comb_mask("Progress Comb", DELTA_COMB, COMB),
        tile(THIN_BAR, name="Delta Track", color=SURFACE_RAISED, radius=2),
        delta_gauge("Delta-Red", thin_left, SLOWER, 0.5, 0.5,
                    alignment=2, radius=rounded(radius=(2, 0, 0, 2))),
        delta_gauge("Delta-Green", thin_right, FASTER, -0.5, -0.25,
                    alignment=0, radius=rounded(radius=(0, 2, 2, 0))),
        # O zero, por cima do pente. Ganha uma segunda passagem em vermelho:
        # e o aviso de volta invalidada.
        marker("Zero", zero, TEXT),
        marker("Invalid Lap", zero, SLOWER, visible=False, bindings={
            "Visible": ncalc("if([LastLapTime] < [BestLapTime] && "
                             "timespantoseconds([LastLapTime]) != 0, 1, 0)")}),
        name="Delta",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=0, MinimumRefreshIntervalMS=0.0,
    )


def layer():
    """A barra superior inteira."""
    return Layer(
        tile(PANEL, name="Background", color=PANEL_COLOR,
             radius=CORNER_RADIUS_PANEL),
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
