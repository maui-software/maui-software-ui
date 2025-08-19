# pages/acoustic_indices.py
import dash
from dash import html, dcc, callback, Input, Output, State, ctx
import dash_mantine_components as dmc
import pandas as pd
import numpy as np
import re
import json

import plotly.graph_objects as go

from acoustic_indices.acoustic_indices_calculation import AcousticIndices
from utils import definitions
from utils import random_utils
from utils import io_utils


from maui import acoustic_indices as maui_acoustic_indices
from maui import visualizations
from maui import utils as maui_utils



dash.register_page(__name__, path="/spectrograms", name="Spectrograms")

# Instantiate AcousticIndices
AIdx = AcousticIndices()
AVAILABLE_INDICES = AIdx.available_indices

layout = dmc.Container([
    dmc.Title("Spectrograms Visualizations", order=1, mb=30),

    dmc.Paper([
        dmc.Stack([
            dmc.Text("Spectrograms", fw=600),
            dcc.Loading(
                id="loading-audio-list-spectrogram", type="dot",
                overlay_style={"visibility": "visible", "filter": "blur(10px)"},
                children=html.Div(id="spectrogram-selection-container"),
            ),
            dmc.Select(
                id="file-path-column-spectrograms",
                label="File Path Column",
                placeholder="Selecione a coluna que contém o file path...",
                searchable=True,
                nothingFoundMessage="Sem colunas para selecionar",
                mb="md",
                value=None,
                required=True,
                clearable=True,
            ),

            # Accordion para configurações adicionais
            dmc.Accordion(
                multiple=True,
                value=[],
                chevronPosition="left",
                variant="separated",
                children=[
                    dmc.AccordionItem([
                        dmc.AccordionControl("Spectrogram Configurations"),
                        dmc.AccordionPanel([
                            dmc.Stack([

                                dmc.Group([
                                    dmc.Select(
                                        label="Mode",
                                        id="spectrogram-mode",
                                        data=[{"value": m, "label": m} for m in ["psd", "mean", "complex"]],
                                        value="psd"
                                    ),
                                    dmc.Select(
                                        label="Window",
                                        id="spectrogram-window",
                                        data=[{"value": m, "label": m} for m in ["hann"]],
                                        value="hann"
                                    ),
                                    dmc.NumberInput(label="nperseg", id="spectrogram-nperseg", value=1024, min=128, step=1),
                                    dmc.NumberInput(label="noverlap", id="spectrogram-noverlap", value="", min=0, step=1),
                                    
                                ], gap="md"),

                                #dmc.Group([
                                #    dmc.NumberInput(label="Altura (pixels)", id="spectrogram-height", value=500, min=100, max=2000),
                                #    dmc.NumberInput(label="Largura (pixels)", id="spectrogram-width", value=1200, min=100, max=4000),
                                #], gap="md"),
                                
                    
                                
                            ])
                        ]),
                    ], value="processing-settings")
                ]
            ),
            html.Div(id="spectrogram-error-alert"),

            dcc.Loading(
                id="loading-idx", type="dot",
                overlay_style={"visibility": "visible", "filter": "blur(10px)"},
                children=dcc.Graph(
                    id="results-container-spectrogram",
                    style={"width": "100%", "height": "500px", "maxWidth": "100%", "objectFit": "contain"},
                    #style={'height': '600px'},
                    #config={'displayModeBar': True, 'toImageButtonOptions': {'height': 600, 'width': 1200}}
                )
            ),
            
            
        ], gap="md"),
    ], p="md", withBorder=False, radius="md", mb="xl", shadow="md", style={"overflow": "auto", "maxWidth": "100%"},),

    dmc.Paper([
        dmc.Stack([
            dmc.Text("False Color Spectrograms", fw=600),

            dmc.Group([
                dmc.Select(
                    id="r-channel-idx-fcs",
                    label="Index mapped to the R channel",
                    placeholder="Select index...",
                    searchable=True,
                    nothingFoundMessage="Sem colunas para selecionar",
                    mb="md",
                    value=None,
                    required=True,
                    clearable=True,
                ),
                dmc.Select(
                    id="g-channel-idx-fcs",
                    label="Index mapped to the G channel",
                    placeholder="Select index...",
                    searchable=True,
                    nothingFoundMessage="Sem colunas para selecionar",
                    mb="md",
                    value=None,
                    required=True,
                    clearable=True,
                ),
                dmc.Select(
                    id="b-channel-idx-fcs",
                    label="Index mapped to the B channel",
                    placeholder="Select index...",
                    searchable=True,
                    nothingFoundMessage="Sem colunas para selecionar",
                    mb="md",
                    value=None,
                    required=True,
                    clearable=True,
                ),

            ], gap="md"),

            dmc.Group([
                dmc.Select(
                    id="datetime-column-fcs",
                    label="Datetime Column",
                    placeholder="Select column...",
                    searchable=True,
                    nothingFoundMessage="Sem colunas para selecionar",
                    mb="md",
                    value=None,
                    required=True,
                    clearable=True,
                ),
                dmc.Select(
                    id="unit-select-fcs",
                    label="Time Unit",
                    data=definitions.AVAILABLE_UNITS,
                    placeholder="Select the time unit...",
                    required=True,
                    clearable=True,
                    searchable=True,
                    mb="md",
                ),

            ], gap="md"),

            dmc.Group([
                dmc.Button(
                    "Generate False Color Spectrograms",
                    id="fcs-run-btn",
                    variant="filled",
                    leftSection=html.I(className="fas fa-play"),
                    size="md"
                )
            ], gap="md"),
            
            html.Div(id="fcs-error-alert"),

            dcc.Loading(
                id="loading-idx", type="dot",
                overlay_style={"visibility": "visible", "filter": "blur(10px)"},
                children=dcc.Graph(
                    id="results-container-fcs",
                    style={"width": "100%", "height": "500px", "maxWidth": "100%", "objectFit": "contain"},
                    #style={'height': '600px'},
                    #config={'displayModeBar': True, 'toImageButtonOptions': {'height': 600, 'width': 1200}}
                )
            ),
            
            
        ], gap="md"),
    ], p="md", withBorder=False, radius="md", mb="xl", shadow="md", style={"overflow": "auto", "maxWidth": "100%"},),

    
    

], size="lg")

