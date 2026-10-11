# -*- coding: utf-8 -*-
import csv, json, re, os, sys, urllib.request, urllib.parse, concurrent.futures as cf, collections, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from desc import describe as _describe, DC
from acc import acc
def describe(n): return acc(_describe(n))

# uso: gen.py <pasta do SimHub> <pasta de trabalho> <saida.md> <docs/propriedades.txt>
SH, O, OUT, PREV = sys.argv[1:5]

def rd(p): return open(p, encoding='utf-8', errors='replace').read()

# ---------- live probing ----------
_cache = {}
def get(name):
    if name in _cache: return _cache[name]
    try:
        r = urllib.request.urlopen('http://localhost:8888/api/GetProperty/' + urllib.parse.quote(name, safe='.'), timeout=6)
        res = (r.status, r.read().decode('utf-8', 'replace'))
    except Exception as e:
        res = (0, '')
    _cache[name] = res
    return res
def probe_all(names):
    names = [n for n in set(names) if n not in _cache]
    with cf.ThreadPoolExecutor(12) as ex:
        list(ex.map(get, names))
def ok(name): return get(name)[0] == 200
def js(code):
    u = 'http://localhost:8888/api/EvaluateStringFormula?interpreter=1&formula=' + urllib.parse.quote(code)
    try: return urllib.request.urlopen(u, timeout=10).read().decode('utf-8', 'replace')
    except Exception: return ''

def esc(s): return str(s).replace('|', '\\|').replace('\n', ' ')
def table(hdr, rows):
    o = ['| ' + ' | '.join(hdr) + ' |', '|' + '|'.join(['---'] * len(hdr)) + '|']
    for r in rows: o.append('| ' + ' | '.join(esc(c) for c in r) + ' |')
    return '\n'.join(o)

L = []
def w(s=''): L.append(s)

# ---------- data: GameData walk ----------
walk = []
aliases = collections.defaultdict(list)
groups = {}
for line in rd(os.path.join(O, 'gamedata_walk.tsv')).splitlines()[1:]:
    p = line.split('\t')
    if p[0] == '#ALIAS': aliases[p[1]].append(p[2].split(',')[0].strip()); continue
    if p[0] == '#GROUP': groups[p[1]] = p[2]; continue
    walk.append(p)

sm = list(csv.reader(open(os.path.join(O, 'support_matrix.tsv'), encoding='utf-8'), delimiter='\t'))
smh = sm[0]; smr = {r[0]: r for r in sm[1:]}
GAMES = [('IRacingReader.IRacingManager', 'iR'), ('ACSharedMemory.ACCManager', 'ACC'), ('ACSharedMemory.ACManager', 'AC'),
         ('ACSharedMemory.ACEVOManager', 'ACE'), ('RfactorReader.LMUManager', 'LMU'), ('RfactorReader.RF2Manager', 'rF2'),
         ('PCarsSharedMemory.AMS2.Automobilista2Manager', 'AMS2'), ('R3EReader.RREManager', 'R3E'),
         ('CodemastersReader.CodemastersF12025Manager', 'F1 25'), ('GTReader.GT7Manager', 'GT7')]
SYM = {'0': 'S', '1': '—', '2': 'C', '9': '·', '8': '?', '7': '?'}
def sup(member, game='IRacingReader.IRacingManager'):
    r = smr.get(member)
    if not r: return '·'
    return SYM.get(r[smh.index(game)], '?')

# ---------- probe core names ----------
core_names = []
for p in walk:
    n = p[0]
    if 'null-in-sample' in p[3] or n.endswith('NN'): continue
    core_names.append('DataCorePlugin.' + n)
    if p[1]: core_names.append(p[1])
for a in aliases.values():
    for x in a: core_names.append('DataCorePlugin.GameData.' + x); core_names.append(x)
core_names += ['DataCorePlugin.' + k for k in DC if '<' not in k]
probe_all(core_names)

# =====================================================================
ver = re.findall(r'\d+\.\d+\.\d+', rd(os.path.join(SH, 'RSC.Version.txt')))[:1]
w('# SimHub — referência completa de propriedades desta instalação')
w()
w('Gerado em %s a partir da instalação em `%s` — **SimHub %s**, pacote RSC %s, plugin Dahl Design.' % (
    datetime.date.today().isoformat(), SH, get('DataCorePlugin.SimHubVersion')[1] or '?', ver[-1] if ver else '?'))
w()
w('**Como foi feito.** As DLLs do SimHub foram lidas por reflexão e o IL dos métodos que registram propriedades foi desmontado '
  '(`DataCorePlugin.DeclareProperties/DeclareObject/DeclareMember`, `GetShortAliasName`, `ParsePropertyPath`, `GetPropertySupportStatus`, '
  'os `Init` de cada plugin etc.). O `GameData` foi reconstruído executando a mesma regra do `DataCorePlugin` sobre uma instância nova de '
  '`StatusData`. Depois, cada nome foi consultado no servidor web local (`GET /api/GetProperty/<nome>`), com o iRacing aberto **fora de sessão**.')
w()
w('**Diferença para `docs/propriedades.txt`.** Aquele arquivo lista nomes encontrados em amostras de telemetria e nos dashboards instalados. '
  'Este parte do código do SimHub: traz tipo, alias, flags (oculto/obsoleto/calculado), suporte por jogo, descrição, faixas reais de índice, '
  'plugins desabilitados, eventos, ações e todas as funções de fórmula. Também corrige uma regra daquele cabeçalho (ver §1.2).')
w()
w('Legenda da coluna **Ao vivo**: ✓ = respondeu 200 agora; vazio = 204 (não existe *ou* está nulo neste momento — fora de sessão muita coisa é nula).')
w()
w('## Sumário')
for t in ['1. Como o SimHub monta os nomes', '2. DataCorePlugin — propriedades de topo', '3. DataCorePlugin.GameData — telemetria normalizada',
          '4. Suporte por jogo', '5. Pilotos e leaderboard (funções driver*)', '6. GameRawData do iRacing', '7. Plugins do SimHub',
          '8. Plugins de terceiros instalados', '9. Eventos', '10. Ações', '11. Funções de fórmula (NCalc e JavaScript)', '12. API HTTP local', '13. Limites desta análise']:
    w('- [%s](#%s)' % (t, re.sub(r'[^\w -]', '', t.lower()).strip().replace(' ', '-')))
w()

# ---------- 1 ----------
w('## 1. Como o SimHub monta os nomes')
w()
w('### 1.1 Prefixo')
w('Toda propriedade é registrada por um plugin e ganha o nome da **classe** do plugin como prefixo: `DataCorePlugin.`, `PersistantTrackerPlugin.`, '
  '`IRacingExtraProperties.`, `DahlDesign.` etc. (`PluginManager.AttachDelegate/AttachProperty/AddProperty(name, pluginType, ...)`). '
  'Plugin desabilitado em *Settings → Plugins* não registra nada — os nomes dele simplesmente não existem.')
