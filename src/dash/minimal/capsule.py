"""O miolo da capsula: fundo, pedais, marcha, velocidade, RPM, OTS e voltas.

    [ freio <======|======> acelerador ]
           52 |  00
    km/h  relativo     MARCHA     OTS READY 094      rpm
    223   (5 linhas)              VOLTA TOTAL STINT  770

Os pedais enchem do centro para fora, como no dash principal, e o valor
fica logo acima da marcha. A marcha e o unico branco verdadeiro; o resto
usa o cinza dos valores.
"""

from simhub.bindings import formatted, ncalc
from simhub.model import GearText, LinearGaugeItem
from simhub.theme import (
    BRAKE, CAPSULE_EDGE, CAPSULE_FILL, FONT, GEAR, MINI_TRACK, TEXT,
    TEXT_SECONDARY, THROTTLE, rounded,
)
from .. import ots
from ..widgets import CENTER, LEFT, RIGHT, text
from .base import CAPSULE, RADIUS, SKIP_SLOW, Region, group, rect

# --- Medidas (pixels do canvas) ----------------------------------------------

PEDALS = Region(120.0, 9.0, 657.0, 14.0)
PEDAL_GAP = 4.0
PEDAL_RADIUS = 3
BRAKE_VALUE = Region(363.0, 29.0, 84.0, 34.0)
THROTTLE_VALUE = Region(455.0, 29.0, 84.0, 34.0)
SIZE_PEDAL = 34.0

GEAR_BOX = Region(364.0, 54.0, 170.0, 170.0)
SIZE_GEAR = 176.0

SIZE_READOUT = 44.0
SIZE_READOUT_LABEL = 11.0
SPEED = Region(40.0, 87.0, 80.0, SIZE_READOUT)
SPEED_LABEL = Region(40.0, 134.0, 40.0, 14.0)
RPM = Region(778.0, 90.0, 80.0, SIZE_READOUT)
RPM_LABEL = Region(818.0, 137.0, 40.0, 14.0)

#: OTS: "OTS READY" e a barra a esquerda, os segundos na mesma altura do
#: rotulo, a direita.
OTS_HEADER = Region(522.0, 70.0, 140.0, 20.0)
SIZE_OTS_HEADER = 17.0
OTS_SECONDS = Region(671.0, 68.0, 75.0, 30.0)
SIZE_OTS_SECONDS = 30.0
OTS_BAR = Region(522.0, 94.0, 205.0, 9.0)

#: Voltas, abaixo do OTS: a base dos numeros alinha com a base da marcha.
LAP_LABEL_Y, LAP_VALUE_Y = 165.0, 181.0
SIZE_LAP_LABEL, SIZE_LAP_VALUE = 10.0, 22.0
LAP_COLUMNS = [  # (x, largura, alinhamento)
    (522.0, 70.0, CENTER),
    (600.0, 70.0, CENTER),
    (662.0, 70.0, RIGHT),
]


def frame(region):
    """(x, y, largura, altura), na ordem que `text()` recebe."""
    return region.x, region.y, region.width, region.height


def background():
    return rect("Capsule", CAPSULE, CAPSULE_FILL, radius=RADIUS,
                border=CAPSULE_EDGE, thickness=1)


# --- Pedais ------------------------------------------------------------------

def gauge(name, region, color, prop, alignment):
    return LinearGaugeItem(
        name=name,
        IsLinearGauge=True,
        GaugeOrientation=0,
        GaugeAlignment=alignment,
        AutoSize=False,
        GaugeColor=color,
        AlternateGaugeColor=color,
        UseAlternateStyle=False,
        Minimum=0.0, Maximum=100.0, Value=50.0, Steps=0.0,
        PAW=region.width,
        BackgroundColor="#00FFFFFF",
        BorderStyle=rounded(radius=PEDAL_RADIUS),
        Left=region.x, Top=region.y, Width=region.width, Height=region.height,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Value": ncalc(f"[{prop}]")},
    )


def pedal_value(name, region, prop, color, align):
    """Valor do pedal em 2 digitos: some solto (arredonda para 0) e o fundo,
    que arredondaria para 100, vira "00"."""
    return text(region.x, region.y, region.width, region.height, "00",
                name=name, size=SIZE_PEDAL, color=color, align=align,
                bindings={
                    "Text": ncalc(f"if([{prop}]>=99.5,'00',format([{prop}],'00'))"),
                    "Visible": ncalc(f"if([{prop}]<0.5,0,1)"),
                })


def pedals():
    half = (PEDALS.width - PEDAL_GAP) / 2
    brake = Region(PEDALS.x, PEDALS.y, half, PEDALS.height)
    throttle = Region(PEDALS.x + half + PEDAL_GAP, PEDALS.y, half, PEDALS.height)
    return group(
        "Pedals",
        rect("Brake Track", brake, MINI_TRACK, radius=PEDAL_RADIUS),
        gauge("Brake", brake, BRAKE, "Brake", alignment=2),
        rect("Throttle Track", throttle, MINI_TRACK, radius=PEDAL_RADIUS),
        gauge("Throttle", throttle, THROTTLE, "Throttle", alignment=0),
        pedal_value("Brake Value", BRAKE_VALUE, "Brake", BRAKE, RIGHT),
        pedal_value("Throttle Value", THROTTLE_VALUE, "Throttle", THROTTLE, LEFT),
    )


