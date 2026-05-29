import pyodbc
from django.shortcuts import render, redirect
from django.contrib import messages
from db.connection import DB, parse_sql_error


# Decoradores de sesión y rol
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Solo administradores pueden ejecutar operaciones de escritura en el catálogo."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('usuarios:login')
        if not request.session.get('is_admin'):
            messages.error(request, 'No tienes permisos para realizar esta acción.')
            return redirect('usuarios:perfil')
        return view_func(request, *args, **kwargs)
    return wrapper


# CANCIONES

@login_required
def canciones_lista(request):
    busqueda = request.GET.get('q', '').strip()
    try:
        with DB() as db:
            canciones = db.exec('Procesos.sp_ConsultarCanciones')
            generos   = db.exec('Procesos.sp_ConsultarGeneros')
            albumes   = db.exec('Procesos.sp_ConsultarAlbumes')

        # Filtro por búsqueda en Python (simple, sin SP extra)
        if busqueda:
            canciones = [c for c in canciones
                         if busqueda.lower() in c['tituloCancion'].lower()]
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        canciones = []
        generos   = []
        albumes   = []

    return render(request, 'catalogo/canciones.html', {
        'canciones': canciones,
        'generos':   generos,
        'albumes':   albumes,
        'busqueda':  busqueda,
    })


@admin_required
def cancion_nueva(request):
    if request.method == 'POST':
        titulo    = request.POST.get('titulo', '').strip()
        duracion  = request.POST.get('duracion', '').strip()
        id_genero = request.POST.get('id_genero', '').strip()
        id_album  = request.POST.get('id_album', '').strip()

        if not all([titulo, duracion, id_genero, id_album]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('catalogo:canciones')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_InsertarCancion',
                    titulo,
                    float(duracion),
                    int(id_genero),
                    int(id_album)
                )
            messages.success(request, f'Canción "{titulo}" creada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:canciones')


@admin_required
def cancion_editar(request, id):
    if request.method == 'POST':
        titulo    = request.POST.get('titulo', '').strip()
        duracion  = request.POST.get('duracion', '').strip()
        id_genero = request.POST.get('id_genero', '').strip()
        id_album  = request.POST.get('id_album', '').strip()

        if not all([titulo, duracion, id_genero, id_album]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('catalogo:canciones')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_ActualizarCancion',
                    id,
                    titulo,
                    float(duracion),
                    int(id_genero),
                    int(id_album)
                )
            messages.success(request, 'Canción actualizada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:canciones')


@admin_required
def cancion_eliminar(request, id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarCancion', id)
            messages.success(request, 'Canción eliminada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('catalogo:canciones')


# ARTISTAS

@login_required
def artistas_lista(request):
    busqueda = request.GET.get('q', '').strip()
    try:
        with DB() as db:
            artistas    = db.exec('Procesos.sp_ConsultarArtistas')
            productoras = db.exec('Procesos.sp_ConsultarProductoras')

        if busqueda:
            artistas = [a for a in artistas
                        if busqueda.lower() in a['nombreArtista'].lower()]
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        artistas    = []
        productoras = []

    return render(request, 'catalogo/artistas.html', {
        'artistas':    artistas,
        'productoras': productoras,
        'busqueda':    busqueda,
    })


@admin_required
def artista_nuevo(request):
    if request.method == 'POST':
        nombre       = request.POST.get('nombre', '').strip()
        pais         = request.POST.get('pais', '').strip()
        descripcion  = request.POST.get('descripcion', '').strip() or None
        id_productora= request.POST.get('id_productora', '').strip()

        if not all([nombre, pais, id_productora]):
            messages.error(request, 'Nombre, país y productora son obligatorios.')
            return redirect('catalogo:artistas')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_InsertarArtista',
                    nombre, pais, descripcion, int(id_productora)
                )
            messages.success(request, f'Artista "{nombre}" creado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:artistas')


@admin_required
def artista_editar(request, id):
    if request.method == 'POST':
        nombre        = request.POST.get('nombre', '').strip()
        pais          = request.POST.get('pais', '').strip()
        descripcion   = request.POST.get('descripcion', '').strip() or None
        id_productora = request.POST.get('id_productora', '').strip()

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_ActualizarArtista',
                    id, nombre, pais, descripcion, int(id_productora)
                )
            messages.success(request, 'Artista actualizado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:artistas')