w()
w('### 1.2 Atalhos sem prefixo (regra exata)')
w('`DataCorePlugin.GetShortAliasName` só cria atalho em dois casos:')
w()
w('- `GameData.X` (fora de `GameData.NewData`) → atalho **`X`**. Ex.: `[Gear]`, `[SpeedKmh]`, `[Flag_Blue]`.')
w('- `GameRawData.*` → atalho **igual ao próprio nome**. Ex.: `[GameRawData.Telemetry.Speed]`.')
w()
w('Todo o resto exige o nome completo. Conferido agora no servidor local:')
w()
chk = [('DataCorePlugin.GameData.Gear', ''), ('Gear', ''), ('GameData.Gear', 'sem DataCorePlugin. não resolve'),
       ('DataCorePlugin.GameRawData.Telemetry.Speed', ''), ('GameRawData.Telemetry.Speed', ''),
       ('DataCorePlugin.CurrentGame', ''), ('CurrentGame', 'topo do DataCorePlugin não tem atalho'),
       ('DataCorePlugin.GameData.NewData.Gear', 'cópia legada, oculta no editor'), ('GameData.NewData.Gear', '')]
probe_all([c for c, _ in chk])
w(table(['Nome', 'Resposta', 'Obs.'], [['`%s`' % c, '200' if ok(c) else '204', o] for c, o in chk]))
w()
w('> O cabeçalho de `docs/propriedades.txt` diz que "o prefixo `DataCorePlugin.` é opcional". Vale só para os dois casos acima. '
  'O dashboard atual usa sempre o nome completo, então nada quebra.')
w()
w('### 1.3 Aliases declarados no código')
w('Alguns membros têm `[ExposeAlias]` e ficam acessíveis também por outro nome (sempre dentro de `DataCorePlugin.GameData.`, com atalho curto):')
w()
w(table(['Nome principal', 'Alias'], [['`%s`' % k.replace('GameData.', ''), ', '.join('`%s`' % x for x in v)] for k, v in aliases.items()]))
w()
w('### 1.4 Como objetos viram nomes')
w('Regras do `DeclareObject` (o mesmo para `GameData` e `GameRawData`):')
w()
w('- Tipos básicos (números, `bool`, `string`, `enum`, `DateTime`, `TimeSpan`, `Nullable<>`) viram propriedade.')
w('- **Array** → um nome por elemento, sufixo de 2 dígitos **começando em 01**: `CarCoordinates01..03`, `Drivers01`, `Sessions01`.')
w('- **List<> / qualquer IEnumerable que não seja array → ignorado.** Por isso `GameData.Opponents` não existe como propriedade (use §5).')
w('- **Dicionário** → um nome por chave; valores que são arrays são pulados (é por isso que `GameRawData.Telemetry.CarIdx*` do iRacing não existe — ver §6).')
w('- Objetos que implementam `IExposable` escolhem o que expor (`GetValues()`); o iRacing usa isso (§6).')
w('- Objeto **nulo no momento do registro** não gera filhos. O registro acontece com uma instância nova/amostra, então filhos de objetos que só se preenchem em sessão podem não existir.')
w('- Excluídos sempre: caminhos com `.Skin` e terminados em `.OldData`, `.GameOldData`, `.GameNewData`, `.RawData`, `.RawDataObject`, `.Events`.')
w('- `[DoNotExpose]` remove o membro; `[Hidden]` registra mas esconde do seletor do editor; `[ExposeName]` renomeia.')
w()
w('### 1.5 Suporte por jogo (`SupportStatus`)')
w('Cada leitor de jogo pode declarar um método `GD_<Membro>`. O `DataCorePlugin` olha esse método para marcar a propriedade no editor: '
  'sem `GD_` e com `[Computed]` no membro → **calculado pelo SimHub**; `GD_` com `[NotAvailable]` → **não disponível nesse jogo**; '
  '`GD_` com `[Computed]` → calculado; `GD_` sem atributo → **fornecido pelo jogo**. Tabela completa em §4.')
w()
w('### 1.6 Índices: cada plugin usa uma base')
w(table(['Família', 'Faixa real (conferida)'], [
    ['`DataCorePlugin.GameData.CarCoordinatesNN`', '01..03'],
    ['`GameRawData.SessionData...DriversNN`, `SessionsNN`', 'começa em 01 (`Drivers00` não existe)'],
    ['`PersistantTrackerPlugin.DriverAhead_NN_*` / `DriverBehind_NN_*`', '00..04'],
    ['`PersistantTrackerPlugin.PreviousLap_NN*`', '00..09'],
    ['`IRacingExtraProperties.*`', 'varia por família — ver §8.1'],
]))
w()
w('### 1.7 Como ler nas fórmulas')
w('- NCalc: `[DataCorePlugin.GameData.SpeedKmh]` ou `[SpeedKmh]`.')
w("- JavaScript: `$prop('DataCorePlugin.GameData.SpeedKmh')` (ou `$prop('SpeedKmh')`).")
w('- HTTP: `GET http://localhost:8888/api/GetProperty/<nome>` → 200 com o valor, 204 quando não existe ou é nulo.')
w()

# ---------- 2 ----------
w('## 2. DataCorePlugin — propriedades de topo')
w()
w('Registradas em `DataCorePlugin.DeclareProperties`. Nenhuma tem atalho curto (use `DataCorePlugin.<nome>`).')
w()
rows = []
for k, (t, d) in DC.items():
    nm = 'DataCorePlugin.' + k
    live = '' if '<' in k else ('✓' if ok(nm) else '')
    hidden = 'oculta' if k in ('ComputedRPMPercent', 'RPMBlink', 'ComputedTurboPercent', 'BlinkTriggerRatio', 'RPMStartOffset', 'LowFuelLapLevel', 'CustomExpression.CurrentDateTime') else ''
    rows.append(['`%s`' % k, t, hidden, live, acc(d)])
w(table(['Nome (após `DataCorePlugin.`)', 'Tipo', 'Flag', 'Ao vivo', 'Descrição'], rows))
w()
w('Também do `DataCorePlugin`: `InputPressed : <nome>` / `InputReleased : <nome>` (Int32) são criadas pelo `PluginManager` quando um input mapeado é usado.')
w()

# ---------- 3 ----------
w('## 3. DataCorePlugin.GameData — telemetria normalizada')
w()
w('Nome completo: `DataCorePlugin.GameData.<Nome>`; atalho: `<Nome>`. A mesma árvore existe duplicada e oculta em `DataCorePlugin.GameData.NewData.<Nome>`. '
  'Coluna **iR** = suporte no iRacing (S fornecido, C calculado, — indisponível, · sem declaração). Valores "padrão" são os de uma instância vazia.')