@callback(
    Output("file-path-column-spectrograms", "data"),
    Output("file-path-column-spectrograms", "value"),
    Output("datetime-column-fcs", "data"),
    Output("datetime-column-fcs", "value"),
    Output("r-channel-idx-fcs", "data"),
    Output("g-channel-idx-fcs", "data"),
    Output("b-channel-idx-fcs", "data"),
    Input("global-audio-df", "data"),
    Input("global-audio-df-seg", "data"),
    Input("global-audio-df-idx", "data"),
    prevent_initial_call=False
)
def populate_column_choices_fcs(df_json_original, df_json_seg, df_json_idx):
    df_json = df_json_original

    if df_json_seg is not None:
        df_json = df_json_seg

    if not df_json:
        return [], None

    df_json_parse = json.loads(df_json)
    df_json = pd.read_csv(df_json_parse['data_path'])
    #df_json = io_utils.load_df_complex_parquet(df_json_parse['data_path'])



    if isinstance(df_json_idx, str):
        try:
            df_json_idx_parse = json.loads(df_json_idx)
            df_json_idx = pd.read_csv(df_json_idx_parse['data_path'])
            #df_json_idx = io_utils.load_df_complex_parquet(df_json_idx_parse['data_path'])
        except Exception as e:
            return [], None



    cols = list(df_json.columns)
    cols_df_idx = df_json_idx.columns
    cols_idx = list(set(cols_df_idx) - set(cols))


    options = [{"label": col, "value": col} for col in cols]
    default_value_file_path = "file_path" if "file_path" in cols else (cols[0] if cols else None)
    default_value_timestamp = "timestamp_init" if "timestamp_init" in cols else (cols[0] if cols else None)

    options_idx = [{"label": col, "value": col} for col in cols_idx]


    return options, default_value_file_path, options, default_value_timestamp, options_idx, options_idx, options_idx


