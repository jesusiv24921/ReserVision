import warnings
warnings.filterwarnings("ignore", category=UserWarning)

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output

from app import app
from my_project.layout import banner, build_tabs, footer


from my_project.tab_relation.relation import layout_select
from my_project.tab_summary.app_summary import layout_summary
from my_project.tab_conn_factor.app_conn_factor import layout_conn
from my_project.tab_behavior_patterns.behavior import layout_injection_pattern

from my_project.scripts.auth import authenticate 


authenticate(app)

server = app.server
server.secret_key = '26Amarillo3*' 
app.title = "Control de Yacimientos"
app.layout = dbc.Container(
    fluid=True,
    style={"padding": "0"},
    children=[
        dcc.Location(id="url", refresh=False),
        banner(),
        html.Div(id="page-content"),
        footer(),
    ],
)

@app.callback(
    dash.dependencies.Output("page-content", "children"),
    [dash.dependencies.Input("url", "pathname")],
)
def display_page(pathname):
    if pathname == "/":
        return build_tabs()
    else:
        # Devuelve un mensaje genérico si no se encuentra la página
        return html.H3("404 - Página no encontrada. Por favor, regrese al inicio.", style={"text-align": "center"})

# Handle tab selection
@app.callback(
    Output("tabs-content", "children"),
    [
        Input("tabs", "value"),
        Input("si-ip-radio-input", "value"),
    ],
)
def render_content(tab, si_ip):
    """Update the contents of the page depending on what tab the user selects."""
    if tab == "tab-select":
        return layout_select()
    elif tab == "tab-summary":
        return layout_summary()
    elif tab == "tab-behavior":
        return layout_injection_pattern()
    elif tab == "tab-conn":
        return layout_conn()
    else:
        # Devolver un mensaje si no existe la pestaña seleccionada
        return html.H3("Error - Tab no encontrada.", style={"text-align": "center"})

if __name__ == "__main__":
    app.run_server(
        debug=False,
        host="0.0.0.0",
        port=8080,
        processes=1,
        threaded=True,
    )
