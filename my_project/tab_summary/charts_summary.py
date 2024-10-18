import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd

# Funciones de gráficos para la pestaña 'summary'
# ------------------------------------------------------------------------------------------------------------------------------------------------------

# Gráfico Patrón-Productores (tab_summary)
def update_patron(selected_inyectores, selected_productores, selected_ubicacion, data_relacion, mes, pwf, inyeccion_diaria):
    """
    Genera un gráfico con tres subplots que muestran la relación entre un inyector y los productores asociados, incluyendo el comportamiento de la presión.

    Parameters:
    - selected_inyectores: El inyector seleccionado por el usuario.
    - selected_productores: Lista de productores seleccionados por el usuario.
    - selected_ubicacion: Ubicación seleccionada ('PL', 'SL', o 'Ambos').
    - data_relacion: DataFrame que contiene la relación entre inyectores y productores.
    - mes: DataFrame con datos mensuales de producción e inyección.
    - pwf: DataFrame con datos de presión de fondo.
    - inyeccion_diaria: DataFrame con datos diarios de inyección.

    Returns:
    - fig: Objeto de la figura de Plotly que contiene los tres subplots.
    - qo_data: Datos procesados para ser usados en otras partes de la aplicación.
    """
    # Filtrar datos según el inyector seleccionado
    data_relacion_ = data_relacion.copy()
    data_relacion_ = data_relacion_[data_relacion_['Inyector'] == selected_inyectores]

    iny = mes[(mes['IDENTIFICADOR'] == selected_inyectores)]
    inyeccion_diaria_filtrada = inyeccion_diaria[inyeccion_diaria['IDENTIFICADOR'] == selected_inyectores]
    fecha_ini = inyeccion_diaria_filtrada['FECHA'].min()
    iny = iny[iny['FECHA'] >= fecha_ini]
    
    try:
        # Filtrar datos según la ubicación seleccionada
        if selected_ubicacion == 'PL':
            relaciones_filtradas = data_relacion_[data_relacion_['Ubicación'] == 'PL'].reset_index(drop=True)
        elif selected_ubicacion == 'SL':
            relaciones_filtradas = data_relacion_[data_relacion_['Ubicación'] == 'SL'].reset_index(drop=True)
        else:
            relaciones_filtradas = data_relacion_.reset_index(drop=True)

        # Obtener los productores asociados y aplicar filtros adicionales
        productores_asociados = relaciones_filtradas['Asociados'].str.split(',').explode().unique().tolist()
        if selected_productores:
            productores_asociados = [prod for prod in productores_asociados if prod in selected_productores]

        # Filtrar DataFrames de pwf y producción asociados
        pwf_ = pwf[pwf['pozo'].isin(productores_asociados)].reset_index(drop=True)
        prod_aso = mes[mes['IDENTIFICADOR'].isin(productores_asociados)].reset_index(drop=True)
        prod_aso = prod_aso[prod_aso['FECHA'] >= fecha_ini]
        prod_aso = prod_aso[prod_aso['dias'] >= 15]
        
        # Datos para gráficas y otras operaciones
        qo_data = prod_aso[['FECHA', 'IDENTIFICADOR', 'qo', 'qw', 'ql', 'Wcut']].to_dict('records')
        conteo = prod_aso.groupby('FECHA')['IDENTIFICADOR'].count().reset_index()
        productores = prod_aso['IDENTIFICADOR'].unique().tolist()
        prod_agru = prod_aso.groupby('FECHA')[['qo', 'qw', 'ql', 'Wcut', 'WOR']].mean().reset_index()

        # Gráficos de presión dinámica
        pwf_grafico = pwf_[pwf_['pozo'].isin(productores)]
        pwf_grafico = pwf_grafico[pwf_grafico['fecha'] >= fecha_ini]
        filtro_pwf = pwf_grafico.groupby('fecha')['pwf'].mean().reset_index()
        filtro_pwf['pwf_roll'] = filtro_pwf['pwf'].rolling(window=15).mean() 

        # Crear la figura con subplots
        fig = make_subplots(
            rows=3, cols=1,  # Tres filas, una columna
            shared_xaxes=True,  # Compartir el eje x
            vertical_spacing=0.05,  # Espacio vertical entre subplots
            specs=[[{"secondary_y": True}], [{"secondary_y": True}], [{"secondary_y": True}]]  # Activar secondary_y en todos los gráficos
        )

        # Primer gráfico
        fig.add_trace(
            go.Scatter(x=prod_agru['FECHA'], y=prod_agru['qo'], mode='lines', name='qo mean', line=dict(color='green')),
            row=1, col=1, secondary_y=False)
        fig.add_trace(
            go.Scatter(x=prod_agru['FECHA'], y=prod_agru['ql'], mode='lines', name='ql mean', line=dict(color='black')),
            row=1, col=1, secondary_y=False)
        fig.add_trace(
            go.Scatter(x=prod_agru['FECHA'], y=prod_agru['Wcut'], name='BSW', mode='lines', marker_color='blue'),
            row=1, col=1, secondary_y=True)

        # Segundo gráfico
        fig.add_trace(
            go.Scatter(x=filtro_pwf['fecha'], y=filtro_pwf['pwf'], mode='markers', name='Presión Dinámica', marker=dict(color='pink')), row=2, col=1)
        fig.add_trace(
            go.Scatter(x=filtro_pwf['fecha'], y=filtro_pwf['pwf_roll'], mode='lines', name='Presión Dinámica (Media Móvil)', line=dict(color='grey')), row=2, col=1)
        fig.add_trace(
            go.Scatter(x=conteo['FECHA'], y=conteo['IDENTIFICADOR'], mode='lines', name='Conteo Pozos', line=dict(color='purple')), row=2, col=1, secondary_y=True)

        # Tercer gráfico (inyección diaria)
        fig.add_trace(
            go.Scatter(x=inyeccion_diaria_filtrada['FECHA'], y=inyeccion_diaria_filtrada['AGUA_INYECTADA'], 
                       mode='markers', name='Agua Inyectada', marker=dict(size=6, color='blue')), 
            row=3, col=1, secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=inyeccion_diaria_filtrada['FECHA'], y=inyeccion_diaria_filtrada['PIA'], 
                       mode='markers', name='Presión de Inyección', marker=dict(size=6, color='red')), 
            row=3, col=1, secondary_y=True
        )

        # Configurar detalles del gráfico, ejes y layout
        fig.update_layout(
             plot_bgcolor='white', paper_bgcolor='white',
             legend=dict(
                orientation="h",  # Orientación horizontal
                yanchor="top",  # Anclar en la parte superior
                y=1.2,  # Posicionar ligeramente por debajo del gráfico
                xanchor="center",  # Centrar horizontalmente
                x=0.5,  # Centrar horizontalmente
                font=dict(size=14)  # Tamaño de la fuente de la leyenda
            ),
            title=dict(
                text=f'<b>{selected_inyectores}</b>',
                x=0.5,
                xanchor='center',
                y=0.85,
                font=dict(size=20, family="Arial")  # Tamaño y fuente del título
            ),
            xaxis=dict(
                title='',
                tickformat='%Y-%m',
                tickfont=dict(size=16),
            ),
            width=1400,  # Ancho de la imagen
            height=1000,
            margin=dict(t=100),
            modebar_remove=['zoom', 'pan', 'select', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'toggleSpikelines']  # Remover botones no deseados
        )

        # Configurar los ejes
        fig.update_yaxes(title_text="bbl/día", row=1, col=1, secondary_y=False, titlefont=dict(size=14), showgrid=True, gridcolor='lightgray', type='log', gridwidth=1, tickvals=[1,100, 1000, 10000])
        fig.update_yaxes(title_text="%", row=1, col=1, secondary_y=True, titlefont=dict(size=14), showgrid=False)
        fig.update_yaxes(title_text="Pwf (psi)", row=2, col=1, titlefont=dict(size=14), showgrid=True, gridcolor='lightgray')
        fig.update_yaxes(title_text="Conteo Pozos", row=2, col=1, titlefont=dict(size=14), showgrid=False, gridcolor='lightgray', secondary_y=True)
        fig.update_yaxes(title_text="QWI (bbl/día)", row=3, col=1, secondary_y=False, titlefont=dict(size=14), showgrid=True, gridcolor='lightgray')
        fig.update_yaxes(title_text="PWI/Presión (psi)", row=3, col=1, secondary_y=True, titlefont=dict(size=14), showgrid=False)

        return fig, qo_data

    except Exception as e:
        print("Error:", e)
        fig = px.scatter()
        return fig, []

