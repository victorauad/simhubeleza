"""Renderiza um dashboard .djson como HTML autonomo, para revisao de design.

E uma aproximacao estatica: desenha a arvore com os valores de placeholder que
cada controle carrega, sem avaliar formulas. Serve para conferir posicionamento,
contraste e hierarquia sem abrir o SimHub -- nao para conferir telemetria.

Uso:  python3 tools/preview.py [pasta] [-o saida.html]
"""
import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

#: Nome da fonte no SimHub -> arquivo em assets/fonts.
FONT_FILES = {
    "Funnel Sans": "FunnelSans-VariableFont_wght.ttf",
    "Audiowide": "Audiowide-Regular.ttf",
    "Arame Mono": "ArameMono.ttf",
    "0Arame Mono": "ArameMono.ttf",
}

FALLBACK = "system-ui, sans-serif"

#: Sobrescreve a contagem de repeticoes de todas as camadas repetidas, para
#: revisar a coluna cheia sem depender do valor gravado no editor.
REPEAT_OVERRIDE = 0

#: Como tratar controles cujo Visible depende de formula. "hide" mostra o
#: estado de repouso do dashboard, que e o que o piloto ve a maior parte do
#: tempo; "show" revela todas as camadas condicionais sobrepostas.
CONDITIONAL = "hide"

#: HorizontalAlignment / VerticalAlignment do SimHub -> flexbox.
H_ALIGN = {0: "flex-start", 1: "center", 2: "flex-end"}
V_ALIGN = {0: "flex-start", 1: "center", 2: "flex-end"}


def short_type(node):
    return node["$type"].split(",")[0].split(".")[-1]


def css_color(argb):
    """#AARRGGBB do SimHub -> rgba() do CSS."""
    if not isinstance(argb, str) or not argb.startswith("#"):
        return "transparent"
    value = argb[1:]
    if len(value) == 8:
        a, r, g, b = (int(value[i:i + 2], 16) for i in (0, 2, 4, 6))
        return f"rgba({r},{g},{b},{a / 255:.3f})"
    if len(value) == 6:
        return f"#{value}"
    return "transparent"


def font_family(name):
    if name in FONT_FILES:
        return f"'{name}', {FALLBACK}"
    return FALLBACK


def border_css(style):
    """BorderStyle -> raio e borda."""
    if not isinstance(style, dict):
        return ""
    out = []
    radii = [style.get(k, 0) or 0 for k in
             ("RadiusTopLeft", "RadiusTopRight", "RadiusBottomRight", "RadiusBottomLeft")]
    if any(radii):
        out.append("border-radius:" + " ".join(f"{r}px" for r in radii))
    color = style.get("BorderColor")
    widths = [style.get(k, 0) or 0 for k in
              ("BorderTop", "BorderRight", "BorderBottom", "BorderLeft")]
    if color and any(widths):
        out.append("border-style:solid")
        out.append("border-width:" + " ".join(f"{w}px" for w in widths))
        out.append(f"border-color:{css_color(color)}")
        out.append("box-sizing:border-box")
    return ";".join(out)


def box_css(node):
    """Geometria e opacidade comuns a todos os itens posicionados."""
    parts = ["position:absolute"]
    for prop, key in (("left", "Left"), ("top", "Top"),
                      ("width", "Width"), ("height", "Height")):
        if node.get(key) is not None:
            parts.append(f"{prop}:{node[key]}px")
    opacity = node.get("Opacity")
    if opacity is not None and opacity != 100:
        parts.append(f"opacity:{opacity / 100:.3f}")
    blur = node.get("BlurRadius")
    if blur:
        parts.append(f"filter:blur({blur / 2:.1f}px)")
    return parts


