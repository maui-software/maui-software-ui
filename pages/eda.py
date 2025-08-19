# pages/eda.py

import dash
from dash import html, dcc, Input, Output, State, callback, MATCH, ALL
import dash_mantine_components as dmc
import pandas as pd
import plotly.graph_objects as go
from maui import eda

import json

dash.register_page(__name__, path="/eda", name="Exploratory Data Analysis")

# Visualization mapping, functions and parameters according to maui.eda
VISUALIZACOES = {
    "Summary (card_summary)": {
        "func": eda.card_summary,
        "params": [
            {"name": "categories", "type": "multi_column", "label": "Categories (max. 2)", "max": 2, "required": True}
        ],
        "description": "Generates summary cards with general dataset statistics"
    },
    "Heatmap (heatmap_analysis)": {
        "func": eda.heatmap_analysis,
        "params": [
            {"name": "x_axis", "type": "column", "label": "X Axis (categorical)", "required": True},
            {"name": "y_axis", "type": "column", "label": "Y Axis (categorical)", "required": True},
            {"name": "color_continuous_scale", "type": "select", "label": "Color Scale", "default": "Viridis", 
             "options": ["Viridis", "Plasma", "Inferno", "Magma", "Cividis", "Blues", "Greens", "Reds"]}
        ],
        "description": "Creates heatmaps to visualize relationships between categorical variables"
    },
    "Histogram (histogram_analysis)": {
        "func": eda.histogram_analysis,
        "params": [
            {"name": "x_axis", "type": "column", "label": "X Axis (categorical)", "required": True},
            {"name": "category_column", "type": "column", "label": "Group by Category", "required": True}
        ],
        "description": "Histograms of data distribution grouped by category"
    },
    "Duration Boxplot (duration_analysis)": {
        "func": eda.duration_analysis,
        "params": [
            {"name": "category_column", "type": "column", "label": "Category", "required": True},
            {"name": "duration_column", "type": "column", "label": "Duration Column", "default": "duration"}
        ],
        "description": "Boxplots for duration analysis grouped by category"
    },
    "Daily Distribution (daily_distribution_analysis)": {
        "func": eda.daily_distribution_analysis,
        "params": [
            {"name": "date_column", "type": "column", "label": "Date Column", "default": "dt"},
            {"name": "category_column", "type": "column", "label": "Category", "required": True}
        ],
        "description": "Analysis of temporal data distribution over days"
    },
    "Duration Distribution (duration_distribution)": {
        "func": eda.duration_distribution,
        "params": [
            {"name": "time_unit", "type": "string", "label": "Time Unit", "default": "s"}
        ],
        "description": "Statistical distribution of audio file durations"
    },
}

def validate_data_for_visualization(df, viz_type, params_map):
    """Validates whether the data is suitable for the selected visualization"""
    if df is None or df.empty:
        return False, "Dataset is not loaded or is empty."
    
    # Specific validations per visualization type
    if viz_type == "Summary (card_summary)":
        categories = params_map.get("categories", [])
        if not categories:
            return False, "Select at least one category for the summary."
        missing_cols = [col for col in categories if col not in df.columns]
        if missing_cols:
            return False, f"Columns not found in dataset: {', '.join(missing_cols)}"
    
    elif viz_type in ["Heatmap (heatmap_analysis)", "Histogram (histogram_analysis)"]:
        required_cols = ["x_axis", "y_axis"] if "Heatmap" in viz_type else ["x_axis", "category_column"]
        for col_param in required_cols:
            col_name = params_map.get(col_param)
            if not col_name:
                return False, f"Select a column for {col_param.replace('_', ' ').title()}."
            if col_name not in df.columns:
                return False, f"Column '{col_name}' not found in dataset."
    
    elif "duration" in viz_type.lower():
        duration_col = params_map.get("duration_column", "duration")
        if duration_col and duration_col not in df.columns:
            return False, f"Duration column '{duration_col}' not found in dataset."
    
    elif "daily" in viz_type.lower():
        date_col = params_map.get("date_column", "dt")
        if date_col and date_col not in df.columns:
            return False, f"Date column '{date_col}' not found in dataset."
    
    return True, "Valid data for visualization."