# --- Marcha, velocidade e RPM ------------------------------------------------

def gear():
    return GearText(
        name="Gear",
        GearBlinkText=False,
        GearBlinkDelay=100,
        TextColor=GEAR,
        BackgroundColor="#00FFFFFF",
        GearBackgoundColor="#00FFFFFF",
        IgnoreNeutralGear=False,
        GearBlinkBackgroundColor="#FFFF4500",
        GearBlinkBackground=False,
        GearTextColor=GEAR,
        GearBlinkTextColor="#FFFF00FF",
        DesignerText="6",
        NoDataText="N",
        IsTextItem=True,
        Font="Arame Mono",
        FontWeight="Bold",
        FontSize=SIZE_GEAR,
        HorizontalAlignment=CENTER,
        VerticalAlignment=CENTER,
        Left=GEAR_BOX.x, Top=GEAR_BOX.y,
        Width=GEAR_BOX.width, Height=GEAR_BOX.height,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )


def readout(name, value, label, caption, sample, expression, align):
    return [
        text(value.x, value.y, value.width, value.height, sample, name=name,
             size=SIZE_READOUT, color=TEXT, align=align,
             bindings={"Text": formatted(expression, "0")}),
        text(label.x, label.y, label.width, label.height, caption,
             name=f"{name} Label", size=SIZE_READOUT_LABEL,
             color=TEXT_SECONDARY, align=align, font=FONT),
    ]


def readouts():
    return group(
        "Speed & RPM",
        *readout("Speed", SPEED, SPEED_LABEL, "KM/H", "223", "[SpeedKmh]", LEFT),
        # RPM dividido por 10: 8450 vira 845.
        *readout("Rpm", RPM, RPM_LABEL, "RPM", "770", "[Rpms]/10", RIGHT),
    )


# --- OTS ---------------------------------------------------------------------

#: Mesmo criterio do dash principal (`ots.state_formula`): no box o
#: componente inteiro some.
OTS_HIDDEN = "[DahlDesign.PitBoxPosition] > 0"


def ots_layer():
    """Push-to-pass com as cores e a cascata de estados do dash principal:
    verde pronto, roxo piscando ativo, vermelho recarregando (os segundos
    passam a contar a recarga), cinza indisponivel."""
    seconds = text(*frame(OTS_SECONDS), "094", name="OTS Seconds",
                   size=SIZE_OTS_SECONDS, align=LEFT,
                   bindings={"Text": ncalc(ots.SECONDS),
                             "TextColor": ncalc(ots.COLOR),
                             "BlinkEnabled": ncalc(ots.ACTIVE_BLINK)})
    header = text(*frame(OTS_HEADER), "OTS READY", name="OTS State",
                  size=SIZE_OTS_HEADER, align=LEFT, font=FONT,
                  bindings={"Text": ncalc(f"'OTS ' + {ots.LABEL}"),
                            "TextColor": ncalc(ots.COLOR),
                            "BlinkEnabled": ncalc(ots.ACTIVE_BLINK)})
    bar = gauge("OTS Gauge", OTS_BAR, ots.READY, "DahlDesign.SF23.OTTimeLeft",
                alignment=0)
    bar.update(Maximum=ots.CAPACITY, Value=94.0,
               BorderStyle=rounded(radius=2))
    bar["Bindings"]["GaugeColor"] = ncalc(ots.COLOR)
    return group(
        "OTS",
        header, seconds,
        rect("OTS Track", OTS_BAR, MINI_TRACK, radius=2),
        bar,
        bindings={"Visible": ncalc(f"if({OTS_HIDDEN}, 0, 1)")},
    )


# --- Voltas ------------------------------------------------------------------

LAPS = [
    ("Lap", "VOLTA", "12", formatted("[DataCorePlugin.GameData.CurrentLap]", "0")),
    # Corrida por tempo nao tem total de voltas.
    ("Total Laps", "TOTAL", "30", ncalc(
        "if([DataCorePlugin.GameData.TotalLaps] > 0, "
        "format([DataCorePlugin.GameData.TotalLaps], '0'), '--')")),
    # A volta do stint em curso: as completas desde o box mais esta.
    ("Stint Lap", "STINT", "8", ncalc(
        "format([IRacingExtraProperties.iRacing_Player_LapsSinceLastPit] + 1, '0')")),
]


def laps():
    items = []
    for (x, width, align), (name, label, sample, binding) in zip(LAP_COLUMNS, LAPS):
        items.append(text(x, LAP_LABEL_Y, width, 12.0, label,
                          name=f"{name} Label", size=SIZE_LAP_LABEL,
                          color=TEXT_SECONDARY, align=align, font=FONT))
        value = text(x, LAP_VALUE_Y, width, SIZE_LAP_VALUE, sample, name=name,
                     size=SIZE_LAP_VALUE, color=TEXT, align=align,
                     bindings={"Text": binding})
        value["RenderingSkip"] = SKIP_SLOW
        items.append(value)
    return group("Laps", *items)
