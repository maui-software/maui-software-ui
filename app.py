import os
import sys
import threading
import webbrowser

import dash
from dash import Dash, Input, Output, html, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Forçar uso do React 18
dash._dash_renderer._set_react_version("18.2.0")


def resource_path(relative_path: str) -> str:
    """Obtém caminho absoluto para resource, funciona para dev e PyInstaller"""
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Quando executável, incluir utils no sys.path
if getattr(sys, 'frozen', False):
    utils_path = resource_path('utils')
    if os.path.exists(utils_path) and utils_path not in sys.path:
        sys.path.insert(0, utils_path)

# Pastas de assets/pages
if getattr(sys, 'frozen', False):
    assets_folder = resource_path('assets')
    pages_folder = resource_path('pages')
else:
    assets_folder = 'assets'
    pages_folder = 'pages'


app = Dash(
    __name__,
    use_pages=True,
    pages_folder=pages_folder,
    assets_folder=assets_folder,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "MAUI Audio Data Loader - Professional tool for acoustic ecology data analysis"},
        {"http-equiv": "X-UA-Compatible", "content": "IE=edge"},
    ],
)
app.title = "MAUI Audio Data Loader"


app.layout = dmc.MantineProvider(
    theme={"colorScheme": "light"},
    children=[
        dcc.Location(id="url"),
        dcc.Store(id="global-output-df-dir", storage_type="session"),
        dcc.Store(id="global-audio-df", storage_type="session"),
        dcc.Store(id="global-audio-df-seg", storage_type="session"),
        dcc.Store(id="global-audio-df-idx", storage_type="session"),
        dcc.Store(id="quit-modal-open", storage_type="memory"),

        dmc.AppShell(
            navbar={"breakpoint": "sm"},
            children=[
                dmc.AppShellNavbar(
                    p="md",
                    w=300,
                    children=[
                        dmc.Stack(
                            gap="sm",
                            children=[
                                html.Div(
                                    html.Img(
                                        src="/assets/logo.png",
                                        style={
                                            "width": "240px",
                                            "display": "block",
                                            "marginLeft": "auto",
                                            "marginRight": "auto",
                                            "marginBottom": "18px",
                                        },
                                        alt="MAUI Software Logo",
                                    ),
                                    style={
                                        "padding": 20,
                                        "borderBottom": "1px solid #e9ecef",
                                        "marginBottom": 20,
                                    },
                                ),
                                dmc.Stack(
                                    gap="sm",
                                    children=[
                                        dmc.NavLink(
                                            label="Welcome",
                                            leftSection=DashIconify(icon="material-symbols:home-outline-rounded", width=25),
                                            href="/",
                                            id="nav-welcome",
                                            style={"width": "100%"},
                                        ),
                                        dmc.NavLink(
                                            label="Load Audio Data",
                                            leftSection=DashIconify(icon="meteor-icons:upload", width=25),
                                            href="/load-data",
                                            id="nav-load-data",
                                            style={"width": "100%"},
                                        ),
                                        dmc.Tooltip(
                                            id={"type": "tooltip", "index": "segment"},
                                            label="Disabled: load audio data to access",
                                            disabled=True,
                                            position="right",
                                            withArrow=True,
                                            boxWrapperProps={"style": {"width": "100%"}},
                                            children=dmc.NavLink(
                                                label="Audio Segmentation",
                                                leftSection=DashIconify(icon="fluent:cut-16-filled", width=25),
                                                href="/audio-segmentation",
                                                id="nav-audio-segmentation",
                                                disabled=False,
                                                style={"width": "100%"},
                                            ),
                                        ),
                                        dmc.Tooltip(
                                            id={"type": "tooltip", "index": "acoustic"},
                                            label="Disabled: load audio data to access",
                                            disabled=True,
                                            position="right",
                                            withArrow=True,
                                            boxWrapperProps={"style": {"width": "100%"}},
                                            children=dmc.NavLink(
                                                label="Acoustic Indices",
                                                leftSection=DashIconify(icon="fluent:math-formula-20-filled", width=25),
                                                href="/acoustic-indices",
                                                id="nav-acoustic-indices",
                                                disabled=False,
                                                style={"width": "100%"},
                                            ),
                                        ),
                                        dmc.Tooltip(
                                            id={"type": "tooltip", "index": "eda"},
                                            label="Disabled: load audio data to access",
                                            disabled=True,
                                            position="right",
                                            withArrow=True,
                                            boxWrapperProps={"style": {"width": "100%"}},
                                            children=dmc.NavLink(
                                                label="Exploratory Data Analysis",
                                                leftSection=DashIconify(icon="bitcoin-icons:graph-filled", width=25),
                                                href="/eda",
                                                id="nav-eda",
                                                disabled=False,
                                                style={"width": "100%"},
                                            ),
                                        ),
                                        dmc.Tooltip(
                                            id={"type": "tooltip", "index": "spectrograms"},
                                            label="Disabled: load audio data to access",
                                            disabled=True,
                                            position="right",
                                            withArrow=True,
                                            boxWrapperProps={"style": {"width": "100%"}},
                                            children=dmc.NavLink(
                                                label="Spectrograms",
                                                leftSection=DashIconify(icon="bi:soundwave", width=25),
                                                href="/spectrograms",
                                                id="nav-spectrograms",
                                                disabled=False,
                                                style={"width": "100%"},
                                            ),
                                        ),
                                        dmc.Tooltip(
                                            id={"type": "tooltip", "index": "summary"},
                                            label="Disabled: load audio data and calculate acoustic indices to access",
                                            disabled=True,
                                            position="right",
                                            withArrow=True,
                                            boxWrapperProps={"style": {"width": "100%"}},
                                            children=dmc.NavLink(
                                                label="Summary Visualizations",
                                                leftSection=DashIconify(icon="fluent:data-pie-24-filled", width=25),
                                                href="/summary-visualizations",
                                                id="nav-summary-visualizations",
                                                disabled=False,
                                                style={"width": "100%"},
                                            ),
                                        ),

                                        html.Hr(style={"marginTop": "12px", "marginBottom": "12px"}),
                                        dmc.Button(
                                            "Quit App",
                                            id="quit-app-btn",
                                            color="red",
                                            variant="filled",
                                            fullWidth=True,
                                            leftSection=DashIconify(icon="mdi:power", width=22),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                ),

                dmc.AppShellMain(
                    p="md",
                    children=[
                        dash.page_container,

                        # Overlay com blur (controlado via callback)
                        html.Div(
                            id="quit-blur-overlay",
                            style={
                                "position": "fixed",
                                "inset": 0,
                                "backdropFilter": "blur(6px)",
                                "backgroundColor": "rgba(0,0,0,0.25)",
                                "zIndex": 9998,
                                "display": "none",
                            },
                        ),

                        # Modal de encerramento (sem botão OK, texto centralizado)
                        dmc.Modal(
                            id="quit-modal",
                            opened=False,
                            withCloseButton=False,
                            centered=True,
                            overlayProps={"opacity": 0},  # overlay próprio acima
                            zIndex=9999,
                            styles={"body": {"padding": "28px"}},
                            children=dmc.Text(
                                "Maui is not executing. You may close this tab now",
                                size="lg",
                                fw=600,
                                ta="center",  # text-align center
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# Destaque do link ativo
@app.callback(
    Output("nav-welcome", "active"),
    Output("nav-load-data", "active"),
    Output("nav-eda", "active"),
    Output("nav-acoustic-indices", "active"),
    Output("nav-audio-segmentation", "active"),
    Output("nav-summary-visualizations", "active"),
    Output("nav-spectrograms", "active"),
    Input("url", "pathname"),
)
def highlight_active_nav(pathname):
    return [
        pathname == "/",
        pathname == "/load-data",
        pathname == "/eda",
        pathname == "/acoustic-indices",
        pathname == "/audio-segmentation",
        pathname == "/summary-visualizations",
        pathname == "/spectrograms",
    ]


# Habilitar/desabilitar links e tooltips
@app.callback(
    Output("nav-eda", "disabled"),
    Output("nav-acoustic-indices", "disabled"),
    Output("nav-summary-visualizations", "disabled"),
    Output("nav-audio-segmentation", "disabled"),
    Output("nav-spectrograms", "disabled"),
    Output({"type": "tooltip", "index": "eda"}, "disabled"),
    Output({"type": "tooltip", "index": "acoustic"}, "disabled"),
    Output({"type": "tooltip", "index": "summary"}, "disabled"),
    Output({"type": "tooltip", "index": "segment"}, "disabled"),
    Output({"type": "tooltip", "index": "spectrograms"}, "disabled"),
    Input("global-audio-df", "data"),
    Input("global-audio-df-idx", "data"),
)
def disable_links_and_tooltips(global_audio_df, global_audio_df_idx):
    disable_eda = not bool(global_audio_df)
    disable_acoustic = not bool(global_audio_df)
    disable_segment = not bool(global_audio_df)
    disable_spectrograms = not bool(global_audio_df)
    disable_summary = (not bool(global_audio_df)) or (not bool(global_audio_df_idx))

    return (
        disable_eda,
        disable_acoustic,
        disable_summary,
        disable_spectrograms,
        disable_spectrograms,
        not disable_eda,
        not disable_acoustic,
        not disable_summary,
        not disable_segment,
        not disable_spectrograms,
    )


# Botão Quit App — abre modal (com blur) e encerra o servidor logo depois
@app.callback(
    Output("quit-modal-open", "data", allow_duplicate=True),
    Input("quit-app-btn", "n_clicks"),
    prevent_initial_call=True,
)
def quit_app(n_clicks):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate

    # agenda o encerramento do servidor/processo após pequeno atraso
    def _shutdown():
        try:
            from flask import request
            func = request.environ.get("werkzeug.server.shutdown")
            if func:
                func()
                return
        except Exception:
            pass
        os._exit(0)

    # 0.5s para dar tempo do modal/overlay renderizar
    threading.Timer(0.5, _shutdown).start()

    # abrir o modal
    return {"opened": True}


# Controla o modal e o overlay de blur
@app.callback(
    Output("quit-modal", "opened", allow_duplicate=True),
    Output("quit-blur-overlay", "style", allow_duplicate=True),
    Input("quit-modal-open", "data"),
    prevent_initial_call=True,
)
def control_quit_modal(data):
    opened = bool(data and data.get("opened"))
    overlay_style = {
        "position": "fixed",
        "inset": 0,
        "backdropFilter": "blur(6px)",
        "backgroundColor": "rgba(0,0,0,0.25)",
        "zIndex": 9998,
        "display": "block" if opened else "none",
    }
    return opened, overlay_style


def open_browser():
    webbrowser.open_new('http://localhost:8050/')


def main():
    """Execução em modo empacotado"""
    try:
        from waitress import serve

        if getattr(sys, 'frozen', False):
            threading.Timer(2.0, open_browser).start()
            print("MAUI Audio Data Loader iniciando...")
            print("Abrindo no navegador: http://localhost:8050/")

        serve(app.server, host='127.0.0.1', port=8050, threads=4)
    except ImportError:
        print("Waitress não encontrado, usando servidor de desenvolvimento")
        app.run_server(host='127.0.0.1', port=8050, debug=False)


if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        main()
    else:
        app.run(debug=True, port=8050)
