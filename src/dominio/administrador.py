from datetime import date
from typing import TYPE_CHECKING, Optional

from .usuario import Usuario
from .validaciones import validar_texto

if TYPE_CHECKING:
    from .departamento import Departamento
    from .empleado import Empleado
    from .informe import Informe


class Administrador(Usuario):
    """Administrador del sistema EcoTech. Hereda de Usuario (UML: Administrador --|> Usuario)."""

    def __init__(
        self,
        id_usuario: Optional[int],
        nombre: str,
        correo: str,
        contrasena_hash: str = "",
        nivel_acceso: str = "ADMIN",
    ) -> None:
        super().__init__(id_usuario, nombre, correo, contrasena_hash)
        self.nivel_acceso = nivel_acceso

    @property
    def nivel_acceso(self) -> str:
        return self._nivel_acceso

    @nivel_acceso.setter
    def nivel_acceso(self, valor: str) -> None:
        self._nivel_acceso = validar_texto(valor, "El nivel de acceso", 50).upper()

    def generar_informe(self, tipo: str) -> "Informe":
        """UML: generar_informe(tipo: string) Informe. Relación "genera": el informe queda a nombre del admin."""
        from .informe import Informe  # import local: evita dependencia circular al cargar el paquete

        return Informe(
            id_informe=None,
            tipo=tipo,
            fecha_generacion=date.today(),
            contenido="",
            creado_por=self.id_usuario,
        )

    def gestionar_departamento(
        self,
        departamento: "Departamento",
        nuevo_nombre: Optional[str] = None,
        nuevo_gerente: Optional["Empleado"] = None,
    ) -> None:
        """
        UML: gestionar_departamento(departamento). Solo cambia lo que se informa (None = sin cambio);
        las validaciones las aplican los setters del propio Departamento.
        """
        if nuevo_nombre is not None:
            departamento.nombre = nuevo_nombre
        if nuevo_gerente is not None:
            departamento.gerente = nuevo_gerente

    def __str__(self) -> str:
        return (
            f"Administrador(id={self.id_usuario}, nombre='{self.nombre}', "
            f"correo='{self.correo}', nivel='{self.nivel_acceso}')"
        )
