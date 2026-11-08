# Handoff — dash minimal (`SF23_Minimal`)

Status em 2026-11-08 (commit `09283c8`): **gerado, testado no harness e no
preview, ainda não validado no SimHub.** O usuário recebeu o
`.simhubdash` para testar. Este documento serve para retomar numa sessão
nova sem reler a conversa. O resumo curto fica em `ESTADO.md`; aqui estão
o porquê das decisões e o que pode dar errado.

## O que é

Um segundo dash, gerado junto com o principal pelo `build.py`. É uma cápsula
de 900×240 com o box de telemetria pendurado embaixo. O dash tem 900×480 e
fundo transparente, para uso como overlay. Ele vem do canvas de design
<https://claude.ai/artifact/S9sQwrTAbpMiBK7AwPpTP8> e segue três regras:
tudo cabe na cápsula, nenhum desfoque e fórmulas o mais leves possível
(NCalc com constante onde der).

| Arquivo (`src/dash/minimal/`) | O quê |
|---|---|
| `__init__.py` | `items()`, shell e tela transparentes, `NAME`/`DASH_ID` |
| `base.py` | Medidas (`CAPSULE`, `TRACE_BOX`, centros dos arcos), `rect`, `group`, cadências `SKIP_SLOW = 9` / `SKIP_NAMES = 29` |
| `leds.py` | 9 LEDs por lado em arco, limiares do iRacing por carro, LED de status (bandeira/limiter) |
| `capsule.py` | Fundo, pedais do centro para fora, marcha, km/h, rpm, OTS, LAPS / TO GO / STINT |
| `context.py` | Painel por cima do box: pit e revisão da volta |
| `alerts.py` | Área de alerta com prioridade, no lugar do cabeçalho do OTS |
| `relative.py` | Mini relativo (2 à frente, eu, 2 atrás), dados do IRacingExtraProperties |
| `trace.py` | Box de telemetria e gravador da volta de referência |

## Como gerar, testar e ver

```bash
python3 build.py                  # gera build/SF23_Minimal (e o principal)
python3 tools/check_minimal.py    # harness do gravador da referência (Node)
```

O `.simhubdash` é um zip da pasta, que fica no `build/`, ignorado pelo git:

```bash
rm -f build/SF23_Minimal.simhubdash && (cd build && zip -qr SF23_Minimal.simhubdash SF23_Minimal)
```

Preview em imagem: gerar o HTML, trocar o fundo do `body` e fotografar.
O fundo é transparente, então o `sed` põe `#141414`; um gradiente claro
serve para conferir a opacidade.

```bash
python3 tools/preview.py build/SF23_Minimal -n SF23_Minimal -b -c show -o build/preview_minimal.html
```

```bash
/opt/pw-browsers/chromium --headless --disable-gpu --no-sandbox --hide-scrollbars --force-device-scale-factor=2 --window-size=900,500 --screenshot=build/preview_minimal.png "file:///home/user/simhubeleza/build/preview_minimal.html"
```

O preview desenha os `ChartItem` de pedal com uma volta simulada
(`_pedals()` em `tools/preview.py`). Os gráficos com nome começando em
"Ref" saem um pouco atrasados e mais baixos para não se sobreporem. Não é
telemetria real, só serve para ver o layout. O `formula_audit.py` cobre só
o dash principal.

## Box de telemetria (`trace.py`)

**O que mostra:** uma janela só, com os últimos 15 s (`WINDOW_S`) e o agora
na borda direita. Meu acelerador e freio vão em linha fina. A referência
vai numa faixa larga e translúcida por baixo e mostra o que ela fazia **nos mesmos pontos da pista** por
onde passei nesses 15 s, não nos mesmos segundos. A legenda (YOU / REF) e o
tempo da referência (`REF LAP 1:36.1`, ou `--` sem referência) ficam em
cima; o eixo `-15 s … 0` fica embaixo. Duas bolinhas na linha do agora
mostram o valor atual.

**Histórico de pedidos:** primeiro havia duas janelas, de -10 s a +10 s, com
"o que vem" da referência à frente. O usuário trocou para uma janela só,
com a referência tracejada, e depois aumentou o histórico de 10 s para 15 s.
As chaves `mini_ahead*` e a janela da frente foram removidas. Na crítica
de design de 2026-11-08, o tracejado virou a faixa larga (ver abaixo).

