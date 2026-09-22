from datetime import date
from typing import Optional


class Empleado:
    def __init__(
        self,
        id_empleado: Optional[int],
        nombre: str,
        cargo: str,
        salario: float,
        direccion: str = "",
        telefono: str = "",
        correo: str = "",
        fecha_inicio_contrato: Optional[date] = None,
    ):
        self.id_empleado = id_empleado
        self.nombre = nombre
        self.cargo = cargo
        self.salario = salario
        self.direccion = direccion
        self.telefono = telefono
        self.correo = correo
        self.fecha_inicio_contrato = fecha_inicio_contrato

    def actualizar_salario(self, nuevo_salario: float) -> float:
        """Actualiza el salario del empleado y devuelve el nuevo valor."""
        if nuevo_salario < 0:
            raise ValueError("El salario no puede ser negativo.")
        self.salario = nuevo_salario
        return self.salario

    def __str__(self) -> str:
        return (
            f"Empleado(id={self.id_empleado}, nombre={self.nombre}, "
            f"cargo={self.cargo}, salario={self.salario})"
        )