w()
rows = []
for p in walk:
    n, al, ty, at, sample = p[0], p[1], p[2], p[3], p[4]
    if n.startswith('GameData.BestLapOpponent.'): continue
    short = n.replace('GameData.', '')
    flags = []
    if 'HIDDEN' in at: flags.append('oculta')
    if 'Obsolete' in at: flags.append('obsoleta')
    if 'Computed' in at: flags.append('calculada')
    note = ''
    if 'null-in-sample' in at:
        if ty.startswith('List<') or short in ('Raw', 'RawData'): note = 'não exposta'
        else: note = 'objeto; filhos só se não-nulo'
    live = '✓' if ok('DataCorePlugin.' + n) else ''
    al2 = aliases.get(n)
    d = describe(short)
    if al2: d = (d + ' ' if d else '') + 'Alias: ' + ', '.join(al2) + '.'
    member = short.rstrip('0123456789') if re.search(r'\d\d$', short) else short
    rows.append(['`%s`' % short, ty, ', '.join(flags + ([note] if note else [])), sup(member), live, d])
w(table(['Nome', 'Tipo', 'Flags', 'iR', 'Ao vivo', 'Descrição'], rows))
w()
w('`BestLapOpponent` (oculto) é um `Opponent` completo — o piloto dono da melhor volta da sessão — e expõe `DataCorePlugin.GameData.BestLapOpponent.<campo>` '
  'com os campos da tabela 5.4.')
w()

# ---------- 4 ----------
w('## 4. Suporte por jogo')
w()
w('Calculado a partir dos métodos `GD_*` de cada leitor (ver §1.5). S = fornecido pelo jogo, C = calculado pelo SimHub, — = não disponível. '
  'Só aparecem membros com alguma declaração. Leitores: ' + ', '.join('%s = `%s`' % (b, a.split('.')[-1]) for a, b in GAMES) + '.')
w()
rows = []
for r in sm[1:]:
    vals = [SYM.get(r[smh.index(g)], '?') for g, _ in GAMES]
    if all(v == '·' for v in vals): continue
    rows.append(['`%s`' % r[0]] + vals)
w(table(['Membro'] + [b for _, b in GAMES], rows))
w()
mgrs = [l.split('\t') for l in rd(os.path.join(O, 'managers.tsv')).splitlines()]
w('<details><summary>Todos os %d leitores de jogo encontrados</summary>' % len(mgrs))
w()
w(', '.join('`%s`' % m[1].split('.')[-1] for m in sorted(mgrs, key=lambda m: m[1].split('.')[-1].lower())))
w()
w('</details>')
w()

# ---------- 5 ----------
st = collections.defaultdict(list)
for line in rd(os.path.join(O, 'strings.tsv')).splitlines():
    p = line.split('\t')
    if len(p) == 3: st[p[1]].append(p[2])
def S(m): return st.get(m, [])
REG = 'SimHub.Plugins.OutputPlugins.Dash.TemplatingCommon.NCalcEngineMethodsRegistry::'
w('## 5. Pilotos e leaderboard (funções driver*)')
w()
w('Como `Opponents` é uma lista, o SimHub não a expõe como propriedade. O acesso é por funções de fórmula (NCalc e JS), indexadas pela '
  '**posição no leaderboard** (1 = líder). Para "quem está à frente na pista" use `getopponentleaderboardposition_aheadbehind(-1)` e passe o resultado '
  'para `driver*()`, ou as propriedades `PersistantTrackerPlugin.DriverAhead_NN_*` (§7.1) / `IRacingExtraProperties` (§8.1).')
w()
w('### 5.1 `driver<campo>(posição)`')
ini = S(REG + 'InitOpponentsData')
pairs = [(ini[i], ini[i + 1]) for i in range(0, len(ini) - 1, 2)]
sector_keys = {'bestlap', 'lastlap', 'currentlap', 'best'}
seen = set(); rows = []; srows = []
after_sector = False
for k, d in pairs:
    if k == 'CurrentSector': after_sector = True
    if after_sector and k.lower() in sector_keys and 'sector' in d.lower():
        srows.append(['`driversector%s(pos, setor, acumulado)`' % k.lower(), d]); continue
    nm = 'driver' + k.lower()
    if nm in seen: continue
    seen.add(nm); rows.append(['`%s(pos)`' % nm, d])
w(table(['Função', 'Descrição (texto original do SimHub)'], rows))
w()
w('Também: `isplayer(pos)` (= `driverisplayer`).')
w()
w('### 5.2 `driversector<campo>(posição, setor, acumulado)`')
w(table(['Função', 'Descrição'], srows))
w()
w('### 5.3 Localizar pilotos e classes')
rows = []
for m in ['AddOpponentsFindingMethods', 'AddBestSplitTimesMethods', 'AddCarClassesMethods']:
    s = S(REG + m)
    for i in range(0, len(s) - 2, 3): rows.append(['`%s(%s)`' % (s[i], s[i + 1]), s[i + 2]])
w(table(['Função', 'Descrição'], rows))
w()
w('### 5.4 Campos do objeto `Opponent`')
w('Tipos lidos de `GameReaderCommon.Opponent` (é o que `driver*()` consulta e o que aparece em `GameData.BestLapOpponent.*`).')
w()
rows = []
for p in walk:
    if p[0].startswith('GameData.BestLapOpponent.'):
        f = []
        if 'Obsolete' in p[3]: f.append('obsoleto')
        if 'Computed' in p[3]: f.append('calculado')
        if 'null-in-sample' in p[3]: f.append('objeto')
        rows.append(['`%s`' % p[0].split('.', 2)[2], p[2], ', '.join(f)])
w(table(['Campo', 'Tipo', 'Flags'], rows))
w()

# ---------- 6 ----------
w('## 6. GameRawData do iRacing')
w()
w('Dados crus do leitor (`IRacingReader.DataSampleEx`, que implementa `IExposable`). O `GetValues()` expõe exatamente:')
w()
w('- `GameRawData.Telemetry.<var>` — variáveis do irsdk (dicionário; **arrays ficam de fora**);')
w('- `GameRawData.Telemetry.SessionFlagsDetails.Is<flag>` — cada bit de `SessionFlags` como booleano;')
w('- `GameRawData.SessionData.*` — o YAML da sessão já tipado;')
w('- `GameRawData.CurrentSessionInfo.*` — a sessão corrente (`SessionInfo.SessionsNN` da sessão ativa; nulo fora de sessão).')
w()
w('Prefixo `DataCorePlugin.` opcional aqui (§1.2). Arrays `CarIdx*` (posições, % de volta, pneus etc. de cada carro) não viram propriedade. '
  'O `Telemetry` é um `Dictionary<string, object>` com propriedades tipadas, e `NewRawData()` no JavaScript devolve o objeto cru — então '
  '`NewRawData().Telemetry.CarIdxLapDistPct[idx]` deve funcionar em sessão (não testado aqui: fora de sessão `NewRawData()` devolve null). '
  'Outros dashboards instalados já leem o objeto cru assim (`NewRawData().Cars[...]`, de outro jogo).')
