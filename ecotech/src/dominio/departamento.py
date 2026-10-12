from typing import List, Optional, Union

from .empleado import Empleado


class Departamento:
    """
    Representa un Departamento de EcoTech Solutions.
    Modela agregación con Empleado (1 tiene 1..* Empleados) y asociación con Gerente.
    """

    def __init__(
        self,
        id_departamento: Optional[int],
        nombre: str,
        gerente: Union[Empleado, str, None] = None,
        empleados: Optional[List[Empleado]] = None,
    ) -> None:
        self.id_departamento = id_departamento
        self.nombre = nombre
        self._gerente = gerente
        self.empleados: List[Empleado] = empleados if empleados is not None else []

    @property
    def gerente(self) -> Union[Empleado, str, None]:
        return self._gerente

    @gerente.setter
    def gerente(self, valor: Union[Empleado, str, None]) -> None:
        self._gerente = valor

    @property
    def gerente_nombre(self) -> str:
        """Retorna el nombre del gerente independientemente de si es instancia o cadena."""
        if isinstance(self._gerente, Empleado):
            return self._gerente.nombre
        return str(self._gerente or "Sin Gerente")

    def agregarEmpleado(self, empleado: Empleado) -> None:
        """Método UML (+ agregarEmpleado): asocia un empleado al departamento."""
        if not any(emp.id_empleado == empleado.id_empleado for emp in self.empleados if emp.id_empleado is not None):
            self.empleados.append(empleado)

    def agregar_empleado(self, empleado: Empleado) -> None:
        """Alias en snake_case para convenciones de Python."""
        self.agregarEmpleado(empleado)

    def buscarEmpleado(self, id_empleado: int) -> Optional[Empleado]:
        """Método UML (+ buscarEmpleado): busca un empleado por su identificador."""
        for empleado in self.empleados:
            if empleado.id_empleado == id_empleado:
                return empleado
        return None

    def buscar_empleado(self, id_empleado: int) -> Optional[Empleado]:
        return self.buscarEmpleado(id_empleado)

    def eliminarEmpleado(self, id_empleado: int) -> bool:
        """Método UML (+ eliminarEmpleado): desvincula un empleado del departamento."""
        for indice, empleado in enumerate(self.empleados):
            if empleado.id_empleado == id_empleado:
                del self.empleados[indice]
                return True
        return False

    def eliminar_empleado(self, id_empleado: int) -> bool:
        return self.eliminarEmpleado(id_empleado)

    def eliminarEmpeado(self, id_empleado: int) -> bool:
        """Alias para compatibilidad con código existente."""
        return self.eliminarEmpleado(id_empleado)

    def __str__(self) -> str:
        return (
            f"Departamento(id={self.id_departamento}, nombre='{self.nombre}', "
            f"gerente='{self.gerente_nombre}', empleados={len(self.empleados)})"
        )
