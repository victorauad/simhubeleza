"""Confere o contraste das cores de texto do theme sobre cada superficie.

Duas medidas por par: a razao do WCAG 2 e o Lc do APCA 0.0.98G, que e a
que distingue texto claro sobre fundo escuro. Os pisos sao os niveis do
APCA (github.com/Myndex/apca-w3): Lc 60 para texto de conteudo, 45 para
texto grande e pesado, 30 o minimo absoluto. Todo texto tambem passa de
4.5:1 no WCAG (AA para texto pequeno). Os acentos sao cor de barra e
de chip, entao pedem so 3:1 do WCAG (elemento grafico). O rotulo de cada
chip de aviso da barra superior pede 4.5:1 sobre o proprio chip.

    python3 tools/check_contrast.py        (sai com 1 se algum par falhar)
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash import top_bar  # noqa: E402
from simhub import theme  # noqa: E402

SURFACES = ("BACKGROUND", "PANEL", "TILE", "TILE_RAISED")

#: (cor, piso em Lc do APCA)
TEXT_FLOORS = (
    ("GEAR", 90),
    ("TEXT", 60),
    ("TEXT_SECONDARY", 45),
    ("TEXT_TERTIARY", 30),
)

#: Razao minima do WCAG para qualquer cor de texto, em qualquer superficie.
TEXT_RATIO = 4.5

#: Acentos sobre o tile, em razao do WCAG.
ACCENTS = ("GREEN", "YELLOW", "ORANGE", "RED", "CYAN", "BLUE", "PURPLE",
           "AMBER", "PINK", "THROTTLE", "BRAKE")
ACCENT_FLOOR = 3.0


def channels(color):
    """#AARRGGBB -> (r, g, b) em 0..1. O alfa e ignorado: so cores opacas."""
    return tuple(int(color[i:i + 2], 16) / 255 for i in (3, 5, 7))


def blend(color, under, opacity):
    """`color` com `opacity` (0..1) por cima de `under`, opaco."""
    mixed = (round((a * opacity + b * (1 - opacity)) * 255)
             for a, b in zip(channels(color), channels(under)))
    return "#FF" + "".join(f"{c:02X}" for c in mixed)


def wcag_ratio(fg, bg):
    def luminance(color):
        lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
               for c in channels(color)]
        return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
    high, low = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def apca_lc(text, background):
    """Lc do APCA 0.0.98G. Negativo quando o texto e mais claro que o fundo."""
    def y(color):
        r, g, b = (c ** 2.4 for c in channels(color))
        value = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
        return value if value > 0.022 else value + (0.022 - value) ** 1.414
    t, b = y(text), y(background)
    if b > t:
        s = (b ** 0.56 - t ** 0.57) * 1.14
        return 0.0 if s < 0.1 else (s - 0.027) * 100
    s = (b ** 0.65 - t ** 0.62) * 1.14
    return 0.0 if s > -0.1 else (s + 0.027) * 100


def main():
    failures = 0
    for name, floor in TEXT_FLOORS:
        for surface in SURFACES:
            fg, bg = getattr(theme, name), getattr(theme, surface)
            lc, ratio = abs(apca_lc(fg, bg)), wcag_ratio(fg, bg)
            ok = lc >= floor and ratio >= TEXT_RATIO
            failures += not ok
            print(f"{'ok  ' if ok else 'FALHA'} {name:15} sobre {surface:12}"
                  f" Lc {lc:5.1f} (piso {floor})  {ratio:5.2f}:1 "
                  f"(piso {TEXT_RATIO}:1)")
    for name in ACCENTS:
        ratio = wcag_ratio(getattr(theme, name), theme.TILE)
        ok = ratio >= ACCENT_FLOOR
        failures += not ok
        print(f"{'ok  ' if ok else 'FALHA'} {name:15} sobre TILE        "
              f" {ratio:5.2f}:1 (piso {ACCENT_FLOOR}:1)")
    for name, label, hue, ink, _, level in top_bar.CHIPS:
        if level == top_bar.INFO:
            # Tingido: o texto e o acento sobre o painel com o veu do acento.
            ink, chip = hue, blend(hue, theme.PANEL, theme.BADGE_TINT / 100)
        else:
            chip = hue
        ratio = wcag_ratio(ink, chip)
        ok = ratio >= TEXT_RATIO
        failures += not ok
        print(f"{'ok  ' if ok else 'FALHA'} chip {label:11} ({level:7}) "
              f" {ratio:5.2f}:1 (piso {TEXT_RATIO}:1)")
    print("\ntudo ok" if not failures else f"\n{failures} par(es) abaixo do piso")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
