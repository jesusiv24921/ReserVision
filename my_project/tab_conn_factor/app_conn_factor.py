import dash
from dash import dash_table
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
from plotly.colors import qualitative
from app import app
import pandas as pd
from my_project.scripts.carga_datos import CargaDatos
from my_project.tab_behavior_patterns.graphs_behavior import (
    update_small_graph, 


)
from my_project.tab_conn_factor.conn_fact_func import normalize_column_by_group
from my_project.tab_conn_factor.graphs_conn_factor import create_first_graph_fc

from dtaidistance import dtw

# Se cargan los datos que serán utilizados a lo largo del programa
data_coordenadas = CargaDatos().data_cargar('coordenadas')
data_relacion = CargaDatos().data_cargar('relacion_iny_prod')

# Se identifican los inyectores y productores únicos a partir de los datos
inyectores = data_relacion['Inyector'].unique()
productores = data_relacion['Asociados'].str.split(',').explode().unique()

# Cargar los datos adicionales de controles diarios, datos estáticos y presiones de fondo (pwf)
controles_diarios = CargaDatos().data_cargar('controles_diarios')
data_estatica = CargaDatos().data_cargar('data_estatica')
pwf = CargaDatos().data_cargar('pwf')

# Se carga el conjunto de datos mensual de producción y se convierten las columnas a los tipos correctos
mes = CargaDatos().data_cargar('produccion_mes')
mes = mes.astype({'qo': 'int64', 'ql': 'int64', 'qw': 'int64', 'qwi': 'int64', 'dias': 'float64', 'pwi': 'int64', 'WOR': 'float64', 'Wcut': 'float64'})

# También se carga la data de inyección diaria
inyeccion_diaria = CargaDatos().data_cargar('inyeccion_diaria')

# Se asigna un color único a cada inyector usando una paleta de colores predefinida
color_palette = qualitative.Plotly
color_map = {inyector: color_palette[i % len(color_palette)] for i, inyector in enumerate(inyectores)}

