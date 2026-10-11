# Plano — estados temporários dos componentes laterais

Fonte das regras: `Estados.md` enviado pelo usuário em 2026-10-11 (reproduzido
no fim deste arquivo). Quatro estados que **substituem por alguns segundos** um
componente existente:

| Estado | Ocupa o lugar de | Gatilho | Duração |
|---|---|---|---|
| **Damage** | gráfico de telemetria (esquerda, 472×194) | botão "Damage Report"; dano novo | 3 s (botão); dano novo: a definir (proposta 5 s) |
| **Lap Review** | gráfico de telemetria | volta completada fora do pit, sessão de corrida | até 5 s na volta nova |
| **Weather** | gráfico de telemetria | saída dos boxes; entrar no grid da corrida | 10 s |
| **New Lap Info** | setores (direita, rodapé, 472×100) | volta nova | 5 s |

Nada muda no layout fixo: cada estado cabe exatamente na caixa que substitui,
com o mesmo tile, a mesma tipografia (rótulo em caixa alta cinza, número em
Arame Mono) e as mesmas regras de leitura a distância já usadas nos setores.

---

## 1. O que os dados permitem (pesquisa)

Isso é o que mais condiciona o plano. Resumo do que o iRacing/SimHub expõem:

| Pedido | Disponível? | De onde |
|---|---|---|
| Dano por peça (asa, laterais, suspensão…) | **Não.** O widget Car Damage do iRacing (2026 S3/S4) é UI; as release notes não adicionam variável de SDK | release notes 2026 S4 e S4 P1 |
| Dano novo / gravidade geral | Sim, indireto: `PitRepairLeft` (reparo obrigatório, s) e `PitOptRepairLeft` (opcional, s) crescem quando há dano | SDK |
| Motor (temperatura, pressão de óleo/combustível) | Sim: bitfield `EngineWarnings` | SDK |
| Botão "Damage Report" | Sim, se for botão de volante/joystick: o SimHub lê o mesmo botão (`InputStatus.JoystickPlugin.<device>_B<n>`). Tecla de teclado não | fórum SimHub |
| Previsão do tempo por intervalos | **Não.** iRacing não publica previsão no SDK/API | resposta do iRacing citada no fórum SimHub |
| Clima atual | Sim: `AirTemp`, `TrackTempCrew`, `WindVel`, `WindDir`, `RelativeHumidity`, `Skies`, `Precipitation`, `TrackWetness`, `WeatherDeclaredWet`; `YawNorth` para o vento relativo ao carro | SDK |
| Chance de chuva | Não como previsão. Talvez `WeekendInfo.TrackPrecipitation` (valor de início de sessão) — conferir no dump | SDK (YAML) |
| Tempos dos outros | Sim: leaderboard do IRacingExtraProperties (`..._LastLapTime`, `..._BestLapTime`), `LapsSinceLastPit` por piloto | plugin já usado |
| Média do stint | **Não existe pronta.** Tem que ser acumulada volta a volta (ver §2.3) | — |
| FPS | Sim, do próprio iRacing: `FrameRate` (sem precisar de RTSS) | SDK |
| Ping / qualidade de conexão | Sim: `ChanLatency`/`ChanAvgLatency` (s) e `ChanQuality`/`ChanPartnerQuality` | SDK |
| Temperatura de CPU/GPU | Só com provedor externo ligado no SimHub (Settings → System Infos): **HWiNFO (Pro, shared memory)**, **Aida64** ou **Afterburner**. O sensor embutido foi removido no SimHub 8.3 | wiki "System informations" |

Consequências diretas:

- **Weather** vira "condição atual + tendência", que é o fallback que o
  próprio documento de regras prevê.
- **Damage** não pode pintar peça por peça com dado real. Proposta em §3.1.
- **New Lap Info** depende de o usuário ter um provedor de temperatura ligado.

## 2. Arquitetura comum (Fase A)

### 2.1 Máquina de estados sem estado compartilhado

No SimHub cada fórmula JS tem o próprio `root` e não existe estado global
confiável entre fórmulas. Por isso:

- A lógica de gatilho fica num **prelúdio JS gerado em Python**
  (`src/dash/states.py`, mesmo padrão do `PRELUDE` de `sectors.py`), com uma
  função `state()` que devolve `'damage' | 'weather' | 'review' | null`.
- Cada consumidor (o `Visible` de cada estado e o `Visible` do gráfico) é
  `PRELUDE + "return state() == 'weather';"`. Como todos leem as mesmas
  propriedades com o mesmo relógio (`Date.now()`), chegam à mesma resposta.
