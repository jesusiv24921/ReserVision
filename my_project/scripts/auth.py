import dash_auth

# Lista de usuarios y contraseñas (esto debe almacenarse de forma segura en una aplicación real)
VALID_USERNAME_PASSWORD_PAIRS = {
    'jesuspacheco': '26Amarillo3*',
    'visitante': '26Rojo3*'
}

def authenticate(app):
    """
    Función para agregar autenticación básica a la aplicación Dash.
    """
    # Configurar la autenticación básica con dash-auth
    auth = dash_auth.BasicAuth(
        app,
        VALID_USERNAME_PASSWORD_PAIRS
    )
    return auth
