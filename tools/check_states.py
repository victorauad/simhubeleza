"""Testa as formulas JS dos estados temporarios no Node.

O preview e estatico e nao avalia formula nenhuma; aqui as formulas reais
(as mesmas strings que vao para o .djson) rodam no Node com `$prop`, `root`
e o relogio simulados, quadro a quadro, nos cenarios das regras:

  - carregar o dash nao dispara nada;
  - Lap Review so em corrida, so com volta fechada fora do pit, por 5 s;
  - Weather na saida do pit e ao entrar no carro numa corrida, por 10 s;
  - Damage no botao (3 s), em reparo que cresce e em aviso novo (5 s) --
    so 3 s depois de entrar na pista, e pressao com motor desligado nao conta;
  - prioridade Damage > Weather > Lap Review, com retomada;
  - grafico e setores escondidos exatamente quando o estado aparece;
  - coletores: voltas e media do stint (minha e dos outros).

Antes, compila (so sintaxe) toda formula JS do build -- rode `build.py`
primeiro.

    python3 tools/check_states.py        (precisa de `node` no PATH)
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash import fallback, lap_review, right, states  # noqa: E402
from simhub.bindings import js  # noqa: E402

BUTTON = "InputStatus.JoystickPlugin.Wheel_B14"


def expr(binding):
    return binding["Formula"]["Expression"]


def formulas():
    states.DAMAGE_BUTTON = BUTTON
    return {
        "damage": expr(states.showing("damage")),
        "weather": expr(states.showing("weather")),
        "review": expr(states.showing("review")),
        "chart": expr(states.chart_visible()),
        "clock": expr(states.clock()),
        "newLap": expr(states.new_lap_visible()),
        "sectors": expr(states.sectors_visible()),
        "standings": right.SHOW_STANDINGS_JS,
        "relative": right.SHOW_RELATIVE_JS,
        "myLaps": expr(lap_review.collector_mine(
            "return me.laps ? String(me.laps) : 'N/A';")),
        "myAvg": expr(lap_review.collector_mine(
            "return fmtLap(me.n ? me.sum / me.n : null);")),
        "aheadAvg": expr(lap_review.collector_other(-1)),
        # Com o envelope de N/A do build, como vai para o .djson.
        "fuelLog": fallback.wrap_js(right.FUEL_LOG_JS),
        "trackLog": fallback.wrap_js(right.TRACK_LOG_JS),
        "validRec": expr(states.valid_recorder()),
        "validLog": fallback.wrap_js(right.VALID_LOG_JS + right.VALID_TEXT),
        "validNow": fallback.wrap_js(
            states.BASE + states.VALIDITY
            + "var v = validNow(); return v == null ? null : v;"),
        "naValue": fallback.wrap_js("return $prop('X');"),
        "naRow": fallback.wrap_js("return $prop('X');", "$prop('Row') != 0"),
        "naTwin": fallback._twin(
            {"Name": "LastLapDifference", "Bindings": {"Visible": js(
                "if ($prop('Show')) return 1; else return 0;")}},
            fallback.HIDDEN["Standings/Leaderboard/LastLapDifference"],
        )["Bindings"]["Visible"]["Formula"]["Expression"],
    }


HARNESS = r"""
const F = JSON.parse(process.argv[2]);
const BUTTON = process.argv[3];
// 'shared': armazenamento compartilhado do SimHub presente, com o relogio
// (states.clock) publicando antes dos consumidores. 'solo': sem ele, cada
// consumidor calcula sozinho.
const SHARED = process.argv[4] === 'shared';
let STORE = new Map();
if (SHARED) {
  globalThis.setsharedvalue = (s, k, v) => { STORE.set(s + '/' + k, v); return v; };
  globalThis.getsharedvalueordefault = (s, k, d) =>
    STORE.has(s + '/' + k) ? STORE.get(s + '/' + k) : d;
}
let CLOCK = true;
console.log('-- modo ' + (SHARED ? 'compartilhado' : 'solo'));
let T = 1000000;
Date.now = () => T;
const timespantoseconds = (v) => v;
const format = (v) => String(v);
let P = {};
const $prop = (name) => (name in P ? P[name] : null);
const run = {};
for (const k of Object.keys(F)) {
  const fn = new Function('root', '$prop', 'timespantoseconds', 'format', F[k]);
  const root = {};
  run[k] = () => fn(root, $prop, timespantoseconds, format);
}
const T_ = 'GameRawData.Telemetry.';
const S_ = 'GameRawData.SessionData.SessionInfo.';
function base(over) {
  P = Object.assign({
    [T_ + 'Lap']: 5, [T_ + 'OnPitRoad']: false, [T_ + 'IsOnTrack']: true,
    [T_ + 'SessionNum']: 2,
    [S_ + 'Sessions03.SessionType']: 'Race',
    [T_ + 'PitRepairLeft']: 0, [T_ + 'PitOptRepairLeft']: 0,
    [T_ + 'EngineWarnings']: 0, [BUTTON]: false,
    'DataCorePlugin.GameData.LastLapTime': 82.5,
    'IRacingExtraProperties.iRacing_Player_PositionInClass': 2,
  }, over || {});
}
function set(over) { Object.assign(P, over); }
function state() {
  if (CLOCK) run.clock();
  const s = ['damage', 'weather', 'review'].filter(k => run[k]());
  const chart = run.chart();
  if (s.length > 1) throw new Error('dois estados juntos: ' + s);
  if (chart === (s.length === 1)) throw new Error('grafico e estado juntos');
  return s[0] || null;
}
let fails = 0;
function expect(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) fails++;
  console.log((ok ? 'ok   ' : 'FAIL ') + label + (ok ? '' : `  (veio ${JSON.stringify(got)}, esperava ${JSON.stringify(want)})`));
}
function tick(ms) { T += ms; return state(); }
// Passa a janela de assentamento (3 s apos entrar na pista) sem nada.
function settle() { tick(3000); }
function fresh() {
  STORE = new Map(); CLOCK = true;
  for (const k of Object.keys(F)) {
    const fn = new Function('root', '$prop', 'timespantoseconds', 'format', F[k]);
    const root = {};
    run[k] = () => fn(root, $prop, timespantoseconds, format);
  }
}

