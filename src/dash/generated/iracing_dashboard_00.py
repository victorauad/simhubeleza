"""Dashboard iRacing_Dashboard_00 -- arvore de controles.

GERADO por tools/decompile.py a partir de referencia-manual/iRacing_Dashboard_00.djson.
Ponto de partida da refatoracao; paridade validada por tools/parity.py.
"""

from dash.center import layer as center
from dash.left import layer as left
from dash.right import layer as right
from dash.top_bar import layer as top_bar
from simhub.bindings import formatted, js, ncalc
from simhub.model import (
    OFF, ChartItem, GearText, GradientItem, GroupItem, ImageItem,
    Layer, LinearGaugeItem, RectangleItem, TextItem, WidgetItem,
)

#: Campos do dashboard fora da arvore de controles.
SHELL = {
    "DashboardDebugManager": {
        "WindowPositionSettings": {
            "IsFullScreen": False,
            "Position": '656,831,610,247',
            "TopMost": False,
            "AllowTransparency": True,
            "CloseOnMonitorLoss": False,
            "NoWindowActivate": False,
        },
    },
    "Version": 2,
    "Id": 'a26990bf-4cdf-4ac2-91f4-1ab4388eb874',
    "BaseHeight": 517,
    "BaseWidth": 1280,
    "BackgroundColor": '#FF000000',
    "SnapToGrid": False,
    "HideLabels": True,
    "ShowForeground": True,
    "ForegroundOpacity": 100.0,
    "ShowBackground": True,
    "BackgroundOpacity": 100.0,
    "ShowBoundingRectangles": False,
    "GridSize": 10,
    "Images": [
        {
            "Name": 'PositionGain',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Width": 29,
            "Height": 29,
            "Length": 263,
            "MD5": '228196f73364c8ed0d14b1a51189ab25',
        },
        {
            "Name": 'PositionLoss',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 288,
            "MD5": '43370360d704296ceb6e0d2bb4f86b61',
        },
        {
            "Name": 'cadillac',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 16513,
            "MD5": '4b846debac81d8de3947ca30d1f321cf',
        },
        {
            "Name": 'dallara',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 3154,
            "MD5": '052147260bac0998b82e035b875eacba',
        },
        {
            "Name": 'ferrari',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Width": 199,
            "Height": 199,
            "Length": 21526,
            "MD5": 'f6dddc59693ca722f1ee8962315e7934',
        },
        {
            "Name": 'ford',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 18051,
            "MD5": '075f47bf3b4d61877268d2db52f9268a',
        },
        {
            "Name": 'mazda',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 17571,
            "MD5": 'cbae5d6701ed36445e206343282e40c6',
        },
        {
            "Name": 'LEDSBLUE',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Width": 100,
            "Height": 100,
            "Length": 11925,
            "MD5": '8d54f5864c7a792047c220d7b1bc38c8',
        },
        {
            "Name": 'LEDSOFF',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Width": 100,
            "Height": 100,
            "Length": 1732,
            "MD5": '2e45558835d312c5befcd418ddefb206',
        },
        {
            "Name": 'LEDSRED',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Width": 100,
            "Height": 100,
            "Length": 14765,
            "MD5": 'd0957a6f4cf75bd1e1981ac55b23cafb',
        },
        {
            "Name": 'LEDSYELLOW',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Width": 100,
            "Height": 100,
            "Length": 13448,
            "MD5": '15d7b8569e48901e7bd8c613174a30c6',
        },
        {
            "Name": 'CenterRings_Gray',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Width": 551,
            "Height": 550,
            "Length": 174355,
            "MD5": 'f1267af75a6e3463b016b6df86b30d0a',
        },
        {
            "Name": 'CenterRings_Blue',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 36252,
            "MD5": 'bbd02a1c1c7698c38e1b673a6b72bc6f',
        },
        {
            "Name": 'CenterRings_Red',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 34616,
            "MD5": '491f68837bc225617cd572e47f44497a',
        },
        {
            "Name": 'CenterRings_Green',
            "Extension": '.png',
            "Modified": False,
            "Optimized": True,
            "Length": 158315,
            "MD5": 'aec337fceae231aaa25182a1e08645e6',
        },
    ],
    "Metadata": {
        "ScreenCount": 1.0,
        "InGameScreensIndexs": [
            0,
        ],
        "IdleScreensIndexs": [],
        "MainPreviewIndex": 0,
        "IsOverlay": False,
        "OverlaySizeWarning": True,
        "MetadataVersion": 2.0,
        "EnableOnDashboardMessaging": True,
        "PitScreensIndexs": [],
        "SimHubVersion": '9.10.6',
        "Width": 1280.0,
        "Height": 517.0,
        "DashboardVersion": '',
    },
    "ShowOnScreenControls": True,
    "IsOverlay": False,
    "EnableClickThroughOverlay": True,
    "EnableOnDashboardMessaging": True,
    "UseStrictJSIsolation": False,
    "UseStrictJSIsolationWarning": True,
}

#: Campos da tela fora da lista de itens.
SCREEN = {
    "RenderingSkip": 0,
    "Name": 'Screen',
    "InGameScreen": True,
    "IdleScreen": False,
    "PitScreen": False,
    "ScreenId": '78d787d0-a235-49cf-8b9c-d36edfee5fa0',
    "AllowOverlays": True,
    "IsForegroundLayer": False,
    "IsOverlayLayer": False,
    "OverlayTriggerExpression": {
        "Expression": '',
    },
    "ScreenEnabledExpression": {
        "Expression": "if([GameRawData.Telemetry.IsInGarage]='TRUE',1,0)",
    },
    "OverlayMaxDuration": 0,
    "OverlayMinDuration": 0,
    "IsBackgroundLayer": False,
    "BackgroundColor": '#00FFFFFF',
    "MinimumRefreshIntervalMS": 0.0,
}


def items():
    """Itens de nivel superior da tela."""
    return [
        Layer(
            RectangleItem(
                name='OverallBG',
                BackgroundColor='#FF212121',
                BorderStyle={
                    "RadiusTopLeft": 40,
                    "RadiusTopRight": 40,
                    "RadiusBottomLeft": 10,
                    "RadiusBottomRight": 10,
                },
                Height=515.0,
                Left=0.0,
                Opacity=85.0,
                Top=-1.0,
                Width=1280.0,
            ),
            right(),
            center(),
            left(),
            name='Mid Component2',
            Opacity=95.0,
        ),
        top_bar(),
    ]