w()
w('### 6.1 Telemetry (variáveis presentes na amostra do SimHub)')
tel = json.load(open(os.path.join(SH, 'PluginsData', 'IRacing', 'SampleTelemetry.json'), encoding='utf-8'))
tn = ['DataCorePlugin.GameRawData.Telemetry.' + k for k, v in tel.items() if not isinstance(v, list)]
probe_all(tn)
def jt(v):
    if isinstance(v, bool): return 'bool'
    if isinstance(v, int): return 'int'
    if isinstance(v, float): return 'float'
    if isinstance(v, list): return 'array[%d]' % len(v)
    if v is None: return 'null'
    return type(v).__name__
rows = []; arr = []
for k, v in tel.items():
    if isinstance(v, list): arr.append('`%s`[%d]' % (k, len(v))); continue
    rows.append(['`%s`' % k, jt(v), '✓' if ok('DataCorePlugin.GameRawData.Telemetry.' + k) else '', json.dumps(v)[:40]])
w('Fonte da lista: `PluginsData\\IRacing\\SampleTelemetry.json` (%d variáveis; o conjunto real depende do carro). Exemplo = valor na amostra.' % len(tel))
w()
w(table(['Variável', 'Tipo', 'Ao vivo', 'Exemplo'], rows))
w()
w('Arrays na amostra (não expostos como propriedade): ' + (', '.join(arr) if arr else 'nenhum'))
w()
w('### 6.2 SessionFlagsDetails')
flags = ['checkered', 'white', 'green', 'yellow', 'red', 'blue', 'debris', 'crossed', 'yellowWaving', 'oneLapToGreen', 'greenHeld', 'tenToGo', 'fiveToGo',
         'randomWaving', 'caution', 'cautionWaving', 'black', 'disqualify', 'servicible', 'furled', 'repair', 'startHidden', 'startReady', 'startSet', 'startGo']
vals = [1 << i for i in range(21)] + [268435456, 536870912, 1073741824, 2147483648]
probe_all(['DataCorePlugin.GameRawData.Telemetry.SessionFlagsDetails.Is' + f for f in flags])
w(table(['Propriedade', 'Bit', 'Ao vivo'], [['`GameRawData.Telemetry.SessionFlagsDetails.Is%s`' % f, str(v), '✓' if ok('DataCorePlugin.GameRawData.Telemetry.SessionFlagsDetails.Is' + f) else ''] for f, v in zip(flags, vals)]))
w()
w('### 6.3 Enums úteis do irsdk')
w(table(['Variável', 'Valores'], [
    ['`SessionState`', '0 Invalid, 1 GetInCar, 2 Warmup, 3 ParadeLaps, 4 Racing, 5 Checkered, 6 CoolDown'],
    ['`PlayerTrackSurface` / `CarIdxTrackSurface`', '-1 NotInWorld, 0 OffTrack, 1 InPitStall, 2 AproachingPits, 3 OnTrack'],
    ['`EngineWarnings` (bits)', '1 WaterTemp, 2 FuelPressure, 4 OilPressure, 8 EngineStalled, 16 PitSpeedLimiter, 32 RevLimiterActive'],
]))
w()
w('### 6.4 SessionData (estrutura tipada)')
w('Árvore lida do tipo `IRacingReader.SessionData`. `[i]` vira `NN` começando em **01** (`DriverInfo.Drivers01` = primeiro da lista do YAML). '
  'Os campos são os que o SimHub tipou; o YAML real pode ter mais. Os que são `String` no YAML (ex.: `TrackLength = "6.93 km"`) chegam como texto com unidade.')
w()
raw = [l.split('\t') for l in rd(os.path.join(O, 'iracing_raw.txt')).splitlines()[1:] if '\t' in l]
sd = [r for r in raw if r[0].startswith('GameRawData.SessionData') or r[0].startswith('GameRawData.CurrentSessionInfo')]
sd_names = []
for r in sd:
    nm = 'DataCorePlugin.' + r[0].replace('[i]', '01')
    sd_names.append(nm)
probe_all(sd_names)
rows = []
for r in sd:
    if r[0].startswith('GameRawData.SessionData.DriverInfo.CompetingDrivers') or r[0].startswith('GameRawData.CurrentSessionInfo.Results'): continue
    if r[1].startswith('_') or r[1].endswith('[]') or r[1] in ('SessionData', 'Telemetry', 'GearRatios', 'Object') or r[1].startswith('Dictionary'): continue
    nm = 'DataCorePlugin.' + r[0].replace('[i]', '01')
    rows.append(['`%s`' % r[0].replace('GameRawData.', '').replace('[i]', 'NN'), r[1], '✓' if ok(nm) else ''])
w(table(['Caminho (após `GameRawData.`)', 'Tipo', 'Ao vivo'], rows))
w()
w('`DriverInfo.CompetingDrivers` tem os mesmos campos de `Drivers` (só pilotos competindo, sem pace car/espectador). '
  '`CurrentSessionInfo` tem os mesmos campos de `SessionInfo.SessionsNN`. `CarSetup.Chassis.InCarDials.*` só existe para carros que publicam esses dials.')
w()

# ---------- 7 core plugins ----------
act = json.load(open(os.path.join(SH, 'PluginsData', 'PluginsActivation.json'), encoding='utf-8'))
enabled = {a['ClassName'].split('.')[-1]: a['IsEnabled'] for a in act}
def en(cls):
    if cls not in enabled: return 'sempre ativo'
    return 'ativo' if enabled[cls] else '**desabilitado** nesta instalação'
w('## 7. Plugins do SimHub')
w()
def section(title, cls, prefix, items, note=None):
    w('### ' + title)
    w('Prefixo `%s.` — %s.' % (prefix, en(cls)))
    if note: w(); w(note)
    w()
    names = [prefix + '.' + i[0] for i in items if '<' not in i[0] and 'NN' not in i[0]]
    probe_all(names)
    rows = []
    for nm, ty, d in items:
        live = '' if ('<' in nm or 'NN' in nm) else ('✓' if ok(prefix + '.' + nm) else '')
        if 'NN' in nm:
            live = '✓' if ok(prefix + '.' + nm.replace('NN', '00')) or ok(prefix + '.' + nm.replace('NN', '01')) else ''
        rows.append(['`%s`' % nm, ty, live, d])
    w(table(['Nome', 'Tipo', 'Ao vivo', 'Descrição'], rows))
    w()