@callback(
    Output("spectrogram-selection-container", "children"),
    Input("global-audio-df", "data"),
    Input("global-audio-df-seg", "data"),
    prevent_initial_call=False,
)
def _show_input_data_table(df_json_original, df_json_seg):
    df_json = df_json_original
    if df_json_seg is not None:
        df_json = df_json_seg

    if df_json is None:
        return dash.no_update

    df_json_parse = json.loads(df_json)
    df = pd.read_csv(df_json_parse['data_path'])
    #df = io_utils.load_df_complex_parquet(df_json_parse['data_path'])

    return dmc.Stack([

        dmc.ScrollArea([
            dmc.Table([
                dmc.TableThead([
                    dmc.TableTr([dmc.TableTh("action")] + [dmc.TableTh(col) for col in df.columns])
                ]),
                dmc.TableTbody([
                    dmc.TableTr(
                        [dmc.TableTd(dmc.Button("Visualize Spectrogram", size="xs", variant="light", id={"type": "generate-spectrogram-btn", "index": i}))] +
                        [dmc.TableTd(str(df.iloc[i, j])) for j in range(len(df.columns))]
                        
                    ) for i in range(len(df))
                ]),
            ], striped=True, highlightOnHover=True, withTableBorder=True)
        ], h=400),
    ])


@callback(
    Output("results-container-spectrogram", "figure"),
    Output("spectrogram-error-alert", "children"),
    Input({"type": "generate-spectrogram-btn", "index": dash.ALL}, "n_clicks"),
    
    State("file-path-column-spectrograms", "value"),
    State("global-audio-df", "data"),
    Input("global-audio-df-seg", "data"),
    State("spectrogram-mode", "value"),
    State("spectrogram-window", "value"),
    State("spectrogram-nperseg", "value"),
    State("spectrogram-noverlap", "value"),
    prevent_initial_call=True
)
def _show_spectrogram(n_clicks_list, file_path_col, df_json_original, df_json_seg, mode, window, nperseg, noverlap):

    df_json = df_json_original
    if df_json_seg is not None:
        df_json = df_json_seg

    if not any(n_clicks_list):
        return dash.no_update, dash.no_update

    trigger = ctx.triggered_id
    idx = trigger["index"]

    df_json_parse = json.loads(df_json)
    df = pd.read_csv(df_json_parse['data_path'])
    #df = io_utils.load_df_complex_parquet(df_json_parse['data_path'])
    file_path = df.iloc[idx][file_path_col]

    noverlap = None if noverlap == "" else int(noverlap)

    try:
        fig = visualizations.spectrogram_plot(
            file_path=file_path,
            mode=mode,
            window=window,
            nperseg=nperseg,
            noverlap=noverlap,
            show_plot=False
        )
        fig.update_layout(
            autosize=True,
            width=None
        )
        return fig, ""
    except Exception as e:
        return dash.no_update, dmc.Alert(
            f"Error processing data: {str(e)}",
            color="red",
            title="Error"
        )



