"""
Punto de entrada de EcoTech Solutions.

main.py solo coordina: muestra menús, pide y valida datos, crea objetos del dominio y llama a los DAO.
No contiene SQL ni credenciales (el SQL vive en persistencia/ y la configuración en .env).

Ejecutar desde la raíz del proyecto:
    python -m src.main           menú interactivo
    python -m src.main --demo    demostración automática (CRUD completo + error controlado)
"""
import getpass
import logging
import re
import sys
from datetime import date, datetime
from pathlib import Path

if __package__ in (None, ""):  # permite también "python src/main.py"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dominio import Administrador, Departamento, Empleado, Proyecto, RegistroDeTiempo
from src.dominio.validaciones import (
    validar_contrasena,
    validar_correo,
    validar_fecha,
    validar_numero,
    validar_telefono,
    validar_texto,
    validar_texto_opcional,
)
from src.persistencia import (
    ConexionError,
    DAOError,
    DepartamentoDAO,
    EmpleadoDAO,
    InformeDAO,
    ProyectoDAO,
    RegistroTiempoDAO,
    UsuarioDAO,
    crear_tablas,
)
from src.persistencia.conexion import RAIZ_PROYECTO


# ---------------------------------------------------------------------------
# Entrada de datos: VALIDAR antes de crear objetos (errores esperables).
# Las reglas son las mismas del dominio (src/dominio/validaciones.py), así no se duplican.
# ---------------------------------------------------------------------------
def pedir_con_validacion(mensaje: str, validador, secreto: bool = False):
    """Repite la pregunta hasta que el validador acepte el dato; muestra el motivo si lo rechaza."""
    while True:
        texto = getpass.getpass(mensaje) if secreto else input(mensaje)
        try:
            return validador(texto)
        except ValueError as err:
            print(f"  -> {err}")


def pedir_texto(mensaje: str, campo: str, largo: int = 255, opcional: bool = False) -> str:
    validar = validar_texto_opcional if opcional else validar_texto
    return pedir_con_validacion(mensaje, lambda t: validar(t, campo, largo))


def entero_positivo(texto: str) -> int:
    """Validación previa a int(): solo dígitos ASCII (isdigit() acepta símbolos como '²' que int() rechaza)."""
    texto = texto.strip()
    if not (texto.isascii() and texto.isdigit()) or int(texto) == 0:
        raise ValueError("Debe ingresar un número entero positivo.")
    return int(texto)


def pedir_entero(mensaje: str) -> int:
    return pedir_con_validacion(mensaje, entero_positivo)


def pedir_numero(mensaje: str, campo: str, **limites) -> float:
    return pedir_con_validacion(mensaje, lambda t: validar_numero(t.strip().replace(",", "."), campo, **limites))


def pedir_fecha(mensaje: str, campo: str, opcional: bool = False):
    def validar(texto: str):
        texto = texto.strip()
        if texto == "" and opcional:
            return None
        try:
            return validar_fecha(date.fromisoformat(texto), campo)
        except ValueError:
            raise ValueError("Use el formato AAAA-MM-DD (ejemplo: 2026-03-15).") from None

    return pedir_con_validacion(mensaje, validar)


def pedir_correo(mensaje: str = "Correo: ") -> str:
    return pedir_con_validacion(mensaje, validar_correo)


def pedir_contrasena(mensaje: str = "Contraseña (mín. 8 caracteres, letras y números): ") -> str:
    return pedir_con_validacion(mensaje, validar_contrasena, secreto=True)


