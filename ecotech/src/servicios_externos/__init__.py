"""
Módulo de Integración con Servicios Externos (APIs) - EcoTech Solutions.
Implementa clientes robustos y seguros para clima e indicadores económicos (Criterios 3.1.1, 3.1.2, 3.1.3).
"""

from .clima_service import ClimaService
from .divisas_service import DivisasService

__all__ = ["ClimaService", "DivisasService"]