// 1. Carregar no meio de tudo nao dispara.
fresh(); base({ [T_ + 'PitRepairLeft']: 30, [T_ + 'EngineWarnings']: 0x40 });
expect('carregar nao dispara', state(), null);

// 2. Lap Review em corrida.
fresh(); base(); state();
set({ [T_ + 'Lap']: 6 });
expect('volta nova em corrida -> review', tick(100), 'review');
expect('review aos 4.9 s', tick(4800), 'review');
expect('review acaba aos 5 s', tick(200), null);

// 3. Volta fechada no pit nao conta; treino nao conta.
fresh(); base({ [T_ + 'OnPitRoad']: true }); state();
set({ [T_ + 'Lap']: 6 });
expect('volta pelo pit -> nada', tick(100), null);
fresh(); base({ [S_ + 'Sessions03.SessionType']: 'Practice' }); state();
set({ [T_ + 'Lap']: 6 });
expect('treino -> nada', tick(100), null);

// 4. Weather: saida do pit e entrada no carro em corrida.
fresh(); base({ [T_ + 'OnPitRoad']: true }); state();
set({ [T_ + 'OnPitRoad']: false });
expect('saida do pit -> weather', tick(100), 'weather');
expect('weather aos 9.9 s', tick(9800), 'weather');
expect('weather acaba aos 10 s', tick(200), null);
fresh(); base({ [T_ + 'IsOnTrack']: false }); state();
set({ [T_ + 'IsOnTrack']: true });
expect('entrou no carro em corrida -> weather', tick(100), 'weather');
fresh(); base({ [T_ + 'IsOnTrack']: false, [S_ + 'Sessions03.SessionType']: 'Practice' }); state();
set({ [T_ + 'IsOnTrack']: true });
expect('entrou no carro em treino -> nada', tick(100), null);

// 5. Damage: botao, reparo, aviso.
fresh(); base(); state();
set({ [BUTTON]: true });
expect('botao -> damage', tick(100), 'damage');
expect('segurar o botao nao estende', tick(2800), 'damage');
expect('damage do botao acaba aos 3 s', tick(200), null);
fresh(); base(); state(); settle();
set({ [T_ + 'PitOptRepairLeft']: 12 });
expect('reparo cresceu -> damage', tick(100), 'damage');
expect('damage de dano novo aos 4.9 s', tick(4800), 'damage');
expect('acaba aos 5 s', tick(200), null);
set({ [T_ + 'PitOptRepairLeft']: 4 });
expect('reparo diminuindo (no pit) -> nada', tick(100), null);
fresh(); base(); state(); settle();
set({ [T_ + 'EngineWarnings']: 0x40 });
expect('aviso novo -> damage', tick(100), 'damage');
expect('aviso persistente nao redispara', tick(5000), null);
set({ [T_ + 'EngineWarnings']: 0x40 | 0x10 });
expect('limitador nao conta como dano', tick(100), null);

fresh(); base({ [T_ + 'EngineWarnings']: 'PitSpeedLimiter' }); state(); settle();
set({ [T_ + 'EngineWarnings']: 'PitSpeedLimiter, OilTempWarning' });
expect('aviso como nome de enum -> damage', tick(100), 'damage');

// Grid: dash carregado / carro posto na pista com motor desligado.
fresh(); base({ 'GameRawData.Telemetry.RPM': 0 }); state(); settle();
set({ [T_ + 'EngineWarnings']: 0x02 | 0x04 });
expect('motor desligado: pressao baixa nao e dano', tick(100), null);
set({ [T_ + 'EngineWarnings']: 0x02 | 0x04 | 0x08, 'GameRawData.Telemetry.RPM': 900 });
expect('motor morto (stalled): pressao baixa nao e dano', tick(100), null);
fresh(); base({ [T_ + 'IsOnTrack']: false }); state();
set({ [T_ + 'IsOnTrack']: true, [T_ + 'EngineWarnings']: 0x40 });
expect('aviso logo ao entrar na pista nao e damage', tick(100) === 'damage', false);
expect('nem depois de assentar', tick(3000) === 'damage', false);

// 6. Prioridade e retomada.
fresh(); base({ [T_ + 'OnPitRoad']: true }); state();
set({ [T_ + 'OnPitRoad']: false });
expect('weather', tick(100), 'weather');
set({ [BUTTON]: true });
expect('damage cobre weather', tick(1900), 'damage');
set({ [BUTTON]: false });
expect('weather volta depois do damage', tick(3000), 'weather');
fresh(); base(); state(); settle();
set({ [T_ + 'Lap']: 6 });
expect('review', tick(100), 'review');
set({ [T_ + 'PitRepairLeft']: 40 });
expect('damage cobre review', tick(1000), 'damage');
expect('review ja expirou quando damage acaba', tick(5000), null);

// 7. Direita: New Lap Info x setores.
fresh(); base(); run.newLap(); run.sectors();
set({ [T_ + 'Lap']: 6 }); T += 100;
expect('volta nova -> new lap info', [run.newLap(), run.sectors()], [true, false]);
T += 5000;
expect('5 s depois -> setores', [run.newLap(), run.sectors()], [false, true]);
fresh(); base({ [T_ + 'IsOnTrack']: false }); run.newLap();
set({ [T_ + 'Lap']: 6 }); T += 100;
expect('fora da pista -> sem new lap info', run.newLap(), false);

