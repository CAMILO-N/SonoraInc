import pyodbc
from django.shortcuts import render, redirect
from django.contrib import messages
from db.connection import DB, parse_sql_error


# ── Decorador de sesión ───────────────────────────────────────────────────────
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ════════════════════════════════════════════════════════════════════════════════
# HOME  — página principal del usuario autenticado
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def home(request):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            artistas  = db.exec('Procesos.sp_ConsultarArtistas')
            albumes   = db.exec('Procesos.sp_ConsultarAlbumes')
            playlists = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        artistas  = []
        albumes   = []
        playlists = []

    return render(request, 'explorar/home.html', {
        'artistas':  artistas,
        'albumes':   albumes,
        'playlists': playlists,
    })


# ════════════════════════════════════════════════════════════════════════════════
# BÚSQUEDA  — busca artistas, álbumes y canciones
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def buscar(request):
    q          = request.GET.get('q', '').strip()
    usuario_id = request.session['usuario_id']
    artistas   = []
    albumes    = []
    canciones  = []
    playlists  = []

    try:
        with DB() as db:
            playlists = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)
            if q:
                ql = q.lower()
                todos_artistas  = db.exec('Procesos.sp_ConsultarArtistas')
                todos_albumes   = db.exec('Procesos.sp_ConsultarAlbumes')
                todas_canciones = db.exec('Procesos.sp_ConsultarCanciones')
                artistas  = [a for a in todos_artistas  if ql in a['nombreArtista'].lower()]
                albumes   = [a for a in todos_albumes   if ql in a['tituloAlbum'].lower()]
                canciones = [c for c in todas_canciones if ql in c['tituloCancion'].lower()]
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))

    return render(request, 'explorar/buscar.html', {
        'q':         q,
        'artistas':  artistas,
        'albumes':   albumes,
        'canciones': canciones,
        'playlists': playlists,
    })


# ════════════════════════════════════════════════════════════════════════════════
# DETALLE DE ARTISTA  — info, canciones y seguir/dejar de seguir
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def artista_detail(request, artista_id):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            todos_artistas = db.exec('Procesos.sp_ConsultarArtistas')
            artista        = next((a for a in todos_artistas if a['idArtista'] == artista_id), None)

            # Canciones del artista via SP (evita problema de permisos en tablas directas)
            canciones = db.exec('Procesos.sp_ConsultarCancionesArtista', artista_id)

            playlists = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)

    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        artista   = None
        canciones = []
        playlists = []

    return render(request, 'explorar/artista.html', {
        'artista':   artista,
        'canciones': canciones,
        'playlists': playlists,
    })


# ════════════════════════════════════════════════════════════════════════════════
# DETALLE DE ÁLBUM  — info y canciones del álbum
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def album_detail(request, album_id):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            todos_albumes = db.exec('Procesos.sp_ConsultarAlbumes')
            album         = next((a for a in todos_albumes if a['idAlbum'] == album_id), None)

            # Filtrar canciones del álbum desde el SP general (evita SELECT directo a tablas)
            todas_canciones = db.exec('Procesos.sp_ConsultarCanciones')
            canciones = [c for c in todas_canciones if c.get('Album_idAlbum') == album_id]

            playlists = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)

    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        album     = None
        canciones = []
        playlists = []

    return render(request, 'explorar/album.html', {
        'album':     album,
        'canciones': canciones,
        'playlists': playlists,
    })
