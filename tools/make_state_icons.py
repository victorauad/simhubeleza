"""Gera os icones dos estados temporarios (assets/images).

    WxSun, WxMoon, WxPartlySun, WxPartlyMoon, WxCloud, WxRain, WxHeavyRain
        condicao do tempo, no estado Weather.
    TrendUp, TrendDown
        seta de tendencia de cada campo do Weather.
    WindArrow
        direcao do vento relativa ao carro, no Weather.

Os desenhos sao do Lucide (lucide.dev, ISC), versionados em
assets/icons/lucide/ com a licenca: traco unico de cantos redondos num
grid de 24. Cada elemento do SVG recebe uma cor do theme, e o traco vem
daqui, nao do arquivo.

Rasterizados uma vez pelo Chromium headless (fundo transparente), no dobro
do tamanho em que aparecem. O headless desconta a moldura da janela da
altura do viewport, entao a captura e feita numa janela folgada e recortada
aqui (decodificador PNG minimo, so stdlib). Os PNGs sao versionados; so rode
de novo se mudar um desenho, uma cor ou um tamanho.

    python3 tools/make_state_icons.py [caminho/do/chromium]
"""

import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash import weather  # noqa: E402
from simhub.theme import ICON, ICON_DIM, ICON_RAIN, ICON_SUN  # noqa: E402

OUT = ROOT / "assets" / "images"
LUCIDE = ROOT / "assets" / "icons" / "lucide"
CHROMIUM = "/opt/pw-browsers/chromium"
OVERSAMPLE = 2

#: Traco do Lucide no grid de 24. Num icone pequeno ele vira menos de um
#: pixel e some, entao engrossa ate MIN_STROKE_PX na tela.
STROKE = 2.0
MIN_STROKE_PX = 2.0


def css(argb):
    """#AARRGGBB -> #RRGGBB."""
    return "#" + argb[3:]


SUN, RAIN, LINE, DIM = css(ICON_SUN), css(ICON_RAIN), css(ICON), css(ICON_DIM)

#: Nome no dash -> (icone do Lucide, cor de cada elemento do SVG, em ordem).
ICONS = {
    "WxSun": ("sun", [SUN] * 9),
    "WxMoon": ("moon", [LINE]),
    "WxPartlySun": ("cloud-sun", [SUN] * 5 + [LINE]),
    "WxPartlyMoon": ("cloud-moon", [LINE, DIM]),
    "WxCloud": ("cloudy", [LINE, DIM]),
    "WxRain": ("cloud-rain", [LINE] + [RAIN] * 3),
    "WxHeavyRain": ("cloud-rain-wind", [LINE] + [RAIN] * 3),
    "TrendUp": ("chevron-up", [DIM]),
    "TrendDown": ("chevron-down", [DIM]),
    "WindArrow": ("arrow-up", [DIM] * 2),  # aponta para cima, gira no dash
}

#: Tamanho em que cada um aparece no dash (px).
DISPLAY = {name: weather.ICON for name in ICONS}
DISPLAY.update(TrendUp=weather.ARROW, TrendDown=weather.ARROW,
               WindArrow=weather.WIND_ARROW)


def body(lucide, colors):
    """Os elementos do SVG do Lucide, cada um com o seu stroke."""
    source = (LUCIDE / f"{lucide}.svg").read_text(encoding="utf-8")
    shapes = re.findall(r"<(?:path|circle|line|polyline|rect)\b[^>]*/>", source)
    assert len(shapes) == len(colors), (
        f"{lucide}: {len(shapes)} elementos, {len(colors)} cores")
    return "".join(shape[:-2].rstrip() + f' stroke="{color}"/>'
                   for shape, color in zip(shapes, colors))


def stroke(size):
    return max(STROKE, MIN_STROKE_PX * 24 / size)


def chunk(kind, data):
    body = kind + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF))


def crop(path, width, height):
    """Recorta o canto superior esquerdo de um PNG RGBA de 8 bits."""
    data = path.read_bytes()
    pos, idat, size = 8, b"", None
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        payload = data[pos + 8:pos + 8 + length]
        if kind == b"IHDR":
            size = struct.unpack(">IIBB", payload[:10])
            assert size[2:] == (8, 6), "esperava RGBA de 8 bits"
        elif kind == b"IDAT":
            idat += payload
        pos += 12 + length
    full_w, full_h = size[0], size[1]
    raw, stride, bpp = zlib.decompress(idat), full_w * 4, 4
    rows, prev = [], bytearray(stride)
    for y in range(full_h):
        kind = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if kind == 1:
                line[i] = (line[i] + a) & 0xFF
            elif kind == 2:
                line[i] = (line[i] + b) & 0xFF
            elif kind == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[i] = (line[i] + pred) & 0xFF
        rows.append(bytes(line))
        prev = line
        if len(rows) == height:
            break
    out = b"".join(b"\x00" + row[:width * 4] for row in rows)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(out, 9))
        + chunk(b"IEND", b""))


def render(name, chromium):
    lucide, colors = ICONS[name]
    px = int(DISPLAY[name] * OVERSAMPLE)
    html = ("<!doctype html><html><body style='margin:0;background:transparent'>"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{px}' height='{px}' "
            f"viewBox='0 0 24 24' fill='none' stroke-width='{stroke(DISPLAY[name])}' "
            "stroke-linecap='round' stroke-linejoin='round'>"
            f"{body(lucide, colors)}</svg></body></html>")
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "icon.html"
        page.write_text(html, encoding="utf-8")
        target = OUT / f"{name}.png"
        subprocess.run(
            [chromium, "--headless", "--no-sandbox", "--disable-gpu",
             "--hide-scrollbars", "--default-background-color=00000000",
             f"--window-size={max(px, 400)},{px + 400}",
             f"--screenshot={target}",
             page.as_uri()],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    crop(target, px, px)
    return target


def main(argv):
    chromium = argv[1] if len(argv) > 1 else CHROMIUM
    missing = set(weather.IMAGES) - set(ICONS)
    assert not missing, f"sem desenho: {missing}"
    for name in ICONS:
        print(render(name, chromium))


if __name__ == "__main__":
    main(sys.argv)
