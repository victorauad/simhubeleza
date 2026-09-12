"""Design system do dashboard.

A linguagem visual vem das referencias do Figma -- complications do watchOS:
fundo preto puro, tiles muito escuros de cantos arredondados, numero grande
colado a uma unidade pequena em cinza, rotulos em caixa alta, barras
segmentadas cujo restante fica apagado.

Toda cor e todo tamanho do dashboard sai daqui. Nenhum literal de cor deve
aparecer nos modulos de layout.
"""

# --- Superficies -------------------------------------------------------------

BACKGROUND = "#FF000000"      # preto puro: o painel some, so os dados brilham
TILE = "#FF1C1C1E"
TILE_RAISED = "#FF2C2C2E"
SEPARATOR = "#FF38383A"
TRACK = "#FF2C2C2E"           # trilho apagado das barras segmentadas

# --- Texto -------------------------------------------------------------------

TEXT = "#FFFFFFFF"
TEXT_SECONDARY = "#FF8E8E93"
TEXT_TERTIARY = "#FF636366"
TEXT_ON_LIGHT = "#FF000000"   # sobre a faixa clara da linha do jogador

# --- Acentos (cores de sistema do watchOS) -----------------------------------

GREEN = "#FF30D158"
YELLOW = "#FFFFD60A"
ORANGE = "#FFFF9F0A"
RED = "#FFFF453A"
CYAN = "#FF64D2FF"
BLUE = "#FF0A84FF"
PURPLE = "#FFBF5AF2"
PINK = "#FFFF375F"

# --- Semantica de corrida ----------------------------------------------------
#
# O acento so comunica se cada cor tiver um significado unico e estavel.

RPM_LOW = GREEN               # o motor sobe: verde -> amarelo -> vermelho
RPM_MID = YELLOW
RPM_HIGH = RED
SHIFT = PURPLE                # trocar a marcha agora
SHIFT_BORDER = "#FFD98CF7"
LIMITER = CYAN                # pit limiter ligado
LIMITER_BORDER = "#FF9BE2FF"
LED_OFF = TRACK

FASTER = GREEN                # delta e diferenca de volta
SLOWER = RED
THROTTLE = GREEN
BRAKE = RED

OTS_READY = GREEN             # push-to-pass do SF23
OTS_ACTIVE = YELLOW
OTS_COOLDOWN = ORANGE
OTS_BLOCKED = TEXT_TERTIARY

FLAG_GREEN = GREEN
FLAG_YELLOW = YELLOW
FLAG_WHITE = TEXT
ALERT = ORANGE                # off-track, clipping, input overlap

PLAYER = ORANGE               # destaque do jogador no leaderboard
DISCONNECTED = TEXT_TERTIARY

# --- Tipografia --------------------------------------------------------------

FONT = "Funnel Sans"
FONT_GEAR = "Audiowide"
FONT_MONO = "Arame Mono"      # digitos de largura fixa: delta, gaps, tempos

#: Escala de tamanhos. Nomes em vez de literais espalhados pelo layout.
SIZE_GEAR = 253.0
SIZE_HERO = 56.0              # delta no topo
SIZE_VALUE = 34.0             # valor principal de um tile
SIZE_VALUE_SM = 25.0
SIZE_UNIT = 15.0              # unidade colada ao valor
SIZE_LABEL = 13.0             # rotulo em caixa alta
SIZE_LABEL_SM = 11.0

WEIGHT_VALUE = "Bold"
WEIGHT_UNIT = "Medium"
WEIGHT_LABEL = "SemiBold"

# --- Metricas ----------------------------------------------------------------

CORNER_RADIUS = 5
CORNER_RADIUS_TILE = 10
GUTTER = 6.0                  # respiro entre tiles
PADDING = 8.0                 # respiro interno de um tile


def rounded(border_color=None, thickness=3, radius=CORNER_RADIUS):
    """BorderStyle com cantos arredondados e borda opcional."""
    style = {}
    if border_color is not None:
        style["BorderColor"] = border_color
        style.update({
            "BorderTop": thickness, "BorderBottom": thickness,
            "BorderLeft": thickness, "BorderRight": thickness,
        })
    style.update({
        "RadiusTopLeft": radius, "RadiusTopRight": radius,
        "RadiusBottomLeft": radius, "RadiusBottomRight": radius,
    })
    return style


def alpha(color, percent):
    """Mesma cor com outra opacidade. Aceita e devolve #AARRGGBB."""
    value = max(0, min(255, round(255 * percent / 100)))
    return f"#{value:02X}{color[3:]}"
