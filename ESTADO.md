# Estado do projeto

Retomada rápida para uma sessão nova. O plano completo está em
`/root/.claude/plans/vamos-construir-um-dashboard-hazy-crescent.md`.

## O que é

Dashboard SimHub para **Super Formula SF23 / iRacing**, 1280×517, gerado 100%
por código. Substitui a edição manual no editor do SimHub.

```bash
python3 build.py                    # gera build/iRacing_Dashboard_00
python3 tools/formula_audit.py      # confere que nenhuma fórmula sumiu
python3 tools/preview.py --repeat 8 # gera build/preview.html
python3 tools/preview_modes.py      # um preview por modo -> build/modes/
python3 tools/dump_formulas.py      # re-extrai as fórmulas do original
python3 tools/decompile.py          # .djson -> src/dash/generated/*.py
python3 tools/parity.py             # compara com referencia-manual/
```

Preview como imagem (Chromium já instalado no ambiente):

```bash
/opt/pw-browsers/chromium --headless --disable-gpu --no-sandbox \
  --hide-scrollbars --window-size=1360,660 --screenshot=shot.png \
  "file:///home/user/simhubeleza/build/preview.html"
```

Página de revisão publicada (16 abas: 4 modos da coluna direita, 10 avisos da
barra superior e 2 estados do RPMLed, montadas sobre `build/modes/`):
<https://claude.ai/artifact/7E9k77H5zjfvoEHtYdjqC9>
O fonte dela é `tools/preview_page.html`; para republicar, rodar
`preview_modes.py`, copiar a página como `build/modes/index.html` e publicar
com os 16 arquivos ao lado.

Ao tirar screenshot, usar altura de janela **700**: a 540 o rodapé sai cortado
pela janela, não pelo layout — o que já custou um diagnóstico errado.

## Concluído

- **Fases 1–4**: gerador completo com paridade validada (diff vazio) contra o
  dashboard feito à mão. `RPMLed` e leaderboard reescritos como código legível.
- **Ferramental de redesign**: `tools/preview.py` (render HTML, validado contra
  o export real do SimHub) e `tools/formula_audit.py` (baseline: 103 fórmulas).
- **Design system**: `src/simhub/theme.py` com a paleta watchOS;
  `src/dash/layout.py` com a grade do wireframe; `src/dash/widgets.py` com
  `tile`, `value_unit`, `caption`, `segmented_bar`, `ramp`.
- **Fase 5 completa**: todas as regiões redesenhadas, cada uma em seu módulo
  em `src/dash/`, ligadas pelo dicionário `EXTRACTED` em `tools/decompile.py`:

| Região | Módulo | Camada extraída |
|---|---|---|
| Barra superior | `top_bar.py` | `Top Component` |
| Coluna esquerda | `left.py` | `Left Component2` |
| Centro (marcha/SPD/RPM) | `center.py` | `Center Component` |
| OTS (push-to-pass) | `ots.py` | (dentro de `center.py`) |
| Coluna direita | `right.py` | `Right Component` |
| Leaderboard e overflow | `leaderboard.py` | (dentro de `right.py`) |

- **Fase 6 — barra superior do Figma** (`LDY1mlry0kX59Nw6ueDj1h`, section
  `4317:567`): `top_bar.py` reescrito contra o design medido, `rpmled.py`
  re-autorado (4 slots de 53x36, **vermelho para fora**, invertendo a rodada
  anterior), Inter adicionada em `assets/fonts/`, e a altura da barra passou
  de 115.8 para ~136 (painel de 125.9 + margem de 6 + respiro de 4).
  Toda a geometria da barra deriva de `grid.SCALE` (= 1268/1329) e do helper
  `grid.scaled()`, e as regiões do corpo derivam de `TOP_BAR.bottom` em vez
  dos três literais `115.8` de antes. A barra inferior única agora é o
  `grid.BOTTOM_BAR_HEIGHT` compartilhado (esquerda, OTS e direita), com o
  `STATS_HEIGHT` da esquerda absorvendo a folga.

- **Barras do delta invertidas**: no cartao do delta, a barra grossa passou a
  mostrar o delta progress (`SessionBestLiveDeltaProgressSeconds`, escala de
  0.1 s) e o trilho fino o delta absoluto (`DeltaToSessionBest`, escala de
  0.5 s). Constantes renomeadas para `WIDE_BAR_*` / `THIN_BAR_*`.

- **Pedais em pente**: freio e acelerador viraram um gauge continuo entre um
  trilho e uma mascara PNG (100 dentes, 1 por ponto percentual). O dente de
  cada dezena e pintado na mascara, mais baixo e escuro: nunca acende, so
  demarca. `top_bar.IMAGES` e `ots.IMAGES` entram no Images[] pelo
  `build.py`, com MD5 e tamanho lidos do arquivo. O preview le
  `GaugeAlignment` 2 como "enche da direita" (antes tratava 1).

