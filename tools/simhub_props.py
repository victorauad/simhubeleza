"""Gera docs/propriedades-simhub-completo.md a partir da instalacao do SimHub.

Le as DLLs do SimHub por reflexao (leitores em C# compilados na hora com o
csc do .NET Framework, em x86, como o SimHub), reconstroi o GameData com a
mesma regra do DataCorePlugin e confere cada nome no servidor web local.

    py tools/simhub_props.py [pasta do SimHub]

Requisitos: Windows, .NET Framework 4 (csc.exe), SimHub aberto com o servidor
web em http://localhost:8888 (sem ele o arquivo sai, mas sem a coluna "Ao vivo").
Com o iRacing aberto fora de sessao, o resultado e o mesmo do arquivo commitado.

Os passos intermediarios (calls.tsv, gamedata_walk.tsv, support_matrix.tsv...)
ficam numa pasta temporaria; use --keep para manter e ver o caminho.
Os utilitarios cs/Members.cs e cs/Dis.cs (listar membros e desmontar IL de um
metodo) sao compilados junto, para investigar o que o gerador nao cobre.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent / "simhub_props"
DEFAULT_SIMHUB = r"C:\Program Files (x86)\SimHub"
CSC = Path(r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe")
TOOLS = ["Scan", "Types", "GDWalk", "Members", "Dis"]


def run(cmd, **kw):
    print(">", " ".join(str(c) for c in cmd))
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    keep = "--keep" in sys.argv
    simhub = args[0] if args else DEFAULT_SIMHUB
    if not CSC.exists():
        sys.exit("csc.exe nao encontrado em " + str(CSC))
    # mkdtemp em %TEMP% da um caminho curto; o csc falha com caminhos longos.
    work = Path(tempfile.mkdtemp(prefix="shprops_"))
    try:
        for t in TOOLS:
            run([CSC, "-nologo", "-platform:x86", "-out:" + str(work / (t + ".exe")), HERE / "cs" / (t + ".cs")], cwd=work)
        run([work / "Scan.exe", simhub, work])
        run([work / "Types.exe", simhub, work / "iracing_raw.txt", "IRacingReader.DataSampleEx=GameRawData"])
        run([work / "GDWalk.exe", simhub, work])
        py = [sys.executable, "-I"]
        with open(work / "regs.txt", "w", encoding="utf-8") as f:
            run(py + [HERE / "regs.py", work], stdout=f)
        run(py + [HERE / "probe.py", simhub, work])
        run(py + [HERE / "gen.py", simhub, work, ROOT / "docs" / "propriedades-simhub-completo.md",
                  ROOT / "docs" / "propriedades.txt"])
    finally:
        if keep:
            print("pasta de trabalho:", work)
        else:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