# ---------------------------------------------------------------------------
# Manejo de errores: EXCEPCIONES (errores inesperados), con mensajes seguros para el usuario.
# ---------------------------------------------------------------------------
def ejecutar(accion) -> None:
    """Ejecuta una opción de menú sin que un error la interrumpa. El detalle técnico va al log."""
    try:
        accion()
    except ValueError as err:  # regla del dominio incumplida
        print(f"Dato inválido: {err}")
    except (DAOError, ConexionError) as err:  # fallo de persistencia / conexión (mensaje ya es seguro)
        print(f"No se pudo completar la operación: {err}")
    except OSError:  # exportar informe: ruta o permisos
        print("No se pudo escribir el archivo. Revise el nombre y los permisos.")
    except (KeyboardInterrupt, EOFError):  # Ctrl+C / Ctrl+D (Ctrl+Z en Windows): cancelar, no es un fallo
        print("\nOperación cancelada.")
    except Exception:
        logging.getLogger(__name__).exception("Error inesperado")
        print("Ocurrió un error inesperado. Revise ecotech.log.")


def mostrar_lista(titulo: str, elementos) -> None:
    print(f"\n--- {titulo} ---")
    if not elementos:
        print("(sin registros)")
    for elemento in elementos:
        print(elemento)


def informar(resultado: bool, ok: str, no: str) -> None:
    print(ok if resultado else no)


# ---------------------------------------------------------------------------
# Empleados
# ---------------------------------------------------------------------------
def registrar_empleado() -> None:
    empleado = Empleado(
        None,
        pedir_texto("Nombre: ", "El nombre", 100),
        pedir_texto("Cargo: ", "El cargo", 100),
        pedir_numero("Salario: ", "El salario", minimo=0),
        pedir_correo(),
        pedir_texto("Dirección (opcional): ", "La dirección", 255, opcional=True),
        pedir_con_validacion("Teléfono (opcional): ", validar_telefono),
        pedir_fecha("Inicio de contrato AAAA-MM-DD (opcional): ", "La fecha de contrato", opcional=True),
    )
    EmpleadoDAO.insertar(empleado)
    print(f"Empleado registrado con id {empleado.id_empleado}.")


def buscar_empleado() -> None:
    empleado = EmpleadoDAO.buscar_por_id(pedir_entero("Id del empleado: "))
    print(empleado if empleado else "Empleado no encontrado.")


def buscar_empleado_por_correo() -> None:
    empleado = EmpleadoDAO.buscar_por_correo(pedir_correo())
    print(empleado if empleado else "Empleado no encontrado.")


def actualizar_empleado() -> None:
    empleado = EmpleadoDAO.buscar_por_id(pedir_entero("Id del empleado: "))
    if empleado is None:
        print("Empleado no encontrado.")
        return
    print(f"Actual: {empleado}")
    cargo = pedir_texto("Nuevo cargo (Enter para mantener): ", "El cargo", 100, opcional=True)
    salario = pedir_con_validacion(
        "Nuevo salario (Enter para mantener): ",
        lambda t: None if not t.strip() else validar_numero(t.strip().replace(",", "."), "El salario", minimo=0),
    )
    if cargo:
        empleado.cargo = cargo
    if salario is not None:
        empleado.salario = salario
    informar(EmpleadoDAO.actualizar(empleado), "Empleado actualizado.", "Empleado no encontrado.")


def eliminar_empleado() -> None:
    informar(EmpleadoDAO.eliminar(pedir_entero("Id del empleado: ")), "Empleado eliminado.", "Empleado no encontrado.")


# ---------------------------------------------------------------------------
# Departamentos
# ---------------------------------------------------------------------------
def _pedir_gerente():
    """Pide el id de un gerente. None = sin gerente. Retorna (ok, gerente)."""
    id_texto = pedir_con_validacion(
        "Id del gerente (Enter si no tiene): ",
        lambda t: None if not t.strip() else entero_positivo(t),
    )
    if id_texto is None:
        return True, None
    gerente = EmpleadoDAO.buscar_por_id(id_texto)
    if gerente is None:
        print("No existe un empleado con ese id.")
        return False, None
    return True, gerente


def crear_departamento() -> None:
    nombre = pedir_texto("Nombre del departamento: ", "El nombre del departamento", 100)
    ok, gerente = _pedir_gerente()
    if not ok:
        print("El departamento no fue creado.")
        return
    departamento = Departamento(None, nombre, gerente)
    DepartamentoDAO.insertar(departamento)
    print(f"Departamento creado con id {departamento.id_departamento}.")


