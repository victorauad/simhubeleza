"""Tokens visuais do dashboard.

Centraliza cores e metricas que estavam espalhadas como literais na arvore
exportada pelo editor. Redesenhos passam por aqui.
"""

# --- Cores ------------------------------------------------------------------

LED_OFF = "#FF1E1E1E"
LED_RPM = "#FFDAA520"        # goldenrod: preenchimento progressivo de RPM
SHIFT = "#FFFF00FF"          # magenta: hora de trocar a marcha
SHIFT_BORDER = "#FFFF60F1"
LIMITER = "#FF00FFFF"        # ciano: pit limiter ativo
LIMITER_BORDER = "#FF40E0D0"

# --- Bordas -----------------------------------------------------------------

CORNER_RADIUS = 5


def rounded(border_color=None, thickness=3):
    """BorderStyle com cantos arredondados e borda opcional."""
    style = {}
    if border_color is not None:
        style["BorderColor"] = border_color
        style.update({
            "BorderTop": thickness, "BorderBottom": thickness,
            "BorderLeft": thickness, "BorderRight": thickness,
        })
    style.update({
        "RadiusTopLeft": CORNER_RADIUS, "RadiusTopRight": CORNER_RADIUS,
        "RadiusBottomLeft": CORNER_RADIUS, "RadiusBottomRight": CORNER_RADIUS,
    })
    return style
