import hashlib
import pyodbc
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from db.connection import DB, parse_sql_error


def _hash(password: str) -> str:
    # SHA2_256 en mayusculas para que coincida con HASHBYTES de SQL Server
    return hashlib.sha256(password.encode()).hexdigest().upper()


def login_view(request):
    # redirige al perfil si ya hay sesion activa para evitar doble login
    if request.session.get('usuario_id'):
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        correo   = request.POST.get('correo', '').strip()
        password = request.POST.get('password', '')

        if not correo or not password:
            messages.error(request, 'Completa todos los campos.')
            return render(request, 'usuarios/login.html')

        try:
            with DB() as db:
                usuario = db.exec_one(
                    'Procesos.sp_IniciarSesion',
                    correo,
                    _hash(password)
                )
            if not usuario:
                messages.error(request, 'Credenciales incorrectas.')
                return render(request, 'usuarios/login.html')

            request.session['usuario_id']     = usuario['idUsuario']
            request.session['usuario_nombre'] = usuario['nombreUsuario']
            request.session['usuario_correo'] = usuario['correoUsuario']
            # el SP puede devolver 'rolUsuario' o 'rol' segun la version del esquema
            rol = str(usuario.get('rolUsuario') or usuario.get('rol') or '').lower()
            request.session['is_admin'] = (rol == 'admin')
            messages.success(request, f"Bienvenido, {usuario['nombreUsuario']}.")
            return redirect('explorar:home')

        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return render(request, 'usuarios/login.html')


def logout_view(request):
    # flush elimina toda la sesion, no solo las claves propias de la app
    request.session.flush()
    messages.success(request, 'Sesión cerrada.')
    return redirect('usuarios:login')


def registro_view(request):
    # un usuario autenticado no deberia poder crear otra cuenta desde el mismo navegador
    if request.session.get('usuario_id'):
        return redirect('usuarios:perfil')

    if request.method == 'POST':
        nombre      = request.POST.get('nombre', '').strip()
        # segundo nombre y segundo apellido son opcionales; None en lugar de cadena vacia
        seg_nombre  = request.POST.get('seg_nombre', '').strip() or None
        apellido    = request.POST.get('apellido', '').strip()
        seg_apellido= request.POST.get('seg_apellido', '').strip() or None
        correo      = request.POST.get('correo', '').strip()
        password    = request.POST.get('password', '')
        password2   = request.POST.get('password2', '')
        # fecha de registro siempre es hoy, no se expone al usuario
        fecha       = str(date.today())

        errores = []
        if not all([nombre, apellido, correo, password]):
            errores.append('Todos los campos son obligatorios.')
        if password != password2:
            errores.append('Las contraseñas no coinciden.')
        if len(password) < 6:
            errores.append('La contraseña debe tener mínimo 6 caracteres.')

        if errores:
            for e in errores:
                messages.error(request, e)
            return render(request, 'usuarios/registro.html', {'post': request.POST})

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_RegistrarUsuario',
                    nombre, apellido,
                    seg_nombre, seg_apellido,
                    correo, fecha,
                    _hash(password)
                )
            messages.success(request, 'Cuenta creada. Ya puedes iniciar sesión.')
            return redirect('usuarios:login')

        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
            return render(request, 'usuarios/registro.html', {'post': request.POST})

    return render(request, 'usuarios/registro.html')


def perfil_view(request):
    if not request.session.get('usuario_id'):
        return redirect('usuarios:login')

    usuario_id  = request.session['usuario_id']
    usuario     = None
    suscripcion = None
    try:
        with DB() as db:
            usuario = db.exec_one('Procesos.sp_ConsultarUsuarios', usuario_id)
            subs    = db.exec('Procesos.sp_ConsultarSuscripciones', usuario_id)
            # solo se muestra la suscripcion activa; las vencidas o canceladas se ignoran aqui
            suscripcion = next((s for s in subs if s.get('estadoSuscripcion') == 'Activa'), None)
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))

    return render(request, 'usuarios/perfil.html', {
        'usuario':     usuario,
        'suscripcion': suscripcion,
    })


def perfil_editar_view(request):
    if not request.session.get('usuario_id'):
        return redirect('usuarios:login')

    if request.method == 'POST':
        usuario_id   = request.session['usuario_id']
        nombre       = request.POST.get('nombre', '').strip()
        apellido     = request.POST.get('apellido', '').strip()
        seg_nombre   = request.POST.get('seg_nombre', '').strip() or None
        seg_apellido = request.POST.get('seg_apellido', '').strip() or None
        correo       = request.POST.get('correo', '').strip()

        if not all([nombre, apellido, correo]):
            messages.error(request, 'Nombre, apellido y correo son obligatorios.')
            return redirect('usuarios:perfil')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_ActualizarUsuario',
                    usuario_id, nombre, apellido, seg_nombre, seg_apellido, correo
                )
            # se actualiza la sesion para que el navbar refleje los nuevos datos sin relogin
            request.session['usuario_nombre'] = nombre
            request.session['usuario_correo'] = correo
            messages.success(request, 'Perfil actualizado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('usuarios:perfil')


def perfil_cambiar_password_view(request):
    if not request.session.get('usuario_id'):
        return redirect('usuarios:login')

    if request.method == 'POST':
        usuario_id  = request.session['usuario_id']
        actual      = request.POST.get('password_actual', '')
        nueva       = request.POST.get('password_nueva', '')
        nueva2      = request.POST.get('password_nueva2', '')

        if not all([actual, nueva, nueva2]):
            messages.error(request, 'Completa todos los campos.')
            return redirect('usuarios:perfil')
        if nueva != nueva2:
            messages.error(request, 'Las contraseñas nuevas no coinciden.')
            return redirect('usuarios:perfil')
        if len(nueva) < 6:
            messages.error(request, 'La nueva contraseña debe tener mínimo 6 caracteres.')
            return redirect('usuarios:perfil')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_CambiarContrasenaUsuario',
                    usuario_id, _hash(actual), _hash(nueva)
                )
            messages.success(request, 'Contraseña cambiada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('usuarios:perfil')


def perfil_eliminar_view(request):
    if not request.session.get('usuario_id'):
        return redirect('usuarios:login')

    if request.method == 'POST':
        usuario_id = request.session['usuario_id']
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarUsuario', usuario_id)
            # se invalida la sesion despues de borrar para que no quede un fantasma logueado
            request.session.flush()
            messages.success(request, 'Tu cuenta ha sido eliminada.')
            return redirect('usuarios:login')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('usuarios:perfil')
