# Referências de dashboards de sim racing e volante de F1 (Pinterest como fonte)

## Acesso ao Pinterest: resultado da pesquisa

### Takeaway
O Pinterest não pôde ser usado como fonte. A busca web não indexou pins, e a tentativa de abrir a página de busca do Pinterest voltou sem conteúdo utilizável. Não há nenhum URL de pin nem de board nesta nota. As ideias abaixo vêm de fóruns, lojas, notícias e páginas de produto, com links para cada fonte.

### Cited Findings
- Buscas em inglês por "pinterest sim racing dashboard UI", "pinterest F1 steering wheel display UI", "pinterest racing HUD UI minimal" e "pinterest simhub dash overlay" não retornaram nenhum resultado do Pinterest. — [Busca web (resultados sem domínio pinterest.com)](https://racedepartment.com/threads/sim-dashboard.135875/)
- A página de busca `pinterest.com/search/pins/?q=sim racing dashboard` retornou apenas o nome do site, truncado, sem pins. — tentativa de leitura direta, sem URL de fonte.
- Uma referência de designer de HUD afirma que Pinterest, Behance e Dribbble "não ajudam muito" para HUDs voltados ao piloto. Isso aparece apenas como resumo de resultado de busca, sem leitura da página original. — [Busca web (resumo de resultado)](https://contra.com/p/FgcAeElX-uiux-design-for-mobile-racing-game)

### Inferences
- Para inspiração visual real de pins, a pesquisa precisa ser feita manualmente no Pinterest, com termos como "sim racing cockpit display", "F1 steering wheel display", "racing telemetry UI" ou "SimHub dash". Este agente não conseguiu acessar essa fonte.

### Gaps
- Nenhum pin ou board do Pinterest foi visto, então nenhuma referência de estilo ou layout daquela plataforma está documentada aqui.

---

## Quais informações outros dashboards mostram que o seu ainda não mostra

### Takeaway
Os exemplos mais concretos vêm do volante real de F1 e de hardware comercial (MOZA). Eles mostram delta, brake bias, diferencial, fuel mix e estados de energia em páginas separadas. Isso sugere que o dash pode ganhar uma ou duas páginas alternativas, e não apenas mais elementos na cápsula.

### Cited Findings
- Volantes de F1 atuais usam um display central com muitas páginas, e o piloto alterna entre elas durante a volta. A Autosport cita que o display PCU-8D pode ter "até 100 páginas" customizáveis, mas não detalha como elas são navegadas. — [Autosport: why customised controls are vital](https://www.autosport.com/f1/news/f1-steering-wheels-why-customised-controls-are-vital-to-drivers/10593869/)
- Na mesma matéria, o exemplo citado é a troca do botão de DRS por um ajuste de brake balance quando um piloto usa o volante de outro. Isso mostra que o controle de bias é uma função que pilotos realmente usam. — [Autosport](https://www.autosport.com/f1/news/f1-steering-wheels-why-customised-controls-are-vital-to-drivers/10593869/)
- Resumos de buscas sobre volantes de F1 dizem que páginas típicas incluem fuel mix, ERS mode, brake bias e diff, e que o delta de volta aparece com sinal de menos quando o carro está mais rápido e de mais quando está mais lento. Esses resumos não foram verificados página a página. — [F1 Chronicle: Driver Inputs in 2026](https://f1chronicle.com/f1-driver-inputs-steering-wheel-2026); [PlanetF1: F1 delta explained](https://www.planetf1.com/news/f1-delta-explained-different-contexts-meanings)
- Para 2026, um resumo cita estado de carga da bateria, número de ativações restantes de overtake override, modo aerodinâmico, lap delta e avisos. — [F1 Chronicle](https://f1chronicle.com/f1-driver-inputs-steering-wheel-2026) (resumo de busca, não verificado na página)
- Delta pode ser configurado com referências diferentes, como "Delta Best Lap" ou "Safety Car Delta". — [Busca web sobre volantes de F1 (resumo)](https://www.sportskeeda.com/f1/f1-steering-wheel?ref=carousel)
- O volante Moza Porsche Mission R tem display OLED flexível de 5,4 polegadas, com "UI totalmente customizável", layouts de telemetria, cores e campos de dados editáveis pelo Pit House, e presets incluídos. A página não lista shift lights como item de display, só "RPM LEDs totalmente ajustáveis". — [MOZA Porsche Mission R](https://mozaracing.com/products/moza-porsche-mission-r-steering-wheel)
- Um fórum de sim racing (RaceDepartment) menciona que é possível ter várias páginas de dashboard por jogo e alternar entre elas na hora. — [RaceDepartment: sim-dashboard](https://racedepartment.com/threads/sim-dashboard.135875/) (somente resultado de busca)
- Um pedido na comunidade EA F1 sugere mostrar no display do volante brake balance, diferencial, temperaturas de pneu e freio, motor e dano, para que tudo fique visível na câmera de cockpit. — [EA Forums: multi-function display](https://forums.ea.com/discussions/f1-25-general-discussion-en/multi-function-display-directly-on-the-steering-wheel-screen-in-the-game/12387993)
- A Williams manteve o display no painel até 2024, quando passou a usá-lo dentro do volante, como as outras equipes. — [Busca web sobre display do volante](https://au.motorsport.com/f1/news/f1-steering-wheels-explained-customised-controls-vital/10593852/) (resumo de busca)

### Inferences
- Itens candidatos para o dash, pela presença em volantes reais e em pedidos de comunidade: brake bias (valor atual), diferencial, delta de melhor volta com sinal de cor, fuel restante em voltas, temperatura ou desgaste de pneus, e estado de ERS/energia (para carros híbridos).
- Uma forma de manter o minimalismo é usar páginas alternadas (por exemplo, página de corrida e página de carro/estratégia), com a cápsula principal mostrando sempre o essencial.

### Gaps
- Não foi encontrado um dash de referência de sim racing que mostre fuel, tyres e delta de forma concreta, com medidas de layout. Os sites de dashboards SimHub (Overtake.gg, SimHub community) retornaram 403 ao acesso direto, então os listings de features não foram lidos.
- Não foi possível confirmar exatamente quais campos aparecem em cada página de um volante de F1 real.

---

## Hierarquia de informação em cápsulas e telas compactas

### Takeaway
A pesquisa não encontrou um padrão documentado de hierarquia em dashes minimalistas. O que se sabe: volantes de F1 e dashes de sim racing separam informação em páginas, e o SimHub usa o mesmo editor para dash de monitor e overlay. Vale checar a regra de tamanho máximo de overlay ao adicionar um segundo overlay.

### Cited Findings
- Um moderador da comunidade SimHub explica que dash e overlay são muito próximos e usam o mesmo editor. Um dash fica ao lado do jogo, em outro monitor, enquanto um overlay aparece sobre o jogo. — [SimHub community: dashboards and overlays](https://www.simhubdash.com/community-2/simhub-support/dashboards-dashboard-layouts-overlays-and-overlay-layouts) (resumo de busca)
- Um fórum do SimHub recomenda redimensionar o dash para caber no limite de pixels quando há vários overlays, com link para a wiki do SimHub. — [SimHub community: overlay on a per game and per car basis](https://www.simhubdash.com/community-2/simhub-support/overlay-on-a-per-game-and-per-car-basis/) (resumo de busca)
- Uma dica do Simwiki diz que layouts de overlay podem ser duplicados copiando os arquivos de layout. — [SimWiki: SimHub](https://www.simwiki.net/wiki/SimHub) (resumo de busca)
- O overlay "Essential Information" é descrito na busca como um overlay de informação essencial, mas o conteúdo não foi lido. — [Overtake.gg: Essential Information Overlay](https://overtake.gg/threads/essential-information-overlay.207137) (403 ao acessar)
- Um post do Reiza forum tem uma thread de "community designs" com layouts compartilhados por membros. — [Reiza forum: SIM Dashboard Community Designs](https://forum.reizastudios.com/goto/post?id=237486) (somente resultado de busca)

### Inferences
- A cápsula de 900x240 já cabe bem em um padrão de duas zonas: estado e marchas no centro, dados secundários nas laterais. Um overlay de tela cheia com muitos campos tende a ser menos legível, o que combina com a ideia de páginas alternadas.

### Gaps
- Sem acesso aos layouts de Overtake.gg (SHO XD, SOBDash, Tritium), a hierarquia específica de cada um não foi documentada.

---

## Estados: pit, bandeira, shift light, combustível, troca de página

### Takeaway
Volantes de F1 usam páginas e cores para estados. Não foi possível confirmar o comportamento de estados em dashes de SimHub. As fontes disponíveis apenas citam que o sistema de alerta (avisos) existe.

### Cited Findings
- O volante de F1 mostra avisos e permite alternar páginas durante a corrida. — [F1 Chronicle](https://f1chronicle.com/f1-driver-inputs-steering-wheel-2026) (resumo de busca)
- O hardware da Moza tem "RPM LEDs ajustáveis" pelo software, o que sugere que shift light é um elemento de LED configurável. — [MOZA Porsche Mission R](https://mozaracing.com/products/moza-porsche-mission-r-steering-wheel)
- Um dash do Forza (FM8) foi replicado como overlay SimHub, mostrando que estados e elementos de HUD de jogos são copiados em dashes. — [Busca web sobre overlays de sim racing (resumo)](https://www.racedepartment.com/tags/simhub/page-3)

### Inferences
- Sugestão de estados para testar no dash atual: pit limiter e aviso de combustível baixo podem trocar a cor da cápsula ou o LED de status; bandeira amarela pode colorir a borda; e troca de página pode ser ligada a um botão do volante ou a um atalho do SimHub.

### Gaps
- Não há fonte verificada sobre como dashes populares tratam pit lane, bandeiras e alertas de combustível. Os sites com esses detalhes retornaram 403.

---

## Estilo visual recorrente

### Takeaway
A única referência visual com detalhe verificado é o sistema "customizável com presets" da Moza. Estilos minimalistas de HUD aparecem como tendência em HUDs de jogos (CleanHUD, Forza "simplified HUD"), mas o conteúdo das páginas dessas referências não foi lido.

### Cited Findings
- CleanHUD (para Assetto Corsa Competizione) é descrito como um HUD minimalista para o AMS, com um conjunto de widgets novos. — [RaceDepartment: CleanHUD](https://www.racedepartment.com/downloads/cleanhud.9403/) (resumo de busca)
- O Forza tem um tópico sobre "simplified HUD" nos fóruns oficiais, mas o link redireciona para a página geral do fórum e o conteúdo não foi lido. — [Forza forums: simplified HUD](https://forums.forza.net/t/simplified-hud/608259)
- Uma review de HUDs e GUIs elogia um jogo de corrida que usou só tipografia, sem ícones. — [HUDs and GUIs: E3 2015](https://www.hudsandguis.com/home/e3-2015) (resumo de busca)
- Um kit de Game UI para Figma é descrito como estilo "Minimalist / Modern" com três variações de HUD. — [Busca web sobre racing game UI (resumo)](https://geontavares.gumroad.com/l/racing-gameui)

### Inferences
- Tendência recorrente nas referências encontradas: poucos elementos, tipografia como principal recurso gráfico, e uso de cor para estado, não para decoração. Isso é coerente com o que o dash atual já faz.

### Gaps
- Nenhuma referência verificada de cores, contornos, glow ou segmentação de barras além do que o próprio dash já usa.

---

## Próximos passos sugeridos
- Pesquisar no Pinterest manualmente com termos como "sim racing cockpit display", "F1 steering wheel display", "racing telemetry UI minimal" e "SimHub dash", e salvar os URLs de pins aqui.
- Testar ao menos uma página alternativa no dash (brake bias, delta, fuel, pneus), mantendo a cápsula principal com o que já existe.
- Ler diretamente os layouts da comunidade SimHub (Overtake.gg, RaceDepartment) em um navegador, já que o acesso automatizado retorna 403.
