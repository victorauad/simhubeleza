#!/usr/bin/env python3
"""Testa o gravador da volta de referencia do dash minimal (Node).

Roda a formula `trace.RECORDER` do jeito que o SimHub roda -- uma chamada por
quadro, com o mesmo `root` -- sobre voltas simuladas, e confere:

  - a volta em que o dash foi carregado (pela metade) nunca vira referencia;
  - a primeira volta completa e limpa vira referencia;
  - uma volta mais lenta nao troca a referencia, uma mais rapida troca;
  - volta suja (fora dos limites) ou com passagem pelo pit nao vale;
  - o valor publicado e o da referencia no ponto atual e WINDOW_S a frente;
  - a virada do LapDistPct um quadro antes da volta nao invalida nada.

Uso:  python3 build.py && python3 tools/check_minimal.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from dash.minimal import trace  # noqa: E402

HARNESS = r"""
var formula = new Function('root', '$prop', 'setsharedvalue',
                           'getsharedvalueordefault', FORMULA);
var shared = {};
var setsharedvalue = function (s, k, v) { shared[k] = v; };
var getsharedvalueordefault = function (s, k, d) { return k in shared ? shared[k] : d; };
var root = {};
var state = {};
var $prop = function (name) { return state[name]; };
var LEN = 5000, FPS = 60, failures = [];

// Uma volta a velocidade constante: acelerador = marca da volta, freio =
// trecho da pista (para conferir a leitura a frente).
function lap(number, seconds, opts) {
  opts = opts || {};
  var frames = Math.round(seconds * FPS), start = opts.from || 0;
  for (var f = 0; f < frames; f++) {
    var pct = start + (1 - start) * f / frames;
    state['GameRawData.Telemetry.LapDistPct'] = pct;
    state['DataCorePlugin.GameData.CurrentLap'] = number;
    state['GameRawData.Telemetry.SessionTime'] = (state.t || 0) + 1 / FPS;
    state.t = state['GameRawData.Telemetry.SessionTime'];
    state['DataCorePlugin.GameData.Throttle'] = opts.mark;
    state['DataCorePlugin.GameData.Brake'] = Math.floor(pct * 100);
    state['DataCorePlugin.GameData.SpeedKmh'] = LEN / seconds * 3.6;
    state['IRacingExtraProperties.iRacing_Player_CurrentLapIsClean'] =
      !(opts.dirty && f == Math.floor(frames / 2));
    state['DataCorePlugin.GameData.IsInPitLane'] =
      opts.pit && f < frames / 10 ? 1 : 0;
    formula(root, $prop, setsharedvalue, getsharedvalueordefault);
  }
  // O LapDistPct vira um quadro antes da volta.
  state['GameRawData.Telemetry.LapDistPct'] = 0.0001;
  formula(root, $prop, setsharedvalue, getsharedvalueordefault);
}

// Primeiro quadro da volta seguinte: e quando a volta que acabou e julgada.
function cross(number) {
  state['DataCorePlugin.GameData.CurrentLap'] = number;
  state['GameRawData.Telemetry.LapDistPct'] = 0.0005;
  formula(root, $prop, setsharedvalue, getsharedvalueordefault);
}

function expect(what, got, want) {
  if (got !== want) failures.push(what + ': ' + got + ' != ' + want);
}

state['GameRawData.SessionData.WeekendInfo.TrackLength'] = '5.00 km';
lap(1, 90, { mark: 11, from: 0.4 });          // carregado no meio da volta
cross(2);
expect('volta carregada pela metade', shared.mini_ok, 0);
lap(2, 92, { mark: 22 });                      // primeira completa e limpa
cross(3);
expect('primeira volta limpa vira referencia', shared.mini_thr, 22);
lap(3, 95, { mark: 33 });                      // mais lenta
cross(4);
expect('volta mais lenta nao troca', shared.mini_thr, 22);
lap(4, 89, { mark: 44, dirty: true });         // mais rapida, mas suja
cross(5);
expect('volta suja nao vale', shared.mini_thr, 22);
lap(5, 88, { mark: 55, pit: true });           // mais rapida, saindo do box
cross(6);
expect('volta com pit nao vale', shared.mini_thr, 22);
lap(6, 90, { mark: 66 });                      // mais rapida e limpa
cross(7);
expect('volta mais rapida troca', shared.mini_thr, 66);
expect('referencia publicada', shared.mini_ok, 1);

// Ponto atual e WINDOW_S a frente: o freio simulado e o trecho da pista.
state['GameRawData.Telemetry.LapDistPct'] = 0.5;
state['DataCorePlugin.GameData.SpeedKmh'] = 200;
formula(root, $prop, setsharedvalue, getsharedvalueordefault);
var ahead = 0.5 + (200 / 3.6) * WINDOW / LEN;
expect('freio da referencia agora', shared.mini_brk, 50);
expect('freio da referencia a frente', shared.mini_brk_ahead, Math.floor(ahead * 100));

console.log(JSON.stringify(failures));
"""


def main():
    harness = (f"var FORMULA = {json.dumps(trace.RECORDER['Formula']['Expression'])};\n"
               f"var WINDOW = {trace.WINDOW_S};\n" + HARNESS)
    result = subprocess.run(["node", "-e", harness], capture_output=True, text=True)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        return 1
    failures = json.loads(result.stdout.strip().splitlines()[-1])
    for failure in failures:
        print("FALHOU:", failure)
    if not failures:
        print("gravador da referencia: tudo ok")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
