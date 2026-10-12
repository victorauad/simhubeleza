"""Equivalencia do leaderboard reescrito com as formulas originais.

As formulas como estavam antes da reescrita de desempenho ficam em
`tools/fixtures/leaderboard_legacy.json` (tiradas do build, sem o envelope de
N/A). Aqui as duas versoes rodam no Node com os mesmos grids simulados --
milhares deles: classe de 1 a 63 carros, jogador em qualquer posicao ou sem
posicao, corrida/treino/sessao nula, piloto desconectado, sem volta, linhas
vagas -- e a saida de cada binding, linha por linha, tem que ser a mesma.

Diferencas aceitas, contadas a parte:

  - cores do overflow: o original nao tinha sido restilizado; agora usa a
    paleta da tabela principal (`OVERFLOW_COLORS`);
  - gap no treino de piloto (ou lider) sem volta: o original mostrava
    "+-82.9"; agora e N/A;
  - cor do gap de piloto desconectado no overflow, em corrida: o original
    lia `SessionTypeName` (que nao existe) e nunca reconhecia corrida;
  - gap no treino exatamente na casa do arredondamento (diferenca terminando
    em 5 centesimos): o original somava minutos, segundos e centesimos em
    ponto flutuante e as vezes arredondava para baixo.

Rode `build.py` antes.   python3 tools/check_leaderboard.py [N_GRIDS]
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash import leaderboard as lb  # noqa: E402
from dash.fallback import unwrap  # noqa: E402
from simhub.theme import PLAYER, TEXT, TEXT_TERTIARY  # noqa: E402

LEGACY = ROOT / "tools" / "fixtures" / "leaderboard_legacy.json"
BUILD = ROOT / "build" / "iRacing_Dashboard_00" / "iRacing_Dashboard_00.djson"
#: TEXT da paleta quando a fixture foi tirada. Cor de paleta, nao logica: o
#: legado roda com o TEXT atual no lugar dela.
LEGACY_TEXT = "#FFECEEF0"

#: Cor do overflow original -> cor da paleta atual, por binding.
OVERFLOW_COLORS = {
    "DriverContainer.BackgroundColor": {"White": lb.ROW_BG_PLAYER,
                                        "#FF1C1C1C": lb.ROW_BG},
    "DriverName.TextColor": {"Black": PLAYER, "#FF404040": lb.DISCONNECTED,
                             "Gray": TEXT},
    "DriverPosition.TextColor": {"DarkOrange": PLAYER, "Gray": TEXT_TERTIARY},
    "Gap.TextColor": {"#FF404040": lb.DISCONNECTED},
    "LastLapDifference.TextColor": {"#8800FF7F": lb.FASTER,
                                    "#88FF6347": lb.SLOWER},
}


def current():
    """As formulas do leaderboard no build atual, sem o envelope de N/A."""
    data = json.loads(BUILD.read_text(encoding="utf-8"))
    out = {}

    def walk(node, path):
        name = node.get("Name") or ""
        here = f"{path}/{name}"
        for target, binding in (node.get("Bindings") or {}).items():
            expression = (binding.get("Formula") or {}).get("Expression")
            if (expression and "/Standings/Leaderboard" in here
                    and not name.endswith(" N/A")):
                key = here.split("/Standings/")[1] + "." + target
                out[key] = unwrap(expression)
        for child in node.get("Childrens") or []:
            walk(child, here)

    for screen in data["Screens"]:
        for item in screen["Items"]:
            walk(item, "")
    return out


HARNESS = r"""
const [legacyPath, currentPath, colorsJson, nArg] = process.argv.slice(2);
const fs = require('fs');
const OLD = JSON.parse(fs.readFileSync(legacyPath, 'utf8'));
const NEW = JSON.parse(fs.readFileSync(currentPath, 'utf8'));
const COLORS = JSON.parse(colorsJson);
const N = Number(nArg);

// --- Stubs do SimHub -------------------------------------------------------
// TimeSpan chega como o ToString() do .NET: "hh:mm:ss" ou "hh:mm:ss.fffffff".
const parts = (v) => {
  const m = /^(\d+):(\d+):(\d+)(?:\.(\d+))?$/.exec(String(v));
  if (!m) return null;
  return { h: +m[1], m: +m[2], s: +m[3], f: m[4] ? +('0.' + m[4]) : 0 };
};
const timespantoseconds = (v) => {
  if (v == null) return null;
  if (typeof v === 'number') return v;
  const p = parts(v); if (!p) return null;
  return p.h * 3600 + p.m * 60 + p.s + p.f;
};
const pad = (n, w) => { const s = String(Math.abs(n)); return (n < 0 ? '-' : '') + '0'.repeat(Math.max(0, w - s.length)) + s; };
const format = (v, f) => {
  if (f === 'mm' || f === 'ss' || f === 'ff') {
    const p = parts(v); if (!p) return '';
    if (f === 'mm') return pad(p.m, 2);
    if (f === 'ss') return pad(p.s, 2);
    return pad(Math.floor(p.f * 100 + 1e-9), 2);
  }
  if (f === '00') return pad(Math.round(v), 2);
  const d = f === '0' ? 0 : f.length - 2;
  const m = Math.pow(10, d);
  const r = Math.sign(v) * Math.round(Math.abs(v) * m) / m;
  return r.toFixed(d);
};
let P = {}, R = 1;
const $prop = (name) => (name in P ? P[name] : null);
const repeatindex = () => R;
const compile = (body) => new Function('$prop', 'repeatindex', 'format',
  'timespantoseconds', body);
