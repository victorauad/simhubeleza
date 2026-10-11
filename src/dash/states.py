"""Estados temporarios dos componentes laterais.

Quatro estados tomam por alguns segundos o lugar de um componente fixo:

  Damage        no lugar do grafico de telemetria (esquerda)  -- damage.py
  Weather       idem                                          -- weather.py
  Lap Review    idem                                          -- lap_review.py
  New Lap Info  no lugar dos setores (rodape da direita)      -- new_lap_info.py

Regras completas e decisoes em `docs/estados.md`.

Como o SimHub decide qual aparece
---------------------------------

Cada formula JS tem o proprio `root`, e nao ha estado compartilhado
confiavel entre formulas. Entao a maquina de estados e um prelúdio JS gerado
aqui e repetido em cada consumidor (o `Visible` de cada estado, o do grafico,
os coletores). Todos leem as mesmas propriedades na mesma cadencia e com o
mesmo relogio (`Date.now()`), e chegam a mesma resposta.

O `Visible` de item escondido continua sendo avaliado, entao os consumidores
enxergam as bordas dos gatilhos mesmo com o estado desligado. A primeira
avaliacao so registra o estado atual: carregar o dash no meio de uma volta
nao dispara nada.

Prioridade na esquerda: Damage > Weather > Lap Review. Quem tem prioridade
maior cobre o outro; quando acaba, o coberto volta se a janela dele ainda
estiver aberta (cada um tem o proprio prazo).
"""

from simhub.bindings import js

TELEMETRY = "GameRawData.Telemetry."

#: Expressao JS com o tipo da sessao atual: 'Race', 'Practice',
#: 'Lone Qualify', 'Offline Testing'... O YAML do iRacing fica sob
#: `GameRawData.SessionData.` (sem o prefixo, `$prop` devolve nulo -- conferido
#: na API do SimHub) e nao tem `CurrentSessionNum`; o indice da sessao atual e
#: o `SessionNum` da telemetria, e `SessionsNN` comeca em 01.
SESSION_TYPE_JS = (
    "$prop('GameRawData.SessionData.SessionInfo.Sessions' + "
    f"('0' + ((Number($prop('{TELEMETRY}SessionNum')) || 0) + 1)).slice(-2) "
    "+ '.SessionType')"
)

# --- Configuracao da instalacao do usuario ---------------------------------
#
# Preencher com o que aparece em Available properties no SimHub. Enquanto
# estiver `None`, o gatilho/campo correspondente fica desligado (N/A).

#: Botao "Damage Report" no volante, lido pelo SimHub. No `controls.cfg` do
#: iRacing, `SPCCDamageReport` esta no Volante_PRS-Formula com mascara 0x8000
#: (bit 15). O SimHub numera a partir de 0: os B22/B23 que ele usa para trocar
#: de tela caem nos bits 22/23 do iRacing (MGUK fixed dec/inc). A conferir
#: apertando o botao em Available properties.
DAMAGE_BUTTON = "InputStatus.JoystickPlugin.Volante_PRS-Formula_B15"
#: Temperaturas do provedor ligado em Settings > System Infos -- aqui o MSI
#: Afterburner (CPU_temperature_Degrees, GPU1_temperature_Degrees). Ficam
#: nulas enquanto o Afterburner nao estiver rodando.
CPU_TEMP = "SystemInfosProvider.MainCPUTemp"
GPU_TEMP = "SystemInfosProvider.MainGPUTemp"

# --- Duracoes (s) ----------------------------------------------------------

DURATION = {
    "damage_button": 3.0,
    "damage_new": 5.0,
    "weather": 10.0,
    "review": 5.0,
    "new_lap": 5.0,
}

#: Aumento minimo do tempo de reparo (s) que conta como dano novo -- abaixo
#: disso e ruido de arredondamento.
REPAIR_STEP = 0.5

