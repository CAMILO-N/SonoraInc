from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    # ── Suscripciones ─────────────────────────────────────────────────────────
    path('suscripciones/',                      views.suscripciones,        name='suscripciones'),
    path('suscripciones/nueva/',                views.suscripcion_nueva,    name='suscripcion_nueva'),
    path('suscripciones/<int:id>/editar/',      views.suscripcion_editar,   name='suscripcion_editar'),
    path('suscripciones/<int:id>/eliminar/',    views.suscripcion_eliminar, name='suscripcion_eliminar'),
    # ── Pagos ─────────────────────────────────────────────────────────────────
    path('pagos/',                              views.pagos,                name='pagos'),
    path('pagos/nuevo/',                        views.pago_nuevo,           name='pago_nuevo'),
    path('pagos/<int:id>/eliminar/',            views.pago_eliminar,        name='pago_eliminar'),
    # ── Regalias ──────────────────────────────────────────────────────────────
    path('regalias/',                           views.regalias,             name='regalias'),
    path('regalias/calcular/',                  views.regalias_calcular,    name='regalias_calcular'),
]
