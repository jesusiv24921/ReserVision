import plotly.express as px
import plotly.graph_objs as go

# -------------------------------------------------------------------------------------------------------------------------------------
def update_small_graph(selected_inyectores, selected_pl_sl, selected_productores, data_relacion, data_coordenadas):
    """
    Actualiza el gráfico pequeño de dispersión en función de los inyectores, productores y la ubicación seleccionados.

    Args:
        selected_inyectores (list): Lista de inyectores seleccionados.
        selected_pl_sl (str): Ubicación seleccionada ('PL', 'SL' o 'Ambos').
        selected_productores (list): Lista de productores seleccionados.
        data_relacion (pd.DataFrame): DataFrame con las relaciones entre inyectores y productores.
        data_coordenadas (pd.DataFrame): DataFrame con las coordenadas de los pozos.

    Returns:
        fig (plotly.graph_objs.Figure): Gráfico actualizado en función de los filtros seleccionados.
    """
    try:
        # Filtrar data_relacion según la ubicación seleccionada (PL, SL o Ambos)
        relaciones_filtradas = data_relacion[data_relacion['Ubicación'] == selected_pl_sl] if selected_pl_sl and selected_pl_sl != 'Ambos' else data_relacion
        
        # Filtrar por inyectores seleccionados
        if selected_inyectores:
            relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Inyector'].isin(selected_inyectores)]

        # Filtrar por productores seleccionados
        if selected_productores:
            relaciones_filtradas = relaciones_filtradas[relaciones_filtradas['Asociados'].str.contains('|'.join(selected_productores))]

        # Obtener los pozos a mostrar en el gráfico
        pozos_a_mostrar = set()
        for _, row in relaciones_filtradas.iterrows():
            pozos_a_mostrar.add(row['Inyector'])
            pozos_a_mostrar.update(row['Asociados'].split(","))

        # Filtrar data_coordenadas según los pozos seleccionados
        data_filtrada = data_coordenadas[data_coordenadas['POZO'].isin(pozos_a_mostrar)]

        # Crear gráfico de dispersión con los pozos filtrados
        fig = px.scatter(
            data_filtrada,
            x='X',
            y='Y',
            text='POZO',
            color='TIPO',
            color_discrete_map={
                'productor': '#2E8B57',  # Verde para productores
                'inyector': '#1E90FF'   # Azul para inyectores
            },
            hover_data={'X': False, 'Y': False, 'POZO': True, 'TIPO': False, 'UNIDAD': True},
        )

        # Personalización del gráfico
        fig.update_traces(marker=dict(size=8, line=dict(width=2, color='DarkSlateGrey')), textposition='top center', textfont=dict(size=14))
        fig.update_layout(
            dragmode="zoom",
            height=400,
            margin=dict(l=40, r=40, t=40, b=20),
            xaxis=dict(showgrid=False, showticklabels=False, title=''),
            yaxis=dict(showgrid=False, showticklabels=False, title=''),
            paper_bgcolor='white',
            plot_bgcolor='white',
            template='plotly_white',
            hoverlabel=dict(font_size=12, font_family="Arial"),
            showlegend=False
        )

        # Añadir líneas entre los pozos
        for _, row in relaciones_filtradas.iterrows():
            asociados = row['Asociados'].split(",")
            declarados = row['Declarados'].split(",") if row['Declarados'] else []

            for asociado in asociados:
                asociado = asociado.strip()
                if row['Inyector'] in data_coordenadas['POZO'].values and asociado in data_coordenadas['POZO'].values:
                    pozo_iny = data_coordenadas[data_coordenadas['POZO'] == row['Inyector']].iloc[0]
                    pozo_asoc = data_coordenadas[data_coordenadas['POZO'] == asociado].iloc[0]

                    # Añadir línea continua para pozos no declarados
                    fig.add_trace(go.Scatter(x=[pozo_iny['X'], pozo_asoc['X']], y=[pozo_iny['Y'], pozo_asoc['Y']], mode='lines', line=dict(color='black', width=1), showlegend=False))

                    # Añadir línea discontinua para pozos declarados
                    if asociado in declarados:
                        offset = 0.5
                        fig.add_trace(go.Scatter(x=[pozo_iny['X'] + offset, pozo_asoc['X'] + offset], y=[pozo_iny['Y'] + offset, pozo_asoc['Y'] + offset], mode='lines', line=dict(color='black', width=3, dash='dot'), showlegend=False))

        return fig

    except Exception as e:
        print("Error:", e)
        return px.scatter()