**Delta (`delta_readout()`):** na linha da legenda, ao centro, o delta da
volta atual contra a referência: número com sinal (`-0.23`, o mesmo
`DELTA_TEXT` do dash principal) e uma barra de 200 px que sai do zero —
para a esquerda ganhando tempo, para a direita perdendo, escala de ±0,5 s
(`DELTA_FULL_S`), construída como o trilho fino do dash principal. A fonte
é `[DataCorePlugin.GameData.DeltaToSessionBest]`, que mede contra a melhor
volta da sessão, a mesma que o `RECORDER` guarda como referência: nada é
gravado a mais. O grupo só aparece com referência (`REF_READY`). Sem matiz
de propósito (verde e vermelho são dos pedais): o lado e o sinal dizem
ganho ou perda; `DELTA_GAIN`/`DELTA_LOSS` trocam as cores. **A conferir no
SimHub:** se o gauge com `Maximum` negativo enche para a direita no
minimal como no dash principal.

**Traço de delta (`delta_strip()`):** tira de 34 px na base do box,
abaixo dos pedais (que ficaram com 120 px de altura em vez de 176), no mesmo
eixo de 15 s. Um `ChartItem` com escala fixa de ±1 s (`TRACE_DELTA_S`,
`Minimum`/`Maximum` simétricos, valor limitado por `Max/Min` na fórmula),
zero no meio e três filetes como na grade dos pedais. **Sobe quando estou
mais rápido** (a fórmula inverte o sinal do `DeltaToSessionBest`) e desce
quando perco tempo, neutro como a barra do cabeçalho. Some junto com a
referência. **A conferir no SimHub:** se o `ChartItem` aceita escala
simétrica com valores negativos (se não, a saída é somar 1 ao valor e usar
`Minimum 0`, `Maximum 2`). O preview desenha um delta simulado (o nome do
gráfico tem "Delta").

### Como os gráficos funcionam

- Tudo é `ChartItem`: ele desenha o histórico de um valor com o ponto mais
  novo na borda direita. Com `RenderingSkip 1`, amostra a ~30/s (medido no
  dash principal), então `PointsCount = WINDOW_S × SAMPLES_PER_S = 450`.
  Se no SimHub a linha correr rápido ou devagar demais para 15 s, o ajuste
  é em `SAMPLES_PER_S`.
- Meus pedais vêm de `[Throttle]` e `[Brake]` em NCalc. Os da referência
  vêm de `getsharedvalueordefault('sf23dash', 'mini_thr'|'mini_brk')`.
- **Referência em faixa:** `LineTickness` 5 (`REF_THICKNESS`) com a cor
  do pedal a 40% (`REF_THROTTLE`/`REF_BRAKE` em `src/simhub/theme.py`),
  por baixo das minhas linhas de 2 px. Quando eu acompanho a referência, a
  minha linha corre dentro da faixa e as duas continuam legíveis. No
  tracejado anterior, a referência tinha a mesma espessura e cor a 85%
  (1,3:1 contra a linha cheia) e sumia justamente nesse caso. A legenda
  tem uma amostra da faixa no cinza a 40% (`REF_SWATCH`).
- **Base escondida:** pedal solto desenhava uma linha permanente na base,
  o freio vermelho durante a volta inteira. O fundo do box
  (`TRACE_BOX_FILL`, 92%) foi cortado em duas peças da mesma cor em
  `BASE_TOP` (3 px acima da base): o corpo vai por baixo dos gráficos e a
  tira da base (`Fill Base`) vai por cima. Valor abaixo de ~2% some, e a
  linha de 0% da grade, neutra, vem por cima da tira. As bolinhas do agora
  também somem abaixo de 2% (`DOT_MIN`). Pela tira passa 8% da linha de
  baixo, então sobra um vestígio bem fraco da cor.
- Ordem das camadas em `layer()`: corpo do fundo → referência → meus
  gráficos → tira da base → borda → grade → linha do agora → bolinhas →
  textos.
- Alternativas descartadas para o tracejado anterior: máscara opaca,
  xadrez, valor fora da escala e vários gráficos pequenos. O tracejado em
  colunas (6/4 px) foi substituído pela faixa.

### Gravador da referência (`RECORDER`)

Uma fórmula JS só, ligada ao `Visible` do retângulo "Now" (a linha do
agora). Roda com `RenderingSkip 0`, a cada quadro, e sempre devolve `true`.
**Ela não pode ficar dentro de algo que seja escondido**: com o retângulo
"Now" invisível, a gravação para. O estado fica em `root`.

