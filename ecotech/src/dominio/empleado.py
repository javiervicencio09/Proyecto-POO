from datetime import date
from typing import TYPE_CHECKING, Optional

from .usuario import Usuario

if TYPE_CHECKING:
    from .proyecto import Proyecto
    from .registro_tiempo import RegistroDeTiempo


class Empleado(Usuario):
    """
    Representa a un Empleado en EcoTech Solutions.
    Aplica Herencia extendiendo de Usuario y Encapsulamiento protegiendo datos sensibles.
    """

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
        contrasena_hash: str = "",
    ) -> None:
        super().__init__(
            id_usuario=id_empleado,
            nombre=nombre,
            correo=correo,
            contrasena_hash=contrasena_hash,
        )
        self.cargo = cargo
        self._salario = 0.0
        self.salario = salario
        self._direccion = direccion
        self._telefono = telefono
        self.fecha_inicio_contrato = fecha_inicio_contrato

    @property
    def id_empleado(self) -> Optional[int]:
        """Identificador del empleado vinculado al id_usuario base."""
        return self.id_usuario

    @id_empleado.setter
    def id_empleado(self, valor: Optional[int]) -> None:
        self.id_usuario = valor

    @property
    def salario(self) -> float:
        """Salario protegido mediante encapsulamiento."""
        return self._salario

    @salario.setter
    def salario(self, nuevo_salario: float) -> None:
        if nuevo_salario < 0:
            raise ValueError("El salario no puede ser negativo.")
        self._salario = float(nuevo_salario)

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str) -> None:
        self._direccion = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        self._telefono = valor.strip()

    def actualizar_salario(self, nuevo_salario: float) -> float:
        """Actualiza el salario del empleado a través de su setter validado."""
        self.salario = nuevo_salario
        return self.salario

    def registrarHoras(
        self,
        proyecto: "Proyecto",
        horas: float,
        descripcion_tareas: str,
        fecha: Optional[date] = None,
    ) -> "RegistroDeTiempo":
        """
        Método definido en el UML (+ registrarHoras).
        Registra la carga horaria realizada por este empleado en un proyecto.
        """
        from .registro_tiempo import RegistroDeTiempo

        registro = RegistroDeTiempo(
            id_registro=None,
            fecha=fecha or date.today(),
            horas=horas,
            descripcion_tareas=descripcion_tareas,
            id_empleado=self.id_empleado,
            id_proyecto=getattr(proyecto, "id_proyecto", None),
        )
        return registro

    def __str__(self) -> str:
        return (
            f"Empleado(id={self.id_empleado}, nombre='{self.nombre}', "
            f"cargo='{self.cargo}', salario={self.salario})"
        )