# -------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px
from my_project.tab_behavior_patterns.behavior_func import SeleccionarPruebas
import pandas as pd

def create_first_graph(selected_productores, controles_diarios, selected_date, data_estatica):
    """
    Crear gráfico de dispersión que muestra las relaciones entre BSW y BOPD, junto con líneas de promedio y anotaciones.

    Args:
        selected_productores (list): Lista de productores seleccionados.
        controles_diarios (pd.DataFrame): Datos diarios de producción.
        selected_date (pd.Timestamp or str): Fecha seleccionada como referencia.
        data_estatica (pd.DataFrame): Información estática de los pozos.

    Returns:
        go.Figure: Gráfico actualizado que incluye anotaciones y promedios.
    """
    # Filtrar la data estática
    data_estatica = data_estatica[['pozo', 'Formación', 'tvd_bott_perf', 'subunidad']]
    
    # Filtrar controles diarios y data estática según los productores seleccionados
    if selected_productores:
        data_filtrada = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]
        data_estatica_ = data_estatica[data_estatica['pozo'].isin(selected_productores)]
    else:
        data_filtrada = controles_diarios.iloc[0:0]
        data_estatica_ = data_estatica.iloc[0:0]

    # Seleccionar la última prueba por mes
    data_filtrada_ = SeleccionarPruebas().seleccionar_ultima_prueba_por_mes(data_filtrada, selected_date)
    merge = pd.merge(data_filtrada_, data_estatica_, left_on='IDENTIFICADOR', right_on='pozo', how='left').drop_duplicates(subset=['IDENTIFICADOR', 'FECHA'])

    # Calcular los promedios de qo y bsw
    promedio_qo = merge['qo'].mean()
    promedio_qw = merge['bsw'].mean()

    # Crear gráfico de dispersión con color basado en 'tvd_bott_perf'
    fig = px.scatter(
        merge,
        x='bsw',
        y='qo',
        text='IDENTIFICADOR',
        color='tvd_bott_perf',
        color_continuous_scale='RdYlBu_r',
        hover_data={'bsw': ':.1f', 'qo': True, 'subunidad': True, 'IDENTIFICADOR': False, 'tvd_bott_perf': ':.1f'}
    )

    # Personalización del gráfico
    fig.update_traces(marker=dict(size=12, line=dict(width=0)), textposition='top center', textfont=dict(size=13))
    fig.update_layout(
        xaxis_title="BSW",
        yaxis_title="BOPD",
        height=450,
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="TVD Bott Perf", thickness=10, len=0.6)
    )

    # Añadir líneas de promedio
    fig.add_shape(type='line', x0=promedio_qw, x1=promedio_qw, y0=0, y1=merge['qo'].max() * 1.15, line=dict(color='black', width=1))
    fig.add_shape(type='line', x0=0, x1=merge['bsw'].max() * 1.15, y0=promedio_qo, y1=promedio_qo, line=dict(color='black', width=1))

    # Dibujar un rectángulo que encierre todos los datos
    fig.add_shape(type='rect', x0=0, x1=merge['bsw'].max() * 1.15, y0=0, y1=merge['qo'].max() * 1.15, line=dict(color='black', width=1))

    # Mejorar los ejes
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', range=[0, merge['bsw'].max() * 1.15])
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', range=[0, merge['qo'].max() * 1.15])

    # Añadir anotaciones para los promedios
    fig.add_annotation(x=promedio_qw, y=merge['qo'].max() * 1.15, text=f"{promedio_qw:.0f}", showarrow=False, yshift=10, font=dict(color="blue", size=14))
    fig.add_annotation(x=merge['bsw'].max() * 1.15, y=promedio_qo, text=f"{promedio_qo:.1f}", showarrow=False, xshift=12, font=dict(color="green", size=14))

    return fig



# -------------------------------------------------------------------------------------------------------------------------------------
import plotly.express as px
from my_project.tab_behavior_patterns.behavior_func import SeleccionarPruebas
import pandas as pd