def layout_conn():
    """Genera la estructura visual de la página, que incluye los filtros y gráficos.

    La página contiene filtros para seleccionar inyectores, productores, unidades, 
    ubicación (PL o SL), así como un selector de fecha. Incluye gráficos que se 
    actualizan dinámicamente según los filtros aplicados y una tabla que muestra 
    las distancias DTW.
    """
    return html.Div(
        className="container-row full-width",
        children=[
            # Contenedor para almacenar valores seleccionados (inyectores, productores)
            dcc.Store(id='stored-filters-conn', storage_type='session'),
            dcc.Store(id='associated-producers-conn', storage_type='memory'),
            dcc.Store(id='stored-filters-ql-conn', storage_type='session'),

            # Columna izquierda: filtros y gráficos pequeños
            dbc.Col(
                width=3,
                children=[
                    html.Div(
                        className="container-col",
                        children=[
                            html.H5("Filtro de Inyector"),
                            dcc.Dropdown(
                                id="dropdown-inyector-conn",
                                options=[{'label': inyector, 'value': inyector} for inyector in inyectores],
                                placeholder="Seleccione Inyector",
                                multi=True,
                                persistence=True,
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            html.H5("Filtro de PL o SL"),
                            dcc.Dropdown(
                                id="dropdown-pl-sl-conn",
                                options=[
                                    {"label": "PL", "value": "PL"},
                                    {"label": "SL", "value": "SL"},
                                    {"label": "Ambos", "value": "Ambos"}
                                ],
                                value="Ambos",
                                persistence=True,
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            html.H5("Filtro de Productor"),
                            dcc.Dropdown(
                                id="dropdown-productor-conn",
                                options=[],
                                placeholder="Seleccione Productor",
                                multi=True,
                                searchable=True,
                                persistence=True,
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            html.H5("Seleccione Unidad"),
                            dcc.Dropdown(
                                id="dropdown-unidad-conn",
                                options=[{'label': unidad, 'value': unidad} for unidad in data_coordenadas['UNIDAD'].unique()],
                                placeholder="Seleccione Unidad",
                                multi=False,
                                persistence=True,
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            # Selector de rango de fechas
                            html.H5("Seleccione Fecha"),
                            dcc.DatePickerRange(
                                id='date-picker-conn',
                                min_date_allowed=pd.to_datetime('2020-01-01'),
                                max_date_allowed=pd.to_datetime('2024-12-31'),
                                initial_visible_month=pd.to_datetime('2024-01-01'),
                                start_date=None,
                                end_date=None,
                                persistence=True,
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                        ],
                    ),
                    # Pequeño gráfico que se actualiza según los filtros
                    html.Div(
                        className="small-graph-container",
                        children=[
                            dcc.Graph(
                                id="small-graph-conn",
                                config={
                                    "displayModeBar": True,
                                    "displaylogo": False,
                                    'modeBarButtonsToRemove': [
                                        'zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                                        'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'
                                    ],
                                }
                            ),
                        ],
                    ),
                ],
                style={"margin-right": "10px"}
            ),

            # Columna derecha: gráficos principales y tabla de distancias DTW
            dbc.Col(
                width=9,
                children=[
                    # Primera fila: Gráfico principal
                    dbc.Row(
                        children=[
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="graph-1-conn",
                                        config={
                                            "displayModeBar": True,
                                            "displaylogo": False,
                                            'modeBarButtonsToRemove': [
                                                'zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                                                'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'
                                            ],
                                        },
                                        style={"height": "450px"}
                                    ),
                                    style={"border": "1.5px solid #000", "padding": "0px"}
                                ),
                                width=12,
                            ),
                        ],
                        style={"margin-bottom": "15px"}
                    ),

                    # Tabla para mostrar las distancias DTW calculadas
                    dash_table.DataTable(
                        id='dtw-table-conn',
                        columns=[
                            {'name': 'Productor', 'id': 'Productor'},
                            {'name': 'Inyector', 'id': 'Inyector'},
                            {'name': 'Distancia DTW', 'id': 'Distancia DTW'}
                        ],
                        data=[],
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'center',
                            'padding': '10px',
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        style_header={
                            'backgroundColor': '#f8f9fa',
                            'fontWeight': 'bold',
                            'textAlign': 'center',
                        },
                        style_data_conditional=[
                            {
                                'if': {'column_id': 'Productor'},
                                'textAlign': 'center',
                            },
                            {
                                'if': {'column_id': 'Inyector'},
                                'textAlign': 'center',
                            },
                            {
                                'if': {'column_id': 'Distancia DTW'},
                                'textAlign': 'center',
                            }
                        ],
                        style_as_list_view=True
                    )
                ]
            ),
        ]
    )


# Callback para generar los valores DTW y actualizar la tabla DTW
@app.callback(
    Output('dtw-table-conn', 'data'),
    [
        Input('dropdown-inyector-conn', 'value'),
        Input('dropdown-productor-conn', 'value'),
        Input('date-picker-conn', 'start_date'),
        Input('date-picker-conn', 'end_date'),
        Input('stored-filters-conn', 'data')
    ]
)
def update_dtw_table(selected_inyectores, selected_productores, start_date, end_date, stored_filters):
    """
    Actualiza la tabla de distancias DTW (Dynamic Time Warping) basadas en los inyectores, 
    productores y fechas seleccionadas. Las distancias se calculan para cada par de inyector 
    y productor con datos normalizados.

    Args:
        selected_inyectores (list): Lista de inyectores seleccionados por el usuario.
        selected_productores (list): Lista de productores seleccionados por el usuario.
        start_date (str): Fecha de inicio seleccionada en el rango de fechas.
        end_date (str): Fecha de fin seleccionada en el rango de fechas.
        stored_filters (dict): Filtros almacenados en la sesión (no utilizado directamente aquí).

    Returns:
        list[dict]: Una lista de diccionarios donde cada uno contiene los valores de 'Inyector', 
        'Productor' y la distancia DTW normalizada correspondiente. Si no se encuentran datos, 
        se devuelve una lista vacía.
    """

    # Verificar que los filtros necesarios estén seleccionados
    if not selected_inyectores or not selected_productores or not start_date or not end_date:
        return []

    # Filtrar los datos de inyección por inyector y fechas seleccionadas
    mes_inyector = mes[(mes['IDENTIFICADOR'].isin(selected_inyectores)) & 
                       (mes['FECHA'] >= pd.to_datetime(start_date)) & 
                       (mes['FECHA'] <= pd.to_datetime(end_date))]

    # Filtrar los datos de producción por productor y fechas seleccionadas
    filtered_data = mes[(mes['IDENTIFICADOR'].isin(selected_productores)) & 
                        (mes['FECHA'] >= pd.to_datetime(start_date)) & 
                        (mes['FECHA'] <= pd.to_datetime(end_date))]

    # Normalizar los datos de inyección y producción por grupo
    mes_inyector_norm = normalize_column_by_group(mes_inyector, 'IDENTIFICADOR', 'qwi')
    filtered_data_norm = normalize_column_by_group(filtered_data, 'IDENTIFICADOR', 'ql')

    # Inicializar la lista para almacenar los puntajes DTW
    dtw_scores = []
    
    # Iterar sobre cada combinación de productor e inyector para calcular la distancia DTW
    for productor in selected_productores:
        for inyector in selected_inyectores:
            # Extraer las series de datos normalizadas para productor e inyector
            serie_prod = filtered_data_norm[filtered_data_norm['IDENTIFICADOR'] == productor]['ql_norm'].values
            serie_iny = mes_inyector_norm[mes_inyector_norm['IDENTIFICADOR'] == inyector]['qwi_norm'].values

            # Verificar que ambas series tengan valores antes de calcular DTW
            if len(serie_prod) > 0 and len(serie_iny) > 0:
                # Calcular la distancia DTW entre las series normalizadas
                distancia = dtw.distance(serie_prod, serie_iny)
                
                # Agregar los resultados a la lista
                dtw_scores.append({
                    'Inyector': inyector,
                    'Productor': productor,
                    'Distancia DTW': distancia
                })
            else:
                print(f"Una de las series de {inyector} o {productor} está vacía.")
    
    # Devolver la lista de puntajes DTW normalizados
    if not dtw_scores:
        return []

    # Convertir los resultados a un DataFrame
    matriz_dtw = pd.DataFrame(dtw_scores)

    # Normalizar las distancias DTW utilizando Min-Max scaling
    min_dtw = matriz_dtw['Distancia DTW'].min()
    max_dtw = matriz_dtw['Distancia DTW'].max()
    matriz_dtw['Distancia DTW'] = (matriz_dtw['Distancia DTW'] - min_dtw) / (max_dtw - min_dtw)

    # Redondear las distancias DTW a dos decimales para mejorar la legibilidad
    matriz_dtw['Distancia DTW'] = matriz_dtw['Distancia DTW'].round(2)

    # Devolver los datos de la tabla en formato de diccionario
    return matriz_dtw.to_dict('records')




# Callback para actualizar el dropdown de productores según los filtros seleccionados
@app.callback(
    [Output('dropdown-productor-conn', 'options'),
     Output('dropdown-productor-conn', 'value')],
    [
        Input('dropdown-inyector-conn', 'value'),
        Input('dropdown-pl-sl-conn', 'value'),
        Input('dropdown-unidad-conn', 'value')
    ]
)
def update_productores_dropdown_conn(selected_inyectores, selected_pl_sl, selected_unidad):
    """
    Actualiza las opciones disponibles y los valores seleccionados en el dropdown de productores 
    en función de los filtros de inyector, ubicación (PL/SL), y unidad seleccionados por el usuario.

    Args:
        selected_inyectores (list): Lista de inyectores seleccionados por el usuario.
        selected_pl_sl (str): Filtro de ubicación (PL/SL/Ambos) seleccionado por el usuario.
        selected_unidad (str): Unidad seleccionada en el filtro de unidad.

    Returns:
        tuple: Devuelve una lista de opciones para el dropdown de productores, 
        y una lista de valores seleccionados. Si no se encuentran datos, devuelve opciones vacías.
    """

    # Si no se seleccionan inyectores, utilizar todos los inyectores disponibles
    if not selected_inyectores:
        selected_inyectores = data_relacion['Inyector'].unique()

    # Filtrar las relaciones por los inyectores seleccionados
    relaciones_filtradas = data_relacion[data_relacion['Inyector'].isin(selected_inyectores)]

    # Filtrar las relaciones por la ubicación (PL/SL) si se ha seleccionado un valor diferente de 'Ambos'
    if selected_pl_sl and selected_pl_sl != 'Ambos':
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Ubicación'] == selected_pl_sl]

    # Filtrar las relaciones por unidad si se ha seleccionado una unidad específica
    if selected_unidad:
        # Obtener los productores asociados a la unidad seleccionada
        productores_en_unidad = data_coordenadas[
            (data_coordenadas['TIPO'] == 'productor') & (data_coordenadas['UNIDAD'] == selected_unidad)
        ]['POZO'].unique()
        
        # Filtrar las relaciones basadas en los productores que están en la unidad seleccionada
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Asociados'].isin(productores_en_unidad)]

    # Extraer la lista de productores asociados desde las relaciones filtradas
    productores_asociados = relaciones_filtradas['Asociados'].str.split(',').explode().unique()

    # Crear las opciones del dropdown a partir de los productores asociados
    dropdown_options = [{'label': productor.strip(), 'value': productor.strip()} for productor in productores_asociados]

    # Devolver las opciones del dropdown y los valores seleccionados (inicialmente vacío)
    return dropdown_options, list(productores_asociados)

# Callback para utilizar en el filtro de fechas el rango mínimo y máximo basado en el inyector seleccionado
@app.callback(
    [Output('date-picker-conn', 'start_date'),
     Output('date-picker-conn', 'end_date')],
    Input('dropdown-inyector-conn', 'value')
)
def update_date_picker_range(selected_inyectores):
    """
    Actualiza el rango de fechas del selector de fechas basado en los inyectores seleccionados.
    Filtra las fechas de inyección diaria y establece los valores mínimos y máximos del rango de fechas.

    Args:
        selected_inyectores (list): Lista de inyectores seleccionados por el usuario en el dropdown.

    Returns:
        tuple: Una tupla con las fechas mínima (start_date) y máxima (end_date) de los inyectores seleccionados. 
               Si no se selecciona ningún inyector, devuelve (None, None).
    """
    if selected_inyectores:
        # Filtrar los datos según los inyectores seleccionados
        inyeccion_diaria_filtrada = inyeccion_diaria[inyeccion_diaria['IDENTIFICADOR'].isin(selected_inyectores)]
        
        # Obtener las fechas mínima y máxima
        fecha_ini = inyeccion_diaria_filtrada['FECHA'].min()
        fecha_max = inyeccion_diaria_filtrada['FECHA'].max()
        
        # Retornar el rango de fechas basado en los inyectores seleccionados
        return fecha_ini, fecha_max
    return None, None  # Retornar None si no hay inyectores seleccionados



# Callback para traer los gráficos en base a los filtros seleccionados
@app.callback(
    [
        Output("small-graph-conn", "figure"),
        Output("graph-1-conn", "figure")
    ],
    [
        Input('stored-filters-conn', 'data'),
        Input('dropdown-unidad-conn', 'value'),  # Filtro de unidad
        Input('dropdown-inyector-conn', 'value'),  # Filtro de inyector
        Input('dropdown-productor-conn', 'value'),  # Filtro de productor
        Input('date-picker-conn', 'start_date'),  # Filtro de fecha inicial
        Input('date-picker-conn', 'end_date')  # Filtro de fecha final
    ]
)
def update_graphs_conn(stored_filters, selected_unidad, selected_inyectores, selected_productores, start_date, end_date):
    """
    Actualiza los gráficos basados en los filtros seleccionados por el usuario.
    
    Se generan gráficos usando los datos filtrados por unidad, inyector, productor y rango de fechas. 
    Si no se seleccionan valores adecuados, se devuelven gráficos vacíos.

    Args:
        stored_filters (dict): Diccionario que contiene los filtros almacenados previamente, como PL/SL.
        selected_unidad (str): Unidad seleccionada por el usuario.
        selected_inyectores (list): Lista de inyectores seleccionados por el usuario en el dropdown.
        selected_productores (list): Lista de productores seleccionados por el usuario en el dropdown.
        start_date (str): Fecha de inicio seleccionada por el usuario en el rango de fechas.
        end_date (str): Fecha de finalización seleccionada por el usuario en el rango de fechas.

    Returns:
        list: Lista con dos gráficos de Plotly: el gráfico pequeño ("small-graph-conn") y el gráfico principal ("graph-1-conn").
              Si no se seleccionan inyectores o productores, devuelve gráficos vacíos.
    """
    
    # Si no hay filtros almacenados, se inicializan por defecto
    if stored_filters is None:
        stored_filters = {'pl_sl': 'Ambos'}
    
    # Verificar si no hay inyectores seleccionados
    if not selected_inyectores:
        empty_fig = px.scatter(title="Seleccione un inyector")
        return [empty_fig, empty_fig]

    # Verificar si no hay productores seleccionados
    if not selected_productores:
        empty_fig = px.scatter(title="Seleccione un productor")
        return [empty_fig, empty_fig]

    # Si no se seleccionan fechas, se toman las fechas mínimas y máximas disponibles
    if not start_date or not end_date:
        start_date = mes['FECHA'].min()
        end_date = mes['FECHA'].max()

    # Filtrar los datos de acuerdo a los inyectores y fechas seleccionados
    mes_inyector = mes[(mes['IDENTIFICADOR'].isin(selected_inyectores)) & 
                       (mes['FECHA'] >= pd.to_datetime(start_date)) & 
                       (mes['FECHA'] <= pd.to_datetime(end_date))]

    # Filtrar los datos de acuerdo a los productores y fechas seleccionados
    filtered_data = mes[(mes['IDENTIFICADOR'].isin(selected_productores)) & 
                        (mes['FECHA'] >= pd.to_datetime(start_date)) & 
                        (mes['FECHA'] <= pd.to_datetime(end_date))]

    # Si los DataFrames están vacíos, retornar gráficos vacíos
    if mes_inyector.empty or filtered_data.empty:
        empty_fig = px.scatter(title="No hay datos disponibles para los filtros seleccionados")
        return [empty_fig, empty_fig]

    # Generar el gráfico pequeño basado en los datos filtrados y los filtros aplicados
    fig_small_graph = update_small_graph(selected_inyectores, stored_filters.get('pl_sl', 'Ambos'), selected_productores, data_relacion, data_coordenadas)
    
    # Generar el gráfico principal basado en los datos filtrados
    fig_graph_1 = create_first_graph_fc(selected_productores, filtered_data, mes_inyector)

    return [fig_small_graph, fig_graph_1]


# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)