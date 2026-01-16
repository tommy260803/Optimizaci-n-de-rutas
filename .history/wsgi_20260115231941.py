from app.app import app

# Convertir la aplicación Dash a WSGI application
application = app.server