def create_second_graph(selected_productores, controles_diarios, selected_date, data_estatica):
    """
    Crear el segundo gráfico de dispersión que muestra la relación entre BWPD y BOPD.
    Añade líneas de promedio y un rectángulo que encierra los datos seleccionados.

    Args:
        selected_productores (list): Lista de productores seleccionados.
        controles_diarios (pd.DataFrame): DataFrame que contiene los datos diarios de producción.
        selected_date (str or pd.Timestamp): Fecha seleccionada para filtrar los datos.
        data_estatica (pd.DataFrame): DataFrame con datos estáticos sobre los pozos.

    Returns:
        fig (plotly.graph_objs.Figure): Gráfico actualizado según los filtros aplicados.
    """
    # Filtrar la data estática según los productores seleccionados
    data_estatica = data_estatica[['pozo', 'Formación', 'tvd_bott_perf', 'subunidad']]

    if selected_productores:
        # Filtrar controles diarios para incluir solo los productores seleccionados
        data_filtrada = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]
        data_estatica_ = data_estatica[data_estatica['pozo'].isin(selected_productores)]
    else:
        # Si no hay productores seleccionados, retornar un DataFrame vacío
        data_filtrada = controles_diarios.iloc[0:0]
        data_estatica_ = data_estatica.iloc[0:0]

    # Obtener la última prueba por mes con la fecha seleccionada
    data_filtrada_ = SeleccionarPruebas().seleccionar_ultima_prueba_por_mes(data_filtrada, selected_date)
    merge = pd.merge(data_filtrada_, data_estatica_, left_on='IDENTIFICADOR', right_on='pozo', how='left')
    merge = merge.drop_duplicates(subset=['IDENTIFICADOR', 'FECHA'])

    # Calcular los promedios
    promedio_qo = merge['qo'].mean()
    promedio_qw = merge['qw'].mean()

    # Crear el gráfico de dispersión
    fig = px.scatter(
        merge,
        x='qw',
        y='qo',
        text='IDENTIFICADOR',
        color='tvd_bott_perf',
        color_continuous_scale='RdYlBu_r',
        hover_data={'qw': ':.1f', 'qo': True, 'subunidad': True, 'IDENTIFICADOR': False, 'tvd_bott_perf': ':.1f'}
    )

    # Personalizar el gráfico
    fig.update_traces(marker=dict(size=12, line=dict(width=0)), textposition='top center', textfont=dict(size=13))

    # Añadir las líneas de promedio
    fig.add_shape(type='line', x0=promedio_qw, x1=promedio_qw, y0=0, y1=merge['qo'].max() * 1.15, line=dict(color='black', width=1))
    fig.add_shape(type='line', x0=0, x1=merge['qw'].max() * 1.15, y0=promedio_qo, y1=promedio_qo, line=dict(color='black', width=1))

    # Dibujar un rectángulo que encierre todos los datos y líneas de promedio
    fig.add_shape(type='rect', x0=0, x1=merge['qw'].max() * 1.15, y0=0, y1=merge['qo'].max() * 1.15, line=dict(color='black', width=1))

    # Configuración de los ejes y el layout del gráfico
    fig.update_layout(
        xaxis_title="BWPD",
        yaxis_title="BOPD",
        height=450,
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="TVD Bott Perf", thickness=10, len=0.6)
    )

    # Ajustes de los ejes
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[0, merge['qw'].max() * 1.15])
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[0, merge['qo'].max() * 1.15])

    # Anotaciones para las líneas de promedio
    fig.add_annotation(x=promedio_qw, y=merge['qo'].max() * 1.15, text=f"{promedio_qw:.0f}", showarrow=False, yshift=10, font=dict(color="blue", size=14))
    fig.add_annotation(x=merge['qw'].max() * 1.15, y=promedio_qo, text=f"{promedio_qo:.0f}", showarrow=False, xshift=12, font=dict(color="green", size=14))

    return fig

# -------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px
from my_project.tab_behavior_patterns.behavior_func import SeleccionarPruebas
import pandas as pd

