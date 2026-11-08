"""Dash minimal: uma capsula horizontal com o box de telemetria pendurado.

Feito a partir do canvas de design "Dash Minimal -- Capsula". Regras do
design: tudo cabe na capsula, o box fica abaixo dela e encostado, formulas o
mais leves possivel (NCalc com constante onde der) e nenhum desfoque.

    leds.py      arcos de LED de RPM nas pontas, com o LED de status
    capsule.py   fundo, pedais, marcha, velocidade, RPM, OTS, voltas e combustivel
    alerts.py    area de alerta com prioridade, no lugar do cabecalho do OTS
    relative.py  mini relativo (2 a frente, eu, 2 atras)
    trace.py     box de telemetria contra a volta de referencia
    context.py   painel por cima do box: pit e revisao da volta

Gerado ao lado do dash principal por `build.py`, como `SF23_Minimal`.
"""

import uuid

from simhub.dashboard import metadata, screen, shell
from . import alerts, capsule, context, leds, relative, trace
from .base import HEIGHT, WIDTH, group

NAME = "SF23_Minimal"
DASH_ID = str(uuid.uuid5(uuid.NAMESPACE_URL, f"simhubeleza/{NAME}"))

#: Fundo transparente: fora da capsula e do box nao ha nada desenhado.
TRANSPARENT = "#00000000"

METADATA = metadata(WIDTH, HEIGHT, idle_screens=(), overlay_size_warning=True,
                    Category=None, Title=None, Description=None, Author=None)

SHELL = dict(shell(DASH_ID, int(WIDTH), int(HEIGHT), metadata=METADATA),
             BackgroundColor=TRANSPARENT)

SCREEN = screen(str(uuid.uuid5(uuid.NAMESPACE_URL, f"simhubeleza/{NAME}/screen")),
                background=TRANSPARENT, idle=False)


def items():
    """Itens de nivel superior da tela, de tras para a frente."""
    return [
        group(
            "Capsule",
            capsule.background(),
            leds.layer(),
            capsule.pedals(),
            relative.layer(),
            capsule.gear(),
            capsule.ots_layer(alert_active=alerts.ACTIVE),
            alerts.layer(),
            capsule.laps(),
            capsule.fuel(),
            capsule.readouts(),
        ),
        trace.layer(),
        # Por cima do box, so no pit ou logo depois de uma volta de corrida.
        context.layer(),
    ]
