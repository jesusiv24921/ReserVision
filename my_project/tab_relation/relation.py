import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import html, dcc
import plotly.express as px
import plotly.graph_objs as go
from plotly.colors import qualitative

from app import app
from my_project.scripts.carga_datos import CargaDatos

# Se cargan los datos necesarios desde la clase CargaDatos
# Se incluyen datos de coordenadas y relaciones entre inyectores y productores
data_coordenadas = CargaDatos().data_cargar('coordenadas')
data_relacion = CargaDatos().data_cargar('relacion_iny_prod')

# Extraemos las listas únicas de inyectores y productores a partir de los datos cargados
inyectores = data_relacion['Inyector'].unique()
productores = data_relacion['Asociados'].str.split(',').explode().unique()

# Se genera un mapeo de colores para los inyectores, utilizando la paleta cualitativa de Plotly
color_palette = qualitative.Plotly
color_map = {inyector: color_palette[i % len(color_palette)] for i, inyector in enumerate(inyectores)}

def layout_select():
    """Genera la estructura visual para la pestaña 'Seleccionar Datos'. 
    Esta pestaña incluye los dropdowns para seleccionar inyectores, productores, y ubicaciones, 
    así como un gráfico interactivo con leyendas que se actualiza dinámicamente.
    """
    return html.Div(
        className="container-col tab-container",
        style={"height": "100vh", "backgroundColor": "#f0f0f0"},  # Establece altura completa y fondo gris claro
        children=[
            # Almacenamiento en sesión para las selecciones realizadas en los dropdowns
            dcc.Store(id='dropdown-value-store-inyector', storage_type='session'),
            dcc.Store(id='dropdown-value-store-productor', storage_type='session'),
            dcc.Store(id='dropdown-value-store-ubicacion', storage_type='session'),

            # Contenedor principal con tres dropdowns: ubicación, inyector y productor
            html.Div(
                className="mt-2 mb-4 d-flex justify-content-between",
                children=[
                    html.Div(
                        children=[
                            # Dropdown para seleccionar la ubicación (PL, SL o ambos)
                            dcc.Dropdown(
                                id="ubicacion-dropdown",
                                options=[
                                    {'label': 'PL', 'value': 'PL'},
                                    {'label': 'SL', 'value': 'SL'},
                                    {'label': 'Ambos', 'value': 'Ambos'}
                                ],
                                value='Ambos',  # Valor por defecto
                                placeholder="Seleccione Ubicación",
                                className="mt-2 mb-2"
                            ),
                        ],
                        style={"width": "30%"},
                    ),
                    html.Div(
                        children=[
                            # Dropdown para seleccionar los inyectores (permite selección múltiple)
                            dcc.Dropdown(
                                id="dataset-dropdown-inyector",
                                options=[{'label': inyector, 'value': inyector} for inyector in inyectores],
                                placeholder="Seleccione Inyector",
                                multi=True,
                                className="mt-2 mb-2"
                            ),
                        ],
                        style={"width": "30%"},
                    ),
                    html.Div(
                        children=[
                            # Dropdown para seleccionar los productores (permite selección múltiple y es buscable)
                            dcc.Dropdown(
                                id="dataset-dropdown-productor",
                                options=[{'label': productor.strip(), 'value': productor.strip()} for productor in productores],
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

            # Leyenda que muestra el significado de las líneas continuas y discontínuas (declarado/no declarado)
            html.Div(
                className="legend-container",
                style={"display": "flex", "justify-content": "center", "margin-bottom": "10px"},
                children=[
                    html.Div(
                        style={"display": "flex", "align-items": "center", "margin-right": "20px"},
                        children=[
                            # Leyenda para líneas discontinuas (declarado)
                            html.Div(
                                style={"width": "40px", "height": "0px", "border-top": "3px dashed black", "margin-right": "8px"}
                            ),
                            html.Span("Declarado")
                        ]
                    ),
                    html.Div(
                        style={"display": "flex", "align-items": "center"},
                        children=[
                            # Leyenda para líneas continuas (no declarado)
                            html.Div(
                                style={
                                    "width": "40px", 
                                    "height": "0px", 
                                    "background-color": "black", 
                                    "border-top": "3px solid black", 
                                    "margin-right": "8px"
                                }
                            ),
                            html.Span("No Declarado")
                        ]
                    ),
                ]
            ),

            # Gráfico que representa los pozos e inyectores, configurado para ser interactivo
            dcc.Graph(
                id="petroleo-graph",
                config={
                    "displayModeBar": True,
                    "scrollZoom": True,  # Habilita zoom mediante scroll del mouse
                    "modeBarButtonsToAdd": ["pan2d", "zoom2d"],
                    "displaylogo": False,  # Oculta el logo de Plotly en el gráfico
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"],  # Se eliminan botones innecesarios
                },
                style={"height": "400vh", "overflow": "hidden", "backgroundColor": "#f0f0f0"},
            ),
        ]
    )


# Callback para actualizar los valores de los dropdowns basados en los datos almacenados
@app.callback(
    [Output("dataset-dropdown-inyector", "value"),
     Output("dataset-dropdown-productor", "value"),
     Output("ubicacion-dropdown", "value")],
    [Input("dropdown-value-store-inyector", "data"),
     Input("dropdown-value-store-productor", "data"),
     Input("dropdown-value-store-ubicacion", "data")]
)
def update_dropdown_values(stored_value_inyector, stored_value_productor, stored_value_ubicacion):
    """
    Actualiza los valores preseleccionados de los dropdowns (inyector, productor y ubicación) 
    utilizando los datos almacenados previamente en el almacenamiento de sesión.

    Args:
        stored_value_inyector (list): Lista de valores seleccionados previamente en el dropdown de inyectores.
        stored_value_productor (list): Lista de valores seleccionados previamente en el dropdown de productores.
        stored_value_ubicacion (str): Valor seleccionado previamente en el dropdown de ubicación (PL/SL/Ambos).

    Returns:
        tuple: Valores actualizados para los dropdowns de inyector, productor y ubicación. 
               Se devuelven listas vacías o 'Ambos' como valores predeterminados si no hay datos almacenados.
    """
    
    # Retorna los valores almacenados o valores por defecto en caso de que no haya valores almacenados
    return stored_value_inyector or [], stored_value_productor or [], stored_value_ubicacion or 'Ambos'

# Callback para almacenar los valores seleccionados de los dropdowns
@app.callback(
    [Output("dropdown-value-store-inyector", "data"),
     Output("dropdown-value-store-productor", "data"),
     Output("dropdown-value-store-ubicacion", "data")],
    [Input("dataset-dropdown-inyector", "value"),
     Input("dataset-dropdown-productor", "value"),
     Input("ubicacion-dropdown", "value")],
    [State("dropdown-value-store-inyector", "data"),
     State("dropdown-value-store-productor", "data"),
     State("dropdown-value-store-ubicacion", "data")]
)
def store_dropdown_values(selected_inyectores, selected_productores, selected_ubicacion, stored_inyectores, stored_productores, stored_ubicacion):
    """
    Almacena los valores seleccionados de los dropdowns (inyector, productor, ubicación)
    en el almacenamiento de sesión, manejando correctamente la interacción entre los componentes
    sin sobrescribir otros valores.

    Args:
        selected_inyectores (list): Inyectores seleccionados en el dropdown de inyectores.
        selected_productores (list): Productores seleccionados en el dropdown de productores.
        selected_ubicacion (str): Ubicación seleccionada en el dropdown de ubicación (PL/SL/Ambos).
        stored_inyectores (list): Inyectores almacenados previamente en sesión.
        stored_productores (list): Productores almacenados previamente en sesión.
        stored_ubicacion (str): Ubicación almacenada previamente en sesión.

    Returns:
        tuple: Actualización de los valores almacenados en el almacenamiento de sesión para inyectores,
               productores y ubicación, dependiendo del componente que haya sido modificado.
    """
    
    # Obtenemos el contexto del callback para saber qué componente disparó el cambio
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Si se selecciona un inyector, reseteamos la selección de productores
    if trigger_id == "dataset-dropdown-inyector":
        return selected_inyectores, [], stored_ubicacion
    # Si se selecciona un productor, reseteamos la selección de inyectores
    elif trigger_id == "dataset-dropdown-productor":
        return [], selected_productores, stored_ubicacion
    # Si se selecciona la ubicación, mantenemos inyectores y productores tal como están
    elif trigger_id == "ubicacion-dropdown":
        return stored_inyectores, stored_productores, selected_ubicacion

    # Retorna los valores almacenados si no hubo cambios en los componentes
    return stored_inyectores, stored_productores, stored_ubicacion


# Callback para actualizar el gráfico en función de los filtros seleccionados
@app.callback(
    Output("petroleo-graph", "figure"),
    [Input("dataset-dropdown-inyector", "value"),
     Input("dataset-dropdown-productor", "value"),
     Input("ubicacion-dropdown", "value")],
    prevent_initial_call=False,
)
def update_graph(selected_inyectores, selected_productores, selected_ubicacion):
    """
    Actualiza el gráfico principal según los inyectores, productores y ubicación seleccionados.
    Dependiendo de las selecciones realizadas, se filtran los datos de relación entre inyectores y productores,
    y se dibujan las líneas de conexión entre ellos con las distancias calculadas.

    Args:
        selected_inyectores (list): Lista de inyectores seleccionados por el usuario.
        selected_productores (list): Lista de productores seleccionados por el usuario.
        selected_ubicacion (str): Filtro de ubicación seleccionado (PL, SL o Ambos).

    Returns:
        go.Figure: Gráfico de Plotly actualizado con las líneas de conexión y las distancias entre pozos.
    """
    try:
        # Filtrar data_relacion según la ubicación seleccionada (PL/SL/Ambos)
        if selected_ubicacion == 'PL':
            relaciones_filtradas = data_relacion[data_relacion['Ubicación'] == 'PL']
        elif selected_ubicacion == 'SL':
            relaciones_filtradas = data_relacion[data_relacion['Ubicación'] == 'SL']
        else:
            relaciones_filtradas = data_relacion  # Mostrar ambos (PL y SL)

        # Crear gráfico de dispersión básico para mostrar todos los pozos
        fig = px.scatter(
            data_coordenadas,
            x='X',
            y='Y',
            text='POZO',
            color='TIPO',
            color_discrete_map={
                'productor': '#2E8B57',  # Verde para los productores
                'inyector': '#1E90FF'   # Azul para los inyectores
            },
            hover_data={'X': False, 'Y': False, 'POZO': True, 'TIPO': False, 'UNIDAD': True},  # Datos adicionales en el hover
        )

        # Personalización del gráfico
        fig.update_traces(marker=dict(size=8, line=dict(width=2, color='DarkSlateGrey')), textposition='top center', textfont=dict(size=14))
        fig.update_layout(
            dragmode="zoom",  # Habilitar el zoom por defecto
            height=800,
            margin=dict(l=40, r=40, t=40, b=20),
            xaxis=dict(showgrid=False, showticklabels=False, title=''),
            yaxis=dict(showgrid=False, showticklabels=False, title=''),
            paper_bgcolor='#f0f0f0',
            plot_bgcolor='#f0f0f0',
            template='plotly_white',
            hoverlabel=dict(font_size=12, font_family="Arial"),
            showlegend=False
        )

        # Definir una función para calcular la distancia euclidiana entre dos puntos (X, Y)
        def calcular_distancia(x1, y1, x2, y2):
            return ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5

        # Agregar las líneas de conexión para los inyectores seleccionados
        if selected_inyectores:
            for selected_inyector in selected_inyectores:
                relaciones = relaciones_filtradas[relaciones_filtradas['Inyector'] == selected_inyector]
                for _, row in relaciones.iterrows():
                    asociados = row['Asociados'].split(",")
                    declarados = row['Declarados'].split(",") if row['Declarados'] else []

                    for asociado in asociados:
                        asociado = asociado.strip()  # Eliminar espacios innecesarios
                        if selected_inyector in data_coordenadas['POZO'].values and asociado in data_coordenadas['POZO'].values:
                            pozo_iny = data_coordenadas[data_coordenadas['POZO'] == selected_inyector].iloc[0]
                            pozo_asoc = data_coordenadas[data_coordenadas['POZO'] == asociado].iloc[0]
                            color_linea = color_map[selected_inyector]

                            # Calcular la distancia euclidiana entre el inyector y el productor
                            distancia = calcular_distancia(pozo_iny['X'], pozo_iny['Y'], pozo_asoc['X'], pozo_asoc['Y'])

                            # Añadir la distancia al hover de las líneas que conectan los pozos
                            fig.add_trace(go.Scatter(
                                x=[pozo_iny['X'], pozo_asoc['X']],
                                y=[pozo_iny['Y'], pozo_asoc['Y']],
                                mode='lines+markers',
                                line=dict(color=color_linea, width=1),
                                marker=dict(size=1, opacity=0),  # Hacemos los marcadores invisibles pero activos en el hover
                                showlegend=False,
                                hoverinfo='text',
                                text=f'Distancia: {distancia:.2f} metros'  # Mostrar la distancia en el hover
                            ))

                            # Dibujar línea discontinua para "Declarados"
                            if asociado in declarados:
                                offset = 0  # Aplicar un pequeño desplazamiento si es necesario
                                fig.add_trace(go.Scatter(
                                    x=[pozo_iny['X'] + offset, pozo_asoc['X']],
                                    y=[pozo_iny['Y'] + offset, pozo_asoc['Y']],
                                    mode='lines+markers',  
                                    line=dict(color=color_linea, width=3, dash='dot'),
                                    marker=dict(size=1, opacity=0),
                                    showlegend=False,
                                    hoverinfo='text',
                                    text=f'Distancia: {distancia:.2f} metros (Declarado)'  # Mostrar la distancia también para los declarados
                                ))

        # Agregar las líneas de conexión para los productores seleccionados
        if selected_productores:
            for selected_productor in selected_productores:
                relaciones = relaciones_filtradas[relaciones_filtradas['Asociados'].str.contains(selected_productor)]
                for _, row in relaciones.iterrows():
                    inyector = row['Inyector']
                    declarados = row['Declarados'].split(",") if row['Declarados'] else []

                    # Verificar que tanto el inyector como el productor seleccionado tengan coordenadas
                    if inyector in data_coordenadas['POZO'].values and selected_productor in data_coordenadas['POZO'].values:
                        pozo_iny = data_coordenadas[data_coordenadas['POZO'] == inyector].iloc[0]
                        pozo_prod = data_coordenadas[data_coordenadas['POZO'] == selected_productor].iloc[0]
                        color_linea = color_map[inyector]

                        # Calcular la distancia euclidiana entre el inyector y el productor
                        distancia = calcular_distancia(pozo_iny['X'], pozo_iny['Y'], pozo_prod['X'], pozo_prod['Y'])

                        # Añadir la distancia al hover de las líneas
                        fig.add_trace(go.Scatter(
                            x=[pozo_iny['X'], pozo_prod['X']],
                            y=[pozo_iny['Y'], pozo_prod['Y']],
                            mode='lines+markers',
                            line=dict(color=color_linea, width=1),
                            marker=dict(size=1, opacity=0),
                            showlegend=False,
                            hoverinfo='text',
                            text=f'Distancia: {distancia:.0f} metros'
                        ))

                        # Dibujar línea discontinua si el productor está declarado
                        if selected_productor in declarados:
                            offset = 0  # Aplicar un pequeño desplazamiento si es necesario
                            fig.add_trace(go.Scatter(
                                x=[pozo_iny['X'] + offset, pozo_prod['X']],
                                y=[pozo_iny['Y'] + offset, pozo_prod['Y']],
                                mode='lines+markers',
                                line=dict(color=color_linea, width=3, dash='dot'),
                                marker=dict(size=1, opacity=0),
                                showlegend=False,
                                hoverinfo='text',
                                text=f'Distancia: {distancia:.2f} metros (Declarado)'
                            ))

        return fig
    
    except Exception as e:
        # Capturar errores y devolver un gráfico vacío si ocurre una excepción
        print("Error:", e)
        fig = px.scatter()
        return fig
