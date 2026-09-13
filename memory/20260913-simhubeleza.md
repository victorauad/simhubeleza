# Handoff — simhubeleza — 2026-09-13

## O que foi feito nesta sessão
- Diagnosticado e corrigido o formato de importação do dashboard no SimHub: descoberto que o SimHub importa um arquivo único `.simhubdash` (zip com extensão trocada), não uma pasta solta em `DashTemplates`.
- Criado `tools/package.py`: empacota `build/iRacing_Dashboard_00/` num `.simhubdash`, com os arquivos aninhados numa subpasta com o nome do dashboard dentro do zip (primeira tentativa, com arquivos soltos na raiz do zip, travava a tela de import no SimHub sem nome/thumbnail).
- Validado end-to-end pelo usuário: importação no SimHub funcionou ("consegui, deu tudo certo").
- Atualizado `ESTADO.md` com o comando `python3 tools/package.py` e instruções corretas de importação.
- Usuário gravou um vídeo (mp4) do dashboard rodando ao vivo no SimHub. Extraídos frames via PyAV + Pillow (sem ffmpeg disponível no ambiente) e analisado visualmente contra o código-fonte.
- Da análise do vídeo, confirmadas como **intencionais** (não bugs): o chip "OVERLAP" disparando durante trail-braking, e a cor magenta/roxa do shift light e do texto de marcha no redline.
- Identificado como bug real (não visto antes): o valor numérico do pedal (freio/acelerador) no topo pode estourar a caixa (valores como "296" ou "9105" em vez de 0–100), sugerindo que `[Brake]`/`[Throttle]` sem prefixo de plugin não resolvem para o percentual esperado — provavelmente precisam ser `[DataCorePlugin.GameData.NewData.Brake]`/`...Throttle`.
- Usuário ditou (por voz, mensagem parcialmente cortada) uma lista de 9 ajustes de UI a fazer — investigação de código concluída para a maioria, ainda sem nenhuma edição feita:
  1. Componente Delta (barra superior) descentralizado; pedais de freio/acelerador também descentralizados; espaçamento entre eles errado.
  2. Encolher a largura da coluna CENTER para igualar à largura do card Delta.
  3. Igualar a largura do componente OTS também — Delta, Center e OTS com a mesma largura, usando Delta como referência.
  4. Modo Standings: texto grande demais para a caixa (ou caixa pequena demais) — ainda não investigado (falta abrir `src/dash/leaderboard.py`).
  5. Grip: texto cortado; a propriedade tem ~5-6 valores possíveis; usuário quer um código numérico 1→5-ou-6 (1 = mais grip, número maior = menos grip). **Faltam os valores exatos da enum** — usuário não completou a lista ao ditar.
  6. Rain: hoje sempre mostra "NA" (bug herdado do dashboard original); quando não há dado de chuva, deveria mostrar "--" em vez de "NA".
  7. Time: deve mostrar minutos restantes totais como número simples (ex: "90"), não no formato hora:minuto atual (`mm\.ss` em `[SessionTimeLeft]`).
  8. FPL target / FPL last: o rótulo de unidade está longe demais do valor numérico; quer valor alinhado à direita com distância fixa e consistente até a unidade — mesma correção deveria valer para "uma porcentagem" (campo exato ambíguo na transcrição).
  9. Quando o pedal (acelerador ou freio) não está pressionado, o valor numérico fica invisível — precisa sempre aparecer (inclusive "00" com pedal solto). Nota: o código atual de `top_bar.py` (`pedal()`) não tem nenhum binding de `Visible`, então a causa raiz ainda não está clara a partir do código-fonte sozinho.
- Instalado o skill `co-coach-handoff` (copiado do repositório `victorauad/co-coach`, removendo a seção de sync automático ao GitHub que era específica daquele projeto). Commitado e enviado ao branch `claude/blissful-wright-286ewk`.

