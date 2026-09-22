from typing import List

from .empleado import Empleado


class Departamento:
    def __init__(self, id_departamento: int | None, nombre: str, gerente: str, empleados: List[Empleado] = None):
        self.id_departamento = id_departamento
        self.nombre = nombre
        self.gerente = gerente
        self.empleados: List[Empleado] = empleados if empleados is not None else []

    def agregar_empleado(self, empleado: Empleado) -> None:
        self.empleados.append(empleado)

    def buscarEmpleado(self, id_empleado: int) -> Empleado | None:
        """Busca un empleado por su identificador dentro del departamento."""
        for empleado in self.empleados:
            if empleado.id_empleado == id_empleado:
                return empleado
        return None

    def eliminarEmpleado(self, id_empleado: int) -> bool:
        """Elimina un empleado por su identificador y devuelve True si se eliminó."""
        for indice, empleado in enumerate(self.empleados):
            if empleado.id_empleado == id_empleado:
                del self.empleados[indice]
                return True
        return False

    def eliminarEmpeado(self, id_empleado: int) -> bool:
        """Alias con el nombre solicitado por el proyecto."""
        return self.eliminarEmpleado(id_empleado)

    def __str__(self) -> str:
        return f"Departamento(id={self.id_departamento}, nombre={self.nombre}, gerente={self.gerente}, empleados={len(self.empleados)})"

