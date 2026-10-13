from typing import List, Optional

from .empleado import Empleado
from .validaciones import validar_texto


class Departamento:
    """
    Departamento de EcoTech. Relaciones del UML:
      - "empleados": Departamento 1 ◇── 0..* Empleado  -> lista self.empleados
      - "gerente":   Departamento 1 ◇── 0..1 Empleado  -> self.gerente (Empleado o None)
    """

    def __init__(
        self,
        id_departamento: Optional[int],
        nombre: str,
        gerente: Optional[Empleado] = None,
        empleados: Optional[List[Empleado]] = None,
    ) -> None:
        self.id_departamento = id_departamento
        self.nombre = nombre
        self.gerente = gerente
        self.empleados: List[Empleado] = list(empleados) if empleados is not None else []

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "El nombre del departamento", 100)

    @property
    def gerente(self) -> Optional[Empleado]:
        return self._gerente

    @gerente.setter
    def gerente(self, valor: Optional[Empleado]) -> None:
        if valor is not None and not isinstance(valor, Empleado):
            raise ValueError("El gerente debe ser un Empleado (o None si el departamento no tiene).")
        self._gerente = valor

    @property
    def gerente_nombre(self) -> str:
        return self._gerente.nombre if self._gerente is not None else "Sin gerente"

    def agregar_empleado(self, empleado: Empleado) -> None:
        """UML: agregar_empleado(empleado) void. No agrega al mismo empleado dos veces."""
        if not isinstance(empleado, Empleado):
            raise ValueError("Debe indicar un Empleado válido.")
        if empleado not in self.empleados:  # usa Empleado.__eq__
            self.empleados.append(empleado)

    def eliminar_empleado(self, empleado: Empleado) -> None:
        """UML: eliminar_empleado(empleado) void."""
        if empleado in self.empleados:
            self.empleados.remove(empleado)

    def buscar_empleado(self, id_empleado: int) -> Optional[Empleado]:
        """UML: buscar_empleado(id_empleado) Empleado. None si no pertenece al departamento."""
        for emp in self.empleados:
            if emp.id_empleado == id_empleado:
                return emp
        return None

    def __str__(self) -> str:
        return (
            f"Departamento(id={self.id_departamento}, nombre='{self.nombre}', "
            f"gerente='{self.gerente_nombre}', empleados={len(self.empleados)})"
        )
