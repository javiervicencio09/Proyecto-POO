"""
Conexión a la base de datos (SQLite o MySQL).

- El motor y las credenciales vienen del archivo .env (nunca del código).
- Los DAO piden la conexión aquí y no conocen credenciales ni el motor activo.
"""
import logging
import os
import sqlite3
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Carpeta raíz del proyecto (dos niveles sobre src/persistencia/conexion.py)
RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

# Excepciones propias de cada conector. PyMySQL es opcional (solo se usa con MySQL).
try:
    import pymysql
    from pymysql.constants import CLIENT

    ERRORES_INTEGRIDAD = (sqlite3.IntegrityError, pymysql.err.IntegrityError)
    ERRORES_BD = (sqlite3.Error, pymysql.MySQLError)
except ImportError:  # pragma: no cover - depende del entorno
    pymysql = None
    CLIENT = None
    ERRORES_INTEGRIDAD = (sqlite3.IntegrityError,)
    ERRORES_BD = (sqlite3.Error,)


class ConexionError(Exception):
    """Falla al conectar con la base de datos. El mensaje es seguro para mostrar al usuario."""


def obtener_motor() -> str:
    """Retorna el motor configurado en DB_ENGINE ('sqlite' o 'mysql'); por defecto 'sqlite'."""
    return os.getenv("DB_ENGINE", "sqlite").strip().lower()


def marcador_sql() -> str:
    """Marcador de parámetros del conector: '?' en SQLite y '%s' en PyMySQL."""
    return "?" if obtener_motor() == "sqlite" else "%s"


def _ruta_sqlite() -> str:
    """Ruta del archivo .db. Si es relativa se calcula desde la raíz del proyecto (no desde el CWD)."""
    ruta = Path(os.getenv("DB_NAME", "ecotech.db"))
    if not ruta.is_absolute():
        ruta = RAIZ_PROYECTO / ruta
    return str(ruta)


def abrir_conexion() -> Any:
    """Abre y retorna una conexión nueva según DB_ENGINE. Lanza ConexionError si no es posible."""
    motor = obtener_motor()

    if motor == "sqlite":
        ruta = _ruta_sqlite()
        try:
            conexion = sqlite3.connect(ruta)
            conexion.execute("PRAGMA foreign_keys = ON")  # SQLite no valida claves foráneas por defecto
            return conexion
        except sqlite3.Error as err:
            logger.error("No se pudo abrir SQLite '%s': %s", ruta, err)
            raise ConexionError("No fue posible abrir la base de datos local.") from err

    if motor == "mysql":
        if pymysql is None:
            raise ConexionError("Falta instalar PyMySQL (pip install -r requirements.txt).")
        try:
            return pymysql.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "3306")),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "ecotech"),
                charset="utf8mb4",
                autocommit=False,
                connect_timeout=5,
                # rowcount = filas encontradas (no solo modificadas), igual que SQLite
                client_flag=CLIENT.FOUND_ROWS,
            )
        except (pymysql.MySQLError, ValueError) as err:
            logger.error("No se pudo conectar a MySQL: %s", err)  # el detalle va al log, no al usuario
            raise ConexionError(
                "No fue posible conectar con la base de datos. Revise la configuración (.env) "
                "y que el servidor MySQL esté activo."
            ) from err

    raise ConexionError(f"Motor de base de datos no soportado: '{motor}'. Use 'sqlite' o 'mysql'.")


def probar_conexion() -> bool:
    """Retorna True si la base de datos responde."""
    try:
        abrir_conexion().close()
        return True
    except ConexionError:
        return False