def actualizar_departamento() -> None:
    departamento = DepartamentoDAO.buscar_por_id(pedir_entero("Id del departamento: "))
    if departamento is None:
        print("Departamento no encontrado.")
        return
    print(f"Actual: {departamento}")
    nombre = pedir_texto("Nuevo nombre (Enter para mantener): ", "El nombre del departamento", 100, opcional=True)
    if nombre:
        departamento.nombre = nombre
    print("Nuevo gerente: ", end="")
    ok, gerente = _pedir_gerente()
    if not ok:
        print("No se realizaron cambios.")
        return
    if gerente is not None:
        departamento.gerente = gerente
    informar(DepartamentoDAO.actualizar(departamento), "Departamento actualizado.", "Departamento no encontrado.")


def agregar_a_departamento() -> None:
    ok = DepartamentoDAO.agregar_empleado(pedir_entero("Id del departamento: "), pedir_entero("Id del empleado: "))
    informar(ok, "Empleado asignado al departamento.", "Empleado no encontrado.")


def quitar_de_departamento() -> None:
    ok = DepartamentoDAO.eliminar_empleado(pedir_entero("Id del departamento: "), pedir_entero("Id del empleado: "))
    informar(ok, "Empleado quitado del departamento.", "Ese empleado no pertenece al departamento.")


def eliminar_departamento() -> None:
    ok = DepartamentoDAO.eliminar(pedir_entero("Id del departamento: "))
    informar(ok, "Departamento eliminado.", "Departamento no encontrado.")


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------
def crear_proyecto() -> None:
    proyecto = Proyecto(
        None,
        pedir_texto("Nombre: ", "El nombre del proyecto", 150),
        pedir_texto("Descripción: ", "La descripción del proyecto", 500),
        pedir_fecha("Fecha de inicio AAAA-MM-DD: ", "La fecha de inicio"),
    )
    ProyectoDAO.insertar(proyecto)
    print(f"Proyecto creado con id {proyecto.id_proyecto}.")


def actualizar_proyecto() -> None:
    proyecto = ProyectoDAO.buscar_por_id(pedir_entero("Id del proyecto: "))
    if proyecto is None:
        print("Proyecto no encontrado.")
        return
    print(f"Actual: {proyecto}")
    nombre = pedir_texto("Nuevo nombre (Enter para mantener): ", "El nombre del proyecto", 150, opcional=True)
    descripcion = pedir_texto("Nueva descripción (Enter para mantener): ", "La descripción", 500, opcional=True)
    if nombre:
        proyecto.nombre = nombre
    if descripcion:
        proyecto.descripcion = descripcion
    informar(ProyectoDAO.actualizar(proyecto), "Proyecto actualizado.", "Proyecto no encontrado.")


def asignar_a_proyecto() -> None:
    ok = ProyectoDAO.asignar_empleado(pedir_entero("Id del proyecto: "), pedir_entero("Id del empleado: "))
    informar(ok, "Empleado asignado al proyecto.", "Ese empleado ya estaba asignado al proyecto.")


def desasignar_de_proyecto() -> None:
    ok = ProyectoDAO.desasignar_empleado(pedir_entero("Id del proyecto: "), pedir_entero("Id del empleado: "))
    informar(ok, "Empleado desasignado.", "Ese empleado no estaba asignado al proyecto.")


def eliminar_proyecto() -> None:
    informar(ProyectoDAO.eliminar(pedir_entero("Id del proyecto: ")), "Proyecto eliminado.", "Proyecto no encontrado.")


