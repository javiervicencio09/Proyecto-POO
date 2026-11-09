"""
Servicio Externo de Consulta Meteorológica - EcoTech Solutions (Criterios 3.1.1, 3.1.2, 3.1.3).
Permite consultar variables climáticas en tiempo real para anticipar escenarios operativos
y planificar la ejecución de proyectos de tecnologías sostenibles.
"""

import logging
import os
from typing import Any, Dict, Optional

import requests

from src.dominio.registro_clima import RegistroClima
from src.excepciones import (
    APIConexionError,
    APICredencialError,
    APIRespuestaError,
    APITimeoutError,
    ServicioExternoError,
)
from src.seguridad.validador import validar_ciudad

logger = logging.getLogger("ecotech.servicios_externos.clima")

# Mapeo de códigos meteorológicos WMO a descripciones en español
WMO_DESCRIPCIONES: Dict[int, str] = {
    0: "Cielo despejado",
    1: "Principalmente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Niebla",
    48: "Niebla con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna densa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia fuerte",
    66: "Lluvia engelante ligera",
    67: "Lluvia engelante fuerte",
    71: "Nevada ligera",
    73: "Nevada moderada",
    75: "Nevada fuerte",
    77: "Granos de nieve",
    80: "Chubascos de lluvia ligeros",
    81: "Chubascos de lluvia moderados",
    82: "Chubascos de lluvia violentos",
    85: "Chubascos de nieve ligeros",
    86: "Chubascos de nieve fuertes",
    95: "Tormenta eléctrica",
    96: "Tormenta eléctrica con granizo ligero",
    99: "Tormenta eléctrica con granizo fuerte",
}


