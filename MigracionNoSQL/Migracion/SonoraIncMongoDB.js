use("SonoraIncDB");

// -- Seccion 1: Creacion de Colecciones con Validadores e Indices --

// Coleccion usuarios: se define el validador con $jsonSchema para garantizar
// la integridad de los documentos. Suscripcion se embebe como array porque
// siempre se consulta junto al usuario y tiene un tamano controlado.
// idArtista, idCancion e idPlaylist se almacenan como arrays de referencias.

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

// Consulta 2.1 - Playlists con mas de 10 canciones ordenadas por nombre
// Identificamos las playlists mas completas de la plataforma verificando
// que el indice 10 exista dentro del array idCancion.

db.playlists.find(
  { "idCancion.10": { $exists: true } },
  { nombrePlaylist: 1, idUsuario: 1, privacidadPlaylist: 1, _id: 0 }
).sort({ nombrePlaylist: 1 });

// Consulta 2.2 - Regalias con monto mayor a 500 en el ultimo ano
// Identificamos las canciones mas rentables de la plataforma filtrando
// por monto generado y rango de fechas del ultimo periodo anual.

db.regalias.find(
  {
    fechaCalculoRegalia: { $gte: new Date("2024-01-01"), $lte: new Date("2024-12-31") },
    montoGeneradoRegalia: { $gt: 500 }
  },
  { idCancion: 1, fechaCalculoRegalia: 1, cantidadReproduccionesRegalia: 1, montoGeneradoRegalia: 1, _id: 0 }
).sort({ montoGeneradoRegalia: -1 });

// Consulta 2.3 - Canciones con mas de 3 artistas interpretes
// Obtenemos canciones colaborativas verificando que el indice 3
// exista dentro del array idArtista de cada cancion.

db.canciones.find(
  { "idArtista.3": { $exists: true } },
  { tituloCancion: 1, "Genero.nombreGenero": 1, idArtista: 1, idAlbum: 1, _id: 0 }
).sort({ tituloCancion: 1 });

// Consulta 2.4 - Albums lanzados desde 2022 de artistas especificos
// Obtenemos el catalogo reciente de un conjunto de artistas usando $in
// sobre idArtista y un rango de fechas sobre fechaLanzamientoAlbum.

db.albums.find(
  {
    idArtista: { $in: [1, 2, 3, 4, 5] },
    fechaLanzamientoAlbum: { $gte: new Date("2022-01-01") }
  },
  { tituloAlbum: 1, fechaLanzamientoAlbum: 1, idArtista: 1, _id: 0 }
).sort({ fechaLanzamientoAlbum: -1 });

// Consulta 2.5 - Canciones de Pop o Reggaeton con duracion entre 3 y 5 minutos
// Obtenemos las canciones de los generos mas populares cuya duracion se encuentra
// entre 180 y 300 segundos usando $in sobre el campo embebido Genero.nombreGenero.

db.canciones.find(
  {
    "Genero.nombreGenero": { $in: ["Pop", "Reggaeton"] },
    duracionCancion: { $gte: 180, $lte: 300 }
  },
  { tituloCancion: 1, "Genero.nombreGenero": 1, duracionCancion: 1, idArtista: 1, _id: 0 }
).sort({ duracionCancion: -1 });

// Consulta 2.6 - Usuarios Premium activos con artistas seguidos
// Identificamos los usuarios con plan Premium activo que ademas
// siguen al menos un artista en la plataforma.

db.usuarios.find(
  {
    "Suscripcion.tipoPlanSuscripcion": "Premium",
    "Suscripcion.estadoSuscripcion": "Activa",
    "idArtista.0": { $exists: true }
  },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, idArtista: 1, _id: 0 }
).sort({ nombreUsuario: 1 });

// Consulta 2.7 - Usuarios con mas de 5 playlists creadas
// Identificamos los usuarios mas activos en creacion de contenido
// verificando que el indice 5 exista dentro del array idPlaylist.

db.usuarios.find(
  { "idPlaylist.5": { $exists: true } },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, idPlaylist: 1, _id: 0 }
).sort({ nombreUsuario: 1 });

// Consulta 2.8 - Usuarios con mas de 10 canciones con me gusta
// Identificamos los usuarios mas comprometidos con el catalogo musical
// verificando que el indice 10 exista dentro del array idCancion.

db.usuarios.find(
  { "idCancion.10": { $exists: true } },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, _id: 0 }
).sort({ nombreUsuario: 1 });

// Consulta 2.9 - Artistas de Colombia cuya productora opera en otro pais
// Detectamos artistas internacionalizados cuya productora tiene sede
// en un pais diferente al de origen del artista.

db.artistas.find(
  { paisOrigenArtista: "Colombia", "Productora.paisProductora": { $ne: "Colombia" } },
  { nombreArtista: 1, paisOrigenArtista: 1, "Productora.nombreProductora": 1, "Productora.paisProductora": 1, _id: 0 }
).sort({ nombreArtista: 1 });

// Consulta 2.10 - Reproducciones de un usuario en 2024 con duracion mayor a 2 minutos
// Obtenemos el historial de escucha completa de un usuario filtrando
// por rango de fechas y duracion minima de reproduccion.

db.reproducciones.find(
  {
    idUsuario: 1,
    fechaReproduccion: { $gte: new Date("2024-01-01"), $lte: new Date("2024-12-31") },
    duracionReproduccion: { $gt: 120 }
  },
  { fechaReproduccion: 1, duracionReproduccion: 1, idCancion: 1, _id: 0 }
).sort({ fechaReproduccion: -1 });

