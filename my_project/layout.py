import dash_bootstrap_components as dbc
from dash import dcc, html


def footer():
    """
    Crea y retorna el pie de página (footer) de la aplicación.

    El pie de página incluye el logo de la empresa, información sobre la aplicación
    ReserVision, el nombre del desarrollador y enlaces de contacto.

    Retorna:
        dbc.Row: Una fila de Dash Bootstrap Components que contiene el contenido del pie de página.
    """
    return dbc.Row(
        align="center",
        justify="between",
        id="footer-container",
        children=[
            dbc.Col(
                children=[
                    dbc.Row(
                        html.A(
                            children=[
                                html.Img(
                                    src="assets/img/cbe-logo-small.png",
                                )
                            ],
                        )
                    ),
                ],
                width=12,
                md=4,
                style={"padding": "15px"},
            ),
            dbc.Col(
                children=[
                    dbc.Row(
                        [
                            dcc.Markdown(
                                """
                                ### Acerca de ReserVision

                                **Desarrollado por:** Jesús Iván Pacheco Romero  
                                **Aplicación:** *ReserVision*: Una aplicación web para el análisis del comportamiento de pozos productores en relación con la inyección de agua.  
                                **Contacto:** [jesus.pacheco.rom@gmail.com](mailto:jesus.pacheco.rom@gmail.com)  
                                **GitHub:** [Jesús Iván Pacheco Romero](https://github.com/tu-github-username)

                                """
                            ),
                            dcc.Markdown(
                                """
                                """,
                                style={"marginTop": "1rem"},
                            ),
                        ],
                        style={"marginTop": "1rem"},
                    ),
                ],
                width=12,
                md=8,
            ),
        ],
    )


def banner():
    """
    Construye y retorna el banner de la parte superior de la página.

    El banner contiene el logo de la empresa, el título principal "ReserVision" y un lema.
    También incluye dos elementos de selección de valores (Global/Local y SI/IP).

    Retorna:
        html.Div: Un div que contiene el banner con el título y los controles.
    """
    return html.Div(
        id="banner",
        children=[
            dbc.Row(
                align="center",
                children=[
                    dbc.Col(
                        html.A(
                            href="/",
                            children=[
                                html.Img(
                                    src="assets/img/cbe-logo-small.png",
                                ),
                            ],
                        ),
                        width="auto",
                    ),
                    dbc.Col(
                        children=[
                            html.H1(
                                id="banner-title", 
                                children=["ReserVision"],
                                style={"font-size": "5rem"}  # Tamaño del título principal
                            ),
                            html.H2(
                                id="slogan",
                                children=["Inyección Inteligente, Producción Eficiente"],
                                style={"font-size": "2rem", "font-weight": "normal", "margin-top": "0.5rem"}  # Ajusta el tamaño y estilo del lema
                            ),
                        ],
                    ),
                    dbc.Col(
                        style={"fontWeight": "700", "padding": "1rem"},
                        align="end",
                        children=[
                            dbc.Row(
                                style={"text-align": "right"},
                                children=[
                                    dbc.RadioItems(
                                        options=[
                                            {
                                                "label": "Global Value Ranges",
                                                "value": "global",
                                            },
                                            {
                                                "label": "Local Value Ranges",
                                                "value": "local",
                                            },
                                        ],
                                        value="local",
                                        id="global-local-radio-input",
                                        inline=True,
                                    ),
                                ],
                            ),
                            dbc.Row(
                                align="end",
                                style={"text-align": "right"},
                                children=[
                                    dbc.RadioItems(
                                        options=[
                                            {"label": "SI", "value": "si"},
                                            {"label": "IP", "value": "ip"},
                                        ],
                                        value="si",
                                        id="si-ip-radio-input",
                                        inline=True,
                                    ),
                                ],
                            ),
                        ],
                        width="auto",
                    ),
                ],
            ),
        ],
    )


def build_tabs():
    """
    Construye y retorna las pestañas (tabs) de la aplicación.

    Estas pestañas permiten al usuario navegar entre las diferentes secciones de la aplicación, como "Patrones de Inyección",
    "Estadística Patrón", "Comportamiento Patrones" y "Conectividad Inyector-Productor".

    Retorna:
        html.Div: Un div que contiene las pestañas de la aplicación.
    """
    return html.Div(
        id="tabs-container",
        children=[
            dcc.Tabs(
                id="tabs",
                parent_className="custom-tabs",
                value="tab-select",
                children=[
                    dcc.Tab(
                        label="Patrones de Inyección",
                        value="tab-select",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="tab-summary",
                        label="Estadística Patrón",
                        value="tab-summary",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        disabled=False,
                    ),
                    dcc.Tab(
                        id="tab-behavior",
                        label="Comportamiento Patrones",
                        value="tab-behavior",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        disabled=False,
                    ),
                    dcc.Tab(
                        id="tab-conn",
                        label="Conectividad Inyector-Productor",
                        value="tab-conn",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                        disabled=False,
                    ),
                ],
            ),
            html.Div(
                id="store-container",
                children=[store(), html.Div(id="tabs-content")],
            ),
        ],
    )


def store():
    """
    Crea y retorna los componentes de almacenamiento (store) de la aplicación.

    Estos almacenes permiten guardar datos persistentes a lo largo de la sesión de la aplicación.
    El componente Loading muestra una animación de carga mientras los datos se almacenan o recuperan.

    Retorna:
        html.Div: Un div que contiene los componentes de almacenamiento de la aplicación.
    """
    return html.Div(
        id="store",
        children=[
            dcc.Loading(
                [
                    dcc.Store(id="df-store", storage_type="session"),
                    dcc.Store(id="meta-store", storage_type="session"),
                    dcc.Store(id="url-store", storage_type="session"),
                    dcc.Store(id="si-ip-unit-store", storage_type="session"),
                    dcc.Store(id="lines-store", storage_type="session"),
                ],
                fullscreen=True,
                type="dot",
            )
        ],
    )
