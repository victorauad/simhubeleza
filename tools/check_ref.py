"""Testa a volta de referencia: tools/ibt_ref.py e assets/js/refLap.js.

    python3 tools/check_ref.py

Monta um .ibt sintetico (3 voltas com rampas conhecidas), converte e confere
volta escolhida, reamostragem, chave da pista, tempo e o .js gerado. Depois
roda refLap.js no node com um $prop falso: interpolacao, wrap, escala do
volante e os estados "N/A".
"""

import json
import math
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ibt_ref  # noqa: E402

TRACK = "Synthetic Ring - GP"
TICK = 60
FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)


def build_ibt(path):
    """3 voltas: 30 s, 25 s (a mais rapida) e 28 s, mais um trecho de saida."""
    names = [("Lap", 2), ("LapDistPct", 4), ("Throttle", 4), ("Brake", 4),
             ("SteeringWheelAngle", 4), ("OnPitRoad", 1), ("LapLastLapTime", 4)]
    offsets, off = {}, 0
    for name, vtype in names:
        offsets[name] = off
        off += ibt_ref.VAR_TYPES[vtype][1]
    buf_len = off

    rows = []
    # Saida dos boxes: volta 0, nao conta.
    for i in range(TICK * 6):
        rows.append(dict(Lap=0, LapDistPct=0.5 + i / (TICK * 6) * 0.49,
                         Throttle=0.3, Brake=0.0, SteeringWheelAngle=0.0,
                         OnPitRoad=True, LapLastLapTime=0.0))
    last = 0.0
    for lap, secs in ((1, 30.0), (2, 25.0), (3, 28.0)):
        n = int(secs * TICK)
        for i in range(n):
            pct = i / n
            fast = lap == 2
            rows.append(dict(
                Lap=lap, LapDistPct=pct,
                Throttle=pct if fast else 0.5,
                Brake=(1 - pct) if fast else 0.2,
                SteeringWheelAngle=math.radians(90.0) * (2 * pct - 1) if fast else 0.0,
                OnPitRoad=False, LapLastLapTime=last))
        last = secs
    # Volta 4 incompleta (para no meio).
    for i in range(TICK * 5):
        rows.append(dict(Lap=4, LapDistPct=i / (TICK * 20), Throttle=1.0, Brake=0.0,
                         SteeringWheelAngle=0.0, OnPitRoad=False, LapLastLapTime=last))

    yaml = (f"---\nWeekendInfo:\n TrackName: {TRACK}\n TrackID: 1\n"
            "DriverInfo:\n DriverCarIdx: 0\n...\n").encode("latin-1") + b"\0"

    var_offset = ibt_ref.DISK_OFFSET + ibt_ref.DISK_HEADER.size
    info_offset = var_offset + len(names) * ibt_ref.VAR_HEADER.size
    buf_offset = info_offset + len(yaml)

    out = bytearray()
    out += ibt_ref.HEADER.pack(2, 1, TICK, 0, len(yaml), info_offset, len(names),
                               var_offset, 1, buf_len, 0, 0)
    out += ibt_ref.VARBUF.pack(0, buf_offset, 0, 0)
    out += bytes(3 * ibt_ref.VARBUF.size)
    out += ibt_ref.DISK_HEADER.pack(0, 0.0, 0.0, 4, len(rows))
    for name, vtype in names:
        out += ibt_ref.VAR_HEADER.pack(vtype, offsets[name], 1, 0,
                                       name.encode(), b"", b"")
    out += yaml
    for row in rows:
        rec = bytearray(buf_len)
        for name, vtype in names:
            struct.pack_into("<" + ibt_ref.VAR_TYPES[vtype][0], rec, offsets[name], row[name])
        out += rec
    Path(path).write_bytes(bytes(out))


def check_converter(work):
    ibt = work / "test.ibt"
    build_ibt(ibt)
    track, lap, seconds, series = ibt_ref.reference(ibt)
    check(track == TRACK, f"pista: {track!r}")
    check(lap == 2, f"volta mais rapida: {lap}")
    check(abs(seconds - 25.0) < 1e-6, f"tempo: {seconds}")
    for ch in ("thr", "brk", "str"):
        check(len(series[ch]) == ibt_ref.BINS, f"{ch}: {len(series[ch])} pontos")
    check(abs(series["thr"][500] - 50.0) < 0.2, f"thr[500]: {series['thr'][500]}")
    check(abs(series["brk"][250] - 75.0) < 0.2, f"brk[250]: {series['brk'][250]}")
    check(abs(series["str"][0] + 90.0) < 0.2, f"str[0]: {series['str'][0]}")
    check(abs(series["str"][500]) < 0.2, f"str[500]: {series['str'][500]}")

    track1, lap1, seconds1, _ = ibt_ref.reference(ibt, lap=3)
    check(lap1 == 3 and abs(seconds1 - 28.0) < 1e-6, f"--lap 3: {lap1} {seconds1}")
    try:
        ibt_ref.reference(ibt, lap=4)
        check(False, "volta 4 incompleta deveria falhar")
    except SystemExit:
        pass

    out = work / "js"
    ibt_ref.main([str(ibt), "--out", str(out)])
    target = out / "ref_synthetic_ring_gp.js"
    check(target.exists(), f"arquivo gerado: {sorted(p.name for p in out.iterdir())}")
    check(ibt_ref.lap_time(83.4567) == "1:23.457", ibt_ref.lap_time(83.4567))
    return target


HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const props = {};
const ctx = { $prop: (k) => (k in props ? props[k] : null), Math, Number, String, isNaN };
vm.createContext(ctx);
for (const f of process.argv.slice(2)) vm.runInContext(fs.readFileSync(f, 'utf8'), ctx);
const out = {};
const run = (e) => vm.runInContext(e, ctx);
const set = (k, v) => { if (v === undefined) delete props[k]; else props[k] = v; };

// Sem pista: tudo N/A.
out.noTrack = [run('refAvailable()'), run('refLabel()'), run('refThrottle()'), run('refSteer()')];
set('GameRawData.SessionData.WeekendInfo.TrackName', 'Outra Pista');
set('GameRawData.Telemetry.LapDistPct', 0.5);
out.otherTrack = [run('refAvailable()'), run('refLabel()')];

set('GameRawData.SessionData.WeekendInfo.TrackName', 'Synthetic Ring - GP');
out.label = run('refLabel()');
out.mid = [run('refThrottle()'), run('refBrake()'), run('refSteer()')];
set('GameRawData.Telemetry.LapDistPct', 0.2505);
out.interp = run('refThrottle()');
set('GameRawData.Telemetry.LapDistPct', 0.9995);
out.wrap = run('refThrottle()');
set('GameRawData.Telemetry.LapDistPct', 1.5);
out.outside = [run('refAvailable()'), run('refLabel()')];
set('GameRawData.Telemetry.LapDistPct', undefined);
set('DataCorePlugin.GameData.TrackPositionPercent', 0.5);
out.fallback = run('refThrottle()');

out.scale = [0, 90, -90, 180, -180, 400, -400].map((d) => run('refSteerScale(' + d + ')'));
out.liveNA = [run('liveSteerAvailable()'), run('liveSteer()'), run('steerLabel()')];
set('GameRawData.Telemetry.SteeringWheelAngle', -Math.PI / 2);
out.live = [run('liveSteerAvailable()'), run('liveSteer()'), run('steerLabel()')];

run('REFLAPS["L"] = { t: 59.9996, n: 2, thr: [0, 0], brk: [0, 0], str: [0, 0] };');
set('GameRawData.SessionData.WeekendInfo.TrackName', 'L');
out.round = run('refLabel()');
run('REFLAPS["L"].t = 9.5;');
out.short = run('refLabel()');
process.stdout.write(JSON.stringify(out));
"""


def check_js(ref_js, work):
    harness = work / "harness.js"
    harness.write_text(HARNESS)
    # A referencia carrega antes do refLap.js, como no SimHub em ordem alfabetica.
    proc = subprocess.run(["node", str(harness), str(ref_js),
                           str(ROOT / "assets" / "js" / "refLap.js")],
                          capture_output=True, text=True)
    if proc.returncode:
        FAILS.append("node: " + proc.stderr.strip())
        return
    out = json.loads(proc.stdout)
    near = lambda a, b: abs(a - b) < 0.11  # noqa: E731

    check(out["noTrack"] == [False, "REF N/A", 0, 50], f"sem pista: {out['noTrack']}")
    check(out["otherTrack"] == [False, "REF N/A"], f"outra pista: {out['otherTrack']}")
    check(out["label"] == "REF 0:25.000", f"rotulo: {out['label']}")
    thr, brk, steer = out["mid"]
    check(near(thr, 50) and near(brk, 50) and near(steer, 50), f"meio da volta: {out['mid']}")
    check(near(out["interp"], 25.05), f"interpolacao: {out['interp']}")
    # Entre o ultimo ponto (~99.9) e o primeiro (0): metade do caminho.
    check(40 < out["wrap"] < 60, f"wrap: {out['wrap']}")
    check(out["outside"] == [False, "REF N/A"], f"pct fora de 0..1: {out['outside']}")
    check(near(out["fallback"], 50), f"TrackPositionPercent: {out['fallback']}")
    check(out["scale"] == [50, 25, 75, 0, 100, 0, 100], f"escala do volante: {out['scale']}")
    check(out["liveNA"] == [False, 50, "STR N/A"], f"volante sem dado: {out['liveNA']}")
    check(out["live"][0] is True and near(out["live"][1], 75) and out["live"][2] == "STR",
          f"volante ao vivo: {out['live']}")
    check(out["round"] == "REF 1:00.000", f"arredondamento: {out['round']}")
    check(out["short"] == "REF 0:09.500", f"volta curta: {out['short']}")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        ref_js = check_converter(work)
        if ref_js.exists():
            check_js(ref_js, work)
    if FAILS:
        print("\n".join("FALHA: " + f for f in FAILS))
        return 1
    print("referencia ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