#: Bits de `EngineWarnings` que contam como dano (irsdk_EngineWarnings):
#: agua 0x01, pressao de combustivel 0x02, pressao de oleo 0x04, temperatura
#: de oleo 0x40, reparo obrigatorio 0x80, reparo opcional 0x100. Motor
#: morto, limitador e corte de giro ficam de fora.
WARN_WATER, WARN_FUEL_P, WARN_OIL_P = 0x01, 0x02, 0x04
WARN_OIL_T, WARN_MAND_REP, WARN_OPT_REP = 0x40, 0x80, 0x100
DAMAGE_WARNINGS = (WARN_WATER | WARN_FUEL_P | WARN_OIL_P | WARN_OIL_T
                   | WARN_MAND_REP | WARN_OPT_REP)

# --- Cadencia (RenderingSkip) ----------------------------------------------

#: Quem decide visibilidade (gatilhos): ~10 Hz. Todos iguais, para que os
#: consumidores avaliem nos mesmos quadros.
SKIP_GATE = 5
#: Conteudo de um estado ja visivel: ~6 Hz.
SKIP_CONTENT = 9

# --- JS --------------------------------------------------------------------

#: Leitura comum: normaliza booleanos (o SimHub entrega bool, 0/1 ou 'True')
#: e numeros, e le o que todos os gatilhos usam.
BASE = (
    "var yes = function (v) { return v === true || v === 1 || "
    "(v != null && String(v).toUpperCase() === 'TRUE'); };\r\n"
    "var num = function (v) { if (v == null || v === '') return null; "
    "var x = Number(v); return isNaN(x) ? null : x; };\r\n"
    "var now = Date.now();\r\n"
    f"var lap = num($prop('{TELEMETRY}Lap')) || 0;\r\n"
    f"var onPit = yes($prop('{TELEMETRY}OnPitRoad'));\r\n"
    f"var onTrack = yes($prop('{TELEMETRY}IsOnTrack'));\r\n"
)


#: `EngineWarnings` como numero ou como nomes do enum (o SimHub pode
#: entregar qualquer um dos dois, ex. "OilTempWarning, PitSpeedLimiter").
FLAGS = (
    "var flags = function (v) { if (v == null || v === '') return 0; "
    "var x = Number(v); if (!isNaN(x)) return x; "
    "var s = String(v).toLowerCase(); var f = 0; "
    f"if (s.indexOf('watertemp') >= 0) f |= {WARN_WATER}; "
    f"if (s.indexOf('fuelpress') >= 0) f |= {WARN_FUEL_P}; "
    f"if (s.indexOf('oilpress') >= 0) f |= {WARN_OIL_P}; "
    f"if (s.indexOf('oiltemp') >= 0) f |= {WARN_OIL_T}; "
    f"if (s.indexOf('mandrep') >= 0) f |= {WARN_MAND_REP}; "
    f"if (s.indexOf('optrep') >= 0) f |= {WARN_OPT_REP}; "
    "return f; };\r\n"
)


def _button_read():
    if DAMAGE_BUTTON is None:
        return "var btn = false;\r\n"
    return f"var btn = yes($prop('{DAMAGE_BUTTON}'));\r\n"