def build_param_component(param, columns):
    """Builds input components for visualization parameters"""
    base_props = {
        "id": {"type": "eda-param", "name": param["name"]},
        "label": param["label"],
        "required": param.get("required", False),
    }
    
    if param["type"] == "multi_column":
        return dmc.MultiSelect(
            **base_props,
            data=[{"label": col, "value": col} for col in columns],
            maxValues=param.get("max", None),
            searchable=True,
            clearable=True,
            nothingFoundMessage="No columns found",
            placeholder="Select columns..."
        )
    
    elif param["type"] == "column":
        return dmc.Select(
            **base_props,
            data=[{"label": col, "value": col} for col in columns],
            value=param.get("default"),
            searchable=True,
            clearable=True,
            placeholder="Select a column..."
        )
    
    elif param["type"] == "select":
        return dmc.Select(
            **base_props,
            data=[{"label": opt, "value": opt} for opt in param["options"]],
            value=param.get("default"),
            clearable=True,
            placeholder="Select an option..."
        )
    
    elif param["type"] == "string":
        return dmc.TextInput(
            **base_props,
            value=param.get("default", ""),
            placeholder=f"Enter {param['label'].lower()}..."
        )

layout = dmc.Container([
    dmc.Title("Exploratory Data Analysis", order=1, mb=30),
    
    # Info card about EDA
    # dmc.Card([
    #     dmc.CardSection([
    #         dmc.Stack([
    #             dmc.Text("Explore your audio data with MAUI's specialized tools. "
    #                      "Select the visualization type and configure the parameters to generate insights.",
    #                      size="sm", c="dimmed")
    #         ], gap="xs")
    #     ])
    # ], withBorder=True, radius="md", mb="xl"),
    
    # Main controls
    dmc.Paper([
        dmc.Stack([
            dmc.Select(
                id="eda-viz-select",
                label="Visualization Type",
                data=[{"label": k, "value": k} for k in VISUALIZACOES],
                placeholder="Choose the type of visualization...",
                required=True,
                clearable=True,
                searchable=True,
                leftSection=dmc.ThemeIcon(html.I(className="fas fa-chart-line"), size="sm"),
                description="Select the type of analysis you want to perform"
            ),
            
            html.Div(id="viz-description"),
            html.Div(id="eda-param-list", style={"marginBottom": 25}),
            
            dmc.Group([
                dmc.Button(
                    "Generate Visualization",
                    id="eda-run-btn",
                    variant="filled",
                    leftSection=html.I(className="fas fa-play"),
                    size="md"
                ),
                dmc.Button(
                    "Clear Parameters",
                    id="eda-clear-btn",
                    variant="outline",
                    leftSection=html.I(className="fas fa-eraser"),
                    size="md",
                    color="gray"
                )
            ], gap="md")
        ], gap="md"),
    ], p="md", withBorder=False, radius="md", mb="xl", shadow="md"),
    
    # Result area
    html.Div(id="eda-alerts"),
    
    # Chart with corrected loading overlay
    html.Div([
        dcc.Graph(
            id="eda-fig-area",
            style={'height': '600px'},
            config={'displayModeBar': True, 'toImageButtonOptions': {'height': 600, 'width': 1200}}
        ),
        dmc.LoadingOverlay(
            id="eda-loading-overlay",
            visible=False,
            loaderProps={"variant": "oval", "color": "blue", "size": "lg"}
        )
    ], style={"position": "relative"})
], size="lg")

@callback(
    [Output("viz-description", "children"),
     Output("eda-param-list", "children")],
    [Input("eda-viz-select", "value"),
     Input("global-audio-df", "data")]
)
def render_param_inputs(viz, df_json):
    if not viz or not df_json:
        return "", ""
    
    try:
        df_json = json.loads(df_json)
        df = pd.read_parquet(df_json['data_path'])

        viz_info = VISUALIZACOES[viz]
        
        # Visualization description
        description = dmc.Alert(
            viz_info["description"],
            title=f"About: {viz}",
            color="blue",
            variant="light",
            style={"marginBottom": "20px"}
        )
        
        # Parameter components
        params = viz_info["params"]
        if not params:
            param_components = dmc.Text("This visualization does not require additional parameters.",
                                      style={"fontStyle": "italic"})
        else:
            param_components = dmc.Stack([
                build_param_component(param, df.columns) for param in params
            ], gap="sm")
        
        return description, param_components
    
    except Exception as e:
        error_msg = dmc.Alert(f"Error processing data: {str(e)}", color="red", title="Error")
        return error_msg, ""

