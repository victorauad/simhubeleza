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

Página de revisão publicada (as quatro abas de modo, montadas sobre
`build/modes/`): <https://claude.ai/code/artifact/326ce39f-af40-4fbb-87bb-0a9c5068dc36>
O fonte dela é `tools/preview_page.html`; para republicar, gerar
`build/modes/` e publicar a página com esses quatro arquivos ao lado.

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
3. **Altura de linha do leaderboard** — saiu da divisão (13 linhas no corpo da
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
- **Fórmulas removidas de propósito (2)**: `Gas Value.Visible` e
  `Brake Value.Visible` (`if([Throttle]<1,0,1)`). O Figma mostra "00" em
  repouso, então o número não some mais. `formula_audit.py` vai continuar
  listando as duas em REMOVIDAS — é esperado, não regressão.
- Egress para `figma.com` bloqueado: imagens do board só chegam inline via MCP.
- Figma: board `oNysXpR5jA2JbFjFzt60Vq`, section `1993:326`
  (wireframe `1993:481`, referências `1993:482` e `1993:486`).

### Propriedades do SimHub ainda não confirmadas (precisam de validação real)

Usadas nas fórmulas dos modos automáticos da coluna direita (`src/dash/right.py`)
e no lap log redesenhado. Todas seguem nomes padrão do SDK do iRacing/SimHub,
mas nenhuma tinha uso anterior neste projeto — se você puder mandar o
mapeamento de propriedades do SimHub (a lista completa, ou um export do
próprio SimHub), eu confirmo ou corrijo:

- `[GameRawData.Telemetry.IsOnTrack]` — usado para decidir "fora de pista"
  (Standings aparece quando `false`).
- `[GameRawData.Telemetry.LapCurrentLapTime]` — tempo decorrido da volta
  atual; usado como proxy de "acabou de completar uma volta" (`< 4` segundos).
- `PersistantTrackerPlugin.PreviousLap_0<n>_FuelConsumed` — combustível da
  volta `n` no lap log. É um palpite seguindo o padrão de
  `PreviousLap_0<n>_DeltaToSessionBest` (essa sim confirmada, já usada no
  dashboard original); a propriedade de combustível por volta pode ter outro
  nome ou não existir.
- `[Flag_Black]` e `[Flag_Blue]` — chips de bandeira novos da barra superior.
- `[GameRawData.Telemetry.CarLeftRight]` — spotter do iRacing, usado nos chips
  LEFT/RIGHT (valores 2/4/5 à esquerda, 3/4/6 à direita).
- Os chips **DIRT** e **INCIDENT** ficam declarados e desligados: não há
  propriedade clara para eles.
- **Temperatura da pista por volta**: não há (que se saiba) um histórico
  indexado por volta dessa variável no `PersistantTrackerPlugin` — o lap log
  mostra a leitura *atual* só na linha da volta mais recente, em vez de
  repetir um valor errado nas voltas anteriores. Se o `PersistantTrackerPlugin`
  expuser algo como `PreviousLap_0<n>_TrackTemp`, dá para preencher a coluna
  inteira.

## Modos automáticos da coluna direita

Implementado em `src/dash/right.py` (antes só a ferramenta de preview ligava
os modos manualmente; agora são fórmulas reais):

- **Standings**: fora de pista, ou nos 4s seguintes a cada volta completada.
- **Relative**: nos demais casos (o modo padrão de corrida). Agora com 3
  pilotos à frente + o jogador + 3 atrás (antes eram 2+1+2).
- **Practice** (lap log): só em `SessionTypeName = 'Offline Testing'`. Ocupa
  a seção inteira (não divide mais espaço com o relative) e ganhou 3 colunas
  novas por volta — temperatura da pista, delta para a melhor volta e
  combustível consumido (ver pendências de propriedades acima).

## Próximos passos (barra superior)

Tudo abaixo é verificação, não implementação — o código está pronto e o build
está verde (30 arquivos, `verify_fonts` passando).

1. **Comparar cada estado com o Figma lado a lado.** `tools/preview_modes.py`
   emite 16 previews em `build/modes/`: os 4 modos da coluna direita, os 10
   chips de bandeira e os 2 estados do LED (shift light, pit limiter).
   Conferir: ordem dos blocos, altura da fileira fina do pedal vs. dos
   quadrados de RPM, posição do número, o cartão DELTA/BEST, e o chip
   espelhado nos dois lados.
2. **Conferir a cascata da altura**: rodapé esquerdo + OTS + rodapé direito
   ainda lendo como uma barra única, marcha sem estourar com `SIZE_GEAR=185`,
   leaderboard legível a ~21.3px por linha.
3. **`tools/preview_page.html` está desatualizado**: ainda tem as 6 abas de
   bandeira antigas. Trocar pelos 10 chips + shift light + pit limiter, e
   atualizar os `NOTES`. Depois republicar o artefato de revisão.
4. **Mapeamento de propriedades do SimHub**: o usuário se ofereceu para mandar
   a lista completa. Vale aceitar — várias fórmulas (ver pendências acima)
   dependem de nomes não validados.