rl = []
for t in ['AllTimeBest', 'SessionBest']:
    rl += [(t, 'TimeSpan', 'Tempo de referência (%s).' % ('melhor de todos os tempos' if t == 'AllTimeBest' else 'melhor da sessão')),
           (t + 'LastLapDelta', 'Double', 'Delta da última volta contra a referência (s).'),
           (t + 'LiveDelta', 'TimeSpan', 'Delta ao vivo (oculta).'),
           (t + 'LiveDeltaSeconds', 'Double', 'Delta ao vivo em segundos.'),
           (t + 'LiveDeltaProgressSeconds', 'Double', 'Variação do delta (ganhando/perdendo) em segundos.')]
rp = [('Name', 'String', 'Nome'), ('ShortName', 'String', 'Nome curto'), ('Initials', 'String', 'Iniciais'), ('Distance', 'Double', 'Distância na pista até o jogador'),
      ('Gap', 'Double', 'Gap em segundos'), ('GapToPlayer', 'Double', 'Gap ao jogador'), ('RaceGapToPlayer', 'String', 'Gap ao jogador formatado (tempo ou voltas)'),
      ('RaceGapToLeader', 'String', 'Gap ao líder formatado'), ('Position', 'Int32', 'Posição'), ('CarName', 'String', 'Carro'), ('CarNumber', 'String', 'Número'),
      ('CarClass', 'String', 'Classe'), ('IRating', 'Double', 'iRating'), ('CurrentLap', 'Int32', 'Volta atual'), ('LastLapTime', 'TimeSpan', 'Última volta'),
      ('BestLapTime', 'TimeSpan', 'Melhor volta'), ('LapsToPlayer', 'Int32', 'Voltas de diferença para o jogador'), ('LapsToLeader', 'Int32', 'Voltas de diferença para o líder'),
      ('Speed', 'Double', 'Velocidade')]
items = []
for side, pt in [('DriverAhead', 'à frente'), ('DriverBehind', 'atrás')]:
    for k, t, d in rp: items.append(('%s_NN_%s' % (side, k), t, '%s — piloto NN %s na pista (00..04).' % (d, pt)))
items += [('PreviousLap_NN', 'TimeSpan', 'Tempo da volta anterior N (00 = mais recente, até 09).'),
          ('PreviousLap_NN_DeltaToAllTimeBest', 'Double', 'Delta dessa volta contra a melhor de todos os tempos.'),
          ('PreviousLap_NN_DeltaToSessionBest', 'Double', 'Delta contra a melhor da sessão.'),
          ('PreviousLap_NN_DeltaToBest', 'Double', 'Delta contra a melhor (oculta).'),
          ('PreviousLap_NN_IsCurrentSession', 'Int32', 'A volta é da sessão atual (0/1).'),
          ('EstimatedLapTime', 'TimeSpan', 'Volta estimada (oculta).'),
          ('EstimatedLapTime_AllTimeBestBased', 'TimeSpan', 'Volta estimada com base no recorde pessoal.'),
          ('EstimatedLapTime_SessionBestBased', 'TimeSpan', 'Volta estimada com base na melhor da sessão.'),
          ('EstimatedLapTime_SessionBestBasedSimhub', 'TimeSpan', 'Idem, cálculo do SimHub.'),
          ('EstimatedLapTime_SessionBestBasedSimhub_EstimatedDelta', 'Double', 'Delta estimado dessa estimativa.'),
          ('EstimatedLapTime_SessionBestBasedSimhub_ReferenceLapTime', 'TimeSpan', 'Volta de referência usada.')] + rl
section('7.1 Statistics / PersistantTracker', 'LapHitoryPlugin', 'PersistantTrackerPlugin', items,
        'Plugin "Statistics" (classe `PersistantTrackerPlugin`). Gera os deltas ao vivo, histórico de voltas e os pilotos vizinhos na pista. '
        'Eventos `NewAllTimeBest`, `NewRecord`, `NewSessionBest`; ações `ClearLapHistory`, `DiscardCurrentMap`.')
section('7.2 System Info', 'SystemInfoPlugin', 'SystemInfoPlugin', [
    ('CPULoadPercent', 'Double', 'Uso de CPU %.'), ('MemoryLoadPercent', 'Double', 'Uso de memória %.'),
    ('SimHubProcessor', 'Double', 'CPU usada pelo SimHub %.'), ('Uptime', 'TimeSpan', 'Tempo ligado do Windows.')])
section('7.3 SystemInfosProvider (agregador de sensores e mídia)', 'SystemInfosProvider', 'SystemInfosProvider', [
    ('MainCPUTemp', 'Double', 'Temperatura da CPU (da fonte escolhida: Afterburner/HWiNFO/Aida64/SimHub).'),
    ('MainCPULoad', 'Double', 'Carga da CPU.'), ('MainCPUFanSpeed', 'Double', 'Ventoinha da CPU.'),
    ('MainGPUTemp', 'Double', 'Temperatura da GPU.'), ('MainGPULoad', 'Double', 'Carga da GPU.'), ('MainGPUFanSpeed', 'Double', 'Ventoinha da GPU.'),
    ('CurrentFrameRate', 'Double', 'FPS do jogo.'), ('MemoryLoad', 'Double', 'Uso de memória.'),
    ('Title', 'String', 'Título da mídia tocando (Windows).'), ('Artist', 'String', 'Artista da mídia.'),
    ('MonitorPowerStatus', 'Boolean', 'Monitor ligado.')],
    'O mapeamento de cada campo para um sensor fica em `PluginsData\\Common\\SystemInfosProvider.SystemInfosProvider.json`. '
    'Fontes: `AfterburnerPlugin.*` (`AfterburnerConnected` + um nome por sensor do MSI Afterburner, ex. `AfterburnerPlugin.GLOBAL.Framerate_FPS`), '
    '`Aida64Plugin.*` (`Aida64Connected` + sensores), `HWinfoPlugin.*` (sensores). Os nomes dos sensores vêm do programa externo, não do SimHub. '
    'Ações: `MediaNext`, `MediaPlayPause`, `MediaPrevious`.')
section('7.4 ShakeIt Bass Shakers / Motors', 'ShakeITBSV3Plugin', 'ShakeITBSV3Plugin', [
    ('GlobalGain', 'Double', 'Ganho global.'), ('IsMuted', 'Int32', 'Mudo (0/1).'),
    ('<efeito>...', 'Double', 'Cada efeito/saída configurado exporta seu valor (ExportProperties) — nomes vêm da configuração do usuário.')],
    'O mesmo conjunto existe com prefixo `ShakeITMotorsV3Plugin.` (ShakeIt Motors). Ações: `MainFeedbackLevelIncrement/Decrement`, `ToggleMuteFeedback`, `ResetCalibration`.')
