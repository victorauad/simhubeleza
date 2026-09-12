"""Escrita da pasta DashTemplates.

Um dashboard do SimHub nao e um arquivo unico: e um .djson com a arvore de
controles, alguns arquivos irmaos de metadados, um ZIP com as imagens e as
pastas de fontes e extensoes JS. Este modulo monta tudo a partir dos assets
em disco.
"""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ASSETS = ROOT / "assets"


def dashboard_json(shell, screen, items):
    """Recompoe o dashboard completo a partir do shell e da arvore."""
    data = dict(shell)
    data["Screens"] = [dict(screen, Items=items)]
    return data


def write_json(path, data, indent=None):
    text = json.dumps(data, separators=(",", ":") if indent is None else None,
                      indent=indent, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")


def verify_images(images):
    """Confere que Images[] descreve fielmente os PNGs em assets/images.

    O SimHub usa MD5 e Length para decidir se precisa recarregar um recurso,
    entao uma divergencia aqui se manifesta como imagem que nao atualiza.
    """
    problems = []
    for entry in images:
        source = ASSETS / "images" / (entry["Name"] + entry["Extension"])
        if not source.exists():
            problems.append(f"{source.name}: ausente em assets/images")
            continue
        raw = source.read_bytes()
        if int(entry["Length"]) != len(raw):
            problems.append(f"{source.name}: Length {entry['Length']} != {len(raw)}")
        digest = hashlib.md5(raw).hexdigest()
        if digest != entry["MD5"]:
            problems.append(f"{source.name}: MD5 {entry['MD5']} != {digest}")
    return problems


def write_resources(path, images):
    """Gera o ZIP .ressources com os PNGs declarados em Images[]."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for entry in images:
            name = entry["Name"] + entry["Extension"]
            archive.write(ASSETS / "images" / name, arcname=name)


def write_dashboard(out_dir, name, shell, screen, items, metadata=None,
                    carclasses=None):
    """Escreve <name>.djson e seus arquivos irmaos em out_dir."""
    out_dir.mkdir(parents=True, exist_ok=True)
    data = dashboard_json(shell, screen, items)

    write_json(out_dir / f"{name}.djson", data)
    write_json(out_dir / f"{name}.djson.carclasses", carclasses or [])
    if metadata is not None:
        write_json(out_dir / f"{name}.djson.metadata", metadata, indent=2)

    images = data.get("Images") or []
    if images:
        problems = verify_images(images)
        if problems:
            raise ValueError("assets inconsistentes:\n  " + "\n  ".join(problems))
        write_resources(out_dir / f"{name}.djson.ressources", images)
    return data


def verify_fonts(items):
    """Confere que toda fonte referenciada na arvore existe em assets/fonts.

    Uma fonte ausente nao quebra nada na geracao: o SimHub cai numa fonte
    padrao em silencio, e o dashboard so parece "quase certo" na tela. Entao
    a checagem e aqui, onde da para falhar alto.
    """
    available = {path.stem.split("-")[0].lower()
                 for path in (ASSETS / "fonts").iterdir() if path.is_file()}
    used = set()

    def walk(node):
        family = node.get("Font")
        if isinstance(family, str) and family:
            used.add(family)
        for child in (node.get("Childrens") or []):
            walk(child)

    for item in items:
        walk(item)

    missing = sorted(name for name in used
                     if name.replace(" ", "").lower() not in available)
    return missing


def copy_support_files(out_dir, previews=()):
    """Copia fontes, extensoes JS e previews para a pasta do dashboard."""
    fonts = out_dir / "_SHFonts"
    fonts.mkdir(parents=True, exist_ok=True)
    for font in sorted((ASSETS / "fonts").iterdir()):
        shutil.copy2(font, fonts / font.name)

    scripts = out_dir / "JavascriptExtensions"
    scripts.mkdir(parents=True, exist_ok=True)
    for script in sorted((ASSETS / "js").iterdir()):
        shutil.copy2(script, scripts / script.name)

    for preview in previews:
        shutil.copy2(ASSETS / "previews" / preview, out_dir / preview)
