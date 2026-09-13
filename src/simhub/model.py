"""Primitivas de controle do SimHub.

Um controle e apenas um dict pronto para serializacao. O DSL se limita a
preencher o "$type" correto e a aplicar os defaults do tipo, de modo que o
codigo do dashboard so precise declarar o que realmente difere.
"""

from .defaults import DEFAULTS, TYPES

class _Sentinel:
    def __repr__(self):
        return "OFF"


#: Remove um campo herdado dos defaults. None nao serve para isso porque o
#: proprio SimHub grava nulos com significado (ex.: Width ausente em Layer).
OFF = _Sentinel()

#: Idem para `name`, que pode legitimamente valer None ou "".
_UNSET = _Sentinel()


def control(type_name, *children, name=_UNSET, bindings=None, **fields):
    """Monta um controle do tipo indicado.

    Filhos posicionais viram "Childrens"; `fields` sobrescreve os defaults.
    Passe OFF em um campo para remove-lo do resultado.
    """
    if type_name not in DEFAULTS:
        raise KeyError(f"tipo desconhecido: {type_name}")

    node = {"$type": TYPES[type_name]}
    node.update(DEFAULTS[type_name])
    for key, value in fields.items():
        if value is OFF:
            node.pop(key, None)
        else:
            node[key] = value

    if name is not _UNSET:
        node["Name"] = name
    if bindings:
        node["Bindings"] = bindings
    if children:
        node["Childrens"] = list(children)
    return node


def _maker(type_name):
    def make(*children, **kwargs):
        return control(type_name, *children, **kwargs)
    make.__name__ = type_name
    make.__doc__ = f"Cria um {type_name}."
    return make


# Um construtor por tipo presente no dashboard de referencia.
Layer = _maker("Layer")
GroupItem = _maker("GroupItem")
RectangleItem = _maker("RectangleItem")
TextItem = _maker("TextItem")
LinearGaugeItem = _maker("LinearGaugeItem")
GradientItem = _maker("GradientItem")
ChartItem = _maker("ChartItem")
ImageItem = _maker("ImageItem")
GearText = _maker("GearText")
WidgetItem = _maker("WidgetItem")
