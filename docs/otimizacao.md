# Handoff — otimização de desempenho do dash

Status em 2026-10-11: **plano aprovado para depois, nada executado.** O usuário
pediu primeiro o componente de setores (feito) e, em seguida, o plano dos
estados laterais (`docs/estados.md`). Este documento é para retomar a
otimização numa sessão nova sem reler a conversa.

## Por que

O PC do usuário tem gargalo de CPU. O dash roda dentro do SimHub junto com o
iRacing; cada fórmula de item visível é recalculada a cada quadro (~60 fps).
Objetivo: cortar avaliações por segundo sem mudar o visual.

## Como o SimHub gasta CPU (o que embasa o plano)

| Regra | Fonte |
|---|---|
| Toda fórmula de item **visível** roda a cada quadro, sem checar se mudou | OpenDash (engenharia reversa) |
| Item **invisível** só avalia o binding de `Visible`; filhos de layer escondida não rodam | OpenDash, SimHub 6.4.2 |
| `RenderingSkip` é o controle oficial de cadência: `n` = avalia 1 a cada `n+1` quadros (`1` ≈ 30 Hz, `9` ≈ 6 Hz, `29` ≈ 2 Hz) | Wiki Dash Studio — Bindings |
| `MinimumRefreshIntervalMS` existe mas não é documentado; comunidade usa 100–200 ms | fóruns |
| JS: `root` é estado **por fórmula**; não há como compartilhar estado entre fórmulas; engines são em pool | Wiki Javascript Formula Engine |
| Fórmula com erro é reiniciada em ciclos de 30 s (custa) — ver `[DataCorePlugin.LoggingErrorsCount]` | fórum "Lag on dashboards" |
| Gráficos são citados como o item mais pesado | Romainrob (comunidade) |

## Retrato atual (contado no build de `ce960ee`)

`iRacing_Dashboard_00.djson`: 116 itens com binding, **58 fórmulas JS + 133
NCalc**, 103 desses itens em `RenderingSkip 0`. Quando o plano foi feito eram
44 JS + 126 NCalc; a diferença é o componente de setores (`sectors.py`), que
já nasceu com cadência (`SKIP_LIVE = 2`, `SKIP_SLOW = 9`) — é o modelo a seguir.

Pontos quentes (sem mudança desde o plano):

- **Leaderboard** (`leaderboard.py` + `generated/formulas.py`): ~14 JS por
  linha × 13 linhas ≈ 180 avaliações JS por quadro (~11 mil/s). O `Gap` chama
  `$prop` até 7 vezes e converte tempo com `format`/`parseInt` 6 vezes.
- **Gráfico de telemetria** (widget `Telemetry`): 2 linhas de 600 pontos,
  espessura 5, atualização a 10 ms.
- **Desfoques**: brilho da marcha (`center.py`, blur 32, cor dinâmica) e LEDs
  do `rpmled.py` (3 halos por widget + 8 por camada de shift, 2 widgets).
- **Avisos** (`top_bar.py`): pílula e rótulo com `Visible`/`BlinkEnabled`
  repetidos nos dois lados (4 avaliações onde bastaria 1).
- **Campos lentos** a 60 Hz: hora, temperaturas, grip, chuva, vento,
  combustível, voltas, SoF, incidentes, tempo restante.
- **Fórmulas com estado**: flash do bias (2 JS, `left.bias_flash`) e
  balanço (2 JS fazendo a mesma conta, `balance.formula`).

## Feito a partir do relatório de propriedades (`docs/propriedades-simhub-completo.md`)

- **Fase 0 sem Gerenciador de Tarefas:** `python3 build.py --diag` gera também
  `iRacing_Dashboard_00_Diag`, o mesmo dash com uma faixa no rodapé
  (`src/dash/diag.py`, ~2 Hz) mostrando JS/s, NCalc/s (normais + otimizadas),
  fórmulas servidas do cache/s, duração do ciclo de dados (ms), CPU do processo
  SimHub e erros no log — tudo publicado pelo próprio SimHub
  (`DataCorePlugin.Performance_*`, `SystemInfoPlugin.SimHubProcessor`).
- **Máquina de estados calculada uma vez:** o `Visible` do cartão do gráfico
  (`states.clock()`) calcula e publica com `setsharedvalue`; os ~20
  consumidores leem com `getsharedvalueordefault`. Publicação com mais de 1 s
  ou SimHub sem o armazenamento → cada consumidor calcula sozinho, como antes.
  Testado nos dois modos em `tools/check_states.py`.
- **Tipo de sessão:** `GameRawData.CurrentSessionInfo.SessionType` (antes:
  nome `SessionsNN` montado pelo `SessionNum` a cada avaliação, com o caminho
  antigo como reserva). Leaderboard e modo da coluna direita leem o valor
  publicado pela máquina de estados (`states.SESSION_TYPE`) — 26 fórmulas por
  linha do leaderboard a menos montando a string.
- **Flash do bias em NCalc:** `isincreasing`/`isdecreasing` nativas, sem JS e
  sem `root`; o desbotamento virou 4 degraus (`left.BIAS_STEPS`).

