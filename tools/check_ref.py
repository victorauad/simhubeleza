"""Testa a volta de referencia (melhor volta da sessao): assets/js/refLap.js.

    python3 tools/check_ref.py

Roda refLap.js no node com um `$prop` falso e simula uma sessao a 60 Hz:
saida dos boxes (nao conta), volta lenta (vira a referencia), volta mais
rapida (substitui), volta mais rapida mas invalida (ignorada), volta com a
validade da anterior ainda falsa logo depois da virada (conta) e troca de
sessao (zera). Duas vezes: com o armazenamento compartilhado do SimHub (o
gravador publica, o grafico so le -- inclusive um item que so aparece no
fim) e sem ele (cada item grava sozinho). Confere tambem interpolacao, wrap
na linha de chegada, escala do volante, volante ao vivo, arredondamento do
rotulo e os estados "N/A".
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const src = fs.readFileSync(process.argv[2], 'utf8');
const T = 'GameRawData.Telemetry.';
const CLEAN = 'IRacingExtraProperties.iRacing_Player_CurrentLapIsClean';

function session(shared) {
	const props = {};
	const store = {};
	let ms = 1e12;
	const ctx = { $prop: (k) => (k in props ? props[k] : null), Math, Number, String, isNaN,
		Date: { now: () => ms } };
	if (shared) {
		ctx.getsharedvalueordefault = (s, k, d) => ((s + '/' + k) in store ? store[s + '/' + k] : d);
		ctx.setsharedvalue = (s, k, v) => { store[s + '/' + k] = v; };
	}
	vm.createContext(ctx);
	vm.runInContext(src, ctx);
	const set = (k, v) => { if (v === undefined) delete props[k]; else props[k] = v; };
	ctx.rec = {}; ctx.chart = {}; ctx.late = {};
	const out = {};
	const run = (e) => vm.runInContext(e, ctx);
	const snap = (r) => run('[refAvailable(' + r + '), refLabel(' + r + ')]');
	let st = 0;
	const frame = () => {
		set(T + 'SessionTime', st);
		if (shared) run('refRecorder(rec)');
		run('refThrottle(chart); refBrake(chart); refSteer(chart); refLabel(chart)');
		st += 1 / 60; ms += 1000 / 60;
	};
	// Volta de `secs` s: perfil `fast` (rampas) ou plano; `cleanAt(pct)`.
	const drive = (lap, secs, fast, opts) => {
		opts = opts || {};
		const n = Math.round(secs * 60);
		const from = opts.from || 0;
		for (let i = Math.round(from * n); i < n; i++) {
			const pct = i / n;
			const tIn = i / 60;
			set(T + 'Lap', lap);
			set(T + 'LapDistPct', pct);
			set(T + 'Throttle', fast ? pct : 0.5);
			set(T + 'Brake', fast ? 1 - pct : 0.2);
			set(T + 'SteeringWheelAngle', fast ? Math.PI / 2 * (2 * pct - 1) : 0);
			set(T + 'OnPitRoad', !!opts.pit);
			set(CLEAN, opts.clean ? opts.clean(pct, tIn) : true);
			// O iRacing atualiza o tempo da volta anterior ~0.5 s depois.
			if (opts.prev != null && tIn >= 0.5) set(T + 'LapLastLapTime', opts.prev);
			frame();
		}
	};
	set('GameRawData.SessionData.WeekendInfo.TrackName', 'Synthetic Ring');
	set(T + 'SessionNum', 0);
	set(T + 'LapLastLapTime', -1);

	// Sondas de posicao sem pedal/volante: o quadro nao e gravado na volta.
	const probe = (pct, e) => {
		const keep = ['Throttle', 'Brake', 'SteeringWheelAngle'].map((k) => [k, props[T + k]]);
		keep.forEach(([k]) => set(T + k, undefined));
		set(T + 'LapDistPct', pct);
		const r = run(e);
		keep.forEach(([k, v]) => set(T + k, v));
		return r;
	};
	const MID = '[refThrottle(chart), refBrake(chart), refSteer(chart)]';
	frame(); // o gravador publica antes do grafico ler
	out.empty = snap('chart');
	// Dash carregado no meio da volta de saida dos boxes.
	drive(0, 40, false, { from: 0.5, pit: true });
	drive(1, 30, false, { prev: 42.0 });          // termina a volta 1 (30 s)
	// Na volta 2: logo apos a virada ainda N/A (espera o LapLastLapTime).
	set(T + 'Lap', 2); set(T + 'LapDistPct', 0); frame();
	out.lap1Wait = snap('chart');
	drive(2, 25, true, { prev: 30.0 });            // volta 2, mais rapida (25 s)
	out.lap1 = snap('chart');                       // ref = volta 1 (30 s)
	out.lap1Mid = probe(0.5, MID);
	// Volta 3: 20 s mas invalida no meio.
	drive(3, 20, true, { prev: 25.0, clean: (p) => p < 0.6 });
	out.lap2 = snap('chart');                       // ref = volta 2 (25 s)
	out.lap2Mid = probe(0.5, MID);
	out.interp = probe(0.2505, 'refThrottle(chart)');
	out.wrap = probe(0.9995, 'refThrottle(chart)');
	// Volta 4: 24 s, validade ainda falsa (da volta 3) nos primeiros 0.5 s.
	drive(4, 24, true, { prev: 20.0, clean: (p, t) => t >= 0.5 });
	out.lap3 = snap('chart');                       // volta 3 invalida: ainda 25
	drive(5, 28, false, { prev: 24.0 });
	out.lap4 = snap('chart');                       // volta 4 vale: 24
	drive(6, 10, false, { prev: 28.0 });
	out.lap5 = snap('chart');                       // volta 5 mais lenta: 24
	out.late = snap('late');                        // item que so aparece agora
	out.chartRecorded = run('chart.rl != null');
	set(T + 'LapDistPct', 1.5);
	out.outside = snap('chart');
	set(T + 'LapDistPct', undefined);
	set('DataCorePlugin.GameData.TrackPositionPercent', 0.5);
	out.fallback = run('refThrottle(chart)');
	set('DataCorePlugin.GameData.TrackPositionPercent', undefined);
	set(T + 'LapDistPct', 0.3);
	set(T + 'SessionNum', 1);
	frame();
	out.newSession = snap('chart');
	out.newSessionVals = run('[refThrottle(chart), refBrake(chart), refSteer(chart)]');
	return [out, run];
}

const result = {};
const [withShared, run] = session(true);
const [local] = session(false);
result.shared = withShared;
result.local = local;

result.scale = [0, 90, -90, 180, -180, 400, -400].map((d) => run('refSteerScale(' + d + ')'));
run("$prop = (function (k) { return k == 'GameRawData.Telemetry.LapDistPct' ? 0.5 : null; })");
result.liveNA = run('[liveSteerAvailable(), liveSteer(), steerLabel()]');
run("$prop = (function (k) { return k == 'GameRawData.Telemetry.SteeringWheelAngle' ? -Math.PI / 2 "
	+ ": k == 'GameRawData.Telemetry.LapDistPct' ? 0.5 : null; })");
result.live = run('[liveSteerAvailable(), liveSteer(), steerLabel()]');
run('getsharedvalueordefault = undefined; var r = {}; refRecord(r); '
	+ 'r.rl.best = { t: 59.9996, thr: [0, 0], brk: [0, 0], str: [0, 0] };');
result.round = run('refLabel(r)');
run('r.rl.best.t = 9.5;');
result.short = run('refLabel(r)');
process.stdout.write(JSON.stringify(result));
"""