section('7.5 ShakeIt Wind', 'ShakeItWindPlugin', 'ShakeItWindPlugin', [
    ('ActiveMode', 'String', 'Modo ativo (Static/Dynamic).'), ('ActiveModeGain', 'Double', 'Ganho do modo ativo.'), ('ActiveModeIsEnabled', 'Boolean', 'Modo ativo habilitado.'),
    ('OutputLeft', 'Double', 'Saída esquerda.'), ('OutputCenter', 'Double', 'Saída central.'), ('OutputRight', 'Double', 'Saída direita.'),
    ('<Modo>.Gain / .IsEnabled / .OutputLeft / .OutputCenter / .OutputRight', 'Double/Int32', 'Por modo (`Static`, `Dynamic`).')])
section('7.6 Arduino (SerialDash)', 'SerialDashPlugin', 'SerialDashPlugin', [
    ('CurrentLedLayout', 'String', 'Perfil de LEDs ativo.'), ('DisplayIntensity', 'Int32', 'Brilho dos displays.'), ('RGBIntensity', 'Int32', 'Brilho dos LEDs RGB.'),
    ('BlinkTriggerRatioChanged', 'Int32', 'Mudou o limiar de pisca.'), ('RPMStartOffset', 'Object', 'Offset de RPM.'),
    ('GLCDTemplate / OLEDTemplate / SCREEN_<n>', 'Int32', 'Tela ativa de cada display GLCD/OLED.')])
section('7.7 Controllers input (joystick)', 'JoystickPlugin', 'JoystickPlugin', [
    ('<Dispositivo>_<Botão>', 'Int32?', 'Estado de cada botão/eixo dos controles habilitados.')],
    'Botões aparecem também como `InputStatus.JoystickPlugin.<Dispositivo>_B<n>` (usado por mapeamentos). Os dispositivos desta máquina estão em '
    '`PluginsData\\Common\\JoystickPluginSettings.json`: `Realdrive_DD_T112`, `Volante_PRS-Formula`, `PedalDS`.')
section('7.8 Áudio', 'AudioControlPlugin', 'AudioControlPlugin', [
    ('AudioPeak', 'Double', 'Pico de áudio.'), ('AudioPeakLeft', 'Double', 'Pico canal esquerdo.'), ('AudioPeakRight', 'Double', 'Pico canal direito.'),
    ('AudioFFT_Range_<n>', 'Double', 'Faixas de FFT.'), ('SoundsVolume', 'Int32', 'Volume dos sons tocados pelo plugin.')],
    'Classe `AudioPlayPlugin` registra `SoundsVolume` e as ações `Play_<som>`, `IncrementSoundsVolume`, `DecrementSoundsVolume`.')
section('7.9 Web', 'WebPlugin', 'WebPlugin', [('ServerBaseUrl', 'String', 'URL do servidor web do SimHub na rede.')])
section('7.10 Outros plugins nativos', 'HeadsetInfo', 'HeadsetInfo', [
    ('BatteryLevel', 'Int32', 'Headset Logitech G533: bateria %.'), ('BatteryVoltage', 'Double', 'Tensão.'), ('Status', 'String', 'Unplugged/Sleeping/Full/Charging/Discharging.')],
    'Demais (todos **desabilitados** aqui, exceto onde indicado):\n\n'
    '- `ThrustmastersPlugin.` — `OverallGain`, `DefaultWheelAngle`, `WheelDetected` (Int32).\n'
    '- `BeltTensionnerPlugin.` — `Status.Left`, `Status.Right`, `Status.LeftWithoutAutoCenter`, `Status.RightWithoutAutoCenter` (Double).\n'
    '- `SimuLightPlugin.` — `AdalightEnabled`, `AdalightDarkMode`, `AdalightGlobalBrightness`, `OtherLightsEnabled`, `OtherLightsDarkMode`, `OtherLightsGlobalBrightness`, `CaptureFreeze`.\n'
    '- `MotionPlugin.` — `Global.MotionEnabled`, `Global.MotionSuspended`, `Global.DeviceState`, `Global.ActiveMotionSetup`, `Global.ActiveProfilePreset`, '
    '`Global.GlobalMotionSmoothing`, `Global.MotionDetailAmplifier.Enabled/Gain`, `Global.BeltTensioner.KeepParked/Offset`, `Global.TrackProfiler.*` '
    '(CurrentLapValidForProfiling, TrackRecordsCount, MaxPitch, MinPitch, SmoothedMaxPitch, SmoothedMinPitch, CurrentPositionTrackPitch, IsClosedTrack), '
    '`Global.GeometryPrimaryOverflow`, `Global.GeometryOverflowScaling*`, `MotionCompensationComponent.<nome>.*` e por efeito `<efeito>.Enabled/.Gain/.Smoothing/.IsMuted/.IsIsolated/.Washout/.EnableWashout`.\n'
    '- `ControlMapperPlugin.` — estado de cada papel mapeado.\n'
    '- `KeyboardEmulatorPlugin` (ativo) não registra propriedades; só ações.')
w('### 7.11 Propriedades criadas pelo usuário')
w('- `DataCorePlugin.CustomExpression.<nome>` — expressões personalizadas.')
w('- `DataCorePlugin.ExternalScript.<nome>` — blocos `[ExportProperty]` dos scripts em `NCalcScripts\\*.ini` (o `samples.ini` instalado gera, por exemplo, '
  '`DataCorePlugin.ExternalScript.BlinkingGear` — conferido: 200). `[ExportEvent]` vira o evento `DataCorePlugin.ExternalScript.<nome>`; `[ExportLed]` não vira propriedade.')
w('- `DataCorePlugin.Debug_<nome>` — pontos de gráfico de depuração.')
w('- `variable.<nome>` / `[variable.x]` — variáveis de dashboard do Dash Studio (escopo do dash, não globais).')
w()

# ---------- 8 third party ----------
w('## 8. Plugins de terceiros instalados')
w()
regs_txt = rd(os.path.join(O, 'regs.txt'))
def regs_types(dllname):
    out = {}; last = {}
    cur = None
    for line in regs_txt.splitlines():
        if line.startswith('## '): cur = line.split()[1]; continue
        if cur != dllname or not line.startswith('	'): continue
        _, kind, ty, dyn, strs, mname = line.split('	')
        if ty.startswith('Nullable['): ty = ty[9:-1] + '?'
        if ty in ('T', 'U'): ty = ''
        parts = [x.strip() for x in strs.split(' | ')] if strs else []
        idents = [x for x in parts if re.match(r'^[A-Za-z_][\w.]*$', x)]
        for x in idents: out.setdefault(x, set())
        if idents and ty: last.setdefault(idents[-1], set()).add(ty)
        if dyn:
            j = ''.join(p for p in parts if re.match(r'^[\w{}:.]*$', p))
            if j: last.setdefault(j, set()).add(ty) if ty else out.setdefault(j, set())
    for k, v in last.items(): out[k] = v
    return out