@admin_required
def artista_eliminar(request, id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarArtista', id)
            messages.success(request, 'Artista eliminado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('catalogo:artistas')


# ÁLBUMES

@login_required
def albumes_lista(request):
    try:
        with DB() as db:
            albumes  = db.exec('Procesos.sp_ConsultarAlbumes')
            artistas = db.exec('Procesos.sp_ConsultarArtistas')
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        albumes  = []
        artistas = []

    return render(request, 'catalogo/albumes.html', {
        'albumes':  albumes,
        'artistas': artistas,
    })


@admin_required
def album_nuevo(request):
    if request.method == 'POST':
        titulo      = request.POST.get('titulo', '').strip()
        fecha       = request.POST.get('fecha', '').strip()

        if not all([titulo, fecha]):
            messages.error(request, 'Título y fecha son obligatorios.')
            return redirect('catalogo:albumes')

        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_InsertarAlbum', titulo, fecha)
            messages.success(request, f'Álbum "{titulo}" creado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:albumes')


@admin_required
def album_editar(request, id):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        fecha  = request.POST.get('fecha', '').strip()

        if not all([titulo, fecha]):
            messages.error(request, 'Título y fecha son obligatorios.')
            return redirect('catalogo:albumes')

        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_ActualizarAlbum', id, titulo, fecha)
            messages.success(request, 'Álbum actualizado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:albumes')


@admin_required
def album_eliminar(request, id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarAlbum', id)
            messages.success(request, 'Álbum eliminado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('catalogo:albumes')


# GÉNEROS

@login_required
def generos_lista(request):
    try:
        with DB() as db:
            generos = db.exec('Procesos.sp_ConsultarGeneros')
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        generos = []

    return render(request, 'catalogo/generos.html', {'generos': generos})


# PANEL ADMIN

@admin_required
def panel(request):
    try:
        with DB() as db:
            total_canciones  = len(db.exec('Procesos.sp_ConsultarCanciones'))
            total_artistas   = len(db.exec('Procesos.sp_ConsultarArtistas'))
            total_albumes    = len(db.exec('Procesos.sp_ConsultarAlbumes'))
            total_productoras= len(db.exec('Procesos.sp_ConsultarProductoras'))
            total_playlists  = len(db.exec('Procesos.sp_ConsultarPlaylists'))
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        total_canciones = total_artistas = total_albumes = total_productoras = total_playlists = '—'

    return render(request, 'catalogo/panel.html', {
        'total_canciones':   total_canciones,
        'total_artistas':    total_artistas,
        'total_albumes':     total_albumes,
        'total_productoras': total_productoras,
        'total_playlists':   total_playlists,
    })


# PRODUCTORAS

@admin_required
def productoras_lista(request):
    try:
        with DB() as db:
            productoras = db.exec('Procesos.sp_ConsultarProductoras')
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        productoras = []

    return render(request, 'catalogo/productoras.html', {'productoras': productoras})


@admin_required
def productora_nueva(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        pais   = request.POST.get('pais', '').strip()
        correo = request.POST.get('correo', '').strip()

        if not all([nombre, pais, correo]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('catalogo:productoras')

        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_InsertarProductora', nombre, pais, correo)
            messages.success(request, f'Productora "{nombre}" creada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:productoras')


@admin_required
def productora_editar(request, id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        pais   = request.POST.get('pais', '').strip()
        correo = request.POST.get('correo', '').strip()

        if not all([nombre, pais, correo]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('catalogo:productoras')

        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_ActualizarProductora', id, nombre, pais, correo)
            messages.success(request, 'Productora actualizada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('catalogo:productoras')


@admin_required
def productora_eliminar(request, id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarProductora', id)
            messages.success(request, 'Productora eliminada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('catalogo:productoras')


# PLAYLISTS (vista admin — todas las playlists de todos los usuarios)

@admin_required
def playlists_admin(request):
    try:
        with DB() as db:
            playlists = db.exec('Procesos.sp_ConsultarPlaylists')
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        playlists = []

    return render(request, 'catalogo/playlists_admin.html', {'playlists': playlists})
