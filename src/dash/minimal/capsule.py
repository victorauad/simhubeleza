"""O miolo da capsula: fundo, pedais, marcha, velocidade, RPM, OTS e voltas.

    [ freio <======|======> acelerador ]
           52 |  47
    km/h  relativo     MARCHA     OTS READY 094      rpm x1000
    223   (5 linhas)              LAPS TO GO STINT   7.7

Os pedais enchem do centro para fora, como no dash principal, e o valor
fica logo acima da marcha, em cinza e menor que km/h e rpm: a barra ja
diz a cor e o lado, o numero so refina. A marcha e o unico branco
verdadeiro; o resto usa o cinza dos valores.
"""

from simhub.bindings import formatted, ncalc
from simhub.model import GearText, LinearGaugeItem
from simhub.theme import (
    BRAKE, CAPSULE_EDGE, CAPSULE_FILL, FONT, GEAR, MINI_FUEL, MINI_FUEL_SHORT,
    MINI_TRACK, STATUS_RING, TEXT, TEXT_SECONDARY, THROTTLE, rounded,
)
from .. import ots
from ..widgets import CENTER, LEFT, RIGHT, text
from .base import CAPSULE, RADIUS, SKIP_SLOW, Region, group, rect

# --- Medidas (pixels do canvas) ----------------------------------------------

PEDALS = Region(120.0, 9.0, 657.0, 14.0)
PEDAL_GAP = 4.0
#: Raio dos cantos das barras (pedais e OTS).
BAR_RADIUS = 3
#: Mesmo tamanho dos numeros secundarios (OTS, voltas), centrado na altura
#: que o de 34 px ocupava.
SIZE_PEDAL = 30.0
BRAKE_VALUE = Region(363.0, 31.0, 84.0, SIZE_PEDAL)
THROTTLE_VALUE = Region(455.0, 31.0, 84.0, SIZE_PEDAL)

GEAR_BOX = Region(364.0, 54.0, 170.0, 170.0)
SIZE_GEAR = 176.0

SIZE_READOUT = 44.0
SIZE_READOUT_LABEL = 11.0
SPEED = Region(40.0, 87.0, 80.0, SIZE_READOUT)
SPEED_LABEL = Region(40.0, 134.0, 40.0, 14.0)
#: km/h e rpm na mesma altura, espelhados.
RPM = Region(778.0, SPEED.y, 80.0, SIZE_READOUT)
RPM_LABEL = Region(778.0, SPEED_LABEL.y, 80.0, 14.0)

#: OTS: "OTS READY" e a barra a esquerda, os segundos na mesma altura do
#: rotulo, a direita.
OTS_HEADER = Region(522.0, 70.0, 140.0, 20.0)
#: Mesmo tamanho das linhas do relativo.
SIZE_OTS_HEADER = 16.0
OTS_SECONDS = Region(671.0, 68.0, 75.0, 30.0)
SIZE_OTS_SECONDS = 30.0
OTS_BAR = Region(522.0, 94.0, 205.0, 9.0)

#: Voltas, abaixo do OTS e na mesma largura da barra dele: LAPS encosta na
#: borda esquerda, TO GO fica no centro e STINT na borda direita. Como em
#: km/h e rpm, o numero vem em cima e o rotulo embaixo.
LAPS_BLOCK = Region(OTS_BAR.x, 128.0, OTS_BAR.width, 0.0)
SIZE_LAP_VALUE = 30.0
LAP_VALUE_Y = LAPS_BLOCK.y
LAP_LABEL_Y = LAP_VALUE_Y + SIZE_LAP_VALUE + 4.0
LAP_COLUMN_WIDTH = 70.0
LAP_COLUMNS = [  # (x, alinhamento)
    (LAPS_BLOCK.x, LEFT),
    (LAPS_BLOCK.x + (LAPS_BLOCK.width - LAP_COLUMN_WIDTH) / 2, CENTER),
    (LAPS_BLOCK.x + LAPS_BLOCK.width - LAP_COLUMN_WIDTH, RIGHT),
]


#: Combustivel, abaixo das voltas e na mesma largura: rotulo e margem em
#: cima, barra fina embaixo com a marca do que a corrida ainda pede.
FUEL_LABEL = Region(OTS_BAR.x, 192.0, 60.0, 16.0)
FUEL_VALUE = Region(OTS_BAR.x + OTS_BAR.width - 120.0, 192.0, 120.0, 16.0)
FUEL_BAR = Region(OTS_BAR.x, 213.0, OTS_BAR.width, 5.0)
FUEL_MARK_W, FUEL_MARK_H = 2.0, 11.0


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
        BorderStyle=rounded(radius=BAR_RADIUS),
        Left=region.x, Top=region.y, Width=region.width, Height=region.height,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Value": ncalc(f"[{prop}]")},
    )


