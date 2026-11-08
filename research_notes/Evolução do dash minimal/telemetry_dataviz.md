# Referências de telemetria e data-viz minimalista para o dash

## Aviso sobre o Pinterest (leia primeiro)

O Pinterest não foi acessível de forma útil nesta pesquisa. As buscas retornaram apenas páginas de boards, sem o conteúdo dos pins, e as tentativas de WebFetch nos boards voltaram truncadas ou vazias. Por isso, **nenhuma imagem de pin foi visualmente verificada**. As referências de Pinterest abaixo servem apenas como pistas de busca (o que existe e onde procurar). Todas as ideias concretas vêm de fontes abertas (GitHub, sites de overlays, guias), que foram lidas.

Boards e pins encontrados (conteúdo não verificado):
- https://www.pinterest.com/moody3d/race-ui/ ("21 Race UI ideas")
- https://www.pinterest.com/dragonmen/race-ui/ ("63 Race UI ideas")
- https://www.pinterest.com/johnnymotion/telemetry/ ("11 Telemetry ideas", board de 2015)
- https://uk.pinterest.com/christianthuemer/f1/ ("82 F1 ideas", inclui pin de telemetria de Hamilton em Spa 2010, marcha por volta)
- https://in.pinterest.com/pin/371969250491859532/ ("F1 visuals")
- https://kr.pinterest.com/pin/103864335151393859/ (dashboard escuro com gráficos de métricas, minimalista; descrição apenas)
- https://in.pinterest.com/pin/dashboard-light-dark-mode--776167317053603083/ (dashboard em modo claro e escuro; descrição apenas)

Recomendação: abrir esses boards no navegador e salvar 10 a 15 pins de telemetria de pedais, delta e setores. Com as imagens em mãos, dá para validar as ideias abaixo visualmente.

---

## Como o delta é apresentado de forma compacta

### Takeaway
Os overlays mais usados combinam uma barra de delta centralizada no zero, com cor indicando ganho ou perda e um número com sinal. O traço de delta ao longo da volta fica como widget separado. O delta de velocidade costuma ser exibido em caixa separada do delta de tempo.

