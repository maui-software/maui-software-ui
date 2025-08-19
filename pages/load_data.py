# pages/load_data.py

import dash
from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc
import pandas as pd
import os
import json

from utils import io_utils

dash.register_page(__name__, path="/load-data", name="Load Audio Data")

layout = dmc.Container([
    dmc.Title("Load Audio Data", order=1, mb=30),

    dmc.Paper([
        dmc.Stack([
            dmc.TextInput(
                label="Dataset Directory Path",
                placeholder="/path/to/audio/dataset",
                id="dataset-path-input",
                required=True,
                description="Path to directory containing audio files",
            ),
            dmc.TextInput(
                label="YAML Configuration File",
                placeholder="/path/to/config.yaml",
                id="yaml-config-input",
                required=True,
                description="Path to YAML file for filename formatting",
            ),
            dmc.TextInput(
                label="Format Name",
                placeholder="default_format",
                id="format-name-input",
                required=True,
                description="Name of the configuration pattern to use",
            ),
            dmc.Switch(
                id="store-duration-switch",
                label="Calculate Audio Duration",
                description="Whether to calculate and store audio file durations",
                checked=True,
            ),
            dmc.Stack([
                dmc.Text("Sample Percentage", fw=500),
                dcc.Slider(
                    id="sample-percentage-slider",
                    min=1,
                    max=100,
                    value=100,
                    marks={i: f"{i}%" for i in range(0, 101, 20)},
                    tooltip={"placement": "top", "always_visible": False},
                ),
            ], gap="xs"),
            dmc.TextInput(
                label="Output Directory",
                placeholder="./output_dataframes",
                id="output-df-dir",
                required=True,
                description="Path to the directory that the generate dataframes will be stored",
            ),

            dmc.Button(
                "Load Audio Data",
                id="load-data-button",
                variant="filled",
                size="lg",
                loading=False,
            ),

            dmc.Divider(),

            # Container with new column generation fields, initially hidden
            dmc.Stack([

                dmc.Text("Combine Columns to Create Date Field", fw=600),
                dmc.Group([
                    dmc.MultiSelect(
                        id="combine-columns-select",
                        data=[],  # filled dynamically after load
                        label="Select columns",
                        placeholder="Select columns",
                        style={"width": 220}
                    ),
                    dmc.TextInput(
                        id="combine-separator",
                        value=" ",
                        label="Separator",
                        style={"width": 90}
                    ),
                    dmc.TextInput(
                        id="combine-format",
                        value="%Y-%m-%d %H:%M:%S",
                        label="Datetime format",
                        style={"width": 180}
                    ),
                    dmc.TextInput(
                        id="combine-output-name",
                        value="timestamp",
                        label="New column name",
                        style={"width": 160}
                    ),
                    dmc.Select(
                        id="combine-truncate-select",
                        label="Truncate Date To",
                        data=[
                            {"label": "Hour", "value": "hour"},
                            {"label": "Day", "value": "day"},
                            {"label": "Month", "value": "month"},
                            {"label": "Year", "value": "year"},
                            {"label": "None (full timestamp)", "value": "none"},
                            
                            
                            
                            
                        ],
                        value="none",
                        style={"width": 200},
                    ),
                ], gap="sm", mb="sm"),
                
                dmc.Button(
                    "Create Date Column",
                    id="create-date-column-btn"
                ),
            ], id="combine-date-block", style={"display": "none"}),  # hidden initially

            dmc.Space(h=10),
        ], gap="md"),
    ], p="md", withBorder=False, radius="md", mb=30, shadow="md"),

    html.Div(id="results-container"),
], size="xl", p=40)


def _preview(df: pd.DataFrame, sample_perc: int):
    return dmc.Stack([
        dmc.Alert(f"Successfully loaded {len(df)} audio files!", title="Success", color="green"),
        dmc.SimpleGrid([
            dmc.Paper([
                dmc.Text("Total Files", size="sm", c="dimmed"),
                dmc.Text(str(len(df)), size="xl", fw=700),
            ], p="md", withBorder=True),
            dmc.Paper([
                dmc.Text("Columns", size="sm", c="dimmed"),
                dmc.Text(str(len(df.columns)), size="xl", fw=700),
            ], p="md", withBorder=True),
            dmc.Paper([
                dmc.Text("Sample Size", size="sm", c="dimmed"),
                dmc.Text(f"{sample_perc}%", size="xl", fw=700),
            ], p="md", withBorder=True),
        ], cols=3, mb="md"),
        dmc.Title("Dataset Preview", order=3, mb="md"),
        dmc.ScrollArea([
            dmc.Table([
                dmc.TableThead([
                    dmc.TableTr([dmc.TableTh(col) for col in df.columns])
                ]),
                dmc.TableTbody([
                    dmc.TableTr([
                        dmc.TableTd(str(df.iloc[i, j])) for j in range(len(df.columns))
                    ]) for i in range(min(10, len(df)))
                ]),
            ], striped=True, highlightOnHover=True, withTableBorder=True),
        ], h=400),
    ])