// 7b. Direita: Standings x Relative.
function col() {
  const st = run.standings(), rel = run.relative();
  if (st === rel) throw new Error('standings e relative juntos/nenhum');
  return st ? 'standings' : 'relative';
}
fresh(); base({ [T_ + 'SessionState']: 4 });
expect('correndo -> relative', col(), 'relative');
set({ [T_ + 'SessionState']: 'Racing' });
expect('correndo (enum) -> relative', col(), 'relative');
set({ [T_ + 'IsOnTrack']: false });
expect('fora do carro -> standings', col(), 'standings');
set({ [T_ + 'IsReplayPlaying']: true });
expect('replay -> relative', col(), 'relative');
set({ [T_ + 'IsReplayPlaying']: false, [T_ + 'IsOnTrack']: true, [T_ + 'IsInGarage']: 'True' });
expect('garagem -> standings', col(), 'standings');
set({ [T_ + 'IsInGarage']: false, [T_ + 'SessionState']: 1 });
expect('grid (GetInCar) -> standings', col(), 'standings');
set({ [T_ + 'SessionState']: 'Warmup' });
expect('grid (Warmup) -> standings', col(), 'standings');
set({ [T_ + 'SessionState']: 3 });
expect('volta de apresentacao -> relative', col(), 'relative');
set({ [T_ + 'SessionState']: 4, [T_ + 'Lap']: 6 }); T += 100;
expect('volta completa -> standings', col(), 'standings');
T += 4800;
expect('standings aos 4.9 s', col(), 'standings');
T += 200;
expect('relative aos 5 s', col(), 'relative');
fresh(); base({ [T_ + 'IsOnTrack']: false, [T_ + 'IsReplayPlaying']: true }); col();
set({ [T_ + 'Lap']: 6 }); T += 100;
expect('volta completa em replay -> standings', col(), 'standings');
fresh(); base({ [S_ + 'Sessions03.SessionType']: 'Offline Testing', [T_ + 'IsOnTrack']: false });
expect('treino solo -> nenhum (modo Practice)', [run.standings(), run.relative()], [false, false]);

// 7c. Largada: a primeira virada de volta (carro saiu antes da linha) nao
// conta como volta completa -- nem Lap Review, nem New Lap Info, nem Standings.
function all() { return [state(), run.newLap(), col()]; }
fresh(); base({ [T_ + 'SessionState']: 4, [T_ + 'Lap']: 0, [T_ + 'LapDistPct']: 0.97 });
settle(); all();
set({ [T_ + 'Lap']: 1, [T_ + 'LapDistPct']: 0.01 }); T += 100;
expect('largada: cruzar a linha nao conta', all(), [null, false, 'relative']);
for (const pct of [0.3, 0.6, 0.98]) { set({ [T_ + 'LapDistPct']: pct }); T += 100; all(); }
set({ [T_ + 'Lap']: 2, [T_ + 'LapDistPct']: 0.01 }); T += 100;
expect('primeira volta completa conta', all(), ['review', true, 'standings']);
fresh(); base({ [T_ + 'SessionState']: 4, [T_ + 'Lap']: 3, [T_ + 'LapDistPct']: 0.6 });
settle(); all();
set({ [T_ + 'Lap']: 4, [T_ + 'LapDistPct']: 0.01 }); T += 100;
expect('dash aberto no meio da volta: a virada conta', all(), ['review', true, 'standings']);
fresh(); base({ [T_ + 'SessionState']: 4, [T_ + 'Lap']: 0, [T_ + 'LapDistPct']: 0.97,
  'DataCorePlugin.GameData.LastLapTime': null });
function laps() { state(); return run.myLaps(); }
settle(); laps();
set({ [T_ + 'Lap']: 1, [T_ + 'LapDistPct']: 0.01 }); T += 100; laps();
for (const pct of [0.5, 0.99]) { set({ [T_ + 'LapDistPct']: pct }); T += 100; laps(); }
set({ [T_ + 'Lap']: 2, [T_ + 'LapDistPct']: 0.01 }); T += 100;
expect('largada fora da contagem do stint', laps(), '1');

