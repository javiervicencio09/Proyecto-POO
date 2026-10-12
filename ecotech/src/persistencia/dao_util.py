from datetime import date, datetime
from typing import Optional, Union

from src.persistencia.conexion import obtener_motor


class DAOError(Exception):
    """Excepción base para operaciones fallidas en la capa de persistencia."""
    pass


def marcador() -> str:
    """Retorna el marcador de parámetros adecuado según el motor SQL ('%s' o '?')."""
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