@callback(
    Output("results-container", "children"),
    Output("load-data-button", "loading"),
    Output("global-audio-df", "data"),
    Output("global-output-df-dir", "data"),
    Input("load-data-button", "n_clicks"),
    State("global-audio-df", "data"),  # current loaded data (json)
    State("dataset-path-input", "value"),
    State("yaml-config-input", "value"),
    State("format-name-input", "value"),
    State("store-duration-switch", "checked"),
    State("sample-percentage-slider", "value"),
    State("output-df-dir", "value"),

    prevent_initial_call=True,
    allow_duplicate=True,
)
def handle_load(n_clicks, df_json, path, yaml_cfg, fmt_name, store_dur, sample_perc, output_dir):
    if not n_clicks:
        if df_json is not None:
            df_json_parse = json.loads(df_json)
            df = io_utils.load_df_complex_parquet(df_json_parse['data_path'])
            return _preview(df, sample_perc), False, df_json, dash.no_update
        raise dash.exceptions.PreventUpdate

    if not all([path, yaml_cfg, fmt_name]):
        return (
            dmc.Alert("Please fill in all required fields.", color="red", title="Validation Error"),
            False,
            dash.no_update,
            dash.no_update,
        )

    try:
        import maui.io
    except ImportError:
        return (
            dmc.Alert(
                "MAUI software library not found. Install with: pip install maui-software",
                color="red",
                title="Import Error",
            ),
            False,
            dash.no_update,
            dash.no_update,
        )

    try:
        df = maui.io.get_audio_info(
            path,
            format_file_path=yaml_cfg,
            format_name=fmt_name,
            date_time_func=None,
            store_duration=store_dur,
            perc_sample=sample_perc / 100,
        )
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "original_dataset.parquet")

        # df.to_parquet(output_path)
        io_utils.save_df_complex_parquet(df, output_path)

    except Exception as e:
        return (
            dmc.Alert(f"Error loading data: {e}", color="red", title="Loading Error"),
            False,
            dash.no_update,
            dash.no_update,
        )

    return_dict = {"original_data_loaded": True, "data_path": output_path}
    output_dir_dict = {"output_dir": output_dir}

    return _preview(df, sample_perc), False, json.dumps(return_dict), json.dumps(output_dir_dict)


@callback(
    Output("combine-date-block", "style"),
    Output("combine-columns-select", "data"),
    Input("global-audio-df", "data"),
)
def toggle_combine_fields(df_json):
    if df_json:
        df_json = json.loads(df_json)
        df = io_utils.load_df_complex_parquet(df_json['data_path'])
        options = [{"value": col, "label": col} for col in df.columns]
        return {"display": "block"}, options
    return {"display": "none"}, []


@callback(
    Output("global-audio-df", "data", allow_duplicate=True),
    Output("results-container", "children", allow_duplicate=True),
    Input("create-date-column-btn", "n_clicks"),
    State("combine-columns-select", "value"),
    State("combine-separator", "value"),
    State("combine-format", "value"),
    State("combine-output-name", "value"),
    State("combine-truncate-select", "value"),
    State("global-audio-df", "data"),
    State("sample-percentage-slider", "value"),
    prevent_initial_call=True,
)
def create_date_column(n_clicks, cols, sep, fmt, out_name, truncate_level, df_json, sample_perc):
    if not (n_clicks and cols and out_name):
        raise dash.exceptions.PreventUpdate

    df_json = json.loads(df_json)
    df = io_utils.load_df_complex_parquet(df_json['data_path'])
    try:
        combined = df[cols].astype(str).agg(sep.join, axis=1)
        dt_col = pd.to_datetime(combined, format=fmt, errors='coerce')
        if dt_col.isna().any():
            raise ValueError("Some dates could not be parsed with the given format.")

        if truncate_level == "year":
            dt_col = dt_col.dt.to_period("Y").dt.start_time  # mantém como datetime64
        elif truncate_level == "month":
            dt_col = dt_col.dt.to_period("M").dt.start_time  # mantém como datetime64
        elif truncate_level == "day":
            dt_col = dt_col.dt.floor("D")                    # mantém como datetime64
        elif truncate_level == "hour":
            dt_col = dt_col.dt.floor("H")                    # mantém como datetime64
        else:
            # Não formata, mantém como datetime completo
            pass

        dt_col = dt_col.dt.to_pydatetime()

        df[out_name] = dt_col

        print(df.dtypes)

        # df.to_parquet(df_json["data_path"])
        io_utils.save_df_complex_parquet(df, df_json["data_path"])

    except Exception as e:
        return dash.no_update, dmc.Alert(f"Error creating column: {e}", color="red")


    return_dict = {"original_data_loaded": True, "data_path": df_json["data_path"]}

    return (
        json.dumps(return_dict),
        _preview(df, sample_perc),
    )