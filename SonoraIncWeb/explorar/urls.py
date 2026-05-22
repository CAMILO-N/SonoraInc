from django.urls import path
from . import views

app_name = 'explorar'

urlpatterns = [
    path('',                    views.home,          name='home'),
    path('buscar/',             views.buscar,         name='buscar'),
    path('artistas/<int:artista_id>/',  views.artista_detail, name='artista'),
    path('albumes/<int:album_id>/',     views.album_detail,   name='album'),
]