// 8. Coletor do jogador: voltas do stint e media sem volta de saida.
fresh(); base({ [T_ + 'Lap']: 1, [T_ + 'OnPitRoad']: true, 'DataCorePlugin.GameData.LastLapTime': null });
run.myLaps(); run.myAvg();
function lapDone(time, pit) {
  set({ [T_ + 'Lap']: P[T_ + 'Lap'] + 1, [T_ + 'OnPitRoad']: !!pit });
  T += 100; run.myLaps(); run.myAvg();
  set({ 'DataCorePlugin.GameData.LastLapTime': time });
  T += 500; run.myLaps(); run.myAvg();
}
// Sai do pit (o Weather da saida dura 10 s e tem prioridade: espera).
set({ [T_ + 'OnPitRoad']: false }); T += 100; run.myLaps(); run.myAvg();
T += 11000; run.myLaps(); run.myAvg();
lapDone(95.0);           // volta de saida (comecou no pit)
lapDone(82.0);
lapDone(83.0);
set({ [T_ + 'Lap']: P[T_ + 'Lap'] + 1 }); T += 100;
const lapsShown = run.myLaps(), avgShown = run.myAvg();
expect('voltas do stint (review)', lapsShown, '4');
expect('media sem a volta de saida', avgShown, '1:22.5');
// No SimHub os dois coletores rodam em todo quadro: aqui tambem.
set({ [T_ + 'OnPitRoad']: true }); T += 6000; run.myLaps(); run.myAvg();
set({ [T_ + 'OnPitRoad']: false }); T += 100; run.myLaps(); run.myAvg();
T += 11000; run.myLaps(); run.myAvg();
set({ [T_ + 'Lap']: P[T_ + 'Lap'] + 1 }); T += 100;
expect('passou pelo pit: stint recomeca (1 volta, sem media)', [run.myLaps(), run.myAvg()], ['1', 'N/A']);

// 9. Coletor dos outros: o piloto a frente, sem a volta fora da curva.
const B = 'IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_';
fresh(); base({ 'IRacingExtraProperties.iRacing_Player_PositionInClass': 2,
  [B + '00_Name']: 'Nojiri', [B + '00_LastLapTime']: 82.0, [B + '00_BestLapTime']: 81.9,
  [B + '01_Name']: 'Me', [B + '01_LastLapTime']: 82.5, [B + '01_BestLapTime']: 82.4 });
run.aheadAvg();
for (const t of [82.4, 99.0, 82.2]) { set({ [B + '00_LastLapTime']: t }); T += 2100; run.aheadAvg(); }
set({ [T_ + 'Lap']: 6 }); T += 2100;
expect('media do piloto a frente (sem 99.0)', run.aheadAvg(), '1:22.3');

// 10. Consumo por volta no lap log, com root compartilhado entre as linhas
// e com um root por linha (o SimHub nao documenta qual dos dois).
const num = v => (typeof v === 'number' ? +v.toFixed(2) : v);
for (const shared of [true, false]) {
  const fn = new Function('root', '$prop', 'repeatindex', F.fuelLog);
  const roots = [{}, {}, {}];
  const rows = () => [1, 2, 3].map(r => fn(shared ? roots[0] : roots[r - 1], $prop, () => r));
  const tag = shared ? ' (root unico)' : ' (root por linha)';
  base({ [T_ + 'Lap']: 3, [T_ + 'FuelLevel']: 50.0,
         'DataCorePlugin.Computed.Fuel_LastLapConsumption': 2.31 });
  rows();
  set({ [T_ + 'FuelLevel']: 48.9 }); rows();           // volta 3 pela metade: nao conta
  set({ [T_ + 'Lap']: 4 }); rows();
  set({ [T_ + 'FuelLevel']: 46.6 }); rows();
  set({ [T_ + 'Lap']: 5 });
  expect('volta medida; a que estava pela metade fica N/A' + tag, rows().map(num), [2.3, 'N/A', 'N/A']);
  set({ [T_ + 'FuelLevel']: 44.2 }); rows();
  set({ [T_ + 'Lap']: 6 });
  expect('duas voltas medidas' + tag, rows().map(num), [2.4, 2.3, 'N/A']);
  set({ [T_ + 'FuelLevel']: 60.0 }); rows();           // reabasteceu no meio da volta
  set({ [T_ + 'FuelLevel']: 59.0 }); rows();
  set({ [T_ + 'Lap']: 7 });
  expect('volta com reabastecimento fica fora' + tag, rows().map(num), [2.31, 2.4, 2.3]);
  set({ [T_ + 'Lap']: 2, 'DataCorePlugin.Computed.Fuel_LastLapConsumption': null });
  expect('volta sem medida: N/A; volta que nao existe: vazio' + tag, rows().map(num), ['N/A', '', '']);
}

