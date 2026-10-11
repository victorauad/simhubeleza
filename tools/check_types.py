#!/usr/bin/env python3
"""Confere os tipos dos campos dos .djson gerados contra referencia-manual/.

O SimHub (Newtonsoft) nao aceita numero com casa decimal em campo inteiro:
um `100.0` em BorderStyle.RadiusTopLeft derruba o Editar e o Executar. Aqui
cada campo que nas referencias e sempre inteiro precisa sair inteiro.

Uso:  python3 tools/check_types.py PASTA_DO_DASH [...]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _kind(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    return type(v).__name__


def _walk(node, out, owner=""):
    """Junta (tipo do item, campo) -> valor de cada escalar."""
    if isinstance(node, dict):
        owner = node.get("$type", owner).split(",")[0].split(".")[-1]
        for k, v in node.items():
            if isinstance(v, (dict, list)):
                _walk(v, out, owner)
            else:
                out.append(((owner, k), v))
    elif isinstance(node, list):
        for x in node:
            _walk(x, out, owner)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def int_fields():
    """Campos que em todas as referencias aparecem so como inteiro."""
    seen = defaultdict(set)
    for p in (ROOT / "referencia-manual").glob("*.djson"):
        acc = []
        _walk(_load(p), acc)
        for key, v in acc:
            seen[key].add(_kind(v))
    return {key for key, kinds in seen.items() if kinds == {"int"}}


def check(dirs):
    ints = int_fields()
    errors = []
    for d in dirs:
        for p in sorted(Path(d).glob("*.djson")):
            acc = []
            _walk(_load(p), acc)
            for key, v in acc:
                if key in ints and _kind(v) != "int":
                    errors.append(f"{p.name}: {key[0]}.{key[1]} = {v!r}")
    return errors


if __name__ == "__main__":
    errs = check(sys.argv[1:])
    for e in errs:
        print(e)
    print("tipos ok" if not errs else f"{len(errs)} campo(s) inteiro(s) com valor nao inteiro")
    sys.exit(1 if errs else 0)
