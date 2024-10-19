import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash_extensions.enrich import dcc, html, Output, Input
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from dash import dash_table
from dash.dependencies import Input, Output, State
from app import app
from my_project.scripts.carga_datos import CargaDatos
from my_project.tab_summary.charts_summary import update_patron, update_boxplot

# Cargar datos necesarios utilizando la clase CargaDatos
data_coordenadas = CargaDatos().data_cargar('coordenadas')
data_relacion = CargaDatos().data_cargar('relacion_iny_prod')
pwf = CargaDatos().data_cargar('pwf')
mes = CargaDatos().data_cargar('produccion_mes')
mes = mes.astype({'qo': 'int64', 'ql': 'int64', 'qw': 'int64', 'qwi': 'int64', 'dias': 'float64', 'pwi': 'int64', 'WOR': 'float64', 'Wcut': 'float64'})
inyectores = data_relacion['Inyector'].unique()
inyeccion_diaria = CargaDatos().data_cargar('inyeccion_diaria')
data_estatica = CargaDatos().data_cargar('data_estatica')

def layout_summary():
    """
    Genera el layout para la pestaña de resumen, que incluye:
    - Dropdowns para seleccionar inyectores, ubicación y productores
    - Gráfico del mapa de relaciones entre patrones e inyectores
    - Histogramas y una tabla con datos de producción
    - Filtro para rango de fechas
    """
    return html.Div(
        className="container-col",
        id="tab-summary-container",
        children=[
            # Almacenamiento de datos en session/memory stores
            dcc.Store(id='qo-data-store'),
            dcc.Store(id='store-dropdown-inyector'),
            dcc.Store(id='store-dropdown-productor'),
            dcc.Store(id='store-dropdown-ubicacion'),
            
            # Sección de Dropdowns para filtros
            html.Div(
                className="mt-2 mb-4 d-flex justify-content-between",
                children=[
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                id="dataset-dropdown-inyector_2",
                                options=[{'label': inyector, 'value': inyector} for inyector in inyectores],
                                placeholder="Seleccione Inyector",
                                value=inyectores[0],
                                className="mt-2 mb-2"
                            ),
                        ],
                        style={"width": "30%"},
                    ),
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                id="ubicacion-dropdown",
                                options=[
                                    {'label': 'PL', 'value': 'PL'},
                                    {'label': 'SL', 'value': 'SL'},
                                    {'label': 'Ambos', 'value': 'Ambos'}
                                ],
                                value='Ambos',
                                placeholder="Seleccione Ubicación",
                                className="mt-2 mb-2"
                            ),
                        ],
                        style={"width": "30%"},
                    ),
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                id="dataset-dropdown-productor",
                                options=[],
                                placeholder="Seleccione Productor",
                                multi=True,
                                searchable=True,
                                className="mt-2 mb-2"
                            ),
                        ],
                        style={"width": "30%"},
                    ),
                ]
            ),

            # Gráfico del Mapa de Relaciones entre patrones e inyectores
            html.Div(
                className="container-col",
                id="mapa-relaciones-container",
                children=[
                    html.H4("Comportamiento: Patrón & Productores Asociados"),
                    dcc.Loading(
                        type="circle",
                        children=html.Div(
                            dcc.Graph(
                                id="mapa-relaciones-graph",
                                config={
                                    'displayModeBar': True,
                                    'modeBarButtonsToRemove': [
                                        'zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                                        'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'
                                    ],
                                    'displaylogo': False
                                },
                            ),
                            style={"display": "flex", "justifyContent": "center"}
                        ),
                    ),
                ],
                style={"marginBottom": "30px"},
            ),

            # Sección de Histogramas y Tabla de Producción
            html.Div(
                className="container-col",
                id="histogramas-container",
                children=[
                    html.H4(""),
                    dcc.Loading(
                        type="circle",
                        children=[
                            dcc.Graph(id="histograma-graph1"),  # Primer gráfico: Boxplot

                            # Filtro de rango de fechas y botón de descarga
                            html.Div(
                                children=[
                                    dcc.DatePickerRange(
                                        id='date-range-picker',
                                        start_date_placeholder_text="Start Date",
                                        end_date_placeholder_text="End Date",
                                        display_format='DD-MM-YYYY',
                                    ),
                                ],
                                className="mb-4",
                                style={"display": "flex", "justify-content": "space-between"}
                            ),

                            # Tabla de Datos de Producción (qo, ql, BSW)
                            dash_table.DataTable(
                                id='qo-data-table',
                                columns=[
                                    {'name': 'Fecha', 'id': 'FECHA'},
                                    {'name': 'Tasa de Aceite (BOPD)', 'id': 'qo'},
                                    {'name': 'Tasa de Líquidos (BLPD)', 'id': 'ql'},
                                    {'name': 'BSW (%)', 'id': 'Wcut'}
                                ],
                                data=[],  # Los datos se actualizarán dinámicamente
                                page_size=10,  # Número de filas por página
                                style_table={'height': '300px', 'overflowY': 'auto'},  # Ajustes de tamaño de la tabla
                                style_cell={'textAlign': 'center'},  # Alinear texto en el centro
                            )
                        ],
                    ),
                ],
            ),
        ],
    )




