

from pymongo import MongoClient
from datetime import datetime

MONGO_URI = "mongodb+srv://Admin:UDLA@clusterudla02.e3lgsam.mongodb.net/"
cliente = MongoClient(MONGO_URI)
db = cliente["SonoraIncDB"]

def limpiar():
    print("\n" + "=" * 60)

def pausar():
    input("\nPresiona Enter para continuar...")

def mostrar_docs(docs):
    if not docs:
        print("No se encontraron resultados.")
        return
    for doc in docs:
        print(doc)

 
# MENU PRINCIPAL


def menu_principal():
    while True:
        limpiar()
        print("  SONORAINC - GESTION NOSQL")
        print("=" * 60)
        print("  1. Usuarios")
        print("  2. Artistas")
        print("  3. Canciones")
        print("  4. Albums")
        print("  5. Playlists")
        print("  6. Reproducciones")
        print("  7. Regalias")
        print("  8. Pagos")
        print("  0. Salir")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()
        if op == "1": menu_usuarios()
        elif op == "2": menu_artistas()
        elif op == "3": menu_canciones()
        elif op == "4": menu_albums()
        elif op == "5": menu_playlists()
        elif op == "6": menu_reproducciones()
        elif op == "7": menu_regalias()
        elif op == "8": menu_pagos()
        elif op == "0":
            cliente.close()
            print("\nHasta luego.")
            break

 
# USUARIOS
 

