import pyodbc
from datetime import date
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


# SUSCRIPCIONES

@login_required
def suscripciones(request):
    usuario_id = request.session['usuario_id']
    is_admin   = request.session.get('is_admin', False)
    try:
        with DB() as db:
            db.exec_noreturn('Procesos.sp_ActualizarSuscripcionesVencidas')
            if is_admin:
                lista = db.exec('Procesos.sp_ConsultarSuscripciones')
            else:
                lista = db.exec('Procesos.sp_ConsultarSuscripciones', usuario_id)
        activa = None if is_admin else next((s for s in lista if s.get('estadoSuscripcion') == 'Activa'), None)
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        lista  = []
        activa = None

    return render(request, 'finanzas/suscripciones.html', {
        'suscripciones': lista,
        'activa':        activa,
        'is_admin':      is_admin,
    })


_DURACION_PLAN = {'Gratis': 30, 'Premium': 30}


@login_required
def suscripcion_nueva(request):
    if request.method == 'POST':
        from datetime import timedelta
        usuario_id   = request.session['usuario_id']
        tipo_plan    = request.POST.get('tipo_plan', 'Basico').strip()
        hoy          = date.today()
        fecha_inicio = str(hoy)
        fecha_fin    = str(hoy + timedelta(days=_DURACION_PLAN.get(tipo_plan, 30)))
        estado       = 'Activa'

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_RegistrarSuscripcion',
                    usuario_id, tipo_plan, fecha_inicio, fecha_fin, estado
                )
            messages.success(request, f'Suscripción {tipo_plan} activada hasta {fecha_fin}.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('finanzas:suscripciones')


@login_required
def suscripcion_cancelar(request, sub_id):
    if request.method == 'POST':
        usuario_id = request.session['usuario_id']
        try:
            with DB() as db:
                subs = db.exec('Procesos.sp_ConsultarSuscripciones', usuario_id)
                sub  = next((s for s in subs if s.get('idSuscripcion') == sub_id), None)
                if sub:
                    tipo = sub.get('tipoPlanSuscripcion') or sub.get('tipoPlan', 'Basico')
                    fin  = str(sub.get('fechaFinSuscripcion') or sub.get('fechaFin', date.today()))
                    db.exec_noreturn('Procesos.sp_ActualizarSuscripcion', sub_id, tipo, fin, 'Cancelada')
                    messages.success(request, 'Suscripción cancelada.')
                else:
                    messages.error(request, 'Suscripción no encontrada.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('finanzas:suscripciones')


@login_required
def suscripcion_eliminar(request, sub_id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarSuscripcion', sub_id)
            messages.success(request, 'Suscripción eliminada.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('finanzas:suscripciones')


# PAGOS

@login_required
def pagos(request):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            subs_lista  = db.exec('Procesos.sp_ConsultarSuscripciones', usuario_id)
            pagos_lista = []
            for s in subs_lista:
                ps = db.exec('Procesos.sp_ConsultarPagos', s['idSuscripcion'])
                for p in ps:
                    p['_tipoPlan']      = s.get('tipoPlanSuscripcion', s.get('tipoPlan', '—'))
                    p['_idSuscripcion'] = s['idSuscripcion']
                pagos_lista.extend(ps)
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        subs_lista  = []
        pagos_lista = []

    return render(request, 'finanzas/pagos.html', {
        'pagos':         pagos_lista,
        'suscripciones': subs_lista,
    })


@login_required
def pago_nuevo(request):
    if request.method == 'POST':
        id_suscripcion = request.POST.get('id_suscripcion', '').strip()
        fecha          = request.POST.get('fecha', '').strip() or str(date.today())
        monto          = request.POST.get('monto', '').strip()

        if not all([id_suscripcion, monto]):
            messages.error(request, 'Suscripción y monto son obligatorios.')
            return redirect('finanzas:pagos')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_RegistrarPago',
                    int(id_suscripcion), fecha, float(monto)
                )
            messages.success(request, f'Pago de ${monto} registrado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('finanzas:pagos')


@login_required
def pago_eliminar(request, pago_id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarPago', pago_id)
            messages.success(request, 'Pago eliminado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('finanzas:pagos')


# REGALIAS

@login_required
def regalias(request):
    try:
        with DB() as db:
            regalias_lista = db.exec('Procesos.sp_ConsultarRegalias')
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        regalias_lista = []

    return render(request, 'finanzas/regalias.html', {
        'regalias': regalias_lista,
        'hoy':      str(date.today()),
    })


@login_required
def regalias_calcular(request):
    if request.method == 'POST':
        valor_rep   = request.POST.get('valor_rep', '').strip()
        fecha_calc  = request.POST.get('fecha_calc', '').strip() or str(date.today())

        if not valor_rep:
            messages.error(request, 'El valor por reproducción es obligatorio.')
            return redirect('finanzas:regalias')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_CalcularRegaliasGlobal',
                    float(valor_rep), fecha_calc
                )
            messages.success(request, 'Regalias calculadas y actualizadas correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('finanzas:regalias')
