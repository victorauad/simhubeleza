"""Design system do dashboard.

A linguagem visual e a da referencia Grafite (`referencia-design/`), refinada
no canvas de design: fundo grafite, tiles um degrau acima com chanfro na
diagonal, numero grande em Arame Mono colado a uma unidade pequena em cinza,
rotulos em caixa alta, barras em pente cujo restante fica apagado.

Toda cor e todo tamanho do dashboard sai daqui. Nenhum literal de cor deve
aparecer nos modulos de layout.

As cores vem em duas camadas. Os primitivos sao a escala grafite e os
acentos, cada um com um hex. Os papeis (BACKGROUND, TILE, TEXT, FASTER...)
sao apelidos de primitivos, e sao so eles que os modulos de layout importam.
Trocar a aparencia e trocar um primitivo; mudar o que um elemento significa
e reapontar um papel.
"""


def alpha(color, percent):
    """Mesma cor com outra opacidade. Aceita e devolve #AARRGGBB.

    Arredonda meio para cima, como o canvas de design: 30% de 255 da 77.
    """
    value = max(0, min(255, int(255 * percent / 100 + 0.5)))
    return f"#{value:02X}{color[3:]}"


# --- Primitivos: escala grafite ----------------------------------------------
#
# Doze degraus de cinza azulado, do fundo ao branco, com os papeis da escala
# do Radix Colors (radix-ui.com/colors, MIT): 1-2 fundos, 3-5 elementos, 6-8
# bordas, 9-10 texto apagado, 11-12 texto. Os hex sao os da paleta Grafite;
# do Radix vem so a convencao de qual degrau serve para que. Os degraus 1-6
# ficam mais escuros e mais juntos que no Radix: o dash e quase todo fundo.

GRAPHITE_1 = "#FF0C0E11"      # fundo do dash
GRAPHITE_2 = "#FF121519"      # painel, um degrau abaixo do tile
GRAPHITE_3 = "#FF181B1F"      # tile: media do gradiente #1C2025 -> #15181C
GRAPHITE_4 = "#FF1F2328"      # superficie sobre tile
GRAPHITE_5 = "#FF23272D"      # trilho apagado de barra
GRAPHITE_6 = "#FF24292F"      # borda sutil
GRAPHITE_7 = "#FF3A4048"      # borda forte
GRAPHITE_8 = "#FF5F656E"      # sem uso ainda: ponto medio entre 7 e 9
#: Texto apagado: N/A, dado desligado, posicao no leaderboard. Era #6B717A
#: (3.2:1 sobre a linha do leaderboard). Agora 4.5:1 em toda superficie e
#: 5:1 sobre o tile -- o piso de noite da ISO 15008, e a cabine de
#: simulador e noite --, ainda 11 Lc abaixo dos rotulos. Mesmo matiz.
GRAPHITE_9 = "#FF848A93"
GRAPHITE_10 = "#FF9AA0A8"     # texto secundario
#: Texto. Um ponto acima do #B0B6BD do canvas para fechar Lc 60 tambem
#: sobre a superficie elevada (linhas do leaderboard).
GRAPHITE_11 = "#FFB1B7BE"
GRAPHITE_12 = "#FFFFFFFF"     # branco verdadeiro

# --- Superficies -------------------------------------------------------------
#
# Paleta "Grafite" (referencia-design/ e o canvas de refino): grafite quase
# preto, tiles um degrau acima com chanfro, um acento por significado.

BACKGROUND = GRAPHITE_1       # fundo do dash
PANEL = GRAPHITE_2            # painel da barra superior
TILE = GRAPHITE_3
TILE_RAISED = GRAPHITE_4      # linha de lista, superficie sobre tile
SEPARATOR = GRAPHITE_6        # filete entre campos
DIVIDER = GRAPHITE_7          # divisor sob a marcha

#: Trilho apagado de qualquer barra -- o espaco que um dado vai ocupar.
SURFACE_RAISED = GRAPHITE_5
TRACK = SURFACE_RAISED

#: Borda do encaixe do chip de aviso: entre o tile e a superficie sobre ele,
#: fora da escala de proposito -- so contorna o chip apagado.
CHIP_SLOT_BORDER = "#FF1E2227"

# --- Texto -------------------------------------------------------------------

