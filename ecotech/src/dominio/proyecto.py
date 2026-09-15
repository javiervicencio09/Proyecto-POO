from datetime import date
from typing import List

from .empleado import Empleado


class Proyecto:
    """Representa un proyecto de la empresa y los empleados asignados a él."""

    def __init__(
        self,
        id_proyecto: int,
        nombre: str,
        descripcion: str,
        fecha_inicio: date,
        empleados_asignados: List[Empleado] = None,
    ):
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.empleados_asignados: List[Empleado] = empleados_asignados if empleados_asignados is not None else []

    def asignarEmpleado(self, empleado: Empleado) -> bool:
        """Asigna un empleado al proyecto si aún no está asignado."""
        if any(item.id_empleado == empleado.id_empleado for item in self.empleados_asignados):
            return False
        self.empleados_asignados.append(empleado)
        return True

    def desasignarEmpleado(self, empleado: Empleado | int) -> bool:
        """Desasigna un empleado por objeto o por su identificador."""
        id_empleado = empleado.id_empleado if isinstance(empleado, Empleado) else empleado
        for indice, item in enumerate(self.empleados_asignados):
            if item.id_empleado == id_empleado:
                del self.empleados_asignados[indice]
                return True
        return False

    def asignar_empleado(self, empleado: Empleado) -> bool:
        return self.asignarEmpleado(empleado)

    def desasignar_empleado(self, empleado: Empleado | int) -> bool:
        return self.desasignarEmpleado(empleado)

    def __str__(self) -> str:
        return (
            f"Proyecto(id={self.id_proyecto}, nombre={self.nombre}, "
            f"descripcion={self.descripcion}, inicio={self.fecha_inicio}, "
            f"empleados={len(self.empleados_asignados)})"
        )