// 10b. Temperatura da pista por volta, nos dois jeitos de root.
for (const shared of [true, false]) {
  const fn = new Function('root', '$prop', 'repeatindex', F.trackLog);
  const roots = [{}, {}, {}];
  const rows = () => [1, 2, 3].map(r => fn(shared ? roots[0] : roots[r - 1], $prop, () => r));
  const tag = shared ? ' (root unico)' : ' (root por linha)';
  base({ [T_ + 'Lap']: 3, [T_ + 'TrackTemp']: 30.0 });
  expect('pista: dash recem-aberto, so a leitura atual' + tag, rows(), [30, 'N/A', '']);
  set({ [T_ + 'TrackTemp']: 31.0 }); rows();
  set({ [T_ + 'Lap']: 4, [T_ + 'TrackTemp']: 32.0 });
  expect('pista: volta 3 gravada com a ultima leitura dela' + tag, rows(), [31, 'N/A', 'N/A']);
  set({ [T_ + 'TrackTemp']: null }); rows();
  set({ [T_ + 'Lap']: 5 });
  expect('pista: leitura sumiu, fica a ultima valida' + tag, rows(), [32, 31, 'N/A']);
  set({ [T_ + 'Lap']: 2 });
  expect('pista: sessao nova zera; sem leitura, N/A' + tag, rows(), ['N/A', '', '']);
}

// 10c. Validade por volta: o gravador sempre visivel publica; o lap log
// (root por linha) e o "Now" leem. Volta suja em qualquer leitura = INV.
{
  const C = 'IRacingExtraProperties.iRacing_Player_CurrentLapIsClean';
  const fn = new Function('root', '$prop', 'repeatindex', F.validLog);
  const roots = [{}, {}, {}];
  const rows = () => [1, 2, 3].map(r => fn(roots[r - 1], $prop, () => r));
  const step = (ms) => { T += ms; run.validRec(); return rows(); };
  STORE = new Map();
  base({ [T_ + 'Lap']: 3, [C]: true });
  expect('validade: dash recem-aberto, nada gravado', step(0), ['N/A', 'N/A', '']);
  step(2000); set({ [T_ + 'Lap']: 4 }); step(100);
  expect('validade: volta 3 so foi vista pela metade e conta', step(2000), ['OK', 'N/A', 'N/A']);
  expect('validade: volta atual limpa', run.validNow(), 1);
  set({ [C]: false }); step(2000);
  expect('validade: volta atual suja', run.validNow(), 0);
  set({ [C]: true }); step(2000);
  expect('validade: volta suja continua INV mesmo limpando depois', run.validNow(), 0);
  set({ [T_ + 'Lap']: 5 }); step(100);
  expect('validade: virada de volta (janela de graca)', run.validNow(), 1);
  expect('validade: log com a volta suja', step(2000), ['INV', 'OK', 'N/A']);
  set({ [T_ + 'Lap']: 7 }); step(100); step(2000);
  expect('validade: contagem pulou 5 -> 7, voltas 5 e 6 ficam N/A', rows(), ['N/A', 'N/A', 'INV']);
  set({ [C]: null }); step(2000);
  expect('validade: sem a propriedade, Now fica N/A', run.validNow(), 'N/A');
}

// 11. Envelope de N/A (dash/fallback.py): dado ausente nunca fica em branco;
// vazio so quando a formula diz que a linha nao existe.
const na = (vals) => { set(vals); return [run.naValue(), run.naRow()]; };
base({});
expect('propriedade ausente vira N/A', na({ Row: 1 }), ['N/A', 'N/A']);
expect('NaN vira N/A', na({ X: NaN, Row: 1 }), ['N/A', 'N/A']);
expect('zero e valor, nao N/A', na({ X: 0, Row: 1 }), [0, 0]);
expect("'' de proposito continua vazio", na({ X: '', Row: 1 }), ['', '']);
expect('linha que nao existe fica vazia', na({ X: null, Row: 0 }), ['N/A', '']);

