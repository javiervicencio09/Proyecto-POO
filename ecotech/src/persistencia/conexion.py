import os
import sqlite3
from typing import Any

from dotenv import load_dotenv

load_dotenv()


class ConexionError(Exception):
    """Excepción personalizada para fallas de conexión a la base de datos."""
    pass


def obtener_motor() -> str:
    """Retorna el motor configurado ('sqlite' o 'mysql'), por defecto 'sqlite'."""
    return os.getenv("DB_ENGINE", "sqlite").lower()


def abrir_conexion() -> Any:
    """
    Establece y retorna una conexión con la base de datos configurada.
    Implementa manejo de excepciones (Criterio 2.1.4) para estabilidad del sistema.
    """
    motor = obtener_motor()

    if motor == "sqlite":
        nombre_bd = os.getenv("DB_NAME", "ecotech.db")
        try:
            conn = sqlite3.connect(nombre_bd)
            # Habilitar claves foráneas en SQLite para integridad referencial
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as err:
            raise ConexionError(f"No fue posible abrir la base de datos SQLite '{nombre_bd}': {err}") from err

    if motor == "mysql":
        try:
            import pymysql
        except ImportError as err:
            raise ConexionError("El paquete PyMySQL no está instalado en el entorno.") from err

        host = os.getenv("DB_HOST", "localhost")
        port = int(os.getenv("DB_PORT", "3306"))
        user = os.getenv("DB_USER", "root")
        password = os.getenv("DB_PASSWORD", "")
        database = os.getenv("DB_NAME", "ecotech")

        try:
            return pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                charset="utf8mb4",
                autocommit=False,
            )
        except pymysql.MySQLError as err:
            raise ConexionError(
                f"Error al conectar con WampServer MySQL ({host}:{port}/{database}): {err}. "
                "Verifique que WampServer esté activo y que la base de datos exista."
            ) from err

    raise ConexionError(f"Motor de base de datos no soportado: '{motor}'")


def probar_conexion() -> bool:
    """Valida si la conexión a la base de datos responde correctamente."""
    try:
        conn = abrir_conexion()
        conn.close()
        return True
    except ConexionError:
        return False