def create_third_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf):
    """
    Crear un gráfico de dispersión que muestra la relación entre Kh e IP, con líneas de promedio y un rectángulo.

    Args:
        selected_productores (list): Lista de productores seleccionados.
        controles_diarios (pd.DataFrame): DataFrame con los datos diarios de producción.
        selected_date (str or pd.Timestamp): Fecha seleccionada para filtrar los datos.
        data_estatica (pd.DataFrame): Información estática de los pozos.
        pwf (pd.DataFrame): Datos de presión de fondo fluyente (Pwf).

    Returns:
        fig (plotly.graph_objs.Figure): Gráfico actualizado según los filtros aplicados.
    """
    # Filtrar data estática para incluir columnas relevantes
    data_estatica = data_estatica[['pozo', 'Formación', 'tvd_bott_perf', 'subunidad', 'py', 'h (tvd)', 'k']]

    if selected_productores:
        # Filtrar los datos para incluir solo los productores seleccionados
        data_filtrada = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]
        data_estatica_ = data_estatica[data_estatica['pozo'].isin(selected_productores)]
        pwf_ = pwf[pwf['pozo'].isin(selected_productores)].reset_index(drop=True)
    else:
        # Si no hay productores seleccionados, retornar DataFrames vacíos
        data_filtrada = controles_diarios.iloc[0:0]
        data_estatica_ = data_estatica.iloc[0:0]
        pwf_ = pwf.iloc[0:0]

    # Obtener la última prueba por mes
    data_filtrada_ = SeleccionarPruebas().seleccionar_ultima_prueba_por_mes(data_filtrada, selected_date)
    pwf_filtrada_ = SeleccionarPruebas().seleccionar_ultima_pwf_por_mes(pwf_, selected_date)

    # Fusionar los DataFrames
    merge_ = pd.merge(data_filtrada_, data_estatica_, left_on='IDENTIFICADOR', right_on='pozo', how='left')
    merge = pd.merge(merge_, pwf_filtrada_, left_on='IDENTIFICADOR', right_on='pozo', how='left')

    # Crear las columnas IP y Kh
    merge['IP'] = merge['ql'] / (merge['py'] - merge['pwf'])
    merge['kh'] = (merge['k'] * merge['h (tvd)']) / 1000
    merge = merge.drop_duplicates(subset=['IDENTIFICADOR', 'FECHA'])

    # Calcular los promedios
    promedio_ip = merge['IP'].mean()
    promedio_kh = merge['kh'].mean()

    # Crear el gráfico de dispersión
    fig = px.scatter(
        merge,
        x='kh',
        y='IP',
        text='IDENTIFICADOR',
        color='tvd_bott_perf',
        color_continuous_scale='RdYlBu_r',
        hover_data={'kh': ':.1f', 'IP': ':.1f', 'subunidad': True, 'IDENTIFICADOR': False, 'tvd_bott_perf': ':.1f'}
    )

    # Personalización del gráfico
    fig.update_traces(marker=dict(size=12, line=dict(width=0)), textposition='top center', textfont=dict(size=13))

    # Definir los valores mínimos para el eje Y (IP)
    y0 = -merge['IP'].min() * 0.5 if merge['IP'].min() > 0 else merge['IP'].min() * 0.5

    # Añadir las líneas de promedio
    fig.add_shape(type='line', x0=promedio_kh, x1=promedio_kh, y0=merge['IP'].min() + y0, y1=merge['IP'].max() * 1.15, line=dict(color='black', width=1))
    fig.add_shape(type='line', x0=0, x1=merge['kh'].max() * 1.15, y0=promedio_ip, y1=promedio_ip, line=dict(color='black', width=1))

    # Dibujar un rectángulo que encierre todos los datos y líneas de promedio
    fig.add_shape(type='rect', x0=0, x1=merge['kh'].max() * 1.15, y0=merge['IP'].min() + y0, y1=merge['IP'].max() * 1.15, line=dict(color='black', width=1))

    # Configurar el layout del gráfico
    fig.update_layout(
        xaxis_title="Kh",
        yaxis_title="IP",
        height=450,
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="TVD Bott Perf", thickness=10, len=0.6)
    )

    # Ajustes de los ejes
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[0, merge['kh'].max() * 1.15])
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[merge['IP'].min() + y0, merge['IP'].max() * 1.15])

    # Anotaciones para las líneas de promedio
    fig.add_annotation(x=promedio_kh, y=merge['IP'].max() * 1.15, text=f"{promedio_kh:.0f}", showarrow=False, yshift=10, font=dict(color="blue", size=14))
    fig.add_annotation(x=merge['kh'].max() * 1.15, y=promedio_ip, text=f"{promedio_ip:.2f}", showarrow=False, xshift=12, font=dict(color="green", size=14))

    return fig


# -------------------------------------------------------------------------------------------------------------------------------------
import plotly.express as px
from my_project.tab_behavior_patterns.behavior_func import SeleccionarPruebas
import pandas as pd