// 12. Gemeo N/A de campo que o original esconde sem dado (diferenca de
// volta do leaderboard): aparece so na linha de outro piloto.
{
  const fn = new Function('root', '$prop', 'repeatindex', 'format', F.naTwin);
  const pad = (v) => ('0' + v).slice(-2);
  const twin = (row) => fn({}, $prop, () => row, pad);
  base({ 'IRacingExtraProperties.iRacing_Player_PositionInClass': 2,
    [B + '00_PositionInClass']: 1, [B + '01_PositionInClass']: 2, [B + '02_PositionInClass']: 0 });
  set({ Show: 0 });
  expect('escondido: N/A no outro piloto, vazio na minha linha e na vaga',
    [twin(1), twin(2), twin(3)], [1, 0, 0]);
  set({ Show: 1 });
  expect('com dado: o gemeo some', [twin(1), twin(2), twin(3)], [0, 0, 0]);
}

// 13. Tipo de sessao: a sessao corrente pronta vale mais que a montada pelo
// indice.
fresh(); base({ 'GameRawData.CurrentSessionInfo.SessionType': 'Practice' }); state();
set({ [T_ + 'Lap']: 6 });
expect('CurrentSessionInfo = Practice -> sem review', tick(100), null);
fresh(); base({ 'GameRawData.CurrentSessionInfo.SessionType': 'Race',
  [S_ + 'Sessions03.SessionType']: 'Practice' }); state();
set({ [T_ + 'Lap']: 6 });
expect('CurrentSessionInfo = Race -> review', tick(100), 'review');

// 14. Relogio parado: depois de 1 s sem publicacao, os consumidores
// calculam sozinhos e continuam de acordo entre si e com o grafico.
fresh(); base(); state();
CLOCK = false;
tick(1100);
set({ [T_ + 'Lap']: 6 });
expect('sem relogio, volta nova -> review', tick(100), 'review');
expect('sem relogio, acaba aos 5 s', tick(5000), null);

console.log(fails ? `\n${fails} falha(s)` : '\ntudo ok');
process.exit(fails ? 1 : 0);
"""


SYNTAX = r"""
const fs = require('fs');
const forms = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let bad = 0;
for (const [where, code] of forms) {
  try { new Function('root', '$prop', code); }
  catch (e) { bad++; console.log('FAIL sintaxe: ' + where + ' -- ' + e.message); }
}
console.log(`sintaxe: ${forms.length - bad}/${forms.length} formulas JS do build compilam`);
process.exit(bad ? 1 : 0);
"""


def built_formulas():
    """(caminho, codigo) de toda formula JS do dash gerado."""
    out = []

    def walk(node, path):
        if isinstance(node, dict):
            name = node.get("Name") or ""
            for key, binding in (node.get("Bindings") or {}).items():
                formula = (binding or {}).get("Formula") or {}
                if formula.get("Interpreter") == 1:
                    out.append((f"{path}/{name}.{key}", formula["Expression"]))
            for child in node.get("Childrens") or []:
                walk(child, f"{path}/{name}")
            for screen in node.get("Screens") or []:
                for item in screen.get("Items") or []:
                    walk(item, path)

    for djson in (ROOT / "build" / "iRacing_Dashboard_00").glob("*.djson"):
        walk(json.loads(djson.read_text(encoding="utf-8")), djson.stem)
    return out


def main():
    node = shutil.which("node")
    if node is None:
        print("node nao encontrado -- nada testado", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "forms.json"
        data.write_text(json.dumps(built_formulas()), encoding="utf-8")
        script = Path(tmp) / "syntax.js"
        script.write_text(SYNTAX, encoding="utf-8")
        syntax = subprocess.run([node, str(script), str(data)]).returncode
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "check_states.js"
        script.write_text(HARNESS, encoding="utf-8")
        codes = [subprocess.run(
            [node, str(script), json.dumps(formulas()), BUTTON, mode]).returncode
            for mode in ("solo", "shared")]
    return max(codes) or syntax


if __name__ == "__main__":
    sys.exit(main())
