import os
import unittest

from src.dominio.empleado import Empleado
from src.dominio.informe import Informe
from src.dominio.usuario import Usuario
from src.excepciones import (
    APIConexionError,
    APIRespuestaError,
    APITimeoutError,
    AutenticacionError,
    ConexionError,
    DAOError,
    EcoTechError,
    PersistenciaError,
    SeguridadError,
    ServicioExternoError,
    ValidacionError,
)
from src.seguridad.validador import (
    hashear_contrasena,
    sanitizar_nombre_archivo,
    sanitizar_texto,
    validar_ciudad,
    validar_codigo_moneda,
    validar_contrasena,
    validar_correo,
    validar_numero,
    verificar_contrasena,
)


class SeguridadYExcepcionesTestCase(unittest.TestCase):
    """
    Suite de pruebas para validar el manejo de excepciones y los mecanismos defensivos
    de seguridad del sistema EcoTech Solutions (Criterios 3.1.2 y 3.1.3).
    """

    def test_jerarquia_de_excepciones(self):
        """Verifica que las excepciones personalizadas hereden correctamente."""
        self.assertTrue(issubclass(SeguridadError, EcoTechError))
        self.assertTrue(issubclass(ValidacionError, SeguridadError))
        self.assertTrue(issubclass(ValidacionError, ValueError))
        self.assertTrue(issubclass(AutenticacionError, SeguridadError))

        self.assertTrue(issubclass(PersistenciaError, EcoTechError))
        self.assertTrue(issubclass(ConexionError, PersistenciaError))
        self.assertTrue(issubclass(DAOError, PersistenciaError))

        self.assertTrue(issubclass(ServicioExternoError, EcoTechError))
        self.assertTrue(issubclass(APIConexionError, ServicioExternoError))
        self.assertTrue(issubclass(APITimeoutError, ServicioExternoError))
        self.assertTrue(issubclass(APIRespuestaError, ServicioExternoError))

    def test_validacion_correo(self):
        """Valida detección de formatos correctos y bloqueo de correos inválidos."""
        self.assertEqual(validar_correo("admin@ecotech.cl"), "admin@ecotech.cl")
        self.assertEqual(validar_correo("  contacto@empresa.com  "), "contacto@empresa.com")

        with self.assertRaises(ValidacionError):
            validar_correo("")
        with self.assertRaises(ValidacionError):
            validar_correo("correo_sin_arroba.cl")
        with self.assertRaises(ValidacionError):
            validar_correo("correo@invalido")

    def test_validacion_contrasena_y_timing_attack(self):
        """Valida que no se permitan contraseñas cortas o vacías y verifica hash seguro."""
        with self.assertRaises(ValidacionError):
            validar_contrasena("123")
        with self.assertRaises(ValidacionError):
            validar_contrasena("   ")

        pwd = "AdminSeguro2026*"
        h = hashear_contrasena(pwd)
        self.assertTrue(verificar_contrasena(pwd, h))
        self.assertFalse(verificar_contrasena("ClaveErronea", h))
        self.assertFalse(verificar_contrasena("", h))

    def test_prevencion_nan_infinito_en_numeros(self):
        """Valida que no se acepten valores NaN ni infinitos en campos numéricos."""
        self.assertEqual(validar_numero(1500.5, "Salario", minimo=0), 1500.5)

        with self.assertRaises(ValidacionError):
            validar_numero(float("nan"), "Salario")
        with self.assertRaises(ValidacionError):
            validar_numero(float("inf"), "Salario")
        with self.assertRaises(ValidacionError):
            validar_numero(-100, "Salario", minimo=0)

    def test_proteccion_path_traversal(self):
        """Valida que no se permita escapar del directorio de salida en exportación de informes."""
        nombre_limpio = sanitizar_nombre_archivo("../../etc/passwd.txt")
        self.assertNotIn("..", nombre_limpio)
        self.assertNotIn("/", nombre_limpio)
        self.assertEqual(nombre_limpio, "passwd.txt")

        # Debe rechazar extensiones no permitidas (ej. ejecutables o scripts)
        with self.assertRaises(ValidacionError):
            sanitizar_nombre_archivo("malware.exe")

    def test_validaciones_api_ciudad_y_moneda(self):
        """Valida los filtros de entrada requeridos para el consumo de servicios externos."""
        self.assertEqual(validar_ciudad("Santiago"), "Santiago")
        self.assertEqual(validar_ciudad("Viña del Mar"), "Viña del Mar")

        with self.assertRaises(ValidacionError):
            validar_ciudad("<script>alert(1)</script>")
        with self.assertRaises(ValidacionError):
            validar_ciudad("A")  # Demasiado corto

        self.assertEqual(validar_codigo_moneda("usd"), "USD")
        self.assertEqual(validar_codigo_moneda("EUR"), "EUR")

        with self.assertRaises(ValidacionError):
            validar_codigo_moneda("DOLAR")  # No es ISO 3 letras
        with self.assertRaises(ValidacionError):
            validar_codigo_moneda("123")

    def test_empleado_defensivo(self):
        """Valida encapsulamiento y defensas en la clase Empleado."""
        emp = Empleado(1, "Carlos Tapia", "Ingeniero", 1500000.0, correo="carlos@ecotech.cl")
        self.assertEqual(emp.salario, 1500000.0)

        with self.assertRaises(ValueError):
            emp.salario = -500.0
        with self.assertRaises(ValueError):
            emp.salario = float("nan")

    def test_informe_exportar_seguro(self):
        """Verifica que el informe se exporte con nombre de archivo sanitizado."""
        inf = Informe(99, "Resumen Técnico", contenido="Operación exitosa.")
        archivo_salida = "test_export_seguro.txt"
        try:
            inf.exportar(archivo_salida)
            self.assertTrue(os.path.exists(archivo_salida))
        finally:
            if os.path.exists(archivo_salida):
                os.remove(archivo_salida)


if __name__ == "__main__":
    unittest.main()

