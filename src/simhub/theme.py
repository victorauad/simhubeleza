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
TILE = "#FF1C1C1C"            # medido no Figma da barra superior
TILE_RAISED = "#FF2C2C2E"
SEPARATOR = "#FF38383A"

#: Cinza claro do Figma: o cartao do delta e o trilho apagado de qualquer
#: barra segmentada. Mais claro que TILE_RAISED -- e o que separa "espaco que
#: um dado vai ocupar" de "superficie de fundo".
SURFACE_RAISED = "#FF414144"
TRACK = SURFACE_RAISED        # trilho apagado das barras segmentadas

# --- Texto -------------------------------------------------------------------

TEXT = "#FFE5E5E5"            # o Figma nao usa branco puro
TEXT_SECONDARY = "#FF8E8E93"
TEXT_TERTIARY = "#FF636366"
TEXT_ON_LIGHT = "#FF000000"   # sobre a faixa clara da linha do jogador

#: Rotulo apagado do Figma: o mesmo cinza do texto, a 38%. Literal porque
#: `alpha()` so existe no fim do modulo -- e o unico caso.
TEXT_DIM = "#61E5E5E5"

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

ALERT = ORANGE                # off-track, clipping, input overlap

PLAYER = ORANGE               # destaque do jogador no leaderboard
DISCONNECTED = TEXT_TERTIARY

# --- Chips de aviso da barra superior ----------------------------------------
#
# O Figma desenha dez avisos no mesmo chip, um por vez. Cada um e um par
# (fundo, texto): o fundo carrega o significado a distancia, o texto so
# precisa ter contraste em cima dele.
#
# Os hex do proprio Figma nao puderam ser lidos (limite de chamadas do MCP);
# estes vem da paleta do tema, escolhidos pela cor lida do screenshot. Falta
# bater os exatos -- ver ESTADO.md.

FLAG_GREEN = GREEN
FLAG_YELLOW = YELLOW
FLAG_WHITE = "#FFFFFFFF"      # bandeira branca e branco puro, nao o TEXT
FLAG_BLACK = "#FF0A0A0A"
FLAG_BLUE = BLUE
FLAG_DIRT = ORANGE
FLAG_INCIDENT = "#FF8E1B14"   # vermelho fechado: incidente ja levado
FLAG_PROXIMITY = ORANGE       # spotter: carro na esquerda / na direita
FLAG_OVERLAP = ORANGE         # acelerador e freio juntos

# --- Tipografia --------------------------------------------------------------

#: O Figma usa uma familia so, em Bold. Os digitos continuam sem "pular" de
#: largura por `UseMonospacedText` + `CharWidth`, que independem da familia --
#: por isso FONT_MONO nao precisa mais de uma fonte monoespacada de verdade.
FONT = "Inter"
FONT_GEAR = "Inter"
FONT_MONO = "Inter"           # digitos de largura fixa: delta, gaps, tempos

#: Escala de tamanhos. Nomes em vez de literais espalhados pelo layout.
#: Os da barra superior sao os do Figma ja escalados (ver layout.scaled).
SIZE_GEAR = 185.0             # cabe na altura que sobra depois da barra nova
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
