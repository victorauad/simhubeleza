"""Gera as mascaras de pente das barras de freio e acelerador.

A barra de pedal e um gauge continuo com uma imagem por cima. A imagem e
opaca na cor do painel e vazada nos dentes, entao o gauge (e o trilho por
baixo dele) so aparece dentro dos dentes: 100 dentes, um por ponto
percentual, com o dente de cada dezena mais alto.

Os dois lados enchem do centro para fora, entao as dezenas caem em lugares
diferentes em cada um -- por isso sao duas imagens, nao uma espelhada.

    python3 tools/make_pedal_comb.py

Saida: assets/images/PedalCombLeft.png e PedalCombRight.png. So stdlib.
"""

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash import top_bar  # noqa: E402
from simhub.theme import TILE  # noqa: E402

TEETH = 100
#: A imagem sai no dobro da resolucao do dash, para o SimHub reduzir em vez
#: de ampliar (dente nitido em tela de alta densidade).
OVERSAMPLE = 2
TOOTH_WIDTH = 2.0             # px do dash
MINOR_INSET = 0.25            # dente comum: 25% mais curto em cima e embaixo


def png(width, height, rows):
    """PNG RGBA minimo. `rows` e uma lista de bytes, 4 por pixel."""
    def chunk(kind, data):
        body = kind + data
        return (struct.pack(">I", len(data)) + body
                + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))

    raw = b"".join(b"\x00" + row for row in rows)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9))
            + chunk(b"IEND", b""))


def comb(width, height, major_from_center):
    """Mascara: cor do painel com os dentes vazados."""
    a, r, g, b = (int(TILE[i:i + 2], 16) for i in (1, 3, 5, 7))
    solid = bytes((r, g, b, a))
    clear = bytes((0, 0, 0, 0))

    tooth = round(TOOTH_WIDTH * OVERSAMPLE)
    pitch = (width - tooth) / (TEETH - 1)
    inset = round(height * MINOR_INSET)

    holes = []                # (x0, x1, y0, y1) de cada dente
    for index in range(TEETH):
        x0 = round(index * pitch)
        major = major_from_center(index)
        y0, y1 = (0, height) if major else (inset, height - inset)
        holes.append((x0, x0 + tooth, y0, y1))

    rows = []
    for y in range(height):
        row = bytearray(solid * width)
        for x0, x1, y0, y1 in holes:
            if y0 <= y < y1:
                row[x0 * 4:x1 * 4] = clear * (x1 - x0)
        rows.append(bytes(row))
    return png(width, height, rows)


def main():
    area = top_bar.side_box(top_bar.LEFT, *top_bar.PEDAL_BAR)
    width = round(area.width * OVERSAMPLE)
    height = round(area.height * OVERSAMPLE)
    out = ROOT / "assets" / "images"

    # Indice 0 e o dente mais a esquerda da imagem. A esquerda (freio) o
    # centro do dash fica na direita da imagem; a direita (acelerador), na
    # esquerda. A dezena e o dente de numero 10, 20, ... contado do centro.
    sides = {
        "PedalCombLeft": lambda i: (TEETH - i) % 10 == 0,
        "PedalCombRight": lambda i: (i + 1) % 10 == 0,
    }
    for name, major in sides.items():
        path = out / f"{name}.png"
        path.write_bytes(comb(width, height, major))
        print(f"{path.relative_to(ROOT)}  {width}x{height}")


if __name__ == "__main__":
    main()
