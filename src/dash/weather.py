"""Weather: as condicoes da pista por 10 s ao sair do pit ou ir para o grid.

Ocupa o lugar do grafico de telemetria. O iRacing nao publica a previsao do
tempo no SDK, entao o estado mostra a condicao atual e a tendencia -- o
fallback que as regras pedem:

  icone     ceu (`Skies`) x chuva (`Precipitation`) x dia/noite
            (`SolarAltitude`), com o nome da condicao embaixo.
  grade     AIR, TRACK, WIND (com a seta e HEAD/TAIL/CROSS relativos ao
            carro: `WindDir` - `YawNorth`), HUMIDITY, ASPHALT
            (`TrackWetness`) e RAIN.
  tendencia seta para cima/baixo no canto de cada campo, comparando com
            ~10 min atras.

A tendencia precisa de historico, e filho de layer escondida nao e avaliado:
as setas sao `ImageItem`s fora do layer do estado, e o proprio `Visible`
delas e o coletor (amostra a cada 30 s, sempre).

A convencao de `WindDir` (de onde o vento vem) e a mesma da seta da linha de
stats; se a seta apontar ao contrario em pista, as duas estao erradas juntas.
"""

from simhub.bindings import js
from simhub.model import ImageItem, Layer
from simhub.theme import CYAN, MONO_ADVANCE, SIZE_LABEL, TEXT, YELLOW
from . import layout as grid
from . import states
from .widgets import CENTER, caption, separators, text

T = states.TELEMETRY

INSET_X, INSET_Y = 14.0, 10.0
ICON_ZONE = 120.0
ICON = 84.0
VALUE_SIZE = 30.0
ARROW = 12.0
WIND_ARROW = 16.0
#: Amostragem e janela da tendencia.
SAMPLE_MS = 30_000
WINDOW = 20                    # amostras: 20 x 30 s = 10 min
MIN_SAMPLES = 3

#: Icones (assets/images, gerados por tools/make_state_icons.py) e a regra
#: de cada um. `rain`, `skies` e `night` vem de WX.
ICONS = [
    ("WxHeavyRain", "rain >= 0.35"),
    ("WxRain", "rain >= 0.03 && rain < 0.35"),
    ("WxCloud", "rain < 0.03 && skies >= 2"),
    ("WxPartlySun", "rain < 0.03 && skies == 1 && !night"),
    ("WxPartlyMoon", "rain < 0.03 && skies == 1 && night"),
    ("WxSun", "rain < 0.03 && skies < 1 && !night"),
    ("WxMoon", "rain < 0.03 && skies < 1 && night"),
]
TRENDS = ("TrendUp", "TrendDown")
IMAGES = (*(name for name, _ in ICONS), *TRENDS, "WindArrow")

WX = (
    f"var rain = num($prop('{T}Precipitation')) || 0;\r\n"
    f"var skies = num($prop('{T}Skies')) || 0;\r\n"
    f"var sun = num($prop('{T}SolarAltitude'));\r\n"
    "var night = sun != null && sun < 0;\r\n"
)

CONDITION = (
    "if (rain >= 0.35) return 'Heavy rain';\r\n"
    "if (rain >= 0.03) return 'Rain';\r\n"
    "if (skies >= 3) return 'Overcast';\r\n"
    "if (skies >= 2) return 'Mostly cloudy';\r\n"
    "if (skies >= 1) return 'Partly cloudy';\r\n"
    "return night ? 'Clear night' : 'Clear';"
)

#: `TrackWetness` (irsdk_TrackWetness): 0 desconhecido, 1 seco ... 7
#: extremamente molhado.
WETNESS = ("N/A", "DRY", "M.DRY", "DAMP", "L.WET", "WET", "V.WET", "X.WET")

