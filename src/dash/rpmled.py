"""Widget RPMLed -- os quatro quadrados nas pontas da barra superior.

Geometria do Figma (section 4317:567): quadrados de 53x36 com 6 de respiro,
o vermelho na ponta de fora. O widget e desenhado nessas unidades e escalado
pela barra superior na hora de posicionar.

Quatro camadas empilhadas sobre os mesmos 4 slots:

    BG            fundo escuro, sempre visivel
    RPM           preenchimento progressivo conforme o motor sobe
    Shift Light   magenta, ao passar do SLBlinkRPM: trocar a marcha agora
    Shift Light2  ciano, enquanto o pit limiter estiver ligado

Os dois ultimos sao estados que o Figma desenha explicitamente. As camadas de
alerta repetem os 4 slots tres vezes -- nao e redundancia: o SimHub nao tem
efeito de glow, entao passagens borradas sobrepostas formam o halo e uma
passagem final desenha a borda nitida por cima.
"""

from simhub.bindings import ncalc
from simhub.dashboard import metadata, screen, shell
from simhub.model import OFF, Layer, RectangleItem
from simhub.theme import (
    LED_OFF, LIMITER, LIMITER_BORDER, RPM_HIGH, RPM_LOW, RPM_MID, SHIFT,
    SHIFT_BORDER, rounded,
)

#: Tamanho nativo, nas unidades do Figma: os quatro quadrados de 53x36 a
#: partir de x=40, com 6 de respiro (40, 99, 158, 216). O widget e colocado
#: ja escalado pela barra superior, entao aqui ficam as medidas do desenho.
SLOT_W, SLOT_H = 53.0, 36.0
SLOT_GAP = 6.0
SLOT_COUNT = 4

WIDTH = int(SLOT_W * SLOT_COUNT + SLOT_GAP * (SLOT_COUNT - 1))  # 229
HEIGHT = int(SLOT_H)

#: Posicao X dos slots, do externo (indice 0) para o interno.
SLOT_X = [(SLOT_W + SLOT_GAP) * index for index in range(SLOT_COUNT)]
SLOT_Y = 0.0

#: Nomes dos retangulos em cada passagem das camadas de alerta: artefatos da
#: duplicacao no editor, sem significado, mantidos para bater com o original.
PASS_NAMES = [
    ["4", "3", "2", "1"],
    ["5", "6", "7", "8"],
    ["9", "10", "11", "12"],
]

#: Por slot, do externo para o interno: cor e o RPM que o acende.
#:
#: A rampa do Figma poe o vermelho na ponta de FORA e o verde apontando para o
#: centro do dash, entao o motor "cresce" das bordas para dentro do campo de
#: visao. O iRacing expoe os tres limiares por carro, entao o SF23 traz os
#: proprios. Segmentos acesos vao em brilho cheio: a hierarquia vem da cor,
#: nao de uma rampa de opacidade.
RPM_SLOTS = [
    (RPM_HIGH, "PlayerCarSLLastRPM"),
    (RPM_MID, "PlayerCarSLShiftRPM"),
    (RPM_LOW, "PlayerCarSLFirstRPM"),
    (RPM_LOW, "PlayerCarSLFirstRPM"),
]

BLUR = 20.0
BORDER_THICKNESS = 3
SLOT_RADIUS = 3        # raio do Figma


def optional(value):
    """None significa "campo ausente", nao "campo com valor nulo"."""
    return OFF if value is None else value


