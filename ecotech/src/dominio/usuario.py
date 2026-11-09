from typing import Optional

from src.seguridad.validador import (
    hashear_contrasena,
    sanitizar_texto,
    validar_contrasena,
    validar_correo,
    verificar_contrasena,
)


class Usuario:
    """
    Clase base que modela a un usuario del sistema EcoTech Solutions.
    Aplica encapsulamiento protegiendo credenciales y datos de contacto,
    con validaciones defensivas y prevención de ataques de tiempo (Criterio 3.1.2).
    """

    def __init__(
        self,
        id_usuario: Optional[int],
        nombre: str,
        correo: str,
        contrasena_hash: str = "",
    ) -> None:
        self.id_usuario = id_usuario
        self.nombre = sanitizar_texto(nombre, max_longitud=100) if nombre else ""
        self._correo = ""
        self.correo = correo
        self._contrasena_hash = contrasena_hash

    @property
    def id(self) -> Optional[int]:
        """Alias para correspondencia exacta con el diagrama UML (- id: int)."""
        return self.id_usuario

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        self.id_usuario = valor

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if valor:
            self._correo = validar_correo(valor)
        else:
            self._correo = ""

    @property
    def contrasena_hash(self) -> str:
        """Propiedad protegida: retorna el hash de la contraseña."""
        return self._contrasena_hash

    @contrasena_hash.setter
    def contrasena_hash(self, valor: str) -> None:
        self._contrasena_hash = valor

    @staticmethod
    def hashear_contrasena(contrasena_plana: str) -> str:
        """Genera el hash seguro SHA-256 de una contraseña en texto plano."""
        if not contrasena_plana:
            return ""
        return hashear_contrasena(contrasena_plana)

    def establecer_contrasena(self, contrasena_plana: str) -> None:
        """
        Valida, cifra y almacena la contraseña del usuario.
        Lanza ValidacionError si la contraseña no cumple con la longitud mínima requerida.
        """
        validar_contrasena(contrasena_plana, min_longitud=6)
        self._contrasena_hash = self.hashear_contrasena(contrasena_plana)

    def autenticar(self, contrasena_plana: str) -> bool:
        """
        Método definido en el UML (+ autenticar: bool).
        Compara de forma segura (mitigando Timing Attacks) la contraseña con el hash almacenado.
        """
        if not self._contrasena_hash or not contrasena_plana:
            return False
        return verificar_contrasena(contrasena_plana, self._contrasena_hash)

    def __str__(self) -> str:
        return f"Usuario(id={self.id_usuario}, nombre='{self.nombre}', correo='{self.correo}')"