def render_text(node, text_key="Text"):
    """TextItem e GearText: caixa flex com a fonte e o alinhamento do controle."""
    parts = box_css(node)
    parts.append("display:flex")
    parts.append(f"justify-content:{H_ALIGN.get(node.get('HorizontalAlignment', 0), 'flex-start')}")
    parts.append(f"align-items:{V_ALIGN.get(node.get('VerticalAlignment', 1), 'center')}")
    parts.append(f"font-family:{font_family(node.get('Font'))}")
    parts.append(f"font-size:{node.get('FontSize', 16)}px")
    parts.append(f"color:{css_color(node.get('TextColor') or node.get('GearTextColor'))}")
    weight = node.get("FontWeight")
    if weight:
        parts.append("font-weight:" + {"Thin": "200", "Light": "300", "Normal": "400",
                                       "Medium": "500", "SemiBold": "600", "Bold": "700",
                                       "ExtraBold": "800", "Black": "900"}.get(weight, "400"))
    background = node.get("BackgroundColor")
    if background:
        parts.append(f"background:{css_color(background)}")
    parts.append(border_css(node.get("BorderStyle")))
    if node.get("UseMonospacedText"):
        parts.append("font-variant-numeric:tabular-nums")
        parts.append("letter-spacing:0.02em")
    parts.append("white-space:pre")
    parts.append("line-height:1")
    parts.append("overflow:hidden")

    content = node.get(text_key) or node.get("DesignerText") or ""
    return f'<div style="{";".join(p for p in parts if p)}">{escape(str(content))}</div>'


def render_rectangle(node):
    parts = box_css(node)
    parts.append(f"background:{css_color(node.get('BackgroundColor'))}")
    parts.append(border_css(node.get("BorderStyle")))
    return f'<div style="{";".join(p for p in parts if p)}"></div>'


def render_gauge(node):
    """LinearGaugeItem: trilho com preenchimento proporcional ao valor."""
    minimum = node.get("Minimum", 0.0) or 0.0
    maximum = node.get("Maximum", 100.0) or 100.0
    value = node.get("Value", 0.0) or 0.0
    span = (maximum - minimum) or 1
    fraction = max(0.0, min(1.0, (value - minimum) / span))

    parts = box_css(node)
    parts.append(f"background:{css_color(node.get('BackgroundColor'))}")
    parts.append(border_css(node.get("BorderStyle")))
    parts.append("overflow:hidden")

    horizontal = (node.get("GaugeOrientation", 0) == 0)
    # GaugeAlignment 1 preenche a partir da ponta oposta.
    reverse = node.get("GaugeAlignment", 0) == 1
    fill = [f"background:{css_color(node.get('GaugeColor'))}", "position:absolute"]
    if horizontal:
        fill += [f"width:{fraction * 100:.2f}%", "height:100%", "top:0",
                 "right:0" if reverse else "left:0"]
    else:
        fill += [f"height:{fraction * 100:.2f}%", "width:100%", "left:0",
                 "top:0" if reverse else "bottom:0"]
    return (f'<div style="{";".join(p for p in parts if p)}">'
            f'<div style="{";".join(fill)}"></div></div>')


def render_gradient(node):
    """GradientItem: so a moldura. O brush do SimHub nao tem equivalente direto."""
    parts = box_css(node)
    parts.append(border_css(node.get("BorderStyle")))
    return f'<div style="{";".join(p for p in parts if p)}"></div>'


def render_image(node, images):
    parts = box_css(node)
    data = images.get(node.get("Image"))
    if data:
        parts.append(f"background-image:url(data:image/png;base64,{data})")
        parts.append("background-size:contain")
        parts.append("background-repeat:no-repeat")
        parts.append("background-position:center")
    return f'<div style="{";".join(p for p in parts if p)}"></div>'


