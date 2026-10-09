"""Gera as mascaras de pente das barras da barra superior e do OTS.

Cada barra em pente e um gauge continuo com uma imagem por cima. A imagem e
opaca na cor do fundo e vazada nos dentes, entao o gauge (e o trilho por
baixo dele) so aparece dentro dos dentes.

    PedalCombLeft/Right  freio e acelerador: 100 dentes, 1 por ponto
                         percentual. O dente de cada dezena nao acende: fica
                         pintado na mascara, mais baixo e escuro, demarcando. Os dois enchem do
                         centro para fora, entao as dezenas caem em lugares
                         diferentes em cada um -- por isso duas imagens.
    DeltaComb            delta progress: dentes a cada 4 px saindo do zero,
                         no meio, para os dois lados.
    OtsComb              push-to-pass: dentes a cada 4 px da esquerda.

    python3 tools/make_combs.py

Saida em assets/images/. So stdlib. Mudou a medida de uma barra (em
`dash.top_bar` ou `dash.ots`), rode de novo.
"""

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash import ots, top_bar  # noqa: E402
from simhub.theme import PANEL, TILE  # noqa: E402

#: A imagem sai no dobro da resolucao do dash, para o SimHub reduzir em vez
#: de ampliar (dente nitido em tela de alta densidade).
OVERSAMPLE = 2
TOOTH_WIDTH = 2.0             # px do dash
TOOTH_PITCH = 4.0             # pente do delta e do OTS
PEDAL_TEETH = 100
#: Marcador da dezena: mais baixo que o dente comum (recuado em cima e
#: embaixo) e pintado na mascara, entao nunca acende.
PEDAL_MARK_INSET = 9.0
PEDAL_MARK_COLOR = "#FF353B43"


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


def comb(area, color, teeth, marks=()):
    """Mascara do tamanho de `area`, na cor `color` (#AARRGGBB), vazada nos
    dentes. `teeth` traz (x, inset) de cada dente, em px do dash relativos
    a borda esquerda da area; `inset` encurta o dente em cima e embaixo.
    `marks`, no mesmo formato, sao dentes pintados em PEDAL_MARK_COLOR em
    vez de vazados: marcadores que nao acendem."""
    width = round(area.width * OVERSAMPLE)
    height = round(area.height * OVERSAMPLE)
    a, r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5, 7))
    solid = bytes((r, g, b, a))
    clear = bytes((0, 0, 0, 0))
    tooth = round(TOOTH_WIDTH * OVERSAMPLE)

    def spans(spec):
        out = []              # (x0, x1, y0, y1) de cada dente
        for x, inset in spec:
            x0 = max(0, min(width - tooth, round(x * OVERSAMPLE)))
            y0 = round(inset * OVERSAMPLE)
            out.append((x0, x0 + tooth, y0, height - y0))
        return out

    ma, mr, mg, mb = (int(PEDAL_MARK_COLOR[i:i + 2], 16) for i in (1, 3, 5, 7))
    mark = bytes((mr, mg, mb, ma))
    painted = [(spans(teeth), clear), (spans(marks), mark)]

    rows = []
    for y in range(height):
        row = bytearray(solid * width)
        for boxes, pixel in painted:
            for x0, x1, y0, y1 in boxes:
                if y0 <= y < y1:
                    row[x0 * 4:x1 * 4] = pixel * (x1 - x0)
        rows.append(bytes(row))
    return png(width, height, rows), (width, height)


def pedal_comb(area, major):
    """Dentes comuns vazados na altura toda; a dezena vira marcador."""
    pitch = (area.width - TOOTH_WIDTH) / (PEDAL_TEETH - 1)
    teeth = [(index * pitch, 0.0) for index in range(PEDAL_TEETH)
             if not major(index)]
    marks = [(index * pitch, PEDAL_MARK_INSET) for index in range(PEDAL_TEETH)
             if major(index)]
    return comb(area, PANEL, teeth, marks)


def delta_teeth():
    """Dentes saindo do zero: a metade esquerda cresce para a esquerda, a
    direita para a direita, com a folga do marcador no meio."""
    left, right = top_bar.halves(top_bar.COMB, top_bar.COMB_CENTER_GAP)
    count = int(left.width // TOOTH_PITCH)
    origin = top_bar.COMB.x
    teeth = []
    for index in range(count):
        teeth.append((left.right - TOOTH_WIDTH - index * TOOTH_PITCH - origin, 0.0))
        teeth.append((right.x + index * TOOTH_PITCH - origin, 0.0))
    return teeth


def ots_teeth(area):
    count = int((area.width + TOOTH_PITCH - TOOTH_WIDTH) // TOOTH_PITCH)
    return [(index * TOOTH_PITCH, 0.0) for index in range(count)]


def main():
    pedal = top_bar.side_box(top_bar.LEFT, *top_bar.PEDAL_BAR)
    # Indice 0 e o dente mais a esquerda da imagem. A esquerda (freio) o
    # centro do dash fica na direita da imagem; a direita (acelerador), na
    # esquerda. A dezena e o dente de numero 10, 20, ... contado do centro.
    masks = {
        "PedalCombLeft": pedal_comb(
            pedal, lambda i: (PEDAL_TEETH - i) % 10 == 0),
        "PedalCombRight": pedal_comb(
            pedal, lambda i: (i + 1) % 10 == 0),
        top_bar.DELTA_COMB: comb(top_bar.COMB, TILE, delta_teeth()),
        ots.COMB_IMAGE: comb(ots.COMB_AREA, TILE, ots_teeth(ots.COMB_AREA)),
    }
    out = ROOT / "assets" / "images"
    for name, (data, (width, height)) in masks.items():
        path = out / f"{name}.png"
        path.write_bytes(data)
        print(f"{path.relative_to(ROOT)}  {width}x{height}")


if __name__ == "__main__":
    main()
