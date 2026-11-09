from datetime import date, datetime
import sqlite3
from typing import Any, Optional, Union

from src.excepciones import DAOError
from src.persistencia.conexion import obtener_motor


def marcador(conexion: Optional[Any] = None) -> str:
    """
    Retorna el marcador de parámetros adecuado ('%s' o '?').
    Si se suministra una conexión activa, detecta con exactitud si es SQLite o MySQL.
    """
    if conexion is not None:
        if isinstance(conexion, sqlite3.Connection):
            return "?"
        return "%s"
    return "%s" if obtener_motor() == "mysql" else "?"


def convertir_fecha(valor: Union[date, datetime, str, None]) -> Optional[date]:
    """Convierte cadenas ISO o datetimes retornados por la BD a objetos date estándar."""
    if valor is None or isinstance(valor, date):
        return valor
    if isinstance(valor, datetime):
        return valor.date()
    try:
        return date.fromisoformat(str(valor).split(" ")[0])
    except (ValueError, TypeError):
        return None
