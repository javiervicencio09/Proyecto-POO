"""
Módulo de Excepciones del Sistema EcoTech Solutions.
Define la jerarquía de excepciones personalizadas para el dominio,
la persistencia, la seguridad y el consumo de servicios externos (APIs).
Cumple con los Criterios 3.1.2 y 3.1.3 (estabilidad, seguridad y no exposición sensible).
"""


class EcoTechError(Exception):
    """Excepción raíz de todas las excepciones personalizadas del sistema EcoTech Solutions."""

    def __init__(self, mensaje: str, codigo_error: str = "ECOTECH_ERROR") -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_error = codigo_error

    def __str__(self) -> str:
        return f"[{self.codigo_error}] {self.mensaje}"


# =====================================================================
# EXCEPCIONES DE SEGURIDAD Y VALIDACIÓN (Criterio 3.1.2)
# =====================================================================

class SeguridadError(EcoTechError):
    """Excepción base para violaciones de políticas de seguridad."""

    def __init__(self, mensaje: str, codigo_error: str = "SEGURIDAD_ERROR") -> None:
        super().__init__(mensaje, codigo_error)


class AutenticacionError(SeguridadError):
    """Lanzada cuando fallan las credenciales o se excede el límite de intentos."""

    def __init__(self, mensaje: str = "Credenciales de acceso inválidas.") -> None:
        super().__init__(mensaje, codigo_error="AUTH_ERROR")


class AutorizacionError(SeguridadError):
    """Lanzada cuando un usuario intenta acceder a una funcionalidad sin los privilegios requeridos."""

    def __init__(self, mensaje: str = "No posee los privilegios requeridos para esta acción.") -> None:
        super().__init__(mensaje, codigo_error="ACCESO_DENEGADO")


class ValidacionError(SeguridadError, ValueError):
    """Lanzada cuando una entrada de usuario no cumple con el formato o longitud permitida."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo_error="VALIDACION_ERROR")


# =====================================================================
# EXCEPCIONES DE PERSISTENCIA Y BASE DE DATOS
# =====================================================================

class PersistenciaError(EcoTechError):
    """Excepción base para fallas en la capa de persistencia."""

    def __init__(self, mensaje: str, codigo_error: str = "PERSISTENCIA_ERROR") -> None:
        super().__init__(mensaje, codigo_error)


class ConexionError(PersistenciaError):
    """Lanzada ante fallas de conexión al motor de base de datos."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo_error="CONEXION_BD_ERROR")


class DAOError(PersistenciaError):
    """Lanzada ante fallos en transacciones o consultas SQL."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje, codigo_error="DAO_SQL_ERROR")


# =====================================================================
# EXCEPCIONES DE SERVICIOS EXTERNOS Y APIS (Criterio 3.1.3)
# =====================================================================

class ServicioExternoError(EcoTechError):
    """Excepción base para fallos al interactuar con APIs externas."""

    def __init__(self, mensaje: str, codigo_error: str = "API_ERROR", servicio: str = "") -> None:
        super().__init__(mensaje, codigo_error)
        self.servicio = servicio


class APIConexionError(ServicioExternoError):
    """Lanzada ante problemas de conectividad o red hacia el servicio externo."""

    def __init__(self, mensaje: str = "No fue posible conectar con el servicio externo.", servicio: str = "") -> None:
        super().__init__(mensaje, codigo_error="API_CONEXION_ERROR", servicio=servicio)


class APITimeoutError(ServicioExternoError):
    """Lanzada cuando la solicitud a la API excede el tiempo límite de espera."""

    def __init__(self, mensaje: str = "El servicio externo tardó demasiado en responder.", servicio: str = "") -> None:
        super().__init__(mensaje, codigo_error="API_TIMEOUT", servicio=servicio)


class APIRespuestaError(ServicioExternoError):
    """Lanzada cuando la API responde con un código HTTP de error (404, 500) o JSON inválido."""

    def __init__(self, mensaje: str, codigo_http: int = 0, servicio: str = "") -> None:
        super().__init__(mensaje, codigo_error=f"API_HTTP_{codigo_http}" if codigo_http else "API_RESPUESTA_ERROR", servicio=servicio)
        self.codigo_http = codigo_http


class APICredencialError(ServicioExternoError):
    """Lanzada cuando falta la clave de API o fue rechazada (HTTP 401/403)."""

    def __init__(self, mensaje: str = "Credencial o llave de API externa no configurada o inválida.", servicio: str = "") -> None:
        super().__init__(mensaje, codigo_error="API_AUTH_ERROR", servicio=servicio)