# 8.1 IRacingExtraProperties
w('### 8.1 RSC — iRacing Extra Properties')
w('Prefixo `IRacingExtraProperties.` — %s. Lista de nomes do próprio autor (`RSC.iRacingExtraProperties.txt`, 586 famílias); '
  'faixas medidas agora variando o primeiro `NN` (o segundo `NN`, quando existe, ficou em 00). O plugin informa ter **%s** propriedades registradas '
  '(`IRacingExtraProperties.PropertyCount`).' % (en('IRacingExtraProperties'), get('IRacingExtraProperties.PropertyCount')[1] or '?'))
w()
pr = {}
for line in rd(os.path.join(O, 'probe_rsc.tsv')).splitlines():
    p = line.split('\t')
    pr[p[0]] = p
rt = regs_types('RSC.iRacingExtraProperties.dll')
rtn = {}
for k, v in rt.items():
    rtn[re.sub(r'\{0:00\}', 'NN', k)] = v
fams = collections.OrderedDict()
for n in rd(os.path.join(SH, 'RSC.iRacingExtraProperties.txt')).splitlines():
    n = n.strip()
    if not n: continue
    fams.setdefault(re.sub(r'(?<=_)\d\d(?=_|$)', 'NN', n), n)
def guess_type(val):
    v = val.strip()
    if v == '': return 'String'
    if v in ('true', 'false'): return 'Boolean'
    if re.match(r'^"?-?\d+:\d\d:\d\d', v) or re.match(r'^"\d+\.\d\d:\d\d', v): return 'TimeSpan'
    if re.match(r'^-?\d+$', v): return 'número'
    if re.match(r'^-?\d+\.\d+(E[-+]?\d+)?$', v): return 'Double'
    return 'String'
groups_rsc = collections.OrderedDict()
for fam, sample in fams.items():
    short = fam.replace('IRacingExtraProperties.', '')
    head = short.split('_')[0] if not short.startswith('iRacing_') else 'iRacing_' + short.split('_')[1]
    groups_rsc.setdefault(head, []).append((fam, sample, short))
for head, lst in groups_rsc.items():
    rows = []
    for fam, sample, short in lst:
        p = pr.get(fam)
        if p and p[1] == 'RANGE': rng, live = p[2], ('✓' if p[2] != 'none(204)' else '')
        elif p: rng, live = '', ('✓' if p[1] == '200' else '')
        else: rng, live = '', ''
        if rng == 'none(204)': rng = '(nulo agora)'
        t = rtn.get(short) or rtn.get(short.replace('iRacing_', ''))
        ty = '/'.join(sorted(x for x in t if x)) if t else ''
        if not ty:
            v = get(sample)[1] if live else ''
            ty = guess_type(v) + '*' if v else ''
        rows.append(['`%s`' % short, ty, rng, live])
    w('<details><summary><code>%s*</code> — %d famílias</summary>' % (head, len(lst)))
    w()
    w(table(['Nome', 'Tipo', 'Faixa NN', 'Ao vivo'], rows))
    w()
    w('</details>')
    w()
w('Tipo com `*` = deduzido do valor atual (não encontrado no registro estático).')
w()

# 8.2 other RSC + Dahl
prev = [l.strip() for l in rd(PREV).splitlines() if l.strip() and not l.startswith('#')]
def plugin_section(title, prefix, dll, cls, desc=None):
    rt = regs_types(dll)
    cands = set()
    for k in rt:
        if '{' in k: continue
        cands.add(prefix + '.' + k)
    for n in prev:
        if n.startswith(prefix + '.'): cands.add(n.replace('NN', '01'))
    probe_all(cands)
    found = sorted(c for c in cands if ok(c))
    w('### ' + title)
    w('Prefixo `%s.` — %s.%s' % (prefix, en(cls), (' ' + desc) if desc else ''))
    w()
    rows = []
    for c in found:
        short = c[len(prefix) + 1:]
        t = rt.get(short)
        ty = '/'.join(sorted(x for x in t if x)) if t else ''
        if not ty: ty = guess_type(get(c)[1]) + '*'
        rows.append(['`%s`' % short, ty])
    dyn = sorted(k.replace('{0:00}', 'NN').replace('{0:0}', 'N') for k in rt if '{' in k and re.match(r'^[\w{}:]+$', k))
    if rows:
        w('<details><summary>%d propriedades confirmadas ao vivo</summary>' % len(rows))
        w()
        w(table(['Nome', 'Tipo'], rows))
        w()
        w('</details>')
    else:
        w('Nenhuma confirmada ao vivo agora.')
    if dyn:
        w(); w('Padrões dinâmicos no código: ' + ', '.join('`%s`' % d for d in dyn))
    w()
    return len(rows)

plugin_section('8.2 Dahl Design', 'DahlDesign', 'DahlDesign.dll', 'DahlDesign',
               'Propriedades do pacote Dahl Design (dashboards DDU/DDC, spotter, rotary, smooth gear). Lista = nomes do código + dos dashboards instalados, confirmados no servidor.')
for t, pfx, dll in [('8.3 RSC — The Many-Faced Dash', 'TheManyFacedDash', 'RSC.TheManyFacedDash.dll'),
                    ('8.4 RSC — Input Display (ExtraInputProperties)', 'ExtraInputProperties', 'RSC.ExtraInputProperties.dll'),
                    ('8.5 RSC — Auto Brightness', 'AutoBrightness', 'RSC.AutoBrightness.dll'),
                    ('8.6 RSC — Checklist', 'Checklist', 'RSC.Checklist.dll'),
                    ('8.7 RSC — SimHUD Projection', 'SimHUDProjection', 'RSC.SimHUDProjection.dll'),
                    ('8.8 RSC — Persistent Odometer', 'PersistentOdometer', 'RSC.PersistentOdometer.dll'),
                    ('8.9 RSC — Logitech Battery', 'LogitechBatteryLevel', 'RSC.LogitechBatteryLevel.dll'),
                    ('8.10 RSC — Sounds', 'Sounds', 'RSC.Sounds.dll'),
                    ('8.11 RSC — Updater', 'Updater', 'RSC.Updater.dll')]:
    plugin_section(t, pfx, dll, pfx)
w('Os plugins RSC também gravam em `InputStatus.*` (ex.: `InputStatus.GraphicalDashPlugin.DashChecklistItemN`, marcha do H-shifter) e todos têm `AAA.ShowAllProps`, '
  '`AAA.LogPluginPerformance` e `DataUpdateFrametime`.')
w()
w('> `LovelyPlugin.*` aparece nos dashboards baixados mas o plugin **não está instalado** — essas propriedades não existem nesta máquina.')
w()

