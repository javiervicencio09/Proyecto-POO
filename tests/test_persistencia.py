"""
Pruebas de los DAO contra una base SQLite temporal (no toca ecotech.db ni el .env del equipo).
Cubre CRUD de cada entidad, relaciones, resultados normales (None / False) y errores controlados.
"""
import os
import tempfile
import unittest
import uuid
from datetime import date

from src.dominio import (
    Administrador,
    Departamento,
    Empleado,
    Proyecto,
    RegistroDeTiempo,
    Usuario,
)
from src.persistencia import (
    DAOError,
    DAOIntegridadError,
    DepartamentoDAO,
    EmpleadoDAO,
    InformeDAO,
    ProyectoDAO,
    RegistroTiempoDAO,
    UsuarioDAO,
    crear_tablas,
)


def correo_unico(prefijo: str = "t") -> str:
    return f"{prefijo}_{uuid.uuid4().hex[:10]}@ecotech.cl"


class PersistenciaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._carpeta = tempfile.TemporaryDirectory()
        cls._env_previo = {k: os.environ.get(k) for k in ("DB_ENGINE", "DB_NAME")}
        os.environ["DB_ENGINE"] = "sqlite"
        os.environ["DB_NAME"] = os.path.join(cls._carpeta.name, "prueba.db")  # ruta absoluta
        crear_tablas()

    @classmethod
    def tearDownClass(cls):
        for clave, valor in cls._env_previo.items():
            if valor is None:
                os.environ.pop(clave, None)
            else:
                os.environ[clave] = valor
        cls._carpeta.cleanup()

    # ---- helpers -------------------------------------------------------------------------
    def _empleado(self, nombre="Tester", cargo="QA"):
        return EmpleadoDAO.insertar(Empleado(None, nombre, cargo, 900000.0, correo_unico("emp")))

    def _proyecto(self, nombre="Proyecto de prueba"):
        return ProyectoDAO.insertar(Proyecto(None, nombre, "Descripción", date.today()))

    # ---- Usuario / Administrador ----------------------------------------------------------
    def test_crud_usuario_y_autenticacion(self):
        correo = correo_unico("user")
        usuario = Usuario(None, "Usuario Prueba", correo)
        usuario.establecer_contrasena("ClaveSegura123")

        UsuarioDAO.insertar(usuario)
        self.assertIsNotNone(usuario.id_usuario)

        self.assertEqual(UsuarioDAO.autenticar(correo, "ClaveSegura123").nombre, "Usuario Prueba")
        self.assertIsNone(UsuarioDAO.autenticar(correo, "ClaveIncorrecta1"))
        self.assertIsNone(UsuarioDAO.autenticar("no.existe@ecotech.cl", "ClaveSegura123"))

        usuario.nombre = "Nombre Nuevo"
        self.assertTrue(UsuarioDAO.actualizar(usuario))
        self.assertEqual(UsuarioDAO.buscar_por_id(usuario.id_usuario).nombre, "Nombre Nuevo")

        self.assertTrue(UsuarioDAO.eliminar(usuario.id_usuario))
        self.assertFalse(UsuarioDAO.eliminar(usuario.id_usuario))   # ya no existe: resultado normal
        self.assertIsNone(UsuarioDAO.buscar_por_id(usuario.id_usuario))

    def test_crud_administrador_conserva_su_tipo(self):
        admin = Administrador(None, "Admin TI", correo_unico("admin"), nivel_acceso="senior")
        admin.establecer_contrasena("AdminPass99")
        UsuarioDAO.insertar(admin)

        recuperado = UsuarioDAO.buscar_por_id(admin.id_usuario)
        self.assertIsInstance(recuperado, Administrador)
        self.assertEqual(recuperado.nivel_acceso, "SENIOR")
        self.assertTrue(recuperado.autenticar("AdminPass99"))

        admin.nivel_acceso = "total"
        self.assertTrue(UsuarioDAO.actualizar(admin))
        self.assertEqual(UsuarioDAO.buscar_por_id(admin.id_usuario).nivel_acceso, "TOTAL")
        UsuarioDAO.eliminar(admin.id_usuario)

    def test_usuariodao_no_guarda_empleados(self):
        with self.assertRaises(DAOError):
            UsuarioDAO.insertar(Empleado(None, "E", "Dev", 1, correo_unico()))

    # ---- Empleado -------------------------------------------------------------------------
    def test_crud_empleado(self):
        correo = correo_unico("ana")
        empleado = Empleado(None, "Ana Torres", "Dev", 1200000.0, correo, "Calle 1", "555-1234", date(2026, 3, 15))
        EmpleadoDAO.insertar(empleado)
        self.assertIsNotNone(empleado.id_empleado)               # insertar() deja el id generado

        leido = EmpleadoDAO.buscar_por_id(empleado.id_empleado)
        self.assertEqual((leido.nombre, leido.cargo, leido.salario), ("Ana Torres", "Dev", 1200000.0))
        self.assertEqual(leido.fecha_inicio_contrato, date(2026, 3, 15))
        self.assertEqual(EmpleadoDAO.buscar_por_correo(correo.upper()).id_empleado, empleado.id_empleado)
        self.assertIn(empleado, EmpleadoDAO.listar())            # listar() retorna objetos Empleado
        self.assertIsInstance(EmpleadoDAO.listar()[0], Empleado)

        empleado.cargo = "Líder Técnica"
        empleado.salario = 1500000
        self.assertTrue(EmpleadoDAO.actualizar(empleado))
        self.assertEqual(EmpleadoDAO.buscar_por_id(empleado.id_empleado).cargo, "Líder Técnica")

        self.assertTrue(EmpleadoDAO.eliminar(empleado.id_empleado))
        self.assertIsNone(EmpleadoDAO.buscar_por_id(empleado.id_empleado))
        self.assertFalse(EmpleadoDAO.eliminar(empleado.id_empleado))

    def test_empleado_inexistente_es_resultado_normal(self):
        self.assertIsNone(EmpleadoDAO.buscar_por_id(999999))
        self.assertIsNone(EmpleadoDAO.buscar_por_correo("nadie@ecotech.cl"))
        fantasma = Empleado(999999, "Fantasma", "Dev", 1, correo_unico())
        self.assertFalse(EmpleadoDAO.actualizar(fantasma))

    def test_correo_duplicado_es_error_controlado_y_hace_rollback(self):
        base = self._empleado()
        repetido = Empleado(None, "Otro", "Dev", 1, base.correo)
        with self.assertRaises(DAOIntegridadError):
            EmpleadoDAO.insertar(repetido)
        self.assertIsNone(repetido.id_empleado)                  # el id se asigna solo tras el COMMIT

    def test_no_se_inserta_dos_veces_el_mismo_objeto(self):
        empleado = self._empleado()
        with self.assertRaises(DAOError):
            EmpleadoDAO.insertar(empleado)
        sin_guardar = Empleado(None, "Sin guardar", "Dev", 1, correo_unico())
        with self.assertRaises(DAOError):
            EmpleadoDAO.actualizar(sin_guardar)

    def test_consultas_parametrizadas_resisten_inyeccion_sql(self):
        self._empleado()
        self.assertIsNone(EmpleadoDAO.buscar_por_correo("' OR '1'='1"))
        self.assertIsNone(EmpleadoDAO.buscar_por_correo("x'; DROP TABLE usuario; --"))
        self.assertGreaterEqual(len(EmpleadoDAO.listar()), 1)    # las tablas siguen ahí

    # ---- Departamento ----------------------------------------------------------------------
    def test_departamento_con_gerente_y_empleados(self):
        gerente, otro = self._empleado("Gerente"), self._empleado("Otro")
        depto = DepartamentoDAO.insertar(Departamento(None, "Tecnología", gerente))
        self.assertIsNotNone(depto.id_departamento)

        self.assertTrue(DepartamentoDAO.agregar_empleado(depto.id_departamento, gerente.id_empleado))
        self.assertTrue(DepartamentoDAO.agregar_empleado(depto.id_departamento, otro.id_empleado))
        self.assertFalse(DepartamentoDAO.agregar_empleado(depto.id_departamento, 999999))

        leido = DepartamentoDAO.buscar_por_id(depto.id_departamento)
        self.assertEqual(leido.gerente, gerente)
        self.assertEqual(len(leido.empleados), 2)

        self.assertTrue(DepartamentoDAO.eliminar_empleado(depto.id_departamento, otro.id_empleado))
        self.assertFalse(DepartamentoDAO.eliminar_empleado(depto.id_departamento, otro.id_empleado))

        depto.nombre = "Tecnología e Innovación"
        depto.gerente = None
        self.assertTrue(DepartamentoDAO.actualizar(depto))
        leido = DepartamentoDAO.buscar_por_id(depto.id_departamento)
        self.assertEqual(leido.nombre, "Tecnología e Innovación")
        self.assertIsNone(leido.gerente)

        self.assertTrue(DepartamentoDAO.eliminar(depto.id_departamento))
        self.assertIsNone(DepartamentoDAO.buscar_por_id(depto.id_departamento))
        self.assertIsNotNone(EmpleadoDAO.buscar_por_id(gerente.id_empleado))  # sus empleados no se borran

    def test_gerente_no_guardado_es_rechazado(self):
        sin_guardar = Empleado(None, "Nuevo", "Dev", 1, correo_unico())
        with self.assertRaises(DAOError):
            DepartamentoDAO.insertar(Departamento(None, "Depto", sin_guardar))

    def test_empleado_en_departamento_inexistente_viola_clave_foranea(self):
        empleado = self._empleado()
        with self.assertRaises(DAOIntegridadError):
            DepartamentoDAO.agregar_empleado(999999, empleado.id_empleado)

    # ---- Proyecto y asignaciones ------------------------------------------------------------
    def test_crud_proyecto_y_asignaciones(self):
        proyecto = self._proyecto("Migración")
        empleado = self._empleado()

        self.assertTrue(ProyectoDAO.asignar_empleado(proyecto.id_proyecto, empleado.id_empleado))
        self.assertFalse(ProyectoDAO.asignar_empleado(proyecto.id_proyecto, empleado.id_empleado))  # ya asignado
        self.assertEqual(len(ProyectoDAO.buscar_por_id(proyecto.id_proyecto).empleados_asignados), 1)
        with self.assertRaises(DAOIntegridadError):
            ProyectoDAO.asignar_empleado(proyecto.id_proyecto, 999999)

        proyecto.nombre = "Migración a la nube"
        self.assertTrue(ProyectoDAO.actualizar(proyecto))
        self.assertEqual(ProyectoDAO.buscar_por_id(proyecto.id_proyecto).nombre, "Migración a la nube")
        self.assertIn(proyecto.id_proyecto, [p.id_proyecto for p in ProyectoDAO.listar()])

        self.assertTrue(ProyectoDAO.desasignar_empleado(proyecto.id_proyecto, empleado.id_empleado))
        self.assertFalse(ProyectoDAO.desasignar_empleado(proyecto.id_proyecto, empleado.id_empleado))
        self.assertTrue(ProyectoDAO.eliminar(proyecto.id_proyecto))
        self.assertIsNone(ProyectoDAO.buscar_por_id(proyecto.id_proyecto))

    # ---- RegistroDeTiempo ------------------------------------------------------------------
    def test_registro_tiempo_dao(self):
        empleado, proyecto = self._empleado(), self._proyecto()
        registro = empleado.registrar_horas(proyecto, 5.0, "Pruebas de regresión")
        RegistroTiempoDAO.insertar(registro)
        self.assertIsNotNone(registro.id_registro)

        self.assertEqual(len(RegistroTiempoDAO.listar_por_proyecto(proyecto.id_proyecto)), 1)
        self.assertEqual(len(RegistroTiempoDAO.listar_por_empleado(empleado.id_empleado)), 1)
        self.assertEqual(RegistroTiempoDAO.total_horas_proyecto(proyecto.id_proyecto), 5.0)

        registro.horas = 6.5
        self.assertTrue(RegistroTiempoDAO.actualizar(registro))
        self.assertEqual(RegistroTiempoDAO.buscar_por_id(registro.id_registro).horas, 6.5)

        self.assertTrue(RegistroTiempoDAO.eliminar(registro.id_registro))
        self.assertFalse(RegistroTiempoDAO.eliminar(registro.id_registro))

    def test_registro_con_empleado_inexistente_es_rechazado(self):
        proyecto = self._proyecto()
        huerfano = RegistroDeTiempo(None, date.today(), 2, "tarea", 999999, proyecto.id_proyecto)
        with self.assertRaises(DAOIntegridadError):
            RegistroTiempoDAO.insertar(huerfano)

    def test_eliminar_empleado_elimina_en_cascada_sus_registros(self):
        empleado, proyecto = self._empleado(), self._proyecto()
        registro = RegistroTiempoDAO.insertar(empleado.registrar_horas(proyecto, 3, "tarea"))
        EmpleadoDAO.eliminar(empleado.id_empleado)
        self.assertIsNone(RegistroTiempoDAO.buscar_por_id(registro.id_registro))

    # ---- Informe ---------------------------------------------------------------------------
    def test_informe_dao(self):
        admin = Administrador(None, "Admin", correo_unico("adm"))
        UsuarioDAO.insertar(admin)
        informe = admin.generar_informe("Auditoría")
        informe.generar({"Empleados": 3})
        InformeDAO.insertar(informe)
        self.assertIsNotNone(informe.id_informe)

        leido = InformeDAO.buscar_por_id(informe.id_informe)
        self.assertEqual((leido.tipo, leido.creado_por), ("Auditoría", admin.id_usuario))
        self.assertIn("Empleados: 3", leido.contenido)

        informe.contenido = "Contenido corregido"
        self.assertTrue(InformeDAO.actualizar(informe))
        self.assertEqual(InformeDAO.buscar_por_id(informe.id_informe).contenido, "Contenido corregido")

        self.assertTrue(InformeDAO.eliminar(informe.id_informe))
        self.assertIsNone(InformeDAO.buscar_por_id(informe.id_informe))


if __name__ == "__main__":
    unittest.main()
