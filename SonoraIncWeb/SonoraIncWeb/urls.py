from django.urls import path, include
from django.views.generic import RedirectView

# no se registra el admin de Django porque la autenticacion es propia con sesiones manuales
urlpatterns = [
    # la raiz redirige al login para que el navegador no muestre una pagina en blanco
    path('', RedirectView.as_view(url='/usuarios/login/'), name='home'),
    path('usuarios/',    include('usuarios.urls')),
    path('catalogo/',    include('catalogo.urls')),
    path('interaccion/', include('interaccion.urls')),
    path('finanzas/',    include('finanzas.urls')),
    path('reportes/',    include('reportes.urls')),
    path('explorar/',    include('explorar.urls')),
]
