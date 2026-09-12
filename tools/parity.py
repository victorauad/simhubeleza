"""Compara o dashboard gerado com o feito a mao.

A comparacao e estrutural, nao textual: o SimHub usa Json.NET, que ignora a
ordem das chaves, e floats vindos do C# carregam ruido de representacao
(32.999999999999993). Normalizamos os dois lados e exigimos diff vazio.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "referencia-manual"
GEN = ROOT / "build" / "iRacing_Dashboard_00"

FLOAT_PRECISION = 6


def normalize(value):
    if isinstance(value, float):
        rounded = round(value, FLOAT_PRECISION)
        return int(rounded) if rounded == int(rounded) else rounded
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in sorted(value.items())}
    if isinstance(value, list):
        return [normalize(v) for v in value]
    if isinstance(value, str):
        # O editor grava quebras de linha como CRLF; a diferenca e cosmetica.
        return value.replace("\r\n", "\n")
    return value


def diff(expected, actual, path="", out=None):
    """Coleta divergencias como (caminho, esperado, obtido)."""
    out = [] if out is None else out
    if type(expected) is not type(actual) and not (
        isinstance(expected, (int, float)) and isinstance(actual, (int, float))
    ):
        out.append((path, f"<{type(expected).__name__}>", f"<{type(actual).__name__}>"))
        return out

    if isinstance(expected, dict):
        for key in sorted(set(expected) | set(actual)):
            if key not in expected:
                out.append((f"{path}.{key}", "<ausente>", repr(actual[key])[:70]))
            elif key not in actual:
                out.append((f"{path}.{key}", repr(expected[key])[:70], "<ausente>"))
            else:
                diff(expected[key], actual[key], f"{path}.{key}", out)
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            out.append((path, f"{len(expected)} itens", f"{len(actual)} itens"))
        for i, (e, a) in enumerate(zip(expected, actual)):
            diff(e, a, f"{path}[{i}]", out)
    elif expected != actual:
        out.append((path, repr(expected)[:70], repr(actual)[:70]))
    return out


def diff_zip(ref_path, gen_path, name):
    import zipfile
    with zipfile.ZipFile(ref_path) as a, zipfile.ZipFile(gen_path) as b:
        expected = {n: a.read(n) for n in a.namelist()}
        actual = {n: b.read(n) for n in b.namelist()}
    problems = []
    for member in sorted(set(expected) | set(actual)):
        if member not in expected:
            problems.append((f"{name}/{member}", "<ausente>", "<presente>"))
        elif member not in actual:
            problems.append((f"{name}/{member}", "<presente>", "<ausente>"))
        elif expected[member] != actual[member]:
            problems.append((f"{name}/{member}", "<bytes>", "<bytes diferentes>"))
    return problems


def compare_file(name):
    ref_path, gen_path = REF / name, GEN / name
    if not gen_path.exists():
        return [(name, "<arquivo>", "<nao gerado>")]
    if name.endswith(".ressources"):
        # ZIP: comparamos o conteudo, nao os bytes. O nivel de compressao e o
        # timestamp variam entre gravacoes sem que o recurso mude.
        return diff_zip(ref_path, gen_path, name)
    if name.endswith(".png"):
        same = ref_path.read_bytes() == gen_path.read_bytes()
        return [] if same else [(name, "<bytes>", "<bytes diferentes>")]
    expected = normalize(json.loads(ref_path.read_text(encoding="utf-8")))
    actual = normalize(json.loads(gen_path.read_text(encoding="utf-8")))
    return diff(expected, actual, name)


def main():
    targets = [p.name for p in sorted(REF.iterdir()) if p.is_file()]
    failures = 0
    for name in targets:
        problems = compare_file(name)
        status = "OK " if not problems else "DIFF"
        print(f"[{status}] {name}")
        for path, expected, actual in problems[:12]:
            print(f"        {path}\n          esperado: {expected}\n          obtido:   {actual}")
        if len(problems) > 12:
            print(f"        ... mais {len(problems) - 12} divergencias")
        failures += len(problems)

    print()
    if failures:
        print(f"FALHA: {failures} divergencias")
        return 1
    print("PARIDADE OK: nenhuma divergencia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
