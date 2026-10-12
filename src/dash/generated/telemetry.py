"""Dashboard Telemetry -- arvore de controles.

GERADO por tools/decompile.py a partir de referencia-manual/Telemetry.djson.
Ponto de partida da refatoracao; paridade validada por tools/parity.py.
"""

from simhub.bindings import formatted, js, ncalc
from simhub.theme import (
    BRAKE_REF, STEER_LIVE, STEER_REF, TEXT_SECONDARY, THROTTLE_REF,
)
from simhub.model import (
    OFF, ChartItem, GearText, GradientItem, GroupItem, ImageItem,
    Layer, LinearGaugeItem, RectangleItem, TextItem, WidgetItem,
)

#: Campos do dashboard fora da arvore de controles.
SHELL = {
    "DashboardDebugManager": {
        "WindowPositionSettings": {
            "IsFullScreen": False,
            "Position": '182,182,607,250',
            "TopMost": False,
            "AllowTransparency": False,
            "CloseOnMonitorLoss": False,
            "NoWindowActivate": False,
        },
    },
    "Version": 2,
    "Id": 'ddeb90e3-9996-4b3c-b1d6-01f2c02eba3e',
    "BaseHeight": 250,
    "BaseWidth": 607,
    "BackgroundColor": '#FF000000',
    "SnapToGrid": False,
    "HideLabels": False,
    "ShowForeground": True,
    "ForegroundOpacity": 100.0,
    "ShowBackground": True,
    "BackgroundOpacity": 100.0,
    "ShowBoundingRectangles": False,
    "GridSize": 10,
    "Images": [],
    "Metadata": {
        "ScreenCount": 1.0,
        "InGameScreensIndexs": [
            0,
        ],
        "IdleScreensIndexs": [
            0,
        ],
        "MainPreviewIndex": 0,
        "IsOverlay": False,
        "OverlaySizeWarning": False,
        "MetadataVersion": 2.0,
        "EnableOnDashboardMessaging": True,
        "PitScreensIndexs": [],
        "SimHubVersion": '9.10.6',
        "Width": 607.0,
        "Height": 250.0,
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
    "IdleScreen": True,
    "PitScreen": False,
    "ScreenId": 'e4524095-7ce9-44c9-a644-0167a6fb160f',
    "AllowOverlays": True,
    "IsForegroundLayer": False,
    "IsOverlayLayer": False,
    "OverlayTriggerExpression": {
        "Expression": '',
    },
    "ScreenEnabledExpression": {
        "Expression": '',
    },
    "OverlayMaxDuration": 0,
    "OverlayMinDuration": 0,
    "IsBackgroundLayer": False,
    "BackgroundColor": '#FF000000',
    "MinimumRefreshIntervalMS": 0.0,
}


def items():
    """Itens de nivel superior da tela."""
    return [
        Layer(
            Layer(
                RectangleItem(
                    name='bg5',
                    BackgroundColor='#00000000',
                    BorderStyle={
                        "RadiusTopLeft": 8,
                        "RadiusTopRight": 8,
                        "RadiusBottomLeft": 8,
                        "RadiusBottomRight": 8,
                    },
                    Height=250.0,
                    Left=7.0,
                    Opacity=60.0,
                    Top=0.0,
                    Width=600.0,
                ),
                GroupItem(
                    RectangleItem(
                        name='RectangleItem',
                        BackgroundColor='#FF2A2F35',
                        BorderStyle={
                            "BorderColor": '#00FFFFFF',
                        },
                        Height=1.0,
                        Left=0.0,
                        Width=590.0,
                    ),
                    TextItem(
                        name='TextItem',
                        Font='Arame Mono',
                        FontSize=18.0,
                        Text='0',
                        TextColor='#FF6B717A',
                        BackgroundColor='#FF181B1F',
                        BorderStyle={
                            "RadiusTopLeft": 5,
                            "RadiusTopRight": 5,
                            "RadiusBottomLeft": 5,
                            "RadiusBottomRight": 5,
                        },
                        Height=19.0,
                        Left=559.0,
                        Top=0.0,
                        Width=33.0,
                    ),
                    TextItem(
                        name='TextItem2',
                        Font='Arame Mono',
                        FontSize=18.0,
                        Text='0',
                        TextColor='#FF6B717A',
                        BackgroundColor='#FF181B1F',
                        BorderStyle={
                            "RadiusTopLeft": 5,
                            "RadiusTopRight": 5,
                            "RadiusBottomLeft": 5,
                            "RadiusBottomRight": 5,
                        },
                        Height=19.0,
                        Left=559.0,
                        Top=0.0,
                        Width=33.0,
                    ),
                    name='0',
                ),
                RectangleItem(
                    name='Line 1',
                    BackgroundColor='#FF1F2328',
                    BorderStyle={
                        "BorderColor": '#00FFFFFF',
                    },
                    Height=1.0,
                    Left=11.0,
                    Top=208.0,
                    Width=590.0,
                ),
                GroupItem(
                    RectangleItem(
                        name='RectangleItem',
                        BackgroundColor='#FF2A2F35',
                        BorderStyle={
                            "BorderColor": '#00FFFFFF',
                        },
                        Height=1.0,
                        Left=0.0,
                        Width=590.0,
                    ),
                    TextItem(
                        name='TextItem',
                        Font='Arame Mono',
                        FontSize=18.0,
                        Text='25',
                        TextColor='#FF6B717A',
                        BackgroundColor='#FF181B1F',
                        BorderStyle={
                            "RadiusTopLeft": 5,
                            "RadiusTopRight": 5,
                            "RadiusBottomLeft": 5,
                            "RadiusBottomRight": 5,
                        },
                        Height=19.0,
                        Left=559.0,
                        Top=0.0,
                        Width=33.0,
                    ),
                    name='25',
                    Top=171.0,
                ),
                RectangleItem(
                    name='Line 2',
                    BackgroundColor='#FF1F2328',
                    BorderStyle={
                        "BorderColor": '#00FFFFFF',
                    },
                    Height=1.0,
                    Left=11.0,
                    Top=152.0,
                    Width=590.0,
                ),
                GroupItem(
                    RectangleItem(
                        name='RectangleItem',
                        # Zero do volante: um degrau mais claro que 25/75.
                        BackgroundColor='#FF3E454E',
                        BorderStyle={
                            "BorderColor": '#00FFFFFF',
                        },
                        Height=1.0,
                        Left=0.0,
                        Width=590.0,
                    ),
                    TextItem(
                        name='TextItem',
                        Font='Arame Mono',
                        FontSize=18.0,
                        Text='50',
                        TextColor='#FF6B717A',
                        BackgroundColor='#FF181B1F',
                        BorderStyle={
                            "RadiusTopLeft": 5,
                            "RadiusTopRight": 5,
                            "RadiusBottomLeft": 5,
                            "RadiusBottomRight": 5,
                        },
                        Height=19.0,
                        Left=559.0,
                        Top=0.0,
                        Width=33.0,
                    ),
                    name='50',
                    Top=115.5,
                ),
                RectangleItem(
                    name='Line 3',
                    BackgroundColor='#FF1F2328',
                    BorderStyle={
                        "BorderColor": '#00FFFFFF',
                    },
                    Height=1.0,
                    Left=11.0,
                    Top=96.0,
                    Width=590.0,
                ),
                GroupItem(
                    RectangleItem(
                        name='RectangleItem',
                        BackgroundColor='#FF2A2F35',
                        BorderStyle={
                            "BorderColor": '#00FFFFFF',
                        },
                        Height=1.0,
                        Left=0.0,
                        Width=590.0,
                    ),
                    TextItem(
                        name='TextItem',
                        Font='Arame Mono',
                        FontSize=18.0,
                        Text='75',
                        TextColor='#FF6B717A',
                        BackgroundColor='#FF181B1F',
                        BorderStyle={
                            "RadiusTopLeft": 5,
                            "RadiusTopRight": 5,
                            "RadiusBottomLeft": 5,
                            "RadiusBottomRight": 5,
                        },
                        Height=19.0,
                        Left=559.0,
                        Top=0.0,
                        Width=33.0,
                    ),
                    name='75',
                    Top=60.0,
                ),
                RectangleItem(
                    name='Line 4',
                    BackgroundColor='#FF1F2328',
                    BorderStyle={
                        "BorderColor": '#00FFFFFF',
                    },
                    Height=1.0,
                    Left=11.0,
                    Top=41.0,
                    Width=590.0,
                ),
                GroupItem(
                    RectangleItem(
                        name='RectangleItem',
                        BackgroundColor='#FF2A2F35',
                        BorderStyle={
                            "BorderColor": '#00FFFFFF',
                        },
                        Height=1.0,
                        Left=0.0,
                        Width=590.0,
                    ),
                    TextItem(
                        name='TextItem',
                        Font='Arame Mono',
                        FontSize=18.0,
                        Text='100',
                        TextColor='#FF6B717A',
                        BackgroundColor='#FF181B1F',
                        BorderStyle={
                            "RadiusTopLeft": 5,
                            "RadiusTopRight": 5,
                            "RadiusBottomLeft": 5,
                            "RadiusBottomRight": 5,
                        },
                        # Height/Top iguais aos outros quatro rotulos: com
                        # Top=-8 a caixa saia 4px acima do widget e cruzava a
                        # borda do painel da coluna esquerda.
                        Height=19.0,
                        Left=551.0,
                        Top=0.0,
                        Width=42.0,
                    ),
                    name='100',
                    Top=4.0,
                ),
                name='bg',
                IsFreezed=True,
            ),
            # Volta de referencia (.ibt convertido por tools/ibt_ref.py) e
            # volante. Desenhados antes dos pedais ao vivo, que ficam por
            # cima; referencia em linha mais fina (3 contra 5) e translucida,
            # sem descer de 3 para nao sumir com o dash reduzido. Volante com
            # zero na linha de 50 (direita para cima), +-180 graus na altura.
            ChartItem(
                name='steer_ref',
                # Volante da referencia.
                LineColor=STEER_REF,
                LineTickness=3,
                PointsCount=240.0,
                RenderingSkip=1,
                bindings={
                    "CurrentValue": js('return refSteer();', jsext=3),
                    "Visible": js('return refAvailable();', jsext=3),
                },
            ),
            ChartItem(
                name='steer_live',
                # Volante ao vivo.
                LineColor=STEER_LIVE,
                LineTickness=4,
                PointsCount=240.0,
                RenderingSkip=1,
                bindings={
                    "CurrentValue": js('return liveSteer();', jsext=3),
                    "Visible": js('return liveSteerAvailable();', jsext=3),
                },
            ),
            ChartItem(
                name='brake_ref',
                # Freio da referencia.
                LineColor=BRAKE_REF,
                LineTickness=3,
                PointsCount=240.0,
                RenderingSkip=1,
                bindings={
                    "CurrentValue": js('return refBrake();', jsext=3),
                    "Visible": js('return refAvailable();', jsext=3),
                },
            ),
            ChartItem(
                name='throttle_ref',
                # Acelerador da referencia.
                LineColor=THROTTLE_REF,
                LineTickness=3,
                PointsCount=240.0,
                RenderingSkip=1,
                bindings={
                    "CurrentValue": js('return refThrottle();', jsext=3),
                    "Visible": js('return refAvailable();', jsext=3),
                },
            ),
            ChartItem(
                name='brake',
                # Janela curta (~8 s a 30 amostras/s): com 600 pontos o
                # grafico cobria ~20 s e as curvas viravam degraus.
                PointsCount=240.0,
                RenderingSkip=1,
                bindings={
                    "CurrentValue": ncalc('[Brake]'),
                },
            ),
            ChartItem(
                name='[Throttle]',
                LineColor='#FF1DAF4D',
                # Janela curta (~8 s a 30 amostras/s): com 600 pontos o
                # grafico cobria ~20 s e as curvas viravam degraus.
                PointsCount=240.0,
                RenderingSkip=1,
                bindings={
                    "CurrentValue": ncalc('[Throttle]'),
                },
            ),
            # Rotulos da referencia e do volante, no estilo das gridlines.
            # Larguras fixas por texto; o estado sem dado mostra "N/A".
            TextItem(
                name='Ref-label',
                Font='Arame Mono',
                FontSize=18.0,
                Text='REF N/A',
                TextColor=TEXT_SECONDARY,
                BackgroundColor='#FF181B1F',
                BorderStyle={
                    "RadiusTopLeft": 5,
                    "RadiusTopRight": 5,
                    "RadiusBottomLeft": 5,
                    "RadiusBottomRight": 5,
                },
                Height=19.0,
                Left=15.0,
                Top=4.0,
                Width=140.0,
                bindings={
                    "Text": js('return refLabel();', jsext=3),
                },
            ),
            TextItem(
                name='Steer-label',
                Font='Arame Mono',
                FontSize=18.0,
                Text='STR',
                TextColor=STEER_LIVE,
                BackgroundColor='#FF181B1F',
                BorderStyle={
                    "RadiusTopLeft": 5,
                    "RadiusTopRight": 5,
                    "RadiusBottomLeft": 5,
                    "RadiusBottomRight": 5,
                },
                Height=19.0,
                Left=511.0,
                Top=115.5,
                Width=44.0,
                bindings={
                    "Visible": js('return liveSteerAvailable();', jsext=3),
                },
            ),
            TextItem(
                name='Steer-label N/A',
                Font='Arame Mono',
                FontSize=18.0,
                Text='STR N/A',
                TextColor=TEXT_SECONDARY,
                BackgroundColor='#FF181B1F',
                BorderStyle={
                    "RadiusTopLeft": 5,
                    "RadiusTopRight": 5,
                    "RadiusBottomLeft": 5,
                    "RadiusBottomRight": 5,
                },
                Height=19.0,
                Left=471.0,
                Top=115.5,
                Width=84.0,
                bindings={
                    "Visible": js('return !liveSteerAvailable();', jsext=3),
                },
            ),
            TextItem(
                name='Badge-throttle',
                Font='Arame Mono',
                FontSize=19.0,
                Text='0',
                TextColor='#FF000000',
                BackgroundColor='#FF25BD11',
                BorderStyle={
                    "RadiusTopLeft": 5,
                    "RadiusTopRight": 5,
                    "RadiusBottomLeft": 5,
                    "RadiusBottomRight": 5,
                },
                # 227 (repouso, vindo da formula de Top) + 25 passava dos
                # 250 de altura do widget: o badge sobrava para fora embaixo.
                Height=23.0,
                Left=560.0,
                Top=227.0,
                Width=44.0,
                RenderingSkip=1,
                MinimumRefreshIntervalMS=10.0,
                bindings={
                    "Text": formatted('[Throttle]', '00'),
                    "Top": ncalc('227-(2.23*[Throttle])'),
                },
            ),
            TextItem(
                name='Badge-brake',
                Font='Arame Mono',
                FontSize=19.0,
                Text='0',
                TextColor='#FFFFFFFF',
                BackgroundColor='#FFE73636',
                BorderStyle={
                    "RadiusTopLeft": 5,
                    "RadiusTopRight": 5,
                    "RadiusBottomLeft": 5,
                    "RadiusBottomRight": 5,
                },
                # 227 (repouso, vindo da formula de Top) + 25 passava dos
                # 250 de altura do widget: o badge sobrava para fora embaixo.
                Height=23.0,
                Left=560.0,
                Top=227.0,
                Width=44.0,
                RenderingSkip=1,
                MinimumRefreshIntervalMS=10.0,
                bindings={
                    "Text": formatted('[Brake]', '00'),
                    "Top": ncalc('227-(2.23*[brake])'),
                },
            ),
            name='Telemetry',
        ),
    ]
