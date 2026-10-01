import unittest
from datetime import date

from src.dominio.empleado import Empleado
from src.dominio.proyecto import Proyecto


class EmpleadoTestCase(unittest.TestCase):
    def test_creacion_empleado_basica(self):
        empleado = Empleado(1, "Ana Pérez", "Desarrolladora", 1200000)

        self.assertEqual(empleado.id_empleado, 1)
        self.assertEqual(empleado.nombre, "Ana Pérez")
        self.assertEqual(empleado.cargo, "Desarrolladora")
        self.assertEqual(empleado.salario, 1200000)

    def test_creacion_empleado_con_datos_completos(self):
        empleado = Empleado(
            2,
            "Luis Gómez",
            "Analista",
            1100000,
            direccion="Calle 123",
            telefono="555-1234",
            correo="luis@example.com",
            fecha_inicio_contrato=date(2024, 1, 15),
        )

        self.assertEqual(empleado.direccion, "Calle 123")
        self.assertEqual(empleado.telefono, "555-1234")
        self.assertEqual(empleado.correo, "luis@example.com")
        self.assertEqual(empleado.fecha_inicio_contrato, date(2024, 1, 15))

    def test_asignacion_y_desasignacion_de_empleados(self):
        proyecto = Proyecto(1, "Migración", "Migración a la nube", date.today())
        empleado = Empleado(1, "Ana Pérez", "Desarrolladora", 1200000)

        self.assertTrue(proyecto.asignarEmpleado(empleado))
        self.assertEqual(len(proyecto.empleados_asignados), 1)
        self.assertTrue(proyecto.desasignarEmpleado(empleado))
        self.assertEqual(len(proyecto.empleados_asignados), 0)


if __name__ == "__main__":
    unittest.main()