def _generate_fcs_fig(
    df: pd.DataFrame,
    fc_spectrogram: np.array,
    indices: list,
    fig_size: dict,
    tick_interval: int,
):
    """
    Display a false color spectrogram using Plotly.

    This function visualizes a false color spectrogram generated from
    acoustic indices. The spectrogram is displayed using Plotly with
    customized hover text and axis formatting.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the timestamps for the spectrogram.

    fc_spectrogram : np.array
        A 3D numpy array representing the false color spectrogram,
        where the third dimension corresponds to the color channels (R, G, B).

    fig_size : dict
        Dictionary specifying the figure size with 'width' and 'height' keys.
        If None, default values {'width': 2000, 'height': 1000} are used.

    tick_interval : int
        Interval for selecting ticks on the x-axis. If None, the default value is 40.

    Raises
    ------
    AttributeError
        If `fig_size` does not contain both 'width' and 'height' keys.

    Notes
    -----
    - The spectrogram is displayed with customized hover text showing the timestamp
      for each pixel.
    - The function uses Plotly's `go.Figure` and `go.Image` for rendering the image.
    - The layout is updated to ensure the spectrogram is displayed correctly
      with proper scaling and formatting.
    """

    fig_size = {"width": 2000, "height": 1000} if fig_size is None else fig_size
    tick_interval = 40 if tick_interval is None else tick_interval
    if "height" not in fig_size.keys() or "width" not in fig_size.keys():
        raise AttributeError("fig_size must contain width and height keys.")

    # 3.1 Create the figure
    fig = go.Figure()

    # 3.2. Add the image trace with hover text
    hover_text = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()

    # Create hover text for each pixel in the image
    customdata = np.array([hover_text] * fc_spectrogram.shape[0])

    fig.add_trace(
        go.Image(
            z=fc_spectrogram,
            customdata=customdata,
            hovertemplate="Timestamp: %{customdata}<extra></extra>",
        )
    )

    width = None
    height = None
    if fig_size is not None:
        width = fig_size["width"]
        height = fig_size["height"]

    # Create the x-axis values based on the timestamp
    x_axis_values = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S").tolist()

    # Select a subset of x ticks based on the tick_interval
    tick_indices = list(range(0, len(x_axis_values), tick_interval))
    tick_values = [x_axis_values[i] for i in tick_indices]

    # 3.3. Update layout for better visualization
    fig.update_layout(
        title=f"""{re.sub(r'_per_bin', '', indices[0])} (R), """
        f"""{re.sub(r'_per_bin', '', indices[1])} (G) and {indices[2]} """
        f"""(B) False Color Spectrogram""",
        xaxis={
            "showgrid": False,
            "zeroline": False,
            "tickvals": tick_indices,
            "ticktext": tick_values,
            "tickangle": 90,
        },
        yaxis={
            "showgrid": False,
            "zeroline": False,
            "scaleanchor": "x",
            "autorange": True,
            "range": [0, fc_spectrogram.shape[0]],
        },
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
        width=width,
        height=height,
    )

    return fig

@callback(
    Output("results-container-fcs", "figure"),
    Output("fcs-error-alert", "children"),
    Input("fcs-run-btn", "n_clicks"),

    State("global-audio-df-idx", "data"),
    State("r-channel-idx-fcs", "value"),
    State("g-channel-idx-fcs", "value"),
    State("b-channel-idx-fcs", "value"),
    State("datetime-column-fcs", "value"),
    State("unit-select-fcs", "value"),
    prevent_initial_call=True
)
def _show_fc_spectrogram(n_clicks, df_json, r_index, g_index, b_index, datetime_col, unit):
    if not n_clicks:
        return dash.no_update, dash.no_update

    df_json_parse = json.loads(df_json)
    df = pd.read_csv(df_json_parse['data_path'])
    #df = io_utils.load_df_complex_parquet(df_json_parse['data_path'])



    max_val = df[datetime_col].max().value
    if max_val > 1e12:
        # Provavelmente está em microssegundos ou nanosegundos, ajustar conforme necessário
        timestamp_unit = 'us'  # ou 'ns'
    elif max_val > 1e10:
        # Provavelmente está em milissegundos
        timestamp_unit = 'ms'
    else:
        # Provavelmente em segundos
        timestamp_unit = 's'

    df[datetime_col] = pd.to_datetime(df[datetime_col], unit=timestamp_unit)

    print(datetime_col, r_index, g_index, b_index, unit)

    print(df[datetime_col])
    print(df[r_index])
    print("df.loc[0, r_index]:",  type(df.loc[0, r_index]))
    print("df.loc[0, r_index][0]:",  type(df.loc[0, r_index][0]))
    print(df[g_index])
    print(type(df.loc[0, g_index]))

    print(df[b_index])
    print(type(df.loc[0, b_index]))


    try:
        trunc_unit = "min"
        if unit != "scale_60":
            trunc_unit = "s"
        df["timestamp"] = df[datetime_col].dt.floor(trunc_unit)

        fcs = visualizations.false_color_spectrogram_plot(
            df,
            datetime_col = datetime_col,
            indices = [r_index, g_index, b_index],
            display = False,
            unit = unit
        )

        fig = _generate_fcs_fig(
            df = df,
            fc_spectrogram = fcs,
            indices = [r_index, g_index, b_index],
            fig_size = None,
            tick_interval = None
        )

        fig.update_layout(
            autosize=True,
            width=None
        )
        return fig, ""
    except Exception as e:
        return dash.no_update, dmc.Alert(
            f"Error processing data: {str(e)}",
            color="red",
            title="Error"
        )