// Consulta 2.11 - Canciones en espanol de duracion menor a 3 minutos
// Obtenemos canciones cortas en idioma espanol ideales para listas
// de reproduccion rapida o contenido de redes sociales.

db.canciones.find(
  { idiomaCancion: "Espanol", duracionCancion: { $lt: 180 } },
  { tituloCancion: 1, duracionCancion: 1, "Genero.nombreGenero": 1, idArtista: 1, _id: 0 }
).sort({ duracionCancion: 1 });

// Consulta 2.12 - Pagos realizados en el primer trimestre de 2025
// Obtenemos todos los cobros registrados en el primer trimestre del ano
// para analizar el comportamiento de facturacion en ese periodo.

db.pagos.find(
  { fechaPago: { $gte: new Date("2025-01-01"), $lte: new Date("2025-03-31") } },
  { idUsuario: 1, fechaPago: 1, montoPago: 1, idSuscripcion: 1, _id: 0 }
).sort({ fechaPago: -1 });

// Consulta 2.13 - Playlists publicas creadas en el ultimo ano
// Obtenemos el contenido publico mas reciente de la plataforma
// para identificar tendencias en creacion de playlists.

db.playlists.find(
  {
    privacidadPlaylist: "Publica",
    fechaCreacionPlaylist: { $gte: new Date("2024-01-01") }
  },
  { nombrePlaylist: 1, idUsuario: 1, fechaCreacionPlaylist: 1, _id: 0 }
).sort({ fechaCreacionPlaylist: -1 });

// Consulta 2.14 - Artistas de Mexico o Argentina con productora propia
// Obtenemos artistas latinoamericanos de estos paises cuya productora
// tambien opera en el mismo pais usando $in y condicion sobre campo embebido.

db.artistas.find(
  {
    paisOrigenArtista: { $in: ["Mexico", "Argentina"] },
    "Productora.paisProductora": { $in: ["Mexico", "Argentina"] }
  },
  { nombreArtista: 1, paisOrigenArtista: 1, "Productora.nombreProductora": 1, _id: 0 }
).sort({ paisOrigenArtista: 1, nombreArtista: 1 });

// Consulta 2.15 - Canciones de Rock con mas de 2 artistas interpretes
// Identificamos colaboraciones dentro del genero Rock verificando
// que el indice 2 exista en el array idArtista y filtrando por genero.

db.canciones.find(
  { "Genero.nombreGenero": "Rock", "idArtista.2": { $exists: true } },
  { tituloCancion: 1, idArtista: 1, duracionCancion: 1, _id: 0 }
).sort({ tituloCancion: 1 });

// Consulta 2.16 - Albums lanzados antes del 2020 ordenados por fecha
// Obtenemos el catalogo clasico de la plataforma para identificar
// el contenido de mayor antiguedad disponible en SonoraInc.

db.albums.find(
  { fechaLanzamientoAlbum: { $lt: new Date("2020-01-01") } },
  { tituloAlbum: 1, fechaLanzamientoAlbum: 1, idArtista: 1, _id: 0 }
).sort({ fechaLanzamientoAlbum: 1 });

// Consulta 2.17 - Usuarios con suscripcion cancelada o vencida
// Identificamos usuarios inactivos cuya suscripcion ya no esta vigente
// para campanas de reactivacion o analisis de churn de la plataforma.

db.usuarios.find(
  { "Suscripcion.estadoSuscripcion": { $in: ["Cancelada", "Vencida"] } },
  { nombreUsuario: 1, apellidoUsuario: 1, correoUsuario: 1, _id: 0 }
).sort({ apellidoUsuario: 1 });

// Consulta 2.18 - Reproducciones de canciones especificas en cualquier usuario
// Obtenemos todas las reproducciones de un conjunto de canciones para
// analizar el alcance de esas canciones en la base de usuarios.

db.reproducciones.find(
  { idCancion: { $in: [1, 2, 3, 4, 5] } },
  { idUsuario: 1, idCancion: 1, fechaReproduccion: 1, duracionReproduccion: 1, _id: 0 }
).sort({ idCancion: 1, fechaReproduccion: -1 });

// Consulta 2.19 - Regalias con mas de 10000 reproducciones en el periodo
// Identificamos las canciones con mayor volumen de escuchas en un periodo
// de calculo para detectar los hits mas importantes de la plataforma.

db.regalias.find(
  { cantidadReproduccionesRegalia: { $gt: 10000 } },
  { idCancion: 1, fechaCalculoRegalia: 1, cantidadReproduccionesRegalia: 1, montoGeneradoRegalia: 1, _id: 0 }
).sort({ cantidadReproduccionesRegalia: -1 });

// Consulta 2.20 - Pagos con monto mayor a 9.99 realizados por usuarios especificos
// Obtenemos los cobros de plan Premium de un conjunto de usuarios para
// analizar el historial de facturacion de los clientes mas valiosos.

db.pagos.find(
  { idUsuario: { $in: [1, 2, 3, 4, 5] }, montoPago: { $gt: 9.99 } },
  { idUsuario: 1, fechaPago: 1, montoPago: 1, idSuscripcion: 1, _id: 0 }
).sort({ idUsuario: 1, fechaPago: -1 });