# Callback para actualizar las opciones del dropdown de productores basado en la selección de inyector y ubicación
@app.callback(
    Output("dataset-dropdown-productor", "options"),
    [Input("dataset-dropdown-inyector_2", "value"),
     Input("ubicacion-dropdown", "value")],
    prevent_initial_call=True
)
def update_productor_dropdown(selected_inyector, selected_ubicacion):
    """
    Actualiza las opciones del dropdown de productores en función del inyector y la ubicación seleccionados.

    Args:
        selected_inyector (str): El inyector seleccionado.
        selected_ubicacion (str): La ubicación seleccionada (PL, SL, Ambos).

    Returns:
        list: Lista de diccionarios con las opciones de productores para el dropdown.
    """
    # Verificar si se ha seleccionado un inyector
    if not selected_inyector:
        return []

    # Filtrar las relaciones según el inyector seleccionado
    relaciones_filtradas = data_relacion[data_relacion['Inyector'] == selected_inyector]

    # Aplicar filtro adicional por ubicación seleccionada (PL, SL o Ambos)
    if selected_ubicacion == 'PL':
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Ubicación'] == 'PL']
    elif selected_ubicacion == 'SL':
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Ubicación'] == 'SL']

    # Extraer y limpiar la lista de productores asociados
    productores_asociados = relaciones_filtradas['Asociados'].str.split(',').explode().unique().tolist()

    # Generar las opciones para el dropdown de productores
    opciones_productores = [{'label': productor.strip(), 'value': productor.strip()} for productor in productores_asociados]

    return opciones_productores


@app.callback(
    [Output("mapa-relaciones-graph", "figure"), Output("qo-data-store", "data")],
    [Input("dataset-dropdown-inyector_2", "value"),
     Input("dataset-dropdown-productor", "value"),
     Input("ubicacion-dropdown", "value")],
    prevent_initial_call=False
)
def update_patron_rel(selected_inyectores, selected_productores, selected_ubicacion):
    """
    Actualiza el gráfico del mapa de relaciones y almacena los datos de Qo en el Store.

    Args:
        selected_inyectores (list): Lista de inyectores seleccionados en el dropdown.
        selected_productores (list): Lista de productores seleccionados en el dropdown.
        selected_ubicacion (str): Ubicación seleccionada (PL, SL o Ambos).

    Returns:
        tuple: Figura actualizada para el gráfico del mapa de relaciones y datos actualizados de Qo.
    """
    # Llamar a la función auxiliar `update_patron` que realiza la lógica principal
    # y pasa los datos necesarios.
    figura_mapa_relaciones, qo_data = update_patron(
        selected_inyectores, selected_productores, selected_ubicacion,
        data_relacion, mes, pwf, inyeccion_diaria
    )
    
    # Devolver la figura actualizada y los datos de Qo al Store
    return figura_mapa_relaciones, qo_data


@app.callback(
    [Output("histograma-graph1", "figure"), Output("qo-data-table", "data")],
    [Input("qo-data-store", "data"),
     Input('date-range-picker', 'start_date'),
     Input('date-range-picker', 'end_date')],
    prevent_initial_call=True
)
def update_histograma1_callback(qo_data, start_date, end_date):
    """
    Actualiza el gráfico del histograma y la tabla de datos de tasas de aceite (Qo) 
    basado en los datos almacenados y el rango de fechas seleccionado.

    Args:
        qo_data (list): Los datos de tasas de aceite almacenados.
        start_date (str): La fecha de inicio seleccionada en el selector de fechas.
        end_date (str): La fecha de fin seleccionada en el selector de fechas.

    Returns:
        tuple: Figura del histograma actualizada y datos para la tabla.
    """
    # Verificar si los datos de Qo están disponibles
    if not qo_data:
        return px.scatter(title="No data available"), []  # Devuelve un gráfico vacío y una tabla vacía si no hay datos

    # Llamar a la función `update_boxplot` para actualizar el gráfico y la tabla basados en el rango de fechas seleccionado
    return update_boxplot(qo_data, start_date, end_date)

