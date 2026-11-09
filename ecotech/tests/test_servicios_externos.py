import unittest
from unittest.mock import MagicMock, patch

import requests

from src.dominio.pago_internacional import PagoInternacional
from src.dominio.registro_clima import RegistroClima
from src.excepciones import (
    APIConexionError,
    APIRespuestaError,
    APITimeoutError,
    ValidacionError,
)
from src.persistencia import ClimaDAO, PagoInternacionalDAO, crear_tablas
from src.servicios_externos import ClimaService, DivisasService


class ServiciosExternosTestCase(unittest.TestCase):
    """
    Suite de pruebas unitarias para el consumo seguro de APIs externas,
    manejo de excepciones de red y persistencia local (Criterios 3.1.1, 3.1.2, 3.1.3).
    """

    @classmethod
    def setUpClass(cls):
        crear_tablas()

    def setUp(self):
        self.clima_service = ClimaService(timeout=2.0)
        self.divisas_service = DivisasService(timeout=2.0)
        self.clima_dao = ClimaDAO()
        self.pago_dao = PagoInternacionalDAO()

    # =========================================================================
    # PRUEBAS DEL SERVICIO METEOROLÓGICO (CLIMA)
    # =========================================================================

    @patch("requests.get")
    def test_clima_consulta_exitosa_open_meteo(self, mock_get):
        """Verifica el flujo exitoso de geocodificación y pronóstico meteorológico."""
        resp_geo = MagicMock()
        resp_geo.status_code = 200
        resp_geo.json.return_value = {
            "results": [
                {"name": "Santiago", "country": "Chile", "latitude": -33.45, "longitude": -70.66}
            ]
        }

        resp_forecast = MagicMock()
        resp_forecast.status_code = 200
        resp_forecast.json.return_value = {
            "current": {
                "temperature_2m": 22.5,
                "relative_humidity_2m": 45.0,
                "weather_code": 0,
                "wind_speed_10m": 12.0,
            }
        }

        mock_get.side_effect = [resp_geo, resp_forecast]

        registro = self.clima_service.consultar_clima("Santiago", id_proyecto=1)
        self.assertIsInstance(registro, RegistroClima)
        self.assertEqual(registro.ciudad, "Santiago, Chile")
        self.assertEqual(registro.temperatura, 22.5)
        self.assertEqual(registro.humedad, 45.0)
        self.assertEqual(registro.estado_clima, "Cielo despejado")
        self.assertTrue(registro.es_condicion_favorable())
        self.assertIn("CONDICIONES ÓPTIMAS", registro.recomendacion)

    @patch("requests.get")
    def test_clima_condicion_adversa_lluvia_tormenta(self, mock_get):
        """Verifica que precipitaciones o vientos generen alertas operativas para proyectos sostenibles."""
        resp_geo = MagicMock()
        resp_geo.status_code = 200
        resp_geo.json.return_value = {
            "results": [{"name": "Valdivia", "country": "Chile", "latitude": -39.81, "longitude": -73.24}]
        }

        resp_forecast = MagicMock()
        resp_forecast.status_code = 200
        resp_forecast.json.return_value = {
            "current": {
                "temperature_2m": 11.0,
                "relative_humidity_2m": 90.0,
                "weather_code": 63,  # Lluvia moderada
                "wind_speed_10m": 42.0,  # Viento fuerte
            }
        }

        mock_get.side_effect = [resp_geo, resp_forecast]

        registro = self.clima_service.consultar_clima("Valdivia")
        self.assertFalse(registro.es_condicion_favorable())
        self.assertIn("ALERTA METEOROLÓGICA", registro.recomendacion)

    @patch("requests.get")
    def test_clima_timeout_de_red(self, mock_get):
        """Valida que solicitudes lentas capturen APITimeoutError sin congelar el sistema."""
        mock_get.side_effect = requests.exceptions.Timeout("Expiró el tiempo de espera.")

        with self.assertRaises(APITimeoutError):
            self.clima_service.consultar_clima("Antofagasta")

    @patch("requests.get")
    def test_clima_falla_de_conexion(self, mock_get):
        """Valida el manejo defensivo cuando no existe conexión a Internet."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Falla de DNS.")

        with self.assertRaises(APIConexionError):
            self.clima_service.consultar_clima("Concepción")

    def test_clima_ciudad_invalida_seguridad(self):
        """Valida que entradas maliciosas o inyecciones se bloqueen antes de enviar paquetes a la red."""
        with self.assertRaises(ValidacionError):
            self.clima_service.consultar_clima("<script>alert('xss')</script>")
        with self.assertRaises(ValidacionError):
            self.clima_service.consultar_clima("")

    # =========================================================================
    # PRUEBAS DEL SERVICIO DE DIVISAS Y PAGOS INTERNACIONALES
    # =========================================================================

    @patch("requests.get")
    def test_divisas_consulta_mindicador_exitosa(self, mock_get):
        """Verifica la conversión de salarios con la API de Mindicador.cl."""
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "codigo": "dolar",
            "serie": [{"fecha": "2026-11-09T03:00:00.000Z", "valor": 950.0}],
        }
        mock_get.return_value = resp

        info = self.divisas_service.obtener_tasa_cambio("USD", "CLP")
        self.assertAlmostEqual(info["tasa_directa"], 1.0 / 950.0)
        self.assertEqual(info["moneda_destino"], "USD")

        pago = self.divisas_service.calcular_pago_internacional(
            id_empleado=10,
            salario_origen=950000.0,
            moneda_destino="USD",
        )
        self.assertEqual(pago.monto_origen, 950000.0)
        self.assertEqual(pago.monto_convertido, 1000.0)
        self.assertEqual(pago.moneda_destino, "USD")

    @patch("requests.get")
    def test_divisas_fallback_automatico(self, mock_get):
        """Verifica que si Mindicador falla, se use automáticamente la API de respaldo."""
        resp_fallback = MagicMock()
        resp_fallback.status_code = 200
        resp_fallback.json.return_value = {
            "result": "success",
            "rates": {"USD": 0.001025, "EUR": 0.00095},
            "time_last_update_utc": "Mon, 09 Nov 2026 12:00:00 +0000",
        }

        # Simular fallo en Mindicador y respuesta exitosa en fallback
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Mindicador caído"),
            resp_fallback,
        ]

        info = self.divisas_service.obtener_tasa_cambio("EUR", "CLP")
        self.assertEqual(info["moneda_destino"], "EUR")
        self.assertEqual(info["tasa_directa"], 0.00095)
        self.assertIn("Global API", info["fuente"])

    # =========================================================================
    # PRUEBAS DE PERSISTENCIA LOCAL DE APIS (Criterio 3.1.1)
    # =========================================================================

    def test_persistencia_clima_dao(self):
        """Valida que los registros de clima se guarden, consulten y sirvan como caché local."""
        from src.dominio.proyecto import Proyecto
        from src.persistencia import ProyectoDAO
        from datetime import date

        proy_dao = ProyectoDAO()
        proy = Proyecto(None, "Parque Solar Atacama", "Instalación fotovoltaica", date.today())
        id_proy = proy_dao.guardar(proy)

        reg = RegistroClima(
            id_registro_clima=None,
            id_proyecto=id_proy,
            ciudad="Calama, Chile",
            temperatura=28.0,
            humedad=15.0,
            estado_clima="Despejado",
            recomendacion="Óptimo para paneles solares.",
        )
        id_c = self.clima_dao.guardar(reg)
        self.assertIsNotNone(id_c)

        recuperado = self.clima_dao.buscar_por_id(id_c)
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.ciudad, "Calama, Chile")

        ultimo = self.clima_dao.obtener_ultimo_clima(id_proy)
        self.assertIsNotNone(ultimo)
        self.assertEqual(ultimo.temperatura, 28.0)

        # Limpieza
        self.assertTrue(self.clima_dao.eliminar(id_c))
        proy_dao.eliminar(id_proy)

    def test_persistencia_pago_internacional_dao(self):
        """Valida que las liquidaciones en divisas se almacenen correctamente en la base de datos."""
        from src.dominio.empleado import Empleado
        from src.persistencia import EmpleadoDAO

        emp_dao = EmpleadoDAO()
        emp = Empleado(None, "Ingeniero Solar", "Especialista", 1800000.0, correo="solar_qa@ecotech.cl")
        id_emp = emp_dao.guardar(emp)

        pago = PagoInternacional(
            id_pago=None,
            id_empleado=id_emp,
            id_proyecto=None,
            monto_origen=1800000.0,
            moneda_origen="CLP",
            monto_convertido=1890.0,
            moneda_destino="USD",
            tipo_cambio=0.00105,
            detalles="Liquidación proyecto internacional.",
        )
        id_p = self.pago_dao.guardar(pago)
        self.assertIsNotNone(id_p)

        pagos_emp = self.pago_dao.listar_por_empleado(id_emp)
        self.assertTrue(len(pagos_emp) >= 1)
        self.assertEqual(pagos_emp[0].moneda_destino, "USD")

        # Limpieza
        self.assertTrue(self.pago_dao.eliminar(id_p))
        emp_dao.eliminar(id_emp)


if __name__ == "__main__":
    unittest.main()
