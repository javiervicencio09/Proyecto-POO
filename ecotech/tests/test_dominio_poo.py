import unittest
from datetime import date

from src.dominio import (
    Administrador,
    Departamento,
    Empleado,
    Informe,
    Proyecto,
    RegistroDeTiempo,
    Usuario,
)


class DominioPOOTestCase(unittest.TestCase):
    def test_usuario_encapsulamiento_y_autenticacion(self):
        usuario = Usuario(1, "Carlos Gomez", "carlos@ecotech.cl")
        usuario.establecer_contrasena("Admin123*")

        self.assertEqual(usuario.id, 1)
        self.assertEqual(usuario.nombre, "Carlos Gomez")
        self.assertTrue(usuario.autenticar("Admin123*"))
        self.assertFalse(usuario.autenticar("Erronea"))

        # Validar excepción por correo inválido
        with self.assertRaises(ValueError):
            usuario.correo = "correo_invalido_sin_arroba"

    def test_herencia_administrador(self):
        admin = Administrador(10, "Super Admin", "admin@ecotech.cl", nivel_acceso="SUPER")

        # Verifica herencia
        self.assertIsInstance(admin, Usuario)
        admin.establecer_contrasena("Root2026")
        self.assertTrue(admin.autenticar("Root2026"))

        # Verifica métodos propios de Administrador definidos en UML
        depto = Departamento(1, "Recursos Humanos", "Juan")
        admin.gestionarDepartamento(depto, nuevo_nombre="RRHH y Personas")
        self.assertEqual(depto.nombre, "RRHH y Personas")

        informe = admin.generarInforme(tipo="Rendimiento Mensual")
        self.assertIsInstance(informe, Informe)
        self.assertEqual(informe.tipo, "Rendimiento Mensual")

    def test_herencia_y_encapsulamiento_empleado(self):
        emp = Empleado(
            id_empleado=5,
            nombre="Valentina Silva",
            cargo="Ingeniera de Software",
            salario=1500000.0,
            correo="valentina@ecotech.cl",
        )

        # Herencia de Usuario
        self.assertIsInstance(emp, Usuario)
        self.assertEqual(emp.id_usuario, 5)

        # Encapsulamiento de salario (no negativo)
        with self.assertRaises(ValueError):
            emp.salario = -500

        with self.assertRaises(ValueError):
            emp.actualizar_salario(-100)

        emp.salario = 1600000.0
        self.assertEqual(emp.salario, 1600000.0)

    def test_registro_de_tiempo_y_calculo_horas(self):
        emp = Empleado(2, "Pedro", "Desarrollador", 1000000, correo="pedro@ecotech.cl")
        proyecto = Proyecto(1, "EcoApp", "App móvil sustentable", date.today())

        registro1 = emp.registrarHoras(proyecto, 4.5, "Desarrollo de API de login")
        registro2 = emp.registrarHoras(proyecto, 3.5, "Pruebas de endpoints")

        self.assertEqual(registro1.horas, 4.5)
        self.assertEqual(registro1.id_empleado, 2)
        self.assertEqual(registro1.id_proyecto, 1)

        total = RegistroDeTiempo.calcularHorasTotales([registro1, registro2])
        self.assertEqual(total, 8.0)

        # Horas inválidas deben disparar excepción
        with self.assertRaises(ValueError):
            emp.registrarHoras(proyecto, -1.0, "Hora negativa")
        with self.assertRaises(ValueError):
            emp.registrarHoras(proyecto, 25.0, "Supera 24 horas diarias")

    def test_informe_generar_y_exportar(self):
        informe = Informe(1, "Reporte de Sostenibilidad", date(2026, 10, 11))
        datos = {"Total Empleados": 15, "Proyectos Activos": 3}
        cuerpo = informe.generar(datos)

        self.assertIn("REPORTE DE SOSTENIBILIDAD", cuerpo)
        self.assertIn("Total Empleados: 15", cuerpo)
        exportado = informe.exportar()
        self.assertEqual(cuerpo, exportado)


if __name__ == "__main__":
    unittest.main()
