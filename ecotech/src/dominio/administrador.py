from datetime import date
from typing import TYPE_CHECKING, Optional

from .usuario import Usuario

if TYPE_CHECKING:
    from .departamento import Departamento
    from .informe import Informe


class Administrador(Usuario):
    """
    Representa a un Administrador en el sistema EcoTech Solutions.
    Hereda de Usuario y añade capacidades de gestión de departamentos e informes.
    """

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

    def generarInforme(
        self,
        tipo: str,
        fecha_generacion: Optional[date] = None,
        contenido: str = "",
    ) -> "Informe":
        """
        Método definido en el UML (+ generarInforme).
        Crea una nueva instancia de Informe generada por el administrador.
        """
        from .informe import Informe

        fecha = fecha_generacion or date.today()
        return Informe(
            id_informe=None,
            tipo=tipo,
            fecha_generacion=fecha,
            contenido=contenido,
            creado_por=self.id_usuario,
        )

    def gestionarDepartamento(
        self,
        departamento: "Departamento",
        nuevo_nombre: Optional[str] = None,
        nuevo_gerente: Optional[str] = None,
    ) -> None:
        """
        Método definido en el UML (+ gestionarDepartamento).
        Permite al administrador modificar los datos operacionales de un departamento.
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
