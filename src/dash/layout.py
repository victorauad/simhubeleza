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


#: Grade do wireframe, em pixels do dashboard.
TOP_BAR = Region(0.0, 0.0, 1280.0, 115.8)
LEFT = Region(0.0, 115.8, 484.0, 389.1)
CENTER = Region(484.0, 115.8, 312.1, 297.0)
OTS = Region(484.0, 412.9, 312.1, 92.1)
RIGHT = Region(796.0, 115.8, 484.0, 389.1)

#: Margem externa do painel. O wireframe deixa ~12px livres no rodape.
MARGIN = 6.0
