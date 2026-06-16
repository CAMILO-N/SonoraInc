USE SonoraInc;
GO

-- Coleccion Usuario
-- se usan Seguridad.Usuario, Finanzas.Suscripcion,
-- Interaccion.UsuarioArtista, Interaccion.UsuarioCancion e Interaccion.Playlist
-- para consolidar en un solo documento al usuario con sus suscripciones embebidas
-- y sus referencias a artistas, canciones y playlists como arrays de ids.

SELECT
    u.idUsuario AS _id,
    u.nombreUsuario,
    u.apellidoUsuario,
    u.segundoNombreUsuario AS segunNombreUsuario,
    u.segundoApellidoUsuario,
    u.correoUsuario,
    u.fechaRegistroUsuario,
    u.rolUsuario,
    CASE WHEN u.rolUsuario = 'admin'
         THEN 'Admin123Sonora'
         ELSE CONCAT('Sonora', u.idUsuario)
    END AS passwordUsuario,
    (
        SELECT
            s.idSuscripcion,
            s.tipoPlanSuscripcion,
            s.fechaInicioSuscripcion,
            s.fechaFinSuscripcion,
            s.estadoSuscripcion
        FROM Finanzas.Suscripcion s
        WHERE s.Usuario_idUsuario = u.idUsuario
        FOR JSON PATH, INCLUDE_NULL_VALUES
    ) AS Suscripcion,
    (
        SELECT ua.Artista_idArtista AS idArtista
        FROM Interaccion.UsuarioArtista ua
        WHERE ua.Usuario_idUsuario = u.idUsuario
        FOR JSON PATH, INCLUDE_NULL_VALUES
    ) AS idArtista,
    (
        SELECT uc.Cancion_idCancion AS idCancion
        FROM Interaccion.UsuarioCancion uc
        WHERE uc.Usuario_idUsuario = u.idUsuario
        FOR JSON PATH, INCLUDE_NULL_VALUES
    ) AS idCancion,
    (
        SELECT p.idPlaylist
        FROM Interaccion.Playlist p
        WHERE p.Usuario_idUsuario = u.idUsuario
        FOR JSON PATH, INCLUDE_NULL_VALUES
    ) AS idPlaylist
FROM Seguridad.Usuario u
FOR JSON PATH, ROOT('usuarios'), INCLUDE_NULL_VALUES;
GO


-- Coleccion Artista: 
-- se usan Catalogo.Artista y Catalogo.Productora
-- para embeber la informacion de la productora directamente dentro
-- del documento del artist ya que siempre se consultan juntos.

SELECT
    a.idArtista AS _id,
    a.nombreArtista,
    a.paisOrigenArtista,
    a.descripcionArtista,
    JSON_QUERY((
        SELECT
            p.nombreProductora,
            p.correoProductora,
            p.paisProductora
        FROM Catalogo.Productora p
        WHERE p.idProductora = a.Productora_idProductora
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER, INCLUDE_NULL_VALUES
    )) AS Productora
FROM Catalogo.Artista a
FOR JSON PATH, ROOT('artistas'), INCLUDE_NULL_VALUES;

-- Coleccion Album: 
-- se usa Catalogo.Album e Interaccion.ArtistaCancion
-- para obtener el artista principal del album por la cancion

SELECT
    al.idAlbum AS _id,
    al.tituloAlbum,
    al.fechaLanzamientoAlbum,
    JSON_QUERY((
        SELECT TOP 1 ac.Artista_idArtista AS idArtista
        FROM Interaccion.ArtistaCancion ac
        INNER JOIN Catalogo.Cancion c ON ac.Cancion_idCancion = c.idCancion
        WHERE c.Album_idAlbum = al.idAlbum
        GROUP BY ac.Artista_idArtista
        ORDER BY COUNT(*) DESC
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER, INCLUDE_NULL_VALUES
    )) AS idArtista
FROM Catalogo.Album al
FOR JSON PATH, ROOT('albums'), INCLUDE_NULL_VALUES;