- Grava acelerador e freio em `BINS = 400` trechos do `LapDistPct`
  (~13 m numa pista de 5 km). A volta só vale com 97% dos trechos gravados
  (`COVERAGE`).
- Um salto real de posição (reset, reboque) invalida a volta. A virada do
  `LapDistPct` um quadro antes ou depois da volta não invalida.
- **A referência é a melhor volta da sessão**, a mesma do `BestLapTime`,
  então volta invalida não conta. Ao virar a volta, a que acabou fica
  **pendente até a próxima virada**. O `BestLapTime` pode chegar segundos
  depois do `LastLapTime`, e julgar a volta num quadro só fazia a
  referência nunca aparecer. Esse foi o bug original.
- O tempo oficial da volta pendente é o `LastLapTime` quando ele muda desde
  a virada. Com o IRacingExtraProperties
  (`iRacing_Player_CurrentLapIsClean`, lido depois de `CLEAN_GRACE_S = 1 s`
  da virada), a volta limpa vale pelo próprio tempo, sem esperar o
  `BestLapTime`.
- A primeira volta depois de abrir o dash nunca vale, porque não foi
  gravada inteira. A melhor volta feita antes de o dash abrir não tem
  pedais, então a referência só aparece depois da próxima volta limpa ou
  melhor.
- Reset para os boxes (a volta conta para trás) perde só a volta em curso.
  `SessionNum` novo, ou `BestLapTime` zerado, apaga a referência.
- Ele publica `mini_ok`, `mini_best`, `mini_thr` e `mini_brk` no
  armazenamento `sf23dash`, o mesmo do dash principal; o prefixo `mini_`
  evita colisão. Os valores são interpolados entre os centros dos trechos,
  para o gráfico não virar escada. Sem `setsharedvalue` (`HAS_SHARED`
  falso), não há referência: a camada fica escondida e o rótulo mostra
  `--`.
- **Mini-setores:** a volta é dividida em 10 trechos iguais do `LapDistPct`
  (`SECTORS`). O gravador guarda o tempo em que cruzou cada fronteira,
  interpolado entre os dois quadros (`c.s`), e o tempo total da volta
  (`c.tot`, na virada). Ao fechar um setor, publica o delta dele contra a
  referência em `mini_sd0`…`mini_sd9` (segundos; 99 = sem dado). O setor 0 é
  o primeiro a fechar numa volta nova e apaga o resultado da anterior, então
  o resultado da volta que acabou fica na tela até lá; o último setor fecha
  na virada. Reset, salto de posição, sessão nova e fim da referência
  apagam tudo. O `sdone` não mede a volta contra ela mesma. Na tela
  (`sectors()`, linha do eixo, entre `-15 s` e `0`): um bloco por setor,
  claro = ganhei, laranja = perdi, cinza = igual (±`SECTOR_EQUAL_S`, 0,02 s),
  apagado = sem dado. Precisão: o início da volta é o quadro em que o `Lap`
  mudou, então o setor 0 e o último carregam o erro de um quadro (~16 ms).
- O harness `tools/check_minimal.py` roda a fórmula quadro a quadro sobre
  voltas simuladas. A sequência básica roda em 4 variantes: normal,
  `BestLapTime` 5 s atrasado, com validade, e com validade e atraso. Há
  ainda testes de reset, sessão nova, leitura interpolada no ponto atual e
  dos mini-setores (voltas com duração por setor).
  O código antigo falha nas variantes com atraso. **Mudou o `RECORDER`?
  Rode o harness.**

## LEDs de RPM (`leds.py`)

Até o SLLastRPM, cada LED acende na cor do seu passo: um azul que clareia
para fora, interpolado entre os quatro pontos de `RPM_RAMP` (a rampa do
dash principal; verde e vermelho ficam para os pedais, e o roxo é o único
sinal de troca). Acima do SLBlinkRPM, o mesmo critério do brilho roxo da marcha
no dash principal (`center.GLOW_COLOR`), a rampa sai inteira e os 18 LEDs
piscam em roxo, juntos, alternando entre roxo e apagado.

- Antes, cada LED roxo tinha o próprio `BlinkEnabled`: cada um com o seu
  relógio, e na fase apagada a rampa aparecia por baixo, então o pisca
  alternava entre roxo e as cores da rampa.