#: `TrackWetness` como numero ou como nome do enum.
WET = (
    "var wet = function (v) { if (v == null || v === '') return null; "
    "var x = Number(v); if (!isNaN(x)) return x; "
    "var names = ['unknown', 'dry', 'mostlydry', 'verylightlywet', "
    "'lightlywet', 'moderatelywet', 'verywet', 'extremelywet']; "
    "var i = names.indexOf(String(v).toLowerCase().replace(/[^a-z]/g, '')); "
    "return i < 0 ? null : i; };\r\n"
)

#: (nome, rotulo, exemplo, expressao JS do numero, formato JS do texto,
#: limiar da tendencia). O formato recebe `v`.
FIELDS = [
    ("Air", "Air", "24",
     f"num($prop('{T}AirTemp'))", "Math.round(v)", 0.5),
    ("Track", "Track", "38",
     f"(num($prop('{T}TrackTempCrew')) || num($prop('{T}TrackTemp')))",
     "Math.round(v)", 1.0),
    ("Wind", "Wind", "12",
     f"(num($prop('{T}WindVel')) == null ? null : "
     f"num($prop('{T}WindVel')) * 3.6)", "Math.round(v)", 2.0),
    ("Humidity", "Humidity", "62",
     f"(function (h) {{ return h != null && h <= 1 ? h * 100 : h; }})"
     f"(num($prop('{T}RelativeHumidity')))", "Math.round(v)", 3.0),
    ("Asphalt", "Asphalt", "DRY", f"wet($prop('{T}TrackWetness'))",
     f"{list(WETNESS)!r}[Math.max(0, Math.min(7, Math.round(v)))]", 0.9),
    ("Rain", "Rain", "0",
     f"(function (r) {{ return r == null ? null : r * 100; }})"
     f"(num($prop('{T}Precipitation')))", "Math.round(v)", 5.0),
]

#: Angulo do vento relativo ao nariz do carro, em graus, de -180 a 180.
WIND_RELATIVE = (
    f"var wd = num($prop('{T}WindDir')); var yaw = num($prop('{T}YawNorth'));\r\n"
    "var rel = (wd == null || yaw == null) ? null : "
    "((wd - yaw) * 180 / Math.PI) % 360;\r\n"
    "if (rel != null) { if (rel > 180) rel -= 360; if (rel < -180) rel += 360; }\r\n"
)


def value_formula(expression, fmt):
    return js(states.BASE + WET + f"var v = {expression};\r\n"
              "if (v == null) return 'N/A';\r\n"
              f"return String({fmt});")


def asphalt_color():
    return js(states.BASE + WET
              + f"var v = wet($prop('{T}TrackWetness')) || 0;\r\n"
              f"return v >= 4 ? '{CYAN}' : v >= 2 ? '{YELLOW}' : '{TEXT}';")


def trend_visible(expression, threshold, sign):
    """Coletor + `Visible` de uma seta: amostra a cada 30 s e compara com a
    amostra mais antiga da janela."""
    test = f"t > {threshold}" if sign > 0 else f"t < -{threshold}"
    return js(
        states.left_prelude() + WET
        + f"var v = {expression};\r\n"
        "var h = root.h || (root.h = []);\r\n"
        f"if (v != null && (root.t == null || now - root.t >= {SAMPLE_MS})) "
        f"{{ root.t = now; h.push(v); if (h.length > {WINDOW}) h.shift(); }}\r\n"
        "if (state != 'weather' || v == null || "
        f"h.length < {MIN_SAMPLES}) return false;\r\n"
        "var t = v - h[0];\r\n"
        f"return {test};"
    )


def image(name, region, image_name, *, bindings=None):
    return ImageItem(
        name=name,
        Image=image_name,
        AutoSize=False,
        BackgroundColor="#00FFFFFF",
        Left=region.x, Top=region.y,
        Width=region.width, Height=region.height,
        Visible=True,
        BlinkPhasisInverted=False,
        RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings=bindings,
    )


