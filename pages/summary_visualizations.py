# pages/summary_visualizations.py

import dash
from dash import html, dcc, Input, Output, State, callback, ALL, MATCH
import dash_mantine_components as dmc
import pandas as pd
import plotly.graph_objects as go
from maui import visualizations

import json

dash.register_page(__name__, path="/summary-visualizations", name="Summary Visualizations")

VISUALIZATIONS = {
    "Radar Plot": {
        "func": visualizations.indices_radar_plot,
        "params": [
            {"name": "indices", "type": "multi_column", "label": "Indices", "required": True},
            {"name": "agg_type", "type": "select", "label": "Aggregation", "options": ["mean", "median", "stddev", "var", "max", "min"], "default": "mean", "required": True},
            {"name": "group_by", "type": "multi_column", "label": "Group by Columns (max 2)", "max": 2},
            {"name": "max_cols", "type": "int", "label": "Max Columns (subplots)", "default": 3}
        ],
        "description": "Radar plot for comparing acoustic indices, using aggregation and grouping."
    },
    "Histogram Plot": {
        "func": visualizations.indices_histogram_plot,
        "params": [
            {"name": "indices", "type": "multi_column", "label": "Indices", "required": True},
            {"name": "group_by", "type": "column", "label": "Group by (optional)"},
            {"name": "max_cols", "type": "int", "label": "Max Columns (subplots)", "default": 3}
        ],
        "description": "Histograms showing the distribution of acoustic indices."
    },
    "Violin Plot": {
        "func": visualizations.indices_violin_plot,
        "params": [
            {"name": "indices", "type": "multi_column", "label": "Indices", "required": True},
            {"name": "group_by", "type": "column", "label": "Group by (optional)"}
        ],
        "description": "Violin plot showing distribution/density of indices."
    },
    "Polar Bar Plot": {
        "func": visualizations.polar_bar_plot,
        "params": [
            {"name": "date_time_col", "type": "column", "label": "Date/Datetime Column", "required": True},
            {"name": "categories_col", "type": "column", "label": "Categories Column", "required": True},
            {"name": "percent", "type": "bool", "label": "Show as percent (optional)", "default": False}
        ],
        "description": "Polar bar plot to visualize categories throughout the year."
    },
    "Parallel Coordinates Plot": {
        "func": visualizations.parallel_coordinates_plot,
        "params": [
            {"name": "indices", "type": "multi_column", "label": "Indices (min. 2)", "required": True},
            {"name": "color_col", "type": "column", "label": "Color By Column", "required": True}
        ],
        "description": "Parallel coordinates plot for multivariate analysis."
    }
}

def build_param_component(param, columns):
    base_props = {
        "id": {"type": "summary-param", "name": param["name"]},
        "label": param.get("label", param["name"]),
        "required": param.get("required", False),
    }
    if param["type"] == "multi_column":
        multi_props = {**base_props}
        multi_props.update({
            "data": [{"label": col, "value": col} for col in columns],
            "searchable": True,
            "clearable": True,
            "nothingFoundMessage": "No columns found",
            "placeholder": "Select columns..."
        })
        if param.get("max") is not None:
            multi_props["maxValues"] = param["max"]
        return dmc.MultiSelect(**multi_props)
    elif param["type"] == "column":
        return dmc.Select(
            **base_props,
            data=[{"label": col, "value": col} for col in columns],
            searchable=True,
            clearable=True,
            placeholder="Select a column..."
        )
    elif param["type"] == "select":
        return dmc.Select(
            **base_props,
            data=[{"label": v, "value": v} for v in param["options"]],
            value=param.get("default"),
            clearable=True,
            placeholder="Select an option..."
        )
    elif param["type"] == "int":
        return dmc.NumberInput(
            **base_props,
            value=param.get("default", None),
            min=1,
            max=12,
            hideControls=False
        )
    elif param["type"] == "bool":
        return dmc.Switch(
            id={"type": "summary-param", "name": param["name"]},
            label=param["label"],
            checked=param.get("default", False)
        )

layout = dmc.Container([
    dmc.Title("Summary Visualizations", order=1, mb=30),
    dmc.Paper([
        dmc.Stack([
            dmc.Select(
                id="summary-viz-select",
                label="Visualization Type",
                data=[{"label": k, "value": k} for k in VISUALIZATIONS.keys()],
                placeholder="Choose the type of visualization...",
                required=True,
                clearable=True,
                searchable=True,
            ),
            html.Div(id="summary-viz-description"),
            html.Div(id="summary-param-list", style={"marginBottom": 25}),
            dmc.Group([
                dmc.Button("Generate Visualization", id="summary-run-btn", variant="filled", leftSection=html.I(className="fas fa-play"), size="md"),
                dmc.Button("Clear Parameters", id="summary-clear-btn", variant="outline", leftSection=html.I(className="fas fa-eraser"), size="md", color="gray")
            ], gap="md")
        ], gap="md"),
    ], p="md", withBorder=False, radius="md", mb="xl", shadow="md"),
    html.Div(id="summary-alerts"),
    html.Div([
        dcc.Graph(
            id="summary-fig-area",
            style={'height': '600px'},
            config={'displayModeBar': True, 'toImageButtonOptions': {'height': 600, 'width': 1200}}
        ),
        dmc.LoadingOverlay(
            id="summary-loading-overlay",
            visible=False,
            loaderProps={"variant": "oval", "color": "blue", "size": "lg"}
        ),
    ], style={"position": "relative"})
], size="lg")

