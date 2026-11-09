"""
Servicio Externo de Indicadores Económicos y Divisas - EcoTech Solutions (Criterios 3.1.1, 3.1.2, 3.1.3).
Permite consultar el tipo de cambio de monedas internacionales (USD, EUR, etc.)
en tiempo real para liquidar y ajustar pagos de trabajadores en proyectos internacionales.
"""

import logging
import os
from typing import Any, Dict, Optional

import requests

from src.dominio.pago_internacional import PagoInternacional
from src.excepciones import (
    APIConexionError,
    APIRespuestaError,
    APITimeoutError,
    ServicioExternoError,
)
from src.seguridad.validador import validar_codigo_moneda, validar_numero

logger = logging.getLogger("ecotech.servicios_externos.divisas")


class DivisasService:
    """
    Cliente para la consulta de tipos de cambio internacionales.
    Utiliza como proveedor primario Mindicador.cl (API oficial de indicadores económicos de Chile)
    y dispone de fallback automático mediante Open Exchange Rates / open.er-api.
    """

    def __init__(self, timeout: Optional[float] = None) -> None:
        self.provider = os.getenv("EXCHANGE_API_PROVIDER", "mindicador").lower().strip()
        self.api_url = os.getenv("EXCHANGE_API_URL", "https://mindicador.cl/api")
        self.fallback_url = os.getenv("EXCHANGE_FALLBACK_URL", "https://open.er-api.com/v6/latest/CLP")
        try:
            self.timeout = float(timeout or os.getenv("API_TIMEOUT", "5.0"))
        except (ValueError, TypeError):
            self.timeout = 5.0

    def obtener_tasa_cambio(
        self, moneda_destino: str = "USD", moneda_origen: str = "CLP"
    ) -> Dict[str, Any]:
        """
        Obtiene la tasa de conversión actual entre moneda_origen y moneda_destino.
        Retorna un diccionario con:
        - 'moneda_origen': str
        - 'moneda_destino': str
        - 'tasa_directa': float (cuánto equivale 1 unidad de origen en destino)
        - 'valor_un_dolar_en_pesos': float (referencia para CLP)
        - 'fecha_actualizacion': str
        - 'fuente': str
        """
        origen = validar_codigo_moneda(moneda_origen)
        destino = validar_codigo_moneda(moneda_destino)

        if origen == destino:
            return {
                "moneda_origen": origen,
                "moneda_destino": destino,
                "tasa_directa": 1.0,
                "fecha_actualizacion": "Hoy",
                "fuente": "Paridad Idéntica (1:1)",
            }

        # Intento con proveedor primario (Mindicador.cl si origen es CLP y destino es USD/EUR)
        if self.provider == "mindicador" and origen == "CLP" and destino in ("USD", "EUR", "UF"):
            try:
                return self._consultar_mindicador(destino)
            except (APITimeoutError, APIConexionError, APIRespuestaError) as err:
                logger.warning("Falla en Mindicador.cl (%s). Activando fallback open.er-api.", err)
                return self._consultar_fallback_rates(origen, destino)

        return self._consultar_fallback_rates(origen, destino)

    def _consultar_mindicador(self, destino: str) -> Dict[str, Any]:
        """Consulta directa a Mindicador.cl."""
        codigo_api = "dolar" if destino == "USD" else ("euro" if destino == "EUR" else "uf")
        url = f"{self.api_url.rstrip('/')}/{codigo_api}"

        try:
            resp = requests.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout as err:
            raise APITimeoutError(
                f"Tiempo de espera agotado al consultar cotización de {destino}.",
                servicio="Mindicador.cl",
            ) from err
        except requests.exceptions.ConnectionError as err:
            raise APIConexionError(
                "No fue posible conectar con Mindicador.cl.",
                servicio="Mindicador.cl",
            ) from err
        except requests.exceptions.RequestException as err:
            raise ServicioExternoError(
                f"Error en la petición a Mindicador.cl: {err}",
                servicio="Mindicador.cl",
            ) from err

        if resp.status_code != 200:
            raise APIRespuestaError(
                f"Mindicador.cl reportó error HTTP {resp.status_code}.",
                codigo_http=resp.status_code,
                servicio="Mindicador.cl",
            )

        try:
            data = resp.json()
            serie = data.get("serie", [])
            if not serie:
                raise APIRespuestaError(
                    f"No se encontraron series de valores para '{destino}'.",
                    servicio="Mindicador.cl",
                )
            ultimo_registro = serie[0]
            valor_clp = float(ultimo_registro.get("valor", 0.0))
            fecha_str = str(ultimo_registro.get("fecha", ""))[:10]

            if valor_clp <= 0:
                raise APIRespuestaError(
                    "Mindicador.cl entregó un valor de tipo de cambio nulo o negativo.",
                    servicio="Mindicador.cl",
                )

            # 1 unidad de destino = valor_clp pesos.
            # Por lo tanto, 1 CLP = (1 / valor_clp) unidades de destino.
            tasa_directa = 1.0 / valor_clp

            return {
                "moneda_origen": "CLP",
                "moneda_destino": destino,
                "tasa_directa": tasa_directa,
                "valor_referencia": valor_clp,
                "fecha_actualizacion": fecha_str,
                "fuente": "Mindicador.cl (Banco Central de Chile)",
            }
        except (ValueError, KeyError) as err:
            raise APIRespuestaError(
                "Error al procesar la respuesta JSON de Mindicador.cl.",
                servicio="Mindicador.cl",
            ) from err

    def _consultar_fallback_rates(self, origen: str, destino: str) -> Dict[str, Any]:
        """Consulta al servicio internacional multi-divisa como contingencia o para monedas no soportadas por Mindicador."""
        url = f"https://open.er-api.com/v6/latest/{origen}"

        try:
            resp = requests.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout as err:
            raise APITimeoutError(
                f"Tiempo de espera agotado al consultar API internacional para {origen}->{destino}.",
                servicio="Open ER API",
            ) from err
        except requests.exceptions.ConnectionError as err:
            raise APIConexionError(
                "No fue posible conectar con el servicio internacional de divisas.",
                servicio="Open ER API",
            ) from err
        except requests.exceptions.RequestException as err:
            raise ServicioExternoError(
                f"Error al consultar divisas internacionales: {err}",
                servicio="Open ER API",
            ) from err

        if resp.status_code != 200:
            raise APIRespuestaError(
                f"El servicio de divisas reportó código HTTP {resp.status_code}.",
                codigo_http=resp.status_code,
                servicio="Open ER API",
            )

        try:
            data = resp.json()
            rates = data.get("rates", {})
            if destino not in rates:
                raise APIRespuestaError(
                    f"La divisa '{destino}' no está disponible en las cotizaciones internacionales.",
                    codigo_http=404,
                    servicio="Open ER API",
                )
            tasa_directa = float(rates[destino])
            fecha_str = str(data.get("time_last_update_utc", ""))[:16]

            return {
                "moneda_origen": origen,
                "moneda_destino": destino,
                "tasa_directa": tasa_directa,
                "valor_referencia": (1.0 / tasa_directa) if tasa_directa > 0 else 0.0,
                "fecha_actualizacion": fecha_str,
                "fuente": "Open Exchange Rates (Global API)",
            }
        except (ValueError, KeyError) as err:
            raise APIRespuestaError(
                "Estructura JSON inválida en cotizaciones internacionales.",
                servicio="Open ER API",
            ) from err

    def calcular_pago_internacional(
        self,
        id_empleado: int,
        salario_origen: float,
        moneda_destino: str = "USD",
        moneda_origen: str = "CLP",
        id_proyecto: Optional[int] = None,
        detalles_adicionales: str = "",
    ) -> PagoInternacional:
        """
        Calcula la liquidación ajustada al tipo de cambio en tiempo real y construye
        una instancia de PagoInternacional con datos validados.
        """
        emp_id = int(validar_numero(id_empleado, "ID Empleado", minimo=1))
        monto_orig = validar_numero(salario_origen, "Monto de origen", minimo=0.0)
        mon_dest = validar_codigo_moneda(moneda_destino)
        mon_orig = validar_codigo_moneda(moneda_origen)

        info_tasa = self.obtener_tasa_cambio(moneda_destino=mon_dest, moneda_origen=mon_orig)
        tasa = float(info_tasa["tasa_directa"])
        monto_convertido = round(monto_orig * tasa, 2)

        detalles = (
            f"Tasa aplicada: {tasa:.6f} ({mon_orig}->{mon_dest}) provista por "
            f"{info_tasa['fuente']} [Fecha: {info_tasa['fecha_actualizacion']}]. "
            f"{detalles_adicionales}".strip()
        )

        return PagoInternacional(
            id_pago=None,
            id_empleado=emp_id,
            id_proyecto=id_proyecto,
            monto_origen=monto_orig,
            moneda_origen=mon_orig,
            monto_convertido=monto_convertido,
            moneda_destino=mon_dest,
            tipo_cambio=tasa,
            detalles=detalles,
        )

