use("SonoraIncDB");

// -- Seccion 1: Creacion de Colecciones con Validadores e Indices --



db.createCollection("usuarios", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "nombreUsuario", "apellidoUsuario", "correoUsuario",
        "fechaRegistroUsuario", "rolUsuario", "Suscripcion"],
      properties: {
        _id: { bsonType: "int" },
        nombreUsuario: { bsonType: "string" },
        apellidoUsuario: { bsonType: "string" },
        segunNombreUsuario: { bsonType: "string" },
        segundoApellidoUsuario: { bsonType: "string" },
        correoUsuario: { bsonType: "string" },
        fechaRegistroUsuario: { bsonType: "date" },
        rolUsuario: { bsonType: "string", enum: ["admin", "usuario"] },
        passwordUsuario: { bsonType: "string" },
        Suscripcion: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["tipoPlanSuscripcion", "fechaInicioSuscripcion", "estadoSuscripcion"],
            properties: {
              idSuscripcion: { bsonType: "int" },
              tipoPlanSuscripcion: { bsonType: "string", enum: ["Gratis", "Premium"] },
              fechaInicioSuscripcion: { bsonType: "date" },
              fechaFinSuscripcion: { bsonType: "date" },
              estadoSuscripcion: { bsonType: "string", enum: ["Activa", "Cancelada", "Vencida"] },
            },
          },
        },
        idArtista: { bsonType: "array", items: { bsonType: "int" } },
        idCancion: { bsonType: "array", items: { bsonType: "int" } },
        idPlaylist: { bsonType: "array", items: { bsonType: "int" } },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.usuarios.createIndex({ correoUsuario: 1 }, { unique: true });
db.usuarios.createIndex({ rolUsuario: 1 });

// Coleccion artistas: la productora se embebe directamente porque cada artista
// pertenece a una sola productora y siempre se consultan juntos.

