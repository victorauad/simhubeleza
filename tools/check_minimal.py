#!/usr/bin/env python3
"""Testa o gravador da volta de referencia do dash minimal (Node).

Roda a formula `trace.RECORDER` do jeito que o SimHub roda -- uma chamada por
quadro, com o mesmo `root` -- sobre voltas simuladas, e confere:

  - a volta em que o dash foi carregado (pela metade) nunca vira referencia;
  - a referencia e a volta que virou o BestLapTime da sessao, julgada so
    quando o iRacing publica o tempo dela (com atraso, como no jogo) --
    inclusive quando o BestLapTime muda segundos depois do LastLapTime;
  - um reset (a volta conta para tras) nao apaga a referencia;
  - com o IRacingExtraProperties, a volta limpa vale pelo proprio tempo e a
    suja nunca vale;
  - volta mais lenta, ou invalida (o jogo nao conta), nao troca;
  - um LastLapTime velho igual ao best nao promove a volta seguinte;
  - o valor publicado e o da referencia no ponto atual, interpolado entre
    trechos;
  - a virada do LapDistPct um quadro antes da volta nao invalida nada;
  - mini-setores: o delta de cada setor contra a referencia (voltas com
    duracao por setor), o ultimo setor fechado na virada, o resultado da
    volta anterior ate o setor 0 da proxima fechar, e nada sem referencia.

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
                           'getsharedvalueordefault', 'timespantoseconds', FORMULA);
var shared = {};
var setsharedvalue = function (s, k, v) { shared[k] = v; };
var getsharedvalueordefault = function (s, k, d) { return k in shared ? shared[k] : d; };
var timespantoseconds = function (v) { return Number(v) || 0; };
var root = {};
var state = {};
var $prop = function (name) { return state[name]; };
var LEN = 5000, FPS = 60, DELAY = 40, failures = [];
var BEST = 'DataCorePlugin.GameData.BestLapTime';
var LAST = 'DataCorePlugin.GameData.LastLapTime';
var CLEAN = 'IRacingExtraProperties.iRacing_Player_CurrentLapIsClean';
var publish = null;   // tempo da volta anterior, que o jogo publica com atraso
var bestLag = 0;      // quadros entre o LastLapTime e o BestLapTime
var withClean = false;

function reset(opts) {
  root = {}; state = {}; shared = {}; publish = null;
  bestLag = opts.bestLag || 0; withClean = !!opts.clean;
  state['GameRawData.SessionData.WeekendInfo.TrackLength'] = '5.00 km';
  state[BEST] = 0; state[LAST] = 0;
}

function frame() {
  formula(root, $prop, setsharedvalue, getsharedvalueordefault, timespantoseconds);
}

function apply() {
  if (!publish) return;
  state[LAST] = publish.seconds;
  if (!bestLag) applyBest();
}

function applyBest() {
  if (!publish) return;
  if (publish.valid && (!(state[BEST] > 0) || publish.seconds < state[BEST]))
    state[BEST] = publish.seconds;
  publish = null;
}

// Uma volta a velocidade constante: acelerador = marca da volta, freio =
// trecho da pista (para conferir a leitura no ponto atual).
function lap(number, seconds, opts) {
  opts = opts || {};
  var frames = Math.round(seconds * FPS), start = opts.from || 0;
  // `sectors`: duracao de cada um dos 10 setores (soma = seconds), para voltas
  // que nao andam a velocidade constante; `upto`: so essa fracao da volta.
  var cum = null;
  if (opts.sectors) {
    cum = [0];
    opts.sectors.forEach(function (d) { cum.push(cum[cum.length - 1] + d); });
    seconds = cum[cum.length - 1];
    frames = Math.round(seconds * FPS);
  }
  var run = Math.round(frames * (opts.upto || 1));
  var dirtyAt = opts.valid === false ? Math.floor(frames / 2) : frames;
  for (var f = 0; f < run; f++) {
    if (f == DELAY) apply();
    if (bestLag && f == DELAY + bestLag) applyBest();
    // A validade da volta velha ainda aparece no comeco da nova.
    if (withClean && f >= DELAY / 2) state[CLEAN] = f < dirtyAt;
    var k = f / frames;
    var pct = start + (1 - start) * k;
    if (cum) {
      var el = f / FPS, i = 0;
      while (i < 9 && el >= cum[i + 1]) i++;
      pct = (i + (el - cum[i]) / (cum[i + 1] - cum[i])) / 10;
    }
    state['GameRawData.Telemetry.LapDistPct'] = pct;
    state['GameRawData.Telemetry.Lap'] = number;
    state['GameRawData.Telemetry.SessionTime'] = (state.t || 0) + 1 / FPS;
    state.t = state['GameRawData.Telemetry.SessionTime'];
    state['DataCorePlugin.GameData.Throttle'] = opts.mark;
    state['DataCorePlugin.GameData.Brake'] = Math.floor(pct * 100);
    state['DataCorePlugin.GameData.SpeedKmh'] = LEN / seconds * 3.6;
    frame();
  }
  if (opts.upto) return;
  publish = { seconds: seconds, valid: opts.valid !== false };
  // O LapDistPct vira um quadro antes da volta; com `early`, o jogo publica
  // o tempo antes de virar a volta.
  if (opts.early) apply();
  state['GameRawData.Telemetry.LapDistPct'] = 0.0001;
  frame();
}

function expect(what, got, want, tolerance) {
  var ok = tolerance ? Math.abs(got - want) <= tolerance : got === want;
  if (!ok) failures.push(what + ': ' + got + ' != ' + want);
}

// A sequencia basica, nos tres jeitos de o SimHub entregar a melhor volta.
function basic(tag, opts) {
  reset(opts);
  var e = function (what, got, want) { expect(tag + what, got, want); };
  lap(1, 100, { mark: 11, from: 0.4 });          // carregado no meio da volta
  lap(2, 92, { mark: 22 });
  e('volta carregada pela metade', shared.mini_ok, 0);
  lap(3, 95, { mark: 33 });                       // mais lenta
  e('primeira volta completa e a melhor vira referencia', shared.mini_thr, 22);
  e('tempo da referencia', shared.mini_best, 92);
  lap(4, 89, { mark: 44, valid: false });         // mais rapida, mas invalida
  e('volta mais lenta nao troca', shared.mini_thr, 22);
  lap(5, 91.5, { mark: 55 });                     // melhor volta
  e('volta invalida nao vale', shared.mini_thr, 22);
  lap(6, 91.6, { mark: 66 });                     // LastLapTime velho = best
  e('volta mais rapida troca', shared.mini_thr, 55);
  lap(7, 91, { mark: 77, early: true });          // tempo publicado antes da virada
  e('LastLapTime velho nao promove a seguinte', shared.mini_thr, 55);
  lap(8, 93, { mark: 88 });
  e('tempo publicado antes da virada', shared.mini_thr, 77);
  e('referencia publicada', shared.mini_ok, 1);
  e('tempo da melhor volta', shared.mini_best, 91);
}
basic('', {});
basic('best atrasado 5 s: ', { bestLag: 300 });
basic('com validade: ', { clean: true });
basic('com validade e best atrasado: ', { clean: true, bestLag: 300 });

// Reset para os boxes (a volta conta para tras): a referencia fica.
reset({});
lap(1, 100, { mark: 11, from: 0.4 });
lap(2, 92, { mark: 22 });
lap(3, 95, { mark: 33 });
lap(1, 30, { mark: 0, from: 0.7 });
expect('reset nao apaga a referencia', shared.mini_best, 92);
expect('reset: pedais da referencia', shared.mini_thr, 22);
// Sessao nova: comeca do zero.
state['GameRawData.Telemetry.SessionNum'] = 1;
state[BEST] = 0;
frame();
expect('sessao nova apaga a referencia', shared.mini_ok, 0);

// Leitura no ponto atual: o freio simulado e o trecho da pista.
reset({});
lap(1, 100, { mark: 11, from: 0.4 });
lap(2, 92, { mark: 22 });
lap(3, 95, { mark: 33 });
[0.2, 0.5, 0.83].forEach(function (q) {
  state['GameRawData.Telemetry.LapDistPct'] = q;
  frame();
  expect('freio da referencia em ' + q, shared.mini_brk, q * 100, 1.5);
});

// Mini-setores. A referencia tem 9.2 s em cada setor (92 s); a volta de
// teste perde 0.5 s no setor 3, ganha 0.3 s no 5 e perde 0.4 s no ultimo.
function even(d) { var a = []; for (var i = 0; i < 10; i++) a.push(d); return a; }
function sd(k) { return shared['mini_sd' + k]; }
var mix = even(9.2); mix[3] += 0.5; mix[5] -= 0.3; mix[9] += 0.4;
function sectorLaps() {
  reset({});
  lap(1, 100, { mark: 11, from: 0.4 });
  lap(2, 92, { sectors: even(9.2), mark: 22 });
  expect('sem referencia, setor sem dado', sd(3), 99);
  lap(3, 95, { sectors: even(9.5), mark: 33 });
  expect('contra a referencia (lap 2) nos 0.3 s a mais por setor', sd(4), 0.3, 0.02);
  lap(4, 92.4, { sectors: mix, mark: 44 });
}
// Volta 4 inteira: setores 0-8 fechados no caminho, o 9 so na virada.
sectorLaps();
for (var q = 0; q < 9; q++)
  expect('setor ' + q + ' contra a referencia', sd(q), q == 3 ? 0.5 : q == 5 ? -0.3 : 0, 0.02);
expect('ultimo setor ainda sem dado', sd(9), 99);
// A virada fecha o ultimo setor (a volta 5 comeca no quadro seguinte).
sectorLaps();
lap(5, 92, { sectors: even(9.2), mark: 55, upto: 0.05 });
expect('ultimo setor fechado na virada', sd(9), 0.4, 0.03);
expect('resultado da volta anterior fica ate o setor 0 fechar', sd(3), 0.5, 0.02);
sectorLaps();
lap(5, 92, { sectors: even(9.2), mark: 55, upto: 0.15 });
expect('setor 0 da volta nova apaga o resultado anterior', sd(3), 99);
expect('setor 0 da volta nova', sd(0), 0, 0.02);
// Reset (a volta conta para tras): o resultado some, a referencia fica.
sectorLaps();
lap(2, 30, { sectors: even(3), mark: 0 });
expect('reset apaga os setores', sd(3), 99);
expect('reset: a referencia fica', shared.mini_ok, 1);

console.log(JSON.stringify(failures));
"""


def main():
    harness = (f"var FORMULA = {json.dumps(trace.RECORDER['Formula']['Expression'])};\n"
               + HARNESS)
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
