"""Conformidad UML -> Python: clases, atributos (visibilidad), métodos y relaciones del diagrama."""
import inspect
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


def _empleado(id_empleado=None, nombre="Empleado Test", correo="emp@ecotech.cl"):
    return Empleado(id_empleado, nombre, "Dev", 1000000.0, correo)


def _publicos_propios(clase):
    """Métodos públicos definidos en la propia clase (sin heredados, sin properties)."""
    return {
        nombre
        for nombre, valor in vars(clase).items()
        if not nombre.startswith("_") and (inspect.isfunction(valor) or isinstance(valor, (staticmethod, classmethod)))
    }


class TestDominioUML(unittest.TestCase):
    def test_01_herencia(self):
        self.assertTrue(issubclass(Administrador, Usuario))
        self.assertTrue(issubclass(Empleado, Usuario))
        self.assertFalse(issubclass(Departamento, Usuario))

    def test_02_atributos_publicos_del_uml(self):
        """Atributos marcados con + en el UML existen y son accesibles."""
        self.assertTrue(hasattr(Usuario(1, "U", "u@ecotech.cl"), "id_usuario"))
        self.assertTrue(hasattr(Departamento(1, "D"), "id_departamento"))
        self.assertTrue(hasattr(Proyecto(1, "P", "d", date.today()), "id_proyecto"))
        self.assertTrue(hasattr(RegistroDeTiempo(1, date.today(), 1, "t"), "id_registro"))
        informe = Informe(1, "Tipo")
        for atributo in ("id_informe", "tipo", "fecha_generacion", "contenido"):
            self.assertTrue(hasattr(informe, atributo))

    def test_03_atributos_privados_estan_encapsulados_con_property(self):
        """Atributos marcados con - en el UML se exponen solo mediante @property (con validación)."""
        privados = [
            (Usuario, "nombre"), (Usuario, "correo"), (Usuario, "contrasena_hash"),
            (Administrador, "nivel_acceso"),
            (Departamento, "nombre"),
            (Empleado, "cargo"), (Empleado, "direccion"), (Empleado, "telefono"),
            (Empleado, "fecha_inicio_contrato"), (Empleado, "salario"),
            (Proyecto, "nombre"), (Proyecto, "descripcion"), (Proyecto, "fecha_inicio"),
            (RegistroDeTiempo, "fecha"), (RegistroDeTiempo, "horas"), (RegistroDeTiempo, "descripcion_tareas"),
            (Informe, "creado_por"),
        ]
        for clase, atributo in privados:
            with self.subTest(clase=clase.__name__, atributo=atributo):
                self.assertIsInstance(getattr(clase, atributo, None), property)

    def test_04_firmas_de_metodos_segun_uml(self):
        firmas = [
            (Usuario.autenticar, ["contrasena_plana"]),
            (Administrador.generar_informe, ["tipo"]),
            (Administrador.gestionar_departamento, ["departamento"]),
            (Empleado.registrar_horas, ["proyecto", "horas", "descripcion_tareas"]),
            (Departamento.agregar_empleado, ["empleado"]),
            (Departamento.eliminar_empleado, ["empleado"]),
            (Departamento.buscar_empleado, ["id_empleado"]),
            (Proyecto.asignar_empleado, ["empleado"]),
            (Proyecto.desasignar_empleado, ["empleado"]),
            (RegistroDeTiempo.calcular_horas_totales, ["registros"]),
            (Informe.generar, ["datos"]),
            (Informe.exportar, ["ruta"]),
        ]
        for metodo, esperados in firmas:
            with self.subTest(metodo=metodo.__qualname__):
                parametros = [p for p in inspect.signature(metodo).parameters if p != "self"]
                self.assertEqual(parametros[: len(esperados)], esperados)

    def test_05_no_sobran_atributos(self):
        """Los atributos de instancia son los del UML más las claves/colecciones de las relaciones."""
        esperados = {
            Usuario: ({"id_usuario", "nombre", "correo", "contrasena_hash"}, Usuario(1, "U", "u@ecotech.cl")),
            Administrador: (
                {"id_usuario", "nombre", "correo", "contrasena_hash", "nivel_acceso"},
                Administrador(1, "A", "a@ecotech.cl"),
            ),
            Empleado: (
                {"id_usuario", "nombre", "correo", "contrasena_hash", "cargo", "direccion", "telefono",
                 "fecha_inicio_contrato", "salario", "registros_tiempo"},  # registros_tiempo = relación "registra"
                _empleado(),
            ),
            Departamento: (
                {"id_departamento", "nombre", "gerente", "empleados"},  # relaciones "gerente" y "empleados"
                Departamento(1, "D"),
            ),
            Proyecto: (
                {"id_proyecto", "nombre", "descripcion", "fecha_inicio",
                 "empleados_asignados", "registros_tiempo"},  # relaciones "asignado a" y "corresponde a"
                Proyecto(1, "P", "d", date.today()),
            ),
            RegistroDeTiempo: (
                {"id_registro", "fecha", "horas", "descripcion_tareas",
                 "id_empleado", "id_proyecto"},  # claves foráneas de las relaciones
                RegistroDeTiempo(1, date.today(), 1, "t"),
            ),
            Informe: (
                {"id_informe", "tipo", "fecha_generacion", "contenido", "creado_por"},
                Informe(1, "T"),
            ),
        }
        for clase, (atributos, objeto) in esperados.items():
            with self.subTest(clase=clase.__name__):
                reales = {nombre.lstrip("_") for nombre in vars(objeto)}
                self.assertEqual(reales, atributos)

    def test_06_no_sobran_metodos(self):
        """Métodos públicos propios de cada clase = los del UML (Usuario suma los de manejo seguro de la contraseña)."""
        esperados = {
            Usuario: {"autenticar", "hashear_contrasena", "establecer_contrasena"},
            Administrador: {"generar_informe", "gestionar_departamento"},
            Empleado: {"registrar_horas"},
            Departamento: {"agregar_empleado", "eliminar_empleado", "buscar_empleado"},
            Proyecto: {"asignar_empleado", "desasignar_empleado"},
            RegistroDeTiempo: {"calcular_horas_totales"},
            Informe: {"generar", "exportar"},
        }
        for clase, metodos in esperados.items():
            with self.subTest(clase=clase.__name__):
                self.assertEqual(_publicos_propios(clase), metodos)

    def test_07_validaciones_de_datos(self):
        with self.assertRaises(ValueError):
            Usuario(1, "", "correo@ecotech.cl", "hash")
        with self.assertRaises(ValueError):
            Usuario(1, "   ", "correo@ecotech.cl")
        with self.assertRaises(ValueError):
            Usuario(1, "Nombre", "sin-arroba")
        with self.assertRaises(ValueError):
            Departamento(1, "")
        with self.assertRaises(ValueError):
            Proyecto(1, "P", "desc", "no-es-fecha")
        with self.assertRaises(ValueError):
            Informe(1, "  ")

    def test_08_usuario_correo_y_contrasena(self):
        u = Usuario(2, "Prueba", "  PRUEBA@Ecotech.cl ")
        self.assertEqual(u.correo, "prueba@ecotech.cl")  # se normaliza
        u.establecer_contrasena("Secreto123*")
        self.assertTrue(u.autenticar("Secreto123*"))
        self.assertFalse(u.autenticar("ClaveEquivocada1"))
        self.assertFalse(u.autenticar(""))
        self.assertNotIn("Secreto123", u.contrasena_hash)  # nunca se guarda en texto plano
        self.assertTrue(u.contrasena_hash.startswith("pbkdf2_sha256$"))

    def test_09_administrador_gestiona_departamento(self):
        admin = Administrador(3, "Admin", "admin@ecotech.cl")
        depto = Departamento(1, "Finanzas")
        admin.gestionar_departamento(depto, nuevo_nombre="Contabilidad")
        self.assertEqual(depto.nombre, "Contabilidad")
        with self.assertRaises(ValueError):
            admin.gestionar_departamento(depto, nuevo_nombre="")
        gerente = _empleado(7)
        admin.gestionar_departamento(depto, nuevo_gerente=gerente)
        self.assertIs(depto.gerente, gerente)
        with self.assertRaises(ValueError):
            depto.gerente = "Juan"  # el UML define al gerente como Empleado

    def test_10_registro_de_horas_e_informes(self):
        emp = _empleado(4)
        proj = Proyecto(1, "Proyecto Alpha", "Desc", date.today())
        registro = emp.registrar_horas(proj, 5.5, "Desarrollo de módulos")
        self.assertEqual(registro.horas, 5.5)
        self.assertEqual((registro.id_empleado, registro.id_proyecto), (4, 1))

        admin = Administrador(5, "Jefe", "jefe@ecotech.cl")
        informe = admin.generar_informe("Operativo")
        self.assertEqual(informe.tipo, "Operativo")
        self.assertEqual(informe.creado_por, 5)

    def test_11_relaciones_del_uml_en_el_codigo(self):
        """Asociaciones: se representan con referencias entre objetos."""
        emp = _empleado(1)
        proj = Proyecto(1, "P", "d", date.today())
        depto = Departamento(1, "D", gerente=emp)
        depto.agregar_empleado(emp)
        proj.asignar_empleado(emp)
        registro = emp.registrar_horas(proj, 2, "tarea")
        self.assertIs(depto.gerente, emp)                       # Departamento 1 ◇─ 0..1 Empleado (gerente)
        self.assertIn(emp, depto.empleados)                      # Departamento 1 ◇─ 0..* Empleado
        self.assertIn(emp, proj.empleados_asignados)             # Empleado 0..* ─ 0..* Proyecto
        self.assertIn(registro, emp.registros_tiempo)            # Empleado 1 ─ 0..* RegistroDeTiempo
        self.assertIn(registro, proj.registros_tiempo)           # Proyecto 1 ─ 0..* RegistroDeTiempo


if __name__ == "__main__":
    unittest.main()
