import pyodbc
from datetime import date
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
# PLAYLISTS
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def playlists_lista(request):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            playlists = db.exec('Procesos.sp_ConsultarPlaylists', usuario_id)
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        playlists = []

    return render(request, 'interaccion/playlists.html', {'playlists': playlists})


@login_required
def playlist_nueva(request):
    if request.method == 'POST':
        usuario_id  = request.session['usuario_id']
        nombre      = request.POST.get('nombre', '').strip()
        privacidad  = request.POST.get('privacidad', 'Publica').strip()
        descripcion = request.POST.get('descripcion', '').strip() or None
        fecha       = request.POST.get('fecha', '').strip() or str(date.today())

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return redirect('interaccion:playlists')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_CrearPlaylist',
                    usuario_id, nombre, fecha, privacidad, descripcion
                )
            messages.success(request, f'Playlist "{nombre}" creada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('interaccion:playlists')


@login_required
def playlist_editar(request, id):
    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        privacidad  = request.POST.get('privacidad', 'Publica').strip()
        descripcion = request.POST.get('descripcion', '').strip() or None

        if not nombre:
            messages.error(request, 'El nombre es obligatorio.')
            return redirect('interaccion:playlists')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_ActualizarPlaylist',
                    id, nombre, privacidad, descripcion
                )
            messages.success(request, 'Playlist actualizada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('interaccion:playlists')


@login_required
def playlist_eliminar(request, id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarPlaylist', id)
            messages.success(request, 'Playlist eliminada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('interaccion:playlists')


# ════════════════════════════════════════════════════════════════════════════════
# CANCIONES EN PLAYLIST
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def playlist_canciones(request, id):
    try:
        with DB() as db:
            canciones       = db.exec('Procesos.sp_ConsultarCancionesDePlaylist', id)
            todas_canciones = db.exec('Procesos.sp_ConsultarCanciones')
            playlists       = db.exec('Procesos.sp_ConsultarPlaylists', request.session['usuario_id'])
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        canciones = []
        todas_canciones = []
        playlists = []

    playlist_actual = next((p for p in playlists if p.get('idPlaylist') == id), None)

    return render(request, 'interaccion/playlist_canciones.html', {
        'canciones':       canciones,
        'todas_canciones': todas_canciones,
        'playlist_id':     id,
        'playlist':        playlist_actual,
    })


@login_required
def playlist_agregar_cancion(request, id):
    if request.method == 'POST':
        id_cancion = request.POST.get('id_cancion', '').strip()
        next_url   = request.POST.get('next', '').strip()

        if not id_cancion:
            messages.error(request, 'Selecciona una canción.')
            return redirect(next_url or ('interaccion:playlist_canciones', id))

        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_AgregarCancionPlaylist', id, int(id_cancion))
            messages.success(request, 'Canción agregada a la playlist.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

        if next_url:
            return redirect(next_url)

    return redirect('interaccion:playlist_canciones', id=id)


@login_required
def playlist_eliminar_cancion(request, id_playlist, id_cancion):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarCancionPlaylist', id_playlist, id_cancion)
            messages.success(request, 'Canción eliminada de la playlist.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('interaccion:playlist_canciones', id=id_playlist)


# ════════════════════════════════════════════════════════════════════════════════
# LIKES  (me gusta en canciones)
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def likes_lista(request):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            likes     = db.exec('Procesos.sp_ConsultarLikesUsuario', usuario_id)
            canciones = db.exec('Procesos.sp_ConsultarCanciones')
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        likes     = []
        canciones = []

    return render(request, 'interaccion/likes.html', {
        'likes':     likes,
        'canciones': canciones,
    })


@login_required
def like_toggle(request, id_cancion):
    if request.method == 'POST':
        usuario_id = request.session['usuario_id']
        accion     = request.POST.get('accion', 'dar')

        try:
            with DB() as db:
                if accion == 'quitar':
                    db.exec_noreturn('Procesos.sp_EliminarUsuarioCancion', usuario_id, id_cancion)
                    messages.success(request, 'Me gusta quitado.')
                else:
                    # Toggle: el SP agrega si no existe, quita si ya existe
                    resultado = db.exec_one('Procesos.sp_ToggleLikeCancion', usuario_id, id_cancion)
                    if resultado and resultado.get('accion') == 'quitar':
                        messages.success(request, 'Me gusta quitado.')
                    else:
                        messages.success(request, 'Me gusta registrado.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

        next_url = request.POST.get('next', '').strip()
        if next_url:
            return redirect(next_url)

    return redirect('interaccion:likes')


# ════════════════════════════════════════════════════════════════════════════════
# ARTISTAS SEGUIDOS
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def artistas_seguidos(request):
    usuario_id = request.session['usuario_id']
    busqueda   = request.GET.get('q', '').strip()
    try:
        with DB() as db:
            artistas = db.exec('Procesos.sp_ConsultarArtistas')
            seguidos = db.exec('Procesos.sp_ConsultarUsuarioArtista', usuario_id)
            seguidos_ids = {s['idArtista'] for s in seguidos}

        if busqueda:
            artistas = [a for a in artistas
                        if busqueda.lower() in a['nombreArtista'].lower()]

        # Seguidos primero, luego el resto (ambos grupos en orden alfabético)
        artistas.sort(key=lambda a: (0 if a['idArtista'] in seguidos_ids else 1,
                                     a['nombreArtista']))
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        artistas     = []
        seguidos_ids = set()

    return render(request, 'interaccion/artistas_seguidos.html', {
        'artistas':     artistas,
        'busqueda':     busqueda,
        'seguidos_ids': seguidos_ids,
    })


@login_required
def artista_seguir(request, id):
    if request.method == 'POST':
        usuario_id = request.session['usuario_id']

        try:
            with DB() as db:
                resultado = db.exec_one('Procesos.sp_ToggleSeguirArtista', usuario_id, id)
                if resultado and resultado.get('accion') == 'dejar':
                    messages.success(request, 'Dejaste de seguir a este artista.')
                else:
                    messages.success(request, 'Ahora sigues a este artista.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

        next_url = request.POST.get('next', '').strip()
        if next_url:
            return redirect(next_url)

    return redirect('interaccion:artistas_seguidos')


# ════════════════════════════════════════════════════════════════════════════════
# REPRODUCCIONES
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def reproduccion_registrar(request):
    if request.method == 'POST':
        usuario_id = request.session['usuario_id']
        id_cancion = request.POST.get('id_cancion', '').strip()
        duracion   = request.POST.get('duracion', '').strip()
        fecha      = request.POST.get('fecha', '').strip() or str(date.today())

        if not all([id_cancion, duracion]):
            messages.error(request, 'Canción y duración son obligatorios.')
            return redirect('interaccion:likes')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_RegistrarReproduccion',
                    usuario_id, int(id_cancion), fecha, float(duracion)
                )
            messages.success(request, 'Reproducción registrada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('interaccion:likes')