def create_four_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf):
    """
    Crear un gráfico de dispersión que muestra la relación entre BSW e IP para los productores seleccionados.
    Se agregan líneas de promedio y un rectángulo que encierra los datos.

    Args:
        selected_productores (list): Lista de productores seleccionados.
        controles_diarios (pd.DataFrame): Datos de producción diaria.
        selected_date (str or pd.Timestamp): Fecha seleccionada para filtrar las pruebas.
        data_estatica (pd.DataFrame): Datos estáticos de los pozos (como TVD, formación, etc.).
        pwf (pd.DataFrame): Datos de presión de fondo fluyente (PWF).

    Returns:
        fig (plotly.graph_objs.Figure): Gráfico de dispersión con las líneas de promedio y anotaciones.
    """
    # Filtrar los datos estáticos para incluir las columnas relevantes
    data_estatica = data_estatica[['pozo', 'Formación', 'tvd_bott_perf', 'subunidad', 'py', 'h (tvd)', 'k']]

    # Filtrar los datos según los productores seleccionados
    if selected_productores:
        data_filtrada = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]
        data_estatica_ = data_estatica[data_estatica['pozo'].isin(selected_productores)]
        pwf_ = pwf[pwf['pozo'].isin(selected_productores)].reset_index(drop=True)
    else:
        # Si no hay productores seleccionados, retornar DataFrames vacíos
        data_filtrada = controles_diarios.iloc[0:0]
        data_estatica_ = data_estatica.iloc[0:0]
        pwf_ = pwf.iloc[0:0]

    # Seleccionar la última prueba y PWF por mes según la fecha seleccionada
    data_filtrada_ = SeleccionarPruebas().seleccionar_ultima_prueba_por_mes(data_filtrada, selected_date)
    pwf_filtrada_ = SeleccionarPruebas().seleccionar_ultima_pwf_por_mes(pwf_, selected_date)

    # Fusionar los DataFrames de producción, estática y PWF
    merge_ = pd.merge(data_filtrada_, data_estatica_, left_on='IDENTIFICADOR', right_on='pozo', how='left')
    merge = pd.merge(merge_, pwf_filtrada_, left_on='IDENTIFICADOR', right_on='pozo', how='left')

    # Crear la columna de IP
    merge['IP'] = merge['ql'] / (merge['py'] - merge['pwf'])
    merge = merge.drop_duplicates(subset=['IDENTIFICADOR', 'FECHA'])

    # Calcular los promedios
    promedio_ip = merge['IP'].mean()
    promedio_bsw = merge['bsw'].mean()

    # Crear el gráfico de dispersión con color basado en 'tvd_bott_perf'
    fig = px.scatter(
        merge,
        x='bsw',
        y='IP',
        text='IDENTIFICADOR',
        color='tvd_bott_perf',
        color_continuous_scale='RdYlBu_r',
        hover_data={'bsw': ':.1f', 'IP': ':.1f', 'subunidad': True, 'IDENTIFICADOR': False, 'tvd_bott_perf': ':.1f'}
    )

    # Personalización del gráfico
    fig.update_traces(marker=dict(size=12, line=dict(width=0)), textposition='top center', textfont=dict(size=13))

    # Definir los valores mínimos para el eje Y
    ip_min = merge['IP'].min()
    y0 = -merge['IP'].min() * 0.5 if ip_min > 0 else merge['IP'].min() * 0.5

    # Añadir las líneas de promedio
    fig.add_shape(type='line', x0=promedio_bsw, x1=promedio_bsw, y0=ip_min + y0, y1=merge['IP'].max() * 1.15, line=dict(color='black', width=1))
    fig.add_shape(type='line', x0=0, x1=merge['bsw'].max() * 1.15, y0=promedio_ip, y1=promedio_ip, line=dict(color='black', width=1))

    # Dibujar un rectángulo que encierre todos los datos y líneas de promedio
    fig.add_shape(type='rect', x0=0, x1=merge['bsw'].max() * 1.15, y0=ip_min + y0, y1=merge['IP'].max() * 1.15, line=dict(color='black', width=1))

    # Configuración del layout del gráfico
    fig.update_layout(
        xaxis_title="BSW",
        yaxis_title="IP",
        height=450,
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="TVD Bott Perf", thickness=10, len=0.6)
    )

    # Mejorar los ejes y expandir la rejilla
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[0, merge['bsw'].max() * 1.15])
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[ip_min + y0, merge['IP'].max() * 1.15])

    # Anotaciones para las líneas de promedio
    fig.add_annotation(x=promedio_bsw, y=merge['IP'].max() * 1.15, text=f"{promedio_bsw:.1f}", showarrow=False, yshift=10, font=dict(color="blue", size=14))
    fig.add_annotation(x=merge['bsw'].max() * 1.15, y=promedio_ip, text=f"{promedio_ip:.1f}", showarrow=False, xshift=12, font=dict(color="green", size=14))

    return fig


# -------------------------------------------------------------------------------------------------------------------------------------

import plotly.express as px
from my_project.tab_behavior_patterns.behavior_func import SeleccionarPruebas
import pandas as pd