def slot(x, name, color, opacity=70.0, blur=None, border=None, bindings=None):
    """Um segmento da barra."""
    return RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(border, BORDER_THICKNESS, radius=SLOT_RADIUS),
        BlurRadius=optional(blur),
        Left=x, Top=SLOT_Y, Width=SLOT_W, Height=SLOT_H,
        Opacity=optional(opacity),
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def group(name, *children, visible=True, bindings=None, freezed=None):
    """Camada agrupadora."""
    return Layer(
        *children,
        name=name,
        Group=True,
        Repetitions=0,
        IsFreezed=optional(freezed),
        Visible=visible,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def above(rpm_property):
    """Acende quando o motor passa do limiar indicado."""
    return ncalc(
        "if(\r\n\r\n[Rpms] > [GameRawData.Telemetry.%s],\r\n\r\n1,0\r\n\r\n)"
        % rpm_property
    )


def positions(mirror):
    """As posicoes X dos slots, espelhadas quando `mirror` esta ligado.

    RPM_SLOTS esta na ordem "do externo para o interno", e sem espelho o slot
    externo cai em x=0 -- a borda esquerda do widget, que e a borda de fora na
    zona esquerda do painel. A zona direita usa a versao espelhada, onde o
    reflexo (`WIDTH - x - SLOT_W`) leva o mesmo slot para a borda direita.
    Assim os dois RPMLed apontam o vermelho para fora do dash, como no Figma,
    sem que RPM_SLOTS precise saber de que lado esta.
    """
    if not mirror:
        return SLOT_X
    return [WIDTH - x - SLOT_W for x in SLOT_X]


def background(mirror):
    """Trilho apagado: os segmentos que ainda nao acenderam."""
    return group("BG", *(
        slot(x, name, LED_OFF, opacity=None)
        for x, name in zip(positions(mirror), PASS_NAMES[0])
    ))


def rpm(mirror):
    return group("RPM", *(
        slot(x, name, color, opacity=None,
             bindings={"Visible": above(rpm_property)})
        for x, name, (color, rpm_property)
        in zip(positions(mirror), PASS_NAMES[0], RPM_SLOTS)
    ))


def glow(name, color, passes, visible_when, mirror, freezed=None):
    """Camada de alerta. `passes` traz (blur, border) de cada passagem."""
    rects = [
        slot(x, rect_name, color, opacity=None, blur=blur, border=border)
        for (blur, border), names in zip(passes, PASS_NAMES)
        for x, rect_name in zip(positions(mirror), names)
    ]
    return group(name, *rects, visible=False, freezed=freezed,
                 bindings={"Visible": visible_when})


def shift_light(mirror):
    """Magenta: halo sem borda nas duas primeiras passagens, borda na terceira."""
    return glow(
        "Shift Light", SHIFT,
        passes=[(BLUR, None), (BLUR, None), (None, SHIFT_BORDER)],
        visible_when=above("PlayerCarSLBlinkRPM"),
        mirror=mirror, freezed=True,
    )


def pit_limiter(mirror):
    """Ciano: borda em todas as passagens, o que engrossa o contorno."""
    return glow(
        "Shift Light2", LIMITER,
        passes=[(BLUR, LIMITER_BORDER), (BLUR, LIMITER_BORDER),
                (None, LIMITER_BORDER)],
        visible_when=ncalc("if([PitLimiterOn] && [DataCorePlugin.GameRunning], 1, 0)"),
        mirror=mirror,
    )


def items(mirror=False):
    """Itens de nivel superior da tela.

    `mirror=True` gera a variante usada pela instancia direita do painel --
    mesma logica, vermelho na ponta oposta.
    """
    return [
        group("LEDs", background(mirror), rpm(mirror), shift_light(mirror)),
        pit_limiter(mirror),
    ]


SHELL = shell(
    "a6a2c114-735c-47df-aa4b-ea64520493e8", WIDTH, HEIGHT,
    metadata=metadata(WIDTH, HEIGHT),
)

SCREEN = screen("ceaed06c-88e6-49dc-8523-984531f72a0e")

#: Arquivo espelhado -- mesmo formato, Id proprio para o SimHub nao confundir
#: os dois widgets embutidos.
SHELL_MIRRORED = shell(
    "b7b3d225-846d-58e0-bb05-fb75631504f9", WIDTH, HEIGHT,
    metadata=metadata(WIDTH, HEIGHT),
)

SCREEN_MIRRORED = screen("dfbfe217-99f7-5ade-9634-a95642e83a0f")
