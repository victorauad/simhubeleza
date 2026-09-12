"""Grade do dashboard, derivada do wireframe do Figma.

As regioes do wireframe estavam sobrepostas ao dash real no board, o que deu a
conversao exata de unidades do board para pixels (fator 0,185641). As tres
colunas somam 1280 no ponto.
"""

WIDTH, HEIGHT = 1280.0, 517.0


class Region:
    """Um retangulo da grade, com helpers de posicionamento relativo."""

    def __init__(self, x, y, width, height):
        self.x, self.y = x, y
        self.width, self.height = width, height

    @property
    def right(self):
        return self.x + self.width

    @property
    def bottom(self):
        return self.y + self.height

    def inset(self, top=0.0, right=0.0, bottom=0.0, left=0.0):
        """Regiao menor, recuada por dentro."""
        return Region(self.x + left, self.y + top,
                      self.width - left - right, self.height - top - bottom)

    def at(self, dx=0.0, dy=0.0):
        """Ponto absoluto a partir do canto superior esquerdo da regiao."""
        return self.x + dx, self.y + dy

    def columns(self, count, gutter=0.0):
        """Divide em colunas iguais separadas por gutter."""
        span = (self.width - gutter * (count - 1)) / count
        return [Region(self.x + (span + gutter) * i, self.y, span, self.height)
                for i in range(count)]

    def rows(self, count, gutter=0.0):
        span = (self.height - gutter * (count - 1)) / count
        return [Region(self.x, self.y + (span + gutter) * i, self.width, span)
                for i in range(count)]

    def split_top(self, height, gutter=0.0):
        """Fatia de cima e o resto."""
        top = Region(self.x, self.y, self.width, height)
        rest = Region(self.x, self.y + height + gutter,
                      self.width, self.height - height - gutter)
        return top, rest

    def __repr__(self):
        return (f"Region(x={self.x:.1f}, y={self.y:.1f}, "
                f"w={self.width:.1f}, h={self.height:.1f})")


#: Margem externa do painel. O wireframe deixa ~12px livres no rodape.
MARGIN = 6.0

# --- Barra superior, medida no Figma ----------------------------------------
#
# A revisao da barra veio desenhada em 1329x132 (Figma, section 4317:567). Ela
# entra aqui como o painel arredondado da barra, preservando a margem externa
# que as outras secoes usam -- entao a escala sai da largura, e a altura vem
# junto. Uma constante so: qualquer coordenada do Figma vira pixel do dash
# multiplicando por `SCALE`.

DESIGN_WIDTH, DESIGN_HEIGHT = 1329.0, 132.0

TOP_BAR_PANEL_WIDTH = WIDTH - MARGIN * 2
SCALE = TOP_BAR_PANEL_WIDTH / DESIGN_WIDTH
TOP_BAR_PANEL_HEIGHT = DESIGN_HEIGHT * SCALE

#: Respiro entre a barra e as colunas.
TOP_BAR_GAP = 4.0


def scaled(*values):
    """Converte medidas do Figma (frame de 1329x132) para pixels do dash."""
    out = tuple(value * SCALE for value in values)
    return out[0] if len(out) == 1 else out


#: Grade do wireframe, em pixels do dashboard. Tudo abaixo da barra deriva do
#: rodape dela, entao mexer na altura da barra reposiciona as colunas sozinho.
TOP_BAR = Region(0.0, 0.0, WIDTH,
                 MARGIN + TOP_BAR_PANEL_HEIGHT + TOP_BAR_GAP)

#: O rodape do painel e fixo: a moldura do dash reserva ~12px ali.
BODY_BOTTOM = 505.0
BODY_TOP = TOP_BAR.bottom
BODY_HEIGHT = BODY_BOTTOM - BODY_TOP

#: Altura da faixa inferior -- a mesma para o rodape da esquerda, o OTS e o
#: rodape da direita, que juntos formam uma barra inferior unica. Sai daqui,
#: nao de "o que sobrou" em cada coluna, senao os tres se desalinham a cada
#: mudanca de altura da barra superior.
BOTTOM_BAR_HEIGHT = 86.1

LEFT = Region(0.0, BODY_TOP, 484.0, BODY_HEIGHT)
RIGHT = Region(796.0, BODY_TOP, 484.0, BODY_HEIGHT)
OTS = Region(484.0, BODY_BOTTOM - BOTTOM_BAR_HEIGHT - MARGIN,
             312.1, BOTTOM_BAR_HEIGHT + MARGIN)
CENTER = Region(484.0, BODY_TOP, 312.1, OTS.y - BODY_TOP)