def create_five_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf):
    """
    Crear un gráfico de dispersión que muestra la relación entre PWF y QL, con líneas de promedio y un rectángulo.

    Args:
        selected_productores (list): Lista de productores seleccionados.
        controles_diarios (pd.DataFrame): DataFrame que contiene los datos de producción diaria.
        selected_date (str or pd.Timestamp): Fecha seleccionada para filtrar los datos.
        data_estatica (pd.DataFrame): Información estática de los pozos (como TVD, formación, etc.).
        pwf (pd.DataFrame): Datos de presión de fondo fluyente (PWF).

    Returns:
        fig (plotly.graph_objs.Figure): Gráfico de dispersión actualizado con anotaciones y líneas de promedio.
    """
    # Filtrar los datos estáticos para incluir las columnas relevantes
    data_estatica = data_estatica[['pozo', 'Formación', 'tvd_bott_perf', 'subunidad', 'py', 'h (tvd)', 'k']]

    # Filtrar los datos según los productores seleccionados
    if selected_productores:
        data_filtrada = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]
        data_estatica_ = data_estatica[data_estatica['pozo'].isin(selected_productores)]
        pwf_ = pwf[pwf['pozo'].isin(selected_productores)].reset_index(drop=True)
    else:
        # Si no hay productores seleccionados, retornar DataFrames vacíos
        data_filtrada = controles_diarios.iloc[0:0]
        data_estatica_ = data_estatica.iloc[0:0]
        pwf_ = pwf.iloc[0:0]

    # Seleccionar la última prueba y PWF por mes según la fecha seleccionada
    data_filtrada_ = SeleccionarPruebas().seleccionar_ultima_prueba_por_mes(data_filtrada, selected_date)
    pwf_filtrada_ = SeleccionarPruebas().seleccionar_ultima_pwf_por_mes(pwf_, selected_date)

    # Fusionar los DataFrames de producción, estática y PWF
    merge_ = pd.merge(data_filtrada_, data_estatica_, left_on='IDENTIFICADOR', right_on='pozo', how='left')
    merge = pd.merge(merge_, pwf_filtrada_, left_on='IDENTIFICADOR', right_on='pozo', how='left')
    merge = merge.drop_duplicates(subset=['IDENTIFICADOR', 'FECHA'])

    # Calcular los promedios
    promedio_ql = merge['ql'].mean()
    promedio_pwf = merge['pwf'].mean()

    # Crear el gráfico de dispersión con color basado en 'tvd_bott_perf'
    fig = px.scatter(
        merge,
        x='pwf',
        y='ql',
        text='IDENTIFICADOR',
        color='tvd_bott_perf',
        color_continuous_scale='RdYlBu_r',
        hover_data={'pwf': ':.1f', 'ql': True, 'subunidad': True, 'IDENTIFICADOR': False, 'tvd_bott_perf': ':.1f'}
    )

    # Personalización del gráfico
    fig.update_traces(marker=dict(size=12, line=dict(width=0)), textposition='top center', textfont=dict(size=13))

    # Añadir las líneas de promedio
    fig.add_shape(type='line', x0=promedio_pwf, x1=promedio_pwf, y0=0, y1=merge['ql'].max() * 1.15, line=dict(color='black', width=1))
    fig.add_shape(type='line', x0=0, x1=merge['pwf'].max() * 1.15, y0=promedio_ql, y1=promedio_ql, line=dict(color='black', width=1))

    # Dibujar un rectángulo que encierre todos los datos y líneas de promedio
    fig.add_shape(type='rect', x0=0, x1=merge['pwf'].max() * 1.15, y0=0, y1=merge['ql'].max() * 1.15, line=dict(color='black', width=1))

    # Configuración del layout del gráfico
    fig.update_layout(
        xaxis_title="PWF",
        yaxis_title="BFPD",
        height=450,
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="TVD Bott Perf", thickness=10, len=0.6)
    )

    # Mejorar los ejes y expandir la rejilla
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[0, merge['pwf'].max() * 1.15])
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[0, merge['ql'].max() * 1.15])

    # Anotaciones para las líneas de promedio
    fig.add_annotation(x=promedio_pwf, y=merge['ql'].max() * 1.15, text=f"{promedio_pwf:.0f}", showarrow=False, yshift=10, font=dict(color="blue", size=14))
    fig.add_annotation(x=merge['pwf'].max() * 1.15, y=promedio_ql, text=f"{promedio_ql:.0f}", showarrow=False, xshift=12, font=dict(color="green", size=14))

    return fig

