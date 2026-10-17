// Volta de referencia do grafico de telemetria: a melhor volta valida da
// sessao atual, gravada pelo proprio dash enquanto o piloto anda.
//
// Gravacao: acelerador, freio (0..100) e volante (graus) da volta em
// andamento, em REF_BINS posicoes uniformes de LapDistPct. Na virada de
// `Lap` a volta vira a referencia se: nao passou pelos boxes, ficou limpa
// (iRacing_Player_CurrentLapIsClean, mesma regra de states.VALIDITY), foi
// gravada quase inteira (nenhum buraco maior que REF_MAX_GAP posicoes) e e
// mais rapida que a referencia atual. Troca de pista ou de sessao
// (SessionNum), ou a contagem de voltas voltando, zera tudo.
//
// Quem grava e o item "Ref Lap Recorder" (coluna direita, sempre visivel):
// refRecorder(root) publica a referencia pelo armazenamento compartilhado do
// SimHub. Os itens do grafico chamam refXxx(root) e leem o publicado; se a
// publicacao estiver velha ou o armazenamento nao existir, cada item grava
// sozinho no proprio root (so enquanto estiver na tela).

var REF_BINS = 500;
// Buraco maximo (em posicoes) preenchido por interpolacao: 5% da volta.
var REF_MAX_GAP = 25;
// Espera depois da virada para o iRacing atualizar LapLastLapTime.
var REF_TIME_WAIT_S = 1.5;
// LapLastLapTime so vale se bater com o tempo medido ate essa diferenca.
var REF_TIME_TOL_S = 0.5;
// Logo depois da virada a validade ainda pode ser a da volta que acabou.
var REF_GRACE_S = 1.0;
// Logo depois da virada LapDistPct ainda pode trazer ~1.0 da volta anterior.
var REF_WRAP_S = 0.3;
var REF_SCOPE = 'sf23dash';
var REF_STALE_MS = 1000;
var REF_LAP_CLEAN = 'IRacingExtraProperties.iRacing_Player_CurrentLapIsClean';

// Escala fixa do volante no grafico: +-180 graus de volante cobrem a altura
// toda, com o zero na linha de 50. Fixa para o grafico nao "respirar".
var REF_STEER_RANGE = 180;

function refNum(v) {
	if (v == null || v === '') { return null; }
	var x = Number(v);
	return isNaN(x) ? null : x;
}

function refYes(v) {
	return v === true || v === 1 || (v != null && String(v).toUpperCase() === 'TRUE');
}

function refHasShared() {
	return typeof getsharedvalueordefault === 'function' && typeof setsharedvalue === 'function';
}

function refKey() {
	var track = $prop('GameRawData.SessionData.WeekendInfo.TrackName');
	var sess = $prop('GameRawData.Telemetry.SessionNum');
	return String(track == null ? '' : track) + '|' + String(sess == null ? '' : sess);
}

function refPct() {
	var pct = refNum($prop('GameRawData.Telemetry.LapDistPct'));
	if (pct == null) {
		pct = refNum($prop('DataCorePlugin.GameData.TrackPositionPercent'));
	}
	if (pct == null || pct < 0 || pct > 1) { return null; }
	return pct;
}

// Relogio em segundos: SessionTime do iRacing, ou o do sistema.
function refClock() {
	var t = refNum($prop('GameRawData.Telemetry.SessionTime'));
	return t == null ? Date.now() / 1000 : t;
}

function refEmptyLap() {
	return { thr: [], brk: [], str: [], dirty: false };
}