const run = (fn) => fn($prop, repeatindex, format, timespantoseconds);
const FO = {}, FN = {};
for (const k of Object.keys(OLD)) FO[k] = compile(OLD[k].Expression);
for (const k of Object.keys(NEW)) FN[k] = compile(NEW[k]);
const missing = Object.keys(OLD).filter(k => !(k in NEW));
const extra = Object.keys(NEW).filter(k => !(k in OLD));

// --- Grids simulados (PRNG fixo: o teste e reprodutivel) -------------------
let seed = 12345;
const rnd = () => { seed = (seed * 1103515245 + 12345) & 0x7fffffff; return seed / 0x7fffffff; };
const pick = (a) => a[Math.floor(rnd() * a.length)];
const ts = (sec) => {
  if (sec === 0) return '00:00:00';
  const h = Math.floor(sec / 3600), m = Math.floor(sec % 3600 / 60);
  const s = Math.floor(sec % 60), ticks = Math.round((sec % 1) * 1e7);
  return pad(h, 2) + ':' + pad(m, 2) + ':' + pad(s, 2) +
    (ticks ? '.' + String(ticks).padStart(7, '0') : '');
};
const lapTime = () => pick([0, 1]) ? Math.round((80 + rnd() * 15) * 1000) / 1000
  : Math.round((80 + rnd() * 15) * 100) / 100;
const B = 'IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_';
const ME = 'Driver Me';

function grid() {
  P = {};
  const F = pick([1, 3, 5, 10, 12, 13, 14, 15, 16, 20, 25, 40, 63]);
  const me = pick([0, ...Array.from({ length: F }, (_, j) => j + 1)]);
  const nullTail = rnd() < 0.2;
  for (let j = 0; j < 64; j++) {
    const k = B + pad(j, 2) + '_';
    if (j < F) {
      const isMe = j + 1 === me;
      P[k + 'Name'] = isMe ? ME : 'Driver ' + j;
      P[k + 'PositionInClass'] = rnd() < 0.05 ? 0 : j + 1;
      P[k + 'IsConnected'] = rnd() < 0.1 ? false : true;
      P[k + 'LastLapTime'] = ts(rnd() < 0.1 ? 0 : lapTime());
      P[k + 'BestLapTime'] = ts(rnd() < 0.08 ? 0 : lapTime());
      P[k + 'GapToLeaderString'] = j === 0 ? '0.0' : pick(['+1.2', '+12.7', '1L', '+0.4']);
    } else if (!nullTail) {
      P[k + 'Name'] = ''; P[k + 'PositionInClass'] = 0;
      P[k + 'IsConnected'] = false; P[k + 'LastLapTime'] = '00:00:00';
      P[k + 'BestLapTime'] = '00:00:00'; P[k + 'GapToLeaderString'] = '';
    }
  }
  P['PlayerClassOpponentsCount'] = F;
  P['IRacingExtraProperties.iRacing_Player_PositionInClass'] = me;
  P['DataCorePlugin.GameData.PlayerName'] = ME;
  P['LastLapTime'] = ts(rnd() < 0.15 ? 0 : lapTime());
  P['GameRawData.Telemetry.Lap'] = pick([0, 1, 2, 3, 7]);
  P['DataCorePlugin.GameRawData.Telemetry.LapBestLap'] = pick([0, 3]);
  P['GameRawData.CurrentSessionInfo.SessionType'] = pick(['Race', 'Race', 'Practice', 'Lone Qualify', null]);
  P['GameRawData.Telemetry.SessionNum'] = 0;
  P['GameRawData.SessionData.SessionInfo.Sessions01.SessionType'] = pick(['Race', 'Practice']);
}

