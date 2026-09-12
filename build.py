#!/usr/bin/env python3
"""Gera a pasta DashTemplates completa a partir do codigo.

Uso:  python3 build.py [destino]

Sem argumento, escreve em build/. Passe o caminho da pasta DashTemplates do
SimHub para instalar direto.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from dash.generated import iracing_dashboard_00 as main_dash  # noqa: E402
from dash.generated import rpmled, telemetry  # noqa: E402
from simhub.build import copy_support_files, write_dashboard  # noqa: E402

DASH_NAME = "iRacing_Dashboard_00"

#: Metadados lidos pelo SimHub para listar o dashboard e dimensionar a janela.
METADATA = {
    "ScreenCount": 1.0,
    "InGameScreensIndexs": [0],
    "IdleScreensIndexs": [],
    "MainPreviewIndex": 0,
    "IsOverlay": False,
    "OverlaySizeWarning": True,
    "MetadataVersion": 2.0,
    "EnableOnDashboardMessaging": True,
    "PitScreensIndexs": [],
    "SimHubVersion": "9.10.6",
    "Category": None,
    "Title": None,
    "Description": None,
    "Author": None,
    "Width": 1280.0,
    "Height": 517.0,
    "DashboardVersion": "",
}

#: Widgets embutidos, referenciados por WidgetItem na tela principal.
WIDGETS = [("RPMLed", rpmled), ("Telemetry", telemetry)]


def main(argv):
    out_root = Path(argv[1]) if len(argv) > 1 else ROOT / "build"
    out_dir = out_root / DASH_NAME

    write_dashboard(
        out_dir, DASH_NAME,
        main_dash.SHELL, main_dash.SCREEN, main_dash.items(),
        metadata=METADATA,
    )
    for name, module in WIDGETS:
        write_dashboard(out_dir, name, module.SHELL, module.SCREEN, module.items())

    copy_support_files(
        out_dir,
        previews=[f"{DASH_NAME}.djson.png", f"{DASH_NAME}.djson.00.png"],
    )

    files = sum(1 for _ in out_dir.rglob("*") if _.is_file())
    print(f"gerado: {out_dir}  ({files} arquivos)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