"-------------------------------------------------------------------------------------------------------------------------------------"

# -------------------------------------------------------------------------------------------------------------------------------------
import plotly.express as px
from my_project.tab_behavior_patterns.behavior_func import SeleccionarPruebas
import pandas as pd
from my_project.scripts.carga_datos import CargaDatos
import numpy as np

kr = CargaDatos().data_cargar('kr')

def create_six_graph(selected_productores, controles_diarios, selected_date, data_estatica, pwf):
    """
    Crear un gráfico de dispersión que muestra la relación entre Kh y Skin para los productores seleccionados.
    Realiza interpolación de datos, agrega líneas de promedio y un rectángulo que encierra los datos.

    Args:
        selected_productores (list): Lista de productores seleccionados.
        controles_diarios (pd.DataFrame): Datos de producción diaria.
        selected_date (str or pd.Timestamp): Fecha seleccionada para filtrar las pruebas.
        data_estatica (pd.DataFrame): Datos estáticos de los pozos (como TVD, formación, etc.).
        pwf (pd.DataFrame): Datos de presión de fondo fluyente (PWF).

    Returns:
        fig (plotly.graph_objs.Figure): Gráfico de dispersión con interpolación de Kro y líneas de promedio.
    """
    # Filtrar los datos estáticos para incluir las columnas relevantes
    data_estatica = data_estatica[['pozo', 'Formación', 'tvd_bott_perf', 'subunidad', 'py', 'h (tvd)', 'k', 'uo', 'bo', 're', 'rw', 'bw']]

    # Filtrar los datos según los productores seleccionados
    if selected_productores:
        data_filtrada = controles_diarios[controles_diarios['IDENTIFICADOR'].isin(selected_productores)]
        data_estatica_ = data_estatica[data_estatica['pozo'].isin(selected_productores)]
        pwf_ = pwf[pwf['pozo'].isin(selected_productores)].reset_index(drop=True)
    else:
        # Si no hay productores seleccionados, retornar DataFrames vacíos
        data_filtrada = controles_diarios.iloc[0:0]
        data_estatica_ = data_estatica.iloc[0:0]
        pwf_ = pwf.iloc[0:0]

    # Seleccionar la última prueba y PWF por mes según la fecha seleccionada
    data_filtrada_ = SeleccionarPruebas().seleccionar_ultima_prueba_por_mes(data_filtrada, selected_date)
    pwf_filtrada_ = SeleccionarPruebas().seleccionar_ultima_pwf_por_mes(pwf_, selected_date)

    # Fusionar los DataFrames de producción, estática y PWF
    merge_ = pd.merge(data_filtrada_, data_estatica_, left_on='IDENTIFICADOR', right_on='pozo', how='left')
    merge = pd.merge(merge_, pwf_filtrada_, left_on='IDENTIFICADOR', right_on='pozo', how='left')

    # Calcular la fracción de agua (Fw)
    merge['fw'] = (merge['qw'] * merge['bw']) / (merge['qo'] * merge['bo'] + (merge['qw'] * merge['bw']))

    # Realizar la interpolación para Kro
    resultados = []
    for index, row in merge.iterrows():
        fw_pozo = row['fw']
        pozo = row['IDENTIFICADOR']
        df_menores = kr[kr['Fw'] <= fw_pozo]
        df_mayores = kr[kr['Fw'] >= fw_pozo]
        if not df_menores.empty and not df_mayores.empty:
            fw_min = df_menores.iloc[-1]
            fw_max = df_mayores.iloc[0]
            kro_interpolado = np.interp(fw_pozo, [fw_min['Fw'], fw_max['Fw']], [fw_min['Kro'], fw_max['Kro']])
            resultados.append({'IDENTIFICADOR': pozo, 'Fw': fw_pozo, 'Kro_interpolado': kro_interpolado})
        else:
            resultados.append({'IDENTIFICADOR': pozo, 'Fw': fw_pozo, 'Kro_interpolado': None})

    result = pd.DataFrame(resultados)
    merge_final = pd.merge(merge, result, on='IDENTIFICADOR', how='left')

    # Calcular Skin (s) y Kh
    merge_final['s'] = ((0.00708 * merge_final['k'] * merge_final['Kro_interpolado'] * merge_final['h (tvd)'] * (merge_final['py'] - merge_final['pwf'])) /
                        (merge_final['bo'] * merge_final['uo'] * merge_final['qo'])) - ((np.log(merge_final['re'] / merge_final['rw'])) - 3 / 4)
    merge_final['kh'] = (merge_final['k'] * merge_final['h (tvd)']) / 1000
    merge_final = merge_final.drop_duplicates(subset=['IDENTIFICADOR', 'FECHA'])

    # Calcular los promedios
    promedio_skin = merge_final['s'].mean()
    promedio_kh = merge_final['kh'].mean()

    # Crear el gráfico de dispersión con color basado en 'tvd_bott_perf'
    fig = px.scatter(
        merge_final,
        x='kh',
        y='s',
        text='IDENTIFICADOR',
        color='tvd_bott_perf',
        color_continuous_scale='RdYlBu_r',
        hover_data={'kh': ':.1f', 's': ':.1f', 'subunidad': True, 'IDENTIFICADOR': False, 'tvd_bott_perf': ':.1f'}
    )

    # Personalización del gráfico
    fig.update_traces(marker=dict(size=12, line=dict(width=0)), textposition='bottom center', textfont=dict(size=13))

    # Añadir las líneas de promedio
    fig.add_shape(type='line', x0=promedio_kh, x1=promedio_kh, y0=merge_final['s'].min() * 0.5, y1=merge_final['s'].max() * 1.5, line=dict(color='black', width=1))
    fig.add_shape(type='line', x0=0, x1=merge_final['kh'].max() * 1.15, y0=promedio_skin, y1=promedio_skin, line=dict(color='black', width=1))

    # Dibujar un rectángulo que encierre todos los datos y líneas de promedio
    fig.add_shape(type='rect', x0=0, x1=merge_final['kh'].max() * 1.15, y0=merge_final['s'].min() * 0.5, y1=merge_final['s'].max() * 1.5, line=dict(color='black', width=1))

    # Configuración del layout del gráfico
    fig.update_layout(
        xaxis_title="Kh",
        yaxis_title="Skin",
        height=450,
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(title="TVD Bott Perf", thickness=10, len=0.6)
    )

    # Mejorar los ejes y expandir la rejilla
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[0, merge_final['kh'].max() * 1.15])
    fig.update_yaxes(showgrid=True, gridwidth=0.5, gridcolor='LightGrey', zeroline=True, zerolinewidth=1, zerolinecolor='LightGrey', range=[merge_final['s'].min() * 0.5, merge_final['s'].max() * 1.5])

    # Anotaciones para las líneas de promedio
    fig.add_annotation(x=promedio_kh, y=merge_final['s'].max() * 1.5, text=f"{promedio_kh:.0f}", showarrow=False, yshift=10, font=dict(color="blue", size=14))
    fig.add_annotation(x=merge_final['kh'].max() * 1.15, y=promedio_skin, text=f"{promedio_skin:.1f}", showarrow=False, xshift=12, font=dict(color="green", size=14))

    return fig


