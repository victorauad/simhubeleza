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

#: Valores: cinza claro, legivel com o dash reduzido mas sem peso -- o unico
#: branco verdadeiro e a marcha (GEAR), para ela ser a primeira leitura.
TEXT = "#FFB0B6BD"
GEAR = "#FFFFFFFF"
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
#: Pedais: o maior destaque do dash. Cor propria, mais saturada e clara que
#: o verde/vermelho de delta, para nao disputar com nada no painel.
THROTTLE = "#FF2BFF88"
BRAKE = "#FFFF2D2D"

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
# Quinze avisos no mesmo chip, um por vez. Cada um e um par (fundo, texto): o
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
FLAG_CHECKERED = SURFACE_RAISED  # grafite com texto claro: fim da sessao
FLAG_RED = RED                # sessao interrompida
FLAG_REPAIR = "#FF050607"     # meatball: preto com o disco laranja no texto
FLAG_SLOW_CAR = AMBER         # carro lento/parado a frente
FLAG_SPEEDING = CYAN          # ciano do pit: acima do limite no pit lane

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
SIZE_HERO = 50.0              # delta no topo
SIZE_VALUE = 34.0             # valor principal de um tile
SIZE_VALUE_SM = 27.0
SIZE_UNIT = 11.0              # unidade colada ao valor
SIZE_LABEL = 10.5             # rotulo em caixa alta
SIZE_LABEL_SM = 10.0

#: Barra inferior (rodape esquerdo, OTS, setores, New Lap Info). O dash fica
#: reduzido na frente do volante, e a barra e lida de relance: rotulo e valor
#: maiores que no resto do dash, limitados pela largura das fileiras.
SIZE_LABEL_FOOTER = 12.5
SIZE_VALUE_FOOTER = 30.0

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
    # O SimHub le o raio como inteiro: "100.0" derruba o carregamento do dash.
    tl, tr, br, bl = (int(r + 0.5) for r in (tl, tr, br, bl))
    style.update({
        "RadiusTopLeft": tl, "RadiusTopRight": tr,
        "RadiusBottomLeft": bl, "RadiusBottomRight": br,
    })
    return style


def alpha(color, percent):
    """Mesma cor com outra opacidade. Aceita e devolve #AARRGGBB."""
    value = max(0, min(255, round(255 * percent / 100)))
    return f"#{value:02X}{color[3:]}"


#: Pente dos pedais. O vao entre dentes e so um veu sobre o gauge: o aceso
#: le como um bloco quase solido com estrias finas, em vez de dentes soltos.
PEDAL_COMB_GAP = alpha(PANEL, 45)
#: Trilho apagado: fantasma tingido na cor do pedal, bem abaixo do aceso.
THROTTLE_TRACK = alpha(THROTTLE, 9)
BRAKE_TRACK = alpha(BRAKE, 9)

# --- Dash minimal (capsula) --------------------------------------------------
#
# O dash minimal (src/dash/minimal/) usa a mesma paleta, com fundos
# translucidos e sem nenhum desfoque: a capsula a 88%, o box da telemetria
# um degrau mais transparente. Os 45% do canvas ficaram transparentes
# demais no SimHub.

CAPSULE_FILL = alpha(BACKGROUND, 88)
CAPSULE_EDGE = SEPARATOR
TRACE_BOX_FILL = alpha("#FF101216", 75)
TRACE_BOX_EDGE = alpha(TEXT, 18)
#: Trilho dos LEDs apagados, das barras dos pedais e da barra do OTS.
MINI_TRACK = "#FF1A1D21"
#: Rampa dos LEDs de RPM, do primeiro ao ultimo; roxo para trocar a marcha.
MINI_RPM_RAMP = (GREEN, YELLOW, RED)
MINI_SHIFT = SHIFT
#: Aro claro do LED de status na bandeira preta, que sumiria no fundo.
STATUS_RING = "#FFE6E9ED"
#: Filetes do box: grade de 0/50/100% e a linha do "agora" no meio.
TRACE_GRID = alpha(STATUS_RING, 7)
TRACE_NOW = alpha(STATUS_RING, 55)
#: Traco da volta de referencia: a cor do pedal, apagada.
REF_THROTTLE = alpha(THROTTLE, 60)
REF_BRAKE = alpha(BRAKE, 60)
