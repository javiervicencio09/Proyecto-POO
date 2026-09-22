from src.persistencia.conexion import obtener_motor
from datetime import date, datetime


def marcador() -> str:
    return "%s" if obtener_motor() == "mysql" else "?"


def convertir_fecha(valor: date | datetime | str | None) -> date | None:
    if valor is None or isinstance(valor, date):
        return valor
    return date.fromisoformat(valor)