#!/usr/bin/env python3
"""Gera a pasta DashTemplates completa a partir do codigo.

Uso:  python3 build.py [--diag] [--name=NOME] [destino]

Sem argumento, escreve em build/. Passe o caminho da pasta DashTemplates do
SimHub para instalar direto. `--diag` gera tambem `iRacing_Dashboard_00_Diag`,
o mesmo dash com a faixa de medicao de desempenho (dash/diag.py).
`--name=NOME` gera so o dash normal com outro nome e outro Id, para instalar
ao lado do atual sem sobrescrever.
"""
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from dash import diag, fallback, fixes, ots, rpmled, top_bar, weather  # noqa: E402
from dash.generated import iracing_dashboard_00 as main_dash  # noqa: E402
from dash.generated import telemetry  # noqa: E402
from simhub.build import (  # noqa: E402
    copy_support_files, image_entry, verify_fonts, write_dashboard,
)

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
#: RPMLedMirrored e o RPMLed com o vermelho na ponta oposta, para a instancia
#: direita do painel apontar para dentro do dash como a esquerda.
WIDGETS = [
    ("RPMLed", rpmled.SHELL, rpmled.SCREEN, rpmled.items()),
    ("RPMLedMirrored", rpmled.SHELL_MIRRORED, rpmled.SCREEN_MIRRORED,
     rpmled.items(mirror=True)),
    ("Telemetry", telemetry.SHELL, telemetry.SCREEN, telemetry.items()),
]


def main(argv):
    names = [a.split("=", 1)[1] for a in argv[1:] if a.startswith("--name=")]
    args = [a for a in argv[1:] if not a.startswith("--")]
    out_root = Path(args[0]) if args else ROOT / "build"
    if names:
        # O SimHub identifica o dash pelo Id e mostra o nome da pasta: outro
        # nome precisa de outro Id, ou a importacao sobrescreve o instalado.
        name = names[0]
        return build(out_root, name,
                     dash_id=str(uuid.uuid5(uuid.NAMESPACE_URL,
                                            f"simhubeleza/{name}")))
    code = build(out_root, DASH_NAME)
    if code == 0 and "--diag" in argv:
        code = build(out_root, diag.DASH_NAME, extra=[diag.layer()],
                     dash_id=diag.DASH_ID)
    return code


def build(out_root, dash_name, extra=(), dash_id=None):
    out_dir = out_root / dash_name

    # Fonte ausente e falha silenciosa no SimHub -- para aqui, nao la.
    missing = verify_fonts(main_dash.items())
    if missing:
        print("fonte referenciada sem arquivo em assets/fonts: "
              + ", ".join(missing), file=sys.stderr)
        return 1

    # Images[] do SHELL vem do dashboard original; as imagens novas do
    # redesign entram aqui, com MD5 e tamanho lidos do arquivo.
    shell = dict(main_dash.SHELL)
    if dash_id:
        shell["Id"] = dash_id
    shell["Images"] = list(main_dash.SHELL["Images"]) + [
        image_entry(name)
        for name in (*top_bar.IMAGES, *ots.IMAGES, *weather.IMAGES)]

    # Nenhum campo de texto fica em branco por falta de dado: vira N/A.
    write_dashboard(
        out_dir, dash_name,
        shell, main_dash.SCREEN,
        fallback.apply(fixes.apply(main_dash.items() + list(extra))),
        metadata=METADATA,
    )
    for name, widget_shell, widget_screen, widget_items in WIDGETS:
        write_dashboard(out_dir, name, widget_shell, widget_screen,
                        fallback.apply(fixes.apply(widget_items)))

    copy_support_files(
        out_dir,
        previews=[f"{DASH_NAME}.djson.png", f"{DASH_NAME}.djson.00.png"],
    )
    if dash_name != DASH_NAME:
        for suffix in (".djson.png", ".djson.00.png"):
            (out_dir / f"{DASH_NAME}{suffix}").rename(
                out_dir / f"{dash_name}{suffix}")

    files = sum(1 for _ in out_dir.rglob("*") if _.is_file())
    print(f"gerado: {out_dir}  ({files} arquivos)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
