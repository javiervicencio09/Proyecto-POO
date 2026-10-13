"""Comportamiento POO del dominio: encapsulamiento, herencia, polimorfismo y casos límite."""
import math
import os
import tempfile
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
        self.assertFalse(usuario.autenticar("Erronea1"))
        with self.assertRaises(ValueError):
            usuario.correo = "correo_invalido_sin_arroba"

    def test_contrasena_debil_es_rechazada(self):
        usuario = Usuario(1, "Carlos", "carlos@ecotech.cl")
        for debil in ("corta1", "sololetrasaqui", "12345678", ""):
            with self.subTest(contrasena=debil), self.assertRaises(ValueError):
                usuario.establecer_contrasena(debil)

    def test_misma_contrasena_genera_hashes_distintos_por_la_sal(self):
        a, b = Usuario(1, "A", "a@ecotech.cl"), Usuario(2, "B", "b@ecotech.cl")
        a.establecer_contrasena("Igual1234")
        b.establecer_contrasena("Igual1234")
        self.assertNotEqual(a.contrasena_hash, b.contrasena_hash)
        self.assertTrue(a.autenticar("Igual1234") and b.autenticar("Igual1234"))

    def test_herencia_y_polimorfismo(self):
        admin = Administrador(10, "Super Admin", "admin@ecotech.cl", nivel_acceso="super")
        emp = Empleado(11, "Ema", "Dev", 1, "ema@ecotech.cl")
        for usuario in (admin, emp):
            self.assertIsInstance(usuario, Usuario)
            usuario.establecer_contrasena("Root2026")
            self.assertTrue(usuario.autenticar("Root2026"))  # método heredado, no duplicado
        self.assertEqual(admin.nivel_acceso, "SUPER")
        self.assertIn("Administrador(", str(admin))   # __str__ especializado
        self.assertIn("Empleado(", str(emp))

    def test_empleado_encapsulamiento(self):
        emp = Empleado(5, "Valentina Silva", "Ingeniera", 1500000.0, "valentina@ecotech.cl")
        self.assertEqual(emp.id_usuario, 5)
        self.assertEqual(emp.id_empleado, 5)

        for invalido in (-500, True, "abc", None, math.nan, math.inf):
            with self.subTest(salario=invalido), self.assertRaises(ValueError):
                emp.salario = invalido
        emp.salario = "1600000"
        self.assertEqual(emp.salario, 1600000.0)

        with self.assertRaises(ValueError):
            emp.cargo = "   "
        with self.assertRaises(ValueError):
            emp.telefono = "abc"
        emp.telefono = "+56 9 1234 5678"
        self.assertEqual(emp.telefono, "+56 9 1234 5678")

    def test_empleado_nuevos_no_se_confunden_entre_si(self):
        """Dos empleados aún sin id son distintos; con el mismo id son el mismo."""
        a = Empleado(None, "A", "Dev", 1, "a@ecotech.cl")
        b = Empleado(None, "B", "Dev", 1, "b@ecotech.cl")
        self.assertNotEqual(a, b)
        self.assertEqual(Empleado(3, "X", "Dev", 1, "x@ecotech.cl"), Empleado(3, "Y", "QA", 1, "y@ecotech.cl"))

        depto = Departamento(1, "D")
        depto.agregar_empleado(a)
        depto.agregar_empleado(b)
        depto.agregar_empleado(a)          # repetido: no se duplica
        self.assertEqual(len(depto.empleados), 2)
        depto.eliminar_empleado(b)         # elimina a B y no a A
        self.assertEqual(depto.empleados, [a])

        proyecto = Proyecto(1, "P", "d", date.today())
        proyecto.asignar_empleado(a)
        proyecto.asignar_empleado(b)
        self.assertEqual(len(proyecto.empleados_asignados), 2)
        proyecto.desasignar_empleado(a)
        self.assertEqual(proyecto.empleados_asignados, [b])

    def test_departamento_busca_empleado(self):
        emp = Empleado(9, "Nueve", "Dev", 1, "nueve@ecotech.cl")
        depto = Departamento(1, "D", empleados=[emp])
        self.assertIs(depto.buscar_empleado(9), emp)
        self.assertIsNone(depto.buscar_empleado(123))
        self.assertEqual(Departamento(2, "Sin gerente").gerente_nombre, "Sin gerente")

    def test_registro_de_tiempo_y_calculo_horas(self):
        emp = Empleado(2, "Pedro", "Desarrollador", 1000000, "pedro@ecotech.cl")
        proyecto = Proyecto(1, "EcoApp", "App móvil sustentable", date.today())

        registro1 = emp.registrar_horas(proyecto, 4.5, "Desarrollo de API de login")
        registro2 = emp.registrar_horas(proyecto, 3.5, "Pruebas de endpoints")

        self.assertEqual(registro1.horas, 4.5)
        self.assertEqual((registro1.id_empleado, registro1.id_proyecto), (2, 1))
        self.assertEqual(RegistroDeTiempo.calcular_horas_totales([registro1, registro2]), 8.0)
        self.assertEqual(len(emp.registros_tiempo), 2)
        self.assertEqual(len(proyecto.registros_tiempo), 2)

    def test_horas_invalidas_no_dejan_registros_a_medias(self):
        emp = Empleado(2, "Pedro", "Dev", 1, "pedro@ecotech.cl")
        proyecto = Proyecto(1, "EcoApp", "d", date.today())
        casos = [(-1.0, "negativa"), (0, "cero"), (25.0, "supera 24"), (math.nan, "nan"), (True, "bool"), ("x", "texto")]
        for horas, motivo in casos:
            with self.subTest(motivo=motivo), self.assertRaises(ValueError):
                emp.registrar_horas(proyecto, horas, "tarea")
        with self.assertRaises(ValueError):
            emp.registrar_horas(proyecto, 2, "   ")
        with self.assertRaises(ValueError):
            emp.registrar_horas(None, 2, "sin proyecto")
        self.assertEqual(emp.registros_tiempo, [])
        self.assertEqual(proyecto.registros_tiempo, [])

    def test_informe_generar_y_exportar(self):
        informe = Informe(1, "Reporte de Sostenibilidad", date(2026, 10, 11))
        with self.assertRaises(ValueError):
            informe.exportar("no_importa.txt")  # aún sin contenido

        informe.generar({"Total Empleados": 15, "Proyectos Activos": 3})
        self.assertIn("REPORTE DE SOSTENIBILIDAD", informe.contenido)
        self.assertIn("Total Empleados: 15", informe.contenido)

        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, "subcarpeta", "informe.txt")
            informe.exportar(ruta)
            with open(ruta, encoding="utf-8") as archivo:
                self.assertEqual(archivo.read(), informe.contenido)


if __name__ == "__main__":
    unittest.main()
