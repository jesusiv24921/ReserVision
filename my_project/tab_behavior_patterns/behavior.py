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
    create_first_graph, create_second_graph, create_third_graph, 
    create_four_graph, create_five_graph, create_six_graph, create_qo_ql_graph
)


# Cargar los datos requeridos desde los archivos correspondientes
data_coordenadas = CargaDatos().data_cargar('coordenadas')
data_relacion = CargaDatos().data_cargar('relacion_iny_prod')

# Extraer los valores únicos de inyectores y productores
inyectores = data_relacion['Inyector'].unique()
productores = data_relacion['Asociados'].str.split(',').explode().unique()

controles_diarios = CargaDatos().data_cargar('controles_diarios')
data_estatica = CargaDatos().data_cargar('data_estatica')
pwf = CargaDatos().data_cargar('pwf')

# Asignar colores a cada inyector utilizando una paleta de colores
color_palette = qualitative.Plotly
color_map = {inyector: color_palette[i % len(color_palette)] for i, inyector in enumerate(inyectores)}

def layout_injection_pattern():
    """
    Genera el layout principal de la página que contiene los filtros de selección y gráficos.
    
    La página incluye filtros para seleccionar inyectores, productores, PL/SL, unidades y fechas. También se configuran
    gráficos pequeños que se actualizan dinámicamente según los filtros aplicados.
    
    Returns:
        html.Div: Layout de la página con los filtros y gráficos distribuidos en columnas.
    """
    return html.Div(
        className="container-row full-width",
        children=[
            # Almacenar los valores seleccionados en un dcc.Store para los filtros
            dcc.Store(id='stored-filters', storage_type='session'),
            dcc.Store(id='associated-producers', storage_type='memory'),  # Almacenar productores asociados
            dcc.Store(id='stored-filters-ql', storage_type='session'),

            # Primera columna con los filtros y gráficos pequeños
            dbc.Col(
                width=3,
                children=[
                    # Filtros de selección
                    html.Div(
                        className="container-col",
                        children=[
                            html.H5("Filtro de Inyector"),
                            dcc.Dropdown(
                                id="dropdown-inyector",
                                options=[{'label': inyector, 'value': inyector} for inyector in inyectores],
                                placeholder="Seleccione Inyector",
                                multi=True,
                                persistence=True,  # Mantener los valores seleccionados
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            html.H5("Filtro de PL o SL"),
                            dcc.Dropdown(
                                id="dropdown-pl-sl",
                                options=[
                                    {"label": "PL", "value": "PL"},
                                    {"label": "SL", "value": "SL"},
                                    {"label": "Ambos", "value": "Ambos"}
                                ],
                                value="Ambos",  # Valor por defecto
                                persistence=True,  # Mantener los valores seleccionados
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            html.H5("Filtro de Productor"),
                            dcc.Dropdown(
                                id="dropdown-productor",
                                options=[],  # Opciones dinámicas
                                placeholder="Seleccione Productor",
                                multi=True,
                                persistence=True,
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            html.H5("Seleccione Unidad"),
                            dcc.Dropdown(
                                id="dropdown-unidad",
                                options=[{'label': unidad, 'value': unidad} for unidad in data_coordenadas['UNIDAD'].unique()],
                                placeholder="Seleccione Unidad",
                                multi=False,
                                persistence=True,  # Mantener los valores seleccionados
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                            # Selector de fecha
                            html.H5("Seleccione Fecha"),
                            dcc.DatePickerSingle(
                                id='date-picker',
                                min_date_allowed=pd.to_datetime('2020-01-01'),
                                max_date_allowed=pd.to_datetime('2024-12-31'),
                                initial_visible_month=pd.to_datetime('2024-01-01'),
                                date=None,  # Sin fecha seleccionada por defecto
                                persistence=True,  # Mantener los valores seleccionados
                                persistence_type='session',
                                className="mt-2 mb-2"
                            ),
                        ],
                    ),
                    # Gráfico pequeño que se actualiza según los filtros
                    html.Div(
                        className="small-graph-container",
                        children=[
                            dcc.Graph(
                                id="small-graph",
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
                    # Filtro adicional para seleccionar productores para el gráfico de Qo y Ql
                    html.H5("Seleccione Productores para Qo y Ql"),
                    dcc.Dropdown(
                        id="dropdown-productores-ql-graph",
                        options=[],  # Opciones dinámicas
                        placeholder="Seleccione Productores",
                        multi=True,
                        className="mt-2 mb-2"
                    ),
                    # Gráfico de Qo y Ql en función de los productores seleccionados
                    html.Div(
                        className="small-graph-container",
                        children=[
                            dcc.Graph(
                                id="small-graph1",
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
            # Segunda columna: gráficos principales en varias filas
            dbc.Col(
                width=9,  # Ajusta el ancho de la segunda columna
                children=[
                    # Primera fila de gráficos
                    dbc.Row(
                        children=[
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="graph-1",
                                        config={
                                            "displayModeBar": True,
                                            "displaylogo": False,  # Elimina el logo de Plotly
                                            'modeBarButtonsToRemove': [
                                                'zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d',
                                                'autoScale2d', 'toggleSpikelines', 'hoverClosestCartesian', 'hoverCompareCartesian'
                                            ],
                                        },
                                        style={"height": "450px"}
                                    ),
                                    style={"border": "1.5px solid #000", "padding": "0px"}  # Agregar borde y padding
                                ),
                                width=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="graph-2",
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
                                width=6,
                            ),
                        ],
                        style={"margin-bottom": "15px"}  # Añadir margen inferior para separar filas
                    ),
                    # Otras filas de gráficos
                    dbc.Row(
                        children=[
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="graph-3",
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
                                width=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="graph-4",
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
                                width=6,
                            ),
                        ],
                        style={"margin-bottom": "15px"}
                    ),
                    # Tercera fila de gráficos
                    dbc.Row(
                        children=[
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="graph-5",
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
                                width=6,
                            ),
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(
                                        id="graph-6",
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
                                width=6,
                            ),
                        ],
                        style={"margin-bottom": "15px"}
                    ),
                ],
            ),
        ],
    )

# Callback para actualizar el dropdown de productores según los filtros seleccionados
@app.callback(
    [Output('dropdown-productor', 'options'),
     Output('dropdown-productor', 'value')],
    [
        Input('dropdown-inyector', 'value'),
        Input('dropdown-pl-sl', 'value'),
        Input('dropdown-unidad', 'value')
    ]
)
def update_productores_dropdown(selected_inyectores, selected_pl_sl, selected_unidad):
    """
    Actualiza las opciones del dropdown de productores según los filtros seleccionados de inyector, PL/SL y unidad.
    
    Si no se seleccionan inyectores, se utiliza la lista completa de inyectores disponibles. 
    Luego, las relaciones se filtran por los inyectores seleccionados y, si corresponde, 
    por la ubicación PL/SL y la unidad. Finalmente, se genera una lista de productores asociados 
    basada en las relaciones filtradas.
    
    Args:
        selected_inyectores (list): Lista de inyectores seleccionados.
        selected_pl_sl (str): Filtro de ubicación PL, SL o Ambos.
        selected_unidad (str): Unidad seleccionada para filtrar productores.

    Returns:
        list: Opciones del dropdown de productores.
        list: Valores seleccionados para el dropdown de productores.
    """
    
    # Si no se seleccionan inyectores, usar todos los disponibles
    if not selected_inyectores:
        selected_inyectores = data_relacion['Inyector'].unique()

    # Filtrar las relaciones según los inyectores seleccionados
    relaciones_filtradas = data_relacion[data_relacion['Inyector'].isin(selected_inyectores)]

    # Filtrar por PL/SL si está seleccionado un valor diferente de 'Ambos'
    if selected_pl_sl and selected_pl_sl != 'Ambos':
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Ubicación'] == selected_pl_sl]

    # Filtrar por unidad si se ha seleccionado una
    if selected_unidad:
        productores_en_unidad = data_coordenadas[
            (data_coordenadas['TIPO'] == 'productor') & (data_coordenadas['UNIDAD'] == selected_unidad)
        ]['POZO'].unique()
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Asociados'].isin(productores_en_unidad)]

    # Extraer y organizar los productores asociados
    productores_asociados = relaciones_filtradas['Asociados'].str.split(',').explode().unique()

    # Generar las opciones para el dropdown de productores
    dropdown_options = [{'label': productor.strip(), 'value': productor.strip()} for productor in productores_asociados]

    # Retornar las opciones generadas y la lista de productores seleccionados
    return dropdown_options, list(productores_asociados)


# Callback para guardar los productores seleccionados para el gráfico de Qo y Ql
@app.callback(
    Output('stored-filters-ql', 'data'),
    Input("dropdown-productores-ql-graph", "value"),
    prevent_initial_call=True
)
def store_selected_productores_ql(selected_productores_ql):
    """
    Almacena los productores seleccionados para el gráfico de Qo y Ql en un almacenamiento de sesión.
    
    Este callback se activa cuando se seleccionan productores en el dropdown correspondiente y guarda 
    estos valores en el almacenamiento de sesión para ser utilizados posteriormente en la restauración.

    Args:
        selected_productores_ql (list): Lista de productores seleccionados.

    Returns:
        dict: Un diccionario con los productores seleccionados almacenados.
    """
    # Almacenar los productores seleccionados en un diccionario para su uso posterior
    return {'selected_productores_ql': selected_productores_ql}


# Callback para restaurar los productores seleccionados para el gráfico de Qo y Ql
@app.callback(
    Output("dropdown-productores-ql-graph", "value"),
    Input('stored-filters-ql', 'data')
)
def restore_selected_productores_ql(stored_data):
    """
    Restaura los productores previamente seleccionados para el gráfico de Qo y Ql a partir de los datos almacenados.
    
    Este callback se encarga de recuperar los valores guardados de los productores seleccionados en el almacenamiento 
    de sesión y los vuelve a establecer en el dropdown de selección de productores.

    Args:
        stored_data (dict): Diccionario con los productores previamente seleccionados almacenados.

    Returns:
        list: La lista de productores previamente seleccionados o una lista vacía si no hay datos almacenados.
    """
    # Verificar si existen datos almacenados y devolverlos, de lo contrario devolver una lista vacía
    if stored_data:
        return stored_data.get('selected_productores_ql', [])
    return []


# Callback para actualizar todos los gráficos según los filtros aplicados
@app.callback(
    [
        Output("small-graph", "figure"),
        Output("graph-1", "figure"),
        Output("graph-2", "figure"),
        Output("graph-3", "figure"),
        Output("graph-4", "figure"),
        Output("graph-5", "figure"),
        Output("graph-6", "figure"),
    ],
    [
        Input('stored-filters', 'data'),
        Input('dropdown-unidad', 'value'),  # Filtro de unidad
        Input('dropdown-inyector', 'value'),  # Filtro de inyector
        Input('dropdown-productor', 'value'),  # Filtro de productor
        Input('date-picker', 'date')  # Filtro de fecha
    ]
)
def update_graphs(stored_filters, selected_unidad, selected_inyectores, selected_productores, selected_date):
    """
    Actualiza todos los gráficos principales en función de los filtros seleccionados.

    Este callback se encarga de recibir los filtros aplicados por el usuario (inyectores, productores, unidad y fecha) 
    y luego ajusta los gráficos correspondientes para reflejar los datos filtrados.

    Args:
        stored_filters (dict): Filtros almacenados, como PL/SL seleccionado.
        selected_unidad (str): La unidad seleccionada por el usuario.
        selected_inyectores (list): Lista de inyectores seleccionados.
        selected_productores (list): Lista de productores seleccionados.
        selected_date (str): Fecha seleccionada para filtrar los datos.

    Returns:
        list: Lista de figuras de gráficos actualizados para cada componente de la interfaz.
    """

    # Verificar si no hay filtros almacenados y asignar valores por defecto si es necesario
    if stored_filters is None:
        stored_filters = {'pl_sl': 'Ambos'}  # Valor por defecto si no se han almacenado filtros

    # Verificar si se han seleccionado inyectores y productores; si no, mostrar gráficos vacíos
    if not selected_inyectores or not selected_productores:
        empty_fig = px.scatter(title="Seleccione los filtros para visualizar los datos")
        return [empty_fig] * 7  # Devuelve gráficos vacíos para todas las salidas

    # Filtrar relaciones por inyectores seleccionados
    relaciones_filtradas = data_relacion[data_relacion['Inyector'].isin(selected_inyectores)]
    
    # Filtrar por PL/SL si está especificado en los filtros almacenados
    if stored_filters.get('pl_sl') != 'Ambos':
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Ubicación'] == stored_filters.get('pl_sl')]

    # Filtrar por unidad seleccionada, si aplica
    if selected_unidad:
        productores_en_unidad = data_coordenadas[
            (data_coordenadas['TIPO'] == 'productor') & (data_coordenadas['UNIDAD'] == selected_unidad)
        ]['POZO'].unique()
        relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Asociados'].isin(productores_en_unidad)]

    # Filtrar los controles diarios por los productores seleccionados
    filtered_data = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]
    
    # Filtrar por la fecha seleccionada, si existe
    if selected_date:
        selected_date = pd.to_datetime(selected_date)
        filtered_data = filtered_data[filtered_data['FECHA'] <= selected_date]

    # Actualizar los gráficos utilizando los datos filtrados
    fig_small_graph = update_small_graph(selected_inyectores, stored_filters.get('pl_sl', 'Ambos'), selected_productores, data_relacion, data_coordenadas)
    fig_graph_1 = create_first_graph(selected_productores, controles_diarios, selected_date, data_estatica)
    fig_graph_2 = create_second_graph(selected_productores, controles_diarios, selected_date, data_estatica)
    fig_graph_3 = create_third_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf)
    fig_graph_4 = create_four_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf)
    fig_graph_5 = create_five_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf)
    fig_graph_6 = create_six_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf)

    # Retornar las figuras de los gráficos actualizados
    return [fig_small_graph, fig_graph_1, fig_graph_2, fig_graph_3, fig_graph_4, fig_graph_5, fig_graph_6]



# Callback para actualizar el dropdown de productores para el gráfico de Qo y Ql
@app.callback(
    Output('dropdown-productores-ql-graph', 'options'),
    [Input('dropdown-inyector', 'value')]
)
def update_productores_ql_dropdown(selected_inyectores):
    """
    Actualiza el dropdown de productores utilizado en el gráfico de Qo y Ql.

    La función recibe el inyector seleccionado y filtra los productores asociados a dicho inyector. 
    Si no hay inyector seleccionado, se listan todos los productores disponibles.

    Args:
        selected_inyectores (list): Lista de inyectores seleccionados.

    Returns:
        list: Opciones del dropdown en formato [{'label': productor, 'value': productor}].
    """
    if not selected_inyectores:
        # Si no hay inyectores seleccionados, se muestran todos los productores
        all_productores = data_relacion['Asociados'].str.split(',').explode().unique()
        return [{'label': productor.strip(), 'value': productor.strip()} for productor in all_productores]

    # Filtrar las relaciones para obtener solo los productores asociados a los inyectores seleccionados
    relaciones_filtradas = data_relacion[data_relacion['Inyector'].isin(selected_inyectores)]
    productores_asociados = relaciones_filtradas['Asociados'].str.split(',').explode().unique()

    # Generar las opciones del dropdown basadas en los productores filtrados
    return [{'label': productor.strip(), 'value': productor.strip()} for productor in productores_asociados]


# Callback para actualizar el gráfico de Qo y Ql según los productores seleccionados
@app.callback(
    Output("small-graph1", "figure"),
    Input("dropdown-productores-ql-graph", "value")
)
def update_ql_graph(selected_productores):
    """
    Actualiza el gráfico de Qo y Ql en función de los productores seleccionados.

    La función recibe una lista de productores seleccionados y filtra los datos de producción 
    diarios para generar un gráfico con las series temporales de Qo y Ql. Si no hay productores seleccionados,
    se muestra un gráfico vacío con un mensaje adecuado.

    Args:
        selected_productores (list): Lista de productores seleccionados por el usuario.

    Returns:
        plotly.graph_objs.Figure: Gráfico de líneas o dispersión que muestra Qo y Ql según los productores seleccionados.
    """
    # Verificar si no se seleccionaron productores y devolver un gráfico vacío con un mensaje
    if not selected_productores:
        return px.scatter(title="Seleccione un productor para ver el gráfico")

    # Filtrar los datos de controles diarios para los productores seleccionados
    filtered_data = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]

    # Verificar si los datos filtrados están vacíos
    if filtered_data.empty:
        return px.scatter(title="No hay datos disponibles para los productores seleccionados")

    # Asegurarse de que la columna FECHA esté en formato datetime
    filtered_data['FECHA'] = pd.to_datetime(filtered_data['FECHA'], errors='coerce')

    # Crear el gráfico de Qo y Ql utilizando la función auxiliar 'create_qo_ql_graph'
    fig_graph = create_qo_ql_graph(filtered_data)

    # Retornar el gráfico generado
    return fig_graph



# Ejecutar la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)
