import unittest
from datetime import date

from src.dominio.empleado import Empleado
from src.dominio.proyecto import Proyecto


class EmpleadoTestCase(unittest.TestCase):
    def test_creacion_empleado_basica(self):
        empleado = Empleado(1, "Ana Pérez", "Desarrolladora", 1200000, "ana@ecotech.cl")

        self.assertEqual(empleado.id_empleado, 1)
        self.assertEqual(empleado.nombre, "Ana Pérez")
        self.assertEqual(empleado.cargo, "Desarrolladora")
        self.assertEqual(empleado.salario, 1200000)
        self.assertEqual(empleado.direccion, "")        # opcionales con valor por defecto
        self.assertIsNone(empleado.fecha_inicio_contrato)

    def test_creacion_empleado_con_datos_completos(self):
        empleado = Empleado(
            2,
            "Luis Gómez",
            "Analista",
            1100000,
            "luis@example.com",
            direccion="Calle 123",
            telefono="555-1234",
            fecha_inicio_contrato=date(2024, 1, 15),
        )

        self.assertEqual(empleado.direccion, "Calle 123")
        self.assertEqual(empleado.telefono, "555-1234")
        self.assertEqual(empleado.correo, "luis@example.com")
        self.assertEqual(empleado.fecha_inicio_contrato, date(2024, 1, 15))

    def test_correo_es_obligatorio(self):
        with self.assertRaises(ValueError):
            Empleado(1, "Ana", "Dev", 1, "")
        with self.assertRaises(TypeError):  # ni siquiera puede omitirse en la firma
            Empleado(1, "Ana", "Dev", 1)

    def test_asignacion_y_desasignacion_de_empleados(self):
        proyecto = Proyecto(1, "Migración", "Migración a la nube", date.today())
        empleado = Empleado(1, "Ana Pérez", "Desarrolladora", 1200000, "ana@ecotech.cl")

        proyecto.asignar_empleado(empleado)
        proyecto.asignar_empleado(empleado)  # repetido: se ignora
        self.assertEqual(len(proyecto.empleados_asignados), 1)
        proyecto.desasignar_empleado(empleado)
        self.assertEqual(len(proyecto.empleados_asignados), 0)


if __name__ == "__main__":
    unittest.main()
