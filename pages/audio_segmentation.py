# pages/audio_segmentation.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc
import pandas as pd
import json
import os

from utils import definitions
from utils import random_utils


from maui import utils as maui_utils

dash.register_page(__name__, path="/audio-segmentation", name="Audio Segmentation")



layout = dmc.Container([
    dmc.Title("Audio Segmentation", order=1, mb=30),

    dmc.Paper([
        dmc.Stack([

            dmc.Group([
                dmc.Select(
                    id="file-path-column-seg",
                    label="File Path Column",
                    placeholder="Select them file_path column...",
                    searchable=True,
                    nothingFoundMessage="Sem colunas para selecionar",
                    mb="md",
                    value=None,
                    required=True,
                    clearable=True,
                ),

                dmc.Select(
                    id="datetime-column-seg",
                    label="Datetime Column",
                    placeholder="Select the datetime columns...",
                    searchable=True,
                    nothingFoundMessage="Sem colunas para selecionar",
                    mb="md",
                    value=None,
                    required=True,
                    clearable=True,
                ),

                dmc.Select(
                    id="unit-select-seg",
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
                    "Segment Audios",
                    id="segmentation-run-btn",
                    variant="filled",
                    leftSection=html.I(className="fas fa-play"),
                    size="md"
                )
            ], gap="md")
        ], gap="md"),
    ], p="md", withBorder=False, radius="md", mb="xl", shadow="md"),

    # Área de resultados ENVOLVIDA em dcc.Loading!
    dcc.Loading(
        id="loading-idx-seg", type="dot",
        overlay_style={"visibility": "visible", "filter": "blur(10px)"},
        children=html.Div(id="results-container-idx-seg")
    ),

], size="lg")


# Preenche as opções da Select para coluna de file path, lendo do DataFrame armazenado
@callback(
    Output("file-path-column-seg", "data"),
    Output("file-path-column-seg", "value"),
    Output("datetime-column-seg", "data"),
    Output("datetime-column-seg", "value"),
    Input("global-audio-df", "data"),
    prevent_initial_call=False
)
def populate_column_choices(df_json):
    if not df_json:
        return [], None

    # Se for string JSON, converta para dict
    if isinstance(df_json, str):
        try:
            df_json = json.loads(df_json)
            df = pd.read_parquet(df_json['data_path'])
        except Exception as e:
            return [], None

    if not isinstance(df_json, dict):
        return [], None

    cols = list(df.columns)
    print(cols)

    options = [{"label": col, "value": col} for col in cols]
    default_value_file_path = "file_path" if "file_path" in cols else (cols[0] if cols else None)
    default_value_timestamp = "timestamp_init" if "timestamp_init" in cols else (cols[0] if cols else None)

    return options, default_value_file_path, options, default_value_timestamp


@callback(
    Output("results-container-idx-seg", "children"),
    Output("segmentation-run-btn", "n_clicks"),
    Output("global-audio-df-seg", "data"),

    Input("segmentation-run-btn", "n_clicks"),

    State("global-audio-df", "data"),
    State("global-audio-df-seg", "data"),
    State("file-path-column-seg", "value"),
    State("datetime-column-seg", "value"),
    State("unit-select-seg", "value"),
    State("global-output-df-dir", "data"),

    prevent_initial_call=False
)
def calculate_and_show(n_clicks, df_json_original, df_json, file_path_col, datetime_col,
                      unit, output_dir_json):

    if df_json_original is None:
        if not n_clicks:
            return dmc.Alert("Load the dataset before calculating acoustic indices.", color="yellow", title="Validation Error"), False, None
        else:
            return dmc.Alert("You need to load the dataset before calculating acoustic indices!", color="red", title="Validation Error"), False, None

    if not n_clicks:
        if df_json is not None:
            df_json_parse = json.loads(df_json)
            df = pd.read_parquet(df_json_parse['data_path'])
            return dmc.Stack([
                dmc.Alert(
                    "Loading already segmented dataset!",
                    title="Alert",
                    color="yellow"
                ),
                dmc.ScrollArea([
                    dmc.Table([
                        dmc.TableThead([
                            dmc.TableTr(
                                [dmc.TableTh(col) for col in df.columns]
                            )
                        ]),
                        dmc.TableTbody([
                            dmc.TableTr([
                                dmc.TableTd(
                                    (val if len(val) <= 30 else val[:27] + '...')
                                    if isinstance(val := str(df.iloc[i, j]), str) else val,
                                    style={
                                        "maxHeight": "40px",
                                        "overflow": "hidden",
                                        "textOverflow": "ellipsis",
                                        "whiteSpace": "nowrap"
                                    }
                                ) for j in range(len(df.columns))
                            ]) for i in range(min(200, len(df)))
                        ]),
                    ],
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True),
                ], h=400),
            ]), False, None
        return dash.no_update, False, None

    df_json_original_parse = json.loads(df_json_original)
    df = pd.read_parquet(df_json_original_parse['data_path'])

    if df_json is not None:
        df_json_parse = json.loads(df_json)
        df_json_seg = pd.read_parquet(df_json_parse['data_path'])
    else:
        df_json_seg = None

    if n_clicks:

        min_duration = random_utils.unit_conversion(unit)

        output_dir_json_parse = json.loads(output_dir_json)
        output_dir = output_dir_json_parse["output_dir"]

        output_dir_segments = os.path.join(output_dir, "audio_segments")
        print(output_dir)
        print(output_dir_segments)
        print(df.dtypes)


        df_json_seg = maui_utils.segment_audio_files(
            df=df,
            min_duration=min_duration,
            output_dir=output_dir_segments,
            file_path_col=file_path_col,
            datetime_col=datetime_col
        )
        df_json_seg['duration'] = (df_json_seg['end_time'] - df_json_seg['start_time']).dt.total_seconds()

        output_path = os.path.join(output_dir, "segmented_dataset.parquet")

        df_json_seg.to_parquet(output_path)


    if df_json_seg is not None:
        return_dict = {"indices_data_loaded": True, "data_path": output_path}
    else:
        None

    return dmc.Stack([
        dmc.Alert(
            "Successfully segmented audio files!",
            title="Success",
            color="green"
        ),
        dmc.ScrollArea([
            dmc.Table([
                dmc.TableThead([
                    dmc.TableTr(
                        [dmc.TableTh(col) for col in df_json_seg.columns]
                    )
                ]),
                dmc.TableTbody([
                    dmc.TableTr([
                        dmc.TableTd(
                            (val if len(val) <= 30 else val[:27] + '...')
                            if isinstance(val := str(df_json_seg.iloc[i, j]), str) else val,
                            style={
                                "maxHeight": "40px",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                                "whiteSpace": "nowrap"
                            }
                        ) for j in range(len(df_json_seg.columns))
                    ]) for i in range(min(200, len(df_json_seg)))
                ]),
            ],
            striped=True,
            highlightOnHover=True,
            withTableBorder=True),
        ], h=400),
    ]), False, json.dumps(return_dict)