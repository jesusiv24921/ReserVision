import dash_bootstrap_components as dbc
from dash_extensions.enrich import DashProxy, ServersideOutputTransform

app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    transforms=[ServersideOutputTransform()],
    suppress_callback_exceptions=True,
)
TIMEOUT = 600

app.index_string = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="Jesús Iván Pacheco Romero">
    <meta name="keywords" content="Análisis de inyección, Producción de pozos, Machine Learning, Campos petroleros">
    <meta name="description" content="Esta aplicación web está diseñada para monitorear y analizar el comportamiento de patrones de inyección y producción en campos petroleros. Permite revisar posibles daños en los pozos y utiliza machine learning para encontrar similitudes entre fluidos inyectados y producidos.">
    <title>ReserVision</title>
    <link rel="manifest" href="./assets/manifest.json">
    <meta name="theme-color" content="#003262" />
    <meta property="og:image" content="./assets/imagen-app.png">
    <meta property="og:description" content="Una herramienta web para el monitoreo y análisis de inyección y producción en campos petroleros.">
    <meta property="og:title" content="Monitor de Inyección y Producción">
    {%favicon%}
    {%css%}
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
"""