### Cited Findings
- O delta bar do overlay Official Overlays do benofficial2 mostra um campo central de Delta Time e um campo maior à direita com Delta Speed. A referência é o melhor limpo da sessão (ou o melhor histórico em classificação). Em corrida, o lado esquerdo mostra gap e intervalo para os carros vizinhos. A barra só aparece depois de uma volta de referência limpa. — [fixfactory/bo2-official-overlays](https://github.com/fixfactory/bo2-official-overlays)
- O Delta Speed muda de cor conforme o sinal. — [fixfactory/bo2-official-overlays](https://github.com/fixfactory/bo2-official-overlays)
- O Track Impulse oferece um "Delta Trace" com o traço contínuo de tempo ganho ou perdido contra o melhor ou a última volta. — [Track Impulse, overlays](https://track-impulse.com/overlays) (snippet de busca; a página lida só listou o nome do widget)
- O RaceLab tem um widget "Delta trace", descrito como linha contínua do tempo ganho ou perdido contra uma volta de referência. Também oferece "Build your own", com até 12 widgets personalizados, incluindo barras de delta e de combustível. — [RaceLab](https://racelab.app/)
- Um plugin de AC descreve a barra de delta estilo iRacing como uma barra ancorada no centro: a cor indica se você está ganhando ou perdendo tempo, e o comprimento indica a magnitude. — [jamessanford/assetto-corsa-deltabar](https://github.com/jamessanford/assetto-corsa-deltabar) (somente snippet de busca, não aberto)
- Um overlay do Overtake.gg (Ben's Delta Overlay) diz que ajuda a ver na hora se a velocidade no meio da curva está acima ou abaixo da referência. — [Ben's Delta Overlay](https://www.overtake.gg/downloads/bens-delta-overlay.65615/) (somente snippet de busca)
- A RaceLab avisa que overlays de delta são ótimos para treino e tomada de tempo, mas podem distrair em corrida. — [RaceLab](https://racelab.app/) (somente snippet de busca)

### Inferences
- Para o dash, a barra de delta pode ser um retângulo centrado no zero, com largura proporcional ao delta (limitado a ±X s), e um texto "+0.234" ao lado. Isso é feito só com retângulos e texto.
- O traço de delta ao longo da volta é uma linha de histórico, então cabe no ChartItem. Vale desenhar uma linha de zero fina e usar a mesma escala de tempo do gráfico de pedais, para o olho correlacionar delta com frenagem e aceleração.
- Atenção à cor: verde e vermelho já são usados pelo acelerador e pelo freio. Se o delta usar verde (ganho) e vermelho (perda), os gráficos vão se confundir. Sugestão: delta em azul ou ciano para ganho e laranja para perda, ou manter o delta fora da caixa de telemetria.
- Mostrar o delta só depois de uma volta de referência válida, como faz o bo2, evita valores sem sentido no início da sessão.

### Gaps
- Não foi possível ver o visual real dos pins de Pinterest sobre delta. Não dá para afirmar cores exatas nem proporções dos widgets que aparecem nos boards.
- Não encontrei especificação de escala de delta (quantos segundos ocupam a barra inteira) em nenhuma fonte aberta lida.

---

## Cores de setor (roxo, verde, amarelo) e o que elas significam

### Takeaway
A convenção comum é roxo para melhor da sessão, verde para melhor pessoal e cinza ou amarelo para mais lento. Mas o significado do roxo depende do jogo, pois nem todos publicam os tempos dos outros pilotos.

### Cited Findings
- Um guia descreve verde como melhor pessoal, roxo como melhor da sessão, e cores mistas como sinal de inconsistência, tráfego ou desgaste de pneu. — [Setting up the In-Game Overlays (pitsngiggles)](https://www.pitsngiggles.com/blog/setting-up-overlays) (somente snippet de busca)
- Um projeto usa roxo, verde e cinza, com cinza para trechos mais lentos que o melhor pessoal. — [SimracingBR-overlay](https://github.com/eliezzer/SimracingBR-overlay) (somente snippet de busca)
- O mesmo projeto observa que, em jogos que não publicam tempos de outros pilotos, o roxo costuma significar o melhor pessoal, e só vira melhor da sessão quando você está sozinho na sessão. — [SimracingBR-overlay](https://github.com/eliezzer/SimracingBR-overlay) (somente snippet de busca)
- Alguns overlays recalculam as cores em tempo real: se alguém faz um setor mais rápido, seu roxo cai para verde. — [SimracingBR-overlay, PR de setores](https://github.com/eliezzer/SimracingBR-overlay/pull/1) (somente snippet de busca)
- Como muitos jogos publicam só três setores, alguns overlays cronometram sub-setores por posição na pista e colorem cada trecho. — [Turn Telemetry Dashboard for AC/ACC in SimHub](https://www.overtake.gg/downloads/turn-telemetry-dashboard-for-ac-acc-in-simhub.87270/) (somente snippet de busca)

### Inferences
- Para o dash, um "track strip" de 3 a 10 blocos retangulares no topo da caixa, cada um colorido pelo último tempo de setor ou pela comparação com a referência, dá a leitura de setor sem texto.
- A cor roxa só faz sentido se houver dados de outros pilotos. Se o dash só tiver referência própria, usar uma cor neutra e rotular como "REF" evita falsa informação de "melhor da sessão".
- Os blocos podem ser feitos com retângulos, e a comparação de setor com formula simples (tempo atual menor que referência = verde, senão laranja).

### Gaps
- Nenhum pin ou overlay aberto mostrou as cores exatas em hexadecimal. As cores acima vêm de descrições textuais.

---

## Como diferenciar "você" e "referência" sem perder legibilidade

### Takeaway
A referência costuma ir como área translúcida, traço tracejado, outline ou cor neutra, enquanto o "você" fica em cor saturada e grossa. O projeto atual (faixa de 5 px com 40 %) segue essa lógica.

### Cited Findings
- O TinyPedal diz que seus widgets podem ser transparentes, mas a transparência não funciona no Linux sem composição de desktop. — [TinyPedal](https://github.com/TinyPedal/TinyPedal)
- O kruslim/racing-telemetry-visualiser compara a volta com a referência com os traços sobrepostos, contra a distância da pista. — [kruslim/racing-telemetry-visualiser](https://github.com/kruslim/racing-telemetry-visualiser)
- O kruslim mostra acelerador, freio, velocidade, volante e marcha, todos contra a volta de referência, mais uma curva de delta contra a distância percorrida. — [kruslim/racing-telemetry-visualiser](https://github.com/kruslim/racing-telemetry-visualiser)
- O bo2 usa laranja só no Spotter (barras aparecem quando há sobreposição lado a lado), ou seja, cor forte reservada para um estado específico. — [fixfactory/bo2-official-overlays](https://github.com/fixfactory/bo2-official-overlays)
- O Dash Overlay do bo2 usa caixas coloridas por categoria: verde para "ir mais rápido" (DRS, ERS), amarelo para combustível e pit, laranja para ajustes de carro, vermelho para freio e ABS. — [fixfactory/bo2-official-overlays](https://github.com/fixfactory/bo2-official-overlays)

### Inferences
- Manter a referência como área larga e translúcida é bom para ler o formato geral. Uma ideia extra é uma referência em linha tracejada ou pontilhada, que pode ser feita com retângulos pequenos (ou uma linha separada com cor de baixa opacidade). Isso separa o traço do ref do traço da área.
- Usar a cor forte (verde e vermelho) só para você, e neutro (branco ou cinza com opacidade) para a referência, mantém a semântica dos canais de pedal.
- Os dois pontos atuais no valor corrente funcionam bem como âncora. Um rótulo pequeno do valor (ex.: "100 %") ao lado do ponto fica legível sem ocupar espaço.

### Gaps
- Não foi possível medir contraste ou legibilidade real nas imagens.

---

## Widgets mínimos que condensam muita informação

### Takeaway
Os padrões que aparecem em overlays e guias de dashboard para pouco espaço são: barra de bullet (valor, alvo e faixas de fundo), sparkline, barra segmentada e ticks em arco. Quase tudo pode ser feito com linhas, retângulos e texto.

### Cited Findings
- O bullet graph foi criado por Stephen Few como substituto de gauges e medidores, que mostram pouca informação, ocupam muito espaço e têm decoração. Estrutura: barra fina com o valor, marcador de alvo e 2 a 3 faixas de fundo em tons de uma mesma cor. — [Bullet graph (Wikipedia)](https://en.wikipedia.org/wiki/Bullet_graph) e [Bullet Charts guide (Plotly)](https://plotly.com/blog/bullet-chart-guide/) (somente snippets de busca)
- Um guia de dashboards recomenda marcador de alvo fino e escuro, para não se confundir com a barra. — [Plotly, bullet charts](https://plotly.com/python/bullet-charts/) (snippet de busca)
- Um card de métrica pode ter sparkline pequena ao lado do valor, e a sequência Rótulo, Valor, Delta, Período deve ser igual em todos os cards. — [Tabler, sparklines](https://preview.tabler.io/sparkline.html) e [ELMNTL](https://elmntl.co/blog/modern-dashboard-ui-inspiration-for-designers-and-developers/) (snippets de busca)
- O RaceLab tem um "Fuel calculator" com leitura numérica, barra de tanque e contagem regressiva. — [RaceLab](https://racelab.app/)
- O Track Impulse mostra a janela de pit (ex.: voltas 21 a 25) em texto, com combustível restante e litros a colocar. — [Track Impulse](https://track-impulse.com/overlays)
- O RaceLab tem "Track strip": o grid inteiro por posição na volta, em linha horizontal, com placas de setor e gaps para carros próximos. — [RaceLab](https://racelab.app/)
- O bo2 tem "Spotter" com barras laterais laranjas, cujo tamanho representa a sobreposição e a velocidade de ultrapassagem. — [fixfactory/bo2-official-overlays](https://github.com/fixfactory/bo2-official-overlays)
- O RaceLab tem "Dashboard" com tacômetro em arco de 300 graus, marcha, velocidade, volante, pedais e G, em células modulares de barras e traço de inputs. — [RaceLab](https://racelab.app/)

### Inferences
Ideias concretas, todas feitas com linha, retângulo e texto:
1. **Delta centralizado no zero** dentro da caixa de telemetria, como uma barra de 6 px de altura, com cor de ganho ou perda diferente das cores de pedal.
2. **Traço de delta ao longo da volta** como segunda linha (ChartItem de histórico) com linha de zero fina, sobreposta ou em faixa abaixo do pedal.
3. **Faixa de setores** (3 a 10 blocos) no topo, com cor do último tempo comparado à referência.
4. **Marcador de posição na pista** (linha horizontal de 0 a 100 %, ponto para você e tick para o ref), que é um "track strip" simples sem mapa.
5. **Marcador de ponto de frenagem**: traço vertical fino na posição onde o freio começou no ref, comparado ao início atual. Calculado a partir do histórico.
6. **Sparkline de tempos de volta** (últimas 10 voltas) em um retângulo de 80 por 20 px.
7. **Barra bullet de combustível**: barra fina de quanto há no tanque, tick marcando quanto a corrida precisa, faixas de fundo cinza.
8. **Spotter em barras laterais**: retângulos verticais nas bordas que crescem quando há carro ao lado, em cor de alerta.
9. **Caixas de status por categoria** (DRS, ERS, ABS, balanço de freio) com cor de categoria, no estilo do Dash Overlay do bo2.
10. **Tacômetro em ticks**: arco de linhas curtas (ticks) em vez de preenchimento contínuo, com ticks mais longos a cada marco. Mantém leitura rápida e pouco pixel.
11. **Barra segmentada** para RPM ou pneus: retângulos pequenos separados por espaços, com o número de segmentos ativos. Ocupa pouco e lê bem em relance.

### Gaps
- Não foi confirmado se o ChartItem do SimHub aceita linha de zero ou faixas coloridas de fundo. Isso precisa ser testado no dash.
- Nenhum exemplo de sparkline ou bullet chart em pin do Pinterest foi visto.

---

## Ideias de evolução (resumo para o usuário)

Ordem sugerida, da mais barata à mais trabalhosa:
1. Delta centralizado no zero com número e cor diferente das de pedal (retângulos e texto).
2. Faixa de setores no topo da caixa (retângulos com cor por comparação).
3. Traço de delta como segunda linha no mesmo gráfico (ChartItem de histórico).
4. Barra de combustível estilo bullet e janela de pit em texto.
5. Caixas de status por categoria para o restante do dash.
6. Marcadores de ponto de frenagem no histórico (mais cálculo por fórmula).

Cuidado com a cor geral: verde e vermelho estão ocupados pelo acelerador e pelo freio. Reservar roxo apenas para dados de outros pilotos e usar neutro para a referência.

## Fontes lidas
- https://github.com/fixfactory/bo2-official-overlays (página lida)
- https://track-impulse.com/overlays (página lida)
- https://github.com/TinyPedal/TinyPedal (página lida)
- https://racelab.app/ (página lida)
- https://github.com/kruslim/racing-telemetry-visualiser (página lida; a fonte de detalhes de canais do traço foi o resumo da página)
- https://www.overtake.gg/downloads/bens-delta-overlay.65615/ (retornou 403; o detalhe veio só do snippet de busca)
- Snippets de busca usados como fonte de menor confiança: jamessanford/assetto-corsa-deltabar, SimracingBR-overlay, pitsngiggles, Turn Telemetry Dashboard, Tabler, ELMNTL, Plotly, Wikipedia (bullet graph).
- Não lidos com sucesso: Dribbble (tag telemetry, retorno vazio), todos os boards de Pinterest (conteúdo truncado).
