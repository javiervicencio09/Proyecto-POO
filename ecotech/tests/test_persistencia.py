import os
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
from src.persistencia import (
    DAOError,
    DepartamentoDAO,
    EmpleadoDAO,
    InformeDAO,
    ProyectoDAO,
    RegistroTiempoDAO,
    UsuarioDAO,
    crear_tablas,
)


class PersistenciaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Asegurar que las tablas existan antes de las pruebas
        crear_tablas()

    def setUp(self):
        self.usuario_dao = UsuarioDAO()
        self.empleado_dao = EmpleadoDAO()
        self.departamento_dao = DepartamentoDAO()
        self.proyecto_dao = ProyectoDAO()
        self.registro_dao = RegistroTiempoDAO()
        self.informe_dao = InformeDAO()

    def test_crud_usuario_y_autenticacion(self):
        email_test = f"user_test_{date.today().strftime('%Y%m%d%H%M%S')}@ecotech.cl"
        usuario = Usuario(None, "Usuario Prueba", email_test)
        usuario.establecer_contrasena("ClaveSegura123")

        id_u = self.usuario_dao.guardar(usuario)
        self.assertIsNotNone(id_u)

        # Autenticación exitosa
        auth_ok = self.usuario_dao.autenticar(email_test, "ClaveSegura123")
        self.assertIsNotNone(auth_ok)
        self.assertEqual(auth_ok.nombre, "Usuario Prueba")

        # Autenticación errónea
        auth_bad = self.usuario_dao.autenticar(email_test, "ClaveIncorrecta")
        self.assertIsNone(auth_bad)

        # Eliminar
        self.assertTrue(self.usuario_dao.eliminar(id_u))

    def test_crud_administrador(self):
        email_admin = f"admin_test_{date.today().strftime('%Y%m%d%H%M%S')}@ecotech.cl"
        admin = Administrador(None, "Admin TI", email_admin, nivel_acceso="SENIOR")
        admin.establecer_contrasena("AdminPass99")

        id_admin = self.usuario_dao.guardar(admin)
        self.assertIsNotNone(id_admin)

        recuperado = self.usuario_dao.buscar_por_id(id_admin)
        self.assertIsInstance(recuperado, Administrador)
        self.assertEqual(recuperado.nivel_acceso, "SENIOR")

        self.usuario_dao.eliminar(id_admin)

    def test_registro_tiempo_dao(self):
        empleado = Empleado(None, "Tester", "QA", 900000.0, correo="qa@ecotech.cl")
        id_emp = self.empleado_dao.guardar(empleado)

        proyecto = Proyecto(None, "Testing Proj", "Desc", date.today())
        id_proy = self.proyecto_dao.guardar(proyecto)

        reg = RegistroDeTiempo(None, date.today(), 5.0, "Pruebas de regresión", id_emp, id_proy)
        id_reg = self.registro_dao.guardar(reg)
        self.assertIsNotNone(id_reg)

        registros = self.registro_dao.listar_por_proyecto(id_proy)
        self.assertTrue(len(registros) >= 1)

        total_horas = self.registro_dao.total_horas_proyecto(id_proy)
        self.assertEqual(total_horas, 5.0)

        # Limpieza
        self.registro_dao.eliminar(id_reg)
        self.empleado_dao.eliminar(id_emp)
        self.proyecto_dao.eliminar(id_proy)

    def test_informe_dao(self):
        informe = Informe(None, "Auditoría", date.today(), "Informe sin observaciones.")
        id_inf = self.informe_dao.guardar(informe)
        self.assertIsNotNone(id_inf)

        recuperado = self.informe_dao.buscar_por_id(id_inf)
        self.assertIsNotNone(recuperado)
        self.assertEqual(recuperado.tipo, "Auditoría")

        self.assertTrue(self.informe_dao.eliminar(id_inf))


if __name__ == "__main__":
    unittest.main()
