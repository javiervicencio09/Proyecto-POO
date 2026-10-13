"""
Reglas de validación reutilizables. Son la única fuente de verdad: las clases del dominio las usan
en sus setters y main.py las reutiliza para volver a pedir un dato inválido sin duplicar reglas.
Los largos máximos coinciden con las columnas de la base de datos (crear_bd.py).
Todas lanzan ValueError con un mensaje seguro y comprensible para el usuario.
"""
import math
import re
from datetime import date, datetime
from typing import Any, Optional

PATRON_CORREO = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
PATRON_TELEFONO = re.compile(r"^[0-9+\-()\s]{6,20}$")


def validar_texto(valor: Any, campo: str, largo_maximo: int = 255) -> str:
    """Texto obligatorio: sin espacios sobrantes, no vacío y dentro del largo permitido."""
    if not isinstance(valor, str):
        raise ValueError(f"{campo} debe ser un texto.")
    limpio = valor.strip()
    if not limpio:
        raise ValueError(f"{campo} no puede estar vacío.")
    if len(limpio) > largo_maximo:
        raise ValueError(f"{campo} no puede superar {largo_maximo} caracteres.")
    return limpio


def validar_texto_opcional(valor: Any, campo: str, largo_maximo: int = 255) -> str:
    """Texto que puede quedar vacío ('' si no se informa), pero si se informa debe ser válido."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return ""
    return validar_texto(valor, campo, largo_maximo)


def validar_correo(valor: Any) -> str:
    """Correo obligatorio con formato válido; se guarda en minúsculas."""
    limpio = validar_texto(valor, "El correo", 150).lower()
    if not PATRON_CORREO.match(limpio):
        raise ValueError(f"Formato de correo electrónico inválido: {limpio}")
    return limpio


def validar_telefono(valor: Any) -> str:
    """Teléfono opcional: dígitos, espacios y los símbolos + - ( )."""
    limpio = validar_texto_opcional(valor, "El teléfono", 20)
    if limpio and not PATRON_TELEFONO.match(limpio):
        raise ValueError("El teléfono solo puede tener números, espacios y los símbolos + - ( ) (6 a 20 caracteres).")
    return limpio


def validar_contrasena(valor: Any) -> str:
    """Contraseña de al menos 8 caracteres con letras y números."""
    if not isinstance(valor, str) or len(valor) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if not any(c.isalpha() for c in valor) or not any(c.isdigit() for c in valor):
        raise ValueError("La contraseña debe incluir letras y números.")
    return valor


def validar_numero(
    valor: Any,
    campo: str,
    minimo: Optional[float] = None,
    maximo: Optional[float] = None,
    minimo_exclusivo: bool = False,
) -> float:
    """
    Número finito dentro de un rango. Rechaza booleanos (True se comporta como 1 en Python),
    texto no numérico y también 'nan' / 'inf', que float() acepta y romperían las comparaciones.
    """
    if isinstance(valor, bool):
        raise ValueError(f"{campo} no puede ser un valor booleano.")
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{campo} debe ser un valor numérico.") from None
    if not math.isfinite(numero):
        raise ValueError(f"{campo} debe ser un número finito.")
    if minimo is not None:
        if minimo_exclusivo and numero <= minimo:
            raise ValueError(f"{campo} debe ser mayor que {minimo:g}.")
        if not minimo_exclusivo and numero < minimo:
            raise ValueError(f"{campo} no puede ser menor que {minimo:g}.")
    if maximo is not None and numero > maximo:
        raise ValueError(f"{campo} no puede superar {maximo:g}.")
    return numero


def validar_fecha(valor: Any, campo: str, opcional: bool = False) -> Optional[date]:
    """Fecha de tipo date (un datetime se reduce a su fecha)."""
    if valor is None:
        if opcional:
            return None
        raise ValueError(f"{campo} es obligatoria.")
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    raise ValueError(f"{campo} debe ser una fecha válida.")
