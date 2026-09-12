# Estado do projeto

Retomada rápida para uma sessão nova. O plano completo está em
`/root/.claude/plans/vamos-construir-um-dashboard-hazy-crescent.md`.

## O que é

Dashboard SimHub para **Super Formula SF23 / iRacing**, 1280×517, gerado 100%
por código. Substitui a edição manual no editor do SimHub.

```bash
python3 build.py                    # gera build/iRacing_Dashboard_00
python3 tools/preview.py --repeat 8 # gera build/preview.html
python3 tools/formula_audit.py      # confere que nenhuma fórmula sumiu
python3 tools/parity.py             # compara com referencia-manual/
```

Preview como imagem (Chromium já instalado no ambiente):

```bash
/opt/pw-browsers/chromium-1194/chrome-linux/chrome --headless --disable-gpu \
  --no-sandbox --hide-scrollbars --window-size=1360,660 \
  --screenshot=shot.png "file:///home/user/simhubeleza/build/preview.html"
```

## Concluído

- **Fases 1–4**: gerador completo com paridade validada (diff vazio) contra o
  dashboard feito à mão. `RPMLed` e leaderboard reescritos como código legível.
- **Ferramental de redesign**: `tools/preview.py` (render HTML, validado contra
  o export real do SimHub) e `tools/formula_audit.py` (baseline: 103 fórmulas).
- **Design system**: `src/simhub/theme.py` com a paleta watchOS;
  `src/dash/layout.py` com a grade do wireframe; `src/dash/widgets.py` com
  `tile`, `value_unit`, `caption`, `segmented_bar`, `ramp`.
- **Regiões redesenhadas**: barra superior (`src/dash/top_bar.py`) e o widget
  `RPMLed` (progressão verde → amarelo → vermelho).

## Falta (Fase 5)

Redesenhar as regiões restantes, cada uma em seu módulo em `src/dash/`, e
ligá-las pelo dicionário `EXTRACTED` em `tools/decompile.py`:

| Região | Módulo a criar | Camada a extrair |
|---|---|---|
| Coluna esquerda | `left.py` | `Left Component2` |
| Centro (marcha/SPD/RPM) | `center.py` | `Center Component` |
| OTS (push-to-pass) | `ots.py` | `OTS` |
| Coluna direita | `right.py` | `Right Component` |

A coluna direita alterna entre **modos** — standings, overflow, relative
(`Driver Ahead` / `Me` / `Driver Behind`) e `LAP LOG` de treino. Todos precisam
ser restilizados, não só o visível no screenshot.

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
- Egress para `figma.com` bloqueado: imagens do board só chegam inline via MCP.
- Figma: board `oNysXpR5jA2JbFjFzt60Vq`, section `1993:326`
  (wireframe `1993:481`, referências `1993:482` e `1993:486`).
