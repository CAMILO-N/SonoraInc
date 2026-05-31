import pyodbc
from django.shortcuts import render, redirect
from django.contrib import messages
from db.connection import DB, parse_sql_error


# decorador propio porque no se usa django.contrib.auth; la sesion se gestiona manualmente
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def dashboard(request):
    # cada entrada define: clave de contexto, vista SQL, columna de ordenamiento
    secciones = [
        ('canciones_rep',   'Reportes.vCancionesMasReproducidas',  'totalReproducciones'),
        ('actividad',       'Reportes.vActividadUsuarios',          'totalReproducciones'),
        ('canciones_likes', 'Reportes.vCancionesConMasLikes',       'totalLikes'),
        ('artistas_top',    'Reportes.vArtistasMasSeguidos',        'totalSeguidores'),
        ('ingresos',        'Reportes.vIngresosPorSuscripcion',     'totalPagado'),
        ('regalias',        'Reportes.vRegaliasPorCancion',         'totalRegalias'),
        ('por_genero',      'Reportes.vCancionesPorGenero',         'totalCanciones'),
    ]

    # valores por defecto vacios por si falla algun query individual
    ctx = {k: [] for k, _, _ in secciones}

    try:
        with DB() as db:
            # TOP 10 para no saturar el dashboard con tablas enormes
            for key, vista, orden in secciones:
                ctx[key] = db.query(
                    f'SELECT TOP 10 * FROM {vista} ORDER BY {orden} DESC'
                )
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))

    return render(request, 'reportes/dashboard.html', ctx)
