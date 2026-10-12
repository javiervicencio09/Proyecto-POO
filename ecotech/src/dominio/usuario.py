import hashlib
from typing import Optional


class Usuario:
    """
    Clase base que modela a un usuario del sistema EcoTech Solutions.
    Aplica encapsulamiento protegiendo credenciales y datos de contacto.
    """

    def __init__(
        self,
        id_usuario: Optional[int],
        nombre: str,
        correo: str,
        contrasena_hash: str = "",
    ) -> None:
        self.id_usuario = id_usuario
        self.nombre = nombre
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
        valor_limpio = valor.strip()
        if valor_limpio and ("@" not in valor_limpio or "." not in valor_limpio):
            raise ValueError(f"Formato de correo electrónico inválido: {valor}")
        self._correo = valor_limpio

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
        return hashlib.sha256(contrasena_plana.encode("utf-8")).hexdigest()

    def establecer_contrasena(self, contrasena_plana: str) -> None:
        """Cifra y almacena la contraseña del usuario."""
        self._contrasena_hash = self.hashear_contrasena(contrasena_plana)

    def autenticar(self, contrasena_plana: str) -> bool:
        """
        Método definido en el UML (+ autenticar: bool).
        Compara la contraseña en texto plano con el hash almacenado.
        """
        if not self._contrasena_hash or not contrasena_plana:
            return False
        return self.hashear_contrasena(contrasena_plana) == self._contrasena_hash

    def __str__(self) -> str:
        return f"Usuario(id={self.id_usuario}, nombre='{self.nombre}', correo='{self.correo}')"