#: Valores: cinza claro, legivel com o dash reduzido mas sem peso -- o unico
#: branco verdadeiro e a marcha (GEAR), para ela ser a primeira leitura.
TEXT = GRAPHITE_11
GEAR = GRAPHITE_12
TEXT_SECONDARY = GRAPHITE_10  # rotulos
TEXT_TERTIARY = GRAPHITE_9    # unidades, N/A, dado desligado
TEXT_ON_LIGHT = "#FF0A0B0D"   # sobre chip claro (amarelo, branco, laranja)

#: Rotulo da barra superior: o mesmo cinza dos rotulos do resto do dash.
TEXT_DIM = TEXT_SECONDARY

# --- Acentos -----------------------------------------------------------------
#
# Um primitivo por matiz, no papel do degrau 9 do Radix (cor solida). Uma
# variante mais clara, quando existe, fica junto do papel que a usa.

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
#: Linha do jogador: ambar translucido com filete ambar, como no canvas.
PLAYER_ROW = alpha(PLAYER, 22)
PLAYER_ROW_EDGE = alpha(PLAYER, 55)
DISCONNECTED = TEXT_TERTIARY

#: Brilho atras do disco da marcha, por estado (ver center.gear_glow).
GLOW_SHIFT = alpha(SHIFT, 42)
GLOW_OTS_ACTIVE = alpha(GREEN, 38)
GLOW_OTS_COOLDOWN = alpha(OTS_COOLDOWN, 36)
GLOW_LIMITER = alpha(LIMITER, 30)
GLOW_IDLE = alpha(AMBER, 24)

#: Brake bias: ambar em repouso, verde/vermelho por um instante quando muda.
BIAS = AMBER
BIAS_UP = GREEN
BIAS_DOWN = RED

#: Icones de traco (Lucide, tools/make_state_icons.py): o traco no cinza dos
#: valores, a parte de tras e as setas um degrau abaixo, e cor so onde ela
#: carrega a condicao -- sol amarelo, chuva ciano.
ICON = GRAPHITE_11
ICON_DIM = GRAPHITE_10
ICON_SUN = YELLOW
ICON_RAIN = CYAN

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

#: Estado que so fica aceso enquanto dura, no mesmo chip dos avisos: fundo
#: tingido do acento, filete e texto no acento, sem piscar. O aviso que pede
#: acao e o chip cheio que pisca -- no pit, PIT LIMITER e o estado e
#: SPEEDING o aviso, os dois em ciano.
LIMITER_BADGE = alpha(LIMITER, 14)

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

#: Escala de tamanhos, por nivel de leitura -- o que o olho pega primeiro:
#:   1. marcha, delta e pedais: uma fixacao, de longe;
#:   2. valor principal de um tile (velocidade, bias, tempos do rodape);
#:   3. valores de lista (leaderboard, lap log, setores);
#:   4. rotulos em caixa alta: nomeiam, nao competem;
#:   5. unidades.
#: O degrau entre niveis vem do tamanho, nao do peso: texto claro sobre
#: escuro ja "sangra", e negrito a mais embola. Rotulo e o piso do que se le
#: em pista, um tamanho so no dash inteiro, e o valor que ele nomeia tem pelo
#: menos 1.5x a altura dele.
SIZE_GEAR = 170.0             # 1
SIZE_HERO = 50.0              # 1: delta no topo
SIZE_VALUE = 34.0             # 2: valor principal de um tile
SIZE_VALUE_SM = 27.0          # 2
SIZE_LABEL = 12.5             # 4: rotulo em caixa alta (era 10.5)
SIZE_UNIT = 11.0              # 5: unidade colada ao valor

#: Barra inferior (rodape esquerdo, OTS, setores, New Lap Info). O dash fica
#: reduzido na frente do volante, e a barra e lida de relance: valor maior
#: que no resto do dash, limitado pela largura das fileiras. O rotulo e o
#: mesmo de todo o dash.
SIZE_LABEL_FOOTER = SIZE_LABEL
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


#: Pente dos pedais. O vao entre dentes e so um veu sobre o gauge: o aceso
#: le como um bloco quase solido com estrias finas, em vez de dentes soltos.
PEDAL_COMB_GAP = alpha(PANEL, 45)
#: Trilho apagado: fantasma tingido na cor do pedal, bem abaixo do aceso.
THROTTLE_TRACK = alpha(THROTTLE, 9)
BRAKE_TRACK = alpha(BRAKE, 9)
