"""Gera os icones dos estados temporarios (assets/images).

    WxSun, WxMoon, WxPartlySun, WxPartlyMoon, WxCloud, WxRain, WxHeavyRain
        condicao do tempo, no estado Weather.
    TrendUp, TrendDown
        seta de tendencia de cada campo do Weather.
    WindArrow
        direcao do vento relativa ao carro, no Weather.

Desenhados em SVG e rasterizados uma vez pelo Chromium headless (fundo
transparente), no dobro do tamanho em que aparecem. O headless desconta a
moldura da janela da altura do viewport, entao a captura e feita numa janela
folgada e recortada aqui (decodificador PNG minimo, so stdlib). Os PNGs sao versionados;
so rode de novo se mudar um desenho ou uma cor.

    python3 tools/make_state_icons.py [caminho/do/chromium]
"""

import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash import weather  # noqa: E402
from simhub.theme import CYAN, TEXT_SECONDARY, YELLOW  # noqa: E402

OUT = ROOT / "assets" / "images"
CHROMIUM = "/opt/pw-browsers/chromium"
OVERSAMPLE = 2


def css(argb):
    """#AARRGGBB -> #RRGGBB."""
    return "#" + argb[3:]


SUN, RAIN = css(YELLOW), css(CYAN)
CLOUD, CLOUD_BACK = "#C3C8CF", "#7D838C"
MOON = "#D7DBE0"


def sun(cx, cy, r, rays=True):
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SUN}"/>']
    if rays:
        import math
        for i in range(8):
            a = i * math.pi / 4
            x1, y1 = cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3)
            x2, y2 = cx + math.cos(a) * (r + 7), cy + math.sin(a) * (r + 7)
            out.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" '
                       f'y2="{y2:.2f}" stroke="{SUN}" stroke-width="2.6" '
                       'stroke-linecap="round"/>')
    return "".join(out)


def moon(cx, cy, r):
    return (f'<mask id="m"><rect width="48" height="48" fill="white"/>'
            f'<circle cx="{cx + r * 0.55}" cy="{cy - r * 0.45}" r="{r * 0.85}" '
            'fill="black"/></mask>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{MOON}" mask="url(#m)"/>')


def cloud(dx=0.0, dy=0.0, fill=CLOUD):
    shapes = [(17, 29, 7), (26, 23, 10), (35, 29, 7)]
    out = [f'<circle cx="{x + dx}" cy="{y + dy}" r="{r}" fill="{fill}"/>'
           for x, y, r in shapes]
    out.append(f'<rect x="{10 + dx}" y="{29 + dy}" width="32" height="7" '
               f'rx="3.5" fill="{fill}"/>')
    return "".join(out)


def drops(count, dy=0.0):
    xs = {3: (17, 25, 33), 5: (13, 19, 25, 31, 37)}[count]
    return "".join(
        f'<line x1="{x + 2}" y1="{36 + dy}" x2="{x - 1}" y2="{43 + dy}" '
        f'stroke="{RAIN}" stroke-width="2.6" stroke-linecap="round"/>'
        for x in xs)


def chevron(up):
    points = "4,15 12,7 20,15" if up else "4,9 12,17 20,9"
    return (f'<polyline points="{points}" fill="none" stroke="{css(TEXT_SECONDARY)}" '
            'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')


def arrow():
    """Seta neutra da direcao do vento: aponta para cima (gira no dash)."""
    color = css(TEXT_SECONDARY)
    return (f'<line x1="12" y1="21" x2="12" y2="5" stroke="{color}" '
            'stroke-width="3" stroke-linecap="round"/>'
            f'<polyline points="6,11 12,4.5 18,11" fill="none" stroke="{color}" '
            'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')


ICONS = {
    "WxSun": (48, sun(24, 24, 9)),
    "WxMoon": (48, moon(24, 24, 13)),
    "WxPartlySun": (48, sun(17, 17, 7) + cloud(3, 4)),
    "WxPartlyMoon": (48, moon(17, 17, 10) + cloud(3, 4)),
    "WxCloud": (48, cloud(-5, -5, CLOUD_BACK) + cloud(3, 3)),
    "WxRain": (48, cloud(0, -6) + drops(3, -4)),
    "WxHeavyRain": (48, cloud(-4, -9, CLOUD_BACK) + cloud(0, -6)
                    + drops(5, -4)),
    "TrendUp": (24, chevron(True)),
    "TrendDown": (24, chevron(False)),
    "WindArrow": (24, arrow()),
}

#: Tamanho em que cada um aparece no dash (px).
DISPLAY = {name: weather.ICON for name in ICONS}
DISPLAY.update(TrendUp=weather.ARROW, TrendDown=weather.ARROW,
               WindArrow=weather.WIND_ARROW)


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


def render(name, view, body, chromium):
    px = int(DISPLAY[name] * OVERSAMPLE)
    html = ("<!doctype html><html><body style='margin:0;background:transparent'>"
            f"<svg xmlns='http://www.w3.org/2000/svg' width='{px}' height='{px}' "
            f"viewBox='0 0 {view} {view}'>{body}</svg></body></html>")
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
    for name, (view, body) in ICONS.items():
        print(render(name, view, body, chromium))


if __name__ == "__main__":
    main(sys.argv)
