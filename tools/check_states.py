"""Testa as formulas JS dos estados temporarios no Node.

O preview e estatico e nao avalia formula nenhuma; aqui as formulas reais
(as mesmas strings que vao para o .djson) rodam no Node com `$prop`, `root`
e o relogio simulados, quadro a quadro, nos cenarios das regras:

  - carregar o dash nao dispara nada;
  - Lap Review so em corrida, so com volta fechada fora do pit, por 5 s;
  - Weather na saida do pit e ao entrar no carro numa corrida, por 10 s;
  - Damage no botao (3 s), em reparo que cresce e em aviso novo (5 s);
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

from dash import lap_review, right, states  # noqa: E402

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
        "newLap": expr(states.new_lap_visible()),
        "sectors": expr(states.sectors_visible()),
        "myLaps": expr(lap_review.collector_mine(
            "return me.laps ? String(me.laps) : 'N/A';")),
        "myAvg": expr(lap_review.collector_mine(
            "return fmtLap(me.n ? me.sum / me.n : null);")),
        "aheadAvg": expr(lap_review.collector_other(-1)),
        "fuelLog": right.FUEL_LOG_JS,
    }


HARNESS = r"""
const F = JSON.parse(process.argv[2]);
const BUTTON = process.argv[3];
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
function fresh() {
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
fresh(); base(); state();
set({ [T_ + 'PitOptRepairLeft']: 12 });
expect('reparo cresceu -> damage', tick(100), 'damage');
expect('damage de dano novo aos 4.9 s', tick(4800), 'damage');
expect('acaba aos 5 s', tick(200), null);
set({ [T_ + 'PitOptRepairLeft']: 4 });
expect('reparo diminuindo (no pit) -> nada', tick(100), null);
fresh(); base(); state();
set({ [T_ + 'EngineWarnings']: 0x40 });
expect('aviso novo -> damage', tick(100), 'damage');
expect('aviso persistente nao redispara', tick(5000), null);
set({ [T_ + 'EngineWarnings']: 0x40 | 0x10 });
expect('limitador nao conta como dano', tick(100), null);

fresh(); base({ [T_ + 'EngineWarnings']: 'PitSpeedLimiter' }); state();
set({ [T_ + 'EngineWarnings']: 'PitSpeedLimiter, OilTempWarning' });
expect('aviso como nome de enum -> damage', tick(100), 'damage');

// 6. Prioridade e retomada.
fresh(); base({ [T_ + 'OnPitRoad']: true }); state();
set({ [T_ + 'OnPitRoad']: false });
expect('weather', tick(100), 'weather');
set({ [BUTTON]: true });
expect('damage cobre weather', tick(1900), 'damage');
set({ [BUTTON]: false });
expect('weather volta depois do damage', tick(3000), 'weather');
fresh(); base(); state();
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
expect('media sem a volta de saida', avgShown, '1:22.500');
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
expect('media do piloto a frente (sem 99.0)', run.aheadAvg(), '1:22.300');

// 10. Consumo por volta no lap log, com root compartilhado entre as linhas
// e com um root por linha (o SimHub nao documenta qual dos dois).
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
  expect('volta medida; a que estava pela metade fica em branco' + tag, rows().map(v => v === '' ? v : +v.toFixed(2)), [2.3, '', '']);
  set({ [T_ + 'FuelLevel']: 44.2 }); rows();
  set({ [T_ + 'Lap']: 6 });
  expect('duas voltas medidas' + tag, rows().map(v => v === '' ? v : +v.toFixed(2)), [2.4, 2.3, '']);
  set({ [T_ + 'FuelLevel']: 60.0 }); rows();           // reabasteceu no meio da volta
  set({ [T_ + 'FuelLevel']: 59.0 }); rows();
  set({ [T_ + 'Lap']: 7 });
  expect('volta com reabastecimento fica fora' + tag, rows().map(v => v === '' ? v : +v.toFixed(2)), [2.31, 2.4, 2.3]);
}

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
        result = subprocess.run(
            [node, str(script), json.dumps(formulas()), BUTTON])
    return result.returncode or syntax


if __name__ == "__main__":
    sys.exit(main())
