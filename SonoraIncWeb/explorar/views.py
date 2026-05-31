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

# pagina principal del usuario autenticado
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


@login_required
def buscar(request):
    q          = request.GET.get('q', '').strip()
    usuario_id = request.session['usuario_id']
    artistas   = []
    albumes    = []
    canciones  = []
    playlists  = []

    liked_ids = set()
    try:
        with DB() as db:
            # likes y playlists se cargan siempre para que el template pueda marcar canciones
            playlists = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)
            likes     = db.exec('Procesos.sp_ConsultarLikesUsuario', usuario_id)
            liked_ids = {l['idCancion'] for l in likes}
            if q:
                # el filtrado se hace en Python porque no hay SP de busqueda parametrizada
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
        'liked_ids': liked_ids,
    })


@login_required
def artista_detail(request, artista_id):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            # no existe sp_ConsultarArtistaPorId, se filtra desde la lista completa
            todos_artistas  = db.exec('Procesos.sp_ConsultarArtistas')
            artista         = next((a for a in todos_artistas if a['idArtista'] == artista_id), None)
            canciones       = db.exec('Procesos.sp_ConsultarCancionesArtista', artista_id)
            albumes_artista = db.exec('Procesos.sp_ConsultarAlbumesPorArtista', artista_id)
            playlists       = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)
            likes           = db.exec('Procesos.sp_ConsultarLikesUsuario', usuario_id)
            seguidos        = db.exec('Procesos.sp_ConsultarUsuarioArtista', usuario_id)
            # sets para O(1) al marcar canciones y artistas en el template
            liked_ids    = {l['idCancion'] for l in likes}
            seguidos_ids = {s['idArtista'] for s in seguidos}
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        artista         = None
        canciones       = []
        albumes_artista = []
        playlists       = []
        liked_ids       = set()
        seguidos_ids    = set()

    return render(request, 'explorar/artista.html', {
        'artista':         artista,
        'canciones':       canciones,
        'albumes_artista': albumes_artista,
        'playlists':       playlists,
        'liked_ids':       liked_ids,
        'seguidos_ids':    seguidos_ids,
    })


@login_required
def album_detail(request, album_id):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            # idem artista_detail: se filtra en Python por ausencia de SP especifico
            todos_albumes = db.exec('Procesos.sp_ConsultarAlbumes')
            album         = next((a for a in todos_albumes if a['idAlbum'] == album_id), None)
            canciones     = db.exec('Procesos.sp_ConsultarCancionesAlbum', album_id)
            playlists     = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)
            likes         = db.exec('Procesos.sp_ConsultarLikesUsuario', usuario_id)
            liked_ids     = {l['idCancion'] for l in likes}
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        album     = None
        canciones = []
        playlists = []
        liked_ids = set()

    return render(request, 'explorar/album.html', {
        'album':      album,
        'canciones':  canciones,
        'playlists':  playlists,
        'liked_ids':  liked_ids,
    })