const counts = { compared: 0, colors: 0, noLap: 0, rounding: 0, session: 0, format: 0 };
const fails = [];
function compare(key, extraInfo) {
  let a, b;
  try { a = run(FO[key]); } catch (e) { a = 'ERRO ' + e.message; }
  try { b = run(FN[key]); } catch (e) { b = 'ERRO ' + e.message; }
  counts.compared++;
  if (a === b) return;
  const short = key.replace(/^Leaderboard( Overflow)?\//, '');
  if (key.startsWith('Leaderboard Overflow/') && COLORS[short] && COLORS[short][a] === b) {
    counts.colors++; return;
  }
  // O original do overflow lia `SessionTypeName`, que nao existe: nunca
  // reconhecia corrida, e o desconectado ficava cinza.
  if (key === 'Leaderboard Overflow/Gap.TextColor' && a === 'Gray' &&
      b === COLORS['Gap.TextColor']['#FF404040'] &&
      (P['GameRawData.CurrentSessionInfo.SessionType'] ||
       P['GameRawData.SessionData.SessionInfo.Sessions01.SessionType']) === 'Race') {
    counts.session++; return;
  }
  // Tempos e deltas em uma casa (m:ss.f / s.f): o mesmo numero, arredondado.
  if (typeof a === 'string' && typeof b === 'string' && /(Gap|LastLapDifference)\.Text$/.test(key)) {
    const val = (t) => { const m = /^([+-]?)(?:(\d+):)?(\d+(?:\.\d+)?)$/.exec(t.trim());
      return m ? (m[1] === '-' ? -1 : 1) * ((m[2] ? +m[2] * 60 : 0) + +m[3]) : null; };
    const va = val(a), vb = val(b);
    if (va !== null && vb !== null && !/\.\d\d/.test(b) && Math.abs(va - vb) <= 0.0501 &&
        a.trim()[0] === b.trim()[0]) { counts.format++; return; }
  }
  if (key === 'Leaderboard/Gap.Text' && typeof a === 'string' && a.startsWith('+')) {
    const idx = R - 1;
    const cs = (v) => { const s = timespantoseconds(v); return Math.floor((s % 3600) * 100 + 1e-6); };
    const mine = cs(P[B + pad(idx, 2) + '_BestLapTime']), lead = cs(P[B + '00_BestLapTime']);
    if (b === null && (mine === 0 || lead === 0)) { counts.noLap++; return; }
    if (typeof b === 'string' && Math.abs(mine - lead) % 10 === 5 &&
        Math.abs(parseFloat(a.slice(1)) - parseFloat(b.slice(1))) <= 0.1001) { counts.rounding++; return; }
  }
  if (key === 'Leaderboard/Gap.Text') extraInfo = [P[B + pad(R - 1, 2) + '_BestLapTime'], P[B + '00_BestLapTime']];
  if (fails.length < 15) fails.push({ key, row: R, legacy: a, now: b, extraInfo });
  else fails.push(null);
}

for (let n = 0; n < N; n++) {
  grid();
  R = 1;
  compare('Leaderboard.Repetitions');
  compare('Leaderboard Overflow.Visible');
  for (R = 1; R <= 13; R++)
    for (const k of Object.keys(OLD))
      if (k.startsWith('Leaderboard/')) compare(k);
  for (R = 1; R <= 7; R++)
    for (const k of Object.keys(OLD))
      if (k.startsWith('Leaderboard Overflow/')) compare(k);
}

if (missing.length) console.log('FALTANDO no build: ' + missing.join(', '));
if (extra.length) console.log('a mais no build (sem original): ' + extra.join(', '));
console.log(`${N} grids, ${counts.compared} avaliacoes comparadas`);
console.log(`aceitas: ${counts.colors} cor do overflow, ${counts.noLap} gap sem volta -> N/A, ` +
  `${counts.rounding} arredondamento na casa de 5 centesimos, ` +
  `${counts.session} desconectado no overflow em corrida`);
for (const f of fails.filter(Boolean))
  console.log('FAIL ' + JSON.stringify(f));
const bad = fails.length + missing.length;
console.log(bad ? `\n${fails.length} diferenca(s)` : '\nequivalente');
process.exit(bad ? 1 : 0);
"""


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    grids = int(argv[0]) if argv else 3000
    node = shutil.which("node")
    if node is None:
        print("node nao encontrado -- nada testado", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "now.json").write_text(json.dumps(current()), encoding="utf-8")
        (tmp / "check.js").write_text(HARNESS, encoding="utf-8")
        legacy = LEGACY.read_text(encoding="utf-8").replace(LEGACY_TEXT, TEXT)
        (tmp / "legacy.json").write_text(legacy, encoding="utf-8")
        return subprocess.run(
            [node, str(tmp / "check.js"), str(tmp / "legacy.json"), str(tmp / "now.json"),
             json.dumps(OVERFLOW_COLORS), str(grids)]).returncode


if __name__ == "__main__":
    sys.exit(main())