- Agora uma camada só (`Shift`) liga e desliga os 18, com
  `SHIFT_PHASE`: o `SessionTime` em fatias de `BLINK_MS` (180 ms: ~2,8
  flashes por segundo, abaixo dos 3 do critério 2.3.1 da WCAG; eram 120 ms,
  ~4,2), aceso
  nas pares. A rampa tem `Visible` falso na troca (`SHIFTING`).
- O LED de status também pisca em roxo na troca, mesmo com bandeira. O
  pit limiter tem prioridade: com ele ligado não há pisca de troca.
- **Limitador em quatro estados** (`leds.PIT_ALERT`, `LIMITER_LEFT_ON`):
  o LED de status cruza o limitador com estar no pit lane
  (`GameRawData.Telemetry.OnPitRoad`), e o pisca passa a significar erro:

  | Limitador | Pit lane | LED de status |
  |---|---|---|
  | ligado | dentro | ciano fixo (certo) |
  | desligado | dentro, andando (> 10 km/h) | laranja piscando |
  | ligado | dentro, acima do limite (`DahlDesign.PitSpeeding`) | laranja piscando |
  | ligado | fora | ciano piscando (esquecido ligado) |

  Parado no box sem limitador não é erro. Antes o ciano piscava sempre que
  o limitador estava ligado. A tabela-verdade foi conferida em Python; no
  SimHub falta ver se o `OnPitRoad` chega como booleano no `isnull(...)`.
- A conferir no SimHub: se o `Floor(...) % 2` do NCalc funciona e se o
  `SessionTime` avança a cada quadro. Com o jogo pausado, o relógio para
  e o roxo fica parado aceso ou apagado.

## Pedais, km/h e rpm (`capsule.py`)

Ajustes vindos da crítica de design de 2026-11-08:

- **Número dos pedais** em Arame Mono 30 (o tamanho dos números
  secundários), no cinza `TEXT`, não mais na cor do pedal: a barra já diz
  a cor e o lado, e o número em 34 px saturado competia com a marcha.
  Some solto (< 0,5%) **e no fundo** (≥ 99,5%): antes o fundo virava
  "00", que lia como pedal solto.
- **RPM em milhares** com uma casa (`7.7`, rótulo `RPM ×1000`). Antes era
  o RPM dividido por 10 (`770`) com o rótulo `RPM`. Conferir no SimHub se
  a Funnel Sans tem o `×`.
- **km/h e rpm na mesma altura** (`SPEED.y`); antes o rpm ficava 3 px
  abaixo.
- **Rótulos em inglês**: `YOU` (era `VOCÊ`) e `REF LAP` (era `REF. LAP`).
- **Escala de tipos** reduzida a cinco tamanhos: marcha 176, primário 44
  (km/h, rpm), secundário 30 (pedais, OTS, voltas), linha 16 (relativo e
  `OTS READY`, que era 17) e rótulo 11 (inclusive os do box de
  telemetria, que eram 10).
- **Barras** (pedais e OTS) com o mesmo raio de canto, `BAR_RADIUS = 3`
  (o OTS usava 2).
- **Grade do box** (`TRACE_GRID`) de 7% para 15% de alpha: era 1,16:1,
  invisível; agora é 1,5:1, discreta mas presente. A linha de 0% serve de
  base neutra por cima da tira que esconde o pedal solto.

## Bloco de voltas (`capsule.laps()`)

Três colunas abaixo do OTS, na largura da barra dele (522–727): LAPS na
borda esquerda, TO GO no centro e STINT na borda direita. Número em
Arame Mono 30 em cima, rótulo em Funnel Sans 11 embaixo, como km/h e rpm.

- **LAPS:** voltas completas (`CompletedLaps`).
- **TO GO:** voltas que faltam completar: `TotalLaps - CompletedLaps`
  (mínimo 0). Sem total de voltas (corrida por tempo, treino): `N/A`. A
  estimativa por tempo (`iRacing_LapsRemaining`) foi descartada a pedido.
- **STINT:** voltas completas desde a última saída dos boxes
  (`iRacing_Player_LapsSinceLastPit`); sem o plugin, `--`.

Antes era VOLTA (volta atual), TOTAL e STINT (+1, contando a volta em
curso), com rótulo em cima e colunas centralizadas, fora do alinhamento
do OTS.

## Área de alerta (`alerts.py`)

Um slot só para avisar: o cabeçalho do OTS (`OTS READY`, 16 px). Com um
aviso ativo ele toma o lugar do cabeçalho (os segundos e a barra do OTS
ficam), e sem aviso o OTS volta. Ganha o de maior prioridade, em duas ou
três palavras:

1. `RED FLAG`, `BLACK FLAG`, `REPAIR` (meatball)
2. pit: `LIMITER` (andando sem limitador), `SLOW DOWN` (acima do limite no
   pit), `LIMITER ON` (esquecido ligado fora do pit)
3. bandeiras de pista: `YELLOW`, `BLUE FLAG`, `SLOW CAR`
4. combustível: `FUEL SHORT` (não chega ao fim), `LOW FUEL` (< 2 voltas)
5. `DEBRIS`, `CHECKERED`, `LAST LAP`
6. informação: `BB 54.5` (o brake bias mudou nos últimos 2 s)

Tudo NCalc a ~6 Hz; o grupo do aviso nasce escondido e só avalia a cadeia
quando há aviso (`ACTIVE`). Nada pisca: o aviso é condicional e some quando
a condição acaba. O LED de status (`leds.FLAGS`) pinta as mesmas bandeiras e
ganhou as que faltavam (vermelha, meatball, carro lento, pista suja,
quadriculada); `leds.COND_*` são as condições compartilhadas. As cores de
bandeira vêm de `theme.py`.

## Painel de contexto (`context.py`)

O box troca de conteúdo por estado: um painel opaco cobre o box por cima,
só quando há o que mostrar, e some sozinho (grupo escondido por padrão, a
~6 Hz):

- **Pit** (`OnPitRoad`): `PIT LANE`, o limite de velocidade em km/h
  (`TrackPitSpeedLimit`, "60.00 kph" do YAML) e o combustível a abastecer
  (`PitSvFuel`).
- **Volta** (5 s depois de fechar uma volta de corrida fora do pit:
  `SessionTypeName = 'Race'` e `isincreasing(5000, CompletedLaps)`): número
  e tempo da volta, delta contra a melhor (`BEST` se for a melhor; laranja
  se mais lenta) e os 10 mini-setores, que ainda guardam o resultado da
  volta que fechou (o setor 0 da próxima só fecha depois de ~9 s).

Pit tem prioridade. **O painel cobre o box e não o esconde**: o `RECORDER`
mora no `Visible` da linha "Now" e para de gravar se ela sumir. O fundo é
opaco (o do box é 92% e o traço apareceria fantasma). Não depende do dash
principal: sai de propriedades do SimHub, com um JS curto para formatar
tempo (`states.FORMAT`). Na última volta (falta 1) o TO GO mostra `LAST`.
Fora do que foi pedido, ficou de fora trocar o traço de delta por sessão
(esconder em corrida): hoje ele aparece sempre.

## Acabamento visual