- **Refino do canvas portado** (paleta Grafite, canvas
  <https://claude.ai/artifact/AbajxTu5mfqDBn6uAcL1J4>):
  - `theme.py`: paleta grafite, Arame Mono nos numeros/rotulos e na marcha,
    Funnel Sans nos nomes, chanfro `(3, 14, 3, 14)` nos tiles (`rounded()`
    aceita tupla de cantos). Na Arame Mono o `text()` ignora `mono`/CharWidth:
    a fonte ja e monoespacada (0.6 em por glifo), e `value_unit` usa isso
    para encostar a unidade no numero.
  - Barra superior em pixels (sem a escala do Figma): painel de 108.92, duas
    linhas de 38.16 da borda ao cartao do delta, cartao centrado como tile.
    O delta progress tambem virou pente (`DeltaComb`). Margem de 6 em todas
    as bordas, inclusive embaixo (`BODY_BOTTOM = 511`).
  - RPM em rampa azul (`RPM_RAMP`), cada LED para fora mais claro e com halo
    borrado maior.
  - Marcha num disco, com brilho por estado (`center.GLOW_COLOR`): roxo no
    limite de RPM > verde com OTS ativo > vermelho carregando > ciano no
    limiter > ambar.
  - OTS: verde pronto, roxo piscando ativo (`BlinkEnabled`), vermelho
    carregando; barra em pente (`OtsComb`).
  - Brake bias brilha verde ao subir e vermelho ao descer por 1.6 s: formula
    JS que guarda o ultimo valor em `root` (`left.bias_flash`). **Nao testado
    no SimHub** -- se `root` nao persistir entre avaliacoes, o numero so fica
    ambar.
  - Coluna esquerda/direita sem fundo de coluna: cada bloco e um tile, com
    filetes entre campos. Linha do jogador em ambar.
  - Mascaras: `python3 tools/make_combs.py` (substitui `make_pedal_comb.py`)
    -- mudou a medida de uma barra, rode de novo.

- **Barra de balanço sub/sobre-esterço** (`src/dash/balance.py`): rodapé da
  coluna central, sob a marcha. O iRacing
  não entrega slip angle, então a fórmula JS estima o ângulo de cada eixo pelo
  modelo de bicicleta (`VelocityX/Y`, `YawRate`, `SteeringWheelAngle`) e mostra
  |alfa_d| - |alfa_t|, suavizado: sub (ciano) para a esquerda, sobre
  (vermelho) para a direita, fundo de escala 3°. Constantes do SF23
  (entre-eixos, distribuição de peso, relação de direção) são estimativas --
  com o carro neutro numa curva longa a barra deve ficar perto do meio; se
  não ficar, ajustar `STEERING_RATIO` primeiro.

- **Setores** (`src/dash/sectors.py`): rodapé da direita. Setor atual em
  cima (destacado, tempo e delta vivos), os dois anteriores embaixo (apagados
  quando são da volta passada); ao lado LAST (+delta), BEST e OPT. Referência:
  melhor volta da sessão -- o SimHub só guarda setores dela. Nulo/zero vira
  N/A; setor ou delta acima de 99 s vira OFF. O delta do setor atual é o
  `SessionBestLiveDeltaSeconds` menos o valor na entrada do setor (em `root`).
  As condições da pista foram para a coluna esquerda: TRACK/AIR/RAIN na linha
  do bias (que perdeu as unidades), HOUR/GRIP no rodapé.

- **`tools/dump_formulas.py`**: extrai as fórmulas longas do original para
  `src/dash/generated/formulas.py`, que os módulos de layout referenciam. É o
  que permite restilizar overflow, relative e lap log sem recopiar trinta
  linhas de JavaScript a mão.

## Falta

**Validar no SimHub de verdade.** É o único passo que não dá para fazer daqui,
e nada do redesign foi visto rodando: o preview é estático e não avalia
fórmula nenhuma. Copiar `build/iRacing_Dashboard_00` para a pasta
`DashTemplates` e abrir.

O que merece olhar primeiro, por ordem de risco:

1. **Cores em fórmula do OTS** — usam nomes CSS, não hex (ver pendências).
   Se hex funcionar, trocar pelos valores exatos da paleta.
2. **Escala do widget de telemetria** — virou `472/607` (largura exata do
   painel) no lugar do `0.74` do original. Conferir se não serrilhou.
3. **Barra de balanço** — conferir os sinais de `VelocityY`/`YawRate`/
   `SteeringWheelAngle` (se a barra for para o lado errado numa curva, o
   sinal de algum deles está trocado) e calibrar `STEERING_RATIO`.
4. **Setores** — `currentlapgetsectortime`/`lastlapgetsectortime`/
   `sessionbestlapgetsectortime`/`bestsectortime` chamadas de dentro do JS e
   `SectorsCount` no iRacing (pode ficar em 3 em pista com mais setores).
5. **Altura de linha do leaderboard** — saiu da divisão (13 linhas no corpo da
   coluna), então ficou menor que a do original. Conferir legibilidade em
   pista, não parado no menu.

## Como redesenhar uma região

1. Ler a subárvore atual em `referencia-manual/iRacing_Dashboard_00.djson`
   para extrair as fórmulas (a lógica de telemetria é preservada intacta).
2. Escrever o módulo usando `layout.py` (posição), `theme.py` (cor/tipografia)
   e `widgets.py` (componentes). Nenhum literal de cor fora de `theme.py`.
3. Registrar em `EXTRACTED` e rodar `decompile.py` para trocar a subárvore.
4. `build.py` → `formula_audit.py` (nenhuma removida) → `preview.py` + screenshot.

## Regras do projeto

- Só stdlib do Python. Sem dependências externas.
- `referencia-manual/` é baseline intocado.
- `None` é valor literal nos construtores; use `OFF` para omitir um campo.
- Plugins exigidos no SimHub: **DahlDesign** (OTS do SF23),
  **IRacingExtraProperties** (leaderboard de classe), **PersistantTrackerPlugin**.

## Pendências conhecidas

- `parity.py` vai divergir conforme o redesign avança — é esperado. A garantia
  ativa passa a ser `formula_audit.py`. O plano prevê um `build.py --legacy`
  para manter a paridade validando o toolchain; ainda não implementado.
- **Cores em fórmula do OTS** usam nomes CSS (`limegreen`, `gold`, `orange`),
  não hex, porque são os que o SimHub resolve com certeza em fórmula de cor.
  Ficam a menos de 1% das cores da paleta.
- **Hexes do Figma não confirmados**: o MCP bateu no limite do plano Starter
  no meio da coleta. Ficaram por bater o cinza do segmento apagado e as 10
  cores dos chips de bandeira; foram implementados com a paleta do tema (o
  vermelho voltou `#ff453a`, idêntico ao `theme.RED`, o que sugere que a
  paleta bate).
- Egress para `figma.com` bloqueado: imagens do board só chegam inline via MCP.
- Figma: board `oNysXpR5jA2JbFjFzt60Vq`, section `1993:326`
  (wireframe `1993:481`, referências `1993:482` e `1993:486`).

### Propriedades do SimHub — validadas com dumps reais do usuário

O usuário mandou dois dumps da própria instalação: `SampleTelemetry.json`
(4954 propriedades de `GameRawData.Telemetry.*`) e `SampleSessionData.json`.
Resolveu quase tudo que estava pendente.

**Confirmadas, sem mudança de código:**

- `[GameRawData.Telemetry.IsOnTrack]` — existe, booleano nativo.
- `[GameRawData.Telemetry.LapCurrentLapTime]` — existe, numérico, em segundos.
- `[GameRawData.Telemetry.CarLeftRight]` — existe. Os valores batem com o
  enum público do SDK do iRacing (`irsdk_CarLeftRight`): 2/4/5 à esquerda,
  3/4/6 à direita — exatamente o que os chips LEFT/RIGHT já assumiam.
- `[Flag_Green]`, `[Flag_Yellow]`, `[Flag_White]` — não aparecem no dump (são
  computadas por outro plugin, não telemetria bruta), mas o dashboard
  original já as usa sem prefixo — confirmação indireta e sólida.

**Corrigida — nome estava errado:**

- `[SessionTypeName]`, usada para decidir o modo Practice, **não existe** —
  não apareceu em nenhum dos dois dumps nem no dashboard original; era
  invenção sem base, ao contrário de `CarLeftRight`, que acertou por
  coincidir com o SDK. O caminho real, confirmado no dump:
  `SessionInfo.CurrentSessionNum` (índice da sessão atual) mais
  `SessionInfo.Sessions0<n>.SessionType` (o texto, indexado por sessão do
  fim de semana). NCalc não indexa propriedade dinamicamente, então a
  condição de "está em treino" (`IN_PRACTICE_JS` em `right.py`) agora é
  JavaScript com `$prop()` e concatenação — mesmo padrão que o lap log já
  usava para `PreviousLap_0<n>_*`. Os dois formulas que a incorporavam
  (Standings, Relative) viraram JS também, pelo mesmo motivo.
  **Ressalva que continua**: a string exata de uma sessão de treino livre
  solo (`'Offline Testing'`) segue sem confirmação — nenhum dos dois dumps
  era desse tipo de sessão (eram fins de semana com practice/qualy/race).

**Confirmada — o maior risco da lista, resolvido:**

- O usuário mandou `PluginsData\PluginsActivation.json`. O plugin de
  histórico de volta está **instalado e ativo** (`IsEnabled: true`,
  aparece 3× — uma cópia por perfil de jogo). A classe interna é
  `SimHub.Plugins.DataPlugins.PersistantTracker.LapHitoryPlugin` (o "Hitory"
  sem o "s" é erro de digitação do próprio SimHub, não afeta nada) —
  irrelevante para nós, porque o prefixo de propriedade
  `PersistantTrackerPlugin.PreviousLap_XX_*` já vinha confirmado pelo uso no
  dashboard original. `IRacingExtraProperties` também está `IsEnabled: true`.
  Isso remove o risco de o lap log inteiro não resolver nada em tela.

**Ainda sem confirmação:**

- `[Flag_Black]` e `[Flag_Blue]` — mesma categoria de `Flag_Green`, sem
  confirmação direta ainda.
- `PersistantTrackerPlugin.PreviousLap_0<n>_FuelConsumed` — o plugin existe
  e está ativo, mas o **nome exato desta propriedade específica** ainda é
  palpite (segue o padrão de `_DeltaToSessionBest`, mas pode não existir com
  esse sufixo). Só um dump do próprio `PersistantTrackerPlugin` confirma.
- Os chips **DIRT** e **INCIDENT** ficam declarados e desligados: não há
  propriedade clara para eles.
- **Temperatura da pista por volta**: não há (que se saiba) um histórico
  indexado por volta dessa variável no `PersistantTrackerPlugin` — o lap log
  mostra a leitura *atual* só na linha da volta mais recente, em vez de
  repetir um valor errado nas voltas anteriores.
- A string exata de uma sessão de treino livre solo (`'Offline Testing'`,
  usada para o modo Practice em `right.py`) segue sem confirmação — os dumps
  recebidos eram sempre de fins de semana com practice/qualy/race, nunca de
  uma sessão avulsa de treino.

## Modos automáticos da coluna direita

Implementado em `src/dash/right.py` (antes só a ferramenta de preview ligava
os modos manualmente; agora são fórmulas reais):

- **Standings**: fora de pista, ou nos 4s seguintes a cada volta completada.
- **Relative**: nos demais casos (o modo padrão de corrida). Agora com 3
  pilotos à frente + o jogador + 3 atrás (antes eram 2+1+2).
- **Practice** (lap log): só quando a sessão atual é `'Offline Testing'`
  (ver como isso é resolvido nas pendências de propriedades acima — é JS,
  não NCalc simples). Ocupa a seção inteira (não divide mais espaço com o
  relative) e ganhou 3 colunas novas por volta — temperatura da pista, delta
  para a melhor volta e combustível consumido (ver pendências acima).

## Verificação visual da barra superior — feita

Confirmado no render: a barra inferior é única de verdade (rodapé esquerdo,
OTS e rodapé direito partilham topo 418.9 e base 505.0, agora por construção
via `grid.BOTTOM_BAR_HEIGHT`); o vermelho do RPMLed aponta para fora nos dois
lados; a marcha a `SIZE_GEAR=185` não estoura; o lap log ocupa a seção inteira
com as 5 colunas; e o cartão do delta cai nas coordenadas do Figma.

Dois defeitos achados e corrigidos:

- `Time` e `Hour` renderizavam `00:0C` — cinco glifos a 25px num campo de
  70.4px. `Region.columns()` agora aceita `weights`, e os dois rodapés dão
  1.4× à coluna de tempo (mesmo padrão do `left.BIAS_WIDTH`).
- No widget de telemetria, a caixa do rótulo `100` começava 8px acima do grupo
  e saía 4px por cima do widget; os badges de pedal vazavam 2px por baixo.
  Ambos ajustados em `src/dash/generated/telemetry.py` sem tocar em fórmula.

## O que ainda falta

1. **Mapeamento de propriedades do SimHub.** É o maior bloqueio. Os arquivos
   `PluginsData\IRacing\SampleTelemetry.json` e `SampleSessionData.json` da
   instalação do usuário são um dump da struct do iRacing e resolvem quase
   tudo. Há um sinal de alerta: uma varredura pelas DLLs não achou **nenhuma**
   string `PreviousLap_`, e não existe pasta do `PersistantTrackerPlugin` em
   `PluginsData` — se o plugin não estiver instalado, o lap log inteiro não
   resolve nada em tela.
2. **Validar no SimHub de verdade** (abaixo).
3. No lap log, a coluna TRACK sai apagada em todas as linhas no preview. A
   intenção era apagar só as voltas antigas e manter viva a da volta atual;
   como é fórmula, só dá para confirmar rodando.
