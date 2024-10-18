import plotly.graph_objs as go

def normalize_column_by_group(df, group_col, value_col):
    """
    Normaliza una columna por grupo dentro de un DataFrame. 
    Cada grupo se normaliza de forma independiente entre 0 y 1.
    
    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos a normalizar.
        group_col (str): La columna que define los grupos (por ejemplo, 'IDENTIFICADOR').
        value_col (str): La columna de valores que se desea normalizar.
    
    Returns:
        pd.DataFrame: El DataFrame con la columna normalizada añadida.
    """
    df[value_col + '_norm'] = df.groupby(group_col)[value_col].transform(
        lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() != x.min() else 0
    )
    return df

def create_first_graph_fc(selected_productores, filtered_data, mes_inyector_filtered):
    """
    Crea un gráfico de líneas que muestra los valores normalizados por productor y por inyector. 
    Los valores se normalizan de forma independiente para cada productor e inyector.

    Args:
        selected_productores (list): Lista de productores seleccionados.
        filtered_data (pd.DataFrame): Datos filtrados que contienen la información de los productores.
        mes_inyector_filtered (pd.DataFrame): Datos filtrados que contienen la información de los inyectores.

    Returns:
        go.Figure: Un gráfico de Plotly con las líneas de productores e inyectores normalizadas.
    """
    
    # Normalizar los valores de 'qwi' en mes_inyector_filtered por cada inyector
    mes_inyector_filtered = normalize_column_by_group(mes_inyector_filtered, 'IDENTIFICADOR', 'qwi')
    
    # Filtrar y normalizar los valores de 'ql' en filtered_data por cada productor
    if selected_productores:
        # Si hay productores seleccionados, filtrar filtered_data por los productores seleccionados
        data_filtrada = filtered_data[filtered_data['IDENTIFICADOR'].isin(selected_productores)]
    else:
        # Si no hay productores seleccionados, crear un DataFrame vacío para evitar mostrar datos no deseados
        data_filtrada = filtered_data.iloc[0:0]
    
    # Normalizar los valores de 'ql' por cada productor en data_filtrada
    data_filtrada = normalize_column_by_group(data_filtrada, 'IDENTIFICADOR', 'ql')

    # Crear el gráfico
    fig = go.Figure()

    # Agregar la traza del inyector con los valores normalizados
    fig.add_trace(
        go.Scatter(
            x=mes_inyector_filtered['FECHA'],
            y=mes_inyector_filtered['qwi_norm'],
            text=mes_inyector_filtered['IDENTIFICADOR'],
            mode='lines',
            name="Inyector (Normalizado)"
        )
    )

    # Agregar las trazas para cada productor con los valores normalizados
    for productor in data_filtrada['IDENTIFICADOR'].unique():
        productor_data = data_filtrada[data_filtrada['IDENTIFICADOR'] == productor]
        
        fig.add_trace(
            go.Scatter(
                x=productor_data['FECHA'],
                y=productor_data['ql_norm'],
                mode='lines',
                name=f"Productor {productor} (Normalizado)",
                text=productor_data['IDENTIFICADOR'],
                hovertemplate=(
                    '<b>%{text}</b><br>' +
                    'Fecha: %{x}<br>' +
                    'Ql (Normalizado): %{y:.2f}<br>'
                )
            )
        )

        # Configurar el fondo blanco
    fig.update_layout(
        paper_bgcolor='white',  # Fondo externo al gráfico
        plot_bgcolor='white',   # Fondo del gráfico
        xaxis=dict(showgrid=True),  # Mostrar las líneas de la cuadrícula en el eje X
        yaxis=dict(showgrid=True),  # Mostrar las líneas de la cuadrícula en el eje Y
    )

    return fig




