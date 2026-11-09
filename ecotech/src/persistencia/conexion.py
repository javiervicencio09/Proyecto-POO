import logging
import os
import socket
import sqlite3
from typing import Any, Optional

from dotenv import load_dotenv

from src.excepciones import ConexionError

load_dotenv()
logger = logging.getLogger("ecotech.persistencia")

# Cache de disponibilidad de MySQL durante la sesión para evitar reintentos bloqueantes
_MYSQL_DISPONIBLE: Optional[bool] = None


def obtener_motor() -> str:
    """Retorna el motor configurado ('sqlite' o 'mysql'), por defecto 'sqlite'."""
    return os.getenv("DB_ENGINE", "sqlite").lower()


def _revisar_puerto_mysql(host: str, port: int, timeout: float = 0.5) -> bool:
    """Valida rápidamente si el socket de MySQL responde antes de intentar handshake completo."""
    global _MYSQL_DISPONIBLE
    if _MYSQL_DISPONIBLE is not None:
        return _MYSQL_DISPONIBLE
    try:
        with socket.create_connection((host, port), timeout=timeout):
            _MYSQL_DISPONIBLE = True
            return True
    except (socket.error, OSError):
        _MYSQL_DISPONIBLE = False
        return False


def abrir_conexion() -> Any:
    """
    Establece y retorna una conexión con la base de datos configurada.
    Implementa manejo de excepciones y contingencia automática (Criterio 3.1.3):
    Si MySQL no está disponible, conmuta transparentemente a SQLite local asegurando la continuidad del sistema.
    """
    motor = obtener_motor()

    if motor == "sqlite":
        nombre_bd = os.getenv("DB_NAME", "ecotech.db")
        try:
            conn = sqlite3.connect(nombre_bd)
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as err:
            raise ConexionError(f"No fue posible abrir la base de datos SQLite '{nombre_bd}': {err}") from err

    if motor == "mysql":
        try:
            import pymysql
        except ImportError:
            logger.warning("PyMySQL no instalado. Activando contingencia con SQLite local.")
            return _abrir_sqlite_fallback()

        host = os.getenv("DB_HOST", "localhost")
        try:
            port = int(os.getenv("DB_PORT", "3306"))
        except ValueError:
            port = 3306

        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME", "ecotech")

        # Comprobación de socket no bloqueante
        if not _revisar_puerto_mysql(host, port):
            logger.info("Servidor MySQL en %s:%s no disponible. Utilizando SQLite local.", host, port)
            return _abrir_sqlite_fallback()

        try:
            return pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset="utf8mb4",
                autocommit=False,
                connect_timeout=2,
            )
        except (pymysql.MySQLError, Exception) as err:
            global _MYSQL_DISPONIBLE
            _MYSQL_DISPONIBLE = False
            logger.info("Fallo en autenticación/conexión MySQL (%s). Conmutando a SQLite.", err)
            return _abrir_sqlite_fallback()

    raise ConexionError(f"Motor de base de datos no soportado: '{motor}'")


def _abrir_sqlite_fallback() -> sqlite3.Connection:
    """Abre la base de datos local SQLite como mecanismo de resiliencia ante fallos externos."""
    nombre_bd = os.getenv("DB_SQLITE_FALLBACK", "ecotech.db")
    try:
        conn = sqlite3.connect(nombre_bd)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as err:
        raise ConexionError("Falla crítica: No fue posible abrir la base de datos de contingencia.") from err


def probar_conexion() -> bool:
    """Valida si la conexión a la base de datos responde correctamente."""
    try:
        conn = abrir_conexion()
        conn.close()
        return True
    except ConexionError:
        return False