# ---------- 9/10 events, actions ----------
ev = collections.defaultdict(set); ac = collections.defaultdict(set)
for line in rd(os.path.join(O, 'calls.tsv')).splitlines():
    p = line.split('\t')
    if len(p) < 4: continue
    m = re.search(r'\.(AddEvent|AddAction)<', p[2])
    if not m or not (p[0].startswith('SimHub') or p[0].startswith('RSC') or p[0].startswith('Dahl')): continue
    if 'LoggingView' in p[1] or 'PatternBuilder' in p[1]: continue
    toks = re.findall(r'"((?:[^"\\]|\\.)*)"|<(Concat|Format)>', p[3])
    s = [a for a, b in toks if not b]
    if not s: continue
    dyn = any(b for a, b in toks)
    name = s[-1] + ('…' if dyn else '')
    owner = p[1].split('::')[0].split('.')[-1].split('`')[0].split('+')[0]
    (ev if m.group(1) == 'AddEvent' else ac)[owner].add(name)
w('## 9. Eventos')
w('Usáveis em gatilhos (ShakeIt, LEDs, `timesincelastevent(nome)`). Nome completo: `<Plugin>.<evento>`.')
w()
w(table(['Origem', 'Eventos'], [[k, ', '.join('`%s`' % x for x in sorted(v))] for k, v in sorted(ev.items())]))
w()
w('## 10. Ações')
w('Mapeáveis em *Controls and events* e chamáveis por `triggeraction(nome)` ou `GET /api/TriggerAction/<nome>`. "…" = nome com parte dinâmica.')
w()
w(table(['Origem', 'Ações'], [[k, ', '.join('`%s`' % x for x in sorted(v))] for k, v in sorted(ac.items())]))
w()

# ---------- 11 functions ----------
w('## 11. Funções de fórmula (NCalc e JavaScript)')
w()
cc = S('SimHub.Plugins.OutputPlugins.Dash.TemplatingCommon.NCalcEngineBase::.cctor')
i = 1; rows = []
while i + 2 < len(cc):
    if cc[i].startswith('Function '): break
    rows.append(['`%s`' % cc[i + 1], cc[i + 2]]); i += 3
gen = S(REG + 'AddGenericMethods') + S(REG + 'AddColorFunctions') + S(REG + 'AddControllerFunctions')
w('### 11.1 Gerais')
w(table(['Assinatura', 'Descrição (original)'], rows))
w()
w('Só existem no NCalc, além das acima: `progress`, `setvalue`, `getvalue`. JS tem também `root`, `setcomponentproperty`, `NewRawData()`, `OldRawData()`.')
w()
w('### 11.2 Dash Studio, cores e controles')
rows = []
for m in ['AddGenericMethods', 'AddColorFunctions']:
    s = S(REG + m)
    for k in range(0, len(s) - 2, 3): rows.append(['`%s(%s)`' % (s[k], s[k + 1]), s[k + 2].replace('\\r\\n', ' ')])
rows += [["`getcontrollerbuttonstate('vidpidquery', buttonId)`", 'Estado (bool) do botão buttonId (a partir de 0) do primeiro controle que casa com a query; null se não achar.'],
         ["`getcontrollername('vidpidquery')`", 'Nome do primeiro controle que casa com a query; null se não achar.'],
         ["`getcontrollerpid('vidpidquery')`", 'Product ID do controle; null se não achar.'],
         ["`getcontrolleraxis('vidpidquery', axisid)`", 'Valor do eixo: 0 X, 1 Y, 2 Z, 3-5 rotação X/Y/Z, 6-7 sliders, 8-11 sliders de aceleração/velocidade, 12-14 aceleração X/Y/Z, 15+ POV.'],
         ['(vidpidquery)', "VID,PID em hex (`'0x1234,0x4567'`); várias separadas por `;`; `*` é coringa. Requer o plugin de controles e só lê dispositivos habilitados."]]
w(table(['Função', 'Descrição'], rows))
w()
keys = js('return Object.keys(this).join(",");')
if keys:
    w('### 11.3 Globais do motor JavaScript (lidas agora do SimHub)')
    w(', '.join('`%s`' % k for k in keys.split(',') if k and not k.startswith('eval')))
    w()

# ---------- 12 API ----------
w('## 12. API HTTP local (`http://localhost:8888`)')
w(table(['Rota', 'O que faz'], [
    ['`GET /api/GetProperty/{nome}`', 'Valor de uma propriedade (200) ou 204.'],
    ['`GET /api/EvaluateStringFormula?formula=...&interpreter=0|1`', 'Avalia uma fórmula (0 = NCalc, 1 = JavaScript).'],
    ['`GET /api/GetGamedata`', 'Objeto GameData inteiro em JSON.'],
    ['`GET /api/GetGameDataSimple`', 'Versão resumida.'],
    ['`GET /api/GetLeaderboarddata`, `/api/GetPlayerLeaderboarddata`, `/api/Getaheadbehinddata`', 'Leaderboard e vizinhos.'],
    ['`GET /api/GetSessionLapsHistory`', 'Histórico de voltas da sessão.'],
    ['`GET /api/GetLedsData`', 'Estado dos LEDs.'],
    ['`GET /api/TriggerAction/{acao}`, `/api/TriggerInput/{input}`', 'Dispara ação/input.'],
    ['`POST /api/ExternalInput/Press|Release`, `/api/StreamDeckInput/...`', 'Inputs externos.'],
    ['`GET /api/Dashboards/GetDashboards`', 'Dashboards instalados.'],
    ['`/api/Devices/*`, `/api/Motion/*`, `/api/ControlMapper/*`', 'Dispositivos, Motion, Control Mapper.'],
]))
w()
w('Não há rota que liste todas as propriedades: `PluginManager.GetAllPropertiesNames()` existe, mas não é exposto por HTTP nem ao JavaScript (o Jint roda sem acesso ao CLR).')
w()

# ---------- 13 ----------
w('## 13. Limites desta análise')
w('- **Ao vivo vazio não é "não existe"**: o servidor devolve 204 também para valor nulo. Fora de sessão, muito do `GameData` e do `GameRawData` é nulo.')
w('- Variáveis de `GameRawData.Telemetry` dependem do carro (o irsdk publica conjuntos diferentes); a lista de §6.1 é a amostra que o SimHub guardou.')
w('- Nomes vindos de configuração do usuário (sensores do Afterburner/HWiNFO, efeitos do ShakeIt, botões de controle, expressões e scripts) só podem ser listados com a configuração em uso.')
w('- Descrições de `GameData` são minhas, a partir do nome, tipo e uso; as de §5 e §11 são o texto do próprio SimHub.')
w('- Para regenerar (com o SimHub aberto): `py tools/simhub_props.py`.')
w()
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('ok', len(L), 'lines', len(_cache), 'probes')
