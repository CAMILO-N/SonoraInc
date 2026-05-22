from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # Raíz → login (como cualquier web normal)
    path('', RedirectView.as_view(url='/usuarios/login/'), name='home'),
    path('usuarios/',    include('usuarios.urls')),
    path('catalogo/',    include('catalogo.urls')),
    path('interaccion/', include('interaccion.urls')),
    path('finanzas/',    include('finanzas.urls')),
    path('reportes/',    include('reportes.urls')),
    path('explorar/',    include('explorar.urls')),
]