def left_prelude():
    """Define `state`: 'damage', 'weather', 'review' ou null."""
    ms = {key: int(value * 1000) for key, value in DURATION.items()}
    return (
        BASE
        + f"var race = {SESSION_TYPE_JS} == 'Race';\r\n"
        f"var repair = (num($prop('{TELEMETRY}PitRepairLeft')) || 0) + "
        f"(num($prop('{TELEMETRY}PitOptRepairLeft')) || 0);\r\n"
        + FLAGS
        + f"var warn = flags($prop('{TELEMETRY}EngineWarnings')) "
        f"& {DAMAGE_WARNINGS};\r\n"
        + _button_read()
        + "var st = root.st;\r\n"
        "if (st == null) { st = root.st = { lap: lap, pit: onPit, "
        "track: onTrack, repair: repair, warn: warn, btn: btn, "
        "damage: 0, weather: 0, review: 0 }; }\r\n"
        # Damage: botao (borda de subida), reparo que cresceu em pista, ou
        # aviso novo.
        f"if (btn && !st.btn) st.damage = Math.max(st.damage, now + "
        f"{ms['damage_button']});\r\n"
        f"if (onTrack && repair > st.repair + {REPAIR_STEP}) "
        f"st.damage = Math.max(st.damage, now + {ms['damage_new']});\r\n"
        f"if ((warn & ~st.warn) != 0) st.damage = Math.max(st.damage, now + "
        f"{ms['damage_new']});\r\n"
        # Weather: saiu do pit, ou entrou no carro numa corrida (o "Race"
        # que leva ao grid).
        f"if (st.pit && !onPit && onTrack) st.weather = now + {ms['weather']};\r\n"
        f"if (race && onTrack && !st.track) st.weather = now + {ms['weather']};\r\n"
        # Lap Review: volta nova, em corrida, fechada fora do pit.
        f"if (lap > st.lap && race && !onPit) st.review = now + {ms['review']};\r\n"
        "st.lap = lap; st.pit = onPit; st.track = onTrack; "
        "st.repair = repair; st.warn = warn; st.btn = btn;\r\n"
        "var state = now < st.damage ? 'damage' : now < st.weather ? 'weather' "
        ": now < st.review ? 'review' : null;\r\n"
    )


def right_prelude():
    """Define `newLap`: verdadeiro nos primeiros segundos de cada volta."""
    ms = int(DURATION["new_lap"] * 1000)
    return (
        BASE
        + "var nl = root.nl;\r\n"
        "if (nl == null) { nl = root.nl = { lap: lap, until: 0 }; }\r\n"
        f"if (lap > nl.lap && onTrack) nl.until = now + {ms};\r\n"
        "nl.lap = lap;\r\n"
        "var newLap = now < nl.until;\r\n"
    )


def left(body):
    """Formula JS com o estado da esquerda disponivel em `state`."""
    return js(left_prelude() + body)


def right(body):
    return js(right_prelude() + body)


def showing(name):
    """`Visible` de um estado da esquerda."""
    return left(f"return state == '{name}';")


def chart_visible():
    """`Visible` do grafico: some enquanto qualquer estado ocupa o lugar."""
    return left("return state == null;")


def new_lap_visible():
    return right("return newLap;")


def sectors_visible():
    return right("return !newLap;")


def gate(item):
    """Cadencia dos itens que decidem visibilidade."""
    item["RenderingSkip"] = SKIP_GATE
    return item


def content(item):
    item["RenderingSkip"] = SKIP_CONTENT
    return item


#: Formatos comuns, com as mesmas regras dos setores: nulo ou zero vira N/A,
#: acima de 99 s vira OFF.
FORMAT = (
    "var sec = function (v) { if (v == null || v === '') return null; "
    "var s = typeof v === 'number' ? v : timespantoseconds(v); "
    "return (s == null || s <= 0 || isNaN(s)) ? null : s; };\r\n"
    "var fmtLap = function (s) { if (s == null) return 'N/A'; "
    "var ms = Math.round(s * 1000); var m = Math.floor(ms / 60000); "
    "var r = (ms - m * 60000) / 1000; "
    "return m + ':' + (r < 10 ? '0' : '') + r.toFixed(3); };\r\n"
    "var fmtDelta = function (d, p) { if (d == null) return 'N/A'; "
    "var r = Number(d.toFixed(p)); if (r == 0) return 'N/A'; "
    "if (Math.abs(r) > 99) return 'OFF'; "
    "return (r > 0 ? '+' : '') + r.toFixed(p); };\r\n"
)


def color_delta(expression, places, faster, slower, neutral):
    """JS: cor de um delta (negativo = mais rapido)."""
    return (f"var d = {expression}; if (d == null) return '{neutral}'; "
            f"var r = Number(d.toFixed({places})); "
            f"if (r == 0 || Math.abs(r) > 99) return '{neutral}'; "
            f"return r < 0 ? '{faster}' : '{slower}';")