# ---------------------------------------------------------------------------
# Registro de horas
# ---------------------------------------------------------------------------
def registrar_horas() -> None:
    empleado = EmpleadoDAO.buscar_por_id(pedir_entero("Id del empleado: "))
    proyecto = ProyectoDAO.buscar_por_id(pedir_entero("Id del proyecto: "))
    if empleado is None or proyecto is None:
        print("Empleado o proyecto no encontrado.")
        return
    horas = pedir_numero("Horas trabajadas: ", "Las horas", minimo=0, maximo=24, minimo_exclusivo=True)
    tareas = pedir_texto("Tareas realizadas: ", "La descripción de tareas", 500)
    registro = empleado.registrar_horas(proyecto, horas, tareas)
    RegistroTiempoDAO.insertar(registro)
    print(f"Registro guardado con id {registro.id_registro}.")


def horas_de_proyecto() -> None:
    registros = RegistroTiempoDAO.listar_por_proyecto(pedir_entero("Id del proyecto: "))
    mostrar_lista("Registros", registros)
    print(f"Horas totales: {RegistroDeTiempo.calcular_horas_totales(registros):.1f}")


def actualizar_registro() -> None:
    registro = RegistroTiempoDAO.buscar_por_id(pedir_entero("Id del registro: "))
    if registro is None:
        print("Registro no encontrado.")
        return
    print(f"Actual: {registro}")
    registro.horas = pedir_numero("Nuevas horas: ", "Las horas", minimo=0, maximo=24, minimo_exclusivo=True)
    registro.descripcion_tareas = pedir_texto("Nueva descripción de tareas: ", "La descripción de tareas", 500)
    informar(RegistroTiempoDAO.actualizar(registro), "Registro actualizado.", "Registro no encontrado.")


def eliminar_registro() -> None:
    ok = RegistroTiempoDAO.eliminar(pedir_entero("Id del registro: "))
    informar(ok, "Registro eliminado.", "Registro no encontrado.")


# ---------------------------------------------------------------------------
# Usuarios e informes
# ---------------------------------------------------------------------------
def crear_administrador() -> None:
    admin = Administrador(
        None,
        pedir_texto("Nombre: ", "El nombre", 100),
        pedir_correo(),
        nivel_acceso=pedir_texto("Nivel de acceso: ", "El nivel de acceso", 50),
    )
    admin.establecer_contrasena(pedir_contrasena())
    UsuarioDAO.insertar(admin)
    print(f"Administrador creado con id {admin.id_usuario}.")


def iniciar_sesion() -> None:
    usuario = UsuarioDAO.autenticar(pedir_correo(), getpass.getpass("Contraseña: "))
    print(f"Bienvenido/a {usuario.nombre}." if usuario else "Credenciales incorrectas.")


def _ruta_exportacion(nombre: str) -> Path:
    """Los informes se guardan siempre en la carpeta 'reportes' (se descarta cualquier ruta que escriba el usuario)."""
    limpio = re.sub(r"[^\w.\-]", "_", Path(nombre).name)
    if not limpio.strip("."):
        raise ValueError("Nombre de archivo no válido.")
    if not Path(limpio).suffix:
        limpio += ".txt"
    return RAIZ_PROYECTO / "reportes" / limpio


def generar_informe() -> None:
    admin = UsuarioDAO.buscar_por_id(pedir_entero("Id del administrador: "))
    if not isinstance(admin, Administrador):
        print("Ese id no corresponde a un administrador.")
        return
    informe = admin.generar_informe(pedir_texto("Tipo de informe: ", "El tipo de informe", 100))
    informe.generar(
        {
            "Empleados": len(EmpleadoDAO.listar()),
            "Departamentos": len(DepartamentoDAO.listar()),
            "Proyectos": len(ProyectoDAO.listar()),
            "Registros de tiempo": len(RegistroTiempoDAO.listar()),
        }
    )
    InformeDAO.insertar(informe)
    print(informe.contenido)
    nombre = pedir_texto("Nombre de archivo para exportar (Enter para no exportar): ", "El nombre de archivo", 80, opcional=True)
    if nombre:
        ruta = _ruta_exportacion(nombre)
        informe.exportar(str(ruta))
        print(f"Informe exportado en {ruta}.")


def eliminar_informe() -> None:
    informar(InformeDAO.eliminar(pedir_entero("Id del informe: ")), "Informe eliminado.", "Informe no encontrado.")


