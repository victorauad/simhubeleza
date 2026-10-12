"""Converte uma volta de um .ibt do iRacing em volta de referencia do dash.

O JS do SimHub nao le .ibt, entao a volta e convertida aqui, offline, num
`.js` que vai junto no pacote (`assets/js` -> `JavascriptExtensions`):

    python3 tools/ibt_ref.py <arquivo.ibt> [--lap N] [--out DIR]

Por padrao escolhe a volta completa mais rapida (fora dos boxes) e a
reamostra em 1000 pontos de `LapDistPct`: acelerador e freio em 0-100,
volante em graus (convencao do iRacing: positivo = esquerda). A chave e o
`TrackName` do session info, o mesmo que o SimHub expoe em
`SessionData.WeekendInfo.TrackName`; varias pistas convivem, uma por arquivo.

So biblioteca padrao: nada a instalar.
"""

import argparse
import bisect
import math
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "assets" / "js"

#: Pontos da volta reamostrada (~15 KB por pista).
BINS = 1000

#: Tipos de variavel do irsdk: codigo -> (formato struct, tamanho).
VAR_TYPES = {
    0: ("c", 1),   # char
    1: ("?", 1),   # bool
    2: ("i", 4),   # int
    3: ("I", 4),   # bitfield
    4: ("f", 4),   # float
    5: ("d", 8),   # double
}

HEADER = struct.Struct("<10i2i")          # ver .. bufLen, pad[2]
VARBUF = struct.Struct("<2i2i")           # tickCount, bufOffset, pad[2]
DISK_HEADER = struct.Struct("<qddii")     # startDate, startTime, endTime, lapCount, recordCount
VAR_HEADER = struct.Struct("<4i32s64s32s")
DISK_OFFSET = HEADER.size + 4 * VARBUF.size   # 112

CHANNELS = ("Lap", "LapDistPct", "Throttle", "Brake", "SteeringWheelAngle")
OPTIONAL = ("OnPitRoad", "LapLastLapTime")


def read_ibt(path):
    """Le o .ibt e devolve (session_yaml, tick_rate, {canal: [valores]})."""
    data = Path(path).read_bytes()
    (_ver, _status, tick_rate, _upd, info_len, info_offset, num_vars,
     var_offset, _num_buf, buf_len, _p0, _p1) = HEADER.unpack_from(data, 0)
    _tick, buf_offset, _q0, _q1 = VARBUF.unpack_from(data, HEADER.size)
    _date, _start, _end, _laps, records = DISK_HEADER.unpack_from(data, DISK_OFFSET)

    variables = {}
    for i in range(num_vars):
        vtype, offset, count, _as_time, name, _desc, _unit = VAR_HEADER.unpack_from(
            data, var_offset + i * VAR_HEADER.size)
        variables[name.split(b"\0", 1)[0].decode("latin-1")] = (vtype, offset, count)

    missing = [name for name in CHANNELS if name not in variables]
    if missing:
        raise SystemExit(f"{path}: canais ausentes no .ibt: {', '.join(missing)}")

    available = (len(data) - buf_offset) // buf_len if buf_len else 0
    if records <= 0 or records > available:
        records = available

    wanted = [name for name in CHANNELS + OPTIONAL if name in variables]
    out = {name: [] for name in wanted}
    for r in range(records):
        base = buf_offset + r * buf_len
        for name in wanted:
            vtype, offset, _count = variables[name]
            fmt, _size = VAR_TYPES[vtype]
            out[name].append(struct.unpack_from("<" + fmt, data, base + offset)[0])

    yaml = data[info_offset:info_offset + info_len].split(b"\0", 1)[0]
    return yaml.decode("latin-1"), tick_rate, out


def track_name(yaml):
    """`WeekendInfo: TrackName:` do session info."""
    match = re.search(r"^WeekendInfo:\s*$.*?^\s+TrackName:\s*(.+?)\s*$",
                      yaml, re.M | re.S)
    if not match:
        raise SystemExit("TrackName nao encontrado no session info do .ibt")
    return match.group(1).strip().strip("'\"")


