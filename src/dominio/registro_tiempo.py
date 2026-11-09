from datetime import date
from typing import Iterable, Optional

from .validaciones import validar_fecha, validar_numero, validar_texto


class RegistroDeTiempo:
    """
    Horas que un Empleado dedica a un Proyecto. Las relaciones "registra" (Empleado) y
    "corresponde a" (Proyecto) se guardan como claves id_empleado / id_proyecto, que son
    las columnas foráneas de la tabla registro_tiempo.
    """

    def __init__(
        self,
        id_registro: Optional[int],
        fecha: date,
        horas: float,
        descripcion_tareas: str,
        id_empleado: Optional[int] = None,
        id_proyecto: Optional[int] = None,
    ) -> None:
        self.id_registro = id_registro
        self.fecha = fecha
        self.horas = horas
        self.descripcion_tareas = descripcion_tareas
        self.id_empleado = id_empleado
        self.id_proyecto = id_proyecto

    @property
    def fecha(self) -> date:
        return self._fecha

    @fecha.setter
    def fecha(self, valor: date) -> None:
        self._fecha = validar_fecha(valor, "La fecha del registro")

    @property
    def horas(self) -> float:
        return self._horas

    @horas.setter
    def horas(self, valor: float) -> None:
        self._horas = validar_numero(valor, "Las horas", minimo=0, maximo=24, minimo_exclusivo=True)

    @property
    def descripcion_tareas(self) -> str:
        return self._descripcion_tareas

    @descripcion_tareas.setter
    def descripcion_tareas(self, valor: str) -> None:
        self._descripcion_tareas = validar_texto(valor, "La descripción de tareas", 500)

    @staticmethod
    def calcular_horas_totales(registros: Iterable["RegistroDeTiempo"]) -> float:
        """UML: calcular_horas_totales(registros: list) float."""
        return sum(reg.horas for reg in registros)

    def __str__(self) -> str:
        return (
            f"RegistroDeTiempo(id={self.id_registro}, fecha={self.fecha}, horas={self.horas}, "
            f"empleado={self.id_empleado}, proyecto={self.id_proyecto})"
        )