// Preenche os buracos da volta gravada interpolando entre vizinhos (a linha
// de chegada liga o fim no comeco). null se algum buraco for grande demais.
function refFill(lap) {
	var seen = [];
	for (var i = 0; i < REF_BINS; i++) {
		if (lap.thr[i] != null) { seen.push(i); }
	}
	if (seen.length < 2) { return null; }
	var out = { thr: [], brk: [], str: [] };
	var chs = ['thr', 'brk', 'str'];
	for (var k = 0; k < seen.length; k++) {
		var a = seen[k];
		var b = seen[(k + 1) % seen.length];
		var gap = (b - a + REF_BINS) % REF_BINS;
		if (gap === 0) { gap = REF_BINS; }
		if (gap > REF_MAX_GAP) { return null; }
		for (var g = 0; g < gap; g++) {
			var idx = (a + g) % REF_BINS;
			for (var c = 0; c < chs.length; c++) {
				var va = lap[chs[c]][a];
				var vb = lap[chs[c]][b];
				out[chs[c]][idx] = va + (vb - va) * g / gap;
			}
		}
	}
	return out;
}

// Decide a volta que acabou (guardada em rl.pending).
function refSettle(rl) {
	var p = rl.pending;
	rl.pending = null;
	if (p.lap.dirty) { return; }
	var t = p.measured;
	var last = refNum($prop('GameRawData.Telemetry.LapLastLapTime'));
	if (last != null && last > 0 && (t == null || Math.abs(last - t) <= REF_TIME_TOL_S)) {
		t = last;
	}
	if (t == null || !(t > 0)) { return; }
	if (rl.best != null && !(t < rl.best.t)) { return; }
	var filled = refFill(p.lap);
	if (filled == null) { return; }
	filled.t = t;
	rl.best = filled;
	rl.ver++;
}

// Grava um quadro. Estado em root.rl; devolve root.rl.
function refRecord(root) {
	var now = refClock();
	var key = refKey();
	var lap = refNum($prop('GameRawData.Telemetry.Lap'));
	var rl = root.rl;
	if (rl == null || rl.key !== key || (lap != null && rl.lapNo != null && lap < rl.lapNo)
		|| now < rl.at - 1) { // relogio voltou: replay ou sessao nova
		var ver = rl == null ? 0 : rl.ver + 1;
		rl = root.rl = { key: key, lapNo: lap, start: null, at: now, cur: refEmptyLap(),
			pending: null, best: null, ver: ver };
	}
	if (lap == null) { rl.at = now; return rl; }

	if (lap > rl.lapNo) {
		if (lap === rl.lapNo + 1) {
			rl.pending = { lap: rl.cur, measured: rl.start == null ? null : now - rl.start,
				at: now };
		}
		rl.cur = refEmptyLap();
		rl.lapNo = lap;
		rl.start = now;
	}
	rl.at = now;

	var since = rl.start == null ? Infinity : now - rl.start;
	var cur = rl.cur;
	if (refYes($prop('GameRawData.Telemetry.OnPitRoad'))) { cur.dirty = true; }
	var cl = $prop(REF_LAP_CLEAN);
	if (cl != null && cl !== '' && since > REF_GRACE_S && !refYes(cl)) { cur.dirty = true; }

	var pct = refPct();
	var thr = refNum($prop('GameRawData.Telemetry.Throttle'));
	var brk = refNum($prop('GameRawData.Telemetry.Brake'));
	var rad = refNum($prop('GameRawData.Telemetry.SteeringWheelAngle'));
	if (pct != null && thr != null && brk != null && rad != null
		&& !(since < REF_WRAP_S && pct > 0.5)) {
		var i = Math.min(REF_BINS - 1, Math.floor(pct * REF_BINS));
		cur.thr[i] = thr * 100;
		cur.brk[i] = brk * 100;
		cur.str[i] = rad * 180 / Math.PI;
	}

	if (rl.pending != null && now - rl.pending.at >= REF_TIME_WAIT_S) { refSettle(rl); }
	return rl;
}

function refRound(arr) {
	var out = [];
	for (var i = 0; i < arr.length; i++) { out.push(Math.round(arr[i] * 10) / 10); }
	return out.join(',');
}