- Os timers são por **tempo de parede** (`Date.now()` guardado em `root` na
  borda do gatilho), não por contagem de quadros, para não depender da
  cadência.
- `Visible` de item escondido continua sendo avaliado, então esses
  formulários enxergam as bordas mesmo com o estado desligado. Cadência:
  `RenderingSkip 5` (~10 Hz). Risco aceito: no pior caso, 100 ms entre o
  gráfico sumir e o estado aparecer.

### 2.2 Prioridade (esquerda)

Proposta: **Damage > Weather > Lap Review**, com o botão "Damage Report"
sempre vencendo. Um estado de prioridade maior interrompe o atual; quando ele
termina, o interrompido volta se a janela dele ainda não acabou. Na prática
os conflitos são raros: volta completada pelo pit não abre Lap Review, e a
saída do pit (Weather) acontece fora da linha de chegada.

A direita tem um estado só, então não há prioridade.

### 2.3 Coletores (dados que precisam de histórico)

Filhos de layer escondida não são avaliados, então um estado escondido não
consegue acumular histórico (média do stint, tendência do clima). Solução:
os itens que precisam de histórico ficam **fora** do layer do estado, sempre
visíveis, e o próprio texto se autodesliga:

```js
// coleta sempre; só mostra quando o estado está ativo
acumula(root);
return state() == 'review' ? formatado : '';
```

Rodam a 1–2 Hz (`RenderingSkip 29`/`59`), então o custo é baixo. O fundo do
estado (tile) e os textos sem histórico ficam dentro do layer normal.

### 2.4 Esconder o gráfico

O `Visible` do widget de telemetria passa a ser `state() == null`. Enquanto um
estado estiver na tela o gráfico **não é renderizado** — economiza o item mais
caro do dash, em vez de só cobri-lo.

### 2.5 Configuração em um lugar só

`src/dash/states.py` concentra as constantes que dependem da instalação do
usuário:

```python
DAMAGE_BUTTON = "InputStatus.JoystickPlugin.<device>_B<n>"   # o usuário informa
CPU_TEMP = "<propriedade do provedor>"                       # idem
GPU_TEMP = "<propriedade do provedor>"
DURATION = {"damage_button": 3, "damage_new": 5, "review": 5,
            "weather": 10, "newlap": 5}
```

### 2.6 Ferramental

- `tools/preview_modes.py`: uma aba nova por estado (Damage, Lap Review,
  Weather, New Lap Info), mais uma com Damage sobre Lap Review para conferir a
  prioridade. A página publicada passa de 16 para 21 abas.
- Testes do prelúdio em Node (como foi feito com os setores): bordas de
  gatilho, timers, prioridade, preempção e retomada, sessão que não é corrida,
  volta pelo pit.
- Canvas: uma prancheta por estado, importando `Main` com uma prop `state`,
  **antes** de escrever o código de cada estado — o design é aprovado no
  canvas e só então portado.

## 3. Os estados

### 3.1 Damage (esquerda) — o mais incerto

**Gatilhos**
1. Botão: borda de subida em `DAMAGE_BUTTON` → 3 s.
2. Dano novo: `PitRepairLeft + PitOptRepairLeft` aumentou em relação à última
   leitura (com tolerância, porque o valor desce durante o reparo no pit) →
   duração a definir (proposta 5 s). Também dispara se um bit novo acender em
   `EngineWarnings`.

**Conteúdo** — duas opções, a decidir:

- **A. Só o que é real (recomendada para começar).** Desenho de cima do
  fórmula montado com retângulos arredondados do próprio SimHub (asa
  dianteira, bico, cockpit, laterais, assoalho, asa traseira, 4 rodas), todo
  pintado pela gravidade geral (verde/amarelo/laranja/vermelho, escala pelo
  tempo de reparo). Ao lado: `REPAIR` obrigatório e `OPT` opcional em
  segundos, e ícones de motor (água, óleo, combustível) acesos pelo
  `EngineWarnings`. Honesto e barato.
- **B. Estimativa por zona.** Igual à A, mas o aumento de reparo é atribuído
  à zona do impacto, estimada pelo pico de aceleração (`LongAccel`,
  `LatAccel`) no meio segundo anterior: frente, traseira, lado esquerdo, lado
  direito. Precisa de coletor a 30 Hz e vai errar em impactos combinados.
  Roda/suspensão continua sem dado.

Retângulos em vez de PNG: a cor de cada zona muda por fórmula sem precisar de
4 imagens por zona.

