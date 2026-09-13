# simhubeleza

Dashboard SimHub para a **Super Formula SF23 / iRacing**, gerado inteiramente
por código — sem nenhuma edição no editor visual do SimHub.

## Uso

```bash
python3 build.py                      # gera em build/
python3 build.py "/caminho/DashTemplates"   # instala direto no SimHub
```

Sem dependências externas: apenas a stdlib do Python 3.

## Estrutura

| Caminho | Papel |
|---|---|
| `build.py` | Entrypoint: monta a pasta `DashTemplates` completa |
| `src/simhub/` | DSL: tipos de controle, bindings, escrita dos arquivos |
| `src/dash/generated/` | Árvore de controles do dashboard |
| `assets/` | Imagens, fontes, extensões JS e previews |
| `tools/` | Decompilador e verificador de paridade |
| `referencia-manual/` | Dashboard original feito à mão — baseline intocado |

## Verificação

```bash
python3 build.py && python3 tools/parity.py
```

`parity.py` compara o que foi gerado com `referencia-manual/` de forma
estrutural (ordem de chaves e ruído de float são normalizados; o `.ressources`
é comparado pelo conteúdo do ZIP). O critério é **diff vazio**.

## Dependências de plugin no SimHub

O dashboard consome propriedades de plugins que precisam estar instalados:

- **DahlDesign** — push-to-pass do SF23 (`OTAllowed`, `OTActive`, `OTTimeLeft`,
  `OTCooldownActive`), `PitBoxPosition`
- **IRacingExtraProperties** — leaderboard de classe, `iRacing_Class_SoF`,
  `iRacing_Player_iRGainEstimation`
- **PersistantTrackerPlugin** — `SessionBestLiveDeltaProgressSeconds`

## Regenerar a partir do dashboard manual

```bash
python3 tools/derive_defaults.py   # defaults e nomes de tipo por controle
python3 tools/decompile.py         # .djson -> código Python do DSL
```