// Item sempre visivel: grava e publica. Devolve '' (o item nao mostra nada).
function refRecorder(root) {
	root = root || {};
	var rl = refRecord(root);
	if (!refHasShared()) { return ''; }
	if (root.pubVer !== rl.ver || root.pubKey !== rl.key) {
		root.pubVer = rl.ver;
		root.pubKey = rl.key;
		var b = rl.best;
		setsharedvalue(REF_SCOPE, 'refdata', b == null ? ''
			: b.t + '|' + refRound(b.thr) + '|' + refRound(b.brk) + '|' + refRound(b.str));
		setsharedvalue(REF_SCOPE, 'refid', String(Date.now()) + ':' + rl.ver + ':' + rl.key);
	}
	setsharedvalue(REF_SCOPE, 'refat', Date.now());
	return '';
}

function refParse(s) {
	if (s == null || s === '') { return null; }
	var parts = String(s).split('|');
	if (parts.length !== 4) { return null; }
	var t = Number(parts[0]);
	var split = function (p) {
		var a = p.split(',');
		for (var i = 0; i < a.length; i++) { a[i] = Number(a[i]); }
		return a;
	};
	var lap = { t: t, thr: split(parts[1]), brk: split(parts[2]), str: split(parts[3]) };
	if (!(t > 0) || lap.thr.length < 2) { return null; }
	return lap;
}

// A referencia atual: a publicada pelo gravador, ou a gravada aqui mesmo.
function refBest(root) {
	root = root || {};
	if (refHasShared()) {
		var at = refNum(getsharedvalueordefault(REF_SCOPE, 'refat', 0)) || 0;
		if (Date.now() - at < REF_STALE_MS) {
			var id = getsharedvalueordefault(REF_SCOPE, 'refid', '');
			if (root.refId !== id) {
				root.refId = id;
				root.refLap = refParse(getsharedvalueordefault(REF_SCOPE, 'refdata', ''));
			}
			return root.refLap;
		}
	}
	root.refId = null;
	return refRecord(root).best;
}

// Valor do canal na posicao atual, interpolado; o ultimo ponto liga no
// primeiro (a linha de chegada nao tem degrau). null sem referencia.
function refAt(root, ch) {
	var lap = refBest(root);
	var pct = refPct();
	if (lap == null || pct == null) { return null; }
	var data = lap[ch];
	if (data == null || data.length < 2) { return null; }
	var n = data.length;
	var x = pct * n;
	var i = Math.floor(x) % n;
	var j = (i + 1) % n;
	var f = x - Math.floor(x);
	return data[i] + (data[j] - data[i]) * f;
}

function refAvailable(root) {
	return refAt(root, 'thr') != null;
}

// Graus de volante (convencao iRacing: positivo = esquerda) -> 0..100 do
// grafico, com 50 no centro e direita para cima.
function refSteerScale(deg) {
	var d = -Number(deg);
	if (d > REF_STEER_RANGE) { d = REF_STEER_RANGE; }
	if (d < -REF_STEER_RANGE) { d = -REF_STEER_RANGE; }
	return 50 + d / REF_STEER_RANGE * 50;
}

function refThrottle(root) {
	var v = refAt(root, 'thr');
	return v == null ? 0 : v;
}

function refBrake(root) {
	var v = refAt(root, 'brk');
	return v == null ? 0 : v;
}

function refSteer(root) {
	var v = refAt(root, 'str');
	return v == null ? 50 : refSteerScale(v);
}

function liveSteerAvailable() {
	var rad = $prop('GameRawData.Telemetry.SteeringWheelAngle');
	return rad != null && !isNaN(rad);
}

function liveSteer() {
	var rad = $prop('GameRawData.Telemetry.SteeringWheelAngle');
	if (rad == null || isNaN(rad)) { return 50; }
	return refSteerScale(Number(rad) * 180 / Math.PI);
}

function refLabel(root) {
	var lap = refBest(root);
	if (lap == null || refPct() == null || !(lap.t > 0)) { return 'REF N/A'; }
	var ms = Math.round(lap.t * 1000);
	var m = Math.floor(ms / 60000);
	var s = (ms % 60000) / 1000;
	var ss = s.toFixed(3);
	if (s < 10) { ss = '0' + ss; }
	return 'REF ' + m + ':' + ss;
}

function steerLabel() {
	return liveSteerAvailable() ? 'STR' : 'STR N/A';
}
