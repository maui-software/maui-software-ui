# pages/acoustic_indices.py
import dash
from dash import html, dcc, callback, Input, Output, State
import dash_mantine_components as dmc
import pandas as pd
import json
import os

from acoustic_indices.acoustic_indices_calculation import AcousticIndices
from maui import acoustic_indices as maui_acoustic_indices

from utils import io_utils

dash.register_page(__name__, path="/acoustic-indices", name="Acoustic Indices")

# Instantiate AcousticIndices
AIdx = AcousticIndices()
AVAILABLE_INDICES = AIdx.available_indices

layout = dmc.Container([
    dmc.Title("Acoustic Indices Calculation", order=1, mb=30),

    dmc.Paper([
        dmc.Stack([
            dmc.MultiSelect(
                id="indices-idx-select",
                label="Acoustic Index",
                data=[{"label": l, "value": v} for l, v in AVAILABLE_INDICES.items()],
                placeholder="Select the acoustic indices...",
                required=True,
                clearable=True,
                searchable=True,
                description="Select the desired Acoustic Indices"
            ),

            # Select coluna file path, será preenchido por callback
            dmc.Select(
                id="file-path-column",
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
                        dmc.AccordionControl("Additional Configurations"),
                        dmc.AccordionPanel([
                            dmc.Stack([
                                # Tipo de processamento: toggle paralelo/sequencial via RadioGroup CORRIGIDO
                                dmc.RadioGroup(
                                    id="processing-type",
                                    label="Processing Type",
                                    value="sequential",
                                    children=[
                                        dmc.Radio(label="Sequential", value="sequential", mb="sm"),
                                        dmc.Radio(label="Parallel", value="parallel", mb="sm"),
                                    ],
                                    mb="md",
                                ),

                                # Chunk size slider 1-100 default 5
                                dmc.Text("Chunk Size"),
                                dcc.Slider(
                                    id="chunk-size",
                                    min=1,
                                    max=100,
                                    value=5,
                                    step=1,
                                    marks={i: f"{i}" for i in range(0, 81, 20)},
                                    tooltip={"placement": "top", "always_visible": False},

                                ),

                                # Text input para diretório temporário
                                dmc.TextInput(
                                    id="temp-directory",
                                    label="Temporary Directory",
                                    placeholder="Insert the temporary directory",
                                    value="./temp_dir_ac",
                                    mb="md",
                                ),
                            ])
                        ]),
                    ], value="processing-settings")
                ]
            ),

            dmc.Group([
                dmc.Button(
                    "Calculate indices",
                    id="indices-run-btn",
                    variant="filled",
                    leftSection=html.I(className="fas fa-play"),
                    size="md"
                ),
                dmc.Button(
                    "Clear Indices",
                    id="indices-clear-btn",
                    variant="outline",
                    leftSection=html.I(className="fas fa-eraser"),
                    size="md",
                    color="gray"
                )
            ], gap="md")
        ], gap="md"),
    ], p="md", withBorder=False, radius="md", mb="xl", shadow="md"),

    # Área de resultados ENVOLVIDA em dcc.Loading!
    dcc.Loading(
        id="loading-idx", type="dot",
        overlay_style={"visibility": "visible", "filter": "blur(10px)"},
        children=html.Div(id="results-container-idx")
    ),

], size="lg")


# Preenche as opções da Select para coluna de file path, lendo do DataFrame armazenado
@callback(
    Output("file-path-column", "data"),
    Output("file-path-column", "value"),
    Input("global-audio-df", "data"),
    Input("global-audio-df-seg", "data"),
    prevent_initial_call=False
)
def populate_file_path_column_choices(df_json_original, df_json_seg):
    if not df_json_original:
        return [], None

    df_json = df_json_original
    if df_json_seg:
        df_json = df_json_seg

    # Se for string JSON, converta para dict
    if isinstance(df_json, str):
        try:
            df_json = json.loads(df_json)
        except Exception as e:
            return [], None

    if not isinstance(df_json, dict):
        return [], None

    df = io_utils.load_df_complex_parquet(df_json['data_path'])
    cols = df.columns

    options = [{"label": col, "value": col} for col in cols]
    default_value = "file_path" if "file_path" in cols else (cols[0] if cols else None)
    return options, default_value