- **Terceira camada de texto** (`MINI_UNIT`, #7E838A, ~5:1): rótulos e
  unidades de 11 px (KM/H, RPM ×1000, LAPS, TO GO, STINT, YOU, REF, eixo,
  SECTORS, DELTA) ficam abaixo dos valores (`TEXT`) e dos rótulos de linha
  (`TEXT_SECONDARY`). A marcha (branco) e os números mandam.
- **`N` da marcha** a 40% (`GEAR_NEUTRAL`), por binding de `TextColor` e
  `GearTextColor` com `[Gear] = 'N'`.
- **Filete de 1 px** (`capsule.highlight()`, `MINI_HIGHLIGHT`, branco a 12%)
  no trecho reto do topo da cápsula, no lugar de brilho.
- **Não feito:** espaçamento aberto nas unidades (o `TextItem` do SimHub não
  tem espaçamento entre letras) e "valores de marcador em opacidade
  reduzida" (o relatório não define quais).

## Brake bias e batalha

- **Brake bias:** `BB 54.5` em âmbar (`BIAS`) toma o lugar do cabeçalho do
  OTS por 2 s (`BIAS_SHOW_MS`) depois de cada ajuste, como o aviso de menor
  prioridade da área de alerta. A detecção usa `isincreasing`/`isdecreasing` do NCalc, as mesmas
  funções que o dash principal usa para piscar o bias: sem JS nem estado.
  Os números do OTS (`094`) e a barra continuam.
- **Batalha (`relative.py`):** carro a menos de 1 s (`BATTLE_S`) no mini
  relativo: o gap vai ao branco da marcha e aparece um traço de 2 px à
  esquerda do bloco. O limite de 1 s é escolha do projeto. Não há seta de
  tendência do gap: pediria estado em JS para quatro linhas, e nenhuma
  referência sustentou o custo.

## Combustível (`capsule.fuel()`)

Abaixo do bloco de voltas (que subiu de y 150 para 128 para abrir espaço),
na mesma largura: `FUEL` à esquerda, a margem à direita e uma barra fina
de 5 px embaixo, como um gráfico de bullet. Tudo NCalc, a ~6 Hz.

- **Barra:** `Fuel / MaxFuel`, cinza. Vira laranja quando o tanque não
  chega ao fim da corrida.
- **Marca** (traço claro de 2 px): o combustível que falta para a
  bandeira, `Max(TotalLaps - CompletedLaps - LapDistPct, 0) *
  Fuel_LitersPerLap`, como fração da capacidade. Só existe em corrida por
  voltas com consumo medido.
- **Texto:** em corrida por voltas, a margem com sinal em litros (`+1.4 L`:
  sobra; `-0.8 L`: falta). Sem total de voltas, as voltas que o tanque ainda
  dá (`Fuel_RemainingLaps`, `6.2 LAPS`). Sem consumo medido (antes da
  primeira volta), `--`.
- Assume litros (`Fuel` vem em `FuelUnit`; o dash principal faz o mesmo).

## O que conferir no SimHub, por ordem de risco

1. **A referência aparece?** Abrir o dash e dar duas voltas limpas: a
   primeira é descartada, e a segunda deve virar referência ao fechar, ou
   ao virar a seguinte se o `BestLapTime` atrasar. O rótulo deve mostrar o
   tempo dela. Se não aparecer, conferir se o SimHub tem o armazenamento
   compartilhado (o dash principal também usa) e se `LapDistPct`, `Lap` e
   `SessionTime` chegam pelo `GameRawData.Telemetry`.
2. **Velocidade da linha:** a janela deve cobrir 15 s. Se não cobrir,
   ajustar `SAMPLES_PER_S`.
3. **Faixa da referência e tira da base:** conferir se o SimHub desenha a
   linha de 5 px com alpha sem escurecer as junções, e se a tira da base
   não mostra uma emenda com o corpo do box (as duas a 92%).
4. **`Rotation` em `RectangleItem`:** os LEDs são pílulas giradas. O
   preview gira em torno do centro; se o SimHub girar em torno do canto ou
   ignorar a rotação, os arcos saem tortos.
5. **Bolinhas do agora:** elas se movem por binding de `Top`.
6. **LAPS / TO GO / STINT:** conferir se o STINT
   (`iRacing_Player_LapsSinceLastPit`, sem +1) zera na saída dos boxes e
   conta só voltas completas, e se o TO GO bate com o fim da corrida.
7. **Opacidade:** cápsula e box a 92%. Os 45% do canvas ficaram
   transparentes demais.
12. **Acabamento:** o `N` da marcha deve ficar esmaecido (se o `TextColor`
   do `GearText` não aceitar binding, ele fica branco) e o filete de topo
   deve aparecer.
11. **Painel de contexto:** no pit lane o painel deve cobrir o box e, ao
   sair, o gráfico voltar sem perder a gravação da referência; 5 s depois
   de fechar uma volta de corrida deve aparecer a revisão. Conferir
   `TrackPitSpeedLimit`, `PitSvFuel` e `SessionTypeName` e se `LAST`
   cabe na coluna do TO GO.
10. **Área de alerta:** com uma bandeira amarela, o `YELLOW` deve tomar o
   lugar do `OTS READY` e o LED de status ficar amarelo; conferir os nomes
   `SessionFlagsDetails.Isred/Isrepair/Isdebris` e se o aviso some ao fim
   da condição.
9. **Brake bias e batalha:** o `BB` deve aparecer por 2 s ao mexer no
   bias (se `isincreasing`/`isdecreasing` não reagirem a passos de 0,1,
   usar JS com valor anterior em `root`); o traço e o branco do gap devem
   aparecer com um carro a menos de 1 s.
8. **Combustível:** a marca deve ficar à direita do fim da barra quando
   falta combustível (barra laranja) e à esquerda quando sobra; conferir
   se `Fuel_LitersPerLap` já vem preenchido depois da primeira volta e se
   o SimHub aceita o binding de `Left` na marca.

## Ideias em aberto (não pedidas)

- Opção de referência = volta de outro piloto ou volta salva entre sessões.
  Hoje só vale volta gravada com o dash aberto, e nada é persistido.

