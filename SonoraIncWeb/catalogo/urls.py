from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    # Panel admin
    path('',                              views.panel,              name='panel'),
    # Canciones
    path('canciones/',                    views.canciones_lista,    name='canciones'),
    path('canciones/nueva/',              views.cancion_nueva,      name='cancion_nueva'),
    path('canciones/<int:id>/editar/',    views.cancion_editar,     name='cancion_editar'),
    path('canciones/<int:id>/eliminar/',  views.cancion_eliminar,   name='cancion_eliminar'),
    # Artistas
    path('artistas/',                     views.artistas_lista,     name='artistas'),
    path('artistas/nuevo/',               views.artista_nuevo,      name='artista_nuevo'),
    path('artistas/<int:id>/editar/',     views.artista_editar,     name='artista_editar'),
    path('artistas/<int:id>/eliminar/',   views.artista_eliminar,   name='artista_eliminar'),
    # Álbumes
    path('albumes/',                      views.albumes_lista,      name='albumes'),
    path('albumes/nuevo/',                views.album_nuevo,        name='album_nuevo'),
    path('albumes/<int:id>/editar/',      views.album_editar,       name='album_editar'),
    path('albumes/<int:id>/eliminar/',    views.album_eliminar,     name='album_eliminar'),
    # Géneros
    path('generos/',                      views.generos_lista,      name='generos'),
    # Productoras
    path('productoras/',                  views.productoras_lista,  name='productoras'),
    path('productoras/nueva/',            views.productora_nueva,   name='productora_nueva'),
    path('productoras/<int:id>/editar/',  views.productora_editar,  name='productora_editar'),
    path('productoras/<int:id>/eliminar/',views.productora_eliminar,name='productora_eliminar'),
    # Playlists (admin)
    path('playlists/',                    views.playlists_admin,    name='playlists_admin'),
]
