-- ============================================================
-- Stored procedure: canciones de un artista específico
-- Ejecutar en SQL Server Management Studio conectado a SonoraInc
-- ============================================================

USE SonoraInc;
GO

CREATE OR ALTER PROCEDURE Procesos.sp_ConsultarCancionesArtista
    @idArtista INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        c.idCancion,
        c.tituloCancion,
        c.duracionCancion,
        g.nombreGenero,
        al.tituloAlbum,
        al.idAlbum
    FROM   Interaccion.ArtistaCancion ac
    JOIN   Catalogo.Cancion  c  ON ac.Cancion_idCancion = c.idCancion
    LEFT JOIN Catalogo.Genero  g  ON c.Genero_idGenero  = g.idGenero
    LEFT JOIN Catalogo.Album   al ON c.Album_idAlbum    = al.idAlbum
    WHERE  ac.Artista_idArtista = @idArtista;
END;
GO

-- Dar permiso de ejecución al usuario de la app
GRANT EXECUTE ON Procesos.sp_ConsultarCancionesArtista TO SonoraApp;
GO
