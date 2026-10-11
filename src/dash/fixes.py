"""Propriedades do original trocadas de proposito pela certa.

Cada entrada e (padrao, substituicao, motivo). O build passa por toda
formula da arvore e aplica as que valem para a arvore inteira (`TREE`); a
auditoria (`tools/formula_audit.py`) aplica todas ao original antes de
comparar, entao a troca aparece como CORRIGIDA, nao como formula sumida.

Fonte: `docs/propriedades-simhub-completo.md` (reflexao nas DLLs do SimHub
9.10.6 e consulta na API local).
"""
import re

from .states import SESSION_TYPE_JS

#: Prefixo do plugin em minuscula: o SimHub registra pelo nome da classe,
#: `IRacingExtraProperties.` (sec. 1.1 e 8.1). Vem do original, na linha do
#: jogador do leaderboard e do overflow.
PREFIX = (re.compile(r"(?<![A-Za-z])iRacingExtraProperties\."),
          "IRacingExtraProperties.")

#: Trocas aplicadas pelo build em toda formula.
TREE = [PREFIX]

#: Trocas feitas nos modulos (a nova expressao ja sai do gerador); aqui so
#: para a auditoria reconhecer.
AUDIT = TREE + [
    # `SessionTypeName` nao existe no SimHub (docs/propriedades.txt).
    (re.compile(r"\$prop\((['\"])SessionTypeName\1\)"), SESSION_TYPE_JS),
    # `GameData.NewData.*` e a copia legada e oculta (sec. 3); a barra fina
    # ja lia o nome certo, agora o numero tambem.
    (re.compile(r"\[DataCorePlugin\.GameData\.NewData\.DeltaToSessionBest\]"),
     "[DataCorePlugin.GameData.DeltaToSessionBest]"),
    # `RemainingLaps` fica 0 em corrida por tempo; o plugin estima.
    (re.compile(r"\[RemainingLaps\]"),
     "[IRacingExtraProperties.iRacing_LapsRemaining]"),
    # "Volta invalida": a condicao do original (ultima < melhor) nao detecta
    # volta invalida; o plugin diz se a volta atual esta limpa.
    (re.compile(r"if\(\[LastLapTime\]\s*<\s*\[BestLapTime\]\s*&&\s*"
                r"timespantoseconds\(\[LastLapTime\]\)\s*!=\s*0,\s*1,\s*0\)"),
     "if(isnull([IRacingExtraProperties.iRacing_Player_CurrentLapIsClean], "
     "true), 0, 1)"),
]


def fix(expression, table=TREE):
    for pattern, replacement in table:
        expression = pattern.sub(lambda _: replacement, expression)
    return expression


def apply(items):
    """Aplica `TREE` a toda formula da arvore (in place) e devolve `items`."""
    def walk(node):
        for binding in (node.get("Bindings") or {}).values():
            formula = binding.get("Formula") or {}
            if formula.get("Expression"):
                formula["Expression"] = fix(formula["Expression"])
        for child in (node.get("Childrens") or []):
            walk(child)

    for item in items:
        walk(item)
    return items
