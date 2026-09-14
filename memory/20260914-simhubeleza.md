# Handoff — simhubeleza — 2026-09-14

## O que foi feito nesta sessão

### Rodada 1 — os 9 ajustes de UI ditados (commit `45bba89`)
- **Pedais**: binding trocado de `[Brake]`/`[Throttle]` para `[DataCorePlugin.GameData.NewData.Brake]`/`...Throttle` — o caminho sem prefixo devolvia valores absurdos (296, 9105). A fórmula do chip OVERLAP foi atualizada junto.
- **Delta**: o cartão estava 7 unidades deslocado à direita do centro do vão entre os pedais (511→818). Todas as coordenadas do cartão (`CARD`, labels, barras, ticks) deslocadas −7 em `top_bar.py`.
- **Larguras**: `CENTER` e `OTS` deixaram de usar o literal `312.1` e passam a derivar da largura real do cartão do Delta (`289.0 * SCALE` ≈ 275,7px). `LEFT`/`RIGHT` dividem o resto (≈502,1 cada), `RIGHT.x` recalculado.
- **Standings**: `ROW_TEXT_SIZE` deixou de ser 17.0 fixo e virou `min(17.0, ROW_HEIGHT * 0.72)`; `GAP_WIDTH` 64→56 e `DIFF_WIDTH` 78→70 para dar espaço ao nome.
- **Grip / Rain / Time / value_unit**: primeira tentativa — **duas delas falharam em produção**, ver rodada 2.

### Rodada 2 — vídeo + prints revelaram falhas (commit `dfea315`)
O usuário importou o build, filmou de novo (`teste_2.mp4`, 141s) e mandou prints. Extraí frames com PyAV+Pillow e comparei com o código.
- **Grip mostrava `0`**: eu tinha mapeado a enum com nomes inventados (`Optimum`, `High`…). Os dumps que o usuário já havia enviado provam que os valores reais são frases do iRacing: `moderately low usage`, `carry over`. Refeito como fórmula **JavaScript** com `indexOf()` por palavra-chave → `1`–`6`, `CO` para carry over, `--` para string desconhecida.
- **Time mostrava `14:` cortado**: usei `floor()` minúsculo, que **não existe no NCalc do SimHub** — a fórmula cai em silêncio e o controle exibe o valor bruto (TimeSpan) cortado pela caixa. Removido; `timespantoseconds([SessionTimeLeft])/60` com format `"0"` (o format já arredonda).
- **Unidades de medida**: TRACK e AIR em `°C`, RAIN em `%`, TIME em `min` — o rodapé da direita passou a usar o mesmo `value_unit()` da coluna esquerda em vez de montar `text()` à mão. SPD e RPM ganharam a unidade no próprio rótulo (`SPD KM/H`, `RPM X10`); o RPM segue dividido por 10 (decisão do usuário), o rótulo é que diz isso.
- **Pedal em 100%**: removido o hack herdado `if([prop]=100,'00',[prop])`, que mostrava `00` com o acelerador no fundo. Agora `formatted("[prop]", "00")` → `00` / `89` / `100`. Também resolve o freio aparecer com um dígito só.
- **Relative** (pedido no meio da sessão): um único formato `m:ss.fff` nas três variações de linha (antes eram três diferentes — vazio nos de frente, `m\.ss\.ff` nos de trás, e `toshorttime()` na do jogador); largura de glifo derivada da fonte em vez de `14.0` fixo; monoespaçado só nas colunas numéricas (Position, Car Number, Last Lap, Gap, Name2), nome proporcional; nome da linha do jogador ligado a `[DataCorePlugin.GameData.PlayerName]` em vez do placeholder "Lorem ipsum".
- **Leaderboard**: mesma derivação de largura de glifo (`ROW_CHAR_WIDTH = ROW_TEXT_SIZE * 0.62`) — a fonte menor da rodada 1 tinha deixado os dígitos esparramados (`1 0 . 1`). Coluna `Gap` afastada da borda com `PADDING`.
- **`value_unit()`**: `unit_drop` de `0.62` para `0.45` — o `%` do brake bias (fonte grande) caía abaixo do número, parecendo índice. E sem unidade nenhuma, o valor agora ocupa a região inteira.

