---
name: co-coach-handoff
description: Gera um arquivo de memória da sessão atual, salva em memory/YYYYMMDD-projeto.md e imprime um bloco pronto para colar na próxima sessão. Use quando quiser encerrar uma sessão e retomar depois sem perder contexto. Trigger: "/co-coach-handoff", "salva a sessão", "handoff", "encerra a sessão".
---

# Skill: co-coach-handoff

Quando invocado, siga estes passos na ordem:

## 1. Identificar projeto e data

- **Data:** use o formato YYYYMMDD (ex: 20260620)
- **Projeto:** nome da pasta do working directory atual (ex: `co-coach`, `iracing_analysis`)
- **Nome do arquivo:** `YYYYMMDD-projeto.md` dentro da pasta `memory/` do projeto atual

## 2. Criar a pasta memory/ se não existir

```bash
mkdir -p memory
```

## 3. Gerar o arquivo de memória

Escreva o arquivo `memory/YYYYMMDD-projeto.md` com este formato exato:

```markdown
# Handoff — [projeto] — [YYYY-MM-DD]

## O que foi feito nesta sessão
[Lista dos principais itens concluídos — seja específico: arquivos criados/editados, decisões tomadas, problemas resolvidos]

## Estado atual
[Descrição honesta de onde o projeto está agora — o que funciona, o que está pela metade]

## Próximos passos
[Lista ordenada do que fazer na próxima sessão, do mais importante ao menos]

## Decisões e contexto importantes
[Qualquer decisão não óbvia tomada nesta sessão, razões, trade-offs — o que uma IA nova precisaria saber para não refazer o caminho]

## Arquivos relevantes
[Caminhos dos arquivos tocados ou que importam para retomar]
```

Preencha cada seção com base na conversa atual. Seja direto — omita o que não aconteceu.

## 4. Imprimir o bloco de retomada

Após salvar o arquivo, imprima exatamente isto (substituindo os campos):

---

**Arquivo salvo:** `memory/YYYYMMDD-projeto.md`

**Para retomar, rode `/clear` e cole na nova sessão:**

```
Leia o arquivo memory/YYYYMMDD-projeto.md e retome de onde paramos. Confirme o que foi feito e qual é o próximo passo.
```

---

Não faça mais nada após imprimir o bloco. A sessão continua aberta para o usuário decidir quando rodar `/clear`.