def laps(tick_rate, ch):
    """Voltas completas: {lap: (inicio, fim, tempo_s)} com indices de tick."""
    spans = {}
    for i, lap in enumerate(ch["Lap"]):
        start, _end = spans.get(lap, (i, i))
        spans[lap] = (start, i + 1)

    pit = ch.get("OnPitRoad")
    last = ch.get("LapLastLapTime")
    result = {}
    for lap, (start, end) in spans.items():
        if lap <= 0 or end - start < tick_rate * 5:
            continue
        pct = ch["LapDistPct"][start:end]
        # Volta inteira: comeca perto da linha, termina perto dela e nao
        # tem salto (reset, reboque, teleporte de replay).
        if pct[0] > 0.02 or pct[-1] < 0.98:
            continue
        if any(b - a < -0.02 or b - a > 0.05 for a, b in zip(pct, pct[1:])):
            continue
        if pit is not None and any(pit[start:end]):
            continue
        seconds = (end - start) / tick_rate
        # O iRacing publica o tempo oficial alguns ticks depois da virada.
        if last is not None and end + 2 * tick_rate < len(last):
            official = last[end + 2 * tick_rate]
            if official > 0 and abs(official - seconds) < 1.0:
                seconds = official
        result[lap] = (start, end, seconds)
    return result


def resample(xs, ys, n=BINS):
    """Interpolacao linear de ys(xs) em n pontos uniformes de 0 a 1."""
    pairs = sorted(zip(xs, ys))
    px = [p[0] for p in pairs]
    py = [p[1] for p in pairs]
    out = []
    for i in range(n):
        x = i / n
        j = bisect.bisect_left(px, x)
        if j <= 0:
            out.append(py[0])
        elif j >= len(px):
            out.append(py[-1])
        else:
            x0, x1 = px[j - 1], px[j]
            t = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
            out.append(py[j - 1] + (py[j] - py[j - 1]) * t)
    return out


def reference(path, lap=None):
    """Monta a referencia: (pista, volta, tempo, {thr, brk, str})."""
    yaml, tick_rate, ch = read_ibt(path)
    track = track_name(yaml)
    complete = laps(tick_rate, ch)
    if not complete:
        raise SystemExit(f"{path}: nenhuma volta completa fora dos boxes")
    if lap is None:
        lap = min(complete, key=lambda k: complete[k][2])
    elif lap not in complete:
        raise SystemExit(f"volta {lap} nao e completa; disponiveis: "
                         f"{', '.join(map(str, sorted(complete)))}")
    start, end, seconds = complete[lap]
    pct = ch["LapDistPct"][start:end]
    series = {
        "thr": [round(v * 100, 1) for v in resample(pct, ch["Throttle"][start:end])],
        "brk": [round(v * 100, 1) for v in resample(pct, ch["Brake"][start:end])],
        "str": [round(math.degrees(v), 1)
                for v in resample(pct, ch["SteeringWheelAngle"][start:end])],
    }
    return track, lap, seconds, series


def slug(track):
    return re.sub(r"[^A-Za-z0-9]+", "_", track).strip("_").lower() or "track"


def to_js(track, seconds, series):
    def arr(values):
        return "[" + ",".join(f"{v:g}" for v in values) + "]"
    key = track.replace("\\", "\\\\").replace('"', '\\"')
    return (
        "// Gerado por tools/ibt_ref.py -- volta de referencia do grafico de telemetria.\n"
        "var REFLAPS = (typeof REFLAPS !== 'undefined') ? REFLAPS : {};\n"
        f'REFLAPS["{key}"] = {{ t: {seconds:.3f}, n: {BINS},\n'
        f"  thr: {arr(series['thr'])},\n"
        f"  brk: {arr(series['brk'])},\n"
        f"  str: {arr(series['str'])} }};\n"
    )


def lap_time(seconds):
    minutes = int(seconds // 60)
    return f"{minutes}:{seconds - minutes * 60:06.3f}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("ibt", help="arquivo .ibt do iRacing")
    parser.add_argument("--lap", type=int, help="volta especifica (padrao: a mais rapida)")
    parser.add_argument("--out", type=Path, default=OUT_DIR, help="pasta de saida")
    args = parser.parse_args(argv)

    track, lap, seconds, series = reference(args.ibt, args.lap)
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / f"ref_{slug(track)}.js"
    target.write_text(to_js(track, seconds, series), encoding="utf-8")
    print(f"{track}: volta {lap} ({lap_time(seconds)}) -> {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
