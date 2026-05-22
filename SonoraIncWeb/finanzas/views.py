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
# SUSCRIPCIONES
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def suscripciones(request):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            suscripciones = db.exec('Procesos.sp_ConsultarSuscripciones', usuario_id)
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        suscripciones = []

    return render(request, 'finanzas/suscripciones.html', {
        'suscripciones': suscripciones,
    })


@login_required
def suscripcion_nueva(request):
    if request.method == 'POST':
        usuario_id   = request.session['usuario_id']
        tipo_plan    = request.POST.get('tipo_plan', '').strip()
        fecha_inicio = request.POST.get('fecha_inicio', '').strip() or str(date.today())
        fecha_fin    = request.POST.get('fecha_fin', '').strip()
        estado       = request.POST.get('estado', 'Activa').strip()

        if not all([tipo_plan, fecha_fin]):
            messages.error(request, 'Plan y fecha de fin son obligatorios.')
            return redirect('finanzas:suscripciones')

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_RegistrarSuscripcion',
                    usuario_id, tipo_plan, fecha_inicio, fecha_fin, estado
                )
            messages.success(request, f'Suscripción "{tipo_plan}" registrada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('finanzas:suscripciones')


@login_required
def suscripcion_editar(request, id):
    if request.method == 'POST':
        tipo_plan = request.POST.get('tipo_plan', '').strip()
        fecha_fin = request.POST.get('fecha_fin', '').strip()
        estado    = request.POST.get('estado', 'Activa').strip()

        try:
            with DB() as db:
                db.exec_noreturn(
                    'Procesos.sp_ActualizarSuscripcion',
                    id, tipo_plan, fecha_fin, estado
                )
            messages.success(request, 'Suscripción actualizada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))

    return redirect('finanzas:suscripciones')


@login_required
def suscripcion_eliminar(request, id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarSuscripcion', id)
            messages.success(request, 'Suscripción eliminada correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('finanzas:suscripciones')


# ════════════════════════════════════════════════════════════════════════════════
# PAGOS
# ════════════════════════════════════════════════════════════════════════════════

@login_required
def pagos(request):
    usuario_id = request.session['usuario_id']
    try:
        with DB() as db:
            suscripciones = db.exec('Procesos.sp_ConsultarSuscripciones', usuario_id)
            # Obtener pagos de todas las suscripciones del usuario
            pagos_lista = []
            for s in suscripciones:
                ps = db.exec('Procesos.sp_ConsultarPagos', s['idSuscripcion'])
                for p in ps:
                    # Anotar a qué suscripcion pertenece este pago
                    p['_tipoPlan'] = s.get('tipoPlanSuscripcion', s.get('tipoPlan', '—'))
                    p['_idSuscripcion'] = s['idSuscripcion']
                pagos_lista.extend(ps)
    except pyodbc.Error as e:
        messages.error(request, parse_sql_error(e))
        suscripciones = []
        pagos_lista   = []

    return render(request, 'finanzas/pagos.html', {
        'pagos':          pagos_lista,
        'suscripciones':  suscripciones,
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
def pago_eliminar(request, id):
    if request.method == 'POST':
        try:
            with DB() as db:
                db.exec_noreturn('Procesos.sp_EliminarPago', id)
            messages.success(request, 'Pago eliminado correctamente.')
        except pyodbc.Error as e:
            messages.error(request, parse_sql_error(e))
    return redirect('finanzas:pagos')


# ════════════════════════════════════════════════════════════════════════════════
# REGALIAS
# ════════════════════════════════════════════════════════════════════════════════

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