def check_session(name, out):
    near = lambda a, b: abs(a - b) < 0.3  # noqa: E731
    na = [False, "REF N/A"]
    check(out["empty"] == na, f"{name} sem volta: {out['empty']}")
    check(out["lap1Wait"] == na, f"{name} saida dos boxes contou: {out['lap1Wait']}")
    check(out["lap1"] == [True, "REF 0:30.000"], f"{name} volta 1: {out['lap1']}")
    thr, brk, steer = out["lap1Mid"]
    check(near(thr, 50) and near(brk, 20) and near(steer, 50), f"{name} volta 1 meio: {out['lap1Mid']}")
    check(out["lap2"] == [True, "REF 0:25.000"], f"{name} volta 2: {out['lap2']}")
    thr, brk, steer = out["lap2Mid"]
    check(near(thr, 50) and near(brk, 50) and near(steer, 50), f"{name} volta 2 meio: {out['lap2Mid']}")
    check(near(out["interp"], 25.05), f"{name} interpolacao: {out['interp']}")
    # Entre o ultimo ponto (~99.8) e o primeiro (0), 3/4 do caminho.
    check(15 < out["wrap"] < 35, f"{name} wrap: {out['wrap']}")
    check(out["lap3"] == [True, "REF 0:25.000"], f"{name} volta invalida contou: {out['lap3']}")
    check(out["lap4"] == [True, "REF 0:24.000"], f"{name} volta 4: {out['lap4']}")
    check(out["lap5"] == [True, "REF 0:24.000"], f"{name} volta lenta trocou: {out['lap5']}")
    check(out["outside"] == na, f"{name} pct fora de 0..1: {out['outside']}")
    check(near(out["fallback"], 50), f"{name} TrackPositionPercent: {out['fallback']}")
    check(out["newSession"] == na, f"{name} troca de sessao: {out['newSession']}")
    check(out["newSessionVals"] == [0, 0, 50], f"{name} valores sem ref: {out['newSessionVals']}")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        harness = Path(tmp) / "harness.js"
        harness.write_text(HARNESS)
        proc = subprocess.run(["node", str(harness), str(ROOT / "assets" / "js" / "refLap.js")],
                              capture_output=True, text=True)
    if proc.returncode:
        print("FALHA: node: " + proc.stderr.strip())
        return 1
    out = json.loads(proc.stdout)
    shared, local = out["shared"], out["local"]
    check_session("compartilhado", shared)
    check_session("local", local)
    # Com o compartilhado, o grafico so le; um item que aparece no fim ja ve.
    check(shared["chartRecorded"] is False, "compartilhado: o grafico gravou sozinho")
    check(shared["late"] == [True, "REF 0:24.000"], f"item que aparece depois: {shared['late']}")
    check(local["chartRecorded"] is True, "local: o grafico nao gravou")
    check(local["late"] == [False, "REF N/A"], f"local, item novo: {local['late']}")
    check(out["scale"] == [50, 25, 75, 0, 100, 0, 100], f"escala do volante: {out['scale']}")
    check(out["liveNA"] == [False, 50, "STR N/A"], f"volante sem dado: {out['liveNA']}")
    check(out["live"][0] is True and abs(out["live"][1] - 75) < 0.01 and out["live"][2] == "STR",
          f"volante ao vivo: {out['live']}")
    check(out["round"] == "REF 1:00.000", f"arredondamento: {out['round']}")
    check(out["short"] == "REF 0:09.500", f"volta curta: {out['short']}")
    if FAILS:
        print("\n".join("FALHA: " + f for f in FAILS))
        return 1
    print("referencia ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
