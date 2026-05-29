from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/',             views.login_view,                  name='login'),
    path('logout/',            views.logout_view,                  name='logout'),
    path('registro/',          views.registro_view,                name='registro'),
    path('perfil/',            views.perfil_view,                  name='perfil'),
    path('perfil/editar/',     views.perfil_editar_view,           name='perfil_editar'),
    path('perfil/password/',   views.perfil_cambiar_password_view, name='perfil_password'),
    path('perfil/eliminar/',   views.perfil_eliminar_view,         name='perfil_eliminar'),
]