-- Coleccion Cancion: 
-- se usan Catalogo.Cancion, Catalogo.Genero
-- e Interaccion.ArtistaCancion para embeber el genero como documento
-- estatico y referenciar los artistas como array de ids,
-- eliminando la tabla intermedia ArtistaCancion.

SELECT
    c.idCancion AS _id,
    c.tituloCancion,
    c.duracionCancion,
    c.idiomaCancion,
    JSON_QUERY((
        SELECT g.nombreGenero
        FROM Catalogo.Genero g
        WHERE g.idGenero = c.Genero_idGenero
        FOR JSON PATH, WITHOUT_ARRAY_WRAPPER, INCLUDE_NULL_VALUES
    )) AS Genero,
    c.Album_idAlbum AS idAlbum,
    JSON_QUERY((
        SELECT ac.Artista_idArtista AS idArtista
        FROM Interaccion.ArtistaCancion ac
        WHERE ac.Cancion_idCancion = c.idCancion
        FOR JSON PATH, INCLUDE_NULL_VALUES
    )) AS idArtista
FROM Catalogo.Cancion c
FOR JSON PATH, ROOT('canciones'), INCLUDE_NULL_VALUES;

-- Coleccion Playlist:
-- se usan Interaccion.Playlist e Interaccion.CancionPlaylist
-- para referenciar al usuario dueno y convertir la tabla intermedia
-- CancionPlaylist en un array de ids dentro del documento de la playlist.

SELECT
    pl.idPlaylist AS _id,
    pl.nombrePlaylist,
    pl.fechaCreacionPlaylist,
    pl.privacidadPlaylist,
    pl.descripcionPlaylist,
    pl.Usuario_idUsuario AS idUsuario,
    (
        SELECT cp.Cancion_idCancion AS idCancion
        FROM Interaccion.CancionPlaylist cp
        WHERE cp.Playlist_idPlaylist = pl.idPlaylist
        FOR JSON PATH, INCLUDE_NULL_VALUES
    ) AS idCancion
FROM Interaccion.Playlist pl
FOR JSON PATH, ROOT('playlists'), INCLUDE_NULL_VALUES;
GO


-- Coleccion Reproduccion: 
-- se usa Interaccion.Reproduccion directamente
-- manteniendo referencias simples a usuario y cancion, ya que es una
-- coleccion de alto volumen transaccional que no debe embeber datos.

SELECT
    r.idReproduccion AS _id,
    r.fechaReproduccion,
    r.duracionReproduccion,
    r.Usuario_idUsuario AS idUsuario,
    r.Cancion_idCancion AS idCancion
FROM Interaccion.Reproduccion r
FOR JSON PATH, ROOT('reproducciones'), INCLUDE_NULL_VALUES;
GO


-- Coleccion Regalia: 
-- se usa Finanzas.Regalia directamente
-- como coleccion independiente referenciando la cancion por id,
-- ya que los registros de regalias crecen con el tiempo y no
-- deben embeberse dentro de la cancion.

SELECT
    rg.idRegalia AS _id,
    rg.Cancion_idCancion AS idCancion,
    rg.fechaCalculoRegalia,
    rg.cantidadReproduccionesRegalia,
    rg.montoGeneradoRegalia
FROM Finanzas.Regalia rg
FOR JSON PATH, ROOT('regalias'), INCLUDE_NULL_VALUES;
GO


-- Coleccion Pago: 
-- se usan Finanzas.Pago y Finanzas.Suscripcion
-- para recuperar el idUsuario a traves de la suscripcion, ya que
-- en SQL Pago no tiene FK directa a Usuario sino a Suscripcion.

SELECT
    p.idPago AS _id,
    s.Usuario_idUsuario AS idUsuario,
    p.Suscripcion_idSuscripcion AS idSuscripcion,
    p.fechaPago,
    p.montoPago
FROM Finanzas.Pago p
INNER JOIN Finanzas.Suscripcion s ON p.Suscripcion_idSuscripcion = s.idSuscripcion
FOR JSON PATH, ROOT('pagos'), INCLUDE_NULL_VALUES;
GO