### 3.2 Lap Review (esquerda)

**Gatilho:** volta nova (`LapCurrentLapTime < 5`), sessão atual do tipo
`Race` (mesmo lookup de `right._SESSION_TYPE_LOOKUP`), e a volta **não** foi
completada no pit lane (`OnPitRoad` falso na borda da troca de volta, guardado
em `root`).

**Layout em 472×194**, por prioridade visual:

- **P1, faixa de cima (~70 px):** `LAST` grande com o delta para a minha
  melhor volta ao lado (verde/vermelho, mesmo `fmtDelta` dos setores), `STINT
  AVG` e `STINT LAPS`.
- **P2, tabela de 6 linhas (~20 px cada, texto ~16 px, a mesma escala do
  leaderboard):** 3 à frente, 3 atrás. Colunas: posição, nome curto, última
  volta, delta para a **minha** melhor volta, média do stint.

**Dados**

- Meus: `LastLapTime`, `BestLapTime`; voltas do stint pela troca de
  `OnPitRoad` (ou `LapsSinceLastPit` do jogador, se existir no plugin).
- Média do stint (minha e dos 6): coletor (§2.3) que, a cada troca de volta
  de cada carro, soma a última volta e zera ao detectar pit. Volta de saída do
  pit e volta com pit ficam fora da média.
- "Na frente/atrás": proposta **por posição na classe** (mesma fonte do
  leaderboard), não por posição na pista. A decidir.
- Valores nulos ou zero viram `N/A`, como nos setores.

### 3.3 Weather (esquerda)

**Gatilhos:** borda `OnPitRoad` verdadeiro → falso (saída dos boxes); borda de
entrada no carro numa sessão `Race` (`IsOnTrack` falso → verdadeiro, ou
mudança de `SessionState` para o grid) → 10 s.

**Layout em 472×194:** ícone grande à esquerda (céu × chuva × dia/noite) e uma
grade com AIR, TRACK, WIND (velocidade + seta **relativa ao carro**:
`WindDir − YawNorth`), HUMIDITY, TRACK STATE (`TrackWetness` em texto: DRY,
DAMP, WET…; mais o grip que já está no rodapé) e RAIN (intensidade atual; a
chance só se o dump mostrar). Ao lado de cada número, uma seta de tendência ↑
↓ → com cor.

**Tendência:** coletor a 1 Hz guardando uma janela dos últimos ~10 min;
tendência = valor atual contra o de 10 min atrás, com zona morta para não
oscilar. Logo após entrar na sessão não há janela: mostra `→`.

**Ícones:** um conjunto pequeno de PNGs (sol, lua, poucas nuvens, nublado,
encoberto, chuva fraca, chuva forte), desenhados em SVG e rasterizados uma
vez com o Chromium do ambiente, versionados em `assets/` como as máscaras dos
pentes. Visibilidade por fórmula, só um aceso.

### 3.4 New Lap Info (direita)

**Gatilho:** volta nova (`LapCurrentLapTime < 5`), sem condição de sessão.
Fórmula sem estado (NCalc), a mais barata de todas.

**Layout em 472×100:** uma linha de 5 células no padrão dos rodapés (rótulo em
cima, número embaixo, filetes entre células): `FPS`, `PING` (ms), `NET`
(qualidade em %), `CPU °`, `GPU °`. Cor por faixa (verde/âmbar/vermelho), com
limites em constantes. Offline, PING e NET viram `N/A`.

**Ressalva:** os setores acabam de ganhar o `LAST` justamente nesse momento, e
o New Lap Info os cobre por 5 s. Em corrida, o Lap Review mostra a última
volta do lado esquerdo, então a informação não se perde; em treino, se perde
por 5 s.

## 4. Fases e ordem

| Fase | Entrega | Depende de |
|---|---|---|
| **A. Fundação** | `states.py` (prelúdio, prioridade, durações), gráfico com `Visible`, testes em Node, abas no preview | — |
| **B. New Lap Info** | prancheta no canvas → código → preview → `.simhubdash` | nomes das propriedades de temperatura |
| **C. Lap Review** | idem, com coletores de stint | dump do IRacingExtraProperties |
| **D. Weather** | idem, com ícones e coletor de tendência | conferir `RelativeHumidity`, `TrackWetness`, `Skies`, `YawNorth` no dump |
| **E. Damage** | idem, opção A; B só se pedida | nome do botão; conferir `PitRepairLeft`/`PitOptRepairLeft` andando com dano |