def regions(region):
    inner = region.inset(top=INSET_Y, bottom=INSET_Y,
                         left=INSET_X, right=INSET_X)
    icon_zone = grid.Region(inner.x, inner.y, ICON_ZONE, inner.height)
    gutter = 20.0
    grid_zone = inner.inset(left=ICON_ZONE + gutter)
    rows = grid_zone.rows(2, gutter=8.0)
    cells = [cell for row in rows for cell in row.columns(3, gutter=16.0)]
    return inner, icon_zone, grid_zone, cells, gutter


def layer(region):
    """Devolve (layer do estado, layer das setas de tendencia)."""
    inner, icon_zone, grid_zone, cells, gutter = regions(region)
    assert cells[0].width >= 5 * VALUE_SIZE * MONO_ADVANCE, "weather: grade"

    icon = grid.Region(icon_zone.x + (icon_zone.width - ICON) / 2,
                       icon_zone.y + 6.0, ICON, ICON)
    items = [
        *separators([inner, grid.Region(grid_zone.x - gutter / 2, region.y,
                                        0, region.height)],
                    region, name="Weather Separator"),
        *(image(f"Weather {name}", icon, name, bindings={
            "Visible": js(states.BASE + WX + f"return {rule};")})
          for name, rule in ICONS),
        caption(icon_zone.x, icon.bottom + 8.0, icon_zone.width,
                "Partly cloudy", name="Weather Condition", align=CENTER,
                color=TEXT, size=12.0, height=18.0,
                bindings={"Text": js(states.BASE + WX + CONDITION)}),
    ]
    label_h = SIZE_LABEL + 6.0
    arrows = []
    for cell, (name, label, sample, expression, fmt, threshold) in zip(
            cells, FIELDS):
        label_bindings = None
        if name == "Wind":
            label = "Wind head"
            label_bindings = {"Text": js(
                states.BASE + WIND_RELATIVE
                + "if (rel == null) return 'WIND';\r\n"
                "var a = Math.abs(rel);\r\n"
                "return a <= 45 ? 'WIND HEAD' : a >= 135 ? 'WIND TAIL' "
                ": 'WIND CROSS';")}
        items.append(caption(cell.x, cell.y, cell.width, label,
                             name=f"Weather {name} Label",
                             bindings=label_bindings))
        bindings = {"Text": value_formula(expression, fmt)}
        if name == "Asphalt":
            bindings["TextColor"] = asphalt_color()
        items.append(text(cell.x, cell.y + label_h, cell.width,
                          cell.height - label_h, sample,
                          name=f"Weather {name}", size=VALUE_SIZE,
                          weight="Bold", bindings=bindings))
        if name == "Wind":
            value_w = len(sample) * VALUE_SIZE * MONO_ADVANCE
            arrow = grid.Region(cell.x + value_w + 8.0,
                                cell.y + label_h + (cell.height - label_h
                                                    - WIND_ARROW) / 2,
                                WIND_ARROW, WIND_ARROW)
            items.append(image("Weather Wind Arrow", arrow, "WindArrow",
                               bindings={"Rotation": js(
                                   states.BASE + WIND_RELATIVE
                                   + "return rel == null ? 0 : "
                                   "Math.round(180 + rel);")}))
        spot = grid.Region(cell.right - ARROW, cell.y + 1.0, ARROW, ARROW)
        for image_name, sign in zip(TRENDS, (1, -1)):
            arrows.append(states.gate(image(
                f"Weather {name} {image_name}", spot, image_name,
                bindings={"Visible": trend_visible(expression, threshold,
                                                   sign)})))

    shown = Layer(
        *(states.content(item) for item in items),
        name="Weather",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
        bindings={"Visible": states.showing("weather")},
    )
    collectors = Layer(
        *arrows,
        name="Weather Live",
        Group=True, Repetitions=0, Visible=True,
        BlinkPhasisInverted=False, RenderingSkip=0,
        MinimumRefreshIntervalMS=0.0,
    )
    return states.gate(shown), collectors
