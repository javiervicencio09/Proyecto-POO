"""
Módulo de Validación y Sanitización de Entradas Seguras (Criterio 3.1.2).
Previene vulnerabilidades de:
- Inyección SQL / XSS mediante sanitización de cadenas.
- Path Traversal en exportación de archivos.
- Ataques de tiempo (Timing Attacks) en validación de contraseñas mediante hmac.compare_digest.
- Denegación de servicio por valores especiales (NaN, Infinito).
- Entradas erróneas para consultas a APIs externas (ciudades y monedas).
"""

import hashlib
import hmac
import math
import os
import re
from typing import Any, Optional, Sequence

from src.excepciones import ValidacionError

# Patrón RFC básico para correo electrónico
PATRON_CORREO = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

# Patrón para nombres de ciudades permitiendo tildes y caracteres internacionales
PATRON_CIUDAD = re.compile(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\.\']{2,80}$")

# Patrón para códigos de divisa ISO 4217 (3 letras mayúsculas, ej: USD, EUR, CLP)
PATRON_MONEDA = re.compile(r"^[A-Z]{3}$")


def validar_correo(correo: str) -> str:
    """
    Valida y sanitiza una dirección de correo electrónico.
    Lanza ValidacionError si no cumple con el formato estándar o está vacío.
    """
    if not correo or not isinstance(correo, str):
        raise ValidacionError("El correo electrónico no puede estar vacío.")

    limpio = correo.strip().lower()
    if len(limpio) > 150:
        raise ValidacionError("El correo electrónico no puede superar los 150 caracteres.")

    if not PATRON_CORREO.match(limpio):
        raise ValidacionError(f"Formato de correo electrónico inválido: '{limpio}'.")

    return limpio


def validar_contrasena(contrasena: str, min_longitud: int = 6) -> str:
    """
    Valida la robustez básica de la contraseña.
    Evita cadenas vacías, compuestas solo por espacios o menores a la longitud mínima.
    """
    if not contrasena or not isinstance(contrasena, str):
        raise ValidacionError("La contraseña no puede estar vacía.")

    limpia = contrasena.strip()
    if len(limpia) < min_longitud:
        raise ValidacionError(
            f"La contraseña debe contener al menos {min_longitud} caracteres."
        )

    return limpia


def hashear_contrasena(contrasena_plana: str) -> str:
    """
    Genera el hash seguro SHA-256 de una contraseña validada.
    """
    validada = validar_contrasena(contrasena_plana)
    return hashlib.sha256(validada.encode("utf-8")).hexdigest()


def verificar_contrasena(contrasena_plana: str, hash_almacenado: str) -> bool:
    """
    Compara de manera segura una contraseña con su hash almacenado.
    Utiliza hmac.compare_digest para mitigar ataques de tiempo (Timing Attacks).
    """
    if not contrasena_plana or not hash_almacenado:
        return False
    try:
        hash_calculado = hashlib.sha256(contrasena_plana.encode("utf-8")).hexdigest()
        return hmac.compare_digest(hash_calculado, hash_almacenado)
    except Exception:
        return False


def sanitizar_texto(texto: str, max_longitud: int = 200, permitir_vacio: bool = False) -> str:
    """
    Sanitiza una entrada de texto eliminando caracteres de control no imprimibles
    y recortando espacios redundantes para prevenir inyecciones.
    """
    if texto is None:
        if permitir_vacio:
            return ""
        raise ValidacionError("El campo no puede ser nulo.")

    # Remover caracteres de control nulos o no imprimibles
    limpio = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", str(texto)).strip()

    if not limpio and not permitir_vacio:
        raise ValidacionError("El campo de texto no puede estar vacío.")

    if len(limpio) > max_longitud:
        raise ValidacionError(f"El texto supera la longitud máxima permitida de {max_longitud} caracteres.")

    return limpio


def validar_ciudad(ciudad: str) -> str:
    """
    Valida que el nombre de una ciudad o localidad para consulta meteorológica
    sea seguro y no contenga secuencias de inyección.
    """
    if not ciudad or not isinstance(ciudad, str):
        raise ValidacionError("El nombre de la ciudad no puede estar vacío.")

    limpia = sanitizar_texto(ciudad, max_longitud=80)
    if not PATRON_CIUDAD.match(limpia):
        raise ValidacionError(
            f"Nombre de ciudad inválido: '{limpia}'. Solo se permiten letras, espacios y guiones."
        )

    return limpia


def validar_codigo_moneda(moneda: str) -> str:
    """
    Valida un código de divisa internacional según estándar ISO 4217 (ej: USD, EUR, CLP).
    """
    if not moneda or not isinstance(moneda, str):
        raise ValidacionError("El código de divisa no puede estar vacío.")

    limpia = moneda.strip().upper()
    if not PATRON_MONEDA.match(limpia):
        raise ValidacionError(
            f"Código de divisa inválido: '{limpia}'. Debe ser un código ISO de 3 letras (ej: USD, EUR, CLP)."
        )

    return limpia


def validar_numero(
    valor: Any,
    nombre_campo: str = "Valor",
    minimo: Optional[float] = None,
    maximo: Optional[float] = None,
) -> float:
    """
    Valida que un valor sea numérico, finito (no NaN, no Infinito) y esté en rango.
    """
    try:
        num = float(valor)
    except (ValueError, TypeError) as err:
        raise ValidacionError(f"{nombre_campo} debe ser un valor numérico válido.") from err

    if not math.isfinite(num):
        raise ValidacionError(f"{nombre_campo} no puede ser un valor infinito o indefinido (NaN).")

    if minimo is not None and num < minimo:
        raise ValidacionError(f"{nombre_campo} debe ser mayor o igual a {minimo}.")

    if maximo is not None and num > maximo:
        raise ValidacionError(f"{nombre_campo} no puede superar {maximo}.")

    return num


def sanitizar_nombre_archivo(
    nombre_archivo: str,
    extensiones_permitidas: Sequence[str] = (".txt", ".json", ".csv"),
) -> str:
    """
    Previene vulnerabilidades de Path Traversal asegurando que el nombre del archivo
    sea un nombre base seguro sin secuencias relativas (../, ..\\) ni rutas absolutas.
    """
    if not nombre_archivo or not isinstance(nombre_archivo, str):
        raise ValidacionError("El nombre del archivo no puede estar vacío.")

    # Extraer solo el nombre base sin rutas
    base = os.path.basename(nombre_archivo.strip())
    # Remover caracteres peligrosos
    base = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', base)

    if not base or base.startswith("."):
        raise ValidacionError("Nombre de archivo inválido o peligroso.")

    # Validar extensión permitida
    _, ext = os.path.splitext(base)
    if ext.lower() not in [e.lower() for e in extensiones_permitidas]:
        permitidas_str = ", ".join(extensiones_permitidas)
        raise ValidacionError(
            f"Extensión no permitida '{ext}'. Solo se admiten: {permitidas_str}."
        )

    return base