def pedal_value(name, region, prop, align):
    """Valor do pedal em 2 digitos. Some solto (arredondaria para 0) e no
    fundo (arredondaria para 100): a barra cheia ja diz isso, e "00" no
    fundo lia como pedal solto."""
    return text(region.x, region.y, region.width, region.height, "47",
                name=name, size=SIZE_PEDAL, color=TEXT, align=align,
                bindings={
                    "Text": ncalc(f"format([{prop}],'00')"),
                    "Visible": ncalc(f"if([{prop}]<0.5 || [{prop}]>=99.5,0,1)"),
                })


def pedals():
    half = (PEDALS.width - PEDAL_GAP) / 2
    brake = Region(PEDALS.x, PEDALS.y, half, PEDALS.height)
    throttle = Region(PEDALS.x + half + PEDAL_GAP, PEDALS.y, half, PEDALS.height)
    return group(
        "Pedals",
        rect("Brake Track", brake, MINI_TRACK, radius=BAR_RADIUS),
        gauge("Brake", brake, BRAKE, "Brake", alignment=2),
        rect("Throttle Track", throttle, MINI_TRACK, radius=BAR_RADIUS),
        gauge("Throttle", throttle, THROTTLE, "Throttle", alignment=0),
        pedal_value("Brake Value", BRAKE_VALUE, "Brake", RIGHT),
        pedal_value("Throttle Value", THROTTLE_VALUE, "Throttle", LEFT),
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


def readout(name, value, label, caption, sample, expression, align,
            fmt="0"):
    return [
        text(value.x, value.y, value.width, value.height, sample, name=name,
             size=SIZE_READOUT, color=TEXT, align=align,
             bindings={"Text": formatted(expression, fmt)}),
        text(label.x, label.y, label.width, label.height, caption,
             name=f"{name} Label", size=SIZE_READOUT_LABEL,
             color=TEXT_SECONDARY, align=align, font=FONT),
    ]


def readouts():
    return group(
        "Speed & RPM",
        *readout("Speed", SPEED, SPEED_LABEL, "KM/H", "223", "[SpeedKmh]", LEFT),
        # RPM em milhares com uma casa: 7720 vira 7.7, e o rotulo diz a escala.
        *readout("Rpm", RPM, RPM_LABEL, "RPM ×1000", "7.7", "[Rpms]/1000",
                 RIGHT, fmt="0.0"),
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
               BorderStyle=rounded(radius=BAR_RADIUS))
    bar["Bindings"]["GaugeColor"] = ncalc(ots.COLOR)
    return group(
        "OTS",
        header, seconds,
        rect("OTS Track", OTS_BAR, MINI_TRACK, radius=BAR_RADIUS),
        bar,
        bindings={"Visible": ncalc(f"if({OTS_HIDDEN}, 0, 1)")},
    )


# --- Voltas ------------------------------------------------------------------

#: Voltas que faltam completar: total menos completas. Sem total de voltas
#: (corrida por tempo, treino) nao ha conta exata, e a estimativa nao vale:
#: "N/A".
LAPS_TO_GO = (
    "if([DataCorePlugin.GameData.TotalLaps] > 0, "
    "format(Max([DataCorePlugin.GameData.TotalLaps] "
    "- [DataCorePlugin.GameData.CompletedLaps], 0), '0'), 'N/A')"
)

LAPS = [
    ("Laps", "LAPS", "10", formatted("[DataCorePlugin.GameData.CompletedLaps]", "0")),
    ("Laps To Go", "TO GO", "20", ncalc(LAPS_TO_GO)),
    # Voltas completas desde a ultima saida dos boxes; sem o plugin, "--".
    ("Stint Laps", "STINT", "8", ncalc(
        "if(isnull([IRacingExtraProperties.iRacing_Player_LapsSinceLastPit], -1) < 0, '--', "
        "format([IRacingExtraProperties.iRacing_Player_LapsSinceLastPit], '0'))")),
]


def laps():
    items = []
    for (x, align), (name, label, sample, binding) in zip(LAP_COLUMNS, LAPS):
        value = text(x, LAP_VALUE_Y, LAP_COLUMN_WIDTH, SIZE_LAP_VALUE, sample,
                     name=name, size=SIZE_LAP_VALUE, color=TEXT, align=align,
                     bindings={"Text": binding})
        value["RenderingSkip"] = SKIP_SLOW
        items.append(value)
        items.append(text(x, LAP_LABEL_Y, LAP_COLUMN_WIDTH, 14.0, label,
                          name=f"{name} Label", size=SIZE_READOUT_LABEL,
                          color=TEXT_SECONDARY, align=align, font=FONT))
    return group("Laps", *items)


# --- Combustivel -------------------------------------------------------------

FUEL = "[Fuel]"
FUEL_CAP = "[MaxFuel]"
FUEL_PER_LAP = "[DataCorePlugin.Computed.Fuel_LitersPerLap]"
#: Voltas que ainda faltam, contando a fracao da volta atual. So existe com
#: total de voltas (corrida por voltas); sem ele nao ha o que a corrida pede.
LAPS_LEFT = ("([DataCorePlugin.GameData.TotalLaps] - "
             "[DataCorePlugin.GameData.CompletedLaps] - "
             "[GameRawData.Telemetry.LapDistPct])")
HAS_TARGET = f"([DataCorePlugin.GameData.TotalLaps] > 0 && {FUEL_PER_LAP} > 0)"
#: Combustivel que falta para chegar ao fim.
NEEDED = f"(Max({LAPS_LEFT}, 0) * {FUEL_PER_LAP})"

#: Margem com sinal em litros (corrida por voltas); sem total, as voltas
#: que o tanque ainda da; sem consumo medido, "--".
FUEL_TEXT = (
    f"if({HAS_TARGET}, "
    f"if({FUEL} >= {NEEDED}, '+', '-') + format(Abs({FUEL} - {NEEDED}), '0.0') + ' L', "
    f"if({FUEL_PER_LAP} > 0, "
    "format([DataCorePlugin.Computed.Fuel_RemainingLaps], '0.0') + ' LAPS', '--'))"
)
#: Cor da barra: neutra; laranja quando o tanque nao chega ao fim.
FUEL_COLOR = f"if({HAS_TARGET} && {FUEL} < {NEEDED}, '{MINI_FUEL_SHORT}', '{MINI_FUEL}')"
#: Posicao da marca na barra (px): fracao da capacidade que a corrida pede.
FUEL_MARK_X = (f"{FUEL_BAR.x - FUEL_MARK_W / 2:g} + "
               f"Min(Max({NEEDED} / {FUEL_CAP}, 0), 1) * {FUEL_BAR.width:g}")


def fuel():
    """Combustivel como grafico de bullet: a barra e o tanque, a marca e o
    que falta para a bandeira. A marca so existe em corrida por voltas, e a
    barra vira laranja quando nao chega; o texto traz a margem em litros."""
    bar = gauge("Fuel Gauge", FUEL_BAR, MINI_FUEL, "MaxFuel", alignment=0)
    bar["Bindings"] = {
        "Value": ncalc(f"if({FUEL_CAP} > 0, {FUEL} / {FUEL_CAP} * 100, 0)"),
        "GaugeColor": ncalc(FUEL_COLOR),
    }
    bar.update(BorderStyle=rounded(radius=BAR_RADIUS))
    mark = rect("Fuel Mark",
                Region(FUEL_BAR.x + FUEL_BAR.width * 0.62, FUEL_BAR.y - (FUEL_MARK_H - FUEL_BAR.height) / 2,
                       FUEL_MARK_W, FUEL_MARK_H),
                STATUS_RING, radius=1,
                bindings={"Left": ncalc(FUEL_MARK_X),
                          "Visible": ncalc(f"if({HAS_TARGET}, 1, 0)")})
    value = text(*frame(FUEL_VALUE), "+1.4 L", name="Fuel Value",
                 size=SIZE_OTS_HEADER, color=TEXT, align=RIGHT,
                 bindings={"Text": ncalc(FUEL_TEXT)})
    value["RenderingSkip"] = SKIP_SLOW
    mark["RenderingSkip"] = SKIP_SLOW
    bar["RenderingSkip"] = SKIP_SLOW
    return group(
        "Fuel",
        text(*frame(FUEL_LABEL), "FUEL", name="Fuel Label",
             size=SIZE_OTS_HEADER, color=TEXT_SECONDARY, align=LEFT, font=FONT),
        value,
        rect("Fuel Track", FUEL_BAR, MINI_TRACK, radius=BAR_RADIUS),
        bar, mark,
    )
