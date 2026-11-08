# Referências de estados por contexto, alertas e layouts adaptativos (HUD de corrida)

## Nota sobre o método e a fonte de descoberta

- **Pinterest não foi lido diretamente.** As tentativas de WebFetch em três boards/pins do Pinterest retornaram apenas placeholder ("[Content truncated due to length...]"), sem imagens nem descrições. As URLs de Pinterest abaixo vêm dos títulos e descrições dos resultados de busca (WebSearch), **não foram verificadas visualmente**. Trate-as como pistas para abrir manualmente no navegador.
- Os detalhes de design foram obtidos, sempre que possível, nas fontes originais (Matt Birkett, GitHub, fóruns, Overtake, GTPlanet). Quando o conteúdo veio só do snippet de busca (página não aberta ou com erro), isso está indicado.
- Foram usadas aproximadamente 15 chamadas de ferramenta.

---

## 1. Como os HUDs se adaptam por contexto (pit, largada, quali x corrida, bandeiras, última volta, combustível, dano)

### Takeaway
As referências mais úteis mostram um padrão: a tela de broadcast muda o **conteúdo de um painel fixo** conforme a sessão (intro, volta cronometrada, pit, safety car, fim de corrida), em vez de mostrar tudo sempre. Em HUDs de jogo, o padrão recorrente é o **elemento de estado** (nameplate, pit, bandeira) mudar de cor ou de posição, enquanto o restante permanece estável.