# ---------------------------------------------------------------------------
# Menús
# ---------------------------------------------------------------------------
def submenu(titulo: str, opciones: dict) -> None:
    while True:
        print(f"\n=== {titulo} ===")
        for clave, (texto, _) in opciones.items():
            print(f"{clave}. {texto}")
        print("0. Volver")
        eleccion = input("Seleccione una opción: ").strip()
        if eleccion == "0":
            return
        if eleccion in opciones:
            ejecutar(opciones[eleccion][1])
        else:
            print("Opción no válida.")


MENUS = {
    "1": ("Empleados", {
        "1": ("Registrar", registrar_empleado),
        "2": ("Listar", lambda: mostrar_lista("Empleados", EmpleadoDAO.listar())),
        "3": ("Buscar por id", buscar_empleado),
        "4": ("Buscar por correo", buscar_empleado_por_correo),
        "5": ("Actualizar", actualizar_empleado),
        "6": ("Eliminar", eliminar_empleado),
    }),
    "2": ("Departamentos", {
        "1": ("Crear", crear_departamento),
        "2": ("Listar", lambda: mostrar_lista("Departamentos", DepartamentoDAO.listar())),
        "3": ("Actualizar", actualizar_departamento),
        "4": ("Agregar empleado", agregar_a_departamento),
        "5": ("Quitar empleado", quitar_de_departamento),
        "6": ("Eliminar", eliminar_departamento),
    }),
    "3": ("Proyectos", {
        "1": ("Crear", crear_proyecto),
        "2": ("Listar", lambda: mostrar_lista("Proyectos", ProyectoDAO.listar())),
        "3": ("Actualizar", actualizar_proyecto),
        "4": ("Asignar empleado", asignar_a_proyecto),
        "5": ("Desasignar empleado", desasignar_de_proyecto),
        "6": ("Eliminar", eliminar_proyecto),
    }),
    "4": ("Registro de horas", {
        "1": ("Registrar horas", registrar_horas),
        "2": ("Ver horas de un proyecto", horas_de_proyecto),
        "3": ("Actualizar un registro", actualizar_registro),
        "4": ("Eliminar un registro", eliminar_registro),
    }),
    "5": ("Usuarios e informes", {
        "1": ("Crear administrador", crear_administrador),
        "2": ("Iniciar sesión", iniciar_sesion),
        "3": ("Generar informe", generar_informe),
        "4": ("Listar informes", lambda: mostrar_lista("Informes", InformeDAO.listar())),
        "5": ("Eliminar informe", eliminar_informe),
    }),
}


def menu_principal() -> None:
    while True:
        print("\n===== ECOTECH SOLUTIONS =====")
        for clave, (titulo, _) in MENUS.items():
            print(f"{clave}. {titulo}")
        print("0. Salir")
        eleccion = input("Seleccione una opción: ").strip()
        if eleccion == "0":
            print("Hasta luego.")
            return
        if eleccion in MENUS:
            submenu(*MENUS[eleccion])
        else:
            print("Opción no válida.")


