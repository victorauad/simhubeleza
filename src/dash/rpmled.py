"""Widget RPMLed -- os quatro LEDs nas pontas da barra superior.

Geometria do canvas de refino: LEDs de 54x38 com 4 de respiro e chanfro na
diagonal, o mais claro na ponta de fora. O widget e desenhado em pixels e
posicionado pela barra superior praticamente sem escala.

Quatro camadas empilhadas sobre os mesmos 4 slots:

    BG            fundo escuro, sempre visivel
    RPM           rampa azul: cada LED mais claro e com mais brilho que o
                  anterior, conforme o motor sobe
    Shift Light   roxo, ao passar do SLBlinkRPM: trocar a marcha agora
    Shift Light2  ciano, enquanto o pit limiter estiver ligado

As camadas de alerta repetem os 4 slots tres vezes -- nao e redundancia: o
SimHub nao tem efeito de glow, entao passagens borradas sobrepostas formam o
halo e uma passagem final desenha a borda nitida por cima. O brilho da rampa
usa o mesmo truque, com um borrao maior a cada LED.
"""

from simhub.bindings import ncalc
from simhub.dashboard import metadata, screen, shell
from simhub.model import OFF, Layer, RectangleItem
from simhub.theme import (
    CORNER_RADIUS_CHIP, LED_OFF, LIMITER, LIMITER_BORDER, RPM_RAMP, SHIFT,
    SHIFT_BORDER, SURFACE_RAISED, rounded,
)

#: Tamanho nativo, em pixels do dash: quatro LEDs de 54x38 com 4 de respiro.
SLOT_W, SLOT_H = 54.0, 38.0
SLOT_GAP = 4.0
SLOT_COUNT = 4

WIDTH = int(SLOT_W * SLOT_COUNT + SLOT_GAP * (SLOT_COUNT - 1))  # 228
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

#: Por slot, do externo para o interno: cor, borrao do brilho e o RPM que o
#: acende.
#:
#: O motor "cresce" do centro do dash para as bordas: o LED de dentro acende
#: primeiro, em azul escuro e sem brilho; cada LED para fora e mais claro e
#: brilha mais, ate o externo, quase branco. Os limiares sao os do iRacing,
#: por carro.
RPM_SLOTS = [
    (RPM_RAMP[3], 22.0, "PlayerCarSLLastRPM"),
    (RPM_RAMP[2], 14.0, "PlayerCarSLShiftRPM"),
    (RPM_RAMP[1], 8.0, "PlayerCarSLFirstRPM"),
    (RPM_RAMP[0], None, "PlayerCarSLFirstRPM"),
]

BLUR = 20.0
BORDER_THICKNESS = 3
SLOT_RADIUS = CORNER_RADIUS_CHIP


def optional(value):
    """None significa "campo ausente", nao "campo com valor nulo"."""
    return OFF if value is None else value


def slot(x, name, color, opacity=70.0, blur=None, border=None, bindings=None,
         thickness=BORDER_THICKNESS):
    """Um LED da barra."""
    return RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(border, thickness, radius=SLOT_RADIUS),
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
    Assim os dois RPMLed apontam o LED mais claro para fora do dash,
    sem que RPM_SLOTS precise saber de que lado esta.
    """
    if not mirror:
        return SLOT_X
    return [WIDTH - x - SLOT_W for x in SLOT_X]


def background(mirror):
    """Trilho apagado: os LEDs que ainda nao acenderam, com filete."""
    return group("BG", *(
        slot(x, name, LED_OFF, opacity=None, border=SURFACE_RAISED,
             thickness=1)
        for x, name in zip(positions(mirror), PASS_NAMES[0])
    ))


def rpm(mirror):
    """A rampa: um halo borrado atras de cada LED que tem brilho, e o LED
    nitido por cima."""
    rects = []
    for x, name, (color, blur, rpm_property) in zip(
            positions(mirror), PASS_NAMES[0], RPM_SLOTS):
        lit = {"Visible": above(rpm_property)}
        if blur:
            rects.append(slot(x, f"{name} Glow", color, opacity=70.0,
                              blur=blur, bindings=lit))
        rects.append(slot(x, name, color, opacity=None, bindings=lit))
    return group("RPM", *rects)


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
    """Roxo: halo sem borda nas duas primeiras passagens, borda na terceira."""
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
    mesma logica, o LED mais claro na ponta oposta.
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
