# SonoraInc

---

## Requisitos previos

- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **SQL Server** (Express o superior)
- **ODBC Driver 17 for SQL Server** — [descargar aquí](https://learn.microsoft.com/es-es/sql/connect/odbc/download-odbc-driver-for-sql-server)

---

## Configuración de la base de datos

1. Abrir SQL Server Management Studio (SSMS) o Azure Data Studio
2. Ejecutar el script completo: `CreacionBaseSonoraInc.sql`
3. El script crea la base de datos, esquemas, tablas, datos de prueba y todos los stored procedures

---

## Instalación y arranque

### 1. Configurar la conexión a la base de datos

Copiar el archivo de ejemplo y editar las credenciales:

```
copy SonoraIncWeb\config.example.json SonoraIncWeb\config.json
```

Abrir `SonoraIncWeb/config.json` y ajustar los valores:

```json
{
    "database": {
        "driver": "ODBC Driver 17 for SQL Server",
        "server": "localhost",
        "name": "SonoraInc",
        "user": "SonoraApp",
        "password": "App@Sonora2026"
    }
}
```

> Si la instancia de SQL Server no es la default, usar el formato `servidor\instancia` en `server`. Por ejemplo: `MIPC\SQLEXPRESS`.

### 2. Crear el entorno e instalar dependencias

Ejecutar el archivo bat incluido — hace todo automáticamente:

```
iniciar_entorno.bat
```

El script:
- Crea el entorno virtual `entornoSonoraInc/` si no existe
- Instala todas las dependencias desde `requirements.txt`
- Verifica que `config.json` esté presente
- Deja el entorno activado

### 3. Iniciar el servidor

Dentro de la terminal que abre el bat:

```
cd SonoraIncWeb
python manage.py runserver
```

Abrir el navegador en `http://127.0.0.1:8000`

---

## Credenciales de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@sonorainc.com | Admin123Sonora |
| Usuario normal | carlos.mendoza2@hotmail.com | Sonora2 |
| Usuario normal | maria.fernandez3@outlook.com | Sonora3 |

El patrón para los 120 usuarios de prueba es `Sonora` + su `idUsuario` (del 2 al 120).

---

## Estructura del proyecto

```
SonoraInc/
├── CreacionBaseSonoraInc.sql     Script completo de la base de datos
├── requirements.txt              Dependencias Python
├── iniciar_entorno.bat           Setup y arranque del entorno virtual
│
└── SonoraIncWeb/                 Proyecto Django
    ├── config.example.json       Plantilla de configuracion (copiar a config.json)
    ├── config.json               Credenciales locales (NO se sube a git)
    ├── manage.py
    │
    ├── db/
    │   └── connection.py         Conexion a SQL Server y clase DB (context manager)
    │
    ├── SonoraIncWeb/
    │   ├── settings.py           Configuracion Django
    │   └── urls.py               Rutas raiz del proyecto
    │
    ├── usuarios/                 Login, registro, perfil
    ├── explorar/                 Inicio, busqueda, detalle artista/album
    ├── interaccion/              Playlists, likes, artistas seguidos, reproducciones
    ├── finanzas/                 Suscripciones, pagos, regalias
    ├── reportes/                 Dashboard con vistas de negocio
    └── catalogo/                 Panel admin: CRUD de canciones, artistas, albumes,
                                  productoras y playlists
```

---

## Modulos y rutas principales

| Ruta | Descripcion | Acceso |
|---|---|---|
| `/explorar/` | Inicio — artistas, albumes, playlists | Usuario |
| `/explorar/buscar/` | Busqueda global | Usuario |
| `/explorar/artistas/<id>/` | Detalle de artista | Usuario |
| `/explorar/albumes/<id>/` | Detalle de album | Usuario |
| `/interaccion/playlists/` | Mis playlists | Usuario |
| `/interaccion/likes/` | Canciones con me gusta | Usuario |
| `/interaccion/artistas/` | Artistas seguidos | Usuario |
| `/finanzas/suscripciones/` | Mi plan (usuario) / Todas las suscripciones (admin) | Ambos |
| `/finanzas/pagos/` | Historial de pagos | Usuario |
| `/finanzas/regalias/` | Regalias por cancion | Usuario |
| `/reportes/` | Dashboard de reportes de negocio | Admin |
| `/catalogo/` | Panel de administracion | Admin |
| `/catalogo/canciones/` | CRUD canciones | Admin |
| `/catalogo/artistas/` | CRUD artistas | Admin |
| `/catalogo/albumes/` | CRUD albumes | Admin |
| `/catalogo/productoras/` | CRUD productoras | Admin |
| `/catalogo/playlists/` | Gestion de playlists de usuarios | Admin |

---

## Arquitectura

- **Clase DB**: context manager en `db/connection.py` que abre/cierra conexion, maneja commit/rollback y convierte resultados a listas de diccionarios.
- **Autenticacion**: sesiones Django. La contrasena se hashea con `SHA2_256` en Python antes de enviarse al SP `sp_IniciarSesion`.
- **Roles**: columna `rolUsuario` en `Seguridad.Usuario` con valores `admin` o `usuario`. El decorador `admin_required` protege las vistas del catalogo.

---

## Dependencias

| Paquete | Version | Uso |
|---|---|---|
| Django | 6.0.5 | Framework web |
| pyodbc | 5.3.0 | Conexion a SQL Server |
| asgiref | 3.11.1 | Soporte asincrono Django |
| sqlparse | 0.5.5 | Parser SQL (dependencia Django) |
| tzdata | 2026.2 | Zonas horarias |
