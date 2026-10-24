"""Versoes de medicao do dash (Fase 0 de `docs/otimizacao.md`).

Cada versao e o dash de hoje com secoes removidas -- os componentes nao
mudam, so saem da arvore. Comparando o SimHub rodando cada uma no mesmo
replay:

  full     o dash de hoje
  minimal  so RPM/LEDs, marcha, velocidade, delta, pedais e avisos
  empty    so o fundo (cartoes vazios)

completo - vazio = quanto o dash custa; completo - minimo = quanto um dash
minimo economizaria.

Os fundos dos cartoes ficam (estaticos, custo desprezivel) para a imagem
continuar com a mesma moldura. Topo e centro nao leem nada das laterais
(o armazenamento compartilhado de `states.py` so e usado nas laterais),
entao cortar as laterais nao muda o que sobra na tela.
"""

#: Caminhos (nomes separados por "/") removidos em cada versao.
DROP = {
    "full": (),
    "minimal": (
        "Mid Component2/Right Component/Lap Validity Recorder",
        "Mid Component2/Right Component/Ref Lap Recorder",
        "Mid Component2/Right Component/Sectors",
        "Mid Component2/Right Component/New Lap Info",
        "Mid Component2/Right Component/Standings",
        "Mid Component2/Right Component/Relative",
        "Mid Component2/Right Component/Practice",
        "Mid Component2/Center Component/OTS",
        "Mid Component2/Left Component2/Telemetry",
        "Mid Component2/Left Component2/Damage",
        "Mid Component2/Left Component2/Weather",
        "Mid Component2/Left Component2/Lap Review",
        "Mid Component2/Left Component2/Weather Live",
        "Mid Component2/Left Component2/Lap Review Live",
        "Mid Component2/Left Component2/Car",
        "Mid Component2/Left Component2/Session",
    ),
}
DROP["empty"] = DROP["minimal"] + (
    "Mid Component2/Center Component/Speed & Gear",
    "Top Component/LEDs",
    "Top Component/Gas & Brake",
    "Top Component/Delta",
    "Top Component/Alerrts",
    "Top Component/Alerrts2",
)

NAMES = tuple(DROP)


def apply(items, variant):
    """Copia de `items` sem as secoes de `variant`. Falha se um caminho
    nao existir (nome mudou no gerador) em vez de medir a versao errada."""
    drop = set(DROP[variant])
    found = set()

    def walk(node, path):
        here = f"{path}/{node.get('Name') or ''}".lstrip("/")
        if here in drop:
            found.add(here)
            return None
        node = dict(node)
        if node.get("Childrens"):
            node["Childrens"] = [c for c in (walk(c, here) for c in node["Childrens"])
                                 if c is not None]
        return node

    out = [n for n in (walk(item, "") for item in items) if n is not None]
    missing = drop - found
    if missing:
        raise SystemExit(f"variante {variant}: secoes nao encontradas: {sorted(missing)}")
    return out
