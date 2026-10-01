from datetime import date, datetime


def marcador() -> str:
    return "%s"


def convertir_fecha(valor: date | datetime | str | None) -> date | None:
    if valor is None or isinstance(valor, date):
        return valor
    return date.fromisoformat(valor)