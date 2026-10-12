import sys
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
    DepartamentoDAO,
    EmpleadoDAO,
    InformeDAO,
    ProyectoDAO,
    RegistroTiempoDAO,
    UsuarioDAO,
    crear_tablas,
)
from src.servicios import iniciar_interfaz_crud


def ejecutar_demostracion() -> None:
    """Modo demostracion automatica para validar inserciones y relaciones."""
    print("============================================================")
    print("         EJECUCION DEMOSTRATIVA AUTOMATICA ECOTECH")
    print("============================================================")
    crear_tablas()

    empleado_dao = EmpleadoDAO()
    departamento_dao = DepartamentoDAO()
    proyecto_dao = ProyectoDAO()
    registro_dao = RegistroTiempoDAO()
    informe_dao = InformeDAO()
    usuario_dao = UsuarioDAO()

    admin = Administrador(None, "Administrador Sistema", "admin@ecotech.cl", nivel_acceso="SENIOR")
    admin.establecer_contrasena("Admin2026*")
    usuario_dao.guardar(admin)

    empleado1 = Empleado(None, "Ana Perez", "Desarrolladora", 1200000.0, correo="ana@ecotech.cl")
    empleado2 = Empleado(None, "Luis Gomez", "Analista", 1100000.0, correo="luis@ecotech.cl")
    empleado_dao.guardar(empleado1)
    empleado_dao.guardar(empleado2)

    departamento = Departamento(None, "Tecnologia", "Carlos Ruiz")
    departamento_dao.guardar(departamento)
    departamento_dao.agregar_empleado(departamento.id_departamento, empleado1.id_empleado)
    departamento_dao.agregar_empleado(departamento.id_departamento, empleado2.id_empleado)

    proyecto = Proyecto(
        None,
        "Migracion a la nube",
        "Proyecto de modernizacion de infraestructura",
        date.today(),
    )
    proyecto_dao.guardar(proyecto)
    proyecto_dao.asignar_empleado(proyecto.id_proyecto, empleado1.id_empleado)
    proyecto_dao.asignar_empleado(proyecto.id_proyecto, empleado2.id_empleado)

    reg1 = empleado1.registrarHoras(proyecto, 4.0, "Configuracion de contenedores")
    registro_dao.guardar(reg1)

    informe = admin.generarInforme("Resumen Operativo")
    informe.generar({"Empleados": 2, "Proyectos": 1, "Horas": 4.0})
    informe_dao.guardar(informe)

    print("Demostracion completada con exito.")
    print(f"Empleados registrados: {len(empleado_dao.listar())}")
    print(f"Departamentos registrados: {len(departamento_dao.listar())}")
    print(f"Proyectos registrados: {len(proyecto_dao.listar())}")
    print(f"Horas totales en proyecto: {registro_dao.total_horas_proyecto(proyecto.id_proyecto):.1f}")


def main() -> None:
    if "--demo" in sys.argv or "-d" in sys.argv:
        ejecutar_demostracion()
    else:
        iniciar_interfaz_crud()


if __name__ == "__main__":
    main()