# -------------------------------------------------------------------------------------------------------------------------------------

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

def create_qo_ql_graph(filtered_data):
    """
    Crear un gráfico con Qo y Ql a través del tiempo en dos ejes Y diferentes.
    Qo se muestra en el eje Y primario y Ql en el eje Y secundario.

    Args:
        filtered_data (pd.DataFrame): Datos filtrados que contienen las columnas 'FECHA', 'qo', y 'ql'.

    Returns:
        fig (plotly.graph_objs.Figure): Gráfico de líneas para Qo y Ql en el tiempo.
    """
    # Convertir la columna FECHA a formato datetime para asegurar un formato adecuado
    filtered_data.loc[:, 'FECHA'] = pd.to_datetime(filtered_data['FECHA'], errors='coerce')

    # Crear subplots con un segundo eje Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Agregar la traza para Qo en el eje Y primario
    fig.add_trace(
        go.Scatter(x=filtered_data['FECHA'], y=filtered_data['qo'], mode='lines', name='Qo (Caudal de Aceite)', line=dict(color='green')),
        secondary_y=False
    )

    # Agregar la traza para Ql en el eje Y secundario
    fig.add_trace(
        go.Scatter(x=filtered_data['FECHA'], y=filtered_data['ql'], mode='lines', name='Ql (Caudal de Líquidos)', line=dict(color='black')),
        secondary_y=True
    )

    # Configuración del layout del gráfico
    fig.update_layout(
        title="Qo y Ql a través del tiempo",
        xaxis_title="Fecha",
        yaxis=dict(title_text="Caudal de Aceite (Qo)"),
        yaxis2=dict(title_text="Caudal de Líquidos (Ql)", showgrid=False),
        legend=dict(orientation="h", x=0.5, y=-0.2, xanchor="center"),
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    return fig
