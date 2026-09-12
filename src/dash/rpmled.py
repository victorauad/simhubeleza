"""Widget RPMLed -- a barra de 5 segmentos nas pontas do dashboard (333x49).

Quatro camadas empilhadas sobre os mesmos 5 slots:

    BG            fundo escuro, sempre visivel
    RPM           preenchimento progressivo em goldenrod conforme o motor sobe
    Shift Light   magenta, ao passar do SLBlinkRPM: trocar a marcha agora
    Shift Light2  ciano, enquanto o pit limiter estiver ligado

As duas camadas de alerta repetem os 5 slots tres vezes. Nao e redundancia: o
SimHub nao tem efeito de glow, entao passagens borradas sobrepostas formam o
halo e uma passagem final desenha a borda nitida por cima.
"""

from simhub.bindings import ncalc
from simhub.dashboard import metadata, screen, shell
from simhub.model import OFF, Layer, RectangleItem
from simhub.theme import (
    LED_OFF, LIMITER, LIMITER_BORDER, RPM_HIGH, RPM_LOW, RPM_MID, SHIFT,
    SHIFT_BORDER, rounded,
)

WIDTH, HEIGHT = 333, 49

#: Posicao X dos 5 slots, da direita para a esquerda -- a ordem em que o editor
#: gravou, preservada para manter paridade com o dashboard original.
SLOT_X = [268.0, 202.0, 136.0, 71.0, 6.0]
SLOT_Y, SLOT_W, SLOT_H = 9.0, 58.0, 30.0

#: Nomes dos retangulos em cada passagem das camadas de alerta: artefatos da
#: duplicacao no editor, sem significado, mantidos para bater com o original.
PASS_NAMES = [
    ["5", "4", "3", "2", "1"],
    ["", "6", "7", "8", "9"],
    ["10", "11", "12", "13", "14"],
]

#: Por slot, da direita para a esquerda: cor e o RPM que o acende.
#:
#: A barra progride verde -> amarelo -> vermelho conforme o motor sobe, como a
#: barra de nivel das referencias. O iRacing expoe os tres limiares por carro,
#: entao o SF23 traz os proprios. Segmentos acesos vao em brilho cheio: a
#: hierarquia vem da cor, nao de uma rampa de opacidade.
RPM_SLOTS = [
    (RPM_HIGH, "PlayerCarSLLastRPM"),
    (RPM_MID, "PlayerCarSLShiftRPM"),
    (RPM_MID, "PlayerCarSLShiftRPM"),
    (RPM_LOW, "PlayerCarSLFirstRPM"),
    (RPM_LOW, "PlayerCarSLFirstRPM"),
]

BLUR = 20.0
BORDER_THICKNESS = 3


def optional(value):
    """None significa "campo ausente", nao "campo com valor nulo"."""
    return OFF if value is None else value


def slot(x, name, color, opacity=70.0, blur=None, border=None, bindings=None):
    """Um segmento da barra."""
    return RectangleItem(
        name=name,
        IsRectangleItem=True,
        BackgroundColor=color,
        BorderStyle=rounded(border, BORDER_THICKNESS),
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
    """As 5 posicoes X, espelhadas quando `mirror` esta ligado.

    Espelhar troca cada slot pelo seu reflexo (`WIDTH - x - SLOT_W`), o que
    inverte a ordem visual da rampa verde -> amarelo -> vermelho sem mexer em
    RPM_SLOTS -- o significado de cada slot continua o mesmo, so a ponta que
    ele ocupa no widget muda de lado. A instancia da direita do painel usa a
    versao espelhada, para que os dois RPMLed apontem o vermelho para dentro
    do dash -- para o centro -- em vez de os dois para o mesmo lado fisico.
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