def escape(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def render_widget(node, folder, images, depth):
    """WidgetItem: outro dashboard embutido, desenhado em escala."""
    parts = box_css(node)
    parts.append("overflow:hidden")

    target = folder / (node.get("FileName") or "")
    if not target.exists():
        parts.append("outline:1px dashed rgba(255,0,0,.6)")
        return f'<div style="{";".join(p for p in parts if p)}"></div>'

    data = json.loads(target.read_text(encoding="utf-8"))
    inner = render_screen(data, folder, images, depth + 1)

    # AutoSize ajusta o widget a caixa; senao usa a escala gravada.
    if node.get("AutoSize") and data.get("BaseWidth"):
        scale = (node.get("Width") or data["BaseWidth"]) / data["BaseWidth"]
    else:
        scale = node.get("AutoSizeScale") or 1.0

    stage = (f'position:absolute;left:0;top:0;'
             f'width:{data.get("BaseWidth", 100)}px;'
             f'height:{data.get("BaseHeight", 100)}px;'
             f'transform:scale({scale:.4f});transform-origin:top left')
    return (f'<div style="{";".join(p for p in parts if p)}">'
            f'<div style="{stage}">{inner}</div></div>')


def render_node(node, folder, images, depth=0):
    if node.get("Visible") is False:
        return ""
    if CONDITIONAL != "show" and "Visible" in (node.get("Bindings") or {}):
        return ""

    kind = short_type(node)
    if kind in ("Layer", "GroupItem"):
        style = ["position:absolute", "left:0", "top:0", "width:100%", "height:100%"]
        opacity = node.get("Opacity")
        if opacity is not None and opacity != 100:
            style.append(f"opacity:{opacity / 100:.3f}")

        children = node.get("Childrens") or []
        inner = "".join(render_node(c, folder, images, depth) for c in children)

        # Uma camada repetida desenha copias deslocadas verticalmente. Em
        # execucao o SimHub resolve a contagem por formula; aqui usamos o valor
        # gravado, ou o override de --repeat.
        repetitions = REPEAT_OVERRIDE if REPEAT_OVERRIDE else node.get("Repetitions") or 0
        offset = node.get("RepeatTopOffset") or 0
        if repetitions and offset:
            copies = []
            for index in range(int(repetitions)):
                shift = f"transform:translateY({offset * index}px)"
                copies.append(f'<div style="position:absolute;inset:0;{shift}">{inner}</div>')
            inner = "".join(copies)

        return f'<div style="{";".join(style)}">{inner}</div>'

    if kind == "TextItem":
        return render_text(node)
    if kind == "GearText":
        return render_text(node, text_key="DesignerText")
    if kind == "RectangleItem":
        return render_rectangle(node)
    if kind == "LinearGaugeItem":
        return render_gauge(node)
    if kind == "GradientItem":
        return render_gradient(node)
    if kind == "ImageItem":
        return render_image(node, images)
    if kind == "WidgetItem":
        return render_widget(node, folder, images, depth)
    if kind == "ChartItem":
        # O historico de telemetria so existe em tempo de execucao.
        parts = box_css(node)
        parts.append("outline:1px dashed rgba(255,255,255,.15)")
        return f'<div style="{";".join(p for p in parts if p)}"></div>'
    return ""


def render_screen(data, folder, images, depth=0):
    screen = data["Screens"][0]
    return "".join(render_node(item, folder, images, depth)
                   for item in screen["Items"])


def load_images():
    """PNGs dos recursos, em base64, para embutir no HTML."""
    out = {}
    image_dir = ASSETS / "images"
    if image_dir.exists():
        for path in sorted(image_dir.glob("*.png")):
            out[path.stem] = base64.b64encode(path.read_bytes()).decode()
    return out


def font_faces():
    """@font-face embutidos, para o preview bater com o render do SimHub."""
    faces = []
    for name, filename in FONT_FILES.items():
        path = ASSETS / "fonts" / filename
        if not path.exists():
            continue
        data = base64.b64encode(path.read_bytes()).decode()
        faces.append(
            f"@font-face{{font-family:'{name}';"
            f"src:url(data:font/ttf;base64,{data}) format('truetype');"
            f"font-weight:100 900;font-display:block}}"
        )
    return "\n".join(faces)


PAGE = """<meta charset="utf-8">
<title>{title}</title>
<style>
{faces}
:root {{ color-scheme: dark; }}
body {{ margin:0; background:#0b0b0c; color:#e8e8ea;
        font-family:system-ui,sans-serif; padding-block:24px; }}
.wrap {{ max-width:{width}px; margin:0 auto; padding:0 16px; }}
h1 {{ font-size:15px; font-weight:600; margin:0 0 4px; letter-spacing:.01em; }}
p.sub {{ font-size:12px; color:#8e8e93; margin:0 0 16px; }}
.frame {{ position:relative; width:{width}px; height:{height}px;
          background:{background}; overflow:hidden;
          border-radius:6px; box-shadow:0 0 0 1px #2c2c2e; }}
.scaler {{ transform-origin: top left; }}
@media (max-width: {breakpoint}px) {{
  .frame {{ transform: scale(var(--fit)); }}
  .shell {{ height: calc({height}px * var(--fit)); }}
}}
</style>
<div class="wrap">
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
  <div class="shell"><div class="frame">{body}</div></div>
</div>
<script>
// Encolhe o quadro em telas estreitas sem alterar as coordenadas internas.
function fit() {{
  const wrap = document.querySelector('.wrap');
  const available = wrap.clientWidth - 32;
  const scale = Math.min(1, available / {width});
  document.documentElement.style.setProperty('--fit', scale);
}}
addEventListener('resize', fit); fit();
</script>
"""


#: Versao sem moldura: so o painel, do tamanho exato do dashboard. Serve para
#: embutir o preview em outra pagina, que entao cuida do enquadramento.
BARE_PAGE = """<meta charset="utf-8">
<title>{title}</title>
<style>
{faces}
:root {{ color-scheme: dark; }}
html, body {{ margin:0; background:{background}; }}
.frame {{ position:relative; width:{width}px; height:{height}px;
          background:{background}; overflow:hidden; }}
</style>
<div class="frame">{body}</div>
"""


def render_dashboard(folder, name=None, title=None, subtitle="", bare=False):
    """Gera o HTML de um dashboard da pasta indicada."""
    folder = Path(folder)
    candidates = sorted(folder.glob("*.djson"))
    if name:
        target = folder / f"{name}.djson"
    else:
        # O dashboard principal e o que tem arquivo .metadata ao lado.
        with_meta = [p for p in candidates if (folder / (p.name + ".metadata")).exists()]
        target = (with_meta or candidates)[0]

    data = json.loads(target.read_text(encoding="utf-8"))
    images = load_images()
    body = render_screen(data, folder, images)
    width = data.get("BaseWidth", 1280)
    height = data.get("BaseHeight", 517)

    return (BARE_PAGE if bare else PAGE).format(
        title=title or target.stem,
        subtitle=subtitle or f"{width}x{height} — render estatico, sem avaliar formulas",
        faces=font_faces(),
        width=width, height=height,
        breakpoint=width + 64,
        background=css_color(data.get("BackgroundColor")) or "#000",
        body=body,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", default=str(ROOT / "build" / "iRacing_Dashboard_00"),
                        help="pasta do dashboard gerado")
    parser.add_argument("-n", "--name", help="nome do .djson (sem extensao)")
    parser.add_argument("-t", "--title", help="titulo do preview")
    parser.add_argument("-b", "--bare", action="store_true",
                        help="so o painel, sem titulo nem moldura")
    parser.add_argument("-o", "--out", default=str(ROOT / "build" / "preview.html"))
    parser.add_argument("-c", "--conditional", choices=("hide", "show"),
                        default="hide",
                        help="controles acionados por formula")
    parser.add_argument("-r", "--repeat", type=int, default=0,
                        help="forca a contagem de linhas das camadas repetidas")
    args = parser.parse_args(argv)

    global REPEAT_OVERRIDE, CONDITIONAL
    REPEAT_OVERRIDE = args.repeat
    CONDITIONAL = args.conditional

    html = render_dashboard(args.folder, args.name, args.title, bare=args.bare)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"preview: {out}  ({len(html) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
