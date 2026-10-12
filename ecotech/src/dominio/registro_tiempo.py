from datetime import date
from typing import Iterable, Optional


class RegistroDeTiempo:
    """
    Representa el registro de horas trabajadas por un empleado en un proyecto específico.
    Coresponde a la entidad RegistroDeTiempo del diagrama UML.
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
        self._horas = 0.0
        self.horas = horas
        self.descripcion_tareas = descripcion_tareas
        self.id_empleado = id_empleado
        self.id_proyecto = id_proyecto

    @property
    def horas(self) -> float:
        return self._horas

    @horas.setter
    def horas(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("Las horas trabajadas deben ser mayores a 0.")
        if valor > 24:
            raise ValueError("Las horas trabajadas no pueden superar 24 en un solo día.")
        self._horas = float(valor)

    @property
    def descripcionTareas(self) -> str:
        """Alias para correspondencia exacta con el diagrama UML."""
        return self.descripcion_tareas

    @descripcionTareas.setter
    def descripcionTareas(self, valor: str) -> None:
        self.descripcion_tareas = valor

    @staticmethod
    def calcularHorasTotales(registros: Iterable["RegistroDeTiempo"]) -> float:
        """
        Método definido en el UML (+ calcularHorasTotales: float).
        Calcula el total de horas acumuladas en un conjunto de registros de tiempo.
        """
        return sum(reg.horas for reg in registros)

    def __str__(self) -> str:
        return (
            f"RegistroDeTiempo(id={self.id_registro}, fecha={self.fecha}, "
            f"horas={self.horas}, empleado_id={self.id_empleado}, "
            f"proyecto_id={self.id_proyecto}, tareas='{self.descripcion_tareas}')"
        )
