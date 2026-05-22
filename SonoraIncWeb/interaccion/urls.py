from django.urls import path
from . import views

app_name = 'interaccion'

urlpatterns = [
    # ── Playlists ─────────────────────────────────────────────────────────────
    path('playlists/',                                              views.playlists_lista,          name='playlists'),
    path('playlists/nueva/',                                        views.playlist_nueva,           name='playlist_nueva'),
    path('playlists/<int:id>/editar/',                              views.playlist_editar,          name='playlist_editar'),
    path('playlists/<int:id>/eliminar/',                            views.playlist_eliminar,        name='playlist_eliminar'),
    path('playlists/<int:id>/canciones/',                           views.playlist_canciones,       name='playlist_canciones'),
    path('playlists/<int:id>/agregar/',                             views.playlist_agregar_cancion, name='playlist_agregar_cancion'),
    path('playlists/<int:id_playlist>/canciones/<int:id_cancion>/eliminar/',
                                                                    views.playlist_eliminar_cancion,name='playlist_eliminar_cancion'),
    # ── Likes ─────────────────────────────────────────────────────────────────
    path('likes/',                                                  views.likes_lista,              name='likes'),
    path('likes/<int:id_cancion>/toggle/',                          views.like_toggle,              name='like_toggle'),
    # ── Artistas seguidos ─────────────────────────────────────────────────────
    path('artistas/',                                               views.artistas_seguidos,        name='artistas_seguidos'),
    path('artistas/<int:id>/seguir/',                               views.artista_seguir,           name='artista_seguir'),
    # ── Reproducciones ───────────────────────────────────────────────────────
    path('reproduccion/registrar/',                                 views.reproduccion_registrar,   name='reproduccion_registrar'),
]