def menu_usuarios():
    while True:
        limpiar()
        print("  USUARIOS")
        print("=" * 60)
        print("  1. Ver todos los usuarios")
        print("  2. Buscar usuario por ID")
        print("  3. Buscar usuario por correo")
        print("  4. Insertar nuevo usuario")
        print("  5. Actualizar usuario")
        print("  6. Eliminar usuario")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            limpiar()
            docs = list(db.usuarios.find(
                {},
                {"nombreUsuario": 1, "apellidoUsuario": 1, "correoUsuario": 1, "rolUsuario": 1}
            ).sort("apellidoUsuario", 1))
            print("--- Todos los usuarios ---")
            mostrar_docs(docs)
            pausar()

        elif op == "2":
            try:
                id_u = int(input("ID usuario: "))
                doc = db.usuarios.find_one({"_id": id_u})
                limpiar()
                print("--- Resultado ---")
                mostrar_docs([doc] if doc else [])
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            correo = input("Correo: ").strip()
            doc = db.usuarios.find_one({"correoUsuario": correo})
            limpiar()
            print("--- Resultado ---")
            mostrar_docs([doc] if doc else [])
            pausar()

        elif op == "4":
            limpiar()
            print("--- Insertar usuario ---")
            try:
                id_u = int(input("ID: "))
                if db.usuarios.find_one({"_id": id_u}):
                    print(f"Error: Ya existe un usuario con ID {id_u}.")
                else:
                    nombre = input("Nombre: ").strip()
                    apellido = input("Apellido: ").strip()
                    correo = input("Correo: ").strip()
                    if db.usuarios.find_one({"correoUsuario": correo}):
                        print(f"Error: Ya existe un usuario con ese correo.")
                    else:
                        rol = input("Rol (admin/usuario): ").strip()
                        password = input("Password: ").strip()
                        db.usuarios.insert_one({
                            "_id": id_u,
                            "nombreUsuario": nombre,
                            "apellidoUsuario": apellido,
                            "correoUsuario": correo,
                            "fechaRegistroUsuario": datetime.now(),
                            "rolUsuario": rol,
                            "passwordUsuario": password,
                            "Suscripcion": [],
                            "idArtista": [], "idCancion": [], "idPlaylist": []
                        })
                        print(f"Usuario '{nombre} {apellido}' insertado correctamente.")
                        print("Recuerda agregar una suscripcion desde Actualizar -> Agregar suscripcion.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "5":
            limpiar()
            print("--- Actualizar usuario ---")
            print("Deja en blanco los campos que no quieras cambiar.")
            try:
                id_u = int(input("ID usuario: "))
                doc = db.usuarios.find_one({"_id": id_u})
                if not doc:
                    print(f"No existe usuario con ID {id_u}.")
                else:
                    print(f"\nDatos actuales:")
                    print(f"  Nombre:   {doc['nombreUsuario']}")
                    print(f"  Apellido: {doc['apellidoUsuario']}")
                    print(f"  Correo:   {doc['correoUsuario']}")
                    print(f"  Rol:      {doc['rolUsuario']}")
                    print(f"  Password: {doc['passwordUsuario']}")
                    print()
                    campos = {}
                    v = input(f"Nombre [{doc['nombreUsuario']}]: ").strip()
                    if v: campos["nombreUsuario"] = v
                    v = input(f"Apellido [{doc['apellidoUsuario']}]: ").strip()
                    if v: campos["apellidoUsuario"] = v
                    v = input(f"Correo [{doc['correoUsuario']}]: ").strip()
                    if v: campos["correoUsuario"] = v
                    v = input(f"Rol [{doc['rolUsuario']}] (admin/usuario): ").strip()
                    if v: campos["rolUsuario"] = v
                    v = input(f"Password [{doc['passwordUsuario']}]: ").strip()
                    if v: campos["passwordUsuario"] = v

                    if campos:
                        db.usuarios.update_one({"_id": id_u}, {"$set": campos})
                        print("Usuario actualizado correctamente.")
                    else:
                        print("No se realizaron cambios.")

                    agregar = input("\nAgregar nueva suscripcion? (s/n): ").strip().lower()
                    if agregar == "s":
                        id_susc = int(input("ID suscripcion: "))
                        plan = input("Plan (Gratis/Premium): ").strip()
                        f_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
                        f_fin = input("Fecha fin (YYYY-MM-DD, opcional): ").strip()
                        nueva_susc = {
                            "idSuscripcion": id_susc,
                            "tipoPlanSuscripcion": plan,
                            "fechaInicioSuscripcion": datetime.strptime(f_inicio, "%Y-%m-%d"),
                            "estadoSuscripcion": "Activa"
                        }
                        if f_fin:
                            nueva_susc["fechaFinSuscripcion"] = datetime.strptime(f_fin, "%Y-%m-%d")
                        db.usuarios.update_one({"_id": id_u}, {"$push": {"Suscripcion": nueva_susc}})
                        print("Suscripcion agregada.")

                    cancelar = input("Cancelar suscripcion activa? (s/n): ").strip().lower()
                    if cancelar == "s":
                        db.usuarios.update_one(
                            {"_id": id_u, "Suscripcion.estadoSuscripcion": "Activa"},
                            {"$set": {"Suscripcion.$.estadoSuscripcion": "Cancelada"}}
                        )
                        print("Suscripcion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "6":
            limpiar()
            print("--- Eliminar usuario ---")
            try:
                id_u = int(input("ID usuario: "))
                if not db.usuarios.find_one({"_id": id_u}):
                    print(f"No existe usuario con ID {id_u}.")
                else:
                    conf = input(f"Confirmas eliminar usuario {id_u}? (s/n): ").strip().lower()
                    if conf == "s":
                        r = db.usuarios.delete_one({"_id": id_u})
                        print(f"Usuario eliminado: {r.deleted_count}")
                    else:
                        print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# ARTISTAS
 

def menu_artistas():
    while True:
        limpiar()
        print("  ARTISTAS")
        print("=" * 60)
        print("  1. Ver todos los artistas")
        print("  2. Buscar artista por ID")
        print("  3. Buscar artista por nombre")
        print("  4. Insertar nuevo artista")
        print("  5. Actualizar artista")
        print("  6. Eliminar artista")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            limpiar()
            docs = list(db.artistas.find(
                {}, {"nombreArtista": 1, "paisOrigenArtista": 1, "Productora.nombreProductora": 1}
            ).sort("nombreArtista", 1))
            print("--- Todos los artistas ---")
            mostrar_docs(docs)
            pausar()

        elif op == "2":
            try:
                id_a = int(input("ID artista: "))
                doc = db.artistas.find_one({"_id": id_a})
                limpiar()
                mostrar_docs([doc] if doc else [])
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            nombre = input("Nombre artista: ").strip()
            doc = db.artistas.find_one({"nombreArtista": nombre})
            limpiar()
            mostrar_docs([doc] if doc else [])
            pausar()

        elif op == "4":
            limpiar()
            print("--- Insertar artista ---")
            try:
                id_a = int(input("ID artista: "))
                if db.artistas.find_one({"_id": id_a}):
                    print(f"Error: Ya existe un artista con ID {id_a}.")
                else:
                    nombre = input("Nombre: ").strip()
                    pais = input("Pais de origen: ").strip()
                    desc = input("Descripcion (opcional): ").strip()

                    productoras = list(db.artistas.find({}, {"Productora": 1, "_id": 0}))
                    prod_unicas = {}
                    for p in productoras:
                        n = p["Productora"]["nombreProductora"]
                        if n not in prod_unicas:
                            prod_unicas[n] = p["Productora"]
                    lista_prod = list(prod_unicas.values())

                    print("\nProductoras existentes:")
                    for i, p in enumerate(lista_prod, 1):
                        print(f"  {i}. {p['nombreProductora']} ({p['paisProductora']})")
                    print(f"  {len(lista_prod)+1}. Crear nueva productora")

                    elec = input("\nElige una opcion: ").strip()
                    idx = int(elec) - 1
                    if 0 <= idx < len(lista_prod):
                        prod = lista_prod[idx]
                        nombre_prod = prod["nombreProductora"]
                        correo_prod = prod["correoProductora"]
                        pais_prod = prod["paisProductora"]
                    else:
                        nombre_prod = input("Nombre productora: ").strip()
                        correo_prod = input("Correo productora: ").strip()
                        pais_prod = input("Pais productora: ").strip()

                    db.artistas.insert_one({
                        "_id": id_a,
                        "nombreArtista": nombre,
                        "paisOrigenArtista": pais,
                        "descripcionArtista": desc if desc else None,
                        "Productora": {
                            "nombreProductora": nombre_prod,
                            "correoProductora": correo_prod,
                            "paisProductora": pais_prod
                        }
                    })
                    print(f"Artista '{nombre}' insertado correctamente.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "5":
            limpiar()
            print("--- Actualizar artista ---")
            print("Deja en blanco los campos que no quieras cambiar.")
            try:
                id_a = int(input("ID artista: "))
                doc = db.artistas.find_one({"_id": id_a})
                if not doc:
                    print(f"No existe artista con ID {id_a}.")
                else:
                    print(f"\nDatos actuales:")
                    print(f"  Nombre:            {doc['nombreArtista']}")
                    print(f"  Pais:              {doc['paisOrigenArtista']}")
                    print(f"  Descripcion:       {doc.get('descripcionArtista', '')}")
                    print(f"  Productora:        {doc['Productora']['nombreProductora']}")
                    print(f"  Correo Productora: {doc['Productora']['correoProductora']}")
                    print(f"  Pais Productora:   {doc['Productora']['paisProductora']}")
                    print()
                    campos = {}
                    v = input(f"Nombre [{doc['nombreArtista']}]: ").strip()
                    if v: campos["nombreArtista"] = v
                    v = input(f"Pais origen [{doc['paisOrigenArtista']}]: ").strip()
                    if v: campos["paisOrigenArtista"] = v
                    v = input(f"Descripcion [{doc.get('descripcionArtista', '')}]: ").strip()
                    if v: campos["descripcionArtista"] = v
                    v = input(f"Correo productora [{doc['Productora']['correoProductora']}]: ").strip()
                    if v: campos["Productora.correoProductora"] = v
                    if campos:
                        db.artistas.update_one({"_id": id_a}, {"$set": campos})
                        print("Artista actualizado correctamente.")
                    else:
                        print("No se realizaron cambios.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "6":
            limpiar()
            print("--- Eliminar artista ---")
            try:
                id_a = int(input("ID artista: "))
                if not db.artistas.find_one({"_id": id_a}):
                    print(f"No existe artista con ID {id_a}.")
                else:
                    conf = input(f"Confirmas eliminar artista {id_a}? (s/n): ").strip().lower()
                    if conf == "s":
                        r = db.artistas.delete_one({"_id": id_a})
                        print(f"Artista eliminado: {r.deleted_count}")
                    else:
                        print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# CANCIONES
 

def menu_canciones():
    while True:
        limpiar()
        print("  CANCIONES")
        print("=" * 60)
        print("  1. Ver todas las canciones")
        print("  2. Buscar cancion por ID")
        print("  3. Buscar cancion por titulo")
        print("  4. Insertar nueva cancion")
        print("  5. Actualizar cancion")
        print("  6. Eliminar cancion")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            limpiar()
            docs = list(db.canciones.find(
                {}, {"tituloCancion": 1, "Genero.nombreGenero": 1, "duracionCancion": 1}
            ).sort("tituloCancion", 1).limit(50))
            print("--- Canciones (primeras 50) ---")
            mostrar_docs(docs)
            pausar()

        elif op == "2":
            try:
                id_c = int(input("ID cancion: "))
                doc = db.canciones.find_one({"_id": id_c})
                limpiar()
                mostrar_docs([doc] if doc else [])
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            titulo = input("Titulo: ").strip()
            doc = db.canciones.find_one({"tituloCancion": titulo})
            limpiar()
            mostrar_docs([doc] if doc else [])
            pausar()

        elif op == "4":
            limpiar()
            print("--- Insertar cancion ---")
            try:
                id_c = int(input("ID cancion: "))
                if db.canciones.find_one({"_id": id_c}):
                    print(f"Error: Ya existe una cancion con ID {id_c}.")
                else:
                    titulo = input("Titulo: ").strip()
                    duracion = float(input("Duracion en segundos: "))
                    idioma = input("Idioma: ").strip()
                    genero = input("Genero: ").strip()
                    id_album = int(input("ID album: "))
                    ids = input("IDs artistas (separados por coma): ").strip()
                    lista_artistas = [int(x.strip()) for x in ids.split(",")]
                    db.canciones.insert_one({
                        "_id": id_c,
                        "tituloCancion": titulo,
                        "duracionCancion": duracion,
                        "idiomaCancion": idioma,
                        "Genero": {"nombreGenero": genero},
                        "idAlbum": id_album,
                        "idArtista": lista_artistas
                    })
                    print(f"Cancion '{titulo}' insertada correctamente.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "5":
            limpiar()
            print("--- Actualizar cancion ---")
            print("Deja en blanco los campos que no quieras cambiar.")
            try:
                id_c = int(input("ID cancion: "))
                doc = db.canciones.find_one({"_id": id_c})
                if not doc:
                    print(f"No existe cancion con ID {id_c}.")
                else:
                    print(f"\nDatos actuales:")
                    print(f"  Titulo:   {doc['tituloCancion']}")
                    print(f"  Idioma:   {doc.get('idiomaCancion', '')}")
                    print(f"  Duracion: {doc['duracionCancion']} seg")
                    print(f"  Genero:   {doc['Genero']['nombreGenero']}")
                    print()
                    campos = {}
                    v = input(f"Titulo [{doc['tituloCancion']}]: ").strip()
                    if v: campos["tituloCancion"] = v
                    v = input(f"Idioma [{doc.get('idiomaCancion', '')}]: ").strip()
                    if v: campos["idiomaCancion"] = v
                    v = input(f"Genero [{doc['Genero']['nombreGenero']}]: ").strip()
                    if v: campos["Genero.nombreGenero"] = v
                    if campos:
                        db.canciones.update_one({"_id": id_c}, {"$set": campos})
                        print("Cancion actualizada correctamente.")
                    else:
                        print("No se realizaron cambios.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "6":
            limpiar()
            print("--- Eliminar cancion ---")
            try:
                id_c = int(input("ID cancion: "))
                if not db.canciones.find_one({"_id": id_c}):
                    print(f"No existe cancion con ID {id_c}.")
                else:
                    conf = input(f"Confirmas eliminar cancion {id_c}? (s/n): ").strip().lower()
                    if conf == "s":
                        r = db.canciones.delete_one({"_id": id_c})
                        print(f"Cancion eliminada: {r.deleted_count}")
                    else:
                        print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# ALBUMS
 

def menu_albums():
    while True:
        limpiar()
        print("  ALBUMS")
        print("=" * 60)
        print("  1. Ver todos los albums")
        print("  2. Buscar album por ID")
        print("  3. Buscar album por titulo")
        print("  4. Insertar nuevo album")
        print("  5. Actualizar titulo de album")
        print("  6. Eliminar album")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            limpiar()
            docs = list(db.albums.find(
                {}, {"tituloAlbum": 1, "fechaLanzamientoAlbum": 1, "idArtista": 1}
            ).sort("tituloAlbum", 1))
            print("--- Todos los albums ---")
            mostrar_docs(docs)
            pausar()

        elif op == "2":
            try:
                id_al = int(input("ID album: "))
                doc = db.albums.find_one({"_id": id_al})
                limpiar()
                mostrar_docs([doc] if doc else [])
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            titulo = input("Titulo album: ").strip()
            doc = db.albums.find_one({"tituloAlbum": titulo})
            limpiar()
            mostrar_docs([doc] if doc else [])
            pausar()

        elif op == "4":
            limpiar()
            print("--- Insertar album ---")
            try:
                id_al = int(input("ID album: "))
                if db.albums.find_one({"_id": id_al}):
                    print(f"Error: Ya existe un album con ID {id_al}.")
                else:
                    titulo = input("Titulo: ").strip()
                    fecha_str = input("Fecha lanzamiento (YYYY-MM-DD): ").strip()
                    fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                    id_artista = int(input("ID artista: "))
                    db.albums.insert_one({
                        "_id": id_al,
                        "tituloAlbum": titulo,
                        "fechaLanzamientoAlbum": fecha,
                        "idArtista": id_artista
                    })
                    print(f"Album '{titulo}' insertado correctamente.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "5":
            limpiar()
            print("--- Actualizar album ---")
            print("Deja en blanco los campos que no quieras cambiar.")
            try:
                id_al = int(input("ID album: "))
                doc = db.albums.find_one({"_id": id_al})
                if not doc:
                    print(f"No existe album con ID {id_al}.")
                else:
                    print(f"\nDatos actuales:")
                    print(f"  Titulo:             {doc['tituloAlbum']}")
                    print(f"  Fecha lanzamiento:  {doc.get('fechaLanzamientoAlbum', '')}")
                    print(f"  ID Artista:         {doc['idArtista']}")
                    print()
                    campos = {}
                    v = input(f"Titulo [{doc['tituloAlbum']}]: ").strip()
                    if v: campos["tituloAlbum"] = v
                    v = input(f"ID Artista [{doc['idArtista']}]: ").strip()
                    if v: campos["idArtista"] = int(v)
                    if campos:
                        db.albums.update_one({"_id": id_al}, {"$set": campos})
                        print("Album actualizado correctamente.")
                    else:
                        print("No se realizaron cambios.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "6":
            limpiar()
            print("--- Eliminar album ---")
            try:
                id_al = int(input("ID album: "))
                if not db.albums.find_one({"_id": id_al}):
                    print(f"No existe album con ID {id_al}.")
                else:
                    conf = input(f"Confirmas eliminar album {id_al}? (s/n): ").strip().lower()
                    if conf == "s":
                        r = db.albums.delete_one({"_id": id_al})
                        print(f"Album eliminado: {r.deleted_count}")
                    else:
                        print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# PLAYLISTS
 

def menu_playlists():
    while True:
        limpiar()
        print("  PLAYLISTS")
        print("=" * 60)
        print("  1. Ver todas las playlists")
        print("  2. Buscar playlist por ID")
        print("  3. Buscar playlist por nombre")
        print("  4. Insertar nueva playlist")
        print("  5. Actualizar playlist")
        print("  6. Eliminar playlist")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            limpiar()
            docs = list(db.playlists.find(
                {}, {"nombrePlaylist": 1, "privacidadPlaylist": 1, "idUsuario": 1}
            ).sort("nombrePlaylist", 1))
            print("--- Todas las playlists ---")
            mostrar_docs(docs)
            pausar()

        elif op == "2":
            try:
                id_pl = int(input("ID playlist: "))
                doc = db.playlists.find_one({"_id": id_pl})
                limpiar()
                mostrar_docs([doc] if doc else [])
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            nombre = input("Nombre playlist: ").strip()
            doc = db.playlists.find_one({"nombrePlaylist": nombre})
            limpiar()
            mostrar_docs([doc] if doc else [])
            pausar()

        elif op == "4":
            limpiar()
            print("--- Insertar playlist ---")
            try:
                id_pl = int(input("ID playlist: "))
                if db.playlists.find_one({"_id": id_pl}):
                    print(f"Error: Ya existe una playlist con ID {id_pl}.")
                else:
                    nombre = input("Nombre: ").strip()
                    privacidad = input("Privacidad (Privada/Publica): ").strip()
                    desc = input("Descripcion (opcional): ").strip()
                    id_u = int(input("ID usuario dueno: "))
                    db.playlists.insert_one({
                        "_id": id_pl,
                        "nombrePlaylist": nombre,
                        "fechaCreacionPlaylist": datetime.now(),
                        "privacidadPlaylist": privacidad,
                        "descripcionPlaylist": desc if desc else None,
                        "idUsuario": id_u,
                        "idCancion": []
                    })
                    print(f"Playlist '{nombre}' insertada correctamente.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "5":
            limpiar()
            print("--- Actualizar playlist ---")
            print("Deja en blanco los campos que no quieras cambiar.")
            try:
                id_pl = int(input("ID playlist: "))
                doc = db.playlists.find_one({"_id": id_pl})
                if not doc:
                    print(f"No existe playlist con ID {id_pl}.")
                else:
                    print(f"\nDatos actuales:")
                    print(f"  Nombre:      {doc['nombrePlaylist']}")
                    print(f"  Privacidad:  {doc['privacidadPlaylist']}")
                    print(f"  Descripcion: {doc.get('descripcionPlaylist', '')}")
                    print(f"  Canciones:   {doc.get('idCancion', [])}")
                    print()
                    campos = {}
                    v = input(f"Nombre [{doc['nombrePlaylist']}]: ").strip()
                    if v: campos["nombrePlaylist"] = v
                    v = input(f"Privacidad [{doc['privacidadPlaylist']}] (Privada/Publica): ").strip()
                    if v: campos["privacidadPlaylist"] = v
                    v = input(f"Descripcion [{doc.get('descripcionPlaylist', '')}]: ").strip()
                    if v: campos["descripcionPlaylist"] = v
                    if campos:
                        db.playlists.update_one({"_id": id_pl}, {"$set": campos})
                        print("Playlist actualizada correctamente.")
                    else:
                        print("No se realizaron cambios.")

                    agregar = input("\nAgregar cancion a la playlist? (s/n): ").strip().lower()
                    if agregar == "s":
                        id_c = int(input("ID cancion: "))
                        db.playlists.update_one({"_id": id_pl}, {"$addToSet": {"idCancion": id_c}})
                        print("Cancion agregada.")

                    remover = input("Remover cancion de la playlist? (s/n): ").strip().lower()
                    if remover == "s":
                        id_c = int(input("ID cancion: "))
                        db.playlists.update_one({"_id": id_pl}, {"$pull": {"idCancion": id_c}})
                        print("Cancion removida.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "6":
            limpiar()
            print("--- Eliminar playlist ---")
            try:
                id_pl = int(input("ID playlist: "))
                if not db.playlists.find_one({"_id": id_pl}):
                    print(f"No existe playlist con ID {id_pl}.")
                else:
                    conf = input(f"Confirmas eliminar playlist {id_pl}? (s/n): ").strip().lower()
                    if conf == "s":
                        r = db.playlists.delete_one({"_id": id_pl})
                        print(f"Playlist eliminada: {r.deleted_count}")
                    else:
                        print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# REPRODUCCIONES
 

def menu_reproducciones():
    while True:
        limpiar()
        print("  REPRODUCCIONES")
        print("=" * 60)
        print("  1. Ver reproducciones de un usuario")
        print("  2. Ver reproducciones de una cancion")
        print("  3. Insertar nueva reproduccion")
        print("  4. Eliminar reproducciones de un usuario")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            try:
                id_u = int(input("ID usuario: "))
                docs = list(db.reproducciones.find(
                    {"idUsuario": id_u},
                    {"fechaReproduccion": 1, "duracionReproduccion": 1, "idCancion": 1, "_id": 0}
                ).sort("fechaReproduccion", -1).limit(20))
                limpiar()
                print(f"--- Ultimas 20 reproducciones del usuario {id_u} ---")
                mostrar_docs(docs)
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "2":
            try:
                id_c = int(input("ID cancion: "))
                docs = list(db.reproducciones.find(
                    {"idCancion": id_c},
                    {"fechaReproduccion": 1, "duracionReproduccion": 1, "idUsuario": 1, "_id": 0}
                ).sort("fechaReproduccion", -1).limit(20))
                limpiar()
                print(f"--- Ultimas 20 reproducciones de la cancion {id_c} ---")
                mostrar_docs(docs)
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            limpiar()
            print("--- Insertar reproduccion ---")
            try:
                id_u = int(input("ID usuario: "))
                id_c = int(input("ID cancion: "))
                duracion = float(input("Duracion escuchada en segundos: "))
                db.reproducciones.insert_one({
                    "fechaReproduccion": datetime.now(),
                    "duracionReproduccion": duracion,
                    "idUsuario": id_u,
                    "idCancion": id_c
                })
                print("Reproduccion registrada correctamente.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "4":
            limpiar()
            print("--- Eliminar reproducciones de un usuario ---")
            try:
                id_u = int(input("ID usuario: "))
                conf = input(f"Confirmas eliminar TODAS las reproducciones del usuario {id_u}? (s/n): ").strip().lower()
                if conf == "s":
                    r = db.reproducciones.delete_many({"idUsuario": id_u})
                    print(f"Reproducciones eliminadas: {r.deleted_count}")
                else:
                    print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# REGALIAS
 

def menu_regalias():
    while True:
        limpiar()
        print("  REGALIAS")
        print("=" * 60)
        print("  1. Ver regalias de una cancion")
        print("  2. Insertar nueva regalia")
        print("  3. Eliminar regalia")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            try:
                id_c = int(input("ID cancion: "))
                docs = list(db.regalias.find(
                    {"idCancion": id_c},
                    {"fechaCalculoRegalia": 1, "cantidadReproduccionesRegalia": 1, "montoGeneradoRegalia": 1, "_id": 0}
                ).sort("fechaCalculoRegalia", -1))
                limpiar()
                print(f"--- Regalias de la cancion {id_c} ---")
                mostrar_docs(docs)
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "2":
            limpiar()
            print("--- Insertar regalia ---")
            try:
                id_c = int(input("ID cancion: "))
                fecha_str = input("Fecha calculo (YYYY-MM-DD): ").strip()
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                cantidad = int(input("Cantidad reproducciones: "))
                monto = float(input("Monto generado: "))
                db.regalias.insert_one({
                    "idCancion": id_c,
                    "fechaCalculoRegalia": fecha,
                    "cantidadReproduccionesRegalia": cantidad,
                    "montoGeneradoRegalia": monto
                })
                print("Regalia insertada correctamente.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            limpiar()
            print("--- Eliminar regalia ---")
            try:
                id_c = int(input("ID cancion: "))
                fecha_str = input("Fecha calculo (YYYY-MM-DD): ").strip()
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                conf = input("Confirmas la eliminacion? (s/n): ").strip().lower()
                if conf == "s":
                    r = db.regalias.delete_one({"idCancion": id_c, "fechaCalculoRegalia": fecha})
                    print(f"Regalia eliminada: {r.deleted_count}")
                else:
                    print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# PAGOS
 

def menu_pagos():
    while True:
        limpiar()
        print("  PAGOS")
        print("=" * 60)
        print("  1. Ver pagos de un usuario")
        print("  2. Insertar nuevo pago")
        print("  3. Eliminar pago")
        print("  0. Volver")
        print("=" * 60)
        op = input("  Selecciona una opcion: ").strip()

        if op == "1":
            try:
                id_u = int(input("ID usuario: "))
                docs = list(db.pagos.find(
                    {"idUsuario": id_u},
                    {"fechaPago": 1, "montoPago": 1, "idSuscripcion": 1, "_id": 0}
                ).sort("fechaPago", -1))
                limpiar()
                print(f"--- Pagos del usuario {id_u} ---")
                mostrar_docs(docs)
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "2":
            limpiar()
            print("--- Insertar pago ---")
            try:
                id_u = int(input("ID usuario: "))
                id_susc = int(input("ID suscripcion: "))
                fecha_str = input("Fecha pago (YYYY-MM-DD): ").strip()
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                monto = float(input("Monto: "))
                db.pagos.insert_one({
                    "idUsuario": id_u,
                    "idSuscripcion": id_susc,
                    "fechaPago": fecha,
                    "montoPago": monto
                })
                print("Pago insertado correctamente.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "3":
            limpiar()
            print("--- Eliminar pago ---")
            try:
                id_u = int(input("ID usuario: "))
                fecha_str = input("Fecha del pago (YYYY-MM-DD): ").strip()
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
                conf = input("Confirmas la eliminacion? (s/n): ").strip().lower()
                if conf == "s":
                    r = db.pagos.delete_one({"idUsuario": id_u, "fechaPago": fecha})
                    print(f"Pago eliminado: {r.deleted_count}")
                else:
                    print("Operacion cancelada.")
            except Exception as e:
                print(f"Error: {e}")
            pausar()

        elif op == "0":
            break

 
# PUNTO DE ENTRADA
 

if __name__ == "__main__":
    menu_principal()
