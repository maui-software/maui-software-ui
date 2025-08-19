#  pages/welcome.py
import dash
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc
import pandas as pd

dash.register_page(__name__, path="/", name="Welcome")

layout = dmc.Container([
    dmc.Center(
        p="md",
        children=[
            dmc.Image(
                radius="md",
                h=250,
                w="auto",
                fit="contain",
                src="/assets/logo.png",
            )
        ],
    ),

    html.Div(id="dataset-info-welcome"),

    dmc.Grid([
        dmc.GridCol([
            dmc.Card(
                children=[
                    dmc.CardSection(
                        dmc.Image(
                            src="/assets/load_data.png",
                            h=160,
                            alt="Norway",
                        )
                    ),
                    dmc.Group(
                        [
                            dmc.Text("Dataset Load", fw=500),
                        ],
                        justify="space-between",
                        mt="md",
                        mb="xs",
                    ),
                    dmc.Text(
                        "With Maui you cans easly load your dataset according to its file name format",
                        size="sm",
                        c="dimmed",
                    ),
                    
                ],
                withBorder=True,
                shadow="md",
                radius="md",
                w=350,
            )
        ], span=4),
        dmc.GridCol([
            dmc.Card(
                children=[
                    dmc.CardSection(
                        dmc.Image(
                            src="/assets/load_data.png",
                            h=160,
                            alt="Norway",
                        )
                    ),
                    dmc.Group(
                        [
                            dmc.Text("Calculate Acoustic Indices", fw=500),
                        ],
                        justify="space-between",
                        mt="md",
                        mb="xs",
                    ),
                    dmc.Text(
                        "With Maui you cans easly load your dataset according to its file name format",
                        size="sm",
                        c="dimmed",
                    ),
                    
                ],
                withBorder=True,
                shadow="md",
                radius="md",
                w=350,
            )
        ], span=4),

        dmc.GridCol([
            dmc.Card(
                children=[
                    dmc.CardSection(
                        dmc.Image(
                            src="/assets/load_data.png",
                            h=160,
                            alt="Norway",
                        )
                    ),
                    dmc.Group(
                        [
                            dmc.Text("Explore your Data", fw=500),
                        ],
                        justify="space-between",
                        mt="md",
                        mb="xs",
                    ),
                    dmc.Text(
                        "With Maui you cans easly load your dataset according to its file name format",
                        size="sm",
                        c="dimmed",
                    ),
                    
                ],
                withBorder=True,
                shadow="md",
                radius="md",
                w=350,
            )
        ], span=4),

        dmc.GridCol([], span=2),

        dmc.GridCol([
            dmc.Card(
                children=[
                    dmc.CardSection(
                        dmc.Image(
                            src="/assets/load_data.png",
                            h=160,
                            alt="Norway",
                        )
                    ),
                    dmc.Group(
                        [
                            dmc.Text("Visualize Spectrograms", fw=500),
                        ],
                        justify="space-between",
                        mt="md",
                        mb="xs",
                    ),
                    dmc.Text(
                        "With Maui you cans easly load your dataset according to its file name format",
                        size="sm",
                        c="dimmed",
                    ),
                    
                ],
                withBorder=True,
                shadow="md",
                radius="md",
                w=350,
            )
        ], span=4),

        dmc.GridCol([
            dmc.Card(
                children=[
                    dmc.CardSection(
                        dmc.Image(
                            src="/assets/load_data.png",
                            h=160,
                            alt="Norway",
                        )
                    ),
                    dmc.Group(
                        [
                            dmc.Text("Generate Advanced Visualizations", fw=500),
                        ],
                        justify="space-between",
                        mt="md",
                        mb="xs",
                    ),
                    dmc.Text(
                        "With Maui you cans easly load your dataset according to its file name format",
                        size="sm",
                        c="dimmed",
                    ),
                    
                ],
                withBorder=True,
                shadow="md",
                radius="md",
                w=350,
            )
        ], span=4),
        dmc.GridCol([], span=2),
    ], justify="center"),

], size="xl", p=40)


@callback(
    Output("dataset-info-welcome", "children"),
    Input("global-audio-df", "data"),
    prevent_initial_call=True,
)
def show_info(df_json):
    if not df_json:
        return dmc.Alert(
            "No dataset loaded yet. Click 'Start Loading Data' to begin.",
            title="No Data",
            color="blue",
            style={"marginBottom": "30px"},
        )

    try:
        df = pd.read_json(df_json, orient="split")
        return dmc.Alert(
            f"Dataset with {len(df)} audio files is currently loaded and ready for analysis!",
            title="Dataset Loaded",
            color="green",
            style={"marginBottom": "30px"},
        )
    except Exception:
        return dmc.Alert(
            "Error reading loaded dataset.",
            color="yellow",
            style={"marginBottom": "30px"},
        )
