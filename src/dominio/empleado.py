from datetime import date
from typing import TYPE_CHECKING, List, Optional

from .registro_tiempo import RegistroDeTiempo
from .usuario import Usuario
from .validaciones import (
    validar_fecha,
    validar_numero,
    validar_telefono,
    validar_texto,
    validar_texto_opcional,
)

if TYPE_CHECKING:
    from .proyecto import Proyecto


class Empleado(Usuario):
    """Empleado de EcoTech. Hereda de Usuario (UML: Empleado --|> Usuario); id_empleado es el id_usuario."""

    def __init__(
        self,
        id_empleado: Optional[int],
        nombre: str,
        cargo: str,
        salario: float,
        correo: str,
        direccion: str = "",
        telefono: str = "",
        fecha_inicio_contrato: Optional[date] = None,
        contrasena_hash: str = "",
    ) -> None:
        super().__init__(id_usuario=id_empleado, nombre=nombre, correo=correo, contrasena_hash=contrasena_hash)
        self.cargo = cargo
        self.salario = salario
        self.direccion = direccion
        self.telefono = telefono
        self.fecha_inicio_contrato = fecha_inicio_contrato
        # Relación UML "registra" (Empleado 1 ── 0..* RegistroDeTiempo)
        self.registros_tiempo: List[RegistroDeTiempo] = []

    @property
    def id_empleado(self) -> Optional[int]:
        return self.id_usuario

    @id_empleado.setter
    def id_empleado(self, valor: Optional[int]) -> None:
        self.id_usuario = valor

    @property
    def cargo(self) -> str:
        return self._cargo

    @cargo.setter
    def cargo(self, valor: str) -> None:
        self._cargo = validar_texto(valor, "El cargo", 100)

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, valor: float) -> None:
        self._salario = validar_numero(valor, "El salario", minimo=0)

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        self._direccion = validar_texto_opcional(valor, "La dirección", 255)

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self._telefono = validar_telefono(valor)

    @property
    def fecha_inicio_contrato(self) -> Optional[date]:
        return self._fecha_inicio_contrato

    @fecha_inicio_contrato.setter
    def fecha_inicio_contrato(self, valor: Optional[date]) -> None:
        self._fecha_inicio_contrato = validar_fecha(valor, "La fecha de inicio de contrato", opcional=True)

    def registrar_horas(self, proyecto: "Proyecto", horas: float, descripcion_tareas: str) -> RegistroDeTiempo:
        """
        UML: registrar_horas(proyecto, horas, descripcion_tareas) RegistroDeTiempo.
        Crea el registro (que valida horas y descripción) y lo enlaza con ambos extremos de la relación.
        """
        if proyecto is None:
            raise ValueError("Debe indicar un proyecto para registrar horas.")
        registro = RegistroDeTiempo(
            id_registro=None,
            fecha=date.today(),
            horas=horas,
            descripcion_tareas=descripcion_tareas,
            id_empleado=self.id_empleado,
            id_proyecto=proyecto.id_proyecto,
        )
        self.registros_tiempo.append(registro)
        proyecto.registros_tiempo.append(registro)
        return registro

    def __eq__(self, otro: object) -> bool:
        """
        Dos empleados son el mismo si comparten id; mientras no estén guardados (id None)
        solo son iguales si son el mismo objeto. Evita confundir empleados nuevos entre sí.
        """
        if not isinstance(otro, Empleado):
            return NotImplemented
        if self is otro:
            return True
        return self.id_empleado is not None and self.id_empleado == otro.id_empleado

    __hash__ = None  # objeto mutable con igualdad por id: no se usa como clave de conjuntos

    def __str__(self) -> str:
        return f"Empleado(id={self.id_empleado}, nombre='{self.nombre}', cargo='{self.cargo}', salario={self.salario})"