## Estado atual
- Tudo commitado e enviado para `claude/blissful-wright-286ewk` (`45bba89`, `dfea315`). Working tree limpo.
- `build.py`, `tools/formula_audit.py`, previews e `tools/package.py` rodando sem erro. O audit lista 8 fórmulas "REMOVIDAS" — todas são substituições intencionais (Grip, Time, Rain, texto e Visible dos dois pedais, `toshorttime` do relative).
- Dois `.simhubdash` entregues ao usuário nesta sessão; o segundo (v4) **ainda não foi validado ao vivo no SimHub**.
- Agora dá para tirar screenshot dos previews: `pip install playwright` + Chromium em `/opt/pw-browsers/chromium-1194/chrome-linux/chrome` (`launch(executable_path=..., args=["--no-sandbox"])`). **Container efêmero — a próxima sessão precisa reinstalar o pacote.**

## Próximos passos
1. **Esperar a validação do usuário no SimHub** do build v4. Três coisas só o jogo confirma: Grip (se aparecer `--`, é uma string de pista fora da minha tabela — pedir o print e acrescentar), Time (se ainda quebrar, refazer o campo em JS com `$prop`, como o Grip) e o pedal em 100%.
2. Confirmar o formato do tempo de volta no relative: o usuário ditou "M:SS:F" e eu interpretei como `m:ss.fff` (o que a maioria das linhas já mostrava). Se ele quiser uma casa decimal só, é trocar `REL_LAP_FORMAT` em `right.py`.
3. Pendências antigas ainda abertas: o "PUSH TO PASS / READY 200" não tem unidade (não sei a semântica do número — contagem ou segundos); e o `%` do brake bias ainda fica um pouco baixo.

## Decisões e contexto importantes
- **Armadilhas do NCalc do SimHub, confirmadas na prática nesta sessão** (é o que mais economiza tempo da próxima):
  - `floor()` **não existe** e falha em silêncio — o controle mostra o valor bruto da propriedade. `timespantoseconds()` **funciona** em NCalc (está numa fórmula do dashboard original, em `top_bar.py`).
  - NCalc não tem funções de string. Casamento por palavra-chave exige `js()` (`$prop(...)`, `indexOf`), como em `leaderboard.py`.
  - Format string numérico (`'00'`, `'0'`) não trunca: `100` com format `'00'` sai `100`.
- **`SessionTrackRubberState`** devolve frases do iRacing. A ordem dos testes importa: `moderately low usage` também contém `low usage`, então o mais específico vem antes. Mais borracha = mais grip = número menor.
- **Os dumps em `/root/.claude/uploads/2da801b4-.../*.txt`** (`simhub-properties.txt`, `simhub-session.txt`, `export_powershell.md`) são **telemetria crua do iRacing**, não a lista de propriedades computadas do SimHub — não têm `SessionTimeLeft` nem `Rpms`. Para propriedades computadas, a fonte de verdade é `referencia-manual/iRacing_Dashboard_00.djson`.
- **RPM**: o `/10` em `center.py` é herdado do original e foi **mantido por decisão do usuário** — não "conserte" isso achando que é bug de largura de caixa.
- **`tools/formula_audit.py`** marca como "REMOVIDA" qualquer fórmula cujo *texto* mudou, mesmo quando a lógica é equivalente (trocar o nome da propriedade já conta). Ler a lista item a item, não tratar como falha.
- O `Visible` do valor do pedal continua **sem binding de propósito** (o original escondia o número com pedal solto; o Figma mostra `00`). O audit sempre vai listar isso como removido.

## Arquivos relevantes
- `src/dash/top_bar.py` — pedais (binding, formato do valor), cartão do Delta, chips.
- `src/dash/right.py` — `GRIP_EXPRESSION_JS`, `RAIN_EXPRESSION`, rodapé com unidades, e todo o modo relative (`rel_text`, `rel_row`, `REL_LAP_FORMAT`).
- `src/dash/left.py` — rodapé da sessão (Time), linha de stats (brake bias, FPL, wind).
- `src/dash/leaderboard.py` — Standings: `ROW_TEXT_SIZE`, `ROW_CHAR_WIDTH`, larguras de coluna.
- `src/dash/widgets.py` — `value_unit()` (par valor+unidade, `VALUE_UNIT_GAP`, `unit_drop`), `text()`, `segmented_bar()`.
- `src/dash/center.py` — SPD/RPM (rótulos com unidade) e a marcha.
- `src/dash/layout.py` — grade: `_CENTER_WIDTH` derivado do Delta, `LEFT`/`RIGHT`/`OTS`.
- `src/simhub/bindings.py` — `ncalc()`, `js()`, `formatted()`.
- `src/dash/generated/formulas.py` — fórmulas do original; `binding(path, target, format_string=...)` aceita override de formato.
- `referencia-manual/iRacing_Dashboard_00.djson` — original, fonte de verdade para nomes de propriedade.
- `memory/20260913-simhubeleza.md` — handoff da sessão anterior.
