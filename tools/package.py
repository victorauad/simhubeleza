"""Empacota build/iRacing_Dashboard_00 num .simhubdash importavel pelo SimHub.

O SimHub nao le dashboards soltos numa pasta: importa um arquivo unico
.simhubdash (zip com extensao trocada). Os arquivos vao na raiz do zip, sem
uma pasta-mae por cima, preservando subpastas como _SHFonts/ e
JavascriptExtensions/.

Uso:  python3 tools/package.py
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "build" / "iRacing_Dashboard_00"
OUT = ROOT / "build" / "iRacing_Dashboard_00.simhubdash"


def main():
    if not SRC.is_dir():
        sys.exit(f"{SRC} nao existe. Rode 'python3 build.py' primeiro.")

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SRC.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(SRC))

    print(f"gerado {OUT}")


if __name__ == "__main__":
    main()
