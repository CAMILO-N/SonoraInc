import pyodbc
from django.shortcuts import render, redirect
from django.contrib import messages
from db.connection import DB, parse_sql_error


# Decorador de sesión
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# DASHBOARD  — consulta las 7 vistas del esquema Reportes

@login_required
def dashboard(request):
    # Mapeo clave → vista SQL (TOP 10 filas de cada una)
    secciones = {
        'canciones_rep':   'Reportes.vCancionesMasReproducidas',
        'actividad':       'Reportes.vActividadUsuarios',
        'canciones_likes': 'Reportes.vCancionesConMasLikes',
        'artistas_top':    'Reportes.vArtistasMasSeguidos',
        'ingresos':        'Reportes.vIngresosPorSuscripcion',
        'regalias':        'Reportes.vRegaliasPorCancion',
        'por_genero':      'Reportes.vCancionesPorGenero',
    }

    ctx = {k: [] for k in secciones}

    try:
        with DB() as db:
            for key, vista in secciones.items():
                ctx[key] = db.query(f'SELECT TOP 10 * FROM {vista}')
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))

    return render(request, 'reportes/dashboard.html', ctx)