class ClimaService:
    """
    Cliente seguro para el consumo de APIs meteorológicas externas.
    Soporta Open-Meteo (estándar libre sin API key requerida) y OpenWeatherMap (con API key).
    """

    def __init__(self, timeout: Optional[float] = None) -> None:
        self.provider = os.getenv("WEATHER_API_PROVIDER", "open-meteo").lower().strip()
        self.api_key = os.getenv("WEATHER_API_KEY", "").strip()
        self.geocoding_url = os.getenv(
            "WEATHER_GEOCODING_URL", "https://geocoding-api.open-meteo.com/v1/search"
        )
        self.forecast_url = os.getenv(
            "WEATHER_FORECAST_URL", "https://api.open-meteo.com/v1/forecast"
        )
        try:
            self.timeout = float(timeout or os.getenv("API_TIMEOUT", "5.0"))
        except (ValueError, TypeError):
            self.timeout = 5.0

    def consultar_clima(
        self, ciudad: str, id_proyecto: Optional[int] = None
    ) -> RegistroClima:
        """
        Consulta las condiciones climáticas de una ciudad para un proyecto específico.
        Valida la entrada, procesa el JSON externo y retorna una instancia de RegistroClima.
        """
        ciudad_validada = validar_ciudad(ciudad)

        if self.provider == "openweathermap":
            return self._consultar_openweathermap(ciudad_validada, id_proyecto)
        return self._consultar_open_meteo(ciudad_validada, id_proyecto)

    def _consultar_open_meteo(
        self, ciudad: str, id_proyecto: Optional[int]
    ) -> RegistroClima:
        """Consulta utilizando Open-Meteo Geocoding + Forecast APIs."""
        # Paso 1: Geocodificación para obtener coordenadas
        params_geo = {
            "name": ciudad,
            "count": 1,
            "language": "es",
            "format": "json",
        }
        try:
            resp_geo = requests.get(
                self.geocoding_url,
                params=params_geo,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as err:
            logger.warning("Timeout al geocodificar '%s'", ciudad)
            raise APITimeoutError(
                f"Tiempo de espera agotado al localizar '{ciudad}'.",
                servicio="Open-Meteo Geocoding",
            ) from err
        except requests.exceptions.ConnectionError as err:
            logger.warning("Falla de conexión al consultar clima para '%s'", ciudad)
            raise APIConexionError(
                "No fue posible conectar con el servicio meteorológico. Compruebe su conexión a la red.",
                servicio="Open-Meteo",
            ) from err
        except requests.exceptions.RequestException as err:
            raise ServicioExternoError(
                "Ocurrió un error en la solicitud meteorológica.",
                servicio="Open-Meteo",
            ) from err

        if resp_geo.status_code != 200:
            raise APIRespuestaError(
                f"El servicio de localización respondió con código HTTP {resp_geo.status_code}.",
                codigo_http=resp_geo.status_code,
                servicio="Open-Meteo",
            )

        try:
            data_geo = resp_geo.json()
        except ValueError as err:
            raise APIRespuestaError(
                "Respuesta inválida recibida del servicio de geolocalización.",
                servicio="Open-Meteo",
            ) from err

        resultados = data_geo.get("results")
        if not resultados or not isinstance(resultados, list):
            raise APIRespuestaError(
                f"No se encontraron coordenadas meteorológicas para '{ciudad}'.",
                codigo_http=404,
                servicio="Open-Meteo",
            )

        primer_resultado = resultados[0]
        lat = primer_resultado.get("latitude")
        lon = primer_resultado.get("longitude")
        nombre_normalizado = primer_resultado.get("name", ciudad)
        pais = primer_resultado.get("country", "")
        ubicacion_completa = f"{nombre_normalizado}, {pais}" if pais else nombre_normalizado

        # Paso 2: Consulta del clima actual en base a coordenadas
        params_forecast = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        }
        try:
            resp_forecast = requests.get(
                self.forecast_url,
                params=params_forecast,
                timeout=self.timeout,
            )
        except requests.exceptions.Timeout as err:
            raise APITimeoutError(
                f"Tiempo de espera agotado al consultar el pronóstico para '{ciudad}'.",
                servicio="Open-Meteo Forecast",
            ) from err
        except requests.exceptions.ConnectionError as err:
            raise APIConexionError(
                "Falla de conexión al obtener datos del pronóstico meteorológico.",
                servicio="Open-Meteo",
            ) from err
        except requests.exceptions.RequestException as err:
            raise ServicioExternoError(
                "Error de transporte al consultar pronóstico del clima.",
                servicio="Open-Meteo",
            ) from err

        if resp_forecast.status_code != 200:
            raise APIRespuestaError(
                f"Servicio meteorológico reportó código HTTP {resp_forecast.status_code}.",
                codigo_http=resp_forecast.status_code,
                servicio="Open-Meteo",
            )

        try:
            data_forecast = resp_forecast.json()
        except ValueError as err:
            raise APIRespuestaError(
                "Respuesta JSON malformada desde la API de pronóstico.",
                servicio="Open-Meteo",
            ) from err

        current = data_forecast.get("current", {})
        temp = float(current.get("temperature_2m", 0.0))
        hum = float(current.get("relative_humidity_2m", 0.0))
        code = int(current.get("weather_code", 0))
        viento = float(current.get("wind_speed_10m", 0.0))

        estado_descripcion = WMO_DESCRIPCIONES.get(code, "Condición meteorológica variable")
        recomendacion = self._generar_recomendacion_operativa(code, temp, hum, viento)

        return RegistroClima(
            id_registro_clima=None,
            id_proyecto=id_proyecto,
            ciudad=ubicacion_completa,
            temperatura=temp,
            humedad=hum,
            estado_clima=estado_descripcion,
            recomendacion=recomendacion,
        )

    def _consultar_openweathermap(
        self, ciudad: str, id_proyecto: Optional[int]
    ) -> RegistroClima:
        """Consulta utilizando OpenWeatherMap (requiere WEATHER_API_KEY)."""
        if not self.api_key:
            raise APICredencialError(
                "WEATHER_API_KEY no configurada en el archivo .env para OpenWeatherMap.",
                servicio="OpenWeatherMap",
            )

        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": ciudad,
            "appid": self.api_key,
            "units": "metric",
            "lang": "es",
        }
        try:
            resp = requests.get(url, params=params, timeout=self.timeout)
        except requests.exceptions.Timeout as err:
            raise APITimeoutError(
                f"Tiempo de espera agotado al consultar OpenWeatherMap para '{ciudad}'.",
                servicio="OpenWeatherMap",
            ) from err
        except requests.exceptions.ConnectionError as err:
            raise APIConexionError(
                "Falla de conexión hacia OpenWeatherMap.",
                servicio="OpenWeatherMap",
            ) from err
        except requests.exceptions.RequestException as err:
            raise ServicioExternoError(
                "Error de transporte HTTP con OpenWeatherMap.",
                servicio="OpenWeatherMap",
            ) from err

        if resp.status_code == 401:
            raise APICredencialError(
                "Llave de API rechazada por OpenWeatherMap (código 401).",
                servicio="OpenWeatherMap",
            )
        if resp.status_code == 404:
            raise APIRespuestaError(
                f"Localidad '{ciudad}' no encontrada en OpenWeatherMap.",
                codigo_http=404,
                servicio="OpenWeatherMap",
            )
        if resp.status_code != 200:
            raise APIRespuestaError(
                f"Error en OpenWeatherMap: código HTTP {resp.status_code}.",
                codigo_http=resp.status_code,
                servicio="OpenWeatherMap",
            )

        try:
            data = resp.json()
            main = data.get("main", {})
            weather_list = data.get("weather", [{}])
            wind = data.get("wind", {})

            temp = float(main.get("temp", 0.0))
            hum = float(main.get("humidity", 0.0))
            desc = str(weather_list[0].get("description", "Variable")).capitalize()
            viento = float(wind.get("speed", 0.0)) * 3.6  # m/s a km/h
            recomendacion = self._generar_recomendacion_operativa(0, temp, hum, viento, desc)

            return RegistroClima(
                id_registro_clima=None,
                id_proyecto=id_proyecto,
                ciudad=data.get("name", ciudad),
                temperatura=temp,
                humedad=hum,
                estado_clima=desc,
                recomendacion=recomendacion,
            )
        except Exception as err:
            raise APIRespuestaError(
                "Error al procesar el formato de respuesta de OpenWeatherMap.",
                servicio="OpenWeatherMap",
            ) from err

    @staticmethod
    def _generar_recomendacion_operativa(
        wmo_code: int,
        temp: float,
        humedad: float,
        viento_kmh: float,
        desc: str = "",
    ) -> str:
        """
        Genera una directriz operativa para proyectos sostenibles de EcoTech Solutions
        (instalación de paneles fotovoltaicos, aerogeneradores, faenas en terreno).
        """
        desc_lower = desc.lower()
        if wmo_code in range(51, 100) or any(
            p in desc_lower for p in ("lluvia", "tormenta", "nieve", "granizo")
        ):
            return (
                "ALERTA METEOROLÓGICA: Precipitaciones o tormenta activa. "
                "Suspender trabajos en altura, cableado exterior e instalación de paneles solares."
            )

        if viento_kmh > 35.0:
            return (
                f"ALERTA POR RÁFAGAS ({viento_kmh:.1f} km/h): Viento fuerte en terreno. "
                "Restringir izaje de cargas pesadas y asegurar estructuras fotovoltaicas y andamios."
            )

        if temp > 35.0:
            return (
                f"ALERTA TÉRMICA ({temp:.1f}°C): Exposición a calor extremo. "
                "Disponer puntos de hidratación obligatoria y pausas térmicas para cuadrillas."
            )

        if temp < 0.0:
            return (
                f"ALERTA POR HELADAS ({temp:.1f}°C): Bajas temperaturas y riesgo de escarcha. "
                "Precaución en superficies resbaladizas y retrasar fraguado de hormigón."
            )

        return (
            f"CONDICIONES ÓPTIMAS (Viento: {viento_kmh:.1f} km/h, Humedad: {humedad:.0f}%): "
            "Faenas de terreno, mantenimiento ambiental y montaje habilitados con normalidad."
        )

