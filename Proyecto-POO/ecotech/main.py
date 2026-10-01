from datetime import date

from src.dominio import Departamento, Empleado, Proyecto
from src.persistencia import DepartamentoDAO, EmpleadoDAO, ProyectoDAO
from src.persistencia.crear_bd import crear_tablas


def main() -> None:
    crear_tablas()

    empleado_dao = EmpleadoDAO()
    departamento_dao = DepartamentoDAO()
    proyecto_dao = ProyectoDAO()

    empleado1 = Empleado(None, "Ana Pérez", "Desarrolladora", 1200000)
    empleado2 = Empleado(None, "Luis Gómez", "Analista", 1100000)
    empleado_dao.guardar(empleado1)
    empleado_dao.guardar(empleado2)

    departamento = Departamento(None, "Tecnología", "Carlos Ruiz")
    departamento_dao.guardar(departamento)
    departamento.agregar_empleado(empleado1)
    departamento.agregar_empleado(empleado2)
    departamento_dao.agregar_empleado(departamento.id_departamento, empleado1.id_empleado)
    departamento_dao.agregar_empleado(departamento.id_departamento, empleado2.id_empleado)

    proyecto = Proyecto(
        None,
        "Migración a la nube",
        "Proyecto de modernización de infraestructura",
        date.today(),
    )
    proyecto_dao.guardar(proyecto)
    proyecto.asignar_empleado(empleado1)
    proyecto.asignar_empleado(empleado2)
    proyecto_dao.asignar_empleado(proyecto.id_proyecto, empleado1.id_empleado)
    proyecto_dao.asignar_empleado(proyecto.id_proyecto, empleado2.id_empleado)

    print("Empleados guardados:")
    for empleado in empleado_dao.listar():
        print(f"  {empleado}")

    print("Departamentos guardados:")
    for departamento_guardado in departamento_dao.listar():
        print(f"  {departamento_guardado}")

    print("Proyectos guardados:")
    for proyecto_guardado in proyecto_dao.listar():
        print(f"  {proyecto_guardado}")

    print("Relaciones asignadas:")
    print(f"  {departamento} ")
    print(f"  {proyecto}")


if __name__ == "__main__":
    main()