# Gráfico Boxplot (tab_summary)
def update_boxplot(qo_data, start_date, end_date):
    """
    Crea un gráfico boxplot para visualizar la distribución de la tasa de aceite (qo) por fecha.

    Parameters:
    - qo_data: Datos procesados que contienen la tasa de aceite y otros parámetros.
    - start_date: Fecha de inicio para el filtro de datos.
    - end_date: Fecha de fin para el filtro de datos.

    Returns:
    - fig: Objeto de la figura de Plotly que muestra el gráfico boxplot.
    - tab_: Datos formateados para ser usados en una tabla.
    """
    if not qo_data:
        return go.Figure(), []  # Retorna una figura vacía y una lista vacía si no hay datos

    # Convertir los datos de qo a DataFrame y aplicar filtro de fechas
    df_qo = pd.DataFrame(qo_data)
    if start_date and end_date:
        df_qo['FECHA'] = pd.to_datetime(df_qo['FECHA'])
        df_qo = df_qo[(df_qo['FECHA'] >= start_date) & (df_qo['FECHA'] <= end_date)]

    # Crear gráfico de boxplot
    fig = px.box(
        df_qo,
        x='FECHA',
        y='qo',
        color_discrete_sequence=['green']
    )

    # Añadir identificador al hover
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Tasa de Aceite: %{y}<br>Identificador: %{customdata[0]}', customdata=df_qo[['IDENTIFICADOR']])

    # Configurar layout y estilos del gráfico
    fig.update_layout(
        plot_bgcolor='white',  # Fondo del área de trazado
        paper_bgcolor='white',  # Fondo general del gráfico
        xaxis_title='Fecha',
        yaxis_title='Tasa de Aceite (qo)',
        showlegend=False
    )

    # Configurar color de la grilla
    fig.update_xaxes(showgrid=True, gridcolor='lightgray')
    fig.update_yaxes(showgrid=True, gridcolor='lightgray')

    # Preparar datos para la tabla
    tab = df_qo.groupby('FECHA')[['qo', 'ql', 'Wcut']].mean().reset_index()
    tab['FECHA'] = pd.to_datetime(tab['FECHA']).dt.strftime('%d-%m-%Y')
    tab['qo'] = tab['qo'].map('{:,.0f}'.format)  # Formatear 'qo' como entero con comas
    tab['ql'] = tab['ql'].map('{:,.0f}'.format)  # Formatear 'ql' como entero con comas
    tab['Wcut'] = tab['Wcut'].map('{:,.2f}'.format)  # Formatear 'Wcut' como float con dos decimales

    tab_ = tab.to_dict('records')
    return fig, tab_

# ------------------------------------------------------------------------------------------------------------------------------------------------------
