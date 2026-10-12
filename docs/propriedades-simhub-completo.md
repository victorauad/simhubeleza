# SimHub — referência completa de propriedades desta instalação

Gerado em 2026-10-11 a partir da instalação em `C:\Program Files (x86)\SimHub` — **SimHub 9.10.6**, pacote RSC 1.3.4, plugin Dahl Design.

**Como foi feito.** As DLLs do SimHub foram lidas por reflexão e o IL dos métodos que registram propriedades foi desmontado (`DataCorePlugin.DeclareProperties/DeclareObject/DeclareMember`, `GetShortAliasName`, `ParsePropertyPath`, `GetPropertySupportStatus`, os `Init` de cada plugin etc.). O `GameData` foi reconstruído executando a mesma regra do `DataCorePlugin` sobre uma instância nova de `StatusData`. Depois, cada nome foi consultado no servidor web local (`GET /api/GetProperty/<nome>`), com o iRacing aberto **fora de sessão**.

**Diferença para `docs/propriedades.txt`.** Aquele arquivo lista nomes encontrados em amostras de telemetria e nos dashboards instalados. Este parte do código do SimHub: traz tipo, alias, flags (oculto/obsoleto/calculado), suporte por jogo, descrição, faixas reais de índice, plugins desabilitados, eventos, ações e todas as funções de fórmula. Também corrige uma regra daquele cabeçalho (ver §1.2).

Legenda da coluna **Ao vivo**: ✓ = respondeu 200 agora; vazio = 204 (não existe *ou* está nulo neste momento — fora de sessão muita coisa é nula).