## Estado atual
- `.simhubdash` packaging: **funcionando e validado** pelo usuário.
- Vídeo analisado, root causes identificadas para a maior parte da lista de 9 itens (ver acima); nenhuma correção de código ainda foi implementada para esses 9 itens.
- Faltam ainda:
  - Abrir `src/dash/leaderboard.py` (nunca lido nesta sessão) para diagnosticar o item #4.
  - Os valores exatos da enum de Grip (item #5) — pendente de confirmação com o usuário ou com a documentação do iRacing/SimHub.
  - Esclarecer qual campo exato é "a porcentagem" mencionada no item #8.

## Próximos passos
1. Abrir `src/dash/leaderboard.py` e diagnosticar o problema de texto/caixa do modo Standings (item #4).
2. Perguntar ao usuário os valores exatos da enum `SessionTrackRubberState` (Grip) e qual campo é "a porcentagem" do item #8.
3. Implementar as correções, prováveis arquivos:
   - `src/dash/layout.py` — larguras de CENTER/OTS/LEFT/RIGHT (itens #2, #3).
   - `src/dash/top_bar.py` — centralização do Delta e pedais (item #1), binding de Visible dos valores de pedal (item #9).
   - `src/dash/right.py` — Grip (item #5) e Rain (item #6).
   - `src/dash/left.py` — Time (item #7) e espaçamento FPL target/last (item #8, junto com `src/dash/widgets.py::value_unit`).
   - `src/dash/leaderboard.py` — Standings (item #4).
4. Rodar o fluxo de verificação padrão do projeto: `build.py`, `tools/formula_audit.py` (garantir que nenhuma fórmula do original sumiu), `preview.py`/`preview_modes.py`, depois `tools/package.py` para gerar novo `.simhubdash` e pedir validação real do usuário no SimHub.
5. Commitar e dar push para `claude/blissful-wright-286ewk`.

## Decisões e contexto importantes
- `.simhubdash` é um zip com os arquivos do dashboard aninhados numa subpasta nomeada como o dashboard (não soltos na raiz) — confirmado por tentativa e erro real no SimHub do usuário.
- Grip (valor bruto do enum) e Rain (formato "NA" fixo) já eram bugs no dashboard original manual (`referencia-manual/iRacing_Dashboard_00.djson`), confirmado via grep — não são regressões introduzidas pelo redesign.
- `tools/formula_audit.py` garante que nenhuma fórmula do dashboard original desapareça durante o redesign (paridade de lógica, não de layout/estilo) — deve ser rodado antes de considerar qualquer mudança de fórmula concluída.
- Sem dependências externas nas ferramentas do projeto (`tools/*.py` usam só stdlib); `av`/`pillow` usados nesta sessão foram só para análise ad hoc do vídeo, não fazem parte do toolchain do dashboard.
- Ambiente sem `ffmpeg` real utilizável (o ffmpeg do Playwright é um build restrito sem suporte a h264/mov).

## Arquivos relevantes
- `tools/package.py` — empacotador `.simhubdash` (novo, funcionando).
- `ESTADO.md` — status do projeto, atualizado.
- `src/dash/layout.py`, `src/dash/top_bar.py`, `src/dash/center.py`, `src/dash/left.py`, `src/dash/right.py`, `src/dash/widgets.py`, `src/dash/rpmled.py` — lidos por completo, mapeados os pontos de mudança para os 9 itens pendentes.
- `src/dash/leaderboard.py` — ainda não lido, próximo passo.
- `src/simhub/bindings.py` — helpers `ncalc`/`js`/`formatted`/`prop`/`driver_prop`, necessários para as correções de fórmula (Time, Rain, Grip).
- `referencia-manual/iRacing_Dashboard_00.djson` — referência original, usado para confirmar que Grip/Rain já eram bugs herdados.
- `.claude/skills/co-coach-handoff/SKILL.md` — skill recém-instalado (este arquivo de handoff foi gerado por ele).
