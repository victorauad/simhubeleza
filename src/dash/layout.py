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

    def columns(self, count, gutter=0.0, weights=None):
        """Divide em colunas separadas por gutter.

        Sem `weights`, as colunas saem iguais. Com `weights`, cada uma recebe
        uma fatia proporcional do espaco util -- e como um campo se dimensiona
        pelo conteudo dele, nao pela contagem de irmaos. Um valor de tempo
        (`00:00`, cinco glifos) numa fileira de valores de dois digitos corta
        no meio se todo mundo tiver a mesma largura.
        """
        free = self.width - gutter * (count - 1)
        if weights is None:
            weights = [1.0] * count
        elif len(weights) != count:
            raise ValueError(f"weights precisa ter {count} itens")
        total = sum(weights)

        out, x = [], self.x
        for weight in weights:
            span = free * weight / total
            out.append(Region(x, self.y, span, self.height))
            x += span + gutter
        return out

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

    def split_bottom(self, height, gutter=0.0):
        """O resto e a fatia de baixo."""
        rest = Region(self.x, self.y, self.width,
                      self.height - height - gutter)
        bottom = Region(self.x, self.bottom - height, self.width, height)
        return rest, bottom

    def __repr__(self):
        return (f"Region(x={self.x:.1f}, y={self.y:.1f}, "
                f"w={self.width:.1f}, h={self.height:.1f})")


#: Margem externa do painel -- e o respiro entre quaisquer dois blocos. Todo
#: componente que encosta numa borda do dash fica a essa mesma distancia
#: dela, inclusive embaixo.
MARGIN = 6.0

# --- Barra superior ----------------------------------------------------------
#
# Medida no canvas de refino, ja em pixels do dash: duas linhas de 38.16 (os
# pedais em cima; RPM e aviso embaixo) com 12 de respiro interno e 8.6 entre
# elas, e o cartao do delta ocupando as duas no meio.

TOP_BAR_PANEL_WIDTH = WIDTH - MARGIN * 2
TOP_BAR_PANEL_HEIGHT = 108.92

#: Respiro entre a barra e as colunas -- o mesmo da margem.
TOP_BAR_GAP = MARGIN

#: Grade do wireframe, em pixels do dashboard. Tudo abaixo da barra deriva do
#: rodape dela, entao mexer na altura da barra reposiciona as colunas sozinho.
TOP_BAR = Region(0.0, 0.0, WIDTH,
                 MARGIN + TOP_BAR_PANEL_HEIGHT + TOP_BAR_GAP)

BODY_BOTTOM = HEIGHT - MARGIN
BODY_TOP = TOP_BAR.bottom
BODY_HEIGHT = BODY_BOTTOM - BODY_TOP

#: Altura da faixa inferior -- a mesma para o rodape da esquerda, o OTS e o
#: rodape da direita, que juntos formam uma barra inferior unica. Sai daqui,
#: nao de "o que sobrou" em cada coluna, senao os tres se desalinham a cada
#: mudanca de altura da barra superior.
BOTTOM_BAR_HEIGHT = 86.1

LEFT = Region(0.0, BODY_TOP, 484.0, BODY_HEIGHT)
RIGHT = Region(796.0, BODY_TOP, 484.0, BODY_HEIGHT)
OTS = Region(484.0, BODY_BOTTOM - BOTTOM_BAR_HEIGHT,
             312.1, BOTTOM_BAR_HEIGHT)
CENTER = Region(484.0, BODY_TOP, 312.1, OTS.y - BODY_TOP)
