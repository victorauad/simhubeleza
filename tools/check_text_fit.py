"""Confere que todo texto fixo cabe na sua caixa.

O SimHub nao mede texto: um rotulo maior que a caixa quebra linha ou vaza
por cima do vizinho, e uma caixa mais baixa que a fonte corta o texto. Na
Arame Mono todo glifo avanca 0.6 em, entao a largura de um texto fixo e
conhecida -- `len(texto) * 0.6 * tamanho`. Os textos com formula ficam de
fora (o conteudo muda em pista); os de outra fonte tambem (proporcionais,
sem metrica aqui).

Rode depois do `build.py`:

    python3 tools/check_text_fit.py        (sai com 1 se algum nao couber)
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from simhub.theme import FONT_MONO, MONO_ADVANCE  # noqa: E402

BUILD = ROOT / "build" / "iRacing_Dashboard_00"
DASHES = ("iRacing_Dashboard_00.djson", "Telemetry.djson")
#: Folga para ruido de float nas larguras derivadas do layout.
TOLERANCE = 0.5


def texts(node, path=""):
    here = f"{path}/{node.get('Name') or ''}"
    if "FontSize" in node:
        yield here, node
    for child in node.get("Childrens") or []:
        yield from texts(child, here)


def main():
    failures = checked = 0
    for filename in DASHES:
        data = json.loads((BUILD / filename).read_text(encoding="utf-8"))
        for screen in data["Screens"]:
            for item in screen["Items"]:
                for path, node in texts(item):
                    content = node.get("Text") or ""
                    if (node.get("Font") != FONT_MONO or not content
                            or "Text" in (node.get("Bindings") or {})):
                        continue
                    checked += 1
                    size = node["FontSize"]
                    need = len(content) * MONO_ADVANCE * size
                    if need > node["Width"] + TOLERANCE:
                        failures += 1
                        print(f"NAO CABE {content!r} em {size} px: "
                              f"{need:.1f} > {node['Width']:.1f}  {path}")
                    if size > node["Height"] + TOLERANCE:
                        failures += 1
                        print(f"BAIXA DEMAIS {content!r} em {size} px: "
                              f"caixa de {node['Height']:.1f}  {path}")
    print(f"{checked} textos fixos conferidos"
          + ("" if not failures else f", {failures} nao cabem"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
