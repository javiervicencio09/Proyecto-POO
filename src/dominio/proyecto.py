from datetime import date
from typing import List, Optional

from .empleado import Empleado
from .registro_tiempo import RegistroDeTiempo
from .validaciones import validar_fecha, validar_texto


class Proyecto:
    """
    Proyecto de EcoTech. Relaciones del UML:
      - "asignado a":    Empleado 0..* ── 0..* Proyecto -> lista self.empleados_asignados
      - "corresponde a": Proyecto 1 ── 0..* RegistroDeTiempo -> lista self.registros_tiempo
    """

    def __init__(
        self,
        id_proyecto: Optional[int],
        nombre: str,
        descripcion: str,
        fecha_inicio: date,
        empleados_asignados: Optional[List[Empleado]] = None,
    ) -> None:
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.empleados_asignados: List[Empleado] = (
            list(empleados_asignados) if empleados_asignados is not None else []
        )
        self.registros_tiempo: List[RegistroDeTiempo] = []

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "El nombre del proyecto", 150)

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self._descripcion = validar_texto(valor, "La descripción del proyecto", 500)

    @property
    def fecha_inicio(self) -> date:
        return self._fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, valor: date) -> None:
        self._fecha_inicio = validar_fecha(valor, "La fecha de inicio")

    def asignar_empleado(self, empleado: Empleado) -> None:
        """UML: asignar_empleado(empleado) void. Un empleado no se asigna dos veces al mismo proyecto."""
        if not isinstance(empleado, Empleado):
            raise ValueError("Debe indicar un Empleado válido.")
        if empleado not in self.empleados_asignados:
            self.empleados_asignados.append(empleado)

    def desasignar_empleado(self, empleado: Empleado) -> None:
        """UML: desasignar_empleado(empleado) void."""
        if empleado in self.empleados_asignados:
            self.empleados_asignados.remove(empleado)

    def __str__(self) -> str:
        return (
            f"Proyecto(id={self.id_proyecto}, nombre='{self.nombre}', inicio={self.fecha_inicio}, "
            f"empleados={len(self.empleados_asignados)})"
        )