B primeiro porque é o mais simples e certo (prova a fundação na tela); E por
último porque é o que mais depende de validação no SimHub.

Cada fase termina como as anteriores: `build.py` → `formula_audit.py` (nada
some) → preview publicado → `.simhubdash` para testar.

## 5. O que preciso do usuário

1. **Nome do botão** "Damage Report": no SimHub, Available properties, buscar
   `JoystickPlugin` e apertar o botão — o que mudar de 0 para 1 é o nome.
2. **Temperaturas:** qual provedor está ligado (HWiNFO Pro, Aida64 ou
   Afterburner) e o nome das propriedades de temperatura de CPU e GPU.
3. **`RSC.iRacingExtraProperties.txt`** (pasta do SimHub), para confirmar
   `LapsSinceLastPit` e os campos de última volta por piloto.
4. Do `SampleTelemetry.json` já enviado antes: confirmar `PitRepairLeft`,
   `PitOptRepairLeft`, `EngineWarnings`, `RelativeHumidity`, `TrackWetness`,
   `Skies`, `YawNorth`, `FrameRate`, `ChanLatency`, `ChanQuality`, e como os
   arrays `CarIdx*` aparecem.

## 6. Decisões em aberto

1. Prioridade da esquerda: **Damage > Weather > Lap Review** (proposta).
2. Duração do Damage por dano novo: **5 s** (proposta).
3. "3 à frente / 3 atrás" no Lap Review: **por posição na classe** (proposta)
   ou por posição na pista.
4. Damage: **opção A** (proposta) ou B.
5. Lado direito: o documento de regras diz "componente de timing do lado
   direito inferior" (os setores), mas a mensagem fala em "relativo,
   standings". Este plano segue o documento: New Lap Info cobre os setores e
   o relative/standings não muda.

## Fontes

- [iRacing 2026 S4 — release notes (Car Damage widget)](https://support.iracing.com/support/solutions/articles/31000179517-2026-season-4-initial-release-notes-2026-09-09-01-)
- [iRacing 2026 S4 Patch 1 — widget para todos os carros](https://support.iracing.com/support/solutions/articles/31000179767-2026-season-4-patch-1-release-notes-2026-10-01-01-)
- [SDK — índice de variáveis de telemetria](https://sajax.github.io/irsdkdocs/telemetry/)
- [Fórum SimHub — previsão não publicada no SDK](https://www.simhubdash.com/community-2/simhub-support/iracing-rain-update-more-details-and-black-box-info/)
- [SimHub wiki — System informations (HWiNFO/Aida64/Afterburner)](https://github.com/SHWotever/SimHub/wiki/System-informations)
- [SimHub wiki — Javascript Formula Engine (root, isolamento)](https://github.com/SHWotever/SimHub/wiki/Javascript-Formula-Engine)
- [Fórum SimHub — botão de joystick como propriedade](https://www.simhubdash.com/community-2/simhub-support/manually-activate-fans-fan-hotkey-test-fans-with-a-button/)
- [Fórum SimHub — `LapsSinceLastPit` no IRacingExtraProperties](https://www.simhubdash.com/community-2/dashboard-templates/romainrobs-collection/paged/39/)

---

## Anexo — regras originais (Estados.md)

**Damage.** O iRacing lançou um componente de Damage que mostra o desenho de
um carro de fórmula e pinta de vermelho, amarelo ou verde a parte com dano,
do mais grave ao mais leve. Aparece (1) por 3 s ao apertar o botão "Damage
Report" do iRacing e (2) toda vez que o carro tiver um dano novo. Substitui o
componente da telemetria.

**Lap Review.** Toda volta completada, sem ser pelo pitlane, em sessão do tipo
race. Visível por até 5 s depois de abrir a volta nova. P1: minha última volta
e delta para minha melhor; média do stint atual; voltas do stint. P2: última
volta e delta para minha melhor volta dos 3 pilotos à frente e dos 3 atrás;
média do stint atual deles. Substitui o componente da telemetria.

**Weather.** Ao sair dos boxes ou apertar "Race" para ir ao grid, por 10 s.
Previsão por intervalo se houver o dado; se não, atual e tendência. Ar,
pista, vento, direção do vento em relação à pista, estado do asfalto,
umidade, chance de chuva, ícone da condição. Substitui o componente da
telemetria.

**New Lap Info.** Toda volta nova, por 5 s. FPS, ping, qualidade de conexão,
temperatura da CPU e da GPU, organizados visualmente. Substitui o componente
de timing do lado direito inferior.