@callback(
    [Output("eda-fig-area", "figure"),
     Output("eda-alerts", "children"),
     Output("eda-loading-overlay", "visible")],
    [Input("eda-run-btn", "n_clicks")],
    [State("global-audio-df", "data"),
     State("eda-viz-select", "value"),
     State({"type": "eda-param", "name": ALL}, "value"),
     State({"type": "eda-param", "name": ALL}, "id")],
    prevent_initial_call=True
)
def generate_viz(n_clicks, df_json, viz_type, values, ids):
    if not n_clicks:
        return go.Figure(), "", False
    
    # Initial validation
    if not df_json:
        alert = dmc.Alert("No dataset loaded. Go to 'Load Audio Data' first.",
                         color="red", title="Error")
        return go.Figure(), alert, False
    
    if not viz_type:
        alert = dmc.Alert("Select a visualization type.", color="orange", title="Attention")
        return go.Figure(), alert, False
    
    try:
        df_json = json.loads(df_json)
        df = pd.read_parquet(df_json['data_path'])
        params_map = {c['name']: v for c, v in zip(ids, values)}
        
        # Data validation
        is_valid, validation_msg = validate_data_for_visualization(df, viz_type, params_map)
        if not is_valid:
            alert = dmc.Alert(validation_msg, color="red", title="Validation Error")
            return go.Figure(), alert, False
        
        # Run the visualization
        func = VISUALIZACOES[viz_type]["func"]
        
        if viz_type == "Summary (card_summary)":
            categories = params_map.get("categories", []) or []
            card, fig = func(df, categories, show_plot=False)
            
        elif viz_type == "Heatmap (heatmap_analysis)":
            x_axis = params_map.get("x_axis")
            y_axis = params_map.get("y_axis")
            scale = params_map.get("color_continuous_scale", "Viridis") or "Viridis"
            _, fig = func(df, x_axis, y_axis, color_continuous_scale=scale, show_plot=False)
            
        elif viz_type == "Histogram (histogram_analysis)":
            x_axis = params_map.get("x_axis")
            cat_col = params_map.get("category_column")
            fig = func(df, x_axis, cat_col, show_plot=False)
            
        elif viz_type == "Duration Boxplot (duration_analysis)":
            cat_col = params_map.get("category_column")
            dur_col = params_map.get("duration_column", "duration") or "duration"
            fig = func(df, cat_col, dur_col, show_plot=False)
            
        elif viz_type == "Daily Distribution (daily_distribution_analysis)":
            date_col = params_map.get("date_column", "dt") or "dt"
            cat_col = params_map.get("category_column")
            fig = func(df, date_col, cat_col, show_plot=False)
            
        elif viz_type == "Duration Distribution (duration_distribution)":
            time_unit = params_map.get("time_unit", "s") or "s"
            fig = func(df, time_unit=time_unit, show_plot=False)
        
        else:
            fig = go.Figure(layout={"title": f"Visualization '{viz_type}' not implemented."})
        
        # Configure chart layout
        if fig and hasattr(fig, 'update_layout'):
            fig.update_layout(
                height=600,
                margin=dict(l=50, r=50, t=80, b=50),
                font=dict(size=12)
            )
        
        success_alert = dmc.Alert(
            f"Visualization '{viz_type}' generated successfully!",
            color="green",
            title="Success",
            style={"marginBottom": "20px"}
        )
        
        return fig, success_alert, False
    
    except Exception as e:
        error_alert = dmc.Alert(
            f"Error generating visualization: {str(e)}",
            color="red",
            title="Execution Error",
            style={"marginBottom": "20px"}
        )
        return go.Figure(), error_alert, False

@callback(
    Output("eda-loading-overlay", "visible", allow_duplicate=True),
    Input("eda-run-btn", "n_clicks"),
    prevent_initial_call=True
)
def show_loading(n_clicks):
    if n_clicks:
        return True
    return False

@callback(
    [Output({"type": "eda-param", "name": ALL}, "value")],
    [Input("eda-clear-btn", "n_clicks")],
    [State({"type": "eda-param", "name": ALL}, "id")],
    prevent_initial_call=True
)
def clear_parameters(n_clicks, ids):
    if not n_clicks:
        return [[]]
    
    # Returns empty values for all parameters
    return [[None for _ in ids]]
