"""Variante de diagnostico: o dash com uma faixa de medicao por cima.

Fase 0 do plano de desempenho (docs/otimizacao.md), sem Gerenciador de
Tarefas: o proprio SimHub publica quantas formulas avalia por segundo e
quanto dura o ciclo de dados (docs/propriedades-simhub-completo.md, sec. 2 e
7.2). A faixa cobre o rodape de proposito -- e um dash para medir, nao para
correr. Gerada por `python3 build.py --diag` como um dash separado
(`iRacing_Dashboard_00_Diag`), para coexistir com o normal no SimHub.
"""
from simhub.bindings import ncalc
from simhub.theme import PANEL, TEXT
from simhub.model import Layer

from .widgets import CENTER, text, tile
from . import layout as grid

DASH_NAME = "iRacing_Dashboard_00_Diag"

#: O SimHub identifica o dash pelo Id, nao pelo nome da pasta: com o Id do
#: normal, importar um sobrescreve o outro.
DASH_ID = "a4c4951f-4b07-5bdc-863a-6d138d81e4a5"

#: Atualiza a ~2 Hz: a medicao nao deve pesar no que mede.
SKIP = 30

HEIGHT = 26.0


def _n(prop, fmt="0"):
    return f"format(isnull([{prop}], 0), '{fmt}')"


#: JS/s, NCalc/s (normais + otimizadas), servidas do cache, duracao do ciclo
#: de dados, CPU do processo SimHub e erros no log.
READOUT = (
    f"{_n('DataCorePlugin.Performance_JSFormulasPerSecond')} + ' JS/S   ' + "
    f"{_n('DataCorePlugin.Performance_NALCFormulasPerSecond')} + ' + ' + "
    f"{_n('DataCorePlugin.Performance_NALCOptimizedFormulasPerSecond')} + "
    "' NCALC/S   ' + "
    f"{_n('DataCorePlugin.Performance_CachedFormulasPerSecond')} + "
    "' CACHE/S   ' + "
    f"{_n('DataCorePlugin.Performance_FrameDuration', '0.00')} + ' MS   ' + "
    f"'SIMHUB ' + {_n('SystemInfoPlugin.SimHubProcessor', '0.0')} + '%   ' + "
    f"{_n('DataCorePlugin.LoggingErrorsCount')} + ' ERR'"
)


def layer():
    """A faixa, no pe do dash, por cima de tudo."""
    width = 1280.0
    y = 517.0 - HEIGHT
    area = grid.Region(0.0, y, width, HEIGHT)
    background = tile(area, name="Diag Background", color=PANEL, radius=0,
                      opacity=90.0)
    readout = text(0.0, y, width, HEIGHT, "0 JS/S", name="Diag Readout",
                   size=16.0, color=TEXT, align=CENTER,
                   bindings={"Text": ncalc(READOUT)})
    readout["RenderingSkip"] = SKIP
    return Layer(
        background, readout,
        name="Diag",
        Group=True, Repetitions=0, Visible=True, BlinkPhasisInverted=False,
        RenderingSkip=SKIP, MinimumRefreshIntervalMS=0.0,
    )
