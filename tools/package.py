"""Empacota build/iRacing_Dashboard_00 num .simhubdash importavel pelo SimHub.

O SimHub nao le dashboards soltos numa pasta: importa um arquivo unico
.simhubdash (zip com extensao trocada). Primeira tentativa (arquivos soltos
na raiz do zip) travou na tela de import sem nome/thumbnail, entao os
arquivos vao dentro de uma pasta com o nome do dashboard dentro do zip,
espelhando a estrutura de DashTemplates.

Uso:  python3 tools/package.py
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME = "iRacing_Dashboard_00"
SRC = ROOT / "build" / NAME
OUT = ROOT / "build" / f"{NAME}.simhubdash"


def main():
    if not SRC.is_dir():
        sys.exit(f"{SRC} nao existe. Rode 'python3 build.py' primeiro.")

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(SRC.rglob("*")):
            if path.is_file():
                zf.write(path, Path(NAME) / path.relative_to(SRC))

    print(f"gerado {OUT}")


if __name__ == "__main__":
    main()
