"""N/A em vez de campo em branco.

Regra do dash: dado que deveria aparecer e nao veio (propriedade ausente,
nula, NaN) mostra "N/A" -- nunca um buraco na tela, que nao da para
distinguir de "zero", "travou" ou "nao existe".

Em vez de repetir a guarda em cada formula, o build passa por todo binding
de `Text` e envolve a expressao:

  - JavaScript: roda a formula original numa funcao e troca null, undefined
    e NaN por 'N/A'. String vazia (`''`) devolvida de proposito continua
    vazia: e o jeito das formulas dizerem "esta linha nao existe" (volta que
    ainda nao aconteceu, posicao vaga no leaderboard, carro que nao ha).
  - NCalc: `isnull(expressao, 'N/A')`.

Onde a formula original devolve a propriedade crua mesmo numa linha vaga, o
`PRESENT` diz quando a linha existe; fora dela o campo fica vazio.

Alguns campos do dash original nao ficam nulos: sao escondidos (`Visible`)
enquanto o dado nao existe -- diferenca de volta nas duas primeiras voltas,
last lap do relative antes da primeira volta, gap antes do tracking. Para
esses (`HIDDEN`), o build poe ao lado um gemeo identico com o texto "N/A",
visivel exatamente quando o original esta escondido numa linha que existe.

O texto da formula original fica intacto entre o prefixo e o sufixo --
`unwrap` devolve o original (a auditoria compara contra o dash de
referencia); os `Visible` originais nem sao tocados.
"""
import copy

from simhub.theme import TEXT_TERTIARY

NA = "N/A"

JS_HEAD = "var __v = (function () {\r\n"
JS_TAIL = (
    "\r\n})();\r\n"
    "if (__v == null || (typeof __v === 'number' && isNaN(__v))) "
    f"return __present() ? '{NA}' : '';\r\n"
    "return __v;"
)
NC_HEAD = "isnull("
NC_TAIL = f", '{NA}')"

#: Controles cuja formula original devolve o valor cru tambem nas linhas
#: vagas: (caminho terminando no controle) -> condicao JS de "a linha existe".
#: Fora daqui toda linha conta como existente.
BOARD = "IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_"
PRESENT = {
    "Standings/Leaderboard/DriverName": (
        f"$prop('{BOARD}' + format((repeatindex() - 1), '00') + "
        "'_PositionInClass') != 0"),
}


#: Campos escondidos pelo original enquanto nao ha dado: (caminho terminando
#: no controle) -> condicao de "a linha existe", na lingua do `Visible`
#: original (JS: corpo de funcao com return; NCalc: expressao).
PLAYER_POS = "$prop('IRacingExtraProperties.iRacing_Player_PositionInClass')"
OVERFLOW_INDEX = (
    "var index;\r\n"
    "if ($prop('PlayerClassOpponentsCount') - " + PLAYER_POS + " <= 5) "
    "{ index = $prop('PlayerClassOpponentsCount') - 10; }\r\n"
    "else { index = " + PLAYER_POS + " - 5; }\r\n"
)


def _board_row(offset):
    """A linha do leaderboard tem piloto e nao e a do jogador (a diferenca
    para si mesmo nao e dado faltando: fica vazia como no original)."""
    return (
        f"var r = repeatindex(){offset};\r\n"
        f"return $prop('{BOARD}' + format((r - 1), '00') + "
        f"'_PositionInClass') != 0 && !(r == {PLAYER_POS} && {PLAYER_POS} != 0);"
    )


def _relative_row(side):
    return (f"isnull(prop('IRacingExtraProperties.RLB_{side}_Name_0'"
            "+repeatindex()),'')!=''")


HIDDEN = {
    "Standings/Leaderboard/LastLapDifference": _board_row(""),
    "Standings/Leaderboard Overflow/LastLapDifference":
        OVERFLOW_INDEX + _board_row(" + index"),
    "Relative/Driver Ahead Repeat/Last Lap": _relative_row("Ahead"),
    "Relative/Driver Ahead Repeat/Gap": _relative_row("Ahead"),
    "Relative/Driver Behind Repeat/Last Lap": _relative_row("Behind"),
    "Relative/Driver Behind Repeat/Gap": _relative_row("Behind"),
    "Relative/Me/Last Lap": "true",
}


def _present_js(condition):
    body = "return true;" if condition is None else f"return ({condition});"
    return f"var __present = function () {{ {body} }};\r\n"


def wrap_js(expression, present=None):
    return _present_js(present) + JS_HEAD + expression + JS_TAIL


def wrap_ncalc(expression):
    return NC_HEAD + expression + NC_TAIL


def unwrap(expression):
    """A formula original de dentro do envelope (ou ela mesma)."""
    if expression.startswith(NC_HEAD) and expression.endswith(NC_TAIL):
        return expression[len(NC_HEAD):-len(NC_TAIL)]
    start = expression.find(JS_HEAD)
    if (start >= 0 and expression.startswith("var __present = ")
            and expression.endswith(JS_TAIL)):
        return expression[start + len(JS_HEAD):-len(JS_TAIL)]
    return expression


def _wrap(binding, path):
    formula = binding.get("Formula") or {}
    expression = formula.get("Expression")
    if not expression or unwrap(expression) != expression:
        return
    if formula.get("Interpreter") == 1:
        present = next((cond for tail, cond in PRESENT.items()
                        if path.endswith(tail)), None)
        formula["Expression"] = wrap_js(expression, present)
    else:
        formula["Expression"] = wrap_ncalc(expression)


def _twin(node, present):
    """Gemeo "N/A" de um campo que o original esconde sem dado."""
    visible = node["Bindings"]["Visible"]
    formula = visible["Formula"]
    original = formula["Expression"]
    if formula.get("Interpreter") == 1:
        expression = (
            f"var __present = function () {{\r\n{present}\r\n}};\r\n"
            "if (!__present()) return 0;\r\n"
            f"var __shown = function () {{\r\n{original}\r\n}};\r\n"
            "return __shown() ? 0 : 1;")
    else:
        expression = f"({present}) && !({original})"
    twin = copy.deepcopy(node)
    twin["Name"] = f"{node.get('Name')} N/A"
    twin["Text"] = NA
    twin["TextColor"] = TEXT_TERTIARY
    # Parado (preview, editor) fica escondido: quem decide e o binding.
    twin["Visible"] = False
    twin["Bindings"] = {"Visible": {**copy.deepcopy(visible),
                                    "Formula": {**formula, "Expression": expression}}}
    return twin


def apply(items):
    """Envolve todo binding de Text da arvore (in place) e devolve `items`."""
    def walk(node, path):
        here = f"{path}/{node.get('Name') or ''}"
        text = (node.get("Bindings") or {}).get("Text")
        if text:
            _wrap(text, here)
        children = node.get("Childrens") or []
        for child in list(children):
            walk(child, here)
            child_path = f"{here}/{child.get('Name') or ''}"
            present = next((cond for tail, cond in HIDDEN.items()
                            if child_path.endswith(tail)), None)
            if present is not None:
                children.insert(children.index(child) + 1, _twin(child, present))

    for item in items:
        walk(item, "")
    return items