- **Fase 3 — leaderboard reescrito** (`src/dash/leaderboard.py`): cada fórmula
  monta o prefixo da linha uma vez (`_row`), lê cada propriedade uma vez, e o
  gap do treino sai de `timespantoseconds` em centésimos (antes: o tempo
  formatado em texto três vezes por piloto). Linhas a ~6 Hz (`SKIP_ROW = 9`,
  no item; os layers ficam a 60 Hz). Conta estática por quadro (13 linhas +
  7 do overflow): `format()` 643 → 53, leituras de propriedade 1219 → 844;
  avaliações JS/s das linhas ~16.500 → ~1.800. Equivalência:
  `python3 tools/check_leaderboard.py` roda as 29 fórmulas originais
  (`tools/fixtures/leaderboard_legacy.json`) e as novas lado a lado em 3.000
  grids simulados; a auditoria chama esse teste e só aceita as originais como
  REESCRITAS se ele passar. Diferenças de propósito (contadas no teste):
  overflow com a paleta da tabela principal; gap de treino sem volta → N/A
  (antes "+-82.9"); cor de desconectado no overflow em corrida (o original lia
  `SessionTypeName`, que não existe); arredondamento exato na casa de 5
  centésimos.

Não feito ainda: tendência de ar/pista pelo plugin
(`iRacing_AirTemperatureChange`/`iRacing_TrackTemperatureChange` — formato do
texto desconhecido; conferir em `http://localhost:8888/api/GetProperty/IRacingExtraProperties.iRacing_TrackTemperatureChange`
em sessão) NCalc no leaderboard (as fórmulas usam `prop()` dinâmico, que o NCalc tem, mas a equivalência só é testável em JS).

## O plano (fases)

**Fase 0 — Medir.** Acrescentar ao `build.py` variantes de diagnóstico
(sugestão: `python3 build.py --variant {full,no-chart,no-blur,no-leaderboard,bare}`,
cada uma gerando um dash com nome próprio para coexistir no SimHub). O usuário
roda um replay fixo do iRacing ~1 min por variante e anota a CPU do processo
SimHub no Gerenciador de Tarefas, mais `LoggingErrorsCount`. Resultado decide
se as fases 3 e 4 valem.

**Fase 1 — Cadência por categoria (sem mudança visual).** Uma regra única no
gerador (ex.: helper `cadence(item, kind)` em `widgets.py`) aplicando
`RenderingSkip`:

| Dado | Cadência alvo |
|---|---|
| Pedais, RPM, LEDs, marcha, delta, balanço | 60 Hz (como hoje) |
| Avisos, OTS, velocidade | 20–30 Hz |
| Leaderboard, relative, lap log | ~4 Hz |
| Rodapés (hora, clima, combustível, sessão) | ~1 Hz |
| `Repetitions` e `Visible` dos modos | ~2 Hz |

Só o leaderboard cai de ~11 mil para ~700 avaliações JS/s. Maior ganho, menor
risco. Cuidado: `RenderingSkip` em `Layer` vs. em item — confirmar no preview
qual nível o SimHub respeita (os setores aplicam no item).

**Fase 2 — Gráfico.** 600 → 200–250 pontos por linha, espessura 3,
`RenderingSkip 1`. Mesmo intervalo de tempo, menos resolução. Arquivo:
`src/dash/generated/telemetry.py`.

**Fase 3 — Reescrever o JS do leaderboard.** Prefixo
`iRacing_ClassLeaderboard_Driver_NN_` montado uma vez, cada `$prop` lido uma
vez, gap calculado sem passar por texto, NCalc onde der. **Esbarra no
`tools/formula_audit.py`**, que exige as 103 fórmulas originais byte a byte.
Proposta: trocar por teste de equivalência em Node (fórmula original e nova
com os mesmos dados simulados, incluindo treino, carro desconectado, P1).

**Fase 4 — Desfoques (só se a Fase 0 mostrar custo).** Brilhos viram PNGs
pré-renderizados, um por cor, alternando `Visible`; as camadas de shift (8
itens com blur) viram 1 imagem cada.

**Fase 5 — Ajustes menores.** Agrupar pílula+rótulo dos avisos num layer com
um `Visible`; balanço numa fórmula só (NCalc tem `Atan`; suavização pela
cadência); flash do bias a ~30 Hz; ligar `UseStrictJSIsolation` (efeito em
desempenho não confirmado).

**Fase 6 — Lado do SimHub (o usuário testa).** Modo de renderização HTML do
dash; limitar FPS do iRacing (GPU < 90–95%); G-Sync/FreeSync só em tela
cheia; plano de energia de alto desempenho; desligar plugins não usados.

**Ordem:** 0 → 1 → 2 (rápidas, quase sem risco); 3 e 4 conforme a medição.

## Relação com os estados laterais

O plano de estados (`docs/estados.md`) adiciona fórmulas. Ele já foi escrito
para nascer com cadência (gatilhos a ~10 Hz, coletores a 1–2 Hz) e para
**esconder o gráfico** enquanto um estado ocupa o lugar dele — o que, de
quebra, alivia o item mais caro. Se a otimização vier antes, a regra de
cadência da Fase 1 deve ser a mesma usada pelos estados.

## Como validar qualquer fase

```bash
python3 build.py && python3 tools/formula_audit.py
python3 tools/preview_modes.py && cp tools/preview_page.html build/modes/index.html
```

O `build.py` já gera `build/iRacing_Dashboard_00.simhubdash` junto com a pasta —
não precisa zipar à mão.

O preview é estático (não avalia fórmulas): ganho de desempenho só se mede no
SimHub do usuário.

## Fontes

- [Dash Studio — Bindings](https://github.com/SHWotever/SimHub/wiki/Dash-Studio---Bindings)
- [DashStudio performance](https://github.com/SHWotever/SimHub/wiki/DashStudio-performance)
- [Javascript Formula Engine](https://github.com/SHWotever/SimHub/wiki/Javascript-Formula-Engine)
- [OpenDash — formato e loop de bindings](https://github.com/xorob0/OpenDash/blob/main/docs/research/simhub-dash-format.md)
- [SimHub 6.4.2](https://www.simhubdash.com/simhub-6-4-2/)
- [Lag on dashboards](https://www.simhubdash.com/community-2/simhub-support/lag-on-dashboards/)