## Sumário
- [1. Como o SimHub monta os nomes](#1-como-o-simhub-monta-os-nomes)
- [2. DataCorePlugin — propriedades de topo](#2-datacoreplugin--propriedades-de-topo)
- [3. DataCorePlugin.GameData — telemetria normalizada](#3-datacoreplugingamedata--telemetria-normalizada)
- [4. Suporte por jogo](#4-suporte-por-jogo)
- [5. Pilotos e leaderboard (funções driver*)](#5-pilotos-e-leaderboard-funções-driver)
- [6. GameRawData do iRacing](#6-gamerawdata-do-iracing)
- [7. Plugins do SimHub](#7-plugins-do-simhub)
- [8. Plugins de terceiros instalados](#8-plugins-de-terceiros-instalados)
- [9. Eventos](#9-eventos)
- [10. Ações](#10-ações)
- [11. Funções de fórmula (NCalc e JavaScript)](#11-funções-de-fórmula-ncalc-e-javascript)
- [12. API HTTP local](#12-api-http-local)
- [13. Limites desta análise](#13-limites-desta-análise)

## 1. Como o SimHub monta os nomes

### 1.1 Prefixo
Toda propriedade é registrada por um plugin e ganha o nome da **classe** do plugin como prefixo: `DataCorePlugin.`, `PersistantTrackerPlugin.`, `IRacingExtraProperties.`, `DahlDesign.` etc. (`PluginManager.AttachDelegate/AttachProperty/AddProperty(name, pluginType, ...)`). Plugin desabilitado em *Settings → Plugins* não registra nada — os nomes dele simplesmente não existem.

### 1.2 Atalhos sem prefixo (regra exata)
`DataCorePlugin.GetShortAliasName` só cria atalho em dois casos:

- `GameData.X` (fora de `GameData.NewData`) → atalho **`X`**. Ex.: `[Gear]`, `[SpeedKmh]`, `[Flag_Blue]`.
- `GameRawData.*` → atalho **igual ao próprio nome**. Ex.: `[GameRawData.Telemetry.Speed]`.

Todo o resto exige o nome completo. Conferido agora no servidor local:

| Nome | Resposta | Obs. |
|---|---|---|
| `DataCorePlugin.GameData.Gear` | 200 |  |
| `Gear` | 200 |  |
| `GameData.Gear` | 204 | sem DataCorePlugin. não resolve |
| `DataCorePlugin.GameRawData.Telemetry.Speed` | 200 |  |
| `GameRawData.Telemetry.Speed` | 200 |  |
| `DataCorePlugin.CurrentGame` | 200 |  |
| `CurrentGame` | 204 | topo do DataCorePlugin não tem atalho |
| `DataCorePlugin.GameData.NewData.Gear` | 200 | cópia legada, oculta no editor |
| `GameData.NewData.Gear` | 204 |  |

> O cabeçalho de `docs/propriedades.txt` diz que "o prefixo `DataCorePlugin.` é opcional". Vale só para os dois casos acima. O dashboard atual usa sempre o nome completo, então nada quebra.

### 1.3 Aliases declarados no código
Alguns membros têm `[ExposeAlias]` e ficam acessíveis também por outro nome (sempre dentro de `DataCorePlugin.GameData.`, com atalho curto):

| Nome principal | Alias |
|---|---|
| `BrakesTemperatureAvg` | `BrakeTemperatureAvg` |
| `BrakesTemperatureMax` | `BrakeTemperatureMax` |
| `BrakesTemperatureMin` | `BrakeTemperatureMin` |
| `BrakeTemperatureFrontLeft` | `BrakeTemperature1` |
| `BrakeTemperatureFrontRight` | `BrakeTemperature2` |
| `BrakeTemperatureRearLeft` | `BrakeTemperature3` |
| `BrakeTemperatureRearRight` | `BrakeTemperature4` |
| `CarDamagesAvg` | `CarDamageAvg` |
| `CarDamagesMax` | `CarDamageMax` |
| `CarDamagesMin` | `CarDamageMin` |
| `Throttle` | `Gas` |
| `TyreDirtFrontLeft` | `TyreDirtyLevel1` |
| `TyreDirtFrontRight` | `TyreDirtyLevel2` |
| `TyreDirtRearLeft` | `TyreDirtyLevel3` |
| `TyreDirtRearRight` | `TyreDirtyLevel4` |
| `TyresDirtyLevelAvg` | `TyreDirtyLevelAvg` |
| `TyresDirtyLevelMax` | `TyreDirtyLevelMax` |
| `TyresDirtyLevelMin` | `TyreDirtyLevelMin` |
| `TyresTemperatureAvg` | `TyreCoreTemperatureAvg` |
| `TyresTemperatureMax` | `TyreCoreTemperatureMax` |
| `TyresTemperatureMin` | `TyreCoreTemperatureMin` |
| `TyresWearAvg` | `TyreWearAvg` |
| `TyresWearMax` | `TyreWearMax` |
| `TyresWearMin` | `TyreWearMin` |
| `TyreTemperatureFrontLeft` | `TyreCoreTemperature1` |
| `TyreTemperatureFrontRight` | `TyreCoreTemperature2` |
| `TyreTemperatureRearLeft` | `TyreCoreTemperature3` |
| `TyreTemperatureRearRight` | `TyreCoreTemperature4` |
| `TyreWearFrontLeft` | `TyreWear1` |
| `TyreWearFrontRight` | `TyreWear2` |
| `TyreWearRearLeft` | `TyreWear3` |
| `TyreWearRearRight` | `TyreWear4` |

### 1.4 Como objetos viram nomes
Regras do `DeclareObject` (o mesmo para `GameData` e `GameRawData`):

- Tipos básicos (números, `bool`, `string`, `enum`, `DateTime`, `TimeSpan`, `Nullable<>`) viram propriedade.
- **Array** → um nome por elemento, sufixo de 2 dígitos **começando em 01**: `CarCoordinates01..03`, `Drivers01`, `Sessions01`.
- **List<> / qualquer IEnumerable que não seja array → ignorado.** Por isso `GameData.Opponents` não existe como propriedade (use §5).
- **Dicionário** → um nome por chave; valores que são arrays são pulados (é por isso que `GameRawData.Telemetry.CarIdx*` do iRacing não existe — ver §6).
- Objetos que implementam `IExposable` escolhem o que expor (`GetValues()`); o iRacing usa isso (§6).
- Objeto **nulo no momento do registro** não gera filhos. O registro acontece com uma instância nova/amostra, então filhos de objetos que só se preenchem em sessão podem não existir.
- Excluídos sempre: caminhos com `.Skin` e terminados em `.OldData`, `.GameOldData`, `.GameNewData`, `.RawData`, `.RawDataObject`, `.Events`.
- `[DoNotExpose]` remove o membro; `[Hidden]` registra mas esconde do seletor do editor; `[ExposeName]` renomeia.

### 1.5 Suporte por jogo (`SupportStatus`)
Cada leitor de jogo pode declarar um método `GD_<Membro>`. O `DataCorePlugin` olha esse método para marcar a propriedade no editor: sem `GD_` e com `[Computed]` no membro → **calculado pelo SimHub**; `GD_` com `[NotAvailable]` → **não disponível nesse jogo**; `GD_` com `[Computed]` → calculado; `GD_` sem atributo → **fornecido pelo jogo**. Tabela completa em §4.

### 1.6 Índices: cada plugin usa uma base
| Família | Faixa real (conferida) |
|---|---|
| `DataCorePlugin.GameData.CarCoordinatesNN` | 01..03 |
| `GameRawData.SessionData...DriversNN`, `SessionsNN` | começa em 01 (`Drivers00` não existe) |
| `PersistantTrackerPlugin.DriverAhead_NN_*` / `DriverBehind_NN_*` | 00..04 |
| `PersistantTrackerPlugin.PreviousLap_NN*` | 00..09 |
| `IRacingExtraProperties.*` | varia por família — ver §8.1 |

### 1.7 Como ler nas fórmulas
- NCalc: `[DataCorePlugin.GameData.SpeedKmh]` ou `[SpeedKmh]`.
- JavaScript: `$prop('DataCorePlugin.GameData.SpeedKmh')` (ou `$prop('SpeedKmh')`).
- HTTP: `GET http://localhost:8888/api/GetProperty/<nome>` → 200 com o valor, 204 quando não existe ou é nulo.

## 2. DataCorePlugin — propriedades de topo

Registradas em `DataCorePlugin.DeclareProperties`. Nenhuma tem atalho curto (use `DataCorePlugin.<nome>`).

| Nome (após `DataCorePlugin.`) | Tipo | Flag | Ao vivo | Descrição |
|---|---|---|---|---|
| `GameRunning` | Int32 |  | ✓ | Jogo em execução e enviando dados (0/1). |
| `GamePaused` | Int32 |  | ✓ | Jogo pausado (0/1). |
| `CurrentGame` | String |  | ✓ | Código do jogo ativo no SimHub (ex.: IRacing). Sem alias curto. |
| `SimHubVersion` | String |  | ✓ | Versão do SimHub. |
| `GameVolume` | Int32 |  | ✓ | Volume do jogo no mixer do Windows. |
| `SystemVolume` | Double |  | ✓ | Volume mestre do Windows. |
| `DefaultSoundInputIsMuted` | Int32 |  | ✓ | Microfone padrão mudo (0/1). |
| `CurrentDateTime` | DateTime |  | ✓ | Data/hora local. |
| `CustomExpression.CurrentDateTime` | DateTime | oculta | ✓ | Data/hora local (variante usada pelas expressões). |
| `CustomExpression.CompactDelta` | Object |  | ✓ | Delta compacto pronto para exibir. |
| `CustomExpression.<nome>` | Object |  |  | Uma por expressão personalizada definida pelo usuário. |
| `Computed.Fuel_Percent` | Double |  | ✓ | Combustível em %. |
| `Computed.Fuel_RemainingLaps` | Double |  | ✓ | Voltas restantes estimadas com o combustível atual. |
| `Computed.Fuel_RemainingTime` | TimeSpan |  | ✓ | Tempo restante estimado com o combustível atual. |
| `Computed.Fuel_LitersPerLap` | Double |  | ✓ | Consumo médio por volta. |
| `Computed.Fuel_LastLapConsumption` | Double |  | ✓ | Consumo da última volta. |
| `Computed.Fuel_CurrentLapConsumption` | Double |  | ✓ | Consumo na volta atual. |
| `Computed.Fuel_CurrentLapIsValidForTracking` | Int32 |  | ✓ | Volta atual entra na média de consumo (0/1). |
| `ComputedRPMPercent` | Double | oculta |  | RPM em % (oculto). |
| `ComputedTurboPercent` | Double | oculta |  | Turbo em % (oculto). |
| `RPMBlink` | Double | oculta |  | Pisca de redline (oculto). |
| `BlinkTriggerRatio` | Double | oculta |  | Limiar de pisca de redline (oculto). |
| `RPMStartOffset` | Int32 | oculta |  | Offset de início da faixa de RPM dos LEDs (oculto). |
| `LowFuelLapLevel` | Double | oculta |  | Limite de alerta de combustível em voltas (oculto). |
| `DataUpdateFps` | Double |  | ✓ | Frequência de atualização dos dados (Hz). |
| `Performance_JSFormulasPerSecond` | Double |  | ✓ | Fórmulas JS avaliadas por segundo. |
| `Performance_NALCFormulasPerSecond` | Double |  | ✓ | Fórmulas NCalc avaliadas por segundo. |
| `Performance_NALCOptimizedFormulasPerSecond` | Double |  | ✓ | Fórmulas NCalc otimizadas por segundo. |
| `Performance_CachedFormulasPerSecond` | Double |  | ✓ | Fórmulas servidas do cache por segundo. |
| `Performance_RecycledJSExpressions` | Int64 |  | ✓ | Expressões JS recicladas. |
| `Performance_CreatedJSExpressions` | Int64 |  | ✓ | Expressões JS criadas. |
| `Performance_RecycledNCALCExpressions` | Int64 |  | ✓ | Expressões NCalc recicladas. |
| `Performance_CreatedNCALCExpressions` | Int64 |  | ✓ | Expressões NCalc criadas. |
| `Performance_FrameDuration` | Double |  | ✓ | Duração do ciclo de dados (ms). |
| `PluginNotification_Active` | Boolean |  | ✓ | Há notificação de plugin ativa. |
| `PluginNotification_Title` | String |  |  | Título da notificação de plugin. |
| `PluginNotification_Content` | String |  |  | Texto da notificação de plugin. |
| `PluginNotification_PercentValue` | Double? |  |  | Progresso da notificação, %. |
| `GameNotification_Active` | Boolean |  | ✓ | Há notificação do jogo ativa. |
| `GameNotification_Title` | String |  |  | Título da notificação do jogo. |
| `GameNotification_Content` | String |  |  | Texto da notificação do jogo. |
| `LoggingLastMessage` | String |  | ✓ | Última mensagem do log do SimHub. |
| `LoggingLastSeverity` | String |  | ✓ | Severidade da última mensagem. |
| `LoggingErrorsCount` | Int32 |  | ✓ | Erros registrados no log. |
| `HeartRateMonitorLastBPM` | UInt16? |  |  | Batimentos do monitor cardíaco conectado. |
| `HeartRateMonitorSimulatedBloodPressure` | Double? |  |  | Pressão arterial simulada a partir do BPM. |
| `DayNightMode` | String |  | ✓ | Modo dia/noite (Day/Night), alternado pela ação ToggleDayNightMode. |

Também do `DataCorePlugin`: `InputPressed : <nome>` / `InputReleased : <nome>` (Int32) são criadas pelo `PluginManager` quando um input mapeado é usado.

## 3. DataCorePlugin.GameData — telemetria normalizada

Nome completo: `DataCorePlugin.GameData.<Nome>`; atalho: `<Nome>`. A mesma árvore existe duplicada e oculta em `DataCorePlugin.GameData.NewData.<Nome>`. Coluna **iR** = suporte no iRacing (S fornecido, C calculado, — indisponível, · sem declaração). Valores "padrão" são os de uma instância vazia.

| Nome | Tipo | Flags | iR | Ao vivo | Descrição |
|---|---|---|---|---|---|
| `ABSActive` | Int32 |  | S | ✓ | ABS atuando neste instante (0/1). |
| `ABSLevel` | Int32 |  | S | ✓ | Nível/posição do ABS selecionado no carro. |
| `AirTemperature` | Double |  | S | ✓ | Temperatura do ar (unidade em TemperatureUnit). |
| `AllTimeBest` | TimeSpan |  | — | ✓ | Melhor volta de todos os tempos registrada pelo SimHub para carro+pista. |
| `BestLapTime` | TimeSpan |  | S | ✓ | Melhor volta do jogador na sessão. |
| `Brake` | Double |  | S | ✓ | Pedal de freio, 0-100. |
| `Handbrake` | Double |  | S | ✓ | Freio de mão, 0-100. |
| `BrakeBias` | Double |  | S | ✓ | Distribuição de freio (% na dianteira, como o jogo reporta). |
| `BrakesTemperatureAvg` | Double | calculada | C | ✓ | Média das temperaturas de freio (calculado). Alias: BrakeTemperatureAvg. |
| `BrakesTemperatureMax` | Double | calculada | C | ✓ | Máximo das temperaturas de freio (calculado). Alias: BrakeTemperatureMax. |
| `BrakesTemperatureMin` | Double | calculada | C | ✓ | Mínimo das temperaturas de freio (calculado). Alias: BrakeTemperatureMin. |
| `BrakeTemperatureFrontLeft` | Double |  | — | ✓ | Temperatura do freio dianteiro esquerdo. Alias: BrakeTemperature1. |
| `BrakeTemperatureFrontRight` | Double |  | — | ✓ | Temperatura do freio dianteiro direito. Alias: BrakeTemperature2. |
| `BrakeTemperatureRearLeft` | Double |  | — | ✓ | Temperatura do freio traseiro esquerdo. Alias: BrakeTemperature3. |
| `BrakeTemperatureRearRight` | Double |  | — | ✓ | Temperatura do freio traseiro direito. Alias: BrakeTemperature4. |
| `CarCoordinates01` | Double |  | · | ✓ | Posição do carro no mundo, eixo X (array de 3 exposto como 01..03). |
| `CarCoordinates02` | Double |  | · | ✓ | Posição do carro no mundo, eixo Y. |
| `CarCoordinates03` | Double |  | · | ✓ | Posição do carro no mundo, eixo Z. |
| `CarDamage1` | Double |  | — | ✓ | Dano na zona 1 (frente na maioria dos jogos), 0-100. |
| `CarDamage2` | Double |  | — | ✓ | Dano na zona 2 (traseira). |
| `CarDamage3` | Double |  | — | ✓ | Dano na zona 3 (esquerda). |
| `CarDamage4` | Double |  | — | ✓ | Dano na zona 4 (direita). |
| `CarDamage5` | Double |  | — | ✓ | Dano na zona 5 (centro/motor, conforme o jogo). |
| `CarDamagesAvg` | Double | calculada | C | ✓ | Média das zonas de dano. Alias: CarDamageAvg. |
| `CarDamagesMax` | Double | calculada | C | ✓ | Maior dano entre as zonas. Alias: CarDamageMax. |
| `CarDamagesMin` | Double | calculada | C | ✓ | Menor dano entre as zonas. Alias: CarDamageMin. |
| `CarModel` | String |  | S |  | Nome do carro como exibido. |
| `CarId` | String |  | S |  | Identificador interno do carro (usado nos perfis de carro do SimHub). |
| `Clutch` | Double |  | S | ✓ | Pedal de embreagem, 0-100. |
| `CompletedLaps` | Int32 |  | S | ✓ | Voltas completadas. |
| `CurrentLap` | Int32 |  | · | ✓ | Volta atual (CompletedLaps + 1 na maioria dos jogos). |
| `CurrentLapTime` | TimeSpan |  | S | ✓ | Tempo decorrido na volta atual. |
| `CurrentSectorIndex` | Int32 |  | S | ✓ | Setor atual (começa em 1). |
| `DeltaToAllTimeBest` | Double? |  | — |  | Delta ao vivo contra a melhor volta de todos os tempos (s); null sem referência. |
| `DeltaToSessionBest` | Double? |  | S |  | Delta ao vivo contra a melhor volta da sessão (s); null sem referência. |
| `DRSAvailable` | Int32 |  | — | ✓ | DRS disponível (0/1). |
| `DRSEnabled` | Int32 |  | — | ✓ | DRS aberto (0/1). |
| `EngineTorque` | Double |  | — | ✓ | Torque do motor. |
| `FilteredRpms` | Double | oculta, obsoleta | · | ✓ | Obsoleto: RPM filtrado. |
| `FilteredSpeedKmh` | Double | oculta, obsoleta | · | ✓ | Obsoleto: velocidade filtrada km/h. |
| `FilteredSpeedLocal` | Double | oculta, obsoleta | · | ✓ | Obsoleto: velocidade filtrada na unidade local. |
| `FilteredSpeedMph` | Double | oculta, obsoleta | · | ✓ | Obsoleto: velocidade filtrada mph. |
| `Flag_Black` | Int32 |  | S | ✓ | Bandeira preta ativa (0/1). |
| `Flag_Orange` | Int32 |  | — | ✓ | Bandeira preta com círculo laranja / reparo (0/1). |
| `Flag_Blue` | Int32 |  | S | ✓ | Bandeira azul (0/1). |
| `Flag_Checkered` | Int32 |  | S | ✓ | Bandeira quadriculada (0/1). |
| `Flag_Green` | Int32 |  | S | ✓ | Bandeira verde (0/1). |
| `Flag_Name` | String | calculada | C | ✓ | Nome da bandeira ativa de maior prioridade (texto, calculado). |
| `Flag_White` | Int32 |  | S | ✓ | Bandeira branca (0/1). |
| `Flag_Yellow` | Int32 |  | S | ✓ | Bandeira amarela (0/1). |
| `Fuel` | Double |  | S | ✓ | Combustível no tanque (unidade em FuelUnit). |
| `FuelPercent` | Double |  | · | ✓ | Combustível em % do tanque. |
| `Throttle` | Double |  | S | ✓ | Acelerador, 0-100. Alias: Gas. Alias: Gas. |
| `Gear` | String |  | S | ✓ | Marcha como texto: R, N, 1, 2... |
| `IsInPit` | Int32 |  | S | ✓ | Carro parado no box (0/1). |
| `IsInPitSince` | Double |  | · | ✓ | Segundos desde a entrada no box/pit lane. |
| `LastPitStopDuration` | Double |  | · | ✓ | Duração do último pit stop (s). |
| `IsInPitLane` | Int32 |  | S | ✓ | Carro no pit lane (0/1). |
| `LastLapTime` | TimeSpan |  | S | ✓ | Tempo da última volta completada. |
| `LastSectorTime` | TimeSpan | calculada | C | ✓ | Tempo do último setor completado na volta atual. |
| `LastSectorTimeAnyLap` | TimeSpan | calculada | C | ✓ | Tempo do último setor completado, mesmo que de volta anterior. |
| `MapAllowed` | Boolean |  | S | ✓ | O jogo permite exibir o mapa (algumas ligas/jogos bloqueiam). |
| `MaxEngineTorque` | Double | calculada | C | ✓ | Maior torque observado. |
| `MaxFuel` | Double |  | S | ✓ | Capacidade do tanque. |
| `MaxRpm` | Double | calculada | S | ✓ | RPM máximo (do jogo ou aprendido; ver CarSettings_MaxRPM). |
| `MaxTurbo` | Double | calculada | — | ✓ | Maior pressão de turbo observada. |
| `OilPressure` | Double |  | S | ✓ | Pressão do oleo. |
| `OilPressureUnit` | String |  | · | ✓ | Unidade de OilPressure. |
| `OilTemperature` | Double |  | S | ✓ | Temperatura do oleo. |
| `Opponents` | List<Opponent> | não exposta | S |  | Lista de todos os pilotos. NÃO exposta como propriedade (List<> e ignorada) - usar funções driver*() / getopponent*(). |
| `OpponentsAheadOnTrack` | List<Opponent> | não exposta | · |  | Lista de pilotos a frente na pista. NÃO exposta - ver PersistantTrackerPlugin.DriverAhead_NN_*. |
| `OpponentsBehindOnTrack` | List<Opponent> | não exposta | · |  | Lista de pilotos atras na pista. NÃO exposta - ver PersistantTrackerPlugin.DriverBehind_NN_*. |
| `OpponentsAheadOnTrackPlayerClass` | List<Opponent> | não exposta | · |  | Idem, só a classe do jogador. NÃO exposta. |
| `OpponentsBehindOnTrackPlayerClass` | List<Opponent> | não exposta | · |  | Idem, só a classe do jogador. NÃO exposta. |
| `OpponentsPlayerClass` | List<Opponent> | não exposta | · |  | Pilotos da classe do jogador. NÃO exposta. |
| `PitLimiterOn` | Int32 |  | S | ✓ | Limitador de box ligado (0/1). |
| `Position` | Int32 |  | S | ✓ | Posição na corrida. |
| `RemainingLaps` | Int32 |  | · | ✓ | Voltas restantes (sessão por voltas). |
| `ReplayMode` | String |  | · |  | Modo de replay informado pelo jogo. |
| `RoadTemperature` | Double |  | S | ✓ | Temperatura da pista. |
| `Rpms` | Double |  | S | ✓ | RPM atual. |
| `SessionTimeLeft` | TimeSpan |  | S | ✓ | Tempo restante da sessão. |
| `SessionTypeName` | String |  | S |  | Tipo de sessão normalizado pelo SimHub (Practice, Qualify, Race...). Pode ser null fora de sessão. |
| `SpeedKmh` | Double |  | S | ✓ | Velocidade km/h. |
| `SpeedLocal` | Double |  | · | ✓ | Velocidade na unidade do usuário. |
| `SpeedLocalUnit` | String |  | · | ✓ | Unidade de SpeedLocal (KMH/MPH). |
| `TemperatureUnit` | String |  | · | ✓ | Unidade das temperaturas (Celcius/Fahrenheit). |
| `SpeedMph` | Double |  | · | ✓ | Velocidade mph. |
| `TCActive` | Int32 |  | — | ✓ | Controle de tração atuando (0/1). |
| `TCLevel` | Int32 |  | S | ✓ | Nível do controle de tração. |
| `TotalLaps` | Int32 |  | S | ✓ | Total de voltas da sessão (0 se por tempo). |
| `TrackNameWithConfig` | String |  | · |  | Nome + configuração. |
| `TrackCode` | String |  | · |  | Código curto da pista. |
| `TrackConfig` | String |  | S |  | Configuração/traçado. |
| `TrackName` | String |  | S |  | Nome da pista. |
| `TrackId` | String |  | S |  | Identificador interno da pista. |
| `TrackIdWithConfig` | String | oculta | · |  | Identificador + configuração (oculto). |
| `Turbo` | Double |  | — | ✓ | Pressão do turbo. |
| `TurboPercent` | Double |  | · | ✓ | Turbo em % do máximo. |
| `TyrePressureFrontLeft` | Double |  | S | ✓ | Pressão do pneu dianteiro esquerdo. |
| `TyrePressureFrontRight` | Double |  | S | ✓ | Pressão do pneu dianteiro direito. |
| `TyrePressureRearLeft` | Double |  | S | ✓ | Pressão do pneu traseiro esquerdo. |
| `TyrePressureRearRight` | Double |  | S | ✓ | Pressão do pneu traseiro direito. |
| `TyreDirtFrontLeft` | Double |  | — | ✓ | Sujeira no pneu dianteiro esquerdo. Alias: TyreDirtyLevel1. |
| `TyreDirtFrontRight` | Double |  | — | ✓ | Sujeira no pneu dianteiro direito. Alias: TyreDirtyLevel2. |
| `TyreDirtRearLeft` | Double |  | — | ✓ | Sujeira no pneu traseiro esquerdo. Alias: TyreDirtyLevel3. |
| `TyreDirtRearRight` | Double |  | — | ✓ | Sujeira no pneu traseiro direito. Alias: TyreDirtyLevel4. |
| `TyresDirtyLevelAvg` | Double | calculada | C | ✓ | Média da sujeira dos pneus (calculado). Alias: TyreDirtyLevelAvg. |
| `TyresDirtyLevelMax` | Double | calculada | C | ✓ | Máximo da sujeira dos pneus (calculado). Alias: TyreDirtyLevelMax. |
| `TyresDirtyLevelMin` | Double | calculada | C | ✓ | Mínimo da sujeira dos pneus (calculado). Alias: TyreDirtyLevelMin. |
| `TyresTemperatureAvg` | Double | calculada | C | ✓ | Média das temperaturas de pneu (calculado). Alias: TyreCoreTemperatureAvg. |
| `TyresTemperatureMax` | Double | calculada | C | ✓ | Máximo das temperaturas de pneu (calculado). Alias: TyreCoreTemperatureMax. |
| `TyresTemperatureMin` | Double | calculada | C | ✓ | Mínimo das temperaturas de pneu (calculado). Alias: TyreCoreTemperatureMin. |
| `TyresWearAvg` | Double | calculada | C | ✓ | Média do desgaste dos pneus (calculado). Alias: TyreWearAvg. |
| `TyresWearMax` | Double | calculada | C | ✓ | Máximo do desgaste dos pneus (calculado). Alias: TyreWearMax. |
| `TyresWearMin` | Double | calculada | C | ✓ | Mínimo do desgaste dos pneus (calculado). Alias: TyreWearMin. |
| `TyreTemperatureFrontLeft` | Double |  | S | ✓ | Temperatura do pneu dianteiro esquerdo (núcleo/média). Alias: TyreCoreTemperature1. |
| `TyreTemperatureFrontRight` | Double |  | S | ✓ | Temperatura do pneu dianteiro direito (núcleo/média). Alias: TyreCoreTemperature2. |
| `TyreTemperatureRearLeft` | Double |  | S | ✓ | Temperatura do pneu traseiro esquerdo (núcleo/média). Alias: TyreCoreTemperature3. |
| `TyreTemperatureRearRight` | Double |  | S | ✓ | Temperatura do pneu traseiro direito (núcleo/média). Alias: TyreCoreTemperature4. |
| `TyreTemperatureFrontLeftInner` | Double |  | S | ✓ | Temperatura do pneu dianteiro esquerdo, parte interna da banda. |
| `TyreTemperatureFrontLeftMiddle` | Double |  | S | ✓ | Temperatura do pneu dianteiro esquerdo, centro da banda. |
| `TyreTemperatureFrontLeftOuter` | Double |  | S | ✓ | Temperatura do pneu dianteiro esquerdo, parte externa da banda. |
| `TyreTemperatureFrontRightInner` | Double |  | S | ✓ | Temperatura do pneu dianteiro direito, parte interna da banda. |
| `TyreTemperatureFrontRightMiddle` | Double |  | S | ✓ | Temperatura do pneu dianteiro direito, centro da banda. |
| `TyreTemperatureFrontRightOuter` | Double |  | S | ✓ | Temperatura do pneu dianteiro direito, parte externa da banda. |
| `TyreTemperatureRearLeftInner` | Double |  | S | ✓ | Temperatura do pneu traseiro esquerdo, parte interna da banda. |
| `TyreTemperatureRearLeftMiddle` | Double |  | S | ✓ | Temperatura do pneu traseiro esquerdo, centro da banda. |
| `TyreTemperatureRearLeftOuter` | Double |  | S | ✓ | Temperatura do pneu traseiro esquerdo, parte externa da banda. |
| `TyreTemperatureRearRightInner` | Double |  | S | ✓ | Temperatura do pneu traseiro direito, parte interna da banda. |
| `TyreTemperatureRearRightMiddle` | Double |  | S | ✓ | Temperatura do pneu traseiro direito, centro da banda. |
| `TyreTemperatureRearRightOuter` | Double |  | S | ✓ | Temperatura do pneu traseiro direito, parte externa da banda. |
| `TyreWearFrontLeft` | Double |  | S | ✓ | Desgaste do pneu (0-100, 100 = novo na maioria dos jogos) dianteiro esquerdo. Alias: TyreWear1. |
| `TyreWearFrontRight` | Double |  | S | ✓ | Desgaste do pneu (0-100, 100 = novo na maioria dos jogos) dianteiro direito. Alias: TyreWear2. |
| `TyreWearRearLeft` | Double |  | S | ✓ | Desgaste do pneu (0-100, 100 = novo na maioria dos jogos) traseiro esquerdo. Alias: TyreWear3. |
| `TyreWearRearRight` | Double |  | S | ✓ | Desgaste do pneu (0-100, 100 = novo na maioria dos jogos) traseiro direito. Alias: TyreWear4. |
| `LastLapTyreWearFrontLeft` | Double |  | · | ✓ | Desgaste do pneu na última volta dianteiro esquerdo. |
| `LastLapTyreWearFrontRight` | Double |  | · | ✓ | Desgaste do pneu na última volta dianteiro direito. |
| `LastLapTyreWearRearLeft` | Double |  | · | ✓ | Desgaste do pneu na última volta traseiro esquerdo. |
| `LastLapTyreWearRearRight` | Double |  | · | ✓ | Desgaste do pneu na última volta traseiro direito. |
| `WaterTemperature` | Double |  | S | ✓ | Temperatura da agua. |
| `TyrePressureUnit` | String |  | · | ✓ | Unidade das pressoes de pneu. |
| `Sector1Time` | TimeSpan? |  | — |  | Tempo do setor 1 na volta atual. |
| `Sector2Time` | TimeSpan? |  | — |  | Tempo do setor 2 na volta atual. |
| `Sector1LastLapTime` | TimeSpan? | calculada | C |  | Tempo do setor 1 na última volta. |
| `Sector2LastLapTime` | TimeSpan? | calculada | C |  | Tempo do setor 2 na última volta. |
| `Sector3LastLapTime` | TimeSpan? | calculada | C |  | Tempo do setor 3 na última volta. |
| `Sector1BestLapTime` | TimeSpan? | calculada | C |  | Tempo do setor 1 na melhor volta. |
| `Sector2BestLapTime` | TimeSpan? | calculada | C |  | Tempo do setor 2 na melhor volta. |
| `Sector3BestLapTime` | TimeSpan? | calculada | C |  | Tempo do setor 3 na melhor volta. |
| `Sector1BestTime` | TimeSpan? | calculada | C |  | Tempo do setor 1 melhor da sessão (setor isolado). |
| `Sector2BestTime` | TimeSpan? | calculada | C |  | Tempo do setor 2 melhor da sessão (setor isolado). |
| `Sector3BestTime` | TimeSpan? | calculada | C |  | Tempo do setor 3 melhor da sessão (setor isolado). |
| `OpponentsCount` | Int32 | calculada | C | ✓ | Número de pilotos na sessão (inclui o jogador). |
| `PlayerClassOpponentsCount` | Int32 | calculada | C | ✓ | Número de pilotos na classe do jogador. |
| `CarSettings_MaxRPM` | Double |  | · | ✓ | RPM máximo do perfil do carro no SimHub. |
| `CarSettings_MaxFUEL` | Double |  | · | ✓ | Tanque máximo do perfil do carro. |
| `CarSettings_RedLineRPM` | Double |  | · | ✓ | RPM de redline efetivo. |
| `CarSettings_MinimumShownRPM` | Double | oculta, obsoleta | · | ✓ | Obsoleto: RPM mínimo exibido. |
| `CarSettings_CurrentDisplayedRPMPercent` | Double |  | · | ✓ | RPM atual em % da faixa exibida (base dos LEDs). |
| `CarSettings_RPMRedLineReached` | Double |  | · | ✓ | Redline atingido (0/1). |
| `CarSettings_RedLineDisplayedPercent` | Double |  | · | ✓ | Posição do redline na faixa exibida, %. |
| `CarSettings_RPMShiftLight1` | Double |  | · | ✓ | Limite da luz de troca 1 (fração). |
| `CarSettings_RPMShiftLight2` | Double |  | · | ✓ | Limite da luz de troca 2 (fração). |
| `CarSettings_RPMRedLineSetting` | Double |  | · | ✓ | Redline configurado (fração). |
| `CarSettings_RPMRedLinePerGearOverride` | Int32 |  | · | ✓ | Redline por marcha ativo (0/1). |
| `CarSettings_MaxGears` | Int32 |  | · | ✓ | Número de marchas. |
| `PacketTime` | DateTime |  | S | ✓ | Hora do pacote de telemetria. |
| `MaxSpeedKmh` | Double | calculada | C | ✓ | Maior velocidade (km/h) desde o último ResetMaxSpeed. |
| `MaxSpeedMph` | Double | calculada | C | ✓ | Idem em mph. |
| `MaxSpeedLocal` | Double | calculada | C | ✓ | Idem na unidade local. |
| `CarClass` | String |  | · | ✓ | Classe do carro do jogador. |
| `SelfsplitDelta` | Double? |  | · |  | Delta do último setor contra a propria melhor volta. |
| `BestSplitDelta` | Double? |  | · |  | Delta do último setor contra a melhor volta da sessão. |
| `BestLapSameClassOpponent` | Opponent | oculta, objeto; filhos só se não-nulo | · |  | Piloto com melhor volta na classe (objeto oculto; filhos só existem se não-nulo no registro). |
| `BestLapOpponentPosition` | Int32 |  | · | ✓ | Posição no leaderboard do dono da melhor volta (-1 = nenhum). |
| `BestLapOpponentSameClassPosition` | Int32 |  | · | ✓ | Idem, dentro da classe do jogador. |
| `TrackLength` | Double |  | — | ✓ | Comprimento da pista em metros. |
| `ReportedTrackLength` | Double | oculta | · | ✓ | Comprimento informado pelo jogo (oculto). |
| `TrackPositionMeters` | Double | calculada | C | ✓ | Distância percorrida na volta, em metros (calculado). |
| `FuelUnit` | String |  | · | ✓ | Unidade de combustível (Liters/Gallons). |
| `OrientationPitch` | Double |  | S | ✓ | Arfagem (pitch), graus. |
| `OrientationYaw` | Double |  | S | ✓ | Guinada (yaw), graus. |
| `OrientationRoll` | Double |  | S | ✓ | Rolagem (roll), graus. |
| `OrientationRollAcceleration` | Double |  | · | ✓ | Aceleração de rolagem. |
| `OrientationPitchAcceleration` | Double |  | · | ✓ | Aceleração de arfagem. |
| `OrientationYawAcceleration` | Double |  | · | ✓ | Aceleração de guinada. |
| `OrientationYawVelocity` | Double |  | · | ✓ | Velocidade de guinada. |
| `AccelerationSway` | Double? |  | S |  | Aceleração lateral (G). |
| `AccelerationSurge` | Double? |  | S |  | Aceleração longitudinal (G). |
| `AccelerationHeave` | Double? |  | S |  | Aceleração vertical (G). |
| `RollChangeVelocity` | Double? |  | — |  | Taxa de variação da rolagem. |
| `PitchChangeVelocity` | Double? |  | — |  | Taxa de variação da arfagem. |
| `YawChangeVelocity` | Double? |  | — |  | Taxa de variação da guinada. |
| `GlobalAccelerationG` | Double |  | · | ✓ | Aceleração total (G). |
| `ERSMax` | Double |  | S | ✓ | Capacidade do ERS/bateria. |
| `ERSStored` | Double |  | S | ✓ | Energia armazenada no ERS. |
| `ERSPercent` | Double |  | · | ✓ | ERS em %. |
| `LapInvalidated` | Boolean |  | · | ✓ | Volta atual invalidada. |
| `SessionOdo` | Double |  | · | ✓ | Distância percorrida na sessão (m). |
| `SessionOdoLocalUnit` | Double |  | · | ✓ | Idem na unidade local (km/mi). |
| `StintOdo` | Double |  | · | ✓ | Distância no stint (m). |
| `StintOdoLocalUnit` | Double |  | · | ✓ | Idem na unidade local. |
| `InstantConsumption_L100KM` | Double |  | · | ✓ | Consumo instantâneo, L/100 km. |
| `InstantConsumption_MPG_UK` | Double |  | · | ✓ | Consumo instantâneo, MPG (UK). |
| `InstantConsumption_MPG_US` | Double |  | · | ✓ | Consumo instantâneo, MPG (US). |
| `TurnIndicatorLeft` | Int32 |  | — | ✓ | Seta esquerda (0/1). |
| `TurnIndicatorRight` | Int32 |  | — | ✓ | Seta direita (0/1). |
| `PlayerName` | String |  | · | ✓ | Nome do jogador. |
| `Spectating` | Boolean |  | · | ✓ | Jogador está assistindo (não pilotando). |
| `CarSettings_FuelAlertActive` | Int32 |  | · | ✓ | Alerta de combustível disparado (0/1). |
| `CarSettings_FuelAlertEnabled` | Int32 |  | · | ✓ | Alerta de combustível habilitado (0/1). |
| `CarSettings_FuelAlertLaps` | Double |  | · | ✓ | Limite em voltas do alerta de combustível. |
| `EngineMap` | Int32 |  | — | ✓ | Mapa de motor selecionado. |
| `SpotterCarLeft` | Int32 |  | S | ✓ | Carro ao lado esquerdo (0/1). |
| `SpotterCarLeftDistance` | Double |  | · | ✓ | Distância longitudinal do carro a esquerda. |
| `SpotterCarRight` | Int32 |  | S | ✓ | Carro ao lado direito (0/1). |
| `SpotterCarRightDistance` | Double |  | · | ✓ | Distância longitudinal do carro a direita. |
| `SpotterCarLeftAngle` | Double |  | · | ✓ | Ângulo do carro a esquerda. |
| `SpotterCarRightAngle` | Double |  | · | ✓ | Ângulo do carro a direita. |
| `TrackPositionPercent` | Double |  | S | ✓ | Posição na volta, 0.0-1.0. |
| `EngineIgnitionOn` | Int32 |  | C | ✓ | Ignição ligada (0/1). |
| `EngineStarted` | Int32 |  | C | ✓ | Motor funcionando (0/1). |
| `CarSettings_CurrentGearRedLineRPM` | Double |  | · | ✓ | Redline da marcha atual. |
| `DraftEstimate` | Double | oculta, calculada | · | ✓ | Estimativa de vácuo (oculto, calculado). |
| `GuessedElaspedGameTime` | TimeSpan | oculta, calculada | C | ✓ | Tempo de jogo estimado (oculto). |
| `SectorsCount` | Int32? |  | S |  | Número de setores da pista. |
| `PlayerLeaderboardPosition` | Int32 |  | · | ✓ | Índice do jogador no leaderboard do SimHub (usar com driver*()). |
| `HasMultipleClassOpponents` | Boolean |  | · | ✓ | Sessão multiclasse. |
| `IsSessionRestart` | Boolean |  | · | ✓ | A sessão acabou de reiniciar. |
| `PushToPassActive` | Boolean? |  | S |  | Push-to-pass ativo (quando o jogo informa). |
| `PitLimiterSpeed` | Double? |  | S |  | Velocidade do limitador de box, quando o jogo informa. |
| `GroundSpeedKmH` | Double? |  | S |  | Velocidade em relação ao solo, km/h (quando o jogo fornece). |
| `GroundSpeedLocal` | Double? |  | · |  | Idem na unidade local. |
| `Raw` | Object | não exposta | · |  | Objeto bruto do jogo. Não exposto aqui - usar GameRawData.*. |

`BestLapOpponent` (oculto) é um `Opponent` completo — o piloto dono da melhor volta da sessão — e expõe `DataCorePlugin.GameData.BestLapOpponent.<campo>` com os campos da tabela 5.4.

## 4. Suporte por jogo

Calculado a partir dos métodos `GD_*` de cada leitor (ver §1.5). S = fornecido pelo jogo, C = calculado pelo SimHub, — = não disponível. Só aparecem membros com alguma declaração. Leitores: iR = `IRacingManager`, ACC = `ACCManager`, AC = `ACManager`, ACE = `ACEVOManager`, LMU = `LMUManager`, rF2 = `RF2Manager`, AMS2 = `Automobilista2Manager`, R3E = `RREManager`, F1 25 = `CodemastersF12025Manager`, GT7 = `GT7Manager`.

| Membro | iR | ACC | AC | ACE | LMU | rF2 | AMS2 | R3E | F1 25 | GT7 |
|---|---|---|---|---|---|---|---|---|---|---|
| `ABSActive` | S | S | S | — | S | C | S | S | — | — |
| `ABSLevel` | S | — | S | — | S | S | S | S | S | — |
| `AirTemperature` | S | S | S | S | S | S | S | — | — | — |
| `AllTimeBest` | — | — | — | — | — | — | S | — | — | — |
| `BestLapTime` | S | S | S | — | S | S | S | S | S | S |
| `Brake` | S | S | S | S | S | S | S | S | S | S |
| `Handbrake` | S | — | — | — | — | — | S | — | — | — |
| `BrakeBias` | S | S | S | S | S | S | S | S | S | — |
| `BrakesTemperatureAvg` | C | C | C | C | C | C | C | C | C | C |
| `BrakesTemperatureMax` | C | C | C | C | C | C | C | C | C | C |
| `BrakesTemperatureMin` | C | C | C | C | C | C | C | C | C | C |
| `BrakeTemperatureFrontLeft` | — | S | S | S | S | S | S | S | S | — |
| `BrakeTemperatureFrontRight` | — | S | S | S | S | S | S | S | S | — |
| `BrakeTemperatureRearLeft` | — | S | S | S | S | S | S | S | S | — |
| `BrakeTemperatureRearRight` | — | S | S | S | S | S | S | S | S | — |
| `CarDamage1` | — | S | S | S | — | — | S | S | — | — |
| `CarDamage2` | — | S | S | S | — | — | S | S | — | — |
| `CarDamage3` | — | S | S | S | — | — | S | S | — | — |
| `CarDamage4` | — | S | S | S | — | — | S | — | — | — |
| `CarDamage5` | — | S | S | S | — | — | — | — | — | — |
| `CarDamagesAvg` | C | C | C | C | C | C | C | C | C | C |
| `CarDamagesMax` | C | C | C | C | C | C | C | C | C | C |
| `CarDamagesMin` | C | C | C | C | C | C | C | C | C | C |
| `CarModel` | S | S | S | S | S | S | S | S | S | S |
| `CarId` | S | S | S | S | S | S | S | S | S | S |
| `Clutch` | S | S | S | S | S | S | S | S | S | S |
| `CompletedLaps` | S | S | S | — | S | S | S | S | S | S |
| `CurrentLapTime` | S | S | S | — | S | S | S | S | S | S |
| `CurrentSectorIndex` | S | S | S | — | S | S | S | S | S | — |
| `DeltaToAllTimeBest` | — | S | S | — | — | — | — | — | — | — |
| `DeltaToSessionBest` | S | S | — | — | — | — | — | — | — | — |
| `DRSAvailable` | — | S | S | S | — | S | S | S | S | — |
| `DRSEnabled` | — | S | S | S | — | S | S | S | S | — |
| `EngineTorque` | — | — | — | — | S | S | S | — | — | — |
| `Flag_Black` | S | S | S | — | S | S | S | S | — | — |
| `Flag_Orange` | — | S | — | — | — | — | — | — | — | — |
| `Flag_Blue` | S | S | S | — | S | S | S | S | S | — |
| `Flag_Checkered` | S | S | S | — | — | — | S | S | — | — |
| `Flag_Green` | S | S | — | — | S | S | S | S | S | — |
| `Flag_Name` | C | C | C | C | C | C | C | C | C | C |
| `Flag_White` | S | S | S | — | — | — | S | S | — | — |
| `Flag_Yellow` | S | S | S | — | S | S | S | S | S | — |
| `Fuel` | S | S | S | S | S | S | S | S | S | S |
| `Throttle` | S | S | S | S | S | S | S | S | S | S |
| `Gear` | S | S | S | S | S | S | S | S | S | S |
| `IsInPit` | S | S | S | — | S | S | S | S | S | — |
| `IsInPitLane` | S | S | S | — | S | S | S | S | S | — |
| `LastLapTime` | S | S | S | — | S | S | S | S | S | S |
| `LastSectorTime` | C | C | C | C | C | C | C | C | C | C |
| `LastSectorTimeAnyLap` | C | C | C | C | C | C | C | C | C | C |
| `MapAllowed` | S | S | S | S | S | S | S | S | S | S |
| `MaxEngineTorque` | C | C | C | C | C | C | C | C | C | C |
| `MaxFuel` | S | S | S | — | S | S | S | S | S | S |
| `MaxRpm` | S | S | S | — | S | S | S | S | S | S |
| `MaxTurbo` | — | — | — | — | — | — | — | — | — | — |
| `OilPressure` | S | — | — | — | — | — | S | S | — | — |
| `OilTemperature` | S | — | — | — | S | S | S | S | S | S |
| `Opponents` | S | S | S | S | S | S | S | S | S | S |
| `PitLimiterOn` | S | S | S | S | S | S | S | S | S | — |
| `Position` | S | S | S | — | S | S | S | S | S | — |
| `RoadTemperature` | S | S | S | S | S | S | S | — | S | — |
| `Rpms` | S | S | S | S | S | S | S | S | S | S |
| `SessionTimeLeft` | S | S | S | — | S | S | S | S | S | — |
| `SessionTypeName` | S | S | S | — | S | S | S | S | S | — |
| `SpeedKmh` | S | S | S | S | S | S | S | S | S | S |
| `TCActive` | — | S | S | — | C | C | S | S | S | S |
| `TCLevel` | S | S | S | — | S | S | S | S | S | — |
| `TotalLaps` | S | S | S | — | S | S | S | S | S | S |
| `TrackConfig` | S | S | S | — | — | — | S | S | — | — |
| `TrackName` | S | S | S | — | S | S | S | S | S | — |
| `TrackId` | S | S | S | — | S | S | S | S | S | S |
| `Turbo` | — | S | S | S | S | S | S | — | — | S |
| `TyrePressureFrontLeft` | S | S | S | S | S | S | S | S | S | — |
| `TyrePressureFrontRight` | S | S | S | S | S | S | S | S | S | — |
| `TyrePressureRearLeft` | S | S | S | S | S | S | S | S | S | — |
| `TyrePressureRearRight` | S | S | S | S | S | S | S | S | S | — |
| `TyreDirtFrontLeft` | — | S | S | S | — | — | — | S | — | — |
| `TyreDirtFrontRight` | — | S | S | S | — | — | — | S | — | — |
| `TyreDirtRearLeft` | — | S | S | S | — | — | — | S | — | — |
| `TyreDirtRearRight` | — | S | S | S | — | — | — | S | — | — |
| `TyresDirtyLevelAvg` | C | C | C | C | C | C | C | C | C | C |
| `TyresDirtyLevelMax` | C | C | C | C | C | C | C | C | C | C |
| `TyresDirtyLevelMin` | C | C | C | C | C | C | C | C | C | C |
| `TyresTemperatureAvg` | C | C | C | C | C | C | C | C | C | C |
| `TyresTemperatureMax` | C | C | C | C | C | C | C | C | C | C |
| `TyresTemperatureMin` | C | C | C | C | C | C | C | C | C | C |
| `TyresWearAvg` | C | C | C | C | C | C | C | C | C | C |
| `TyresWearMax` | C | C | C | C | C | C | C | C | C | C |
| `TyresWearMin` | C | C | C | C | C | C | C | C | C | C |
| `TyreTemperatureFrontLeft` | S | S | S | S | S | S | S | S | S | S |
| `TyreTemperatureFrontRight` | S | S | S | S | S | S | S | S | S | S |
| `TyreTemperatureRearLeft` | S | S | S | S | S | S | S | S | S | S |
| `TyreTemperatureRearRight` | S | S | S | S | S | S | S | S | S | S |
| `TyreTemperatureFrontLeftInner` | S | S | S | S | S | S | S | S | S | — |
| `TyreTemperatureFrontLeftMiddle` | S | S | S | S | S | S | S | S | — | — |
| `TyreTemperatureFrontLeftOuter` | S | S | S | S | S | S | S | S | — | — |
| `TyreTemperatureFrontRightInner` | S | S | S | S | S | S | S | S | S | — |
| `TyreTemperatureFrontRightMiddle` | S | S | S | S | S | S | S | S | — | — |
| `TyreTemperatureFrontRightOuter` | S | S | S | S | S | S | S | S | — | — |
| `TyreTemperatureRearLeftInner` | S | S | S | S | S | S | S | S | S | — |
| `TyreTemperatureRearLeftMiddle` | S | S | S | S | S | S | S | S | — | — |
| `TyreTemperatureRearLeftOuter` | S | S | S | S | S | S | S | S | — | — |
| `TyreTemperatureRearRightInner` | S | S | S | S | S | S | S | S | S | — |
| `TyreTemperatureRearRightMiddle` | S | S | S | S | S | S | S | S | — | — |
| `TyreTemperatureRearRightOuter` | S | S | S | S | S | S | S | S | — | — |
| `TyreWearFrontLeft` | S | S | S | S | S | S | S | S | S | — |
| `TyreWearFrontRight` | S | S | S | S | S | S | S | S | S | — |
| `TyreWearRearLeft` | S | S | S | S | S | S | S | S | S | — |
| `TyreWearRearRight` | S | S | S | S | S | S | S | S | S | — |
| `WaterTemperature` | S | S | — | S | S | S | S | S | — | — |
| `Sector1Time` | — | S | S | S | S | S | S | S | S | — |
| `Sector2Time` | — | S | S | S | S | S | S | S | S | — |
| `Sector1LastLapTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector2LastLapTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector3LastLapTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector1BestLapTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector2BestLapTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector3BestLapTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector1BestTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector2BestTime` | C | C | C | C | C | C | C | C | C | C |
| `Sector3BestTime` | C | C | C | C | C | C | C | C | C | C |
| `OpponentsCount` | C | C | C | C | C | C | C | C | C | C |
| `PlayerClassOpponentsCount` | C | C | C | C | C | C | C | C | C | C |
| `PacketTime` | S | S | S | S | S | S | S | S | S | S |
| `MaxSpeedKmh` | C | C | C | C | C | C | C | C | C | C |
| `MaxSpeedMph` | C | C | C | C | C | C | C | C | C | C |
| `MaxSpeedLocal` | C | C | C | C | C | C | C | C | C | C |
| `DeltaToBest` | C | C | C | C | C | C | C | C | C | C |
| `DeltaToPlayer` | C | C | C | C | C | C | C | C | C | C |
| `TrackPositionPercent` | S | S | S | S | S | S | S | S | S | — |
| `TrackLength` | — | S | S | S | S | S | S | S | S | — |
| `TrackPositionMeters` | C | C | C | C | C | C | C | C | C | C |
| `OrientationPitch` | S | S | S | S | S | S | S | S | S | S |
| `OrientationYaw` | S | S | S | S | S | S | S | S | S | S |
| `OrientationRoll` | S | S | S | S | S | S | S | S | S | S |
| `AccelerationSway` | S | S | S | S | S | S | S | S | S | S |
| `AccelerationSurge` | S | S | S | S | S | S | S | S | S | S |
| `AccelerationHeave` | S | S | S | S | S | S | S | S | S | S |
| `RollChangeVelocity` | — | — | — | — | — | — | — | S | — | — |
| `PitchChangeVelocity` | — | — | — | — | — | — | — | S | — | — |
| `YawChangeVelocity` | — | — | — | — | — | — | — | S | — | — |
| `ERSMax` | S | S | S | — | — | — | S | — | S | S |
| `ERSStored` | S | S | S | — | — | — | S | — | S | S |
| `TurnIndicatorLeft` | — | S | — | — | — | — | — | — | — | — |
| `TurnIndicatorRight` | — | S | — | — | — | — | — | — | — | — |
| `EngineMap` | — | S | — | — | — | — | — | S | S | — |
| `SpotterCarLeft` | S | S | S | S | S | S | S | S | S | S |
| `SpotterCarRight` | S | S | S | S | S | S | S | S | S | S |
| `EngineIgnitionOn` | C | S | C | S | S | S | C | S | C | C |
| `EngineStarted` | C | S | C | S | C | C | C | S | C | C |
| `GuessedElaspedGameTime` | C | C | C | C | C | C | C | C | C | C |
| `SectorsCount` | S | S | S | — | S | S | S | S | S | S |
| `PushToPassActive` | S | S | — | S | — | — | — | S | — | — |
| `PitLimiterSpeed` | S | S | S | S | S | S | S | S | S | S |
| `GroundSpeedKmH` | S | S | S | S | S | S | S | S | S | S |

<details><summary>Todos os 121 leitores de jogo encontrados</summary>

`ACCManager`, `ACCSpectatorManager`, `ACEVOManager`, `ACManager`, `ATSManagerV2`, `Automobilista2Manager`, `Automobilista2UDPPManager`, `AutomobilistaManager`, `BeamNgManager`, `BeamNgManagerExtra`, `BMWM3CHALLENGEManager`, `CodemastersDirt2Manager`, `CodemastersDirt3Manager`, `CodemastersDirt4Manager`, `CodemastersDirtRally2Manager`, `CodemastersDirtRallyManager`, `CodemastersDirtShowdownManager`, `CodemastersExtradata1Manager`, `CodemastersF12012Manager`, `CodemastersF12013Manager`, `CodemastersF12014Manager`, `CodemastersF12015Manager`, `CodemastersF12016Manager`, `CodemastersF12017Manager`, `CodemastersF12018Manager`, `CodemastersF12019Manager`, `CodemastersF12020Manager`, `CodemastersF12021Manager`, `CodemastersF12022Manager`, `CodemastersF12023Manager`, `CodemastersF12024Manager`, `CodemastersF12025Manager`, `CodemastersGrid2019Manager`, `CodemastersGrid2Manager`, `CodemastersGridAutosportManager`, `CodemastersGridLegendsManager`, `CodemastersManager`, `CodemastersRaceDriverGridManager`, `CodemastersWRC23Manager`, `Condor2Manager`, `Condor3Manager`, `CondorManager`, `ControllerGameManager`, `CopaPetrobrasDeMarcasManager`, `CSGOManager`, `DCSManager`, `Dota2Manager`, `Drift21Manager`, `EliteDangerousManager`, `EpicRollerCoastersManager`, `ETS2ManagerV2`, `eXpanSIMManager`, `FarmingSimulatorManager19Manager`, `FarmingSimulatorManager22Manager`, `FarmingSimulatorManager25Manager`, `FernbusManager`, `FH4Manager`, `FH5Manager`, `FlightSimulatorManager`, `FlightSimulatorManager24`, `FM7Manager`, `FM8Manager`, `FormulaTruck2013Manager`, `FuridashiManager`, `GPBikesManager`, `GRallyManager`, `GT7Manager`, `GTA5ManualTransmissionManager`, `GTR2IWManager`, `GTSportManager`, `HydroSimManager`, `IL2Manager`, `IRacingManager`, `KartKraftManager`, `KRPManager`, `LFSManager`, `LMUManager`, `MotoGP18Manager`, `MXBikesManager`, `NascarHeat4Manager`, `NascarHeat5Manager`, `NoLimits2Manager`, `NR2003Manager`, `OMSI2Manager`, `PCars2Manager`, `PCars2ManagerLegacy`, `PCars2UDPManager`, `PCars3Manager`, `PCars3UDPManager`, `PCarsManager`, `ProjectMotorRacingManager`, `ProjectRCManager`, `RBRManager`, `RBRNGPManager`, `RDSTheOfficialDriftVideoGame`, `RF2Manager`, `RF2SpectatorManager`, `RFManager`, `RREManager`, `SIMBINGTLegendsManager`, `SIMBINGTR2Manager`, `SIMBINGTR2ManagerLegacy`, `SIMBINGTRManager`, `SimBinManager`, `SIMBINRace07Manager`, `SIMBINRaceWTCCManager`, `SIMBINVolvoTheGameManager`, `SRXTheGame`, `StockCarExtremeManager`, `TDUSCManager`, `TonyStewartsAllAmericanRacingManager`, `TonyStewartsSprintCarRacingManager`, `TrackmaniaManager`, `TrackmaniaTurboManager`, `TrainSimulatorManager`, `WarThunderReader`, `WRC10Manager`, `WRCGenerationsManager`, `WRCManager`, `Wreckfest2Manager`, `XPlaneManager`

</details>

## 5. Pilotos e leaderboard (funções driver*)

Como `Opponents` é uma lista, o SimHub não a expõe como propriedade. O acesso é por funções de fórmula (NCalc e JS), indexadas pela **posição no leaderboard** (1 = líder). Para "quem está à frente na pista" use `getopponentleaderboardposition_aheadbehind(-1)` e passe o resultado para `driver*()`, ou as propriedades `PersistantTrackerPlugin.DriverAhead_NN_*` (§7.1) / `IRacingExtraProperties` (§8.1).

### 5.1 `driver<campo>(posição)`
| Função | Descrição (texto original do SimHub) |
|---|---|
| `driveravailable(pos)` | if a driver is available |
| `driverisplayer(pos)` | if the driver is the actual player |
| `drivername(pos)` | the driver's name |
| `driverinitials(pos)` | the driver's name initials |
| `drivershortname(pos)` | the driver's short name (F. Lastname) |
| `drivercarclass(pos)` | the driver's car class |
| `driverbestlap(pos)` | the driver's best lap time |
| `driverlastlap(pos)` | the driver's last lap time |
| `driverdeltatoplayer(pos)` | the driver's delta to the current player best lap |
| `drivercurrentlap(pos)` | the driver's current lap |
| `driverid(pos)` | the driver's unique id |
| `drivercarnumber(pos)` | the driver's car number |
| `driveriscarinpit(pos)` | if the driver car is in Pit |
| `driveriscaringarage(pos)` | if the driver car is in garage (RFactor2) |
| `driveriracingirating(pos)` | the driver's IRating |
| `drivercarname(pos)` | the driver's car name |
| `driverisconnected(pos)` | if the driver is connected (Iracing) |
| `driveriscarinpitlane(pos)` | if the driver car is in Pit lane |
| `drivertrackpositionpercent(pos)` | the driver's track position (0.0 to 1.0) |
| `drivercurrentlaphighprecision(pos)` | the driver's guessed lap in the race including the actual lap percent (0.0 to X.0) |
| `driverdeltatobest(pos)` | the driver's delta to the opponent's best lap |
| `driverclassposition(pos)` | the driver's position in his own class |
| `driverposition(pos)` | the driver's race position  |
| `driverisoutlap(pos)` | if the driver is in first lap after pit out |
| `drivercurrentsector(pos)` | the driver's current sector (starting from 1) |
| `driverbestlapsector1(pos)` | the driver's best lap sector 1 time |
| `driverbestlapsector2(pos)` | the driver's best lap sector 2 time |
| `driverbestlapsector3(pos)` | the driver's best lap sector 3 time |
| `driverlastlapsector1(pos)` | the driver's last finished lap sector 1 time |
| `driverlastlapsector2(pos)` | the driver's last finished lap sector 2 time |
| `driverlastlapsector3(pos)` | the driver's last finished lap sector 3 time |
| `drivercurrrentlapsector1(pos)` | the driver's current lap sector 1 time |
| `drivercurrrentlapsector2(pos)` | the driver's current lap sector 2 time |
| `driverbestsector1sectortime(pos)` | the driver's session best sector 1 time (Time for the sector only) |
| `driverbestsector2sectortime(pos)` | the driver's session best sector 2 time (Time for the sector only) |
| `driverbestsector3sectortime(pos)` | the driver's session best sector 3 time (Time for the sector only) |
| `driverbestlapsector1sectortime(pos)` | the driver's session best lap sector 1 time (Time for the sector only) |
| `driverbestlapsector2sectortime(pos)` | the driver's session best lap sector 2 time (Time for the sector only) |
| `driverbestlapsector3sectortime(pos)` | the driver's session best lap sector 3 time (Time for the sector only) |
| `driverlastlapsector1sectortime(pos)` | the driver's last finished lap sector 1 time (Time for the sector only) |
| `driverlastlapsector2sectortime(pos)` | the driver's last finished lap sector 2 time (Time for the sector only) |
| `driverlastlapsector3sectortime(pos)` | the driver's last finished lap sector 3 time (Time for the sector only) |
| `drivercurrentlapsector1time(pos)` | the driver's current lap sector 1 time (Time for the sector only) |
| `drivercurrentlapsector2time(pos)` | the driver's current lap sector 2 time (Time for the sector only) |
| `driverspeed(pos)` | the actual driver speed (in local unit) |
| `driverrelativegaptoplayer(pos)` | the driver's relative gap to player |
| `driverrelativedistancetoplayer(pos)` | the driver's relative distance to player |
| `drivergaptoleader(pos)` | the driver's gap to the leader |
| `drivergaptoplayer(pos)` | the driver's gap to the player |
| `driverlapstoplayer(pos)` | the driver's laps to player |
| `driverlapstoleader(pos)` | the driver's laps to race leader |
| `drivergaptoleadercombined(pos)` | the driver's gap to the leader (laps or gap) |
| `driverrelativegaptoplayercombined(pos)` | the driver's gap to the player (laps or gap) |
| `drivergaptoclassleadercombined(pos)` | the driver's gap to the player's class leader (laps or gap) |
| `driverlapstoclassleader(pos)` | the driver's laps to his own class leader |
| `drivergaptoclassleader(pos)` | the driver's gap to his own class leader |
| `driverteamname(pos)` | the driver's team name |
| `driverclubname(pos)` | the driver's club name (Iracing) |
| `driverlicencestring(pos)` | the driver's licence string (Iracing) |
| `drivercarclasscolor(pos)` | the driver's car class color (Privided by Iracing, autoassigned otherwise) |
| `drivercarclasstextcolor(pos)` | the driver's car class text color (White or black to be readable over car class color) |
| `driverfronttyrecompound(pos)` | the driver's front tyre compound (S,H,W ... ) |
| `driverreartyrecompound(pos)` | the driver's rear tyre compound (S,H,W ... ) |
| `driverfronttyrecompoundgamecode(pos)` | the driver's front tyre compound as reported by the game |
| `driverreartyrecompoundgamecode(pos)` | the driver's rear tyre compound code as reported by the game |
| `drivertimesincelastpitout(pos)` | how much time the driver's drove since the last pit exit (guessed) |
| `driverlapsdonesincelastpitout(pos)` | how many laps driver's drove since the last pit exit (0.0 to X.0, guessed) |
| `driverpitenteratlap(pos)` | at which lap the driver's entered the pit the last time |
| `driverpitcount(pos)` | how many time the driver went to pits (guessed) |
| `driverpitlastduration(pos)` | how long the last pit stop took (guessed) |
| `drivercurrentlaptime(pos)` | current lap time (guessed) |
| `driversplitdeltaself(pos)` | driver's last completed sector delta against his own best lap |
| `driversplitdeltabestopponent(pos)` | driver's last completed sector delta against the session's best lap opponent |
| `driverpositiongain(pos)` | driver's position gains since the start of the race/connection |
| `driverpositiongainclass(pos)` | driver's position gains in his own class since the start of the race/connection |
| `driverstartposition(pos)` | driver's position at the start of the race/connection |
| `driverstartpositionclass(pos)` | driver's position gains in his own class at the start of the race/connection |
| `driverpushtopassstatus(pos)` | driver's P2P status (IRacing only) |
| `driverpushtopasscount(pos)` | driver's P2P count (IRacing only) |

Também: `isplayer(pos)` (= `driverisplayer`).

### 5.2 `driversector<campo>(posição, setor, acumulado)`
| Função | Descrição |
|---|---|
| `driversectorbestlap(pos, setor, acumulado)` | the driver's best lap sector time |
| `driversectorlastlap(pos, setor, acumulado)` | the driver's last finished lap sector time |
| `driversectorcurrentlap(pos, setor, acumulado)` | the driver's current lap sector time |
| `driversectorbest(pos, setor, acumulado)` | the driver's session best sector time (Theorical time of cumulated best sectors of the session) |

### 5.3 Localizar pilotos e classes
| Função | Descrição |
|---|---|
| `getplayerleaderboardposition()` | Returns the leaderboard position of the current player |
| `getopponentleaderboardposition_aheadbehind(relativeindex)` | Returns the leaderboard position of the player's ahead/behind on track opponents (relativeindex : 0 = player, -1 the first opponent ahead, 1 the first opponent behind etc ... |
| `getopponentleaderboardposition_aheadbehind_playerclassonly(relativeindex)` | Returns the leaderboard position of the player's ahead/behind on track opponents for the player class (relativeindex : 0 = player, -1 the first opponent ahead, 1 the first opponent behind etc ... |
| `getopponentleaderboardposition_playerclassonly(leaderboardposition)` | Returns the leaderboard position of opponents of the same class as player (leaderboardposition : 1 first opponent of the class ...) |
| `getbestlapopponentleaderboardposition()` | Returns the leaderboard position of opponent having the best lap time of the session. |
| `getbestlapopponentleaderboardposition_playerclassonly()` | Returns the leaderboard position of the opponent of the same class as player having the best lap time of the session. |
| `getbestsplitleaderboardposition(sectorindex)` | Returns the leaderboard position of opponent having the best split time of the session (sectorindex starts from 1). |
| `getbestsplittime(sectorindex)` | Returns the the best sector split time of the session (sectorindex starts from 1). |
| `getbestsplitleaderboardposition_playerclassonly(sectorindex)` | Returns the leaderboard position of opponent of the same class as player having the best split time of the session (sectorindex starts from 1). |
| `getbestsplittime_playerclassonly(sectorindex)` | Returns the the best sector split time of the session of opponents of the same class as player (sectorindex starts from 1). |
| `getleaderboardcarclassname(classindex)` | Returns the class name of the nth car class of the leaderboard (classindex : 1 first class of the leaderboard ...) |
| `getleaderboardcarclasscount()` | Returns how many car classes are available in the leaderboard |
| `getleaderboardcarclasscolor(classindex)` | Returns the class color of the nth car class of the leaderboard (classindex : 1 first class of the leaderboard ...) |
| `getleaderboardcarclasstextcolor(classindex)` | Returns the class text color of the nth car class of the leaderboard (classindex : 1 first class of the leaderboard ...) |
| `getleaderboardcarclassopponentscount(classindex)` | Returns the number of opponenents of the nth car class of the leaderboard (classindex : 1 first class of the leaderboard ...) |

### 5.4 Campos do objeto `Opponent`
Tipos lidos de `GameReaderCommon.Opponent` (é o que `driver*()` consulta e o que aparece em `GameData.BestLapOpponent.*`).

| Campo | Tipo | Flags |
|---|---|---|
| `BestLapSector1` | Double? | obsoleto |
| `BestLapSector2` | Double? | obsoleto |
| `BestLapSector3` | Double? | obsoleto |
| `LastLapSector1` | Double? | obsoleto |
| `LastLapSector2` | Double? | obsoleto |
| `LastLapSector3` | Double? | obsoleto |
| `BestSector1` | Double? | obsoleto |
| `BestSector2` | Double? | obsoleto |
| `BestSector3` | Double? | obsoleto |
| `PitRequested` | Boolean? |  |
| `Id` | String |  |
| `Name` | String |  |
| `TeamName` | String |  |
| `ShortName` | String |  |
| `LapValid` | Boolean |  |
| `Initials` | String |  |
| `ClubName` | String |  |
| `LicenceString` | String |  |
| `CarClassColor` | String |  |
| `CarClassTextColor` | String |  |
| `IsConnected` | Boolean |  |
| `IsCarInGarage` | Boolean? |  |
| `IsCarInPit` | Boolean |  |
| `IsCarInPitLane` | Boolean |  |
| `Position` | Int32 |  |
| `LivePosition` | Int32 |  |
| `PositionInClass` | Int32 |  |
| `Coordinates` | Double[] | objeto |
| `CarName` | String |  |
| `CarClass` | String |  |
| `CarClassID` | String |  |
| `IsPlayer` | Boolean |  |
| `BestLapTime` | TimeSpan |  |
| `LastLapTime` | TimeSpan |  |
| `DeltaToBest` | Double? | calculado |
| `DeltaToPlayer` | Double? | calculado |
| `IRacing_IRating` | Double? |  |
| `TrackPositionPercent` | Double? |  |
| `TrackPositionPercentRaw` | Double? |  |
| `CurrentLap` | Int32? |  |
| `CurrentLapHighPrecision` | Double? |  |
| `CarNumber` | String |  |
| `Speed` | Double? |  |
| `GaptoLeader` | Double? |  |
| `GaptoClassLeader` | Double? |  |
| `GaptoLeaderSimHub` | Double? |  |
| `LapsToLeader` | Int32? |  |
| `LapsToClassLeader` | Int32? |  |
| `LapsToPlayer` | Int32? |  |
| `GaptoPlayer` | Double? |  |
| `GapToLeaderCombined` | String |  |
| `GapToPlayerCombined` | String |  |
| `GapToClassLeaderCombined` | String |  |
| `TrackPositionPercentToPlayer` | Double? |  |
| `RelativeGapToPlayer` | Double? |  |
| `RelativeDistanceToPlayer` | Double? |  |
| `RelativeCoordinatesToPlayer` | PointF? | objeto |
| `RelativeVectorAngleToPlayer` | Double |  |
| `RelativeVectorLengthToPlayer` | Double |  |
| `DraftEstimate` | Double |  |
| `CurrentLapSectorTimes` | SectorTimes | objeto |
| `LastLapSectorTimes` | SectorTimes | objeto |
| `BestLapSectorTimes` | SectorTimes | objeto |
| `FrontTyreCompoundGameCode` | String |  |
| `RearTyreCompoundGameCode` | String |  |
| `FrontTyreCompound` | String |  |
| `RearTyreCompound` | String |  |
| `ExtraData` | List<Object> | objeto |
| `PitOutAtTime` | DateTime? |  |
| `PitOutSince` | TimeSpan? |  |
| `PitOutLapsDoneSince` | Double? |  |
| `IsOutLap` | Boolean |  |
| `PitCount` | Int32? |  |
| `PitOutAtLap` | Double? |  |
| `PitEnterAtTime` | DateTime? |  |
| `PitEnterAtLap` | Double? |  |
| `PitLastDuration` | TimeSpan? |  |
| `GuessedLapStartTime` | DateTime? |  |
| `CurrentLapTime` | TimeSpan? |  |
| `StandingStillInPitLaneSince` | DateTime? |  |
| `StandingStillInPitLane` | Boolean |  |
| `CurrentSector` | Int32? |  |
| `StartPosition` | Int32? |  |
| `StartPositionClass` | Int32? |  |
| `SplitDeltaSelf` | Double? |  |
| `SplitDeltaBestLapOpponent` | Double? |  |
| `RacePositionGain` | Int32? |  |
| `RacePositionClassGain` | Int32? |  |
| `DidNotFinish` | Boolean? |  |
| `DidNotQualify` | Boolean? |  |
| `P2PCount` | Int32? |  |
| `P2PStatus` | Boolean? |  |

## 6. GameRawData do iRacing

Dados crus do leitor (`IRacingReader.DataSampleEx`, que implementa `IExposable`). O `GetValues()` expõe exatamente:

- `GameRawData.Telemetry.<var>` — variáveis do irsdk (dicionário; **arrays ficam de fora**);
- `GameRawData.Telemetry.SessionFlagsDetails.Is<flag>` — cada bit de `SessionFlags` como booleano;
- `GameRawData.SessionData.*` — o YAML da sessão já tipado;
- `GameRawData.CurrentSessionInfo.*` — a sessão corrente (`SessionInfo.SessionsNN` da sessão ativa; nulo fora de sessão).

Prefixo `DataCorePlugin.` opcional aqui (§1.2). Arrays `CarIdx*` (posições, % de volta, pneus etc. de cada carro) não viram propriedade. O `Telemetry` é um `Dictionary<string, object>` com propriedades tipadas, e `NewRawData()` no JavaScript devolve o objeto cru — então `NewRawData().Telemetry.CarIdxLapDistPct[idx]` deve funcionar em sessão (não testado aqui: fora de sessão `NewRawData()` devolve null). Outros dashboards instalados já leem o objeto cru assim (`NewRawData().Cars[...]`, de outro jogo).

### 6.1 Telemetry (variáveis presentes na amostra do SimHub)
Fonte da lista: `PluginsData\IRacing\SampleTelemetry.json` (366 variáveis; o conjunto real depende do carro). Exemplo = valor na amostra.

| Variável | Tipo | Ao vivo | Exemplo |
|---|---|---|---|
| `SessionTime` | float | ✓ | 4020.2167154948 |
| `SessionTick` | int | ✓ | 11734 |
| `SessionNum` | int | ✓ | 0 |
| `SessionState` | int | ✓ | 4 |
| `SessionUniqueID` | int | ✓ | 1 |
| `SessionFlags` | int | ✓ | 268435456 |
| `SessionTimeRemain` | float | ✓ | -1.0 |
| `SessionLapsRemain` | int | ✓ | 32767 |
| `SessionLapsRemainEx` | int | ✓ | 32767 |
| `SessionTimeTotal` | float | ✓ | 7200.0 |
| `SessionLapsTotal` | int | ✓ | 32767 |
| `SessionJokerLapsRemain` | int | ✓ | 0 |
| `SessionOnJokerLap` | bool | ✓ | false |
| `SessionTimeOfDay` | float | ✓ | 57720.0 |
| `RadioTransmitCarIdx` | int | ✓ | -1 |
| `RadioTransmitRadioIdx` | int | ✓ | 0 |
| `RadioTransmitFrequencyIdx` | int | ✓ | 0 |
| `DisplayUnits` | int | ✓ | 1 |
| `DriverMarker` | bool | ✓ | false |
| `PushToTalk` | bool | ✓ | false |
| `PushToPass` | bool | ✓ | false |
| `ManualBoost` | bool | ✓ | false |
| `ManualNoBoost` | bool | ✓ | false |
| `IsOnTrack` | bool | ✓ | false |
| `IsReplayPlaying` | bool | ✓ | false |
| `ReplayFrameNum` | int | ✓ | 0 |
| `ReplayFrameNumEnd` | int | ✓ | 0 |
| `IsDiskLoggingEnabled` | bool | ✓ | true |
| `IsDiskLoggingActive` | bool | ✓ | false |
| `FrameRate` | float | ✓ | 22.0719471 |
| `CpuUsageFG` | float | ✓ | 0.953748643 |
| `GpuUsage` | float | ✓ | 0.201233581 |
| `ChanAvgLatency` | float | ✓ | 0.165655434 |
| `ChanLatency` | float | ✓ | 0.166666672 |
| `ChanQuality` | float | ✓ | 1.00815487 |
| `ChanPartnerQuality` | float | ✓ | 0.979999959 |
| `CpuUsageBG` | float | ✓ | 0.673666656 |
| `ChanClockSkew` | float | ✓ | -0.116666667 |
| `MemPageFaultSec` | float | ✓ | 135.0 |
| `MemSoftPageFaultSec` | float | ✓ | 54867.0 |
| `PlayerCarPosition` | int | ✓ | -1 |
| `PlayerCarClassPosition` | int | ✓ | -1 |
| `PlayerCarClass` | int | ✓ | 0 |
| `PlayerTrackSurface` | int | ✓ | -1 |
| `PlayerTrackSurfaceMaterial` | int | ✓ | -1 |
| `PlayerCarIdx` | int | ✓ | 15 |
| `PlayerCarTeamIncidentCount` | int | ✓ | 0 |
| `PlayerCarMyIncidentCount` | int | ✓ | 0 |
| `PlayerCarDriverIncidentCount` | int | ✓ | 0 |
| `PlayerCarWeightPenalty` | float | ✓ | 0.0 |
| `PlayerCarPowerAdjust` | float | ✓ | 0.0 |
| `PlayerCarDryTireSetLimit` | int | ✓ | 0 |
| `PlayerCarTowTime` | float | ✓ | 0.0 |
| `PlayerCarInPitStall` | bool | ✓ | false |
| `PlayerCarPitSvStatus` | int | ✓ | 0 |
| `PlayerTireCompound` | int | ✓ | -1 |
| `PlayerFastRepairsUsed` | int | ✓ | 0 |
| `PaceMode` | int | ✓ | 4 |
| `OnPitRoad` | bool | ✓ | false |
| `SteeringWheelAngle` | float | ✓ | 0.0 |
| `Throttle` | float | ✓ | 0.0 |
| `Brake` | float | ✓ | 0.0 |
| `Clutch` | float | ✓ | 0.0 |
| `Gear` | int | ✓ | -1 |
| `RPM` | float | ✓ | 0.0 |
| `PlayerCarSLFirstRPM` | float | ✓ | 7300.0 |
| `PlayerCarSLShiftRPM` | float | ✓ | 7900.0 |
| `PlayerCarSLLastRPM` | float | ✓ | 8700.0 |
| `PlayerCarSLBlinkRPM` | float | ✓ | 9100.0 |
| `Lap` | int | ✓ | 0 |
| `LapCompleted` | int | ✓ | 0 |
| `LapDist` | float | ✓ | 0.0 |
| `LapDistPct` | float | ✓ | 0.0 |
| `RaceLaps` | int | ✓ | 0 |
| `CarDistAhead` | float | ✓ | 500000.0 |
| `CarDistBehind` | float | ✓ | 500000.0 |
| `LapBestLap` | int | ✓ | 0 |
| `LapBestLapTime` | float | ✓ | 0.0 |
| `LapLastLapTime` | float | ✓ | 0.0 |
| `LapCurrentLapTime` | float | ✓ | 0.0 |
| `LapLasNLapSeq` | int | ✓ | 0 |
| `LapLastNLapTime` | float | ✓ | 0.0 |
| `LapBestNLapLap` | int | ✓ | 0 |
| `LapBestNLapTime` | float | ✓ | 0.0 |
| `LapDeltaToBestLap` | float | ✓ | 0.0 |
| `LapDeltaToBestLap_DD` | float | ✓ | 0.0 |
| `LapDeltaToBestLap_OK` | bool | ✓ | false |
| `LapDeltaToOptimalLap` | float | ✓ | 0.0 |
| `LapDeltaToOptimalLap_DD` | float | ✓ | 0.0 |
| `LapDeltaToOptimalLap_OK` | bool | ✓ | false |
| `LapDeltaToSessionBestLap` | float | ✓ | 0.0 |
| `LapDeltaToSessionBestLap_DD` | float | ✓ | 0.0 |
| `LapDeltaToSessionBestLap_OK` | bool | ✓ | false |
| `LapDeltaToSessionOptimalLap` | float | ✓ | 0.0 |
| `LapDeltaToSessionOptimalLap_DD` | float | ✓ | 0.0 |
| `LapDeltaToSessionOptimalLap_OK` | bool | ✓ | false |
| `LapDeltaToSessionLastlLap` | float | ✓ | 0.0 |
| `LapDeltaToSessionLastlLap_DD` | float | ✓ | 0.0 |
| `LapDeltaToSessionLastlLap_OK` | bool | ✓ | false |
| `Speed` | float | ✓ | 0.0 |
| `Yaw` | float | ✓ | 0.0 |
| `YawNorth` | float | ✓ | 0.0 |
| `Pitch` | float | ✓ | 0.0 |
| `Roll` | float | ✓ | 0.0 |
| `EnterExitReset` | int | ✓ | 0 |
| `TrackTemp` | float | ✓ | 24.9850845 |
| `TrackTempCrew` | float | ✓ | 24.9850845 |
| `AirTemp` | float | ✓ | 18.9850845 |
| `TrackWetness` | int | ✓ | 0 |
| `Skies` | int | ✓ | 2 |
| `AirDensity` | float | ✓ | 1.1433475 |
| `AirPressure` | float | ✓ | 96662.11 |
| `WindVel` | float | ✓ | 4.97918272 |
| `WindDir` | float | ✓ | 2.25060439 |
| `RelativeHumidity` | float | ✓ | 0.9478711 |
| `FogLevel` | float | ✓ | 0.0 |
| `Precipitation` | float | ✓ | 0.0 |
| `SolarAltitude` | float | ✓ | 0.8753556 |
| `SolarAzimuth` | float | ✓ | 4.182666 |
| `WeatherDeclaredWet` | bool | ✓ | false |
| `SteeringFFBEnabled` | bool | ✓ | true |
| `DCLapStatus` | int | ✓ | 2 |
| `DCDriversSoFar` | int | ✓ | 1 |
| `OkToReloadTextures` | bool | ✓ | true |
| `LoadNumTextures` | bool | ✓ | false |
| `CarLeftRight` | int | ✓ | 0 |
| `PitsOpen` | bool | ✓ | true |
| `VidCapEnabled` | bool | ✓ | false |
| `VidCapActive` | bool | ✓ | false |
| `PitRepairLeft` | float | ✓ | 0.0 |
| `PitOptRepairLeft` | float | ✓ | 0.0 |
| `PitstopActive` | bool | ✓ | false |
| `FastRepairUsed` | int | ✓ | 0 |
| `FastRepairAvailable` | int | ✓ | 0 |
| `LFTiresUsed` | int | ✓ | 0 |
| `RFTiresUsed` | int | ✓ | 0 |
| `LRTiresUsed` | int | ✓ | 0 |
| `RRTiresUsed` | int | ✓ | 0 |
| `LeftTireSetsUsed` | int | ✓ | 0 |
| `RightTireSetsUsed` | int | ✓ | 0 |
| `FrontTireSetsUsed` | int | ✓ | 0 |
| `RearTireSetsUsed` | int | ✓ | 0 |
| `TireSetsUsed` | int | ✓ | 0 |
| `LFTiresAvailable` | int | ✓ | 0 |
| `RFTiresAvailable` | int | ✓ | 0 |
| `LRTiresAvailable` | int | ✓ | 0 |
| `RRTiresAvailable` | int | ✓ | 0 |
| `LeftTireSetsAvailable` | int | ✓ | 0 |
| `RightTireSetsAvailable` | int | ✓ | 0 |
| `FrontTireSetsAvailable` | int | ✓ | 0 |
| `RearTireSetsAvailable` | int | ✓ | 0 |
| `TireSetsAvailable` | int | ✓ | 0 |
| `CamCarIdx` | int | ✓ | 15 |
| `CamCameraNumber` | int | ✓ | 7 |
| `CamGroupNumber` | int | ✓ | 10 |
| `CamCameraState` | int | ✓ | 83 |
| `IsOnTrackCar` | bool | ✓ | false |
| `IsInGarage` | bool | ✓ | false |
| `SteeringWheelAngleMax` | float | ✓ | 8.796033 |
| `ShiftPowerPct` | float | ✓ | 0.0 |
| `ShiftGrindRPM` | float | ✓ | 0.0 |
| `ThrottleRaw` | float | ✓ | 0.0 |
| `BrakeRaw` | float | ✓ | 0.0 |
| `ClutchRaw` | float | ✓ | 0.0 |
| `HandbrakeRaw` | float | ✓ | 0.0 |
| `BrakeABSactive` | bool | ✓ | false |
| `EngineWarnings` | int | ✓ | 0 |
| `FuelLevelPct` | float | ✓ | 0.0 |
| `PitSvFlags` | int | ✓ | 0 |
| `PitSvLFP` | float | ✓ | 0.0 |
| `PitSvRFP` | float | ✓ | 0.0 |
| `PitSvLRP` | float | ✓ | 0.0 |
| `PitSvRRP` | float | ✓ | 0.0 |
| `PitSvFuel` | float | ✓ | 0.0 |
| `PitSvTireCompound` | int | ✓ | 0 |
| `P2P_Status` | bool | ✓ | false |
| `P2P_Count` | int | ✓ | 0 |
| `SteeringWheelPctTorque` | float | ✓ | 0.0 |
| `SteeringWheelPctTorqueSign` | float | ✓ | 0.0 |
| `SteeringWheelPctTorqueSignStops` | float | ✓ | 0.0 |
| `SteeringWheelPctIntensity` | float | ✓ | 0.0 |
| `SteeringWheelPctSmoothing` | float | ✓ | 0.0 |
| `SteeringWheelPctDamper` | float | ✓ | 0.0 |
| `SteeringWheelLimiter` | float | ✓ | 0.0 |
| `SteeringWheelMaxForceNm` | float | ✓ | 40.969738 |
| `SteeringWheelPeakForceNm` | float | ✓ | -1.0 |
| `SteeringWheelUseLinear` | bool | ✓ | true |
| `ShiftIndicatorPct` | float | ✓ | 0.0 |
| `ReplayPlaySpeed` | int | ✓ | 0 |
| `ReplayPlaySlowMotion` | bool | ✓ | false |
| `ReplaySessionTime` | float | ✓ | 0.0 |
| `ReplaySessionNum` | int | ✓ | -1 |
| `TireLF_RumblePitch` | float | ✓ | 0.0 |
| `TireRF_RumblePitch` | float | ✓ | 0.0 |
| `TireLR_RumblePitch` | float | ✓ | 0.0 |
| `TireRR_RumblePitch` | float | ✓ | 0.0 |
| `IsGarageVisible` | bool | ✓ | false |
| `SteeringWheelTorque` | float | ✓ | 0.0 |
| `VelocityZ` | float | ✓ | 0.0 |
| `VelocityY` | float | ✓ | 0.0 |
| `VelocityX` | float | ✓ | 0.0 |
| `YawRate` | float | ✓ | 0.0 |
| `PitchRate` | float | ✓ | 0.0 |
| `RollRate` | float | ✓ | 0.0 |
| `VertAccel` | float | ✓ | 0.0 |
| `LatAccel` | float | ✓ | 0.0 |
| `LongAccel` | float | ✓ | 0.0 |
| `dcStarter` | bool | ✓ | false |
| `dcPitSpeedLimiterToggle` | bool | ✓ | false |
| `dcTearOffVisor` | bool | ✓ | false |
| `dpTireChange` | float | ✓ | 0.0 |
| `dpFastRepair` | float | ✓ | 0.0 |
| `dcDashPage` | float | ✓ | 0.0 |
| `dcBrakeBias` | float | ✓ | 0.0 |
| `dpLFTireColdPress` | float | ✓ | 0.0 |
| `dpRFTireColdPress` | float | ✓ | 0.0 |
| `dpLRTireColdPress` | float | ✓ | 0.0 |
| `dpRRTireColdPress` | float | ✓ | 0.0 |
| `dcThrottleShape` | float | ✓ | 0.0 |
| `dcTractionControl` | float | ✓ | 0.0 |
| `FuelUsePerHour` | float | ✓ | 0.0 |
| `Voltage` | float | ✓ | 12.0 |
| `WaterTemp` | float | ✓ | 77.0 |
| `WaterLevel` | float | ✓ | 9.0 |
| `FuelPress` | float | ✓ | 0.0 |
| `OilTemp` | float | ✓ | 77.0 |
| `OilPress` | float | ✓ | 0.0 |
| `OilLevel` | float | ✓ | 9.0 |
| `ManifoldPress` | float | ✓ | 1.0 |
| `FuelLevel` | float | ✓ | 0.0 |
| `Engine0_RPM` | float | ✓ | 0.000194199849 |
| `RRbrakeLinePress` | float | ✓ | 0.0 |
| `RRcoldPressure` | float | ✓ | 131.000763 |
| `RRtempCL` | float | ✓ | 51.7386475 |
| `RRtempCM` | float | ✓ | 51.7386475 |
| `RRtempCR` | float | ✓ | 51.7386475 |
| `RRwearL` | float | ✓ | 1.0 |
| `RRwearM` | float | ✓ | 1.0 |
| `RRwearR` | float | ✓ | 1.0 |
| `LRbrakeLinePress` | float | ✓ | 0.0 |
| `LRcoldPressure` | float | ✓ | 131.000763 |
| `LRtempCL` | float | ✓ | 51.7386475 |
| `LRtempCM` | float | ✓ | 51.7386475 |
| `LRtempCR` | float | ✓ | 51.7386475 |
| `LRwearL` | float | ✓ | 1.0 |
| `LRwearM` | float | ✓ | 1.0 |
| `LRwearR` | float | ✓ | 1.0 |
| `RFbrakeLinePress` | float | ✓ | 0.0 |
| `RFcoldPressure` | float | ✓ | 137.89476 |
| `RFtempCL` | float | ✓ | 51.66501 |
| `RFtempCM` | float | ✓ | 51.66501 |
| `RFtempCR` | float | ✓ | 51.66501 |
| `RFwearL` | float | ✓ | 1.0 |
| `RFwearM` | float | ✓ | 1.0 |
| `RFwearR` | float | ✓ | 1.0 |
| `LFbrakeLinePress` | float | ✓ | 0.0 |
| `LFcoldPressure` | float | ✓ | 137.89476 |
| `LFtempCL` | float | ✓ | 51.66501 |
| `LFtempCM` | float | ✓ | 51.66501 |
| `LFtempCR` | float | ✓ | 51.66501 |
| `LFwearL` | float | ✓ | 1.0 |
| `LFwearM` | float | ✓ | 1.0 |
| `LFwearR` | float | ✓ | 1.0 |
| `LFSHshockDefl` | float | ✓ | 0.0222069081 |
| `LFSHshockVel` | float | ✓ | -0.09453203 |
| `RFSHshockDefl` | float | ✓ | 0.0222069081 |
| `RFSHshockVel` | float | ✓ | -0.09451205 |
| `LRshockDefl` | float | ✓ | 0.111313246 |
| `LRshockVel` | float | ✓ | -0.0595179349 |
| `RRshockDefl` | float | ✓ | 0.111313246 |
| `RRshockVel` | float | ✓ | -0.0594980232 |
| `TickCount` | int | ✓ | 20 |
| `TractionControlSwitch` | int | ✓ | 0 |
| `TractionControlSetting` | float | ✓ | 0.0 |
| `PlayerP2P_Count` | int | ✓ | -1 |
| `PlayerP2P_Status` | bool | ✓ | false |
| `EstimatedLapAltitude` | int | ✓ | 0 |
| `dcDRSToggle` | bool | ✓ | false |
| `dpWingFront` | float | ✓ | 0.0 |
| `dcBrakeBiasFine` | float | ✓ | 0.0 |
| `dcPeakBrakeBias` | float | ✓ | 0.0 |
| `dcBrakeMisc` | float | ✓ | 0.0 |
| `dcEngineBraking` | float | ✓ | 0.0 |
| `dcMGUKDeployMode` | float | ✓ | 0.0 |
| `dcDiffEntry` | float | ✓ | 0.0 |
| `dcDiffMiddle` | float | ✓ | 0.0 |
| `dcDiffExit` | float | ✓ | 0.0 |
| `DRS_Status` | int | ✓ | 0 |
| `PowerMGU_K` | float | ✓ | 0.0 |
| `TorqueMGU_K` | float | ✓ | 0.0 |
| `PowerMGU_H` | float | ✓ | 0.0 |
| `EnergyERSBattery` | float | ✓ | 4000000.0 |
| `EnergyERSBatteryPct` | float | ✓ | 1.0 |
| `EnergyBatteryToMGU_KLap` | float | ✓ | 0.0 |
| `EnergyMGU_KLapDeployPct` | float | ✓ | 0.0 |
| `CFshockDefl` | float | ✓ | 0.110482939 |
| `CFshockVel` | float | ✓ | 9.595361e-09 |
| `ROLLFshockDefl` | float | ✓ | -2.98023224e-07 |
| `ROLLFshockVel` | float | ✓ | -2.83087e-08 |
| `CRshockDefl` | float | ✓ | 0.0117385387 |
| `CRshockVel` | float | ✓ | -3.81133924e-09 |
| `ROLLRshockDefl` | float | ✓ | 1.1920929e-07 |
| `ROLLRshockVel` | float | ✓ | -3.69406039e-09 |
| `PlayerIncidents` | int | ✓ | 0 |
| `Shifter` | int | ✓ | 0 |
| `RRodometer` | float | ✓ | 0.0 |
| `LRodometer` | float | ✓ | 0.0 |
| `RFodometer` | float | ✓ | 0.0 |
| `LFodometer` | float | ✓ | 0.0 |
| `dpFuelFill` | float | ✓ | 0.0 |
| `dpFuelAutoFillEnabled` | float | ✓ | 0.0 |
| `dpFuelAutoFillActive` | float | ✓ | 0.0 |
| `dpFuelAddKg` | float | ✓ | 95.0 |

Arrays na amostra (não expostos como propriedade): `CarIdxLap`[64], `CarIdxLapCompleted`[64], `CarIdxLapDistPct`[64], `CarIdxTrackSurface`[64], `CarIdxTrackSurfaceMaterial`[64], `CarIdxOnPitRoad`[64], `CarIdxPosition`[64], `CarIdxClassPosition`[64], `CarIdxClass`[64], `CarIdxF2Time`[64], `CarIdxEstTime`[64], `CarIdxLastLapTime`[64], `CarIdxBestLapTime`[64], `CarIdxBestLapNum`[64], `CarIdxTireCompound`[64], `CarIdxQualTireCompound`[64], `CarIdxQualTireCompoundLocked`[64], `CarIdxFastRepairsUsed`[64], `CarIdxSessionFlags`[64], `CarIdxPaceLine`[64], `CarIdxPaceRow`[64], `CarIdxPaceFlags`[64], `CarIdxSteer`[64], `CarIdxRPM`[64], `CarIdxGear`[64], `CarIdxP2P_Status`[64], `CarIdxP2P_Count`[64], `SteeringWheelTorque_ST`[6], `VelocityZ_ST`[6], `VelocityY_ST`[6], `VelocityX_ST`[6], `YawRate_ST`[6], `PitchRate_ST`[6], `RollRate_ST`[6], `VertAccel_ST`[6], `LatAccel_ST`[6], `LongAccel_ST`[6], `LFSHshockDefl_ST`[6], `LFSHshockVel_ST`[6], `RFSHshockDefl_ST`[6], `RFSHshockVel_ST`[6], `LRshockDefl_ST`[6], `LRshockVel_ST`[6], `RRshockDefl_ST`[6], `RRshockVel_ST`[6], `CFshockDefl_ST`[6], `CFshockVel_ST`[6], `ROLLFshockDefl_ST`[6], `ROLLFshockVel_ST`[6], `CRshockDefl_ST`[6], `CRshockVel_ST`[6], `ROLLRshockDefl_ST`[6], `ROLLRshockVel_ST`[6]

### 6.2 SessionFlagsDetails
| Propriedade | Bit | Ao vivo |
|---|---|---|
| `GameRawData.Telemetry.SessionFlagsDetails.Ischeckered` | 1 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Iswhite` | 2 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isgreen` | 4 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isyellow` | 8 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isred` | 16 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isblue` | 32 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isdebris` | 64 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Iscrossed` | 128 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsyellowWaving` | 256 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsoneLapToGreen` | 512 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsgreenHeld` | 1024 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IstenToGo` | 2048 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsfiveToGo` | 4096 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsrandomWaving` | 8192 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Iscaution` | 16384 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IscautionWaving` | 32768 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isblack` | 65536 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isdisqualify` | 131072 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isservicible` | 262144 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isfurled` | 524288 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.Isrepair` | 1048576 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsstartHidden` | 268435456 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsstartReady` | 536870912 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsstartSet` | 1073741824 | ✓ |
| `GameRawData.Telemetry.SessionFlagsDetails.IsstartGo` | 2147483648 | ✓ |

### 6.3 Enums úteis do irsdk
| Variável | Valores |
|---|---|
| `SessionState` | 0 Invalid, 1 GetInCar, 2 Warmup, 3 ParadeLaps, 4 Racing, 5 Checkered, 6 CoolDown |
| `PlayerTrackSurface` / `CarIdxTrackSurface` | -1 NotInWorld, 0 OffTrack, 1 InPitStall, 2 AproachingPits, 3 OnTrack |
| `EngineWarnings` (bits) | 1 WaterTemp, 2 FuelPressure, 4 OilPressure, 8 EngineStalled, 16 PitSpeedLimiter, 32 RevLimiterActive |

### 6.4 SessionData (estrutura tipada)
Árvore lida do tipo `IRacingReader.SessionData`. `[i]` vira `NN` começando em **01** (`DriverInfo.Drivers01` = primeiro da lista do YAML). Os campos são os que o SimHub tipou; o YAML real pode ter mais. Os que são `String` no YAML (ex.: `TrackLength = "6.93 km"`) chegam como texto com unidade.

| Caminho (após `GameRawData.`) | Tipo | Ao vivo |
|---|---|---|
| `SessionData.WeekendInfo.TrackName` | String | ✓ |
| `SessionData.WeekendInfo.TrackID` | Int64 | ✓ |
| `SessionData.WeekendInfo.TrackLength` | String | ✓ |
| `SessionData.WeekendInfo.TrackDisplayName` | String | ✓ |
| `SessionData.WeekendInfo.TrackDisplayShortName` | String | ✓ |
| `SessionData.WeekendInfo.TrackConfigName` | String |  |
| `SessionData.WeekendInfo.TrackCity` | String | ✓ |
| `SessionData.WeekendInfo.TrackCountry` | String | ✓ |
| `SessionData.WeekendInfo.TrackAltitude` | String | ✓ |
| `SessionData.WeekendInfo.TrackLatitude` | String | ✓ |
| `SessionData.WeekendInfo.TrackLongitude` | String | ✓ |
| `SessionData.WeekendInfo.TrackNorthOffset` | String |  |
| `SessionData.WeekendInfo.TrackNumTurns` | Int64 | ✓ |
| `SessionData.WeekendInfo.TrackPitSpeedLimit` | String | ✓ |
| `SessionData.WeekendInfo.TrackType` | String | ✓ |
| `SessionData.WeekendInfo.TrackWeatherType` | String | ✓ |
| `SessionData.WeekendInfo.TrackSkies` | String | ✓ |
| `SessionData.WeekendInfo.TrackSurfaceTemp` | String | ✓ |
| `SessionData.WeekendInfo.TrackAirTemp` | String | ✓ |
| `SessionData.WeekendInfo.TrackAirPressure` | String | ✓ |
| `SessionData.WeekendInfo.TrackWindVel` | String | ✓ |
| `SessionData.WeekendInfo.TrackWindDir` | String | ✓ |
| `SessionData.WeekendInfo.TrackRelativeHumidity` | String | ✓ |
| `SessionData.WeekendInfo.TrackFogLevel` | String | ✓ |
| `SessionData.WeekendInfo.TrackCleanup` | Int64 | ✓ |
| `SessionData.WeekendInfo.TrackDynamicTrack` | Int64 | ✓ |
| `SessionData.WeekendInfo.SeriesID` | Int64 | ✓ |
| `SessionData.WeekendInfo.SeasonID` | Int64 | ✓ |
| `SessionData.WeekendInfo.SessionID` | Int64 | ✓ |
| `SessionData.WeekendInfo.SubSessionID` | Int64 | ✓ |
| `SessionData.WeekendInfo.LeagueID` | Int64 | ✓ |
| `SessionData.WeekendInfo.Official` | Int64 | ✓ |
| `SessionData.WeekendInfo.RaceWeek` | Int64 | ✓ |
| `SessionData.WeekendInfo.EventType` | String | ✓ |
| `SessionData.WeekendInfo.Category` | String | ✓ |
| `SessionData.WeekendInfo.SimMode` | String | ✓ |
| `SessionData.WeekendInfo.TeamRacing` | Int64 | ✓ |
| `SessionData.WeekendInfo.MinDrivers` | Int64 | ✓ |
| `SessionData.WeekendInfo.MaxDrivers` | Int64 | ✓ |
| `SessionData.WeekendInfo.DCRuleSet` | String | ✓ |
| `SessionData.WeekendInfo.QualifierMustStartRace` | Int64 | ✓ |
| `SessionData.WeekendInfo.NumCarClasses` | Int64 | ✓ |
| `SessionData.WeekendInfo.NumCarTypes` | Int64 | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.NumStarters` | Int64 | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.StartingGrid` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.QualifyScoring` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.CourseCautions` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.StandingStart` | Int64 | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.Restarts` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.WeatherType` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.Skies` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.WindDirection` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.WindSpeed` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.WeatherTemp` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.RelativeHumidity` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.FogLevel` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.Unofficial` | Int64 | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.CommercialMode` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.NightMode` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.IsFixedSetup` | Int64 | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.StrictLapsChecking` | String | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.HasOpenRegistration` | Int64 | ✓ |
| `SessionData.WeekendInfo.WeekendOptions.HardcoreLevel` | Int64 | ✓ |
| `SessionData.WeekendInfo.TelemetryOptions.TelemetryDiskFile` | String | ✓ |
| `SessionData.SessionInfo.SessionsNN.SessionNum` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.SessionLaps` | String | ✓ |
| `SessionData.SessionInfo.SessionsNN.SessionTime` | String | ✓ |
| `SessionData.SessionInfo.SessionsNN.SessionNumLapsToAvg` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.SessionType` | String | ✓ |
| `SessionData.SessionInfo.SessionsNN.SessionTrackRubberState` | String |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.Position` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.ClassPosition` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.CarIdx` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.Lap` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.Time` | Double |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.FastestLap` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.FastestTime` | Double |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.LastTime` | Double |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.LapsLed` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.LapsComplete` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.LapsDriven` | Double |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.Incidents` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.ReasonOutId` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.ReasonOutStr` | String |  |
| `SessionData.SessionInfo.SessionsNN.ResultsPositionsNN.JokerLapsComplete` | Int64 |  |
| `SessionData.SessionInfo.SessionsNN.ResultsFastestLapNN.CarIdx` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsFastestLapNN.FastestLap` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsFastestLapNN.FastestTime` | Double | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsAverageLapTime` | Double | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsNumCautionFlags` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsNumCautionLaps` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsNumLeadChanges` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsLapsComplete` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.ResultsOfficial` | Int64 | ✓ |
| `SessionData.SessionInfo.SessionsNN.IsRace` | Boolean | ✓ |
| `SessionData.SessionInfo.SessionsNN._SessionLaps` | Int32 | ✓ |
| `SessionData.SessionInfo.SessionsNN._SessionTime` | Double | ✓ |
| `SessionData.SessionInfo.SessionsNN.IsLimitedSessionLaps` | Boolean | ✓ |
| `SessionData.SessionInfo.SessionsNN.IsLimitedTime` | Boolean | ✓ |
| `SessionData.CameraInfo.GroupsNN.GroupNum` | Int64 |  |
| `SessionData.CameraInfo.GroupsNN.GroupName` | String |  |
| `SessionData.CameraInfo.GroupsNN.CamerasNN.CameraNum` | Int64 |  |
| `SessionData.CameraInfo.GroupsNN.CamerasNN.CameraName` | String |  |
| `SessionData.RadioInfo.SelectedRadioNum` | Int64 | ✓ |
| `SessionData.RadioInfo.RadiosNN.RadioNum` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.HopCount` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.NumFrequencies` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.TunedToFrequencyNum` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.ScanningIsOn` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.FrequencyNum` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.FrequencyName` | String |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.Priority` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.CarIdx` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.EntryIdx` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.ClubID` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.CanScan` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.CanSquawk` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.Muted` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.IsMutable` | Int64 |  |
| `SessionData.RadioInfo.RadiosNN.FrequenciesNN.IsDeletable` | Int64 |  |
| `SessionData.DriverInfo.DriverCarIdx` | Int64 | ✓ |
| `SessionData.DriverInfo.PaceCarIdx` | Int64 | ✓ |
| `SessionData.DriverInfo.DriverHeadPosX` | Double | ✓ |
| `SessionData.DriverInfo.DriverHeadPosY` | Double | ✓ |
| `SessionData.DriverInfo.DriverHeadPosZ` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarIdleRPM` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarRedLine` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarFuelKgPerLtr` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarFuelMaxLtr` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarMaxFuelPct` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarSLFirstRPM` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarSLShiftRPM` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarSLLastRPM` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarSLBlinkRPM` | Double | ✓ |
| `SessionData.DriverInfo.DriverPitTrkPct` | Double | ✓ |
| `SessionData.DriverInfo.DriverCarEstLapTime` | Double | ✓ |
| `SessionData.DriverInfo.DriverSetupName` | String |  |
| `SessionData.DriverInfo.DriverSetupIsModified` | Int64 | ✓ |
| `SessionData.DriverInfo.DriverSetupLoadTypeName` | String |  |
| `SessionData.DriverInfo.DriverSetupPassedTech` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.ClubName` | String |  |
| `SessionData.DriverInfo.DriversNN.CarIdx` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.UserName` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.AbbrevName` | String |  |
| `SessionData.DriverInfo.DriversNN.Initials` | String |  |
| `SessionData.DriverInfo.DriversNN.UserID` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.TeamID` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.TeamName` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarNumber` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarNumberRaw` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarPath` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarClassID` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarID` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarIsPaceCar` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarIsAI` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarScreenName` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarScreenNameShort` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarClassShortName` | String |  |
| `SessionData.DriverInfo.DriversNN.CarClassRelSpeed` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarClassLicenseLevel` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarClassMaxFuel` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarClassMaxFuelPct` | String |  |
| `SessionData.DriverInfo.DriversNN.CarClassWeightPenalty` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarClassColor` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarClassEstLapTime` | Double | ✓ |
| `SessionData.DriverInfo.DriversNN.IRating` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.LicLevel` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.LicSubLevel` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.LicString` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.LicColor` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.IsSpectator` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarDesignStr` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.HelmetDesignStr` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.SuitDesignStr` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarNumberDesignStr` | String | ✓ |
| `SessionData.DriverInfo.DriversNN.CarSponsor_1` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.CarSponsor_2` | Int64 | ✓ |
| `SessionData.DriverInfo.DriversNN.IsPaceCar` | Boolean | ✓ |
| `SessionData.SplitTimeInfo.SectorsNN.SectorNum` | Int64 |  |
| `SessionData.SplitTimeInfo.SectorsNN.SectorStartPct` | Double |  |
| `SessionData.CarSetup.Chassis.InCarDials.BrakePressureBias` | String |  |
| `SessionData.CarSetup.Chassis.InCarDials.AbsSwitch` | String |  |
| `SessionData.CarSetup.Chassis.InCarDials.AbsSetting` | String |  |
| `SessionData.CarSetup.Chassis.InCarDials.TractionControlSwitch` | String |  |
| `SessionData.CarSetup.Chassis.InCarDials.TractionControlSetting` | String |  |
| `SessionData.CarSetup.Chassis.InCarDials.EngineMapSetting` | String |  |
| `SessionData.Raw` | String |  |
| `SessionData.InfoUpdate` | Int32 | ✓ |
| `CurrentSessionInfo.SessionNum` | Int64 | ✓ |
| `CurrentSessionInfo.SessionLaps` | String |  |
| `CurrentSessionInfo.SessionTime` | String |  |
| `CurrentSessionInfo.SessionNumLapsToAvg` | Int64 | ✓ |
| `CurrentSessionInfo.SessionType` | String |  |
| `CurrentSessionInfo.SessionTrackRubberState` | String |  |
| `CurrentSessionInfo.IsRace` | Boolean | ✓ |
| `CurrentSessionInfo._SessionLaps` | Int32 | ✓ |
| `CurrentSessionInfo._SessionTime` | Double | ✓ |
| `CurrentSessionInfo.IsLimitedSessionLaps` | Boolean | ✓ |
| `CurrentSessionInfo.IsLimitedTime` | Boolean | ✓ |

`DriverInfo.CompetingDrivers` tem os mesmos campos de `Drivers` (só pilotos competindo, sem pace car/espectador). `CurrentSessionInfo` tem os mesmos campos de `SessionInfo.SessionsNN`. `CarSetup.Chassis.InCarDials.*` só existe para carros que publicam esses dials.

## 7. Plugins do SimHub

### 7.1 Statistics / PersistantTracker
Prefixo `PersistantTrackerPlugin.` — ativo.

Plugin "Statistics" (classe `PersistantTrackerPlugin`). Gera os deltas ao vivo, histórico de voltas e os pilotos vizinhos na pista. Eventos `NewAllTimeBest`, `NewRecord`, `NewSessionBest`; ações `ClearLapHistory`, `DiscardCurrentMap`.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `DriverAhead_NN_Name` | String |  | Nome — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_ShortName` | String |  | Nome curto — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_Initials` | String |  | Iniciais — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_Distance` | Double | ✓ | Distância na pista até o jogador — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_Gap` | Double | ✓ | Gap em segundos — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_GapToPlayer` | Double | ✓ | Gap ao jogador — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_RaceGapToPlayer` | String |  | Gap ao jogador formatado (tempo ou voltas) — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_RaceGapToLeader` | String |  | Gap ao líder formatado — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_Position` | Int32 | ✓ | Posição — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_CarName` | String |  | Carro — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_CarNumber` | String |  | Número — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_CarClass` | String |  | Classe — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_IRating` | Double | ✓ | iRating — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_CurrentLap` | Int32 | ✓ | Volta atual — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_LastLapTime` | TimeSpan | ✓ | Última volta — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_BestLapTime` | TimeSpan | ✓ | Melhor volta — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_LapsToPlayer` | Int32 | ✓ | Voltas de diferença para o jogador — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_LapsToLeader` | Int32 | ✓ | Voltas de diferença para o líder — piloto NN à frente na pista (00..04). |
| `DriverAhead_NN_Speed` | Double | ✓ | Velocidade — piloto NN à frente na pista (00..04). |
| `DriverBehind_NN_Name` | String |  | Nome — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_ShortName` | String |  | Nome curto — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_Initials` | String |  | Iniciais — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_Distance` | Double | ✓ | Distância na pista até o jogador — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_Gap` | Double | ✓ | Gap em segundos — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_GapToPlayer` | Double | ✓ | Gap ao jogador — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_RaceGapToPlayer` | String |  | Gap ao jogador formatado (tempo ou voltas) — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_RaceGapToLeader` | String |  | Gap ao líder formatado — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_Position` | Int32 | ✓ | Posição — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_CarName` | String |  | Carro — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_CarNumber` | String |  | Número — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_CarClass` | String |  | Classe — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_IRating` | Double | ✓ | iRating — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_CurrentLap` | Int32 | ✓ | Volta atual — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_LastLapTime` | TimeSpan | ✓ | Última volta — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_BestLapTime` | TimeSpan | ✓ | Melhor volta — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_LapsToPlayer` | Int32 | ✓ | Voltas de diferença para o jogador — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_LapsToLeader` | Int32 | ✓ | Voltas de diferença para o líder — piloto NN atrás na pista (00..04). |
| `DriverBehind_NN_Speed` | Double | ✓ | Velocidade — piloto NN atrás na pista (00..04). |
| `PreviousLap_NN` | TimeSpan | ✓ | Tempo da volta anterior N (00 = mais recente, até 09). |
| `PreviousLap_NN_DeltaToAllTimeBest` | Double | ✓ | Delta dessa volta contra a melhor de todos os tempos. |
| `PreviousLap_NN_DeltaToSessionBest` | Double | ✓ | Delta contra a melhor da sessão. |
| `PreviousLap_NN_DeltaToBest` | Double | ✓ | Delta contra a melhor (oculta). |
| `PreviousLap_NN_IsCurrentSession` | Int32 | ✓ | A volta é da sessão atual (0/1). |
| `EstimatedLapTime` | TimeSpan | ✓ | Volta estimada (oculta). |
| `EstimatedLapTime_AllTimeBestBased` | TimeSpan | ✓ | Volta estimada com base no recorde pessoal. |
| `EstimatedLapTime_SessionBestBased` | TimeSpan | ✓ | Volta estimada com base na melhor da sessão. |
| `EstimatedLapTime_SessionBestBasedSimhub` | TimeSpan | ✓ | Idem, cálculo do SimHub. |
| `EstimatedLapTime_SessionBestBasedSimhub_EstimatedDelta` | Double | ✓ | Delta estimado dessa estimativa. |
| `EstimatedLapTime_SessionBestBasedSimhub_ReferenceLapTime` | TimeSpan | ✓ | Volta de referência usada. |
| `AllTimeBest` | TimeSpan | ✓ | Tempo de referência (melhor de todos os tempos). |
| `AllTimeBestLastLapDelta` | Double | ✓ | Delta da última volta contra a referência (s). |
| `AllTimeBestLiveDelta` | TimeSpan | ✓ | Delta ao vivo (oculta). |
| `AllTimeBestLiveDeltaSeconds` | Double | ✓ | Delta ao vivo em segundos. |
| `AllTimeBestLiveDeltaProgressSeconds` | Double | ✓ | Variação do delta (ganhando/perdendo) em segundos. |
| `SessionBest` | TimeSpan | ✓ | Tempo de referência (melhor da sessão). |
| `SessionBestLastLapDelta` | Double | ✓ | Delta da última volta contra a referência (s). |
| `SessionBestLiveDelta` | TimeSpan | ✓ | Delta ao vivo (oculta). |
| `SessionBestLiveDeltaSeconds` | Double | ✓ | Delta ao vivo em segundos. |
| `SessionBestLiveDeltaProgressSeconds` | Double | ✓ | Variação do delta (ganhando/perdendo) em segundos. |

### 7.2 System Info
Prefixo `SystemInfoPlugin.` — sempre ativo.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `CPULoadPercent` | Double | ✓ | Uso de CPU %. |
| `MemoryLoadPercent` | Double | ✓ | Uso de memória %. |
| `SimHubProcessor` | Double | ✓ | CPU usada pelo SimHub %. |
| `Uptime` | TimeSpan | ✓ | Tempo ligado do Windows. |

### 7.3 SystemInfosProvider (agregador de sensores e mídia)
Prefixo `SystemInfosProvider.` — sempre ativo.

O mapeamento de cada campo para um sensor fica em `PluginsData\Common\SystemInfosProvider.SystemInfosProvider.json`. Fontes: `AfterburnerPlugin.*` (`AfterburnerConnected` + um nome por sensor do MSI Afterburner, ex. `AfterburnerPlugin.GLOBAL.Framerate_FPS`), `Aida64Plugin.*` (`Aida64Connected` + sensores), `HWinfoPlugin.*` (sensores). Os nomes dos sensores vêm do programa externo, não do SimHub. Ações: `MediaNext`, `MediaPlayPause`, `MediaPrevious`.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `MainCPUTemp` | Double |  | Temperatura da CPU (da fonte escolhida: Afterburner/HWiNFO/Aida64/SimHub). |
| `MainCPULoad` | Double |  | Carga da CPU. |
| `MainCPUFanSpeed` | Double |  | Ventoinha da CPU. |
| `MainGPUTemp` | Double |  | Temperatura da GPU. |
| `MainGPULoad` | Double |  | Carga da GPU. |
| `MainGPUFanSpeed` | Double |  | Ventoinha da GPU. |
| `CurrentFrameRate` | Double |  | FPS do jogo. |
| `MemoryLoad` | Double |  | Uso de memória. |
| `Title` | String |  | Título da mídia tocando (Windows). |
| `Artist` | String |  | Artista da mídia. |
| `MonitorPowerStatus` | Boolean | ✓ | Monitor ligado. |

### 7.4 ShakeIt Bass Shakers / Motors
Prefixo `ShakeITBSV3Plugin.` — ativo.

O mesmo conjunto existe com prefixo `ShakeITMotorsV3Plugin.` (ShakeIt Motors). Ações: `MainFeedbackLevelIncrement/Decrement`, `ToggleMuteFeedback`, `ResetCalibration`.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `GlobalGain` | Double | ✓ | Ganho global. |
| `IsMuted` | Int32 | ✓ | Mudo (0/1). |
| `<efeito>...` | Double |  | Cada efeito/saída configurado exporta seu valor (ExportProperties) — nomes vêm da configuração do usuário. |

### 7.5 ShakeIt Wind
Prefixo `ShakeItWindPlugin.` — ativo.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `ActiveMode` | String | ✓ | Modo ativo (Static/Dynamic). |
| `ActiveModeGain` | Double | ✓ | Ganho do modo ativo. |
| `ActiveModeIsEnabled` | Boolean | ✓ | Modo ativo habilitado. |
| `OutputLeft` | Double | ✓ | Saída esquerda. |
| `OutputCenter` | Double | ✓ | Saída central. |
| `OutputRight` | Double | ✓ | Saída direita. |
| `<Modo>.Gain / .IsEnabled / .OutputLeft / .OutputCenter / .OutputRight` | Double/Int32 |  | Por modo (`Static`, `Dynamic`). |

### 7.6 Arduino (SerialDash)
Prefixo `SerialDashPlugin.` — ativo.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `CurrentLedLayout` | String |  | Perfil de LEDs ativo. |
| `DisplayIntensity` | Int32 | ✓ | Brilho dos displays. |
| `RGBIntensity` | Int32 | ✓ | Brilho dos LEDs RGB. |
| `BlinkTriggerRatioChanged` | Int32 |  | Mudou o limiar de pisca. |
| `RPMStartOffset` | Object | ✓ | Offset de RPM. |
| `GLCDTemplate / OLEDTemplate / SCREEN_<n>` | Int32 |  | Tela ativa de cada display GLCD/OLED. |

### 7.7 Controllers input (joystick)
Prefixo `JoystickPlugin.` — ativo.

Botões aparecem também como `InputStatus.JoystickPlugin.<Dispositivo>_B<n>` (usado por mapeamentos). Os dispositivos desta máquina estão em `PluginsData\Common\JoystickPluginSettings.json`: `Realdrive_DD_T112`, `Volante_PRS-Formula`, `PedalDS`.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `<Dispositivo>_<Botão>` | Int32? |  | Estado de cada botão/eixo dos controles habilitados. |

### 7.8 Áudio
Prefixo `AudioControlPlugin.` — **desabilitado** nesta instalação.

Classe `AudioPlayPlugin` registra `SoundsVolume` e as ações `Play_<som>`, `IncrementSoundsVolume`, `DecrementSoundsVolume`.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `AudioPeak` | Double |  | Pico de áudio. |
| `AudioPeakLeft` | Double |  | Pico canal esquerdo. |
| `AudioPeakRight` | Double |  | Pico canal direito. |
| `AudioFFT_Range_<n>` | Double |  | Faixas de FFT. |
| `SoundsVolume` | Int32 | ✓ | Volume dos sons tocados pelo plugin. |

### 7.9 Web
Prefixo `WebPlugin.` — sempre ativo.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `ServerBaseUrl` | String | ✓ | URL do servidor web do SimHub na rede. |

### 7.10 Outros plugins nativos
Prefixo `HeadsetInfo.` — **desabilitado** nesta instalação.

Demais (todos **desabilitados** aqui, exceto onde indicado):

- `ThrustmastersPlugin.` — `OverallGain`, `DefaultWheelAngle`, `WheelDetected` (Int32).
- `BeltTensionnerPlugin.` — `Status.Left`, `Status.Right`, `Status.LeftWithoutAutoCenter`, `Status.RightWithoutAutoCenter` (Double).
- `SimuLightPlugin.` — `AdalightEnabled`, `AdalightDarkMode`, `AdalightGlobalBrightness`, `OtherLightsEnabled`, `OtherLightsDarkMode`, `OtherLightsGlobalBrightness`, `CaptureFreeze`.
- `MotionPlugin.` — `Global.MotionEnabled`, `Global.MotionSuspended`, `Global.DeviceState`, `Global.ActiveMotionSetup`, `Global.ActiveProfilePreset`, `Global.GlobalMotionSmoothing`, `Global.MotionDetailAmplifier.Enabled/Gain`, `Global.BeltTensioner.KeepParked/Offset`, `Global.TrackProfiler.*` (CurrentLapValidForProfiling, TrackRecordsCount, MaxPitch, MinPitch, SmoothedMaxPitch, SmoothedMinPitch, CurrentPositionTrackPitch, IsClosedTrack), `Global.GeometryPrimaryOverflow`, `Global.GeometryOverflowScaling*`, `MotionCompensationComponent.<nome>.*` e por efeito `<efeito>.Enabled/.Gain/.Smoothing/.IsMuted/.IsIsolated/.Washout/.EnableWashout`.
- `ControlMapperPlugin.` — estado de cada papel mapeado.
- `KeyboardEmulatorPlugin` (ativo) não registra propriedades; só ações.

| Nome | Tipo | Ao vivo | Descrição |
|---|---|---|---|
| `BatteryLevel` | Int32 |  | Headset Logitech G533: bateria %. |
| `BatteryVoltage` | Double |  | Tensão. |
| `Status` | String |  | Unplugged/Sleeping/Full/Charging/Discharging. |

### 7.11 Propriedades criadas pelo usuário
- `DataCorePlugin.CustomExpression.<nome>` — expressões personalizadas.
- `DataCorePlugin.ExternalScript.<nome>` — blocos `[ExportProperty]` dos scripts em `NCalcScripts\*.ini` (o `samples.ini` instalado gera, por exemplo, `DataCorePlugin.ExternalScript.BlinkingGear` — conferido: 200). `[ExportEvent]` vira o evento `DataCorePlugin.ExternalScript.<nome>`; `[ExportLed]` não vira propriedade.
- `DataCorePlugin.Debug_<nome>` — pontos de gráfico de depuração.
- `variable.<nome>` / `[variable.x]` — variáveis de dashboard do Dash Studio (escopo do dash, não globais).

## 8. Plugins de terceiros instalados

### 8.1 RSC — iRacing Extra Properties
Prefixo `IRacingExtraProperties.` — ativo. Lista de nomes do próprio autor (`RSC.iRacingExtraProperties.txt`, 586 famílias); faixas medidas agora variando o primeiro `NN` (o segundo `NN`, quando existe, ficou em 00). O plugin informa ter **28364** propriedades registradas (`IRacingExtraProperties.PropertyCount`).

<details><summary><code>Chat*</code> — 3 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `Chat_Message_NN` |  | 1..10 | ✓ |
| `Chat_Message_NN_LastSent` |  | 1..10 | ✓ |
| `Chat_Message_LastSent` | String |  | ✓ |

</details>

<details><summary><code>CurrentSector*</code> — 3 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `CurrentSector_BestTime` | TimeSpan |  | ✓ |
| `CurrentSector_Index` | Int32 |  | ✓ |
| `CurrentSector_Time` | TimeSpan |  | ✓ |

</details>

<details><summary><code>EnableVideo*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `EnableVideo` | Boolean |  | ✓ |

</details>

<details><summary><code>FPS*</code> — 2 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `FPS_Red_Threshold` | String |  | ✓ |
| `FPS_Yellow_Threshold` | String |  | ✓ |

</details>

<details><summary><code>FuelToAddMode*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `FuelToAddMode` | String |  | ✓ |

</details>

<details><summary><code>GapTrackingReady*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `GapTrackingReady` | Boolean |  | ✓ |

</details>

<details><summary><code>Hybrid*</code> — 7 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `Hybrid_Deploy` | Double |  | ✓ |
| `Hybrid_DeployMode` | String |  | ✓ |
| `Hybrid_DeployModeColor` | String |  | ✓ |
| `Hybrid_DeployModeTextColor` | String |  | ✓ |
| `Hybrid_LastLap_Deploy` | Int32 |  | ✓ |
| `Hybrid_LastLap_SoC` | Int32 |  | ✓ |
| `Hybrid_SoC` | Double |  | ✓ |

</details>

<details><summary><code>iRacing_AirTemperatureChange*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_AirTemperatureChange` | String |  | ✓ |

</details>

<details><summary><code>iRacing_Class*</code> — 36 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_Class_NN_Leaderboard_Driver_NN_AbbrevName` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_BestLapTime` | TimeSpan | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_CarName` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_CarNumber` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_ClassColor` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_ClassName` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_ClubName` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_CurrentLap` | Int32? | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_DeltaToBest` | Double | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_GapChangeLastLap` | TimeSpan | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_GapToLeaderString` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_Initials` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_Interval` | Double? | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_IntervalString` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_iRating` | Double | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_iRGainEstimation` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_IsConnected` | Boolean | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_IsInPit` | Boolean | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_LapDifference` | Double? | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_LapsSinceLastPit` | Int32? | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_LastLapTime` | TimeSpan | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_LastPitLaneDuration` | Double? | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_LastPitStopDuration` | Double? | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_LicenceColor` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_LicenceString` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_Name` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_PositionGain` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_PositionGainColor` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_PositionInClass` | Int32 | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_RelativeGapToLeader` | Double? | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_SafetyRating` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_TeamName` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_TireCompound` | String | 1..9 | ✓ |
| `iRacing_Class_NN_Leaderboard_Driver_NN_TireCompoundColor` | String | 1..9 | ✓ |
| `iRacing_Class_SoF` | Int32 |  | ✓ |
| `iRacing_Class_SoFk` | String |  | ✓ |

</details>

<details><summary><code>iRacing_ClassInfo*</code> — 11 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_ClassInfo_NN_Color` | String | 1..9 | ✓ |
| `iRacing_ClassInfo_NN_LeaderPosition` | Int32 | 1..9 | ✓ |
| `iRacing_ClassInfo_NN_Name` | String | 1..9 | ✓ |
| `iRacing_ClassInfo_NN_OpponentsCount` | Int32 | 1..9 | ✓ |
| `iRacing_ClassInfo_NN_OpponentsWithPosition` | Int32 | 1..9 | ✓ |
| `iRacing_ClassInfo_NN_SoF` | Int32 | 1..9 | ✓ |
| `iRacing_ClassInfo_NN_SoFk` | String* | 1..9 | ✓ |
| `iRacing_ClassInfo_All_OpponentsCount` | Int32 |  | ✓ |
| `iRacing_ClassInfo_All_Populated` | Int32 |  | ✓ |
| `iRacing_ClassInfo_All_SoF` | Int32 |  | ✓ |
| `iRacing_ClassInfo_All_SoFk` | String |  | ✓ |

</details>

<details><summary><code>iRacing_ClassLeaderboard*</code> — 33 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_ClassLeaderboard_Driver_NN_AbbrevName` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_BestLapTime` | TimeSpan | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_CarName` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_CarNumber` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_ClassColor` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_ClassName` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_ClubName` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_DeltaToBest` | Double | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_GapChangeLastLap` | TimeSpan | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_GapToLeaderString` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_Initials` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_Interval` | Double? | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_IntervalString` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_iRating` | Double | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_iRGainEstimation` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_IsConnected` | Boolean | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_IsInPit` | Boolean | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_LapsSinceLastPit` | Int32? | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_LastLapTime` | TimeSpan | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_LastPitLaneDuration` | Double? | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_LastPitStopDuration` | Double? | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_LicenceColor` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_LicenceString` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_Name` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_Position` | Int32 | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_PositionGain` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_PositionGainColor` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_PositionInClass` | Int32 | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_RelativeGapToLeader` | Double? | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_SafetyRating` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_TeamName` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_TireCompound` | String | 0..63 | ✓ |
| `iRacing_ClassLeaderboard_Driver_NN_TireCompoundColor` | String | 0..63 | ✓ |

</details>

<details><summary><code>iRacing_CurrentSession*</code> — 6 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_CurrentSession_IsLimitedSessionLaps` | Boolean |  | ✓ |
| `iRacing_CurrentSession_IsLimitedTime` | Boolean |  | ✓ |
| `iRacing_CurrentSession_ResultsNumCautionFlags` | Int32 |  | ✓ |
| `iRacing_CurrentSession_ResultsNumCautionLaps` | Int32 |  | ✓ |
| `iRacing_CurrentSession_ResultsNumLeadChanges` | Int32 |  | ✓ |
| `iRacing_CurrentSession_SessionTrackRubberState` | String |  | ✓ |

</details>

<details><summary><code>iRacing_DistanceToPitBox*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_DistanceToPitBox` | Double? |  |  |

</details>

<details><summary><code>iRacing_DistanceToPitEntry*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_DistanceToPitEntry` | Double? |  |  |

</details>

<details><summary><code>iRacing_DistanceToPitExit*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_DistanceToPitExit` | Double? |  |  |

</details>

<details><summary><code>iRacing_DriverAhead*</code> — 26 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_DriverAhead_NN_AbbrevName` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_BestLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_CarName` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_CarNumber` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_ClassColor` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_ClassName` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_ClubName` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_Distance` | Double* | 0..1 | ✓ |
| `iRacing_DriverAhead_NN_GapChangeLastLap` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_Initials` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_iRating` | Double | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_IsInPit` | Boolean | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_LapDifference` | Double? | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_LapsSinceLastPit` | Int32? | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_LastLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_LicenceColor` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_LicenceString` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_Name` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_Position` | Int32 | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_PositionInClass` | Int32 | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_RelativeGapToPlayer` | Double? | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_RelativeGapToPlayerColor` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_SafetyRating` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_TeamName` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_TireCompound` | String | 0..4 | ✓ |
| `iRacing_DriverAhead_NN_TireCompoundColor` | String | 0..4 | ✓ |

</details>

<details><summary><code>iRacing_DriverAheadInClass*</code> — 25 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_DriverAheadInClass_NN_AbbrevName` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_BestLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_CarName` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_CarNumber` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_ClassColor` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_ClassName` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_ClubName` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_GapChangeLastLap` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_Initials` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_iRating` | Double | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_IsInPit` | Boolean | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_LapDifference` | Double? | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_LapsSinceLastPit` | Int32? | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_LastLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_LicenceColor` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_LicenceString` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_Name` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_Position` | Int32 | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_PositionInClass` | Int32 | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_RelativeGapToPlayer` | Double? | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_RelativeGapToPlayerColor` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_SafetyRating` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_TeamName` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_TireCompound` | String | 0..4 | ✓ |
| `iRacing_DriverAheadInClass_NN_TireCompoundColor` | String | 0..4 | ✓ |

</details>

<details><summary><code>iRacing_DriverBehind*</code> — 26 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_DriverBehind_NN_AbbrevName` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_BestLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_CarName` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_CarNumber` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_ClassColor` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_ClassName` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_ClubName` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_Distance` | Double* | 0..1 | ✓ |
| `iRacing_DriverBehind_NN_GapChangeLastLap` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_Initials` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_iRating` | Double | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_IsInPit` | Boolean | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_LapDifference` | Double? | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_LapsSinceLastPit` | Int32? | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_LastLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_LicenceColor` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_LicenceString` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_Name` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_Position` | Int32 | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_PositionInClass` | Int32 | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_RelativeGapToPlayer` | Double? | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_RelativeGapToPlayerColor` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_SafetyRating` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_TeamName` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_TireCompound` | String | 0..4 | ✓ |
| `iRacing_DriverBehind_NN_TireCompoundColor` | String | 0..4 | ✓ |

</details>

<details><summary><code>iRacing_DriverBehindInClass*</code> — 25 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_DriverBehindInClass_NN_AbbrevName` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_BestLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_CarName` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_CarNumber` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_ClassColor` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_ClassName` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_ClubName` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_GapChangeLastLap` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_Initials` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_iRating` | Double | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_IsInPit` | Boolean | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_LapDifference` | Double? | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_LapsSinceLastPit` | Int32? | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_LastLapTime` | TimeSpan | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_LicenceColor` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_LicenceString` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_Name` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_Position` | Int32 | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_PositionInClass` | Int32 | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_RelativeGapToPlayer` | Double? | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_RelativeGapToPlayerColor` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_SafetyRating` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_TeamName` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_TireCompound` | String | 0..4 | ✓ |
| `iRacing_DriverBehindInClass_NN_TireCompoundColor` | String | 0..4 | ✓ |

</details>

<details><summary><code>iRacing_EngineLimiter*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_EngineLimiter` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_FuelMaxFuelPerLap*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelMaxFuelPerLap` | String |  | ✓ |

</details>

<details><summary><code>iRacing_FuelPerLapTargetFuelAmount*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelPerLapTargetFuelAmount` | String |  | ✓ |

</details>

<details><summary><code>iRacing_FuelPerLapTargetType*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelPerLapTargetType` | String |  | ✓ |

</details>

<details><summary><code>iRacing_FuelRefuelTarget*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelRefuelTarget` | String |  | ✓ |

</details>

<details><summary><code>iRacing_FuelToAdd*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelToAdd` | String |  | ✓ |

</details>

<details><summary><code>iRacing_FuelToAddKg*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelToAddKg` | String |  | ✓ |

</details>

<details><summary><code>iRacing_FuelToAddPushing*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelToAddPushing` | String |  | ✓ |

</details>

<details><summary><code>iRacing_FuelToAddPushingKg*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_FuelToAddPushingKg` | String |  | ✓ |

</details>

<details><summary><code>iRacing_HandbrakeInputVisible*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_HandbrakeInputVisible` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_LapsRemaining*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_LapsRemaining` | Int32 |  | ✓ |

</details>

<details><summary><code>iRacing_LapsRemainingFloat*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_LapsRemainingFloat` | Int32 |  | ✓ |

</details>

<details><summary><code>iRacing_Last0toPitSpeedTime*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_Last0toPitSpeedTime` | Int32 |  | ✓ |

</details>

<details><summary><code>iRacing_Leaderboard*</code> — 47 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_Leaderboard_Driver_NN_AbbrevName` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_BestLapTime` | TimeSpan | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_CarName` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_CarNumber` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_ClassColor` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_ClassName` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_ClubName` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_CurrentLap` | Int32? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_DeltaToBest` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_GapChangeLastLap` | TimeSpan | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_GapToLeaderString` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_Initials` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_Interval` | Double? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_IntervalString` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_iRating` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_iRGainEstimation` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_IsConnected` | Boolean | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_IsInPit` | Boolean | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LapDifference` | Double? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LapDistPct` | Double? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LapsSinceLastPit` | Int32? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LastLapTime` | TimeSpan | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LastPitLaneDuration` | Double? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LastPitStopDuration` | Double? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LicenceColor` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_LicenceString` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_Name` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_Position` | Int32 | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_PositionGain` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_PositionGainColor` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_PositionInClass` | Int32 | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_RelativeGapToLeader` | Double? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_SafetyRating` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TeamName` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TireCompound` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TireCompoundColor` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerFontSizeValue` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerlapdistPct` | Double? | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerLapperColor` | String | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerLapperColorVisible` | Boolean | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerLapperLeftValue` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerLapperTopValue` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerLeftValue` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerPositionInClass` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerSizeValue` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerTopValue` | Double | 0..63 | ✓ |
| `iRacing_Leaderboard_Driver_NN_TrackerVisible` | Boolean | 0..63 | ✓ |

</details>

<details><summary><code>iRacing_LeaderboardLayout*</code> — 5 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_LeaderboardLayout_BackgroundOpacity` | Int32 |  | ✓ |
| `iRacing_LeaderboardLayout_SLBOffset1` | número* |  | ✓ |
| `iRacing_LeaderboardLayout_SLBOffsetA` | número* |  | ✓ |
| `iRacing_LeaderboardLayout_SLBVisibleLeaders` | número* |  | ✓ |
| `iRacing_LeaderboardLayout_SLBWidth` | número* |  | ✓ |

</details>

<details><summary><code>iRacing_NonRelativeDriverAheadInClass*</code> — 15 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_NonRelativeDriverAheadInClass_NN_BestLapTime` | TimeSpan* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_CarLogoPath` |  | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_CarNumber` | número* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_ClassColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_GapChangeLastLap` | Double* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_GapToPlayer` | número* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_GapToPlayerColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_LapsSinceLastPit` | número* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_LastLapTime` | TimeSpan* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_LicenceColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_LicenceString` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_LicenceTextColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_LineColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_Name` |  | 0..0 | ✓ |
| `iRacing_NonRelativeDriverAheadInClass_NN_PositionInClass` | número* | 0..0 | ✓ |

</details>

<details><summary><code>iRacing_NonRelativeDriverBehindInClass*</code> — 15 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_NonRelativeDriverBehindInClass_NN_BestLapTime` | TimeSpan* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_CarLogoPath` |  | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_CarNumber` | número* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_ClassColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_GapChangeLastLap` | número* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_GapToPlayer` | número* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_GapToPlayerColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_LapsSinceLastPit` | número* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_LastLapTime` | TimeSpan* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_LicenceColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_LicenceString` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_LicenceTextColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_LineColor` | String* | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_Name` |  | 0..0 | ✓ |
| `iRacing_NonRelativeDriverBehindInClass_NN_PositionInClass` | número* | 0..0 | ✓ |

</details>

<details><summary><code>iRacing_PitDriveThroughDuration*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitDriveThroughDuration` | Int32? |  |  |

</details>

<details><summary><code>iRacing_PitEntryTrkPct*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitEntryTrkPct` | Int32? |  |  |

</details>

<details><summary><code>iRacing_PitExitTrkPct*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitExitTrkPct` | Int32? |  |  |

</details>

<details><summary><code>iRacing_PitLaneLength*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitLaneLength` | Int32? |  |  |

</details>

<details><summary><code>iRacing_PitSpeedLimitKph*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitSpeedLimitKph` | Int32? |  |  |

</details>

<details><summary><code>iRacing_PitSpeedLimitMph*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitSpeedLimitMph` | Int32? |  |  |

</details>

<details><summary><code>iRacing_PitWindowIsOpen*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitWindowIsOpen` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_PitWindowIsOpenPushing*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PitWindowIsOpenPushing` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_Player*</code> — 27 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_Player_CarLogoPath` | String |  | ✓ |
| `iRacing_Player_CarNumber` | String |  | ✓ |
| `iRacing_Player_ClassColor` | String |  | ✓ |
| `iRacing_Player_ClassIndex` | Int32 |  | ✓ |
| `iRacing_Player_ClassName` | String |  | ✓ |
| `iRacing_Player_ClubName` | String |  | ✓ |
| `iRacing_Player_CurrentLap` | Int32 |  | ✓ |
| `iRacing_Player_CurrentLapIsClean` | Boolean |  | ✓ |
| `iRacing_Player_GapToLeaderString` | String |  | ✓ |
| `iRacing_Player_Initials` | String |  | ✓ |
| `iRacing_Player_iRating` | Int32 |  | ✓ |
| `iRacing_Player_iRGainEstimation` | String |  | ✓ |
| `iRacing_Player_LapDistPct` | Single |  | ✓ |
| `iRacing_Player_LapsSinceLastPit` | Int32? |  | ✓ |
| `iRacing_Player_LastPitLaneDuration` | Double? |  | ✓ |
| `iRacing_Player_LastPitStopDuration` | Double? |  | ✓ |
| `iRacing_Player_LicenceColor` | String |  | ✓ |
| `iRacing_Player_LicenceString` | String |  | ✓ |
| `iRacing_Player_LicenceTextColor` | String* |  | ✓ |
| `iRacing_Player_Position` | Int32 |  | ✓ |
| `iRacing_Player_PositionGain` | String |  | ✓ |
| `iRacing_Player_PositionInClass` | Int32 |  | ✓ |
| `iRacing_Player_RelativeGapToLeader` | Double? |  | ✓ |
| `iRacing_Player_SafetyRating` | String |  | ✓ |
| `iRacing_Player_SessionBestCleanLapTime` | TimeSpan |  | ✓ |
| `iRacing_Player_TireCompound` | String |  | ✓ |
| `iRacing_Player_TireCompoundColor` | String |  | ✓ |

</details>

<details><summary><code>iRacing_PushToPassActive*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PushToPassActive` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_PushToPassAllowed*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PushToPassAllowed` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_PushToPassCount*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_PushToPassCount` | Int32 |  | ✓ |

</details>

<details><summary><code>iRacing_Session*</code> — 78 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_Session_OverallBestLapTime` | TimeSpan |  | ✓ |
| `iRacing_Session_OverallBestLapTime_AbbrevName` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_BestLapTime` | TimeSpan |  | ✓ |
| `iRacing_Session_OverallBestLapTime_CarLogoPath` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_CarName` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_CarNumber` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_ClassColor` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_ClassName` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_ClubName` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_CurrentLap` | Int32? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_DeltaToBest` | Double |  | ✓ |
| `iRacing_Session_OverallBestLapTime_GapChangeLastLap` | TimeSpan |  | ✓ |
| `iRacing_Session_OverallBestLapTime_GapToLeaderString` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_Initials` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_Interval` | Double? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_IntervalString` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_iRating` | Double |  | ✓ |
| `iRacing_Session_OverallBestLapTime_iRGainEstimation` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_IsConnected` | Boolean |  | ✓ |
| `iRacing_Session_OverallBestLapTime_IsInPit` | Boolean |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LapDifference` | Double? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LapDistPct` | Double? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LapsSinceLastPit` | Int32? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LastLapTime` | TimeSpan |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LastPitLaneDuration` | Double? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LastPitStopDuration` | Double? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LicenceColor` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LicenceString` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_LicenceTextColor` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_Name` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_Position` | Int32 |  | ✓ |
| `iRacing_Session_OverallBestLapTime_PositionGain` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_PositionGainColor` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_PositionInClass` | Int32 |  | ✓ |
| `iRacing_Session_OverallBestLapTime_RelativeGapToLeader` | Double? |  | ✓ |
| `iRacing_Session_OverallBestLapTime_SafetyRating` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_TeamName` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_TireCompound` | String |  | ✓ |
| `iRacing_Session_OverallBestLapTime_TireCompoundColor` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime` | TimeSpan |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_AbbrevName` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_BestLapTime` | TimeSpan |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_CarLogoPath` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_CarName` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_CarNumber` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_ClassColor` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_ClassName` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_ClubName` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_CurrentLap` | Int32? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_DeltaToBest` | Double |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_GapChangeLastLap` | TimeSpan |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_GapToLeaderString` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_Initials` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_Interval` | Double? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_IntervalString` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_iRating` | Double |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_iRGainEstimation` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_IsConnected` | Boolean |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_IsInPit` | Boolean |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LapDifference` | Double? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LapDistPct` | Double? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LapsSinceLastPit` | Int32? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LastLapTime` | TimeSpan |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LastPitLaneDuration` | Double? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LastPitStopDuration` | Double? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LicenceColor` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LicenceString` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_LicenceTextColor` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_Name` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_Position` | Int32 |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_PositionGain` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_PositionGainColor` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_PositionInClass` | Int32 |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_RelativeGapToLeader` | Double? |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_SafetyRating` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_TeamName` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_TireCompound` | String |  | ✓ |
| `iRacing_Session_PlayerClassBestLapTime_TireCompoundColor` | String |  | ✓ |

</details>

<details><summary><code>iRacing_SlowCarAhead*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_SlowCarAhead` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_SlowStoppedCarAheadDistance*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_SlowStoppedCarAheadDistance` | String |  | ✓ |

</details>

<details><summary><code>iRacing_StoppedCarAhead*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_StoppedCarAhead` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacing_TotalLaps*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_TotalLaps` | Int32 |  | ✓ |

</details>

<details><summary><code>iRacing_TrackTemperatureChange*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_TrackTemperatureChange` | String |  | ✓ |

</details>

<details><summary><code>iRacing_UnderPaceCar*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacing_UnderPaceCar` | Boolean |  | ✓ |

</details>

<details><summary><code>iRacingOP*</code> — 2 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `iRacingOP_EnableCarTracker` | String |  | ✓ |
| `iRacingOP_TrackInfoFlagLightsEnabled` | String |  | ✓ |

</details>

<details><summary><code>LeaderboardClassToggle*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `LeaderboardClassToggle` | Boolean |  | ✓ |

</details>

<details><summary><code>LeaderboardClassToggleRelative*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `LeaderboardClassToggleRelative` | Boolean |  | ✓ |

</details>

<details><summary><code>LeaderboardPositionToggle*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `LeaderboardPositionToggle` | Boolean |  | ✓ |

</details>

<details><summary><code>OptimalLapTime*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `OptimalLapTime` | TimeSpan |  | ✓ |

</details>

<details><summary><code>PluginRunning*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `PluginRunning` | Boolean |  | ✓ |

</details>

<details><summary><code>PluginVersion*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `PluginVersion` | String |  | ✓ |

</details>

<details><summary><code>PreviousSector*</code> — 4 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `PreviousSector_NN_BestTime` | TimeSpan | 0..9 | ✓ |
| `PreviousSector_NN_DeltaToBest` | String | 0..9 | ✓ |
| `PreviousSector_NN_Index` | String | 0..9 | ✓ |
| `PreviousSector_NN_Time` | TimeSpan | 0..9 | ✓ |

</details>

<details><summary><code>RadioTransmitCarNumber*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `RadioTransmitCarNumber` | String |  | ✓ |

</details>

<details><summary><code>RadioTransmitDriverName*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `RadioTransmitDriverName` | String |  | ✓ |

</details>

<details><summary><code>RecordedSectorTimes*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `RecordedSectorTimes` | Int32 |  | ✓ |

</details>

<details><summary><code>RLB*</code> — 41 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `RLB_Ahead_BestLapTime_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_CarLogoPath_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_CarNumber_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_ClassColor_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_GapChangeLastLap_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_iRGainEstimation_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_IsInPit_NN` | Boolean | 1..5 | ✓ |
| `RLB_Ahead_LapsSinceLastPit_NN` | Int32? | 1..5 | ✓ |
| `RLB_Ahead_LastLapColor_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_LastLapTime_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_LicenceColor_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_LicenceString_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_LicenceTextColor_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_LineColor_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_Name_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_PositionInClass_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_RelativeGapToPlayer_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_RelativeGapToPlayerColor_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_TireCompound_NN` | String | 1..5 | ✓ |
| `RLB_Ahead_TireCompoundColor_NN` | String | 1..5 | ✓ |
| `RLB_Behind_BestLapTime_NN` | String | 1..5 | ✓ |
| `RLB_Behind_CarLogoPath_NN` | String | 1..5 | ✓ |
| `RLB_Behind_CarNumber_NN` | String | 1..5 | ✓ |
| `RLB_Behind_ClassColor_NN` | String | 1..5 | ✓ |
| `RLB_Behind_GapChangeLastLap_NN` | String | 1..5 | ✓ |
| `RLB_Behind_iRGainEstimation_NN` | String | 1..5 | ✓ |
| `RLB_Behind_IsInPit_NN` | Boolean | 1..5 | ✓ |
| `RLB_Behind_LapsSinceLastPit_NN` | Int32? | 1..5 | ✓ |
| `RLB_Behind_LastLapColor_NN` | String | 1..5 | ✓ |
| `RLB_Behind_LastLapTime_NN` | String | 1..5 | ✓ |
| `RLB_Behind_LicenceColor_NN` | String | 1..5 | ✓ |
| `RLB_Behind_LicenceString_NN` | String | 1..5 | ✓ |
| `RLB_Behind_LicenceTextColor_NN` | String | 1..5 | ✓ |
| `RLB_Behind_LineColor_NN` | String | 1..5 | ✓ |
| `RLB_Behind_Name_NN` | String | 1..5 | ✓ |
| `RLB_Behind_PositionInClass_NN` | String | 1..5 | ✓ |
| `RLB_Behind_RelativeGapToPlayer_NN` | String | 1..5 | ✓ |
| `RLB_Behind_RelativeGapToPlayerColor_NN` | String | 1..5 | ✓ |
| `RLB_Behind_TireCompound_NN` | String | 1..5 | ✓ |
| `RLB_Behind_TireCompoundColor_NN` | String | 1..5 | ✓ |
| `RLB_Player_Name` | String |  | ✓ |

</details>

<details><summary><code>Sector*</code> — 4 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `Sector_NN_BestTime` | TimeSpan | 1..3 | ✓ |
| `Sector_NN_DeltaLastToBest` | Int32/String | 1..3 | ✓ |
| `Sector_NN_LastTime` | TimeSpan | 1..3 | ✓ |
| `Sector_Count` | Int32 |  | ✓ |

</details>

<details><summary><code>SLB*</code> — 44 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `SLB_BestLapColor_NN` | String | 1..64 | ✓ |
| `SLB_BestLapTime_NN` | String | (nulo agora) |  |
| `SLB_CarLogoPath_NN` | String | 1..64 | ✓ |
| `SLB_CarName_NN` | String | 1..64 | ✓ |
| `SLB_CarNameWidth` | Int32 |  | ✓ |
| `SLB_CarNumber_NN` | String | 1..64 | ✓ |
| `SLB_ClassColor_NN` | String | 1..64 | ✓ |
| `SLB_ClubName_NN` | String | 1..64 | ✓ |
| `SLB_ClubNameWidth` | Int32 |  | ✓ |
| `SLB_DeltaToBest_NN` | String | 1..64 | ✓ |
| `SLB_GapChangeLastLap_NN` | String | 1..64 | ✓ |
| `SLB_GapChangeLastLap_Color_NN` | String | 1..64 | ✓ |
| `SLB_GapToLeaderString_NN` | String | 1..64 | ✓ |
| `SLB_Interval_NN` | String | 1..64 | ✓ |
| `SLB_iRating_NN` | String | 1..64 | ✓ |
| `SLB_iRGainEstimation_NN` | String | 1..64 | ✓ |
| `SLB_IsInPit_NN` | Boolean | 1..64 | ✓ |
| `SLB_IsPlayer_NN` | Boolean | 1..64 | ✓ |
| `SLB_LapIncreased_NN` | Boolean | 1..64 | ✓ |
| `SLB_LapsSinceLastPit_NN` | Int32? | 1..64 | ✓ |
| `SLB_LastLapColor_NN` | String | 1..64 | ✓ |
| `SLB_LastLapTime_NN` | String | (nulo agora) |  |
| `SLB_LastPitStopDuration_NN` | String | (nulo agora) |  |
| `SLB_Licence_NN` | String | 1..64 | ✓ |
| `SLB_LicenceColor_NN` | String | 1..64 | ✓ |
| `SLB_LicenceString_NN` | String | 1..64 | ✓ |
| `SLB_LicenceTextColor_NN` | String | 1..64 | ✓ |
| `SLB_Modular_AlignRightOffset` | Int32 |  | ✓ |
| `SLB_Modular_TotalWidth` | Int32 |  | ✓ |
| `SLB_Name_NN` | String | 1..64 | ✓ |
| `SLB_NameWidth` | Int32 |  | ✓ |
| `SLB_Position_NN` | String | 1..64 | ✓ |
| `SLB_PositionGain_NN` | String | 1..64 | ✓ |
| `SLB_PositionGainColor_NN` | String | 1..64 | ✓ |
| `SLB_PositionInClass_NN` | String | 1..64 | ✓ |
| `SLB_RLB_FontSize` | número* |  | ✓ |
| `SLB_RowColor_NN` | String | 1..64 | ✓ |
| `SLB_RowIsVisible_NN` | Boolean | 1..64 | ✓ |
| `SLB_SafetyRating_NN` | String | 1..64 | ✓ |
| `SLB_TeamName_NN` | String | 1..64 | ✓ |
| `SLB_TeamNameWidth` | Int32 |  | ✓ |
| `SLB_TireCompound_NN` | String | 1..64 | ✓ |
| `SLB_TireCompoundColor_NN` | String | 1..64 | ✓ |
| `SLB_TotalRows` | Int32 |  | ✓ |

</details>

<details><summary><code>SpaIsPastBlanchimont*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `SpaIsPastBlanchimont` | Boolean |  | ✓ |

</details>

<details><summary><code>SpectatedCar*</code> — 38 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `SpectatedCar_AbbrevName` | String |  | ✓ |
| `SpectatedCar_BestLapTime` | TimeSpan |  | ✓ |
| `SpectatedCar_CarLogoPath` | String |  | ✓ |
| `SpectatedCar_CarName` | String |  | ✓ |
| `SpectatedCar_CarNumber` | String |  | ✓ |
| `SpectatedCar_ClassColor` | String |  | ✓ |
| `SpectatedCar_ClassName` | String |  | ✓ |
| `SpectatedCar_ClubName` | String |  | ✓ |
| `SpectatedCar_CurrentLap` | Int32? |  | ✓ |
| `SpectatedCar_DeltaToBest` | Double |  | ✓ |
| `SpectatedCar_GapChangeLastLap` | TimeSpan |  | ✓ |
| `SpectatedCar_GapToLeaderString` | String |  | ✓ |
| `SpectatedCar_Initials` | String |  | ✓ |
| `SpectatedCar_Interval` | Double? |  | ✓ |
| `SpectatedCar_IntervalString` | String |  | ✓ |
| `SpectatedCar_iRating` | Double |  | ✓ |
| `SpectatedCar_iRGainEstimation` | String |  | ✓ |
| `SpectatedCar_IsConnected` | Boolean |  | ✓ |
| `SpectatedCar_IsInPit` | Boolean |  | ✓ |
| `SpectatedCar_LapDifference` | Double? |  | ✓ |
| `SpectatedCar_LapDistPct` | Double? |  | ✓ |
| `SpectatedCar_LapsSinceLastPit` | Int32? |  | ✓ |
| `SpectatedCar_LastLapTime` | TimeSpan |  | ✓ |
| `SpectatedCar_LastPitLaneDuration` | Double? |  | ✓ |
| `SpectatedCar_LastPitStopDuration` | Double? |  | ✓ |
| `SpectatedCar_LicenceColor` | String |  | ✓ |
| `SpectatedCar_LicenceString` | String |  | ✓ |
| `SpectatedCar_LicenceTextColor` | String |  | ✓ |
| `SpectatedCar_Name` | String |  | ✓ |
| `SpectatedCar_Position` | Int32 |  | ✓ |
| `SpectatedCar_PositionGain` | String |  | ✓ |
| `SpectatedCar_PositionGainColor` | String |  | ✓ |
| `SpectatedCar_PositionInClass` | Int32 |  | ✓ |
| `SpectatedCar_RelativeGapToLeader` | Double? |  | ✓ |
| `SpectatedCar_SafetyRating` | String |  | ✓ |
| `SpectatedCar_TeamName` | String |  | ✓ |
| `SpectatedCar_TireCompound` | String |  | ✓ |
| `SpectatedCar_TireCompoundColor` | String |  | ✓ |

</details>

<details><summary><code>Stint*</code> — 8 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `Stint_Current_BestLapTime` | TimeSpan |  | ✓ |
| `Stint_Current_Duration` | TimeSpan |  | ✓ |
| `Stint_Current_LapTimeAverage` | TimeSpan |  | ✓ |
| `Stint_Current_TimedLaps` | Int32 |  | ✓ |
| `Stint_Previous_NN_BestLapTime` | TimeSpan/TimeSpan? | 0..9 | ✓ |
| `Stint_Previous_NN_Duration` | TimeSpan/TimeSpan? | 0..9 | ✓ |
| `Stint_Previous_NN_LapTimeAverage` | TimeSpan/TimeSpan? | 0..9 | ✓ |
| `Stint_Previous_NN_TimedLaps` | Int32/Int32? | 0..9 | ✓ |

</details>

<details><summary><code>USDFIDashBestLapMode*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `USDFIDashBestLapMode` | String |  | ✓ |

</details>

<details><summary><code>USDFIDashCurrentPage*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `USDFIDashCurrentPage` | Int32 |  | ✓ |

</details>

<details><summary><code>USDFIDashFlagLights*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `USDFIDashFlagLights` | String |  | ✓ |

</details>

<details><summary><code>USDFIDashLeftDisplayMode*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `USDFIDashLeftDisplayMode` | String |  | ✓ |

</details>

<details><summary><code>USDFIDashTexture*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `USDFIDashTexture` | String |  | ✓ |

</details>

<details><summary><code>USDFIPitScreenVisible*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `USDFIPitScreenVisible` | Boolean |  | ✓ |

</details>

<details><summary><code>USDFITopDisplayToggle*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `USDFITopDisplayToggle` | Boolean |  | ✓ |

</details>

<details><summary><code>WheelImagePath*</code> — 1 famílias</summary>

| Nome | Tipo | Faixa NN | Ao vivo |
|---|---|---|---|
| `WheelImagePath` | String |  | ✓ |

</details>

Tipo com `*` = deduzido do valor atual (não encontrado no registro estático).

### 8.2 Dahl Design
Prefixo `DahlDesign.` — ativo. Propriedades do pacote Dahl Design (dashboards DDU/DDC, spotter, rotary, smooth gear). Lista = nomes do código + dos dashboards instalados, confirmados no servidor.

<details><summary>519 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `ABSToggle` | Boolean* |
| `ARBstiffForward` | Boolean |
| `ARBswapped` | Boolean |
| `AccelerationTo100KPH` | Double |
| `AccelerationTo200KPH` | Double |
| `AheadBestLap` | TimeSpan* |
| `AheadGap` | número* |
| `AheadIsConnected` | Boolean* |
| `AheadIsInPit` | Boolean* |
| `AheadLapsToOvertake` | número* |
| `AheadName` | String* |
| `AheadP2PCount` | número* |
| `AheadP2PStatus` | Boolean* |
| `AheadPace` | TimeSpan* |
| `AheadPrognosis` | número* |
| `AheadRealGap` | número* |
| `AheadSlowLap` | Boolean* |
| `AnimationType` | AnimationType |
| `BehindBestLap` | TimeSpan* |
| `BehindGap` | número* |
| `BehindIsConnected` | Boolean* |
| `BehindIsInPit` | Boolean* |
| `BehindLapsToOvertake` | número* |
| `BehindName` | String* |
| `BehindP2PCount` | número* |
| `BehindP2PStatus` | Boolean* |
| `BehindPace` | TimeSpan* |
| `BehindPrognosis` | número* |
| `BehindRealGap` | número* |
| `BehindSlowLap` | Boolean* |
| `BrakeCurveAUC` | número* |
| `BrakeCurvePeak` | número* |
| `BrakeCurveValues` | String* |
| `CalcAverageFuel` | Double |
| `CalcFuelPerLap` | número* |
| `CalcLastLapFuel` | número* |
| `CalculationAccuracy` | número* |
| `CarAhead01BestLap` | TimeSpan* |
| `CarAhead01ClassColor` | String* |
| `CarAhead01ClassDifference` | número* |
| `CarAhead01IRating` | número* |
| `CarAhead01IsAhead` | Boolean* |
| `CarAhead01IsClassLeader` | Boolean* |
| `CarAhead01JokerLaps` | número* |
| `CarAhead01LapsSincePit` | número* |
| `CarAhead01Licence` | String* |
| `CarAhead01Name` | String* |
| `CarAhead01P2PCount` | número* |
| `CarAhead01P2PStatus` | Boolean* |
| `CarAhead01Position` | número* |
| `CarAhead01RealRelative` | número* |
| `CarAhead01Relative` | número* |
| `CarAhead02ClassColor` | String* |
| `CarAhead02ClassDifference` | número* |
| `CarAhead02IRating` | número* |
| `CarAhead02IsAhead` | Boolean* |
| `CarAhead02IsClassLeader` | Boolean* |
| `CarAhead02JokerLaps` | número* |
| `CarAhead02LapsSincePit` | número* |
| `CarAhead02Licence` | String* |
| `CarAhead02Name` | String* |
| `CarAhead02P2PStatus` | Boolean* |
| `CarAhead02Position` | número* |
| `CarAhead02RealRelative` | número* |
| `CarAhead02Relative` | número* |
| `CarAhead03ClassColor` | String* |
| `CarAhead03ClassDifference` | número* |
| `CarAhead03IRating` | número* |
| `CarAhead03IsAhead` | Boolean* |
| `CarAhead03IsClassLeader` | Boolean* |
| `CarAhead03JokerLaps` | número* |
| `CarAhead03LapsSincePit` | número* |
| `CarAhead03Licence` | String* |
| `CarAhead03Name` | String* |
| `CarAhead03P2PStatus` | Boolean* |
| `CarAhead03Position` | número* |
| `CarAhead03RealRelative` | número* |
| `CarAhead03Relative` | número* |
| `CarAhead04ClassColor` | String* |
| `CarAhead04ClassDifference` | número* |
| `CarAhead04IRating` | número* |
| `CarAhead04IsAhead` | Boolean* |
| `CarAhead04IsClassLeader` | Boolean* |
| `CarAhead04JokerLaps` | número* |
| `CarAhead04LapsSincePit` | número* |
| `CarAhead04Licence` | String* |
| `CarAhead04Name` | String* |
| `CarAhead04P2PStatus` | Boolean* |
| `CarAhead04Position` | número* |
| `CarAhead04RealRelative` | número* |
| `CarAhead04Relative` | número* |
| `CarAhead05ClassDifference` | número* |
| `CarAhead05IsAhead` | Boolean* |
| `CarAhead05IsClassLeader` | Boolean* |
| `CarAhead05Name` | String* |
| `CarAhead05RealRelative` | número* |
| `CarAhead05Relative` | número* |
| `CarBehind01BestLap` | TimeSpan* |
| `CarBehind01ClassColor` | String* |
| `CarBehind01ClassDifference` | número* |
| `CarBehind01IRating` | número* |
| `CarBehind01IsAhead` | Boolean* |
| `CarBehind01IsClassLeader` | Boolean* |
| `CarBehind01IsInPit` | Boolean* |
| `CarBehind01JokerLaps` | número* |
| `CarBehind01LapsSincePit` | número* |
| `CarBehind01Licence` | String* |
| `CarBehind01Name` | String* |
| `CarBehind01P2PCount` | número* |
| `CarBehind01P2PStatus` | Boolean* |
| `CarBehind01Position` | número* |
| `CarBehind01RealRelative` | número* |
| `CarBehind01Relative` | número* |
| `CarBehind02ClassColor` | String* |
| `CarBehind02ClassDifference` | número* |
| `CarBehind02IRating` | número* |
| `CarBehind02IsAhead` | Boolean* |
| `CarBehind02IsClassLeader` | Boolean* |
| `CarBehind02IsInPit` | Boolean* |
| `CarBehind02JokerLaps` | número* |
| `CarBehind02LapsSincePit` | número* |
| `CarBehind02Licence` | String* |
| `CarBehind02Name` | String* |
| `CarBehind02P2PStatus` | Boolean* |
| `CarBehind02Position` | número* |
| `CarBehind02RealRelative` | número* |
| `CarBehind02Relative` | número* |
| `CarBehind03ClassColor` | String* |
| `CarBehind03ClassDifference` | número* |
| `CarBehind03IRating` | número* |
| `CarBehind03IsAhead` | Boolean* |
| `CarBehind03IsClassLeader` | Boolean* |
| `CarBehind03IsInPit` | Boolean* |
| `CarBehind03JokerLaps` | número* |
| `CarBehind03LapsSincePit` | número* |
| `CarBehind03Licence` | String* |
| `CarBehind03Name` | String* |
| `CarBehind03P2PStatus` | Boolean* |
| `CarBehind03Position` | número* |
| `CarBehind03RealRelative` | número* |
| `CarBehind03Relative` | número* |
| `CarBehind04ClassColor` | String* |
| `CarBehind04ClassDifference` | número* |
| `CarBehind04IRating` | número* |
| `CarBehind04IsAhead` | Boolean* |
| `CarBehind04IsClassLeader` | Boolean* |
| `CarBehind04IsInPit` | Boolean* |
| `CarBehind04JokerLaps` | número* |
| `CarBehind04LapsSincePit` | número* |
| `CarBehind04Licence` | String* |
| `CarBehind04Name` | String* |
| `CarBehind04P2PStatus` | Boolean* |
| `CarBehind04Position` | número* |
| `CarBehind04RealRelative` | número* |
| `CarBehind04Relative` | número* |
| `CarBehind05ClassColor` | String* |
| `CarBehind05ClassDifference` | número* |
| `CarBehind05IsAhead` | Boolean* |
| `CarBehind05IsClassLeader` | Boolean* |
| `CarBehind05IsInPit` | Boolean* |
| `CarBehind05JokerLaps` | número* |
| `CarBehind05LapsSincePit` | número* |
| `CarBehind05Name` | String* |
| `CarBehind05P2PCount` | número* |
| `CarBehind05P2PStatus` | Boolean* |
| `CarBehind05RealGap` | número* |
| `CarBehind05RealRelative` | número* |
| `CarBehind05Relative` | número* |
| `CenterDashType` | String |
| `CoupleInCarToPit` | Boolean |
| `CurrentFrontWing` | Double |
| `CurrentPowersteer` | Int32 |
| `CurrentRearWing` | Double |
| `CurrentSector` | número* |
| `CurrentSector1Delta` | número* |
| `CurrentSector1Status` | número* |
| `CurrentSector1Time` | TimeSpan* |
| `CurrentSector2Delta` | número* |
| `CurrentSector2Status` | número* |
| `CurrentSector2Time` | TimeSpan* |
| `CurrentSector3Delta` | número* |
| `CurrentSector3Status` | Int32 |
| `CurrentSector3Time` | TimeSpan* |
| `CurrentTape` | Int32 |
| `DDCDDSEnabled` | Boolean |
| `DDCDDSMode` | número* |
| `DDCEnabled` | Boolean* |
| `DDCPreset` | número* |
| `DDCR1` | número* |
| `DDCR15` | número* |
| `DDCR2` | número* |
| `DDCR3` | número* |
| `DDCR4` | número* |
| `DDCR5` | número* |
| `DDCR6` | número* |
| `DDCR7` | número* |
| `DDCR8` | número* |
| `DDCbitePoint` | número* |
| `DDCbiteSetting` | número* |
| `DDCbrake` | número* |
| `DDCclutch` | número* |
| `DDCclutchEnabled` | Boolean |
| `DDChandbrakeActive` | número* |
| `DDCmagicActive` | número* |
| `DDCneutralActive` | Boolean* |
| `DDCneutralMode` | número* |
| `DDCquickSwitchActive` | número* |
| `DDCquickSwitchMode` | número* |
| `DDCthrottle` | número* |
| `DDUEnabled` | Boolean |
| `DRSCount` | número* |
| `DRSState` | String |
| `DashLEDEnabled` | Boolean |
| `DashType` | String |
| `Dashboard.DeltaScreen` | Int32 |
| `Dashboard.LeftScreen` | Int32 |
| `Dashboard.RightScreen` | Int32 |
| `Dashboard.ShowGenericSplashEnabled` | Boolean |
| `DeltaBarSensitivity` | Double |
| `DeltaLapRecord` | número* |
| `DeltaLapRecordChange` | String* |
| `DeltaLastLap` | número* |
| `DeltaLastLapChange` | String* |
| `DeltaSessionBest` | número* |
| `DeltaSessionBestChange` | String* |
| `ERSCharges` | número* |
| `ERSTarget` | número* |
| `FuelAlert` | Boolean* |
| `FuelConserveToSaveAStop` | número* |
| `FuelConserveToSaveAStopLL` | número* |
| `FuelDelta` | número* |
| `FuelDeltaLL` | número* |
| `FuelMaximumFuelFill` | número* |
| `FuelMinimumFuelFill` | número* |
| `FuelMinimumFuelFillLL` | número* |
| `FuelPerLapOffset` | Double* |
| `FuelPerLapTarget` | número* |
| `FuelPerLapTargetLastLapDelta` | número* |
| `FuelPerLapTargetLocked` | Boolean* |
| `FuelPitStops` | número* |
| `FuelPitStopsLL` | número* |
| `FuelPitWindowFirst` | número* |
| `FuelPitWindowFirstLL` | número* |
| `FuelPitWindowLast` | número* |
| `FuelPitWindowLastLL` | número* |
| `FuelSaveDeltaValue` | número* |
| `FuelSlowestFuelSavePace` | TimeSpan* |
| `FuelTargetDeltaCumulative` | número* |
| `HasABS` | Boolean |
| `HasAntiStall` | Boolean |
| `HasDRS` | Boolean |
| `HasOvertake` | Boolean |
| `HasTC` | Boolean |
| `HighPower` | Boolean |
| `HotLapLivePosition` | número* |
| `HotLapPosition` | Int32 |
| `IRchange` | Double |
| `Idle` | Boolean |
| `IdleRPM` | Int32 |
| `InCarMenu` | Int32 |
| `JokerCount` | Int32 |
| `JokerThisLap` | Boolean |
| `LEDWarnings` | Boolean |
| `Lap01Delta` | número* |
| `Lap01Sector3Time` | TimeSpan* |
| `Lap01Status` | Int32 |
| `Lap01Time` | TimeSpan |
| `Lap02Delta` | número* |
| `Lap02Status` | Int32 |
| `Lap02Time` | TimeSpan |
| `Lap03Delta` | número* |
| `Lap03Status` | Int32 |
| `Lap03Time` | TimeSpan |
| `Lap04Delta` | número* |
| `Lap04Status` | Int32 |
| `Lap04Time` | TimeSpan |
| `Lap05Delta` | número* |
| `Lap05Status` | Int32 |
| `Lap05Time` | TimeSpan |
| `Lap06Delta` | número* |
| `Lap06Status` | Int32 |
| `Lap06Time` | TimeSpan |
| `Lap07Delta` | número* |
| `Lap07Status` | Int32 |
| `Lap07Time` | TimeSpan |
| `Lap08Delta` | número* |
| `Lap08Status` | Int32 |
| `Lap08Time` | TimeSpan |
| `LapBalance` | número* |
| `LapInfoScreen` | Boolean |
| `LapRecord` | TimeSpan |
| `LapRecordAirTemp` | Double |
| `LapRecordSetupIsFixed` | Double |
| `LapRecordTrackTemp` | Double |
| `LapStatus` | Int32 |
| `LapsRemaining` | número* |
| `LargeFuelIncrement` | Int32 |
| `LastGear` | String |
| `LastGearMaxRPM` | Double |
| `LaunchBitePoint` | Double |
| `LaunchGearRelease` | Double |
| `LaunchGearReleased` | Double |
| `LaunchIdealRangeStart` | Double |
| `LaunchIdealRangeStop` | Double |
| `LaunchScreen` | Boolean |
| `LaunchSpin` | Double |
| `LaunchThrottle` | Double |
| `LaunchTimeRelease` | Double |
| `LaunchTimeReleased` | Double |
| `LeftCarGap` | Double? |
| `LeftCarName` | String |
| `MapHigh` | Int32 |
| `MapLow` | Int32 |
| `MenuType` | String |
| `MinimumCornerSpeed` | número* |
| `MyBitePoint` | Double |
| `MyClassColor` | String |
| `MyClutch` | Double |
| `NoBoost` | Boolean |
| `OptimalLapTime` | TimeSpan |
| `OptimalShiftCurrentGear` | Int32 |
| `OptimalShiftGear1` | Int32 |
| `OptimalShiftGear2` | Int32 |
| `OptimalShiftGear3` | Int32 |
| `OptimalShiftGear4` | Int32 |
| `OptimalShiftGear5` | Int32 |
| `OptimalShiftGear6` | Int32 |
| `OptimalShiftGear7` | Int32 |
| `OptimalShiftLastGear` | Int32 |
| `OvertakeMode` | Boolean |
| `P1LapBalance` | número* |
| `P2PCount` | Int32 |
| `P2PStatus` | Boolean |
| `Pace` | TimeSpan* |
| `PaceCheck` | Boolean |
| `PitBoxApproach` | Boolean |
| `PitBoxPosition` | Double |
| `PitCrewType` | número* |
| `PitEntry` | Boolean* |
| `PitExitCar10IsFaster` | Boolean* |
| `PitExitCar11ClassDifference` | número* |
| `PitExitCar11Gap` | número* |
| `PitExitCar11IsAhead` | Boolean* |
| `PitExitCar11IsFaster` | Boolean* |
| `PitExitCar11Name` | String* |
| `PitExitCar11Position` | número* |
| `PitExitCar12ClassDifference` | número* |
| `PitExitCar12Gap` | número* |
| `PitExitCar12IsAhead` | Boolean* |
| `PitExitCar12IsFaster` | Boolean* |
| `PitExitCar12Name` | String* |
| `PitExitCar12Position` | número* |
| `PitExitCar13ClassDifference` | número* |
| `PitExitCar13Gap` | número* |
| `PitExitCar13Name` | String* |
| `PitExitCar13Position` | número* |
| `PitExitCar1ClassDifference` | número* |
| `PitExitCar1Gap` | número* |
| `PitExitCar1IsFaster` | Boolean* |
| `PitExitCar1Name` | String* |
| `PitExitCar1Position` | número* |
| `PitExitCar2ClassDifference` | número* |
| `PitExitCar2Gap` | número* |
| `PitExitCar2IsAhead` | Boolean* |
| `PitExitCar2IsFaster` | Boolean* |
| `PitExitCar2Name` | String* |
| `PitExitCar2Position` | número* |
| `PitExitCar3ClassDifference` | número* |
| `PitExitCar3Gap` | número* |
| `PitExitCar3IsAhead` | Boolean* |
| `PitExitCar3IsFaster` | Boolean* |
| `PitExitCar3Name` | String* |
| `PitExitCar3Position` | número* |
| `PitExitCar4ClassDifference` | número* |
| `PitExitCar4Gap` | número* |
| `PitExitCar4IsAhead` | Boolean* |
| `PitExitCar4IsFaster` | Boolean* |
| `PitExitCar4Name` | String* |
| `PitExitCar4Position` | número* |
| `PitExitCar5ClassDifference` | número* |
| `PitExitCar5Gap` | número* |
| `PitExitCar5IsAhead` | Boolean* |
| `PitExitCar5IsFaster` | Boolean* |
| `PitExitCar5Name` | String* |
| `PitExitCar5Position` | número* |
| `PitExitCar6ClassDifference` | número* |
| `PitExitCar6Gap` | número* |
| `PitExitCar6IsAhead` | Boolean* |
| `PitExitCar6IsFaster` | Boolean* |
| `PitExitCar6Name` | String* |
| `PitExitCar6Position` | número* |
| `PitExitCar7ClassDifference` | número* |
| `PitExitCar7Gap` | número* |
| `PitExitCar7IsAhead` | Boolean* |
| `PitExitCar7IsFaster` | Boolean* |
| `PitExitCar7Name` | String* |
| `PitExitCar7Position` | número* |
| `PitExitCar8ClassDifference` | número* |
| `PitExitCar8Gap` | número* |
| `PitExitCar8IsAhead` | Boolean* |
| `PitExitCar8IsFaster` | Boolean* |
| `PitExitCar8Name` | String* |
| `PitExitCar8Position` | número* |
| `PitExitPosition` | número* |
| `PitMenu` | Int32 |
| `PitSavePaceLock` | Boolean |
| `PitScreen` | Boolean |
| `PitServiceFuelTarget` | número* |
| `PitServiceLFPCold` | Single |
| `PitServiceLFPSet` | Single |
| `PitServiceLRPCold` | Single |
| `PitServiceLRPSet` | Single |
| `PitServiceRFPCold` | Single |
| `PitServiceRFPSet` | Single |
| `PitServiceRRPCold` | Single |
| `PitServiceRRPSet` | Single |
| `PitSpeeding` | Boolean* |
| `PitTimeAdjustment` | número* |
| `PitTimeDriveThrough` | número* |
| `PitTimeFuel` | número* |
| `PitTimeService` | número* |
| `PitTimeTires` | número* |
| `PitTimeTotal` | número* |
| `PitTimeWindscreen` | número* |
| `PitToggleFuel` | Boolean |
| `PitToggleLF` | Boolean |
| `PitToggleLR` | Boolean |
| `PitToggleRF` | Boolean |
| `PitToggleRR` | Boolean |
| `PitToggleRepair` | Boolean |
| `PitToggleWindscreen` | Boolean |
| `Position` | Int32 |
| `PredictedLapTime` | TimeSpan* |
| `QualyLap1Status` | Int32 |
| `QualyLap1Time` | TimeSpan* |
| `QualyLap2Status` | Int32 |
| `QualyLap2Time` | TimeSpan* |
| `QualyWarmUpLap` | Boolean |
| `RaceFinished` | Boolean |
| `Radio` | Boolean |
| `RadioIsSpectator` | Boolean |
| `RadioName` | String |
| `RadioPosition` | Int32 |
| `ReactionTime` | Double |
| `RightCarGap` | Double? |
| `RightCarName` | String |
| `SF23.OTActive` | Boolean* |
| `SF23.OTAllowed` | Boolean* |
| `SF23.OTCooldownActive` | Boolean* |
| `SF23.OTCooldownTimer` | número* |
| `SF23.OTTimeLeft` | número* |
| `SW1BiteSetting` | número* |
| `SW1Brake` | número* |
| `SW1Clutch` | número* |
| `SW1ClutchMode` | número* |
| `SW1DDSMode` | número* |
| `SW1Enabled` | Boolean |
| `SW1HandbrakeActive` | número* |
| `SW1LeftRotaryMode` | número* |
| `SW1LeftToggleMode` | número* |
| `SW1MagicToggleActive` | Boolean* |
| `SW1MagicToggleMode` | número* |
| `SW1NeutralMode` | número* |
| `SW1Preset` | número* |
| `SW1QuickSwitchActive` | Boolean* |
| `SW1QuickSwitchMode` | número* |
| `SW1RadioButtonMode` | número* |
| `SW1RightRotaryMode` | número* |
| `SW1RightToggleMode` | número* |
| `SW1ShifterMode` | número* |
| `SW1Throttle` | número* |
| `SW1ThrottleHoldActive` | Boolean* |
| `SW1bitePoint` | número* |
| `SW1startLED` | Int32 |
| `Sector1Pace` | TimeSpan* |
| `Sector1Score` | número* |
| `Sector2Pace` | TimeSpan* |
| `Sector2Score` | número* |
| `Sector3Pace` | TimeSpan* |
| `Sector3Score` | número* |
| `SessionBestLap` | TimeSpan |
| `SessionBestSector1` | TimeSpan |
| `SessionBestSector2` | TimeSpan |
| `SessionBestSector3` | TimeSpan |
| `ShiftLightRPM` | Double |
| `ShiftTimingAssist` | Boolean |
| `ShiftWarning` | Boolean |
| `ShowBrakeThrottleGaugesEnabled` | Boolean |
| `ShowMapEnabled` | Boolean |
| `SlipLF` | número* |
| `SlipLR` | número* |
| `SlipRF` | número* |
| `SlipRR` | número* |
| `SmallFuelIncrement` | Int32 |
| `SmoothGear` | String |
| `SoF` | Double |
| `SpeedDeltaLapRecord` | número* |
| `SpeedPercentDeltaLapRecord` | número* |
| `SpotterMode` | Boolean |
| `SteeringAngle` | Double |
| `StintCurrentHotlap` | número* |
| `StintInvalidLaps` | Int32 |
| `StintTimer` | TimeSpan* |
| `StintTotalHotlaps` | número* |
| `StintTotalTime` | TimeSpan* |
| `StintValidLaps` | Int32 |
| `StopWatch` | TimeSpan* |
| `StopWatchSplit` | TimeSpan* |
| `StraightLineSpeed` | número* |
| `TCActive` | Boolean* |
| `TCOffTimer` | TimeSpan* |
| `TCToggle` | Boolean* |
| `TestProperty` | número* |
| `ThrottleAgro` | número* |
| `ThrottleCurveValues` | String* |
| `TrackEntry` | Boolean |
| `TrackType` | Int32 |
| `TrueRevLimiter` | Double |
| `Version` | String* |

</details>

Padrões dinâmicos no código: `NNLapSector1Time`

### 8.3 RSC — The Many-Faced Dash
Prefixo `TheManyFacedDash.` — ativo.

<details><summary>34 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `DashColorSet` | String |
| `DashPresetIndex` | String |
| `DashTexture` | String |
| `DashTextureIndex` | String |
| `DataUpdateFrametime` | Double |
| `EnableVideo` | Boolean |
| `Last0to100KphTime` | Int32 |
| `Last0to60MphTime` | Int32 |
| `MFDDashBestLapMode` | String |
| `MFDDashColor_Display_Background_1` | String |
| `MFDDashColor_Display_Background_2` | String |
| `MFDDashColor_Extra_Color_1` | String |
| `MFDDashColor_Extra_Color_2` | String |
| `MFDDashColor_Extra_Color_3` | String |
| `MFDDashColor_Extra_Color_4` | String |
| `MFDDashColor_Extra_Color_5` | String |
| `MFDDashColor_Extra_Color_6` | String |
| `MFDDashColor_Label_Text_1` | String |
| `MFDDashColor_Label_Text_2` | String |
| `MFDDashColor_Main_Text_1` | String |
| `MFDDashColor_Main_Text_2` | String |
| `MFDDashColor_Secondary_Text_1` | String |
| `MFDDashColor_Secondary_Text_2` | String |
| `MFDDashFlagLights` | String |
| `MFDDashGlassEffect` | String |
| `MFDDashMainScreenPitAssists` | String |
| `MFDDashNightMode` | Boolean |
| `MFDDashRightDisplayMode` | String |
| `MFDDashScreenChangeAutomation` | String |
| `MFDDashTopDisplayMode` | String |
| `MFDPitScreenVisible` | Boolean |
| `MFDTopDisplayToggle` | Boolean |
| `PluginRunning` | Boolean |
| `PluginVersion` | String |

</details>

### 8.4 RSC — Input Display (ExtraInputProperties)
Prefixo `ExtraInputProperties.` — ativo.

<details><summary>22 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `Brake` | Int32 |
| `Clutch` | Int32 |
| `ClutchBitePoint` | Int32 |
| `DataUpdateFrametime` | Double |
| `Gear` | Int32 |
| `GearFromHShifter` | Int32 |
| `Handbrake` | Int32 |
| `HandbrakeInputVisible` | Boolean |
| `InputDisplay_ShowFFBClipping` | Boolean |
| `InputDisplay_ShowGear` | Boolean |
| `InputDisplay_ShowTraces` | Boolean |
| `Last0to100KphTime` | Int32 |
| `Last0to60MphTime` | Int32 |
| `PluginRunning` | Boolean |
| `PluginVersion` | String |
| `ShakeIt_ClutchFriction` | Int32 |
| `ShakeIt_GearGrinding` | Int32 |
| `ShakeIt_GearShiftModulated` | Int32 |
| `SteeringAngle` | Int32 |
| `SteeringHalfRange` | Int32 |
| `Throttle` | Int32 |
| `WheelImagePath` | String |

</details>

### 8.5 RSC — Auto Brightness
Prefixo `AutoBrightness.` — ativo.

<details><summary>38 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `AmbientInputCurrent` | Int32 |
| `AmbientInputMax` | Double |
| `AmbientInputMin` | Double |
| `AmbientPropertyMax` | Int32 |
| `AmbientPropertyMin` | Int32 |
| `BlueLightFilterCurrent` | Int32 |
| `BlueLightFilterEnabled` | Boolean |
| `BlueLightFilterMax` | Double |
| `BlueLightFilterMin` | Double |
| `DashLayerBrightnessCurrent` | Int32 |
| `DashLayerBrightnessMax` | Double |
| `DashLayerBrightnessMin` | Double |
| `DashLayerEnabled` | Boolean |
| `DashboardBrightness` | Int32 |
| `DataUpdateFrametime` | Double |
| `GammaFactor` | Double |
| `LedMatrixBrightnessCurrent` | Double |
| `LedMatrixBrightnessMax` | Double |
| `LedMatrixBrightnessMin` | Double |
| `LedMatrixEnabled` | Boolean |
| `ManualInputCurrent` | Int32 |
| `ModeAmbient` | Boolean |
| `ModeManual` | Boolean |
| `MonitorBrightnessCurrent` | Int32 |
| `MonitorBrightnessEnabled` | Boolean |
| `MonitorBrightnessMax` | Double |
| `MonitorBrightnessMin` | Double |
| `PluginRunning` | Boolean |
| `RGBLedsBrightnessCurrent` | Double |
| `RGBLedsBrightnessMax` | Double |
| `RGBLedsBrightnessMin` | Double |
| `RGBLedsEnabled` | Boolean |
| `SensitivityThreshold` | Double |
| `SmoothingEnabled` | Boolean |
| `USBDisplayBrightnessCurrent` | Int32 |
| `USBDisplayBrightnessMax` | Double |
| `USBDisplayBrightnessMin` | Double |
| `USBDisplayEnabled` | Boolean |

</details>

### 8.6 RSC — Checklist
Prefixo `Checklist.` — ativo.

<details><summary>18 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `DashChecklistItemName1` | String* |
| `DashChecklistItemName10` | String* |
| `DashChecklistItemName2` | String* |
| `DashChecklistItemName3` | String* |
| `DashChecklistItemName4` | String* |
| `DashChecklistItemName5` | String* |
| `DashChecklistItemName6` | String* |
| `DashChecklistItemName7` | String* |
| `DashChecklistItemName8` | String* |
| `DashChecklistItemName9` | String* |
| `DashChecklistReady` | Boolean |
| `DataUpdateFrametime` | Double |
| `MFDDashChecklistEnabled` | Boolean |
| `MFDDashChecklistEnabledOnIdleScreen` | Boolean |
| `PluginRunning` | Boolean |
| `PluginVersion` | String |
| `USDFIDashChecklistEnabled` | Boolean |
| `USDFIDashChecklistEnabledOnIdleScreen` | Boolean |

</details>

Padrões dinâmicos no código: `DashChecklistItemNameN`, `DashChecklistItemStatusN`

### 8.7 RSC — SimHUD Projection
Prefixo `SimHUDProjection.` — ativo.

<details><summary>6 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `DataUpdateFrametime` | Double |
| `HUD_RawOpacity` | Int32 |
| `HUD_RightScreen` | String |
| `HUD_TopScreen` | String |
| `PluginRunning` | Boolean |
| `PluginVersion` | String |

</details>

### 8.8 RSC — Persistent Odometer
Prefixo `PersistentOdometer.` — ativo.

<details><summary>14 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `DataUpdateFrametime` | Double |
| `Odometer_CurrentCar_LocalUnit` | Double |
| `Odometer_CurrentCar_km` | Double |
| `Odometer_CurrentCar_mi` | Double |
| `Odometer_CurrentGame_LocalUnit` | Double |
| `Odometer_CurrentGame_km` | Double |
| `Odometer_CurrentGame_mi` | Double |
| `Odometer_Displayed_LocalUnit` | Double |
| `Odometer_Displayed_km` | Double |
| `Odometer_Displayed_mi` | Double |
| `Odometer_Global_LocalUnit` | Double |
| `Odometer_Global_km` | Double |
| `Odometer_Global_mi` | Double |
| `PluginRunning` | Boolean |

</details>

### 8.9 RSC — Logitech Battery
Prefixo `LogitechBatteryLevel.` — ativo.

<details><summary>7 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `DataUpdateFrametime` | Double |
| `Logitech_Device1_Battery_Level` | String |
| `Logitech_Device1_Name` | String |
| `Logitech_Device2_Battery_Level` | String |
| `Logitech_Device2_Name` | String |
| `PluginRunning` | Boolean |
| `PluginVersion` | String |

</details>

Padrões dinâmicos no código: `brand{}levelDISABLEDLogitech_Device1_Name`

### 8.10 RSC — Sounds
Prefixo `Sounds.` — ativo.

<details><summary>3 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `DataUpdateFrametime` | Double |
| `PluginRunning` | Boolean |
| `PluginVersion` | String |

</details>

### 8.11 RSC — Updater
Prefixo `Updater.` — ativo.

<details><summary>8 propriedades confirmadas ao vivo</summary>

| Nome | Tipo |
|---|---|
| `DataUpdateFrametime` | Double |
| `PluginRunning` | Boolean |
| `PluginVersion` | String |
| `RSC_AvailableVersion` | String |
| `RSC_CurrentVersion` | String |
| `RSC_UpdateAvailable` | Boolean |
| `SimHub_RequiredVersion` | String |
| `SimHub_UpdateRequired` | Boolean |

</details>

Os plugins RSC também gravam em `InputStatus.*` (ex.: `InputStatus.GraphicalDashPlugin.DashChecklistItemN`, marcha do H-shifter) e todos têm `AAA.ShowAllProps`, `AAA.LogPluginPerformance` e `DataUpdateFrametime`.

> `LovelyPlugin.*` aparece nos dashboards baixados mas o plugin **não está instalado** — essas propriedades não existem nesta máquina.

## 9. Eventos
Usáveis em gatilhos (ShakeIt, LEDs, `timesincelastevent(nome)`). Nome completo: `<Plugin>.<evento>`.

| Origem | Eventos |
|---|---|
| DataCorePlugin | `ABSLevelChanged`, `BrakeBiasChanged`, `Flag_Black`, `Flag_Blue`, `Flag_Checkered`, `Flag_Green`, `Flag_White`, `Flag_Yellow`, `GameStarted`, `GameStopped`, `GameVolumeChanged`, `InputPressed`, `LastLap`, `LowFuelLapAlert`, `LowFuelLapLevelChanged`, `NewLap`, `NewSessionBest`, `NewValidLap`, `PitEnter`, `PitOut`, `RedlineValueChanged`, `SessionRestarted`, `SessionStatusChanged`, `TCLevelChanged` |
| NCalcTemplateParser | `ExternalScript.…` |
| PersistantTrackerPlugin | `NewAllTimeBest`, `NewRecord`, `NewSessionBest` |
| SerialDashPlugin | `CurrentLedLayoutChanged`, `DisplayIntensityChanged`, `RGBIntensityChanged`, `RPMStartOffsetChanged` |

## 10. Ações
Mapeáveis em *Controls and events* e chamáveis por `triggeraction(nome)` ou `GET /api/TriggerAction/<nome>`. "…" = nome com parte dinâmica.

| Origem | Ações |
|---|---|
| AudioPlayPlugin | `DecrementSoundsVolume`, `IncrementSoundsVolume`, `Play_…` |
| AutoBrightness | `DecreaseBrightness`, `IncreaseBrightness`, `SwithControlMode` |
| BeltTensionnerPlugin | `Recalibrate`, `SetMode_LiveTelemetry`, `SetMode_ReleaseAll`, `SetMode_Zero` |
| ControlMapperPlugin | `ToggleMappingOverlay` |
| Dashboard | `Controls.Dashboard.DeltaScreen.FuelSave`, `Controls.Dashboard.DeltaScreen.FuelTarget`, `Controls.Dashboard.DeltaScreen.LapRecord`, `Controls.Dashboard.DeltaScreen.LastLap`, `Controls.Dashboard.DeltaScreen.Next`, `Controls.Dashboard.DeltaScreen.Previous`, `Controls.Dashboard.DeltaScreen.SessionBest`, `Controls.Dashboard.DeltaScreen.Speed`, `Controls.Dashboard.DeltaScreen.SpeedPercet`, `Controls.Dashboard.LeftScreen.Next`, `Controls.Dashboard.LeftScreen.Practice1`, `Controls.Dashboard.LeftScreen.Practice2`, `Controls.Dashboard.LeftScreen.Previous`, `Controls.Dashboard.LeftScreen.Qualy`, `Controls.Dashboard.LeftScreen.Race1`, `Controls.Dashboard.LeftScreen.Race2`, `Controls.Dashboard.LeftScreen.Race3`, `Controls.Dashboard.LeftScreen.Time1`, `Controls.Dashboard.LeftScreen.Time2`, `Controls.Dashboard.LeftScreen.Time3`, `Controls.Dashboard.RightScreen.Next`, `Controls.Dashboard.RightScreen.Previous`, `Controls.Dashboard.RightScreen.Qualy1`, `Controls.Dashboard.RightScreen.Qualy2`, `Controls.Dashboard.RightScreen.Race1`, `Controls.Dashboard.RightScreen.Race2`, `Controls.Dashboard.RightScreen.Race3`, `Controls.Dashboard.RightScreen.Stint1`, `Controls.Dashboard.RightScreen.Stint2`, `Controls.Dashboard.RightScreen.Track`, `Controls.MapToggle`, `Controls.ShowBrakeThrottleGaugesToggle` |
| Data | `BitePointPressed`, `BitePointReleased`, `DeleteLapRecord`, `Downshift`, `LaunchPressed`, `LaunchReleased`, `MinusPressed`, `NBPressed`, `OKPressed`, `PacePressed`, `PaceReleased`, `PitPressed`, `PitReleased`, `PlusPressed`, `RadioPressed`, `RadioReleased`, `ResetSessionBest`, `TCPressed`, `TCReleased`, `Upshift` |
| DataCorePlugin | `DecrementForceFeedback`, `DecrementGameVolume`, `DecrementLowFuelLapLevel`, `DecrementRedLine`, `DecrementSystemVolume`, `IncrementForceFeedback`, `IncrementGameVolume`, `IncrementLowFuelLapLevel`, `IncrementRedLine`, `IncrementSystemVolume`, `MuteDefaultSoundInput`, `ResetMaxSpeed`, `RestartSession`, `ServerKickVoteNo`, `ServerKickVoteYes`, `ShowSimHubMainWindow`, `StartGame`, `StartReplay`, `StartSlowMotion`, `SwitchABS`, `SwitchAutomaticGearbox`, `SwitchDamageDisplayer`, `SwitchInGameApps`, `SwitchPlayersNames`, `SwitchRacingLine`, `SwitchTractionControl`, `ToggleDayNightMode`, `ToggleManualGameActivation`, `TogglePerGearRedline` |
| DisplayManager | `DisplayScreenFor1s_…`, `DisplayScreenFor3s_…`, `DisplayScreen_…`, `GoToFirstScreen…`, `NextScreen…`, `PreviousScreen…` |
| ExtraInputProperties | `DiscardClutchBitePoint…` |
| GraphicalDashPlugin | `CycleNextDash`, `CyclePreviousDash`, `OverlayClose`, `OverlayEditToggle`, `OverlayHideToggle`, `OverlayLayoutRestart`, `_…` |
| IRacingExtraProperties | `Discard_PitEntryExitLines`, `Discard_ReferenceLap`, `Ignition`, `Leaderboard_Relative_ToggleClass`, `Leaderboard_Standing_ToggleClass`, `Leaderboard_Standing_ToggleFocus`, `Pit_Request_All(FuelCalc)`, `Pit_Request_Fuel(FuelCalc)`, `Pit_Toggle_All(FuelCalc)`, `Pit_Toggle_Fuel(FuelCalc)`, `Reload_Textures`, `Replay_Camera_Next`, `Replay_Camera_Previous`, `Replay_Car_Next`, `Replay_Car_Player`, `Replay_Car_Previous`, `Replay_MoveTo_End`, `Replay_MoveTo_Frame_Next`, `Replay_MoveTo_Frame_Previous`, `Replay_MoveTo_Incident_Next`, `Replay_MoveTo_Incident_Previous`, `Replay_MoveTo_Lap_Next`, `Replay_MoveTo_Lap_Previous`, `Replay_MoveTo_Session_Next`, `Replay_MoveTo_Session_Previous`, `Replay_MoveTo_Start`, `Replay_MoveTo_StartOfRace`, `Replay_Speed_FastForward`, `Replay_Speed_PlayPause`, `Replay_Speed_Rewind`, `Replay_Speed_SlowMotion`, `Starter`, `Telemetry_Marker`, `Telemetry_Toggle`, `UniversalDash_ChangeScreen`, `UniversalDash_NextPage`, `UniversalDash_PreviousPage`, `UniversalDash_ToggleTopDisplay`, `{0:00}…` |
| MainWindow | `ToggleRecord…` |
| MotionPlugin | `.DecrementGain…`, `.DecrementSmoothing…`, `.IncrementGain…`, `.IncrementSmoothing…`, `.ToggleIsolated…`, `.ToggleState…`, `Filters.ToggleCrashFilterSoundFeedback`, `Global.BeltTensioner.DecrementOffset`, `Global.BeltTensioner.DisableKeepParked`, `Global.BeltTensioner.IncrementOffset`, `Global.BeltTensioner.ResetOffset`, `Global.BeltTensioner.SetKeepParked`, `Global.BeltTensioner.ToggleKeepParked`, `Global.DisableMotion`, `Global.EnableMotion`, `Global.GlobalMotionSmoothing.Decrement`, `Global.GlobalMotionSmoothing.Increment`, `Global.MotionDetailAmplifier.DecrementGain`, `Global.MotionDetailAmplifier.IncrementGain`, `Global.MotionDetailAmplifier.Toggle`, `Global.NextProfilePreset`, `Global.OpenEffectsCompactView`, `Global.PreviousProfilePreset`, `Global.SuspendMotion`, `Global.ToggleMotionEnabled`, `Global.ToggleTrackProfiler`, `QuickTest.TogglePitchTest`, `QuickTest.ToggleRollTest`, `Recording.MarkMotionTelemetryRecord` |
| NextionTemplateParserBase | `_DisplayScreenFor1s_…`, `_DisplayScreenFor3s_…`, `_GotoScreen_…`, `_NextPage…`, `_PreviousPage…` |
| PersistantTrackerPlugin | `ClearLapHistory`, `DiscardCurrentMap` |
| Rotary | `InCarMenuDec`, `InCarMenuInc`, `InCarMenu…`, `PitMenuDec`, `PitMenuInc`, `PitMenu…` |
| SerialDashPlugin | `DecrementBlinkTriggerRatio`, `DecrementBlinkTriggerRatio_0.2`, `DecrementBlinkTriggerRatio_0.5`, `DecrementBlinkTriggerRatio_1`, `DecrementDisplayIntensity`, `DecrementRGBIntensity`, `IncrementBlinkTriggerRatio`, `IncrementBlinkTriggerRatio_0.2`, `IncrementBlinkTriggerRatio_0.5`, `IncrementBlinkTriggerRatio_1`, `IncrementDisplayIntensity`, `IncrementRGBIntensity`, `NextLedLayout`, `PreviousLedLayout` |
| ShakeITV3PluginBase | `MainFeedbackLevelDecrement`, `MainFeedbackLevelIncrement…`, `ResetCalibration`, `ToggleMuteFeedback` |
| ShakeItWindPlugin | `.DecreaseGain…`, `.IncreaseGain…`, `.MuteToggle…`, `Wind.CurrentModeMuteToggle`, `Wind.DecreaseCurrentModeGain`, `Wind.IncreaseCurrentModeGain`, `Wind.WindMuteToggle` |
| ShellPlugin | `Run_…` |
| SimHUDProjection | `CycleBrightness`, `CycleRightDisplay`, `CycleTopDisplay` |
| SimuLightPlugin | `FreezeCapture`, `NextOtherLightsCaptureAreaProfile`, `PreviousOtherLightsCaptureAreaProfile`, `ToggleAdaLightEnabled`, `ToggleAdaLightSceneMode`, `ToggleFreezeCapture`, `ToggleOtherLightsEnabled`, `ToggleOtherLightsSceneMode`, `UnfreezeCapture` |
| StaticWindSettings | `StaticWind.DecreaseGain`, `StaticWind.IncreaseGain`, `StaticWind.MuteToggle` |
| SystemInfosProvider | `MediaNext`, `MediaPlayPause`, `MediaPrevious` |
| TheManyFacedDash | `ChangeScreen`, `NextPreset/Randomize`, `ToggleNightMode` |
| ThrustmastersPlugin | `DecreaseWheelGain`, `IncreaseWheelGain` |

## 11. Funções de fórmula (NCalc e JavaScript)

### 11.1 Gerais
| Assinatura | Descrição (original) |
|---|---|
| `if(condition,trueResult, falseResult)` | Returs trueResult if condition is true otherwise returns false |
| `in(value,value1, value2, ....)` | Returns true if value is in the specified set of values |
| `abs(value)` | Returns the absolute value of a specified number. |
| `acos(value)` | Returns the angle whose cosine is the specified number. |
| `asin(value)` | Returns the angle whose sine is the specified number. |
| `atan(value)` | Returns the angle whose tangent is the specified number. |
| `max(value1, value2)` | Returns the larger of two specified numbers. |
| `min(value1, value2)` | Returns the smaller of two numbers. |
| `pow(value, power)` | Returns a specified number raised to the specified power. |
| `round(value, rounding)` | Rounds a value to the nearest integer or specified number of decimal places.. |
| `sign(value)` | Returns a value indicating the sign of a number (1 or -1). |
| `sqrt(value)` | Returns the square root of a specified number. |
| `truncate(value)` | Calculates the integral part of a number. |
| `timesincelastevent(eventname)` | Get time in seconds since the last time event happened. |
| `replace(value, 'texttoreplace', 'replacementtext')` | Replace a text |
| `isnull(value,defaultvalue)` | Specify a default value for unavailable data (null) |
| `isnull(value)` | Returns true when data the data is unavailable (null) |
| `rand(maximumvalue)` | Get a random number from 0 to the maximum value |
| `blink(blinkername, blinkdelay, currentstatus)` | Alternate a value when current status is true, blinker name must be unique |
| `format(value, format)` | Format a value using the specified format |
| `format(value, format, addSign)` | Format a value using the specified format, and optionnaly add sign |
| `left(value, postion, lenght)` | return the left n'th caharcters begining from position |
| `right(value, postion, lenght)` | return the right n'th caharcters begining from position |
| `padleft(value, nbchars)` | Returns a new string of a specified length in which the beginning of the current string is padded with spaces |
| `secondstotimespan(seconds)` | Converts a value from seconds to a time value |
| `timespantoseconds(timespan)` | Converts a time value to seconds |
| `toshorttime(timespan, millisecondsPrecision, alwaysAddSign, forceMinutesDisplay )` | Converts a time value to a string |
| `changed(delay, value)` | Returns true for the specified delay when the value has changed. |
| `isincreasing(delay, value)` | Returns true for the specified delay when the value has increased. |
| `maximum(delay, value)` | Returns the maximum detected and keep it for the specified delay. |
| `minimum(delay, value)` | Returns the minimum detected and keep it for the specified delay. |
| `isdecreasing(delay, value)` | Returns true for the specified delay when the value has decreased. |
| `readtextfile('c:\\\\temp\\\\sample.txt')` | Returns the content of the specified file. |
| `scroll(delay, length, 'texttoscroll', [overflowonly])` | Scrolls the text on the specified length and speed(ms). When overflow only is set to true, scroll will only occur when text is longer than the defined length. |
| `lcase('mY Text')` | Returns the text in lower case ('my text'). |
| `ucase('mY Text')` | Returns the text in upper case ('MY TEXT'). |
| `tcase('mY Text')` | Returns the text in title case ('My Text'). |
| `downloadstring(cacheduration, url)` | Download the content at the url and returns it as a string. |
| `downloadstringasync(cacheduration, url)` | Download the content at the url and returns it as a string. First calls will always be null until the first download is done then updates will be done asynchronously (non blocking) |
| `getrpmtickvalue(position)` | Returns the rpm tick value at position (position from 0 to 100). (ie getrpmtickvalue(50) returns 5000 for a 10000 max rpm) |
| `inertia(value,changespersecond)` | Add change "inertia" to a value so it won't update straight to the new value (ncalc only) |
| `prop(name)` | Get property value by name (ncalc only) |
| `triggeraction(actionName)` | Trigger an action based on its name (function always returns true) |
| `compareversions(versiona, versionb)` | Versions in the 1.2.3 or 1.2.3b1 form returns 0 when equals, 1 when versiona > versionb, -1 when versiona < versionb |
| `currentlapgetsectortime(sectorindex, includePreviousSectorsTime)` | Return the time of the given sector (sectorindex starting from 1), when includePreviousSectorsTime is true the time given cumulates the previous sectors time otherwise it only includes the current sector. |
| `lastlapgetsectortime(sectorindex, includePreviousSectorsTime)` | Return the time of the given sector for the last completed lap (sectorindex starting from 1), when includePreviousSectorsTime is true the time given cumulates the previous sectors time otherwise it only includes the current sector. |
| `bestsectortime(sectorindex, includePreviousSectorsTime)` | Return the best sector time of the given sector (sectorindex starting from 1), when includePreviousSectorsTime is true the time given cumulates the previous sectors time otherwise it only includes the current sector. |
| `sessionbestlapgetsectortime(sectorindex, includePreviousSectorsTime)` | Return the time of the given sector for the session best completed lap (sectorindex starting from 1), when includePreviousSectorsTime is true the time given cumulates the previous sectors time otherwise it only includes the current sector. |
| `log(value)` | Log a value for troubleshooting (JS only) |
| `getsharedvalueordefault(scopeName, keyName, defaultvalue)` | Get a value from the shared storage, if it does not exists the default value is returned (but not created), JS only |
| `setsharedvalue(scopeName, keyName, value)` | Store a value available globally to any formulas (the scope is meant to avoid collisions, use a significant one), JS only |
| `getformulainstanceid()` | Get a an uniqueid (string) for the formula execution instance, JS only |

Só existem no NCalc, além das acima: `progress`, `setvalue`, `getvalue`. JS tem também `root`, `setcomponentproperty`, `NewRawData()`, `OldRawData()`.

### 11.2 Dash Studio, cores e controles
| Função | Descrição |
|---|---|
| `activescreenname()` | Returns the current active dashboard or widget screen name (Dash studio only). |
| `rootdashboardscreenname()` | Returns the current root dashboard active screen name (Dash studio only). |
| `dashboardwidth()` | Returns the current dashboard width (before scaling). 0 when out of a dashboard context |
| `dashboardheight()` | Returns the current dashboard height (before scaling). 0 when out of a dashboard context |
| `dashboarddirectory()` | Returns the current dashboard directory. null when out of a dashboard context |
| `repeatindex(depth)` | Returns the current repeat index (depth is optional, 0 will return the last known repeatindex, 1 the previous one (from the first parent repeated layer) etc ...) |
| `isbuttonpressed()` | Returns the pressed state of the first parent button (DashStudio only). |
| `loopingtimer(timeseconds)` | Returns a 0 to 1 value resetting after the defined time. |
| `maptwocolors(currentValue, startValue, endValue, startColor, endColor)` | Returns a mapped color based on the current value and provided bounds values and colors (colors are hex-encoded strings ie #FF00FF) |
| `mapthreecolors(currentValue, startValue, middleValue, endValue, startColor, middleColor, endColor)` | Returns a mapped color based on the current value and provided bounds values and colors (colors are hex-encoded strings ie #FF00FF) |
| `createthreecolorsgradient(mode, startColor, startColorPositionPercent, middleColor,middleColorPositionPercent, endColor,endColorPositionPercent)` | Returns a mapped color based on the current value and provided bounds values and colors (colors are hex-encoded strings ie #FF00FF)  Mode : 0 Vertical, 1 Horizontal, 2 Diagonal startColor, middleColor, endColor : Gradient stops colors (colors are hex-encoded strings ie #FF00FF,#33FF00FF) startColorPositionPercent, middleColorPositionPercent, endColorPositionPercent : Gradient stops percents 0-100 Returns : a gradient to be used in dashstudio |
| `createtwocolorsgradient(mode, startColor, startColorPositionPercent, endColor,endColorPositionPercent)` | Returns a mapped color based on the current value and provided bounds values and colors (colors are hex-encoded strings ie #FF00FF)  Mode : 0 = Vertical, 1 = Horizontal, 2 = Diagonal startColor, endColor : Gradient stops colors (colors are hex-encoded strings ie #FF00FF,#33FF00FF) startColorPositionPercent, endColorPositionPercent : Gradient stops percents 0-100 Returns : a gradient to be used in dashstudio |
| `getcontrollerbuttonstate('vidpidquery', buttonId)` | Estado (bool) do botão buttonId (a partir de 0) do primeiro controle que casa com a query; null se não achar. |
| `getcontrollername('vidpidquery')` | Nome do primeiro controle que casa com a query; null se não achar. |
| `getcontrollerpid('vidpidquery')` | Product ID do controle; null se não achar. |
| `getcontrolleraxis('vidpidquery', axisid)` | Valor do eixo: 0 X, 1 Y, 2 Z, 3-5 rotação X/Y/Z, 6-7 sliders, 8-11 sliders de aceleração/velocidade, 12-14 aceleração X/Y/Z, 15+ POV. |
| (vidpidquery) | VID,PID em hex (`'0x1234,0x4567'`); várias separadas por `;`; `*` é coringa. Requer o plugin de controles e só lê dispositivos habilitados. |

### 11.3 Globais do motor JavaScript (lidas agora do SimHub)
`log`, `getformulainstanceid`, `root`, `setsharedvalue`, `getsharedvalueordefault`, `$propinternal`, `$prop_cache`, `$prop`, `NewRawData`, `OldRawData`, `triggeraction`, `blink`, `format`, `downloadstring`, `downloadstringasync`, `getrpmtickvalue`, `compareversions`, `left`, `padleft`, `right`, `isnull`, `replace`, `rand`, `readtextfile`, `secondstotimespan`, `timespantoseconds`, `ucase`, `lcase`, `tcase`, `toshorttime`, `currentlapgetsectortime`, `lastlapgetsectortime`, `sessionbestlapgetsectortime`, `bestsectortime`, `timesincelastevent`, `setcomponentproperty`, `driveravailable`, `driverisplayer`, `isplayer`, `drivername`, `driverinitials`, `drivershortname`, `drivercarclass`, `driverbestlap`, `driverlastlap`, `driverdeltatoplayer`, `drivercurrentlap`, `driverid`, `drivercarnumber`, `driveriscarinpit`, `driveriscaringarage`, `driveriracingirating`, `drivercarname`, `driverisconnected`, `driveriscarinpitlane`, `drivertrackpositionpercent`, `drivercurrentlaphighprecision`, `driverdeltatobest`, `driverclassposition`, `driverposition`, `driverisoutlap`, `drivercurrentsector`, `driverbestlapsector1`, `driverbestlapsector2`, `driverbestlapsector3`, `driverlastlapsector1`, `driverlastlapsector2`, `driverlastlapsector3`, `drivercurrrentlapsector1`, `drivercurrrentlapsector2`, `driverbestsector1sectortime`, `driverbestsector2sectortime`, `driverbestsector3sectortime`, `driverbestlapsector1sectortime`, `driverbestlapsector2sectortime`, `driverbestlapsector3sectortime`, `driverlastlapsector1sectortime`, `driverlastlapsector2sectortime`, `driverlastlapsector3sectortime`, `drivercurrentlapsector1time`, `drivercurrentlapsector2time`, `driverspeed`, `driverrelativegaptoplayer`, `driverrelativedistancetoplayer`, `drivergaptoleader`, `drivergaptoplayer`, `driverlapstoplayer`, `driverlapstoleader`, `drivergaptoleadercombined`, `driverrelativegaptoplayercombined`, `drivergaptoclassleadercombined`, `driverlapstoclassleader`, `drivergaptoclassleader`, `driverteamname`, `driverclubname`, `driverlicencestring`, `drivercarclasscolor`, `drivercarclasstextcolor`, `driverfronttyrecompound`, `driverreartyrecompound`, `driverfronttyrecompoundgamecode`, `driverreartyrecompoundgamecode`, `drivertimesincelastpitout`, `driverlapsdonesincelastpitout`, `driverpitenteratlap`, `driverpitcount`, `driverpitlastduration`, `drivercurrentlaptime`, `driversplitdeltaself`, `driversplitdeltabestopponent`, `driverpositiongain`, `driverpositiongainclass`, `driverstartposition`, `driverstartpositionclass`, `driverpushtopassstatus`, `driverpushtopasscount`, `driversectorbestlap`, `driversectorlastlap`, `driversectorcurrentlap`, `driversectorbest`, `activescreenname`, `rootdashboardscreenname`, `dashboardwidth`, `dashboardheight`, `dashboarddirectory`, `repeatindex`, `isbuttonpressed`, `loopingtimer`, `getbestsplitleaderboardposition`, `getbestsplittime`, `getbestsplitleaderboardposition_playerclassonly`, `getbestsplittime_playerclassonly`, `getplayerleaderboardposition`, `getopponentleaderboardposition_aheadbehind`, `getopponentleaderboardposition_aheadbehind_playerclassonly`, `getopponentleaderboardposition_playerclassonly`, `getbestlapopponentleaderboardposition`, `getbestlapopponentleaderboardposition_playerclassonly`, `getleaderboardcarclassname`, `getleaderboardcarclasscount`, `getleaderboardcarclasscolor`, `getleaderboardcarclasstextcolor`, `getleaderboardcarclassopponentscount`, `maptwocolors`, `mapthreecolors`, `createthreecolorsgradient`, `createtwocolorsgradient`, `getcontrollerbuttonstate`, `getcontrollername`, `getcontrollerpid`, `getcontrolleraxis`

## 12. API HTTP local (`http://localhost:8888`)
| Rota | O que faz |
|---|---|
| `GET /api/GetProperty/{nome}` | Valor de uma propriedade (200) ou 204. |
| `GET /api/EvaluateStringFormula?formula=...&interpreter=0\|1` | Avalia uma fórmula (0 = NCalc, 1 = JavaScript). |
| `GET /api/GetGamedata` | Objeto GameData inteiro em JSON. |
| `GET /api/GetGameDataSimple` | Versão resumida. |
| `GET /api/GetLeaderboarddata`, `/api/GetPlayerLeaderboarddata`, `/api/Getaheadbehinddata` | Leaderboard e vizinhos. |
| `GET /api/GetSessionLapsHistory` | Histórico de voltas da sessão. |
| `GET /api/GetLedsData` | Estado dos LEDs. |
| `GET /api/TriggerAction/{acao}`, `/api/TriggerInput/{input}` | Dispara ação/input. |
| `POST /api/ExternalInput/Press\|Release`, `/api/StreamDeckInput/...` | Inputs externos. |
| `GET /api/Dashboards/GetDashboards` | Dashboards instalados. |
| `/api/Devices/*`, `/api/Motion/*`, `/api/ControlMapper/*` | Dispositivos, Motion, Control Mapper. |

Não há rota que liste todas as propriedades: `PluginManager.GetAllPropertiesNames()` existe, mas não é exposto por HTTP nem ao JavaScript (o Jint roda sem acesso ao CLR).

## 13. Limites desta análise
- **Ao vivo vazio não é "não existe"**: o servidor devolve 204 também para valor nulo. Fora de sessão, muito do `GameData` e do `GameRawData` é nulo.
- Variáveis de `GameRawData.Telemetry` dependem do carro (o irsdk publica conjuntos diferentes); a lista de §6.1 é a amostra que o SimHub guardou.
- Nomes vindos de configuração do usuário (sensores do Afterburner/HWiNFO, efeitos do ShakeIt, botões de controle, expressões e scripts) só podem ser listados com a configuração em uso.
- Descrições de `GameData` são minhas, a partir do nome, tipo e uso; as de §5 e §11 são o texto do próprio SimHub.
- Ferramentas usadas (reflexão/IL) ficaram fora do projeto; para regenerar, pedir de novo.
