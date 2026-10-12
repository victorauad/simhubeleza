// Volta de referencia do grafico de telemetria.
//
// Os dados vem de tools/ibt_ref.py, que converte um .ibt em ref_<pista>.js:
//   REFLAPS["<TrackName>"] = { t: <s>, n: 1000, thr: [...], brk: [...], str: [...] }
// Cada canal tem n pontos uniformes de LapDistPct (0 .. 1). Aqui so se le o
// valor na posicao atual do carro.

var REFLAPS = (typeof REFLAPS !== 'undefined') ? REFLAPS : {};

// Escala fixa do volante no grafico: +-180 graus de volante cobrem a altura
// toda, com o zero na linha de 50. Fixa para o grafico nao "respirar".
var REF_STEER_RANGE = 180;

function refLap() {
	var track = $prop('GameRawData.SessionData.WeekendInfo.TrackName');
	if (track == null || track === '') { return null; }
	var lap = REFLAPS[String(track)];
	return (lap && lap.n > 1) ? lap : null;
}

function refPct() {
	var pct = $prop('GameRawData.Telemetry.LapDistPct');
	if (pct == null || isNaN(pct)) {
		pct = $prop('DataCorePlugin.GameData.TrackPositionPercent');
	}
	if (pct == null || isNaN(pct)) { return null; }
	pct = Number(pct);
	if (pct < 0 || pct > 1) { return null; }
	return pct;
}

// Valor do canal na posicao atual, interpolado; o ultimo ponto liga no
// primeiro (a linha de chegada nao tem degrau). null sem referencia.
function refAt(ch) {
	var lap = refLap();
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

function refAvailable() {
	return refAt('thr') != null;
}

// Graus de volante (convencao iRacing: positivo = esquerda) -> 0..100 do
// grafico, com 50 no centro e direita para cima.
function refSteerScale(deg) {
	var d = -Number(deg);
	if (d > REF_STEER_RANGE) { d = REF_STEER_RANGE; }
	if (d < -REF_STEER_RANGE) { d = -REF_STEER_RANGE; }
	return 50 + d / REF_STEER_RANGE * 50;
}

function refThrottle() {
	var v = refAt('thr');
	return v == null ? 0 : v;
}

function refBrake() {
	var v = refAt('brk');
	return v == null ? 0 : v;
}

function refSteer() {
	var v = refAt('str');
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

function refLabel() {
	var lap = refLap();
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