def _preview(df_indices: pd.DataFrame):
    return dmc.Stack([
        dmc.Alert(
            "Successfully calculated Acoustic Indices!",
            title="Success",
            color="green"
        ),
        dmc.ScrollArea([
            dmc.Table([
                dmc.TableThead([
                    dmc.TableTr(
                        [dmc.TableTh(col) for col in df_indices.columns]
                    )
                ]),
                dmc.TableTbody([
                    dmc.TableTr([
                        dmc.TableTd(
                            (val if len(val) <= 30 else val[:27] + '...')
                            if isinstance(val := str(df_indices.iloc[i, j]), str) else val,
                            style={
                                "maxHeight": "40px",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                                "whiteSpace": "nowrap"
                            }
                        ) for j in range(len(df_indices.columns))
                    ]) for i in range(min(10, len(df_indices)))
                ]),
            ],
            striped=True,
            highlightOnHover=True,
            withTableBorder=True),
        ], h=400),
    ])

@callback(
    Output("results-container-idx", "children"),
    Output("indices-run-btn", "n_clicks"),
    Output("global-audio-df-idx", "data"),

    Input("indices-run-btn", "n_clicks"),

    State("global-audio-df-idx", "data"),
    State("global-audio-df-seg", "data"),
    State("global-audio-df", "data"),
    State("indices-idx-select", "value"),
    State("processing-type", "value"),
    State("chunk-size", "value"),
    State("file-path-column", "value"),
    State("temp-directory", "value"),
    State("global-output-df-dir", "data"),
    prevent_initial_call=False
)
def calculate_and_show(n_clicks, df_json, df_json_seg, df_json_original, indices_map,
                      processing_type, chunk_size, file_path_col, temp_dir, output_dir_json):

    if df_json_original is None:
        if not n_clicks:
            if df_json is None:
                return dmc.Alert("Load the dataset before calculating acoustic indices.", color="yellow", title="Validation Error"), False, None
            else:

                return dmc.Alert("Load the dataset before calculating acoustic indices.", color="yellow", title="Validation Error"), False, df_json

        else:
            if df_json is None:
                return dmc.Alert("Load the dataset before calculating acoustic indices.", color="yellow", title="Validation Error"), False, None
            else:
                return dmc.Alert("Load the dataset before calculating acoustic indices.", color="yellow", title="Validation Error"), False, df_json

    if not n_clicks:
        if df_json is None:
            return dash.no_update, False, None
        else:
            df_json_parse = json.loads(df_json)
            df_indices = io_utils.load_df_complex_parquet(df_json_parse['data_path'])
            return _preview(df_indices), False, df_json

    if df_json_seg is None:
        df_json_original_parse = json.loads(df_json_original)
        df = io_utils.load_df_complex_parquet(df_json_original_parse['data_path'])

    else:
        df_json_seg_parse = json.loads(df_json_seg)
        df = io_utils.load_df_complex_parquet(df_json_seg_parse['data_path'])

        

    if df_json is not None:
        df_json_parse = json.loads(df_json)
        df = io_utils.load_df_complex_parquet(df_json_parse['data_path'])
    else:
        df_indices = None

    if n_clicks and indices_map:
        indices = indices_map
        AIdx.set_indices(indices)

        # Ajusta parâmetros do cálculo conforme inputs
        parallel_flag = False
        if processing_type:
            parallel_flag = processing_type.lower() == "parallel"

        df_indices = maui_acoustic_indices.calculate_acoustic_indices(
            df_init=df,
            file_path_col=file_path_col,
            acoustic_indices_methods=AIdx.acoustic_indices_methods,
            pre_calculation_method=AIdx.pre_calculation_method,
            parallel=parallel_flag,
            chunk_size=chunk_size,
            temp_dir=temp_dir
        )

        print("-------------> calculado")


        output_dir_json_parse = json.loads(output_dir_json)
        output_dir = output_dir_json_parse["output_dir"]
        output_path = os.path.join(output_dir, "acoustic_indices_dataset.parquet")
        
        # io_utils.save_df_complex_parquet(df_indices, output_path)
        df_indices.to_csv(output_path)

        print("-------------> Salvo na memoria")



    if df_indices is not None:
        return_dict = {"indices_data_loaded": True, "data_path": output_path}
    else:
        None

    return _preview(df_indices), False, json.dumps(return_dict)


@callback(
    Output("indices-idx-select", "value"),
    Input("indices-clear-btn", "n_clicks"),
    prevent_initial_call=True
)
def clear_indices(n_clicks):
    return []

# Comentários para futuras features:
# - Adicionar controle de processamento paralelo (já incluído via toggle)
# - chunk_size (deixar como parâmetro, já incluído via slider)
# - temp_dir (deixar configurável via input)
# - escolher coluna de file_path (incluso)
