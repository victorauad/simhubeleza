"""Bindings e expressoes.

Um binding liga uma propriedade do controle (Text, Visible, TextColor, ...) a
uma formula avaliada em tempo de execucao. O SimHub aceita duas linguagens:
NCalc, o default, e JavaScript, sinalizado por "Interpreter": 1.
"""


def ncalc(expression):
    """Formula NCalc. Referencia propriedades como [Plugin.Campo]."""
    return {"Formula": {"Expression": expression}, "Mode": 2}


def js(expression, jsext=0, format_string=None):
    """Formula JavaScript. Referencia propriedades via $prop('Plugin.Campo').

    `jsext` seleciona o conjunto de extensoes JavaScript visivel a formula.
    `format_string` formata o valor retornado (ex.: 'mm\\:ss\\.ff').
    """
    binding = {
        "Formula": {"JSExt": jsext, "Interpreter": 1, "Expression": expression},
        "Mode": 2,
    }
    if format_string is not None:
        binding["FormatString"] = format_string
    return binding


def formatted(expression, format_string):
    """Formula NCalc com string de formato (ex.: '+0.00')."""
    binding = ncalc(expression)
    binding["FormatString"] = format_string
    return binding


def prop(name):
    """Referencia NCalc a uma propriedade."""
    return f"[{name}]"


def driver_prop(index_expression, field):
    """Propriedade do leaderboard de classe do IRacingExtraProperties.

    As linhas sao enderecadas por indice de dois digitos, entao o nome da
    propriedade e montado em tempo de execucao a partir do indice da repeticao.
    """
    return (
        "$prop('IRacingExtraProperties.iRacing_ClassLeaderboard_Driver_' + "
        f"format(({index_expression}), '00') + '_{field}')"
    )
