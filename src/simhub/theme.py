"""Design system do dashboard.

A linguagem visual e a da referencia Grafite (`referencia-design/`), refinada
no canvas de design: fundo grafite, tiles um degrau acima com chanfro na
diagonal, numero grande em Arame Mono colado a uma unidade pequena em cinza,
rotulos em caixa alta, barras em pente cujo restante fica apagado.

Toda cor e todo tamanho do dashboard sai daqui. Nenhum literal de cor deve
aparecer nos modulos de layout.
"""

# --- Superficies -------------------------------------------------------------
#
# Paleta "Grafite" (referencia-design/ e o canvas de refino): grafite quase
# preto, tiles um degrau acima com chanfro, um acento por significado.

BACKGROUND = "#FF0C0E11"      # fundo do dash
PANEL = "#FF121519"           # painel da barra superior, um degrau abaixo do tile
TILE = "#FF181B1F"            # tile: media do gradiente #1C2025 -> #15181C
TILE_RAISED = "#FF1F2328"     # linha de lista, superficie sobre tile
SEPARATOR = "#FF24292F"       # filete entre campos

#: Trilho apagado de qualquer barra -- o espaco que um dado vai ocupar.
SURFACE_RAISED = "#FF23272D"
TRACK = SURFACE_RAISED

# --- Texto -------------------------------------------------------------------

TEXT = "#FFECEEF0"
TEXT_SECONDARY = "#FF9AA0A8"  # rotulos
TEXT_TERTIARY = "#FF6B717A"   # unidades, dado desligado
TEXT_ON_LIGHT = "#FF0A0B0D"   # sobre chip claro (amarelo, branco, laranja)

#: Rotulo da barra superior: o mesmo cinza dos rotulos do resto do dash.
TEXT_DIM = TEXT_SECONDARY

# --- Acentos -----------------------------------------------------------------

GREEN = "#FF34D27B"
YELLOW = "#FFFFD23F"
ORANGE = "#FFFF8A1F"
RED = "#FFFF4B3E"
CYAN = "#FF49C6F5"
BLUE = "#FF2F7BFF"
PURPLE = "#FFB56CFF"
AMBER = "#FFF4A73A"
PINK = "#FFFF375F"

# --- Semantica de corrida ----------------------------------------------------
#
# O acento so comunica se cada cor tiver um significado unico e estavel.

#: Rampa do RPM, do slot interno para o externo: azul que clareia e ganha
#: brilho conforme o motor sobe.
RPM_RAMP = ("#FF1F4FA3", "#FF2B6FE0", "#FF3D8EFF", "#FF8CCBFF")
SHIFT = PURPLE                # trocar a marcha agora
SHIFT_BORDER = "#FFD3A6FF"
LIMITER = CYAN                # pit limiter ligado
LIMITER_BORDER = "#FF9BE2FF"
LED_OFF = "#FF111317"

FASTER = GREEN                # delta e diferenca de volta
SLOWER = RED
THROTTLE = GREEN
BRAKE = RED

OTS_READY = GREEN             # push-to-pass do SF23
OTS_ACTIVE = PURPLE           # piscando
OTS_COOLDOWN = RED
OTS_BLOCKED = TEXT_TERTIARY

ALERT = ORANGE                # off-track, clipping, input overlap

PLAYER = AMBER                # destaque do jogador no leaderboard
DISCONNECTED = TEXT_TERTIARY

#: Brilho atras do disco da marcha, por estado (ver center.gear_glow).
GLOW_SHIFT = "#6BB56CFF"
GLOW_OTS_ACTIVE = "#6134D27B"
GLOW_OTS_COOLDOWN = "#5CFF4B3E"
GLOW_LIMITER = "#4D49C6F5"
GLOW_IDLE = "#3DF4A73A"

#: Brake bias: ambar em repouso, verde/vermelho por um instante quando muda.
BIAS = AMBER
BIAS_UP = GREEN
BIAS_DOWN = RED

# --- Chips de aviso da barra superior ----------------------------------------
#
# Dez avisos no mesmo chip, um por vez. Cada um e um par (fundo, texto): o
# fundo carrega o significado a distancia, o texto so precisa de contraste.

FLAG_GREEN = GREEN
FLAG_YELLOW = YELLOW
FLAG_WHITE = "#FFFFFFFF"      # bandeira branca e branco puro, nao o TEXT
FLAG_BLACK = "#FF050607"
FLAG_BLUE = BLUE
FLAG_DIRT = "#FF8B5E34"       # marrom terra: pista suja
FLAG_INCIDENT = RED           # vermelho: incidente ja levado
FLAG_PROXIMITY = ORANGE       # spotter: carro na esquerda / na direita
FLAG_OVERLAP = "#FFD946EF"    # magenta: acelerador e freio juntos

# --- Tipografia --------------------------------------------------------------

#: Arame Mono e monoespacada de verdade (todo glifo com 0.6 em), entao
#: numeros e rotulos nao "pulam" de largura sem precisar de CharWidth. A
#: marcha usa a mesma fonte dos numeros dos pedais. A Funnel Sans fica para
#: o que e lido como palavra: os nomes dos pilotos.
FONT = "Funnel Sans"
FONT_GEAR = "Arame Mono"
FONT_MONO = "Arame Mono"

#: Largura de um glifo da Arame Mono, em fracao do tamanho da fonte.
MONO_ADVANCE = 0.6

#: Escala de tamanhos. Nomes em vez de literais espalhados pelo layout.
SIZE_GEAR = 170.0
SIZE_HERO = 42.0              # delta no topo
SIZE_VALUE = 34.0             # valor principal de um tile
SIZE_VALUE_SM = 27.0
SIZE_UNIT = 11.0              # unidade colada ao valor
SIZE_LABEL = 10.5             # rotulo em caixa alta
SIZE_LABEL_SM = 10.0

WEIGHT_VALUE = "Bold"
WEIGHT_UNIT = "Normal"
WEIGHT_LABEL = "Normal"

# --- Metricas ----------------------------------------------------------------

CORNER_RADIUS = 5

#: Chanfro dos tiles: dois cantos quase retos e dois arredondados, na
#: diagonal (superior esquerdo, superior direito, inferior direito, inferior
#: esquerdo). E a assinatura da paleta Grafite.
CORNER_RADIUS_TILE = (3, 14, 3, 14)
CORNER_RADIUS_PANEL = (4, 22, 4, 22)
CORNER_RADIUS_CHIP = (3, 10, 3, 10)
GUTTER = 6.0                  # respiro entre tiles
PADDING = 8.0                 # respiro interno de um tile


def rounded(border_color=None, thickness=3, radius=CORNER_RADIUS):
    """BorderStyle com cantos arredondados e borda opcional.

    `radius` e um numero (os quatro cantos iguais) ou uma tupla na ordem do
    CSS: superior esquerdo, superior direito, inferior direito, inferior
    esquerdo.
    """
    style = {}
    if border_color is not None:
        style["BorderColor"] = border_color
        style.update({
            "BorderTop": thickness, "BorderBottom": thickness,
            "BorderLeft": thickness, "BorderRight": thickness,
        })
    tl, tr, br, bl = radius if isinstance(radius, tuple) else (radius,) * 4
    style.update({
        "RadiusTopLeft": tl, "RadiusTopRight": tr,
        "RadiusBottomLeft": bl, "RadiusBottomRight": br,
    })
    return style


def alpha(color, percent):
    """Mesma cor com outra opacidade. Aceita e devolve #AARRGGBB."""
    value = max(0, min(255, round(255 * percent / 100)))
    return f"#{value:02X}{color[3:]}"