@callback(
    [Output("summary-viz-description", "children"),
     Output("summary-param-list", "children")],
    [Input("summary-viz-select", "value"),
     Input("global-audio-df-idx", "data")],
    prevent_initial_call=False
)
def render_param_inputs(viz, df_idx_json):
    if not viz:
        return "", ""
    if not df_idx_json:
        return (
            dmc.Alert(
                "You need to calculate the DataFrame with acoustic indices before generating visualizations.",
                title="Warning",
                color="yellow"
            ), ""
        )
    try:
        df_idx_json_parse = json.loads(df_idx_json)
        df = pd.read_csv(df_idx_json_parse['data_path'])
        #df = pd.read_parquet(df_idx_json_parse['data_path'])
        columns = list(df.columns)
        viz_info = VISUALIZATIONS[viz]
        description = dmc.Alert(
            viz_info["description"],
            title=f"About: {viz}",
            color="blue",
            variant="light",
            style={"marginBottom": "20px"}
        )
        params = viz_info["params"]
        if not params:
            param_components = dmc.Text("This visualization does not require additional parameters.", style={"fontStyle": "italic"})
        else:
            param_components = dmc.Stack([build_param_component(param, columns) for param in params], gap="sm")
        return description, param_components
    except Exception as e:
        return dmc.Alert(f"Error processing data: {str(e)}", color="red", title="Error"), ""

@callback(
    [Output("summary-fig-area", "figure"),
     Output("summary-alerts", "children"),
     Output("summary-loading-overlay", "visible")],
    [Input("summary-run-btn", "n_clicks")],
    [State("global-audio-df-idx", "data"),
     State("summary-viz-select", "value"),
     State({"type": "summary-param", "name": ALL}, "value"),
     State({"type": "summary-param", "name": ALL}, "id")],
    prevent_initial_call=True
)
def generate_summary_viz(n_clicks, df_idx_json, viz_type, values, ids):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    if not df_idx_json:
        return go.Figure(), dmc.Alert("You need to calculate the DataFrame with acoustic indices before.", color="yellow", title="Warning"), False
    if not viz_type:
        return go.Figure(), dmc.Alert("Select the type of visualization.", color="orange", title="Attention"), False
    try:
        df_idx_json_parse = json.loads(df_idx_json)
        df = pd.read_csv(df_idx_json_parse['data_path'])
        #df = pd.read_parquet(df_idx_json_parse['data_path'])
        params_map = {comp_id['name']: v for comp_id, v in zip(ids, values)}

        func = VISUALIZATIONS[viz_type]["func"]
        if viz_type == "Radar Plot":
            args = dict(
                df=df,
                indices=params_map.get("indices", []) or [],
                agg_type=params_map.get("agg_type", "mean"),
                group_by=params_map.get("group_by") or None,
                max_cols=params_map.get("max_cols", 3),
                show_plot=False
            )
        elif viz_type == "Histogram Plot":
            args = dict(
                df=df,
                indices=params_map.get("indices", []) or [],
                group_by=params_map.get("group_by") or None,
                max_cols=params_map.get("max_cols", 3),
                show_plot=False
            )
        elif viz_type == "Violin Plot":
            args = dict(
                df=df,
                indices=params_map.get("indices", []) or [],
                group_by=params_map.get("group_by") or None,
                show_plot=False
            )
        elif viz_type == "Polar Bar Plot":
            args = dict(
                df=df,
                date_time_col=params_map.get("date_time_col"),
                categories_col=params_map.get("categories_col"),
                percent=bool(params_map.get("percent", False)),
                show_plot=False
            )
        elif viz_type == "Parallel Coordinates Plot":
            indices = params_map.get("indices", []) or []
            if len(indices) < 2:
                return go.Figure(), dmc.Alert("Select at least 2 indices for Parallel Coordinates Plot.", color="red", title="Validation"), False
            args = dict(
                df=df,
                indices=indices,
                color_col=params_map.get("color_col"),
                show_plot=False
            )
        else:
            return go.Figure(layout={"title": f"Visualization '{viz_type}' not implemented."}), "", False

        fig = func(**args)
        if fig and hasattr(fig, "update_layout"):
            fig.update_layout(
                height=600,
                margin=dict(l=50, r=50, t=80, b=50),
                font=dict(size=12)
            )

        return fig, dmc.Alert(f"Visualization '{viz_type}' generated successfully!", color="green", title="Success", style={"marginBottom": "20px"}), False
    except Exception as e:
        return go.Figure(), dmc.Alert(f"Error generating visualization: {str(e)}", color="red", title="Error!"), False

@callback(
    Output({"type": "summary-param", "name": ALL}, "value"),
    Input("summary-clear-btn", "n_clicks"),
    State({"type": "summary-param", "name": ALL}, "id"),
    prevent_initial_call=True
)
def clear_summary_params(n_clicks, ids):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
    return [None for _ in ids]
