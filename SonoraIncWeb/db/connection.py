import json
import pyodbc
from pathlib import Path

# config.json vive fuera del paquete db/, por eso se sube un nivel con parent.parent
_cfg = json.loads((Path(__file__).parent.parent / 'config.json').read_text())['database']

# TrustServerCertificate evita el error de certificado en instancias locales de SQL Server
_CONNECTION_STRING = (
    f"DRIVER={{{_cfg['driver']}}};"
    f"SERVER={_cfg['server']};"
    f"DATABASE={_cfg['name']};"
    f"UID={_cfg['user']};"
    f"PWD={_cfg['password']};"
    "TrustServerCertificate=yes;"
)


def get_connection():
    return pyodbc.connect(_CONNECTION_STRING)


class DB:
    """
    Context manager para ejecutar SPs de SonoraInc.

    Ejemplo:
        with DB() as db:
            filas = db.exec("Procesos.sp_ConsultarCanciones")
            fila  = db.exec_one("Procesos.sp_IniciarSesion", correo, hash_pw)
            db.exec_noreturn("Procesos.sp_DarLikeCancion", id_usuario, id_cancion)
    """

    def __enter__(self):
        self.conn   = get_connection()
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, *_):
        # rollback automatico si ocurrio una excepcion dentro del bloque with
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cursor.close()
        self.conn.close()
        # False: no suprime la excepcion, la deja propagarse al llamador
        return False

    def exec(self, sp: str, *params) -> list[dict]:
        """Ejecuta SP y devuelve todas las filas como lista de dicts."""
        # pyodbc espera los placeholders como una sola tupla, no como *args
        sql = f"EXEC {sp} {', '.join(['?'] * len(params))}" if params else f"EXEC {sp}"
        self.cursor.execute(sql, *params)
        return self._to_dicts()

    def exec_one(self, sp: str, *params) -> dict | None:
        """Ejecuta SP y devuelve solo la primera fila."""
        rows = self.exec(sp, *params)
        return rows[0] if rows else None

    def query(self, sql: str, *params) -> list[dict]:
        """Ejecuta SQL directo sobre vistas o tablas (no SPs)."""
        self.cursor.execute(sql, *params)
        return self._to_dicts()

    def exec_noreturn(self, sp: str, *params) -> dict | None:
        """Ejecuta SP de escritura (INSERT/UPDATE/DELETE)."""
        sql = f"EXEC {sp} {', '.join(['?'] * len(params))}" if params else f"EXEC {sp}"
        self.cursor.execute(sql, *params)
        try:
            # algunos SPs de escritura devuelven una fila de confirmacion; se intenta leerla
            return self._to_dicts()[0] if self.cursor.description else None
        except Exception:
            return None

    def _to_dicts(self) -> list[dict]:
        if not self.cursor.description:
            return []
        # c[0] es el nombre de columna segun la especificacion DB-API 2.0
        cols = [c[0] for c in self.cursor.description]
        return [dict(zip(cols, row)) for row in self.cursor.fetchall()]


def parse_sql_error(error: pyodbc.Error) -> str:
    """
    Extrae el mensaje legible de un THROW de SQL Server.
    Ej: THROW 50001, 'El correo ya existe.', 1  ->  'El correo ya existe.'
    """
    msg = str(error)
    if "[SQL Server]" in msg:
        parte = msg.split("[SQL Server]")[-1]
        # el numero de linea va entre parentesis al final; se descarta
        if "(" in parte:
            return parte[:parte.rfind("(")].strip()
        return parte.strip()
    return "Error inesperado. Intenta de nuevo."