db.createCollection("artistas", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "nombreArtista", "paisOrigenArtista", "Productora"],
      properties: {
        _id: { bsonType: "int" },
        nombreArtista: { bsonType: "string" },
        paisOrigenArtista: { bsonType: "string" },
        descripcionArtista: { bsonType: "string" },
        Productora: {
          bsonType: "object",
          required: ["nombreProductora", "correoProductora", "paisProductora"],
          properties: {
            nombreProductora: { bsonType: "string" },
            correoProductora: { bsonType: "string" },
            paisProductora: { bsonType: "string" },
          },
        },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.artistas.createIndex({ nombreArtista: 1 });

// Coleccion albums: se mantiene como coleccion independiente porque tiene vida
// propia y no siempre se consulta desde la cancion. idArtista referencia al artista principal.

db.createCollection("albums", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "tituloAlbum", "idArtista"],
      properties: {
        _id: { bsonType: "int" },
        tituloAlbum: { bsonType: "string" },
        fechaLanzamientoAlbum: { bsonType: "date" },
        idArtista: { bsonType: "int" },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.albums.createIndex({ idArtista: 1 });

// Coleccion canciones: Genero se embebe por ser un catalogo estatico y pequeno.
// idAlbum e idArtista se referencian por id para evitar documentos pesados.

db.createCollection("canciones", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "tituloCancion", "duracionCancion", "Genero", "idArtista"],
      properties: {
        _id: { bsonType: "int" },
        tituloCancion: { bsonType: "string" },
        duracionCancion: { bsonType: "double", minimum: 0.1, maximum: 10000000 },
        idiomaCancion: { bsonType: "string" },
        Genero: {
          bsonType: "object",
          required: ["nombreGenero"],
          properties: { nombreGenero: { bsonType: "string" } },
        },
        idAlbum: { bsonType: "int" },
        idArtista: { bsonType: "array", items: { bsonType: "int" } },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.canciones.createIndex({ tituloCancion: 1 });
db.canciones.createIndex({ idAlbum: 1 });
db.canciones.createIndex({ "Genero.nombreGenero": 1 });

// Coleccion playlists: idCancion se almacena como array de referencias
// reemplazando la tabla intermedia CancionPlaylist del modelo relacional.

db.createCollection("playlists", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["_id", "nombrePlaylist", "fechaCreacionPlaylist", "privacidadPlaylist", "idUsuario"],
      properties: {
        _id: { bsonType: "int" },
        nombrePlaylist: { bsonType: "string" },
        fechaCreacionPlaylist: { bsonType: "date" },
        privacidadPlaylist: { bsonType: "string", enum: ["Privada", "Publica"] },
        descripcionPlaylist: { bsonType: "string" },
        idUsuario: { bsonType: "int" },
        idCancion: { bsonType: "array", items: { bsonType: "int" } },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.playlists.createIndex({ idUsuario: 1 });

// Coleccion reproducciones: coleccion de alto volumen transaccional que se mantiene
// independiente con referencias simples a usuario y cancion para inserciones rapidas.

db.createCollection("reproducciones", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["fechaReproduccion", "duracionReproduccion", "idUsuario", "idCancion"],
      properties: {
        fechaReproduccion: { bsonType: "date" },
        duracionReproduccion: { bsonType: "double", minimum: 0 },
        idUsuario: { bsonType: "int" },
        idCancion: { bsonType: "int" },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.reproducciones.createIndex({ fechaReproduccion: 1 });
db.reproducciones.createIndex({ idUsuario: 1 });
db.reproducciones.createIndex({ idCancion: 1 });

// Coleccion regalias: se separo de canciones porque crece con cada periodo de
// calculo y embeberla generaria documentos excesivamente pesados con el tiempo.

db.createCollection("regalias", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["idCancion", "fechaCalculoRegalia", "cantidadReproduccionesRegalia", "montoGeneradoRegalia"],
      properties: {
        idCancion: { bsonType: "int" },
        fechaCalculoRegalia: { bsonType: "date" },
        cantidadReproduccionesRegalia: { bsonType: "int", minimum: 0 },
        montoGeneradoRegalia: { bsonType: "double", minimum: 0 },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.regalias.createIndex({ idCancion: 1 });
db.regalias.createIndex({ fechaCalculoRegalia: 1 });

// Coleccion pagos: se separo de suscripciones porque crece indefinidamente con
// cada cobro registrado y no debe embeberse dentro del documento del usuario.

db.createCollection("pagos", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["idUsuario", "idSuscripcion", "fechaPago", "montoPago"],
      properties: {
        idUsuario: { bsonType: "int" },
        idSuscripcion: { bsonType: "int" },
        fechaPago: { bsonType: "date" },
        montoPago: { bsonType: "double", minimum: 0 },
      },
    },
  },
  validationLevel: "moderate",
  validationAction: "warn",
});

db.pagos.createIndex({ idUsuario: 1 });
db.pagos.createIndex({ fechaPago: 1 });

// -- Seccion 2: Consultas Avanzadas con Find --

// Consulta 2.1 - Playlists publicas con al menos 3 canciones
// Obtenemos playlists publicas que tienen al menos 3 canciones verificando
// que el indice 2 exista dentro del array idCancion.

db.playlists.find(
  {
    privacidadPlaylist: "Publica",
    "idCancion.2": { $exists: true }
  },
  { nombrePlaylist: 1, idUsuario: 1, privacidadPlaylist: 1, _id: 0 }
).sort({ nombrePlaylist: 1 });

// Consulta 2.2 - Canciones de generos especificos con duracion mayor a 180 segundos
// Usamos $in para filtrar por multiples generos y $gt para obtener
// solo las canciones cuya duracion supera los 180 segundos.

db.canciones.find(
  {
    "Genero.nombreGenero": { $in: ["Electronica", "Pop", "Rock"] },
    duracionCancion: { $gt: 180 }
  },
  { tituloCancion: 1, "Genero.nombreGenero": 1, duracionCancion: 1, _id: 0 }
).sort({ duracionCancion: -1 });

// Consulta 2.3 - Albums de artistas especificos lanzados despues del 2021
// Usamos $in para buscar en multiples artistas y $gte para filtrar
// por fecha de lanzamiento como string.

db.albums.find(
  {
    idArtista: { $in: [2, 3, 4, 5] },
    fechaLanzamientoAlbum: { $gte: "2021-01-01" }
  },
  { tituloAlbum: 1, fechaLanzamientoAlbum: 1, idArtista: 1, _id: 0 }
).sort({ fechaLanzamientoAlbum: -1 });

// Consulta 2.4 - Canciones que le gustan a un usuario con duracion menor a 300 segundos
// Usamos findOne para obtener los ids del usuario y luego $in junto con $lt
// para filtrar las canciones referenciadas por duracion.

const u = db.usuarios.findOne({ _id: 7 }, { idCancion: 1, _id: 0 });
db.canciones.find(
  {
    _id: { $in: u.idCancion },
    duracionCancion: { $lt: 300 }
  },
  { tituloCancion: 1, "Genero.nombreGenero": 1, duracionCancion: 1, _id: 0 }
).sort({ duracionCancion: 1 });

// Consulta 2.5 - Reproducciones de canciones especificas con duracion mayor a 100 segundos
// Usamos $in sobre idCancion y $gt sobre duracionReproduccion para obtener
// las escuchas mas completas de un conjunto de canciones.

db.reproducciones.find(
  {
    idCancion: { $in: [35, 48, 61, 5, 12, 18] },
    duracionReproduccion: { $gt: 100 }
  },
  { idCancion: 1, fechaReproduccion: 1, duracionReproduccion: 1, _id: 0 }
).sort({ duracionReproduccion: -1 });

// -- Consultas adicionales --

// Consulta 2.6 - Regalias con monto mayor a 0 entre 2024 y 2025
// Obtenemos regalias con monto generado mayor a cero
// en un rango de fechas especifico.

db.regalias.find(
  {
    fechaCalculoRegalia: { $gte: new Date("2024-01-01"), $lte: new Date("2025-12-31") },
    montoGeneradoRegalia: { $gt: 0 }
  },
  { idCancion: 1, fechaCalculoRegalia: 1, cantidadReproduccionesRegalia: 1, montoGeneradoRegalia: 1, _id: 0 }
).sort({ montoGeneradoRegalia: -1 });

// Consulta 2.7 - Canciones con mas de 1 artista interprete
// Obtenemos canciones con multiples artistas verificando
// que el indice 1 exista en el array idArtista.

db.canciones.find(
  { "idArtista.1": { $exists: true } },
  { tituloCancion: 1, "Genero.nombreGenero": 1, idArtista: 1, idAlbum: 1, _id: 0 }
).sort({ tituloCancion: 1 });

// Consulta 2.8 - Usuarios Premium activos con artistas seguidos
// Obtenemos usuarios con suscripcion Premium activa que ademas
// tienen al menos un artista en su array idArtista.

db.usuarios.find(
  {
    "Suscripcion.tipoPlanSuscripcion": "Premium",
    "Suscripcion.estadoSuscripcion": "Activa",
    "idArtista.0": { $exists: true }
  },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, idArtista: 1, _id: 0 }
).sort({ nombreUsuario: 1 });

// Consulta 2.9 - Usuarios con al menos una playlist
// Obtenemos usuarios que tienen al menos una playlist
// verificando que el indice 0 exista en el array idPlaylist.

db.usuarios.find(
  { "idPlaylist.0": { $exists: true } },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, idPlaylist: 1, _id: 0 }
).sort({ nombreUsuario: 1 });

// Consulta 2.10 - Usuarios con al menos 3 canciones con me gusta
// Obtenemos usuarios que tienen al menos 3 canciones en su array idCancion
// verificando que el indice 2 exista.

db.usuarios.find(
  { "idCancion.2": { $exists: true } },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, _id: 0 }
).sort({ nombreUsuario: 1 });

// Consulta 2.11 - Artistas de Mexico cuya productora opera en otro pais
// Obtenemos artistas de Mexico cuya productora no es de Mexico
// usando $ne sobre el campo embebido Productora.paisProductora.

db.artistas.find(
  { paisOrigenArtista: "Mexico", "Productora.paisProductora": { $ne: "Mexico" } },
  { nombreArtista: 1, paisOrigenArtista: 1, "Productora.nombreProductora": 1, "Productora.paisProductora": 1, _id: 0 }
).sort({ nombreArtista: 1 });

// Consulta 2.12 - Reproducciones del usuario 7 en 2024 con duracion mayor a 120 segundos
// Obtenemos reproducciones de un usuario filtrando por rango de fechas
// y duracion minima de escucha.

db.reproducciones.find(
  {
    idUsuario: 7,
    fechaReproduccion: { $gte: new Date("2024-01-01"), $lte: new Date("2024-12-31") },
    duracionReproduccion: { $gt: 120 }
  },
  { fechaReproduccion: 1, duracionReproduccion: 1, idCancion: 1, _id: 0 }
).sort({ fechaReproduccion: -1 });

// Consulta 2.13 - Canciones en espanol con duracion menor a 180 segundos
// Obtenemos canciones en idioma espanol cuya duracion
// es menor a 3 minutos ordenadas de menor a mayor.

db.canciones.find(
  { idiomaCancion: "Espanol", duracionCancion: { $lt: 180 } },
  { tituloCancion: 1, duracionCancion: 1, "Genero.nombreGenero": 1, idArtista: 1, _id: 0 }
).sort({ duracionCancion: 1 });

// Consulta 2.14 - Pagos realizados en 2024
// Obtenemos todos los pagos registrados entre enero y
// diciembre de 2024 ordenados por fecha descendente.

db.pagos.find(
  { fechaPago: { $gte: new Date("2024-01-01"), $lte: new Date("2024-12-31") } },
  { idUsuario: 1, fechaPago: 1, montoPago: 1, idSuscripcion: 1, _id: 0 }
).sort({ fechaPago: -1 });

// Consulta 2.15 - Playlists publicas creadas desde 2024
// Obtenemos playlists con privacidad Publica cuya fecha
// de creacion es mayor o igual al inicio de 2024.

db.playlists.find(
  {
    privacidadPlaylist: "Publica",
    fechaCreacionPlaylist: { $gte: new Date("2024-01-01") }
  },
  { nombrePlaylist: 1, idUsuario: 1, fechaCreacionPlaylist: 1, _id: 0 }
).sort({ fechaCreacionPlaylist: -1 });

// Consulta 2.16 - Artistas de Mexico o Argentina
// Obtenemos artistas de esos paises usando $in
// sobre el campo paisOrigenArtista.

db.artistas.find(
  { paisOrigenArtista: { $in: ["Mexico", "Argentina"] } },
  { nombreArtista: 1, paisOrigenArtista: 1, "Productora.nombreProductora": 1, _id: 0 }
).sort({ paisOrigenArtista: 1, nombreArtista: 1 });

// Consulta 2.17 - Usuarios con suscripcion activa y plan Gratis
// Obtenemos usuarios cuya suscripcion activa es de tipo Gratis
// usando filtros combinados sobre el array embebido Suscripcion.

db.usuarios.find(
  { "Suscripcion.tipoPlanSuscripcion": "Gratis", "Suscripcion.estadoSuscripcion": "Activa" },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, _id: 0 }
).sort({ apellidoUsuario: 1 });

// Consulta 2.18 - Reproducciones de canciones especificas
// Obtenemos reproducciones de un conjunto de canciones usando $in
// ordenadas por cancion y fecha descendente.

db.reproducciones.find(
  { idCancion: { $in: [35, 48, 61] } },
  { idUsuario: 1, idCancion: 1, fechaReproduccion: 1, duracionReproduccion: 1, _id: 0 }
).sort({ idCancion: 1, fechaReproduccion: -1 });

// Consulta 2.19 - Regalias con mas de 5 reproducciones
// Obtenemos regalias cuya cantidad de reproducciones supera 5
// ordenadas de mayor a menor cantidad.

db.regalias.find(
  { cantidadReproduccionesRegalia: { $gt: 5 } },
  { idCancion: 1, fechaCalculoRegalia: 1, cantidadReproduccionesRegalia: 1, montoGeneradoRegalia: 1, _id: 0 }
).sort({ cantidadReproduccionesRegalia: -1 });

// Consulta 2.20 - Pagos de usuarios especificos con monto mayor a 5
// Obtenemos pagos de un conjunto de usuarios usando $in sobre idUsuario
// filtrando por monto mayor a 5.

db.pagos.find(
  { idUsuario: { $in: [7, 28, 45, 62, 73] }, montoPago: { $gt: 5 } },
  { idUsuario: 1, fechaPago: 1, montoPago: 1, idSuscripcion: 1, _id: 0 }
).sort({ idUsuario: 1, fechaPago: -1 });

// Consulta 2.21 - Canciones que le gustan a un usuario especifico
// Obtenemos las canciones cuyos ids estan en el array idCancion del usuario
// usando findOne y luego $in sobre el campo _id de canciones.

const usuario7 = db.usuarios.findOne({ _id: 7 }, { idCancion: 1, _id: 0 });
db.canciones.find(
  { _id: { $in: usuario7.idCancion } },
  { tituloCancion: 1, "Genero.nombreGenero": 1, duracionCancion: 1, _id: 0 }
).sort({ tituloCancion: 1 });

// Consulta 2.22 - Canciones de un album especifico
// Obtenemos todas las canciones que pertenecen a un album
// filtrando por idAlbum y ordenando por titulo.

db.canciones.find(
  { idAlbum: 3 },
  { tituloCancion: 1, "Genero.nombreGenero": 1, duracionCancion: 1, idArtista: 1, _id: 0 }
).sort({ tituloCancion: 1 });

// Consulta 2.23 - Playlists de un usuario especifico
// Obtenemos todas las playlists creadas por un usuario
// filtrando por idUsuario y ordenando por fecha de creacion.

db.playlists.find(
  { idUsuario: 7 },
  { nombrePlaylist: 1, privacidadPlaylist: 1, fechaCreacionPlaylist: 1, idCancion: 1, _id: 0 }
).sort({ fechaCreacionPlaylist: -1 });

// Consulta 2.24 - Canciones de un artista especifico
// Obtenemos todas las canciones donde el artista aparece
// en el array idArtista usando $in sobre ese campo.

db.canciones.find(
  { idArtista: { $in: [2] } },
  { tituloCancion: 1, "Genero.nombreGenero": 1, duracionCancion: 1, idAlbum: 1, _id: 0 }
).sort({ tituloCancion: 1 });

// Consulta 2.25 - Albums de un artista especifico
// Obtenemos todos los albums asociados a un artista
// filtrando por idArtista y ordenando por fecha de lanzamiento.

db.albums.find(
  { idArtista: 2 },
  { tituloAlbum: 1, fechaLanzamientoAlbum: 1, _id: 0 }
).sort({ fechaLanzamientoAlbum: -1 });
