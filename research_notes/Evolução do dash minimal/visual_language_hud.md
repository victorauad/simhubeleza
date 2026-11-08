# Linguagem visual de clusters e HUDs minimalistas (referências Pinterest e fontes originais)

Aviso de método: o Pinterest quase não se deixou ler. As páginas de pins e boards retornaram apenas placeholders ("[Content truncated due to length...]"), e os boards foram acessados só pelos títulos, contagens e descrições que o buscador expõe. Nenhuma imagem foi vista. Os Dribbble e Behance abertos também voltaram vazios ou com 403, então grande parte do que segue vem de snippets de busca. Onde a ideia é inferência minha sobre o dash, está marcada como tal. Nada aqui foi validado visualmente.

## Como o Pinterest foi tratado

Boards que aparecem nas buscas, com contagem de pins quando exposta:

- [Car HUD and car dashboard interface ideas (56)](https://www.pinterest.com/ryandamico9/car-hud/)
- [Car HUD Design (95 pins, criado em 2018)](https://uk.pinterest.com/barrymccalvey/car-hud-design/), com temas de velocímetro em modo escuro
- [Concept Car UI (16)](https://au.pinterest.com/hudsandguis/concept-car-ui/), com clusters de concept cars (Kia EV7, Renault Twin Run)
- [Dark Modern UI Design (19)](https://www.pinterest.com/juannoguerol/dark-modern-ui-design/)
- [Instrument Cluster GUI Designs (100, 2026)](https://www.pinterest.com/tyronejohnsonjr/instrument-cluster-gui-designs/)
- [Race UI (21)](https://www.pinterest.com/moody3d/race-ui/), que cita um pin de analytics de telemetria de equipe de F1
- [Racing UI (25, em pt-BR)](https://br.pinterest.com/viniciuskastro/racing-ui/)
- [In-Vehicle HMI + HUD](https://www.pinterest.com/dandy_clancy/in-vehicle-hmi-+-hud/)
- [Digital instrument clusters (13)](https://www.pinterest.com/kalicreature/digital-instrument-clusters/), com muitos clusters de aftermarket (Koso, Trail Tech)

Pins individuais com metadados úteis:

- [EV Charging Station Dashboard Concept](https://www.pinterest.com/pin/ev-charging-station-dashboard-concept-in-2023--19210735903401279/), credita Vektora UIUX e origem no Dribbble
- [Digital instrument cluster (Nagaraj)](https://in.pinterest.com/pin/digital-instrument-cluster-design-by-nagaraj--424886546090843675/), origem em Dribbble
- [12 inch cluster, modo Normal com acentos MyColor](https://br.pinterest.com/pin/713539134695155203/), uma foto de produto e não um concept

Conclusão sobre o Pinterest: serve para descoberta de nomes de designers e de origem. Para análise, é preciso abrir cada referência no navegador (ou usar a extensão de navegador) e capturar as imagens. Não dá para depender dele como fonte de dados neste ambiente.

## Pergunta 1: tipografia dos números e unidades

### Takeaway
As referências de cluster minimalista tratam o número principal como o único elemento grande e deixam tudo o mais em tamanho pequeno e uniforme. Não encontrei detalhe tipográfico verificável em fonte primária. A ideia mais útil para o dash é tratar a unidade e o rótulo como uma terceira camada tipográfica, separada do número.

### Cited Findings
- As fontes de cluster de Porsche descritas na imprensa usam uma leitura de alto contraste e ordenada, com poucos elementos. [The Drive](https://www.thedrive.com/news/why-porsches-digital-gauges-are-better-than-everyone-elses); [Porsche Newsroom, Typically Porsche](https://newsroom.porsche.com/en_US/products/typically-porsche-18676.html)
- A tipografia exata usada pela Porsche não foi publicada nas fontes que consultei. Fica como lacuna. [Porsche Newsroom](https://newsroom.porsche.com/en_US/products/typically-porsche-18676.html)
- Um blog de design de cluster afirma que ponteiros analógicos comunicam por forma e movimento melhor do que números e texto, e que os ícones de alerta regulamentados ocupam espaço considerável. [The Turn Signal Blog](https://www.theturnsignalblog.com/the-problem-with-digital-instrument-clusters-and-how-to-design-a-better-one/)
- Google, nas diretrizes Design for Driving, afirma que texto de alta legibilidade reduz o tempo de cada olhar e de cada decisão, e que cadeias longas de texto aumentam a distração. [Google Design for Driving, Visual principles](https://developers.google.com/cars/design/design-foundations/visual-principles) (só o snippet foi lido)
- Texto de HMI em movimento: blogs citam 5,3 a 6 mm de altura mínima, a 60 cm de distância. Um estudo de simulador sugere que tamanhos abaixo de cerca de 6,5 mm aumentam o número e a duração dos olhares. Essas cifras aparecem repetidas e podem vir de uma origem só. [Embitel](https://www.embitel.com/iot-insights/automotive-human-machine-interfaces); [MDPI, Chinese text size study](https://www.mdpi.com/2076-3417/15/16/8874). Não tratam de cluster de corrida e precisam ser checadas na norma.

### Inferences
- Para o dash, a hierarquia atual (176/44/30/16/11) já segue o padrão de número grande, leitura média e rótulo pequeno. Uma melhoria possível é tratar unidades (km/h, RPM×1000) como uma camada própria: mesma família, tamanho próximo de 16 px, caixa-alta e espaçamento entre letras aberto (algo como 0,08 a 0,12 em), alinhadas pela linha de base do número. Isso separa o valor da unidade sem criar um novo tamanho de fonte.
- Se a fonte de número não for tabular, usar `font-variant-numeric: tabular-nums` evita o salto horizontal ao trocar dígitos. Arame Mono já é monoespaçada, então este ponto só vale para as demais fontes do dash (Funnel Sans).
- Zeros à esquerda e marcadores de posição (por exemplo, a marcha neutra "N") podem ficar em opacidade reduzida. Isso enfatiza o valor real sem trocar de fonte.

### Gaps
- Não encontrei nenhuma fonte primária com especificação tipográfica de cluster de corrida ou minimalista. Os designs de Pinterest e Dribbble não puderam ser lidos.
- Não consegui confirmar as fontes de Porsche, BMW ou de qualquer concept.
- Não verifiquei a norma primária (ISO 15005, ISO 15008) sobre altura mínima de caracteres.

## Pergunta 2: sistema de cor, tiers de opacidade e cores de estado

### Takeaway
As referências consultadas descrevem paletas restritas, fundos escuros para dirigir à noite e um único acento para estados. Não consegui extrair valores hexadecimais de nenhuma delas. A lógica de opacidade em camadas, que serve bem ao dash, é inferência minha.

### Cited Findings
- Porsche: paleta restrita, fundos escuros para uso noturno e formas de medidor emprestadas do 911 clássico. Confirmado apenas em resumo de imprensa. [DAX Street](https://daxstreet.com/list/285202/5-cars-with-clear-gauges-vs-5-with-cluttered-clusters/); [Porsche Newsroom](https://newsroom.porsche.com/en_US/products/typically-porsche-18676.html)
- Dribbble "Digital Car Dash: HMI & Cluster UI" (Thomas Moeller, ZeroSixty): fundo quase preto com acento azul, segundo o snippet. Não consegui abrir a página para ver os valores. [Dribbble](https://dribbble.com/shots/16235798-Digital-Car-Dash-HMI-Cluster-UI)
- Dribbble "Bright and minimal vehicle instrument cluster" (John Finnegan): tom claro. Útil como contraste, não como modelo para este dash. [Dribbble](https://dribbble.com/shots/11228180-Bright-and-minimal-vehicle-instrument-cluster)
- Behance "UX/UI Design of Digital Instrument Cluster" (Timotius Petrus): o cluster permite trocar cores e estilos, e vai de minimalista a tradicional. Não consegui abrir a página (403). [Behance](https://www.behance.net/gallery/52933375/UXUI-Design-of-Digital-Instrument-Cluster)
- Diretrizes de HMI: modo escuro é geralmente preferido por reduzir distração e ofuscamento, exceto em navegação, onde o modo claro melhora a leitura. [Google Design for Driving](https://developers.google.com/cars/design/design-foundations/visual-principles) (snippet)
- No Mercedes-AMG e no Williams, as luzes de troca de marcha ficam acima da tela central e acendem em verde, depois amarelo, depois vermelho. Fontes de 2019 e anteriores; não encontrei especificação de 2026. [Mercedes-AMG PETRONAS F1](https://www.mercedesamgf1.com/news/how-does-an-f1-steering-wheel-work); [Motorsport.tech, Williams FW43](https://motorsport.tech/formula-1/master-control-understanding-the-williams-fw-43-steering-wheel)

### Inferences
- Tiers de opacidade sobre um único neutro (por exemplo, texto principal em 100%, secundário em cerca de 60%, terciário em cerca de 35%) permitem hierarquia sem introduzir mais cores. No dash, os 92% de fundo já estão no mesmo espírito.
- Reservar o roxo exclusivamente para o ponto de troca faz dele um sinal único. Se o roxo também aparecer em outro estado, a leitura de "hora de trocar" enfraquece. Este ponto é inferência a partir do desenho atual, não de uma referência.
- Os estados de RPM (verde, amarelo, vermelho) são, na prática, uma escala de intensidade. Vale testar se o vermelho do freio e o vermelho do último LED de RPM são lidos como o mesmo sinal. Se forem, uma das duas cores pode mudar para evitar confusão.
- Acento único com tom desaturado sobre fundo quase preto reduz ruído visual. Isso é consistente com as referências escuras, mas não foi comprovado por nenhuma delas.

### Gaps
- Nenhum hexadecimal confirmado de nenhuma referência.
- Não encontrei estudo que compare sistemas de cor de cluster com desempenho de olhar.
- Os dados sobre dirigir à noite vêm de resumos, não de estudo primário.

## Pergunta 3: forma, geometria e detalhes de linha

### Takeaway
Os clusters de Porsche e as referências de concept mantêm arcos e medidores de formas clássicas, com pouca ornamentação. Para o dash, a principal oportunidade é tratar a linha (divisores, marcas, traço fino) como um vocabulário próprio, sem depender de blur ou de brilho.

### Cited Findings
- Porsche: no 992.2 911, o cluster digital posiciona os medidores externos em semicírculo para que todos os cinco apareçam. Um porta-voz afirmou que layouts totalmente customizáveis podem distrair, e por isso manteve o arranjo tradicional. [The Autopian](https://www.theautopian.com/its-time-everyone-stopped-freaking-out-over-the-new-porsche-911s-digital-gauge-cluster/); [The Drive](https://www.thedrive.com/news/why-porsches-digital-gauges-are-better-than-everyone-elses)
- Porsche: a alternância entre layout de cinco e de três medidores é uma escolha de design, não só de configuração. [The Drive](https://www.thedrive.com/news/why-porsches-digital-gauges-are-better-than-everyone-elses)
- Uma referência de Dribbble (Nagaraj) e vários boards de Pinterest mostram clusters de aftermarket com LEDs segmentados em arco. Os títulos não permitem ver se usam tiques, divisores ou traço fino. [Pinterest, Nagaraj](https://in.pinterest.com/pin/digital-instrument-cluster-design-by-nagaraj--424886546090843675/)

### Inferences
- Segmentos de LED sem traço de fundo ficam mais limpos, mas o arco "apagado" some. Um segmento apagado com opacidade muito baixa (algo perto de 8% do acento) mantém a forma completa do arco visível sem poluir. Esta é uma sugestão a testar.
- Marcas finas entre segmentos ou no ponto de troca dão leitura de escala sem texto. Devem ser de 1 px e em opacidade baixa.
- Divisores de 1 px com opacidade de 10 a 15% separam blocos sem caixas pesadas. Combinam com o raio de 3 px das barras, criando dois raios no sistema (cápsula para o contêiner, 3 px para as barras). Vale confirmar que a diferença é intencional e não um desalinhamento.
- Para profundidade sem blur, opções compatíveis com a restrição: contraste em camadas de opacidade (fundo 92%, bloco ativo a 100%), uma linha de 1 px com opacidade mais alta só na borda superior, e sombra sólida sem raio de desfoque. Efeitos de "glow" feitos com `box-shadow` com desfoque, `filter` ou `backdrop-filter` não se aplicam, pois o dash os proíbe.

### Gaps
- Não encontrei referência com geometria de arco documentada em medidas.
- Não verifiquei se o raio de 3 px é usado em outras referências de cluster.

## Pergunta 4: movimento e transições de estado

### Takeaway
A única referência de movimento com base em fonte primária é a norma de distração (olhares curtos). O movimento para troca de marcha e alerta precisa ser limitado a poucos hertz e sem ruído. A recomendação de frequência de flash vem de diretriz de acessibilidade, não de cluster.

### Cited Findings
- Diretriz de glanceability citada por blogs: cerca de 1,5 s por olhar e no máximo cerca de 12 s de desvio acumulado para completar uma tarefa, atribuídos a ISO 15005 e NHTSA. Um dos blogs cita um limite mais rígido, de 2 s. Não verifiquei a norma. [Embitel](https://www.embitel.com/iot-insights/automotive-human-machine-interfaces); [MDPI, Design of Automotive HMI](https://www.mdpi.com/2076-3417/15/10/5572)
- Google Design for Driving: pouco texto, uma ação primária e poucas secundárias. [Google Design for Driving](https://developers.google.com/cars/design/design-foundations/visual-principles) (snippet)
- Porsche: o cluster oferece modos (por exemplo, Classic com medidores e modo mapa que troca os medidores por navegação). Trocas de modo são um momento de transição, não só de estado. [Porsche Taycan HMI, hmi.gallery](https://www.hmi.gallery/hmi/porsche-taycan-hmi-design)
- Na F1, a troca de marcha é apoiada por luzes visuais e, em alguns carros, por um alerta sonoro no capacete. A redundância é a regra. [Motorsport.tech, Williams FW43](https://motorsport.tech/formula-1/master-control-understanding-the-williams-fw-43-steering-wheel)

### Inferences
- Limitar o piscar do roxo a no máximo 3 flashes por segundo. Isso segue a diretriz WCAG 2.3.1 (limiar de flash, aplicado aqui por cautela). Se o piscar atual for mais rápido, reduzir a frequência ou trocar por uma transição de preenchimento.
- Para troca de marcha, usar troca instantânea ou transição de no máximo cerca de 80 ms. Animar o número grande gera ruído toda vez que muda.
- Para mudanças de modo (por exemplo, alternar entre telemetria e mini-relativo), uma varredura de hairline de 1 px no topo ou na base é suficiente. Não exige animação de conteúdo.
- Um alerta de estado (pneu, combustível, bandeira) deveria ter uma faixa dedicada, como o Porsche faz com o painel abaixo do display. Isso evita que o alerta divida espaço com os medidores.
- Redundância: o dash tem o shift light na parte visual. Se o usuário quiser um alerta sonoro, isto está fora deste escopo, mas vale manter a informação de troca em mais de um canal quando possível.

### Gaps
- Nenhuma referência de cluster com medição de movimento, duração ou frequência.
- Os valores de olhar são de blogs, não da norma.

## Pergunta 5: detalhes que dão sensação de acabamento sem blur

### Takeaway
Acabamento premium em referências escuras vem de consistência de espaçamento, hierarquia de opacidade e poucos detalhes repetidos. Nenhuma referência consultada entrou em detalhe suficiente para citar. As ideias abaixo são inferências a partir das perguntas anteriores.

### Cited Findings
- Porsche: o cluster mantém o layout de medidores de referência do 911 em vez de liberar a customização total, justificando que o layout familiar reduz distração. [The Autopian](https://www.theautopian.com/its-time-everyone-stopped-freaking-out-over-the-new-porsche-911s-digital-gauge-cluster/)
- Dribbble "Car Dashboard UI Concept" listado como limpo, escuro e minimalista. Não consegui abrir a página. [Dribbble, car-ui-dashboard](https://dribbble.com/search/car-ui-dashboard)
- Dribbble "Design for a minimal digital instrument cluster for cars" (listado em tag de instrument cluster, sem autor identificado no snippet). [Dribbble, instrument-cluster](https://dribbble.com/tags/instrument-cluster)
- Behance "BMW Car Dashboard Design" (Denys Nevozhai): objetivo declarado de manter a identidade BMW tornando o cluster moderno e usável. Não consegui abrir a página. [Behance](https://www.behance.net/gallery/12354511/BMW-Car-Dashboard-Design)

### Inferences
- Unidades e rótulos com o mesmo espaçamento entre letras, alinhados pela linha de base, parecem mais finos do que rótulos centralizados.
- Zeros à esquerda e a marcha neutra em opacidade reduzida dão ritmo sem adicionar elementos.
- Uma marca fina de 1 px em torno de cada bloco ativo (por exemplo, o bloco do lap counter) cria destaque sem brilho.
- Manter todo o conjunto em pouquíssimos valores de raio, opacidade e espessura. A consistência reduz a sensação de "tela de jogo" e aumenta a de produto.
- Não usar sombras de desfoque, gradientes de brilho ou textura. Essas são o tipo de detalhe que as referências de concept usam, e que o dash proíbe.

### Gaps
- Nenhum design de referência foi lido em detalhe. A lista de detalhes acima não tem prova visual.
- Não consegui identificar exemplo de cluster de corrida com acabamento premium que use somente recursos sem blur.

## Referências de fonte primária que valem abrir manualmente

Como os Pinterest e vários Dribbble/Behance não puderam ser lidos aqui, estas são as páginas que mais valem uma olhada humana:

- [Dribbble, Digital Car Dash HMI Cluster UI (Thomas Moeller)](https://dribbble.com/shots/16235798-Digital-Car-Dash-HMI-Cluster-UI): fundo escuro com acento azul, segundo o snippet
- [Dribbble, Bright and minimal vehicle instrument cluster (John Finnegan)](https://dribbble.com/shots/11228180-Bright-and-minimal-vehicle-instrument-cluster): contraste de tom claro
- [Dribbble, tag Instrument Cluster](https://dribbble.com/tags/instrument-cluster): "Design for a minimal digital instrument cluster for cars"
- [Behance, UX/UI Design of Digital Instrument Cluster (Timotius Petrus)](https://www.behance.net/gallery/52933375/UXUI-Design-of-Digital-Instrument-Cluster): troca de estilo, minimal a tradicional
- [Behance, BMW Car Dashboard Design (Denys Nevozhai)](https://www.behance.net/gallery/12354511/BMW-Car-Dashboard-Design)
- [The Turn Signal Blog, The Problem With Digital Instrument Clusters](https://www.theturnsignalblog.com/the-problem-with-digital-instrument-clusters-and-how-to-design-a-better-one/): crítica sobre espaço de alerta e leitura por forma
- [Google Design for Driving, Visual principles](https://developers.google.com/cars/design/design-foundations/visual-principles): diretriz primária de legibilidade e modo escuro
- [MDPI, Design of Automotive HMI (2024)](https://www.mdpi.com/2076-3417/15/10/5572): revisão acadêmica, a ser checada

## Limitações gerais

- O Pinterest não foi lido em nenhum pin ou board com conteúdo. Todas as referências dele são de metadados.
- Dribbble e Behance também foram lidos apenas por snippet: as páginas abertas voltaram vazias ou com 403.
- Fontes de F1 têm 2019 a 2023 como base. Não há confirmação de regras de 2026.
- O conjunto de inferências é minha leitura do dash descrito pelo usuário. Não vi o dash renderizado.
- Os valores de distância e altura mínima são de blogs e de estudos de simulador, não de norma primária.