# ---------------------------------------------------------------------------
# Demostración automática: CREATE, READ, UPDATE, DELETE y un error controlado
# ---------------------------------------------------------------------------
def ejecutar_demostracion() -> None:
    print("=== DEMOSTRACIÓN AUTOMÁTICA ECOTECH ===")
    sufijo = datetime.now().strftime("%d%H%M%S")  # correos únicos: la demo se puede repetir

    print("\n[CREATE] Registrando administrador, empleados, departamento, proyecto y horas")
    admin = Administrador(None, "Administrador Sistema", f"admin{sufijo}@ecotech.cl", nivel_acceso="SENIOR")
    admin.establecer_contrasena("Admin2026*")
    UsuarioDAO.insertar(admin)

    ana = Empleado(None, "Ana Perez", "Desarrolladora", 1200000.0, f"ana{sufijo}@ecotech.cl")
    luis = Empleado(None, "Luis Gomez", "Analista", 1100000.0, f"luis{sufijo}@ecotech.cl")
    EmpleadoDAO.insertar(ana)
    EmpleadoDAO.insertar(luis)

    departamento = Departamento(None, "Tecnologia", ana)
    DepartamentoDAO.insertar(departamento)
    DepartamentoDAO.agregar_empleado(departamento.id_departamento, ana.id_empleado)
    DepartamentoDAO.agregar_empleado(departamento.id_departamento, luis.id_empleado)

    proyecto = Proyecto(None, "Migracion a la nube", "Modernizacion de infraestructura", date.today())
    ProyectoDAO.insertar(proyecto)
    ProyectoDAO.asignar_empleado(proyecto.id_proyecto, ana.id_empleado)
    ProyectoDAO.asignar_empleado(proyecto.id_proyecto, luis.id_empleado)

    reg_ana = ana.registrar_horas(proyecto, 4.0, "Configuracion de contenedores")
    reg_luis = luis.registrar_horas(proyecto, 2.5, "Pruebas")
    RegistroTiempoDAO.insertar(reg_ana)
    RegistroTiempoDAO.insertar(reg_luis)

    informe = admin.generar_informe("Resumen Operativo")
    informe.generar({"Empleados": len(EmpleadoDAO.listar()), "Proyectos": len(ProyectoDAO.listar())})
    InformeDAO.insertar(informe)

    print("\n[READ] Consultando lo guardado")
    print(f"  Por id:     {EmpleadoDAO.buscar_por_id(ana.id_empleado)}")
    print(f"  Por correo: {EmpleadoDAO.buscar_por_correo(luis.correo)}")
    print(f"  {DepartamentoDAO.buscar_por_id(departamento.id_departamento)}")
    print(f"  {ProyectoDAO.buscar_por_id(proyecto.id_proyecto)}")
    registros = RegistroTiempoDAO.listar_por_proyecto(proyecto.id_proyecto)
    print(f"  Horas totales del proyecto: {RegistroDeTiempo.calcular_horas_totales(registros):.1f}")

    print("\n[UPDATE] Cambiando cargo de Luis y renombrando el departamento (Administrador.gestionar_departamento)")
    luis.cargo = "Analista Senior"
    print(f"  Actualizado: {EmpleadoDAO.actualizar(luis)}")
    admin.gestionar_departamento(departamento, nuevo_nombre="Tecnologia e Innovacion")
    print(f"  Actualizado: {DepartamentoDAO.actualizar(departamento)}")

    print("\n[DELETE] Eliminando un registro de horas")
    print(f"  Eliminado: {RegistroTiempoDAO.eliminar(reg_luis.id_registro)}")
    print(f"  Eliminar un id inexistente (no es error, retorna False): {RegistroTiempoDAO.eliminar(999999)}")

    print("\n[ERROR CONTROLADO] Intentando registrar un empleado con un correo repetido")
    repetido = Empleado(None, "Otra Ana", "Testing", 900000.0, ana.correo)
    try:
        EmpleadoDAO.insertar(repetido)
    except DAOError as err:
        print(f"  Capturado DAOError -> mensaje seguro: {err}")
        print(f"  Rollback aplicado: el empleado repetido quedó sin id ({repetido.id_empleado}).")

    print("\nDemostración completada con éxito.")


def main() -> None:
    logging.basicConfig(
        filename=str(RAIZ_PROYECTO / "ecotech.log"),
        level=logging.WARNING,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    try:
        crear_tablas()
    except (DAOError, ConexionError) as err:
        print(f"No se pudo preparar la base de datos: {err}")
        sys.exit(1)

    if "--demo" in sys.argv or "-d" in sys.argv:
        ejecutar(ejecutar_demostracion)
    else:
        try:
            menu_principal()
        except (KeyboardInterrupt, EOFError):  # cierre del programa desde el teclado
            print("\nHasta luego.")


if __name__ == "__main__":
    main()
