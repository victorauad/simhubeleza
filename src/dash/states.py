"""Estados temporarios dos componentes laterais.

Quatro estados tomam por alguns segundos o lugar de um componente fixo:

  Damage        no lugar do grafico de telemetria (esquerda)  -- damage.py
  Weather       idem                                          -- weather.py
  Lap Review    idem                                          -- lap_review.py
  New Lap Info  no lugar dos setores (rodape da direita)      -- new_lap_info.py

Regras completas e decisoes em `docs/estados.md`.

Como o SimHub decide qual aparece
---------------------------------

Cada formula JS tem o proprio `root`. O SimHub tem um armazenamento
compartilhado entre formulas (`setsharedvalue` / `getsharedvalueordefault`,
docs/propriedades-simhub-completo.md sec. 11.1): uma formula so -- o
`Visible` do cartao do grafico, o primeiro item da coluna (`clock()`) --
calcula a maquina de estados e publica o resultado com a hora. Os
consumidores (o `Visible` de cada estado, o do grafico, os coletores) leem
o resultado publicado.

Se a publicacao estiver velha (mais de `STALE_MS`) ou o armazenamento nao
existir, cada consumidor volta a calcular sozinho, com o proprio `root`,
como antes: todos leem as mesmas propriedades na mesma cadencia e com o
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
#: A sessao corrente ja vem pronta em `GameRawData.CurrentSessionInfo`
#: (sec. 6.4 do relatorio); a montagem pelo indice fica de reserva.
SESSION_TYPE_JS = (
    "($prop('GameRawData.CurrentSessionInfo.SessionType') || "
    "$prop('GameRawData.SessionData.SessionInfo.Sessions' + "
    f"('0' + ((Number($prop('{TELEMETRY}SessionNum')) || 0) + 1)).slice(-2) "
    "+ '.SessionType'))"
)

#: Escopo das chaves no armazenamento compartilhado do SimHub (global a todos
#: os dashboards: o nome evita colisao).
SHARED = "sf23dash"
#: Publicacao mais velha que isso nao vale: o consumidor calcula sozinho.
STALE_MS = 1000

#: Ha armazenamento compartilhado neste SimHub?
HAS_SHARED = ("(typeof getsharedvalueordefault === 'function' && "
              "typeof setsharedvalue === 'function')")


def shared_get(key, default="null"):
    return f"getsharedvalueordefault('{SHARED}', '{key}', {default})"


def shared_set(key, value):
    return f"setsharedvalue('{SHARED}', '{key}', {value})"


#: Tipo de sessao para quem nao e a maquina de estados (leaderboard, modo da
#: coluna direita): o publicado por `clock()`, ou lido na hora.
SESSION_TYPE = (
    f"(({HAS_SHARED} && Date.now() - {shared_get('at', '0')} < {STALE_MS} "
    f"&& {shared_get('session')}) || {SESSION_TYPE_JS})"
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
#: Motor morto (0x08). Com ele, ou com o giro abaixo de `IDLE_RPM`, as
#: pressoes de oleo e combustivel acendem sem dano nenhum -- e o que acontece
#: ao entrar no carro no grid. Nesses casos as duas pressoes sao ignoradas.
WARN_STALLED = 0x08
IDLE_RPM = 300
#: Depois de carregar o dash ou entrar no carro, por quanto tempo (s) a
#: leitura so vira referencia e nao conta como dano novo.
SETTLE = 3.0
DAMAGE_WARNINGS = (WARN_WATER | WARN_FUEL_P | WARN_OIL_P | WARN_OIL_T
                   | WARN_MAND_REP | WARN_OPT_REP)

# --- Cadencia (RenderingSkip) ----------------------------------------------

#: Quem decide visibilidade (gatilhos): ~10 Hz. Todos iguais, para que os
#: consumidores avaliem nos mesmos quadros.
SKIP_GATE = 5
#: Conteudo de um estado ja visivel: ~6 Hz.
SKIP_CONTENT = 9

#: Faixa de `LapDistPct` que o carro precisa cruzar para a virada de volta
#: contar (exclui a volta de abertura da largada).
MID_LAP = (0.25, 0.75)

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
    f"var pct = num($prop('{TELEMETRY}LapDistPct'));\r\n"
    # Volta completa de verdade: so conta a virada de `Lap` se o carro passou
    # pelo meio da pista desde a virada anterior. Na largada o carro sai
    # antes da linha e a primeira virada vem com poucos metros -- nao conta.
    # Idem para quem sai de um box antes da linha. Sem `LapDistPct`, toda
    # virada conta. Chamar uma vez por quadro, antes de gravar `s.lap`.
    "var lapDone = function (s) { "
    f"if (pct == null || (pct > {MID_LAP[0]} && pct < {MID_LAP[1]})) s.mid = true; "
    "var d = lap > s.lap && s.mid === true; "
    "if (lap != s.lap) s.mid = false; return d; };\r\n"
)


#: Validade da volta em andamento (Boolean do IRacingExtraProperties: cai
#: para falso no primeiro corte de pista ou incidente da volta).
LAP_CLEAN = "IRacingExtraProperties.iRacing_Player_CurrentLapIsClean"
#: Logo depois da virada de `Lap` a propriedade ainda pode trazer o valor da
#: volta que acabou: leituras dentro dessa janela nao contam para a nova.
VALID_GRACE_MS = 1000
#: Quantas voltas o gravador publica (o log mostra 9).
VALID_KEEP = 20

#: Gravador da validade por volta (requer BASE). O SimHub so diz se a volta
#: *atual* esta limpa; o historico e do proprio dash: a volta fica invalida
#: se alguma leitura dela deu falso, e e gravada na virada de `Lap` (so se
#: a volta foi observada e a contagem nao pulou). Define `validOf(n)` (1, 0
#: ou null para a volta `n`) e `validNow()` (a volta em andamento).
#: `validOf` le primeiro o publicado por `valid_recorder()` -- sempre
#: visivel, enxerga voltas em que o consumidor estava escondido -- e cai no
#: gravador local se a publicacao estiver velha.
VALIDITY = (
    f"var cl = $prop('{LAP_CLEAN}');\r\n"
    "var known = cl != null && cl !== '';\r\n"
    "var vr = root.vr;\r\n"
    "if (vr == null || lap < vr.lap) vr = root.vr = "
    "{ lap: lap, h: {}, dirty: false, seen: false, at: 0 };\r\n"
    "if (lap > vr.lap) {\r\n"
    "\tif (lap == vr.lap + 1 && vr.seen) vr.h[vr.lap] = vr.dirty ? 0 : 1;\r\n"
    "\tvr.lap = lap; vr.dirty = false; vr.seen = false; vr.at = now;\r\n"
    "}\r\n"
    f"if (known && now - vr.at > {VALID_GRACE_MS}) "
    "{ vr.seen = true; if (!yes(cl)) vr.dirty = true; }\r\n"
    "var validNow = function () { if (!known) return null; "
    f"if (now - vr.at <= {VALID_GRACE_MS}) return vr.dirty ? 0 : 1; "
    "return (vr.dirty || !yes(cl)) ? 0 : 1; };\r\n"
    "var validOf = function (n) {\r\n"
    f"\tif ({HAS_SHARED} && now - (num({shared_get('lvat', '0')}) || 0) "
    f"< {STALE_MS}) {{\r\n"
    f"\t\tvar s = String({shared_get('lvh', chr(39) * 2)} || '');\r\n"
    "\t\tif (s.indexOf(',' + n + ':1,') >= 0) return 1;\r\n"
    "\t\tif (s.indexOf(',' + n + ':0,') >= 0) return 0;\r\n"
    "\t}\r\n"
    "\tvar v = vr.h[n]; return v == null ? null : v;\r\n"
    "};\r\n"
)


def valid_recorder():
    """`Text` de um item sempre visivel e vazio: grava a validade de cada
    volta e publica as ultimas `VALID_KEEP` como ',12:1,13:0,'."""
    return js(
        BASE + VALIDITY
        + f"if ({HAS_SHARED}) {{\r\n"
        "\tvar out = ',';\r\n"
        f"\tfor (var k = lap - {VALID_KEEP}; k < lap; k++) "
        "if (vr.h[k] != null) out += k + ':' + vr.h[k] + ',';\r\n"
        f"\t{shared_set('lvh', 'out')}; {shared_set('lvat', 'now')};\r\n"
        "}\r\n"
        "return '';"
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
    f"if (s.indexOf('stalled') >= 0) f |= {WARN_STALLED}; "
    "return f; };\r\n"
    # Avisos do motor, sem as pressoes quando o motor esta parado.
    "var engineWarn = function () { "
    f"var w = flags($prop('{TELEMETRY}EngineWarnings')); "
    f"var rpm = num($prop('{TELEMETRY}RPM')); "
    f"if ((w & {WARN_STALLED}) || (rpm != null && rpm < {IDLE_RPM})) "
    f"w &= ~{WARN_OIL_P | WARN_FUEL_P}; "
    "return w; };\r\n"
)


def _button_read():
    if DAMAGE_BUTTON is None:
        return "var btn = false;\r\n"
    return f"var btn = yes($prop('{DAMAGE_BUTTON}'));\r\n"


def _left_compute():
    """Calcula `state` (e `session`) a partir das propriedades e do `root`."""
    ms = {key: int(value * 1000) for key, value in DURATION.items()}
    ms["settle"] = int(SETTLE * 1000)
    return (
        f"var session = {SESSION_TYPE_JS};\r\n"
        "var race = session == 'Race';\r\n"
        f"var repair = (num($prop('{TELEMETRY}PitRepairLeft')) || 0) + "
        f"(num($prop('{TELEMETRY}PitOptRepairLeft')) || 0);\r\n"
        + FLAGS
        + f"var warn = engineWarn() & {DAMAGE_WARNINGS};\r\n"
        + _button_read()
        + "var st = root.st;\r\n"
        "if (st == null) { st = root.st = { lap: lap, pit: onPit, "
        "track: onTrack, repair: repair, warn: warn, btn: btn, "
        "damage: 0, weather: 0, review: 0, settle: now + "
        f"{ms['settle']} }}; }}\r\n"
        # Entrou no carro: o reparo e os avisos de agora sao a referencia.
        f"if (onTrack && !st.track) st.settle = now + {ms['settle']};\r\n"
        "var settled = now >= st.settle;\r\n"
        # Damage: botao (borda de subida), reparo que cresceu em pista, ou
        # aviso novo.
        f"if (btn && !st.btn) st.damage = Math.max(st.damage, now + "
        f"{ms['damage_button']});\r\n"
        f"if (settled && onTrack && repair > st.repair + {REPAIR_STEP}) "
        f"st.damage = Math.max(st.damage, now + {ms['damage_new']});\r\n"
        f"if (settled && (warn & ~st.warn) != 0) st.damage = Math.max(st.damage, now + "
        f"{ms['damage_new']});\r\n"
        # Weather: saiu do pit, ou entrou no carro numa corrida (o "Race"
        # que leva ao grid).
        f"if (st.pit && !onPit && onTrack) st.weather = now + {ms['weather']};\r\n"
        f"if (race && onTrack && !st.track) st.weather = now + {ms['weather']};\r\n"
        # Lap Review: volta nova, em corrida, fechada fora do pit.
        f"if (lapDone(st) && race && !onPit) st.review = now + {ms['review']};\r\n"
        "st.lap = lap; st.pit = onPit; st.track = onTrack; "
        "st.repair = repair; st.warn = warn; st.btn = btn;\r\n"
        "var state = now < st.damage ? 'damage' : now < st.weather ? 'weather' "
        ": now < st.review ? 'review' : null;\r\n"
    )


def left_prelude():
    """Define `state`: 'damage', 'weather', 'review' ou null.

    Le o publicado por `clock()`; calcula sozinho se nao houver publicacao
    recente."""
    return (
        BASE
        + "var state = null;\r\n"
        f"if ({HAS_SHARED} && now - {shared_get('at', '0')} < {STALE_MS}) "
        f"{{ state = {shared_get('left', chr(39) * 2)} || null; }}\r\n"
        "else {\r\n"
        + _left_compute()
        + "}\r\n"
    )


def clock():
    """`Visible` do primeiro item da coluna: calcula a maquina de estados uma
    vez e publica para os consumidores. Sempre visivel."""
    return js(
        BASE + _left_compute()
        + f"if ({HAS_SHARED}) {{ {shared_set('left', "state || ''")}; "
        f"{shared_set('session', "session || ''")}; "
        f"{shared_set('at', 'now')}; }}\r\n"
        "return true;"
    )


def right_prelude():
    """Define `newLap`: verdadeiro nos primeiros segundos de cada volta."""
    ms = int(DURATION["new_lap"] * 1000)
    return (
        BASE
        + "var nl = root.nl;\r\n"
        "if (nl == null) { nl = root.nl = { lap: lap, until: 0 }; }\r\n"
        f"if (lapDone(nl) && onTrack) nl.until = now + {ms};\r\n"
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


#: Tempo em texto, a regra do dash todo: volta em m:ss.f, abaixo de um minuto
#: (setor) em ss.f. Arredonda no decimo antes de quebrar em minutos, para
#: 59.96 virar "1:00.0" e nao "0:60.0".
FMT_TIME = (
    "var fmtTime = function (s) { var t = Math.round(s * 10); "
    "var m = Math.floor(t / 600); var r = t - m * 600; "
    "var ss = Math.floor(r / 10) + '.' + (r % 10); "
    "return m > 0 ? m + ':' + (r < 100 ? '0' : '') + ss : ss; };\r\n"
)

#: Formatos comuns, com as mesmas regras dos setores: nulo ou zero vira N/A,
#: acima de 99 s vira OFF. Delta sempre com um decimal (s.f).
FORMAT = (
    "var sec = function (v) { if (v == null || v === '') return null; "
    "var s = typeof v === 'number' ? v : timespantoseconds(v); "
    "return (s == null || s <= 0 || isNaN(s)) ? null : s; };\r\n"
    + FMT_TIME +
    "var fmtLap = function (s) { return s == null ? 'N/A' : fmtTime(s); };\r\n"
    "var fmtDelta = function (d) { if (d == null) return 'N/A'; "
    "var r = Number(d.toFixed(1)); if (r == 0) return '0.0'; "
    "if (Math.abs(r) > 99) return 'OFF'; "
    "return (r > 0 ? '+' : '') + r.toFixed(1); };\r\n"
)


def color_delta(expression, faster, slower, neutral):
    """JS: cor de um delta (negativo = mais rapido), no decimo que aparece."""
    return (f"var d = {expression}; if (d == null) return '{neutral}'; "
            "var r = Number(d.toFixed(1)); "
            f"if (r == 0 || Math.abs(r) > 99) return '{neutral}'; "
            f"return r < 0 ? '{faster}' : '{slower}';")
