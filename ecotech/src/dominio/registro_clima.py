from datetime import datetime
from typing import Optional

from src.seguridad.validador import sanitizar_texto, validar_ciudad, validar_numero


class RegistroClima:
    """
    Modela el registro de variables climáticas externas asociadas a un proyecto de EcoTech Solutions.
    Permite apoyar la toma de decisiones operativas y anticipar retrasos en terreno (Criterio 3.1.1).
    """

    def __init__(
        self,
        id_registro_clima: Optional[int],
        id_proyecto: Optional[int],
        ciudad: str,
        temperatura: float,
        humedad: float,
        estado_clima: str,
        recomendacion: str = "",
        fecha_consulta: Optional[str] = None,
    ) -> None:
        self.id_registro_clima = id_registro_clima
        self.id_proyecto = id_proyecto
        self.ciudad = validar_ciudad(ciudad)
        self.temperatura = validar_numero(temperatura, "La temperatura", minimo=-50.0, maximo=65.0)
        self.humedad = validar_numero(humedad, "La humedad", minimo=0.0, maximo=100.0)
        self.estado_clima = sanitizar_texto(estado_clima, max_longitud=100)
        self.recomendacion = sanitizar_texto(recomendacion, max_longitud=500, permitir_vacio=True)
        self.fecha_consulta = fecha_consulta or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def es_condicion_favorable(self) -> bool:
        """Determina si las condiciones meteorológicas son aptas para faenas de terreno."""
        clima_inferior = self.estado_clima.lower()
        adversos = ("lluvia", "tormenta", "nieve", "granizo", "viento fuerte", "temporal")
        if any(adverso in clima_inferior for adverso in adversos):
            return False
        if self.temperatura > 38.0 or self.temperatura < 0.0:
            return False
        return True

    def __str__(self) -> str:
        estado = "FAVORABLE" if self.es_condicion_favorable() else "DESFAVORABLE"
        return (
            f"RegistroClima(proyecto_id={self.id_proyecto}, ciudad='{self.ciudad}', "
            f"temp={self.temperatura:.1f}°C, hum={self.humedad:.0f}%, "
            f"estado='{self.estado_clima}', aptitud={estado})"
        )