### Cited Findings
- A tela de broadcast da F1 (redesenho de Matt Birkett) muda o conteúdo da barra superior conforme o estado: contador de voltas ou cronômetro, bandeiras e mensagens de direção de prova; informações de Safety Car entram nessa barra. Uma caixa fixa no canto mostra a série (F1, F2 ou F3). — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- Estados de sessão descritos no mesmo projeto: tela de introdução no início da sessão; gráfico "Flying Lap" no canto inferior direito durante a volta cronometrada; dados de parada nos boxes aparecem na torre de tempos; SC aparece na barra de status; um pequeno ícone de DRS aparece na torre quando o piloto usa DRS; um símbolo de "sem dados" aparece num canto; ao fim da corrida, os três primeiros são destacados na torre. — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- A cor de destaque muda por série: vermelho na F1, azul-claro na F2, prata na F3. Dourado é reservado a gráficos de campeonato e rádio. — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- O redesenho da F1 para a era do efeito solo (2022) concentrou mudanças numa faixa vertical à esquerda da tela, abaixo do logo, e também atualizou introdução, grid de largada e elementos de pit stop. Não consegui abrir a página; só o snippet de busca está disponível. — [Motorsport.com, 2022](https://www.motorsport.com/f1/news/first-look-at-f1s-fresher-new-tv-graphics/9098527/) (502 ao abrir; snippet apenas)
- Em um HUD de jogo recriado em CSS (F1 TV, mundo 2021), cada piloto tem um estado de grid: `ontrack`, `inpit` ou `eliminated`. O estado altera o nameplate. — [bodzaital/f1-graphics-css](https://github.com/bodzaital/f1-graphics-css) (README aberto)
- Modelo de dados de bandeira de corrida (projeto de race control, PR): quadro de bandeira com estados amarela / VSC / SC / reinício, com instrução do que o piloto deve fazer, leitura de penalidade e zonas amarelas exibidas no minimapa. — [Beenster99/TDR PR #15](https://github.com/Beenster99/TDR/pull/15) (snippet de busca; página não aberta)
- Em um HUD baseado em estados de limitador de pit (iRacing, issue de dashboard), o estado depende da posição em relação à pit lane: limitador ligado dentro da pit = correto; ligado fora = erro; desligado dentro = risco de drive-through; ligado após sair da pit = perda de tempo. — [OpenDash issue #777](https://github.com/xorob0/OpenDash/issues/777) (snippet de busca; página não aberta)
- Um dashboard de SimHub para F1 24 (v1.1) mudou a UI do limitador e adicionou um aviso de "Slow Down", que aparece apenas se o piloto excede o delta de tempo sob (V)SC ou se, com limitador ligado, não está desacelerando o suficiente em relação ao limite. — [PFM21 F1 24 SimHub Dashboard](https://www.overtake.gg/downloads/f1-24-simhub-dashboard-by-pfm21.69728/) (snippet de busca)
- Um HUD de F1 em projeto de jogo de código aberto mostra o aviso de pit em unidade explícita, como "50 MPH LIMIT", quando a unidade não é km/h. — [brycejmurrin/f1-game PR #954](https://github.com/brycejmurrin/f1-game/pull/954) (snippet de busca)
- Na GT7 há reclamação recorrente de que as opções de HUD são limitadas e que desligar a maioria dos elementos também esconde os dados de combustível. — [GTPlanet, "Hud: Am I the only one?"](https://www.gtplanet.net/forum/threads/hud-am-i-the-only-one.410623/) (snippet de busca)
- Um mod de HUD para GT7 (Overtake) acrescenta uma exibição de combustível relacionada ao pit e um indicador de temperatura de pneu que avisa quando estão frios ou quentes demais, sinalizando que isso não existe no jogo original. — [Overtake GT7 HUD, updates](https://www.overtake.gg/downloads/gt7-hud.56420/updates) (snippet de busca)
- Um HUD de Assetto Corsa inspirado no GT tem interface adaptativa à proporção de tela (4:3 a 21:9) e permite personalizar elementos de UI. — [Vegetable Studio GT HUD](https://www.patreon.com/vegetable_studio/posts/gran-turismo-hud-156189061) (snippet de busca)
- Um HUD de Forza Motorsport 6 foi descrito por seu designer como "um equilíbrio entre entregar informação importante ao jogador e manter a imersão". A página não detalha quais elementos mudam por contexto. — [Abdul Al Hawasli, Forza 6](https://abdul.design/forza-6-xbox) (página aberta; sem detalhe de estados)
- Pedidos da comunidade de Forza (2023) pedem elementos movíveis, redimensionáveis e com opacidade ajustável, porque o HUD ocupa muito da tela e alguns elementos (tempo de diferença) sobrepõem o espelho da cabine. — [Forza forums, HUD item size and layout customization](https://forums.forza.net/t/hud-item-size-and-layout-customization/626905) (snippet de busca)

### Inferences
- Um padrão de "modo" fácil de implantar no dash: definir 4 a 5 estados (corrida normal, pit lane, largada/formação, bandeira ativa, fim de corrida) e, em cada um, trocar apenas um ou dois blocos (ex.: o bloco de LAPS/TO GO vira "voltas restantes + posição final" no último giro; o bloco de telemetria vira "limitador" na pit). Os exemplos de broadcast sustentam essa lógica de "painel fixo com conteúdo variável".
- O limitador de pit pode ter três ou quatro estados visuais combinando "dentro/fora da pit" e "limitador ligado/desligado", que é exatamente a combinação do exemplo do OpenDash. Isso é o caso mais claro de estado que depende de duas variáveis.
- A bandeira já ocupa a LED de status. A lógica de "quadro de instrução" (ex.: "AMARELA: sem ultrapassagem") pode entrar como banner curto no topo do overlay, sem tomar o restante da tela.
- Ver item de "Gaps" abaixo: não há fonte para a regra de quando uma área deve se reconfigurar, então a escolha de gatilhos é do projeto.

### Gaps
- Não encontrei fontes (Pinterest ou outras) com uma lista padronizada de quais elementos mudam em **qualificação**, **formação de largada** ou **dano**. A GT7 mostra dano, mas a fonte consultada descreve só efeitos de performance, sem UI de dano detalhada. — [Sportskeeda, GT7 car damage](https://sportskeeda.com/esports/is-car-damage-gran-turismo-7) (não aberta)
- Não há fonte oficial da Polyphony Digital sobre como a GT7 apresenta aviso de combustível. Só existem relatos de comunidade.
- Os boards de Pinterest identificados não puderam ser lidos. Não é possível afirmar o conteúdo dos pins.

---

## 2. Padrões de alertas e notificações em UI minimalista (banners, tomada de cor, bordas pulsantes, toasts) e intrusão

### Takeaway
Nas referências, o alerta mais comum é **uma faixa ou quadro fixo que recebe conteúdo temporário**, não um pop-up. A intrusão é controlada por duas regras: o alerta aparece só quando há ação a tomar (ex.: aviso de Slow Down) e o aviso não bloqueia a tela. Há reclamação explícita da comunidade sobre avisos muito intrusivos.

### Cited Findings
- Na broadcast da F1, a barra superior única recebe mensagens de direção de prova, informações de SC e batalhas. Ou seja, um único slot de alerta é reutilizado por tipos diferentes. — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- Em Raceroom, flags e mensagens de penalidade são listadas como elementos "essenciais" do HUD, que só podem ser desligados junto com todos os outros. Ou seja, alertas de segurança são tratados como não opcionais. — [Raceroom Wiki, HUD](https://raceroom.miraheze.org/wiki/HUD) (snippet de busca)
- O aviso de Slow Down do dashboard PFM21 só aparece em condição de erro (delta acima do esperado sob VSC, ou limitador ligado e velocidade acima do limite). Esse é um exemplo de alerta **condicional**, não permanente. — [PFM21 F1 24 SimHub Dashboard](https://www.overtake.gg/downloads/f1-24-simhub-dashboard-by-pfm21.69728/) (snippet de busca)
- Um jogador de GT7 afirmou que o aviso de combustível "precisa ser menos intrusivo"; outro previu que a Polyphony pode fazer mensagens de combustível bloquearem a maior parte da tela por uma ou duas voltas. A segunda frase é especulação, não fato. — [GTPlanet, GT7 HUD design](https://www.gtplanet.net/forum/threads/gran-turismo-7s-hud-design.394111/) e [GTPlanet, "Hud: Am I the only one?"](https://www.gtplanet.net/forum/threads/hud-am-i-the-only-one.410623/) (snippets de busca)
- Um HUD de F1 de projeto aberto usa uma tela de "race control" com instruções de ação ("o que você tem que fazer") para bandeiras, e destaca zonas amarelas no minimapa. — [Beenster99/TDR PR #15](https://github.com/Beenster99/TDR/pull/15) (snippet)
- Em um HUD de jogo, o estado "eliminado" muda o nameplate do piloto para um estado visual distinto, sem pop-up. — [bodzaital/f1-graphics-css](https://github.com/bodzaital/f1-graphics-css) (README aberto)
- Recursos de HUD de corrida em Pinterest (ex.: "Game UI: HUD", com classificação em HUD espacial, diegético e não diegético) mostram que a referência de "não diegético" é a camada de overlay que o dash ocupa. — [Pinterest, Game UI: HUD board (raf_silva)](https://de.pinterest.com/raf_silva/game-ui-hud/) (apenas título/descrição via busca; não verificado visualmente)

### Inferences
- Um padrão de alerta compatível com o dash atual: reservar **uma única área** (ex.: a faixa superior ou a LED de status) que muda de texto e cor para alertas temporários, com prioridade (bandeira > pit > aviso de combustível > informação). Isso evita um novo elemento a cada alerta.
- Alertas de erro (ex.: limitador fora da pit, delta de SC) devem ser **condicionais e temporários**, com duração curta. As fontes indicam que alertas permanentes são o problema apontado pelos usuários.
- Alertas de informação (LAPS, STINT, mensagens de rádio) podem ficar em um canal separado e mais discreto.
- Tomar a cor de um único elemento (ex.: a barra de OTS ou o quadro de gap) como sinal de alerta é menos intrusivo que tomar a tela inteira. Isso é uma inferência a partir da estrutura das referências, não uma regra documentada.

### Gaps
- Não encontrei referência com "toasts" (mensagens que aparecem e somem) em HUD de corrida com medição de intrusão. Os exemplos são de broadcast e de dashboards de SimHub.
- Não há fonte sobre bordas pulsantes ou tempo de exibição recomendado para alertas em HUD. A ideia de borda pulsante não foi confirmada por nenhuma fonte consultada.
- Não há dado de usabilidade sobre o nível de intrusão dos alertas (ex.: tempo de visualização, taxa de erro). Só há opiniões de comunidade.

---

## 3. Padrões para gaps e batalhas de forma compacta (tendência de gap, setas, indicador de batalha)

### Takeaway
As fontes não trazem um padrão específico de **tendência de gap com seta** em HUD de jogo. O que há é (a) a torre de tempos da broadcast mostrar "batalhas, gaps e mudanças de posição" como visões configuráveis, e (b) um indicador de "batalha" na barra de status. Para o dash, a tendência (subindo/descendo) é uma decisão de design do projeto, sem referência direta.

### Cited Findings
- Na broadcast da F1, a torre de tempos pode ser configurada pelo diretor para mostrar dados individuais, **batalhas, gaps, mudanças de posição** ou paradas. Isso indica que gap e batalha são visões diferentes sobre o mesmo bloco. — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- Gráficos de batalha aparecem dentro da barra de status da broadcast (não numa área própria). — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- Na broadcast, a caixa de posição de um piloto fica **azul quando ele está sendo doblado** (lapped: o líder completa uma volta a mais sobre ele). Aqui a cor de posição sinaliza uma relação com outro carro, não o próprio tempo. — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- No HUD da Forza Motorsport (2023), a comunidade reclamou que o tempo de diferença fica por cima do espelho lateral na visão de cabine. — [Forza forums](https://forums.forza.net/t/hud-item-size-and-layout-customization/626905) (snippet)
- Em uma busca por "racing HUD" no Pinterest, o board "HUD racing" (toni0771) e o pin "In Game HUD" (191473421631049514) aparecem como pistas de referência; não verificados. — [Pinterest, HUD racing](https://es.pinterest.com/toni0771/hud-racing/), [Pinterest, In Game HUD](https://www.pinterest.com/pin/191473421631049514/) (apenas título/descrição via busca)

### Inferences
- Como o layout de broadcast separa "gap" (medida de tempo) de "batalha" (relação de posição), a sugestão para o dash é manter as duas leituras em campos distintos, mesmo que compactos: um número de gap e, separadamente, um marcador de relação (ex.: cor ou ícone quando há carro dentro de 1 s).
- A tendência (subindo/descendo) pode ser calculada por uma comparação simples do gap atual com o gap de alguns segundos antes. Isso é uma inferência de implementação; não há fonte de Pinterest que mostre essa técnica.
- O bloco de mini relative (2 à frente, 2 atrás) já tem a forma de torre curta. Uma seta ou variação de cor no próprio bloco é compatível com a leitura de broadcast, mas não há referência específica que valide o formato.

### Gaps
- **Não encontrei nenhuma referência sobre setas de tendência de gap, nem indicadores de "battle" com ícone, em HUD de jogo ou broadcast.** Os exemplos encontrados são descrições textuais ("battle graphics" na barra de status), sem imagem nem regra de exibição.
- Não há fonte sobre a distância de limiar de batalha (ex.: 1 s, 2 s) usada em broadcast ou em jogos.
- Os pins de Pinterest sobre HUD de corrida não puderam ser lidos.

---

## 4. Como a broadcast mostra mudança de posição, volta mais rápida (roxo), melhor volta pessoal (verde) e cores de setor

### Takeaway
A convenção de setor é consistente entre F1 e WEC: **roxo = melhor da sessão**, **verde = melhor pessoal (do próprio piloto)**, **amarelo = mais lento que o próprio melhor**, **branco ou cinza = ainda não há tempo confirmado**. A nuance mais importante vem do WEC: o roxo de volta é o mais rápido entre todas as classes, então o líder de uma classe pode mostrar verde mesmo sendo o melhor da sua classe.

### Cited Findings
- Na broadcast da F1, cada piloto tem três barras de setor ao lado do nome e do tempo de volta. Verde = melhor pessoal; amarelo = setor mais lento; roxo = melhor da sessão. — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- Em um guia de transmissão ao vivo das 24 Horas de Le Mans (WEC): setor em verde = o carro melhorou o próprio melhor naquele setor; roxo = referência da sessão (o mais rápido da sessão para aquele setor); a volta roxa é a mais rápida entre todas as classes. — [24h-lemans.com, live timing guide](https://www.24h-lemans.com/en/news/live-timing-at-the-24-hours-of-le-mans-a-handy-guide-59698) (snippet de busca; página não aberta)
- O mesmo guia do WEC indica que tempos não validados aparecem em cinza e tempos confirmados em branco. — [24h-lemans.com, live timing guide](https://www.24h-lemans.com/en/news/live-timing-at-the-24-hours-of-le-mans-a-handy-guide-59698) (snippet)
- Explicações genéricas de F1 concordam com a convenção e afirmam que, quando um piloto faz um novo melhor de sessão em um setor, o detentor anterior do roxo perde a cor e passa a verde. — [The Field F1, sector colours](https://www.thefieldf1.com/charts/sector-colours) (snippet; página não aberta)
- Na broadcast da F1, o gráfico "Flying Lap" lista os pilotos em volta rápida na ordem em que cruzam a linha, e cada um aparece também no mapa da pista. — [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/)
- Um pin de "Broadcast Graphics" (162551867784321876) foi retornado na busca de F1; não verificado. — [Pinterest pin](https://www.pinterest.com/pin/162551867784321876/) (apenas título via busca)

### Inferences
- Para o dash com OTS, LAPS e telemetria, a mesma convenção pode ser aplicada à **última volta** (ex.: última volta em verde se for melhor pessoal, roxa se for melhor de sessão), e um número de setor pode mudar de cor com a mesma regra.
- Para o caso de "mudança de posição" no broadcast, a referência disponível é a cor da caixa de posição (azul = relação de volta). Não há regra de "subiu/desceu" com cor específica, então o dash pode usar um flash de posição (verde/vermelho) como escolha de projeto, com base na lógica de cor de estado já usada.
- A distinção "melhor de classe x melhor de sessão" é relevante se o dash mostrar classificações multi-classe (ex.: GT3 com GT4). Para uma sessão de classe única, a regra simplifica para "melhor pessoal x melhor da sessão".

### Gaps
- Não encontrei fonte com regra explícita de **flash de subida/descida de posição** (cor ou animação) na broadcast. A fonte disponível só descreve a caixa azul para volta.
- O guia do WEC foi lido apenas pelo snippet; os detalhes de cor do IMSA não foram encontrados (não há guia de IMSA publicado nas fontes consultadas).
- Não há fonte sobre o tempo de exibição de "roxo" (quanto tempo a cor persiste antes de virar verde/amarelo).

---

## Resumo de ideias para o dash (a partir das fontes acima)

Ordenado do mais sustentado pelas fontes para o menos sustentado:

1. **Estado por sessão com painel fixo** (sustentado por Matt Birkett): manter os blocos, trocar conteúdo por estado (corrida, pit, bandeira, fim de corrida).
2. **Uma área de alerta reutilizada, com prioridade** (sustentado por Matt Birkett e pela regra de SC na barra de status): bandeira, pit, combustível, em ordem.
3. **Alertas condicionais, não permanentes** (sustentado pelo Slow Down do PFM21 e pela crítica da comunidade GT7).
4. **Limitador de pit com estados combinados por posição** (sustentado pelo OpenDash, em iRacing): dentro/fora da pit x limitador ligado/desligado.
5. **Convenção de cores de setor e de volta** (sustentada por Matt Birkett e pelo guia do WEC): roxo/verde/amarelo/cinza, com a regra de "melhor da classe x melhor da sessão" se houver multi-classe.
6. **Gap e batalha em campos separados** (inferência a partir da torre de broadcast; sem referência visual de seta de tendência).
7. **Combustível e pneus conforme o contexto** (sustentado pelo mod GT7 e pelo pedido de comunidade para mostrar dados sob demanda; sem padrão oficial).

## Pinterest: lista de URLs encontradas (não verificadas visualmente)

- https://www.pinterest.com/pin/racing-game-hud-and-ui-icons--783415297701244694/ (ícones de HUD de corrida; leva a gamedeveloperstudio.com, segundo a descrição)
- https://www.pinterest.com/moody3d/race-ui/ (board "Race UI", com ideias de Forza Horizon e Forza Motorsport)
- https://www.pinterest.com/pin/191473421631049514/ (pin "In Game HUD", descrito como HUD de direção com indicadores de veículo)
- https://de.pinterest.com/raf_silva/game-ui-hud/ (board "Game UI: HUD", com classificação espacial, diegética e não diegética; cita Forza Motorsport 4)
- https://es.pinterest.com/toni0771/hud-racing/ (board "HUD racing")
- https://www.pinterest.com/ideas/esports-scoreboard-overlay/905449650211/ (ideias de overlay de placar de esports; sem imagem legível)
- https://www.pinterest.com/hanmerdesign/motorsport-graphics/ (board de gráficos de motorsport, com livrés; pouco útil para HUD)
- https://www.pinterest.com/pin/162551867784321876/ (pin de "Broadcast Graphics")
- https://uk.pinterest.com/hudmotorsports/hud-motorsports/ (board de uma equipe real de motorsport, não de HUD de jogo; descartar)

Pinterest, pelo que foi possível verificar, é um canal de descoberta fraco para este tema: os boards são curados por usuários e as páginas não puderam ser lidas. As fontes com detalhe útil vieram de sites de design e de comunidades de sim racing.

## Fontes originais (ordenadas por utilidade para o tema)

- [Matt Birkett, F1 TV Graphics](http://mattbirkett.co.uk/wp/project/f1-tv-graphics/) (página aberta; a mais útil)
- [24h-lemans.com, guia de timing do WEC](https://www.24h-lemans.com/en/news/live-timing-at-the-24-hours-of-le-mans-a-handy-guide-59698) (snippet)
- [PFM21, F1 24 SimHub Dashboard](https://www.overtake.gg/downloads/f1-24-simhub-dashboard-by-pfm21.69728/) (snippet)
- [OpenDash issue #777](https://github.com/xorob0/OpenDash/issues/777) (snippet; iRacing)
- [Beenster99/TDR PR #15](https://github.com/Beenster99/TDR/pull/15) (snippet)
- [bodzaital/f1-graphics-css](https://github.com/bodzaital/f1-graphics-css) (README aberto)
- [brycejmurrin/f1-game PR #954](https://github.com/brycejmurrin/f1-game/pull/954) (snippet)
- [Raceroom Wiki, HUD](https://raceroom.miraheze.org/wiki/HUD) (snippet)
- [GTPlanet, "Hud: Am I the only one?"](https://www.gtplanet.net/forum/threads/hud-am-i-the-only-one.410623/) (snippet)
- [Overtake GT7 HUD, updates](https://www.overtake.gg/downloads/gt7-hud.56420/updates) (snippet)
- [Forza forums, HUD item size and layout customization](https://forums.forza.net/t/hud-item-size-and-layout-customization/626905) (snippet)
- [Abdul Al Hawasli, Forza 6](https://abdul.design/forza-6-xbox) (página aberta; pouco detalhe)
- [Motorsport.com, redesenho de gráficos da F1 (2022)](https://www.motorsport.com/f1/news/first-look-at-f1s-fresher-new-tv-graphics/9098527/) (não abriu, erro 502)
- [Vegetable Studio, GT HUD (AC)](https://www.patreon.com/vegetable_studio/posts/gran-turismo-hud-156189061) (snippet)

## Lacunas gerais

- Pinterest não pôde ser lido (conteúdo vazio nos fetches). Nenhuma referência visual foi analisada diretamente.
- Não há fonte sobre setas de tendência de gap, indicador de batalha com ícone, toasts ou borda pulsante em HUD de corrida.
- Não há padrão documentado para HUD de qualificação, formação de largada ou dano.
- IMSA: não encontrei guia de timing publicado.
- Os detalhes de cor do WEC e da F1 vêm de snippets e de um projeto de design; uma checagem contra os guias oficiais das séries é recomendada antes de usar as cores como regra.
