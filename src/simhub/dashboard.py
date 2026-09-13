"""Envelope de um dashboard: os campos fora da arvore de controles."""


def shell(dashboard_id, width, height, images=None, metadata=None,
          hide_labels=True, debug_manager=None):
    """Campos de topo do .djson.

    `debug_manager` guarda a posicao da janela de preview do editor -- estado de
    autoria, sem efeito em corrida, mantido so por fidelidade ao original.
    """
    return {
        "DashboardDebugManager": debug_manager if debug_manager is not None else {},
        "Version": 2,
        "Id": dashboard_id,
        "BaseHeight": height,
        "BaseWidth": width,
        "BackgroundColor": "#FF000000",
        "SnapToGrid": False,
        "HideLabels": hide_labels,
        "ShowForeground": True,
        "ForegroundOpacity": 100.0,
        "ShowBackground": True,
        "BackgroundOpacity": 100.0,
        "ShowBoundingRectangles": False,
        "GridSize": 10,
        "Images": images if images is not None else [],
        "Metadata": metadata if metadata is not None else {},
        "ShowOnScreenControls": True,
        "IsOverlay": False,
        "EnableClickThroughOverlay": True,
        "EnableOnDashboardMessaging": True,
        "UseStrictJSIsolation": False,
        "UseStrictJSIsolationWarning": True,
    }


def metadata(width, height, idle_screens=(0,), overlay_size_warning=False,
             simhub_version="9.10.6", **extra):
    """Bloco Metadata embutido no .djson (distinto do arquivo .djson.metadata)."""
    data = {
        "ScreenCount": 1.0,
        "InGameScreensIndexs": [0],
        "IdleScreensIndexs": list(idle_screens),
        "MainPreviewIndex": 0,
        "IsOverlay": False,
        "OverlaySizeWarning": overlay_size_warning,
        "MetadataVersion": 2.0,
        "EnableOnDashboardMessaging": True,
        "PitScreensIndexs": [],
        "SimHubVersion": simhub_version,
        "Width": float(width),
        "Height": float(height),
        "DashboardVersion": "",
    }
    data.update(extra)
    return data


def screen(screen_id, background="#FF000000", idle=True,
           enabled_expression="", name="Screen"):
    """Campos da tela fora da lista de itens."""
    return {
        "RenderingSkip": 0,
        "Name": name,
        "InGameScreen": True,
        "IdleScreen": idle,
        "PitScreen": False,
        "ScreenId": screen_id,
        "AllowOverlays": True,
        "IsForegroundLayer": False,
        "IsOverlayLayer": False,
        "OverlayTriggerExpression": {"Expression": ""},
        "ScreenEnabledExpression": {"Expression": enabled_expression},
        "OverlayMaxDuration": 0,
        "OverlayMinDuration": 0,
        "IsBackgroundLayer": False,
        "BackgroundColor": background,
        "MinimumRefreshIntervalMS": 0.0,
    }
