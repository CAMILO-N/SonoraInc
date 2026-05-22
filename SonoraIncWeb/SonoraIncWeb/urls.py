from django.urls import path, include

urlpatterns = [
    path('usuarios/', include('usuarios.urls')),
    path('catalogo/', include('catalogo.urls')),    # ← agregar esta línea
]
