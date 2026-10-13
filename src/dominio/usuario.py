import hashlib
import hmac
import secrets
from typing import Optional

from .validaciones import validar_contrasena, validar_correo, validar_texto


class Usuario:
    """
    Clase base del UML. Administrador y Empleado heredan de ella (relación "hereda"),
    por lo que reutilizan nombre, correo y contraseña sin duplicar código.
    """

    ALGORITMO = "pbkdf2_sha256"
    ITERACIONES = 200_000

    def __init__(
        self,
        id_usuario: Optional[int],
        nombre: str,
        correo: str,
        contrasena_hash: str = "",
    ) -> None:
        self.id_usuario = id_usuario
        self.nombre = nombre  # pasan por su setter: se validan al crear el objeto
        self.correo = correo
        self._contrasena_hash = contrasena_hash

    @property
    def id(self) -> Optional[int]:
        return self.id_usuario

    @id.setter
    def id(self, valor: Optional[int]) -> None:
        self.id_usuario = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self._nombre = validar_texto(valor, "El nombre", 100)

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        self._correo = validar_correo(valor)

    @property
    def contrasena_hash(self) -> str:
        return self._contrasena_hash

    @contrasena_hash.setter
    def contrasena_hash(self, valor: str) -> None:
        self._contrasena_hash = valor

    @staticmethod
    def hashear_contrasena(contrasena_plana: str, sal: Optional[bytes] = None) -> str:
        """
        PBKDF2-HMAC-SHA256 con sal aleatoria (hashlib, librería estándar). Formato guardado:
        algoritmo$iteraciones$sal$hash. La contraseña en texto plano nunca se almacena.
        """
        if not contrasena_plana:
            return ""
        sal = sal if sal is not None else secrets.token_bytes(16)
        derivado = hashlib.pbkdf2_hmac(
            "sha256", contrasena_plana.encode("utf-8"), sal, Usuario.ITERACIONES
        )
        return f"{Usuario.ALGORITMO}${Usuario.ITERACIONES}${sal.hex()}${derivado.hex()}"

    def establecer_contrasena(self, contrasena_plana: str) -> None:
        """Valida la fortaleza de la contraseña y guarda solo su hash."""
        self._contrasena_hash = self.hashear_contrasena(validar_contrasena(contrasena_plana))

    def autenticar(self, contrasena_plana: str) -> bool:
        """Método del UML: autenticar(contrasena_plana: string) bool."""
        if not self._contrasena_hash or not contrasena_plana:
            return False
        try:
            algoritmo, iteraciones, sal_hex, hash_hex = self._contrasena_hash.split("$")
            if algoritmo != self.ALGORITMO:
                return False
            derivado = hashlib.pbkdf2_hmac(
                "sha256", contrasena_plana.encode("utf-8"), bytes.fromhex(sal_hex), int(iteraciones)
            )
        except ValueError:  # hash con formato inesperado
            return False
        return hmac.compare_digest(derivado.hex(), hash_hex)  # comparación en tiempo constante

    def __str__(self) -> str:
        return f"Usuario(id={self.id_usuario}, nombre='{self.nombre}', correo='{self.correo}')"
