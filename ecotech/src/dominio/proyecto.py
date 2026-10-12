from datetime import date
from typing import TYPE_CHECKING, List, Optional, Union

from .empleado import Empleado

if TYPE_CHECKING:
    from .registro_tiempo import RegistroDeTiempo


class Proyecto:
    """
    Representa un Proyecto en EcoTech Solutions.
    Modela asignación de empleados y trazabilidad de registros de tiempo.
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
            empleados_asignados if empleados_asignados is not None else []
        )
        self.registros_tiempo: List["RegistroDeTiempo"] = []

    def asignarEmpleado(self, empleado: Empleado) -> bool:
        """Método UML (+ asignarEmpleado): asigna un empleado si no está asignado."""
        if any(item.id_empleado == empleado.id_empleado for item in self.empleados_asignados):
            return False
        self.empleados_asignados.append(empleado)
        return True

    def asignar_empleado(self, empleado: Empleado) -> bool:
        """Alias snake_case para convenciones de Python."""
        return self.asignarEmpleado(empleado)

    def desasignarEmpleado(self, empleado: Union[Empleado, int]) -> bool:
        """Método UML (+ desasignarEmpleado): desasigna un empleado por objeto o ID."""
        id_emp = empleado.id_empleado if isinstance(empleado, Empleado) else empleado
        for indice, item in enumerate(self.empleados_asignados):
            if item.id_empleado == id_emp:
                del self.empleados_asignados[indice]
                return True
        return False

    def desasignar_empleado(self, empleado: Union[Empleado, int]) -> bool:
        return self.desasignarEmpleado(empleado)

    def agregar_registro_tiempo(self, registro: "RegistroDeTiempo") -> None:
        """Asocia un registro de tiempo al proyecto."""
        self.registros_tiempo.append(registro)

    def total_horas_invertidas(self) -> float:
        """Calcula el total acumulado de horas invertidas en el proyecto."""
        return sum(reg.horas for reg in self.registros_tiempo)

    def __str__(self) -> str:
        return (
            f"Proyecto(id={self.id_proyecto}, nombre='{self.nombre}', "
            f"inicio={self.fecha_inicio}, asignados={len(self.empleados_asignados)}, "
            f"horas_totales={self.total_horas_invertidas()})"
        )
