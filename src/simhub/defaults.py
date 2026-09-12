"""Defaults e nomes de tipo dos controles.

GERADO por tools/derive_defaults.py -- nao editar a mao.
Um campo so entra em DEFAULTS se aparece em todas as instancias do tipo.
"""

#: Nome curto -> "$type" completo gravado pelo SimHub.
TYPES = {
    "ChartItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.ChartItem, SimHub.Plugins",
    "GearText": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.BuiltIn.GearText, SimHub.Plugins",
    "GradientItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.GradientItem, SimHub.Plugins",
    "GroupItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.GroupItem, SimHub.Plugins",
    "ImageItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.ImageItem, SimHub.Plugins",
    "Layer": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.Layer, SimHub.Plugins",
    "LinearGaugeItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.LinearGaugeItem, SimHub.Plugins",
    "RectangleItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.RectangleItem, SimHub.Plugins",
    "TextItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.TextItem, SimHub.Plugins",
    "WidgetItem": "SimHub.Plugins.OutputPlugins.GraphicalDash.Models.WidgetItem, SimHub.Plugins"
}

DEFAULTS = {
    "ChartItem": {
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "ChartEnabled": True,
        "ChartSuspended": False,
        "CurrentValue": 20.0,
        "Height": 244.0,
        "Left": 0.0,
        "LineColor": "#FFD53849",
        "LineTickness": 5,
        "Maximum": 100.0,
        "Minimum": 0.0,
        "MinimumRefreshIntervalMS": 10.0,
        "PointsCount": 600.0,
        "RenderingSkip": 1,
        "Top": 3.0,
        "UseMaximum": True,
        "UseMinimum": True,
        "Visible": True,
        "Width": 586.0
    },
    "GearText": {
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "DesignerText": "N",
        "Font": "Audiowide",
        "FontSize": 253.0,
        "FontWeight": "Bold",
        "GearBackgoundColor": "#00FFFFFF",
        "GearBlinkBackground": False,
        "GearBlinkBackgroundColor": "#FFFF4500",
        "GearBlinkDelay": 100,
        "GearBlinkText": False,
        "GearBlinkTextColor": "#FFFF00FF",
        "GearTextColor": "#CEDAA520",
        "Height": 280.0,
        "HorizontalAlignment": 1,
        "IgnoreNeutralGear": False,
        "IsTextItem": True,
        "Left": 495.5,
        "MinimumRefreshIntervalMS": 0.0,
        "NoDataText": "N",
        "RenderingSkip": 0,
        "TextColor": "#CEDAA520",
        "Top": 172.0,
        "VerticalAlignment": 1,
        "Visible": True,
        "Width": 285.0
    },
    "GradientItem": {
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "BorderStyle": {
            "BorderBottom": 2,
            "BorderColor": "#51FFD700",
            "BorderLeft": 2,
            "BorderRight": 2,
            "BorderTop": 2,
            "RadiusBottomLeft": 10,
            "RadiusBottomRight": 10,
            "RadiusTopLeft": 10,
            "RadiusTopRight": 10
        },
        "Color": {
            "RadialGradientBrush": {
                "@Center": "0.5,0.5",
                "@GradientOrigin": "0.5,0.5",
                "@MappingMode": "RelativeToBoundingBox",
                "@Opacity": "1",
                "@RadiusX": "0.5",
                "@RadiusY": "0.5",
                "@SpreadMethod": "Pad",
                "@xmlns": "http://schemas.microsoft.com/winfx/2006/xaml/presentation",
                "RadialGradientBrush.GradientStops": {
                    "GradientStop": [
                        {
                            "@Color": "#FF595959",
                            "@Offset": "0"
                        },
                        {
                            "@Color": "#BB393939",
                            "@Offset": "1"
                        }
                    ]
                }
            }
        },
        "Height": 369.0,
        "Left": 492.5,
        "MinimumRefreshIntervalMS": 0.0,
        "RenderingSkip": 0,
        "Top": 124.0,
        "Visible": False,
        "Width": 291.0
    },
    "GroupItem": {
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "ChildAlignmentHorizontal": 0,
        "ChildAlignmentVertical": 0,
        "ChildsMargin": {},
        "ChildsPositioning": 0,
        "ChildsPositioningAlignment": 0,
        "GroupPadding": {},
        "Height": 19.0,
        "Left": 11.0,
        "MinimumRefreshIntervalMS": 0.0,
        "RenderingSkip": 0,
        "Top": 227.0,
        "Visible": True,
        "Width": 592.0
    },
    "ImageItem": {
        "AutoSize": False,
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "Height": 65.0,
        "Image": "PositionGain",
        "Left": 400.0,
        "MinimumRefreshIntervalMS": 0.0,
        "RenderingSkip": 0,
        "Top": 315.0,
        "Visible": True,
        "Width": 40.0
    },
    "Layer": {
        "BlinkPhasisInverted": False,
        "Group": True,
        "MinimumRefreshIntervalMS": 0.0,
        "RenderingSkip": 0,
        "Repetitions": 0,
        "Visible": True
    },
    "LinearGaugeItem": {
        "AlternateGaugeColor": "#FF008000",
        "AutoSize": False,
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "BorderStyle": {
            "BorderBottom": 1,
            "BorderColor": "#00FFFFFF",
            "BorderLeft": 1,
            "BorderRight": 1,
            "BorderTop": 1,
            "RadiusBottomLeft": 10,
            "RadiusBottomRight": 10,
            "RadiusTopLeft": 10,
            "RadiusTopRight": 10
        },
        "GaugeAlignment": 0,
        "GaugeColor": "#FF008B8B",
        "GaugeOrientation": 0,
        "Height": 9.0,
        "IsLinearGauge": True,
        "Left": 642.0,
        "Maximum": 100.0,
        "Minimum": 0.0,
        "MinimumRefreshIntervalMS": 0.0,
        "PAW": 145.0,
        "RenderingSkip": 0,
        "Steps": 0.0,
        "Top": 11.0,
        "UseAlternateStyle": False,
        "Value": 100.0,
        "Visible": True,
        "Width": 145.0
    },
    "RectangleItem": {
        "BackgroundColor": "#FF1E1E1E",
        "BlinkPhasisInverted": False,
        "BorderStyle": {
            "RadiusBottomLeft": 5,
            "RadiusBottomRight": 5,
            "RadiusTopLeft": 5,
            "RadiusTopRight": 5
        },
        "Height": 30.0,
        "IsRectangleItem": True,
        "Left": 268.0,
        "MinimumRefreshIntervalMS": 0.0,
        "RenderingSkip": 0,
        "Top": 9.0,
        "Visible": True,
        "Width": 58.0
    },
    "TextItem": {
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "Font": "Funnel Sans",
        "FontSize": 24.0,
        "Height": 40.0,
        "HorizontalAlignment": 1,
        "IsTextItem": True,
        "Left": 31.0,
        "MinimumRefreshIntervalMS": 0.0,
        "RenderingSkip": 0,
        "Text": "00",
        "TextColor": "#FF008B8B",
        "Top": 418.75,
        "VerticalAlignment": 1,
        "Visible": True,
        "Width": 70.0
    },
    "WidgetItem": {
        "AutoSize": True,
        "BackgroundColor": "#00FFFFFF",
        "BlinkPhasisInverted": False,
        "EnableScreenRolesAndActivation": True,
        "FileName": "RPMLed.djson",
        "FreezePageChanges": True,
        "Height": 49.0,
        "InitialScreenIndex": 0,
        "Left": 11.5,
        "MinimumRefreshIntervalMS": 0.0,
        "NextScreenCommand": 0,
        "PreviousScreenCommand": 0,
        "RenderingSkip": 0,
        "Top": 125.0,
        "Visible": True,
        "Width": 333.0
    }
}
