import math
import os
import sys
from datetime import date
from typing import Optional

from src.dominio import (
    Administrador,
    Departamento,
    Empleado,
    Informe,
    PagoInternacional,
    Proyecto,
    RegistroClima,
    RegistroDeTiempo,
    Usuario,
)
from src.excepciones import (
    APIConexionError,
    APIRespuestaError,
    APITimeoutError,
    AutenticacionError,
    AutorizacionError,
    ConexionError,
    DAOError,
    EcoTechError,
    ServicioExternoError,
    ValidacionError,
)
from src.persistencia import (
    ClimaDAO,
    DepartamentoDAO,
    EmpleadoDAO,
    InformeDAO,
    PagoInternacionalDAO,
    ProyectoDAO,
    RegistroTiempoDAO,
    UsuarioDAO,
    crear_tablas,
    probar_conexion,
)
from src.seguridad.validador import (
    sanitizar_nombre_archivo,
    sanitizar_texto,
    validar_ciudad,
    validar_codigo_moneda,
)
from src.servicios_externos import ClimaService, DivisasService


def mostrar_error_seguro(accion: str, err: Exception) -> None:
    """
    Imprime mensajes de error controlados para el usuario final sin exponer
    detalles internos de infraestructura, contraseñas o stacktraces (Criterio 3.1.3).
    """
    if isinstance(err, (ValidacionError, AutenticacionError, AutorizacionError)):
        print(f"Advertencia [{accion}]: {err.mensaje}")
    elif isinstance(err, (DAOError, ConexionError)):
        print(f"Error [{accion}]: Ocurrió un problema de persistencia en la base de datos. Operación revertida con seguridad.")
    elif isinstance(err, ServicioExternoError):
        print(f"Error de Servicio Externo [{accion}]: {err.mensaje}")
    else:
        print(f"Error inesperado [{accion}]: La operación no pudo completarse de manera segura.")


def limpiar_pantalla() -> None:
    """Limpia la terminal de forma compatible entre Windows (cls) y Linux/macOS (clear)."""
    if os.getenv("ECOTECH_NO_CLEAR"):
        return
    os.system("cls" if os.name == "nt" else "clear")


def pausar_y_limpiar(mensaje: str = "Presione Enter para continuar...") -> None:
    """Pausa la ejecución para que el usuario pueda leer los resultados antes de limpiar la pantalla."""
    try:
        input(f"\n{mensaje}")
    except (KeyboardInterrupt, EOFError):
        pass
    limpiar_pantalla()


def leer_texto_no_vacio(mensaje: str, max_longitud: int = 150) -> Optional[str]:
    """Solicita una cadena al usuario asegurando que no quede vacía ni contenga caracteres maliciosos."""
    while True:
        try:
            entrada = input(mensaje).strip()
            if entrada:
                return sanitizar_texto(entrada, max_longitud=max_longitud)
            print("Error: El campo no puede estar vacio. Intente nuevamente.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperacion cancelada por el usuario.")
            return None
        except ValidacionError as v_err:
            print(f"Error de formato: {v_err.mensaje}")


def leer_entero(mensaje: str, minimo: Optional[int] = None, maximo: Optional[int] = None) -> Optional[int]:
    """Lee un entero del usuario con validacion de rango y manejo de excepciones."""
    while True:
        try:
            entrada = input(mensaje).strip()
            if not entrada:
                return None
            valor = int(entrada)
            if minimo is not None and valor < minimo:
                print(f"Error: El valor debe ser mayor o igual a {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"Error: El valor debe ser menor o igual a {maximo}.")
                continue
            return valor
        except ValueError:
            print("Error: Debe ingresar un numero entero valido.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperacion cancelada.")
            return None


def leer_flotante(mensaje: str, minimo: Optional[float] = None) -> Optional[float]:
    """Lee un flotante con validacion de valor minimo y proteccion contra NaN e Infinito."""
    while True:
        try:
            entrada = input(mensaje).strip()
            if not entrada:
                return None
            valor = float(entrada)
            if not math.isfinite(valor):
                print("Error: Debe ingresar un número finito (no se permite NaN ni Infinito).")
                continue
            if minimo is not None and valor < minimo:
                print(f"Error: El valor debe ser mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Error: Debe ingresar un numero decimal valido.")
        except (KeyboardInterrupt, EOFError):
            print("\nOperacion cancelada.")
            return None


def leer_fecha(mensaje: str) -> Optional[date]:
    """Lee una fecha en formato YYYY-MM-DD o retorna la fecha actual si queda en blanco."""
    while True:
        try:
            entrada = input(f"{mensaje} (YYYY-MM-DD, Enter para hoy): ").strip()
            if not entrada:
                return date.today()
            return date.fromisoformat(entrada)
        except ValueError:
            print("Error: Formato de fecha invalido. Debe usar YYYY-MM-DD.")
        except (KeyboardInterrupt, EOFError):
            return None


class SistemaCRUD:
    """
    Controlador central de la aplicacion interactiva de gestion EcoTech Solutions.
    Permite operar el CRUD completo sobre la base de datos con tolerancia a fallos.
    """

    def __init__(self) -> None:
        self.empleado_dao = EmpleadoDAO()
        self.departamento_dao = DepartamentoDAO()
        self.proyecto_dao = ProyectoDAO()
        self.registro_dao = RegistroTiempoDAO()
        self.informe_dao = InformeDAO()
        self.usuario_dao = UsuarioDAO()
        self.clima_dao = ClimaDAO()
        self.pago_dao = PagoInternacionalDAO()
        self.clima_service = ClimaService()
        self.divisas_service = DivisasService()
        self.usuario_actual: Optional[Usuario] = None

    def iniciar_sesion(self) -> bool:
        """
        Sistema de control de acceso obligatorio (Gatekeeper) con credenciales encriptadas
        y mitigación de ataques de fuerza bruta mediante límite de reintentos (Criterio 3.1.2).
        """
        limpiar_pantalla()
        print("\n============================================================")
        print("          CONTROL DE ACCESO - ECOTECH SOLUTIONS")
        print("============================================================")

        # Si no existen usuarios, crear administrador inicial para permitir primer acceso
        try:
            usuarios = self.usuario_dao.listar()
            if not usuarios:
                print("Iniciando por primera vez: Registrando Administrador maestro...")
                admin_inicial = Administrador(None, "Administrador Sistema", "admin@ecotech.cl", nivel_acceso="SENIOR")
                admin_inicial.establecer_contrasena("Admin2026*")
                self.usuario_dao.guardar(admin_inicial)
                print("Administrador creado. Credenciales maestras: admin@ecotech.cl / Admin2026*\n")
        except Exception as err:
            mostrar_error_seguro("Inicialización de Usuarios", err)

        try:
            max_intentos = int(os.getenv("MAX_LOGIN_INTENTOS", "3"))
        except ValueError:
            max_intentos = 3

        intentos = 0
        while intentos < max_intentos:
            intentos += 1
            print(f"\n[Autenticación requerida - Intento {intentos} de {max_intentos}]")
            correo = leer_texto_no_vacio("Correo electrónico: ")
            if not correo:
                return False
            clave = leer_texto_no_vacio("Contraseña: ")
            if not clave:
                return False

            try:
                usuario = self.usuario_dao.autenticar(correo, clave)
                if usuario:
                    self.usuario_actual = usuario
                    tipo = "ADMINISTRADOR" if isinstance(usuario, Administrador) else "USUARIO"
                    print("\n============================================================")
                    print(f" Autenticación Exitosa. Bienvenido(a), {usuario.nombre}!")
                    print(f" Nivel: {tipo} | Correo: {usuario.correo}")
                    print("============================================================")
                    pausar_y_limpiar("Presione Enter para ingresar al Sistema EcoTech...")
                    return True
                else:
                    print("Credenciales inválidas. Correo o contraseña incorrectos.")
            except Exception as err:
                mostrar_error_seguro("Autenticación", err)

        print("\n[ALERTA DE SEGURIDAD] Ha superado el número máximo de intentos fallidos permitidos.")
        print("El acceso al sistema ha sido bloqueado preventivamente.")
        pausar_y_limpiar()
        return False

    def menu_empleados(self) -> None:
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("                GESTION DE EMPLEADOS")
            print("------------------------------------------------------------")
            print("[1] Registrar nuevo empleado")
            print("[2] Listar todos los empleados")
            print("[3] Buscar empleado por ID")
            print("[4] Actualizar salario de empleado")
            print("[5] Eliminar empleado")
            print("[6] Liquidar sueldo en moneda extranjera (API Externa)")
            print("[7] Historial de pagos internacionales del personal")
            print("[0] Volver al menu principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opcion: ", 0, 7)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._crear_empleado()
            elif opc == 2:
                self._listar_empleados()
            elif opc == 3:
                self._buscar_empleado()
            elif opc == 4:
                self._actualizar_salario_empleado()
            elif opc == 5:
                self._eliminar_empleado()
            elif opc == 6:
                self._calcular_pago_internacional()
            elif opc == 7:
                self._listar_pagos_internacionales()
            pausar_y_limpiar()

    def _crear_empleado(self) -> None:
        print("\n--- Registro de Empleado ---")
        nombre = leer_texto_no_vacio("Nombre completo: ")
        if not nombre:
            return
        cargo = leer_texto_no_vacio("Cargo: ")
        salario = leer_flotante("Salario mensual: ", minimo=0.0)
        if salario is None:
            return
        direccion = input("Direccion (opcional): ").strip()
        telefono = input("Telefono (opcional): ").strip()
        correo = input("Correo electronico (opcional): ").strip()
        fecha_contrato = leer_fecha("Fecha inicio contrato")

        try:
            emp = Empleado(
                id_empleado=None,
                nombre=nombre,
                cargo=cargo,
                salario=salario,
                direccion=direccion,
                telefono=telefono,
                correo=correo,
                fecha_inicio_contrato=fecha_contrato,
            )
            nuevo_id = self.empleado_dao.guardar(emp)
            print(f"Empleado registrado exitosamente con ID: {nuevo_id}")
        except (ValueError, DAOError) as err:
            print(f"Error al registrar empleado: {err}")

    def _listar_empleados(self) -> None:
        try:
            empleados = self.empleado_dao.listar()
            print("\n--- Lista de Empleados ---")
            if not empleados:
                print("No hay empleados registrados.")
                return
            for e in empleados:
                print(f"ID: {e.id_empleado} | Nombre: {e.nombre} | Cargo: {e.cargo} | Salario: ${e.salario:,.0f} | Correo: {e.correo}")
        except DAOError as err:
            print(f"Error al consultar base de datos: {err}")

    def _buscar_empleado(self) -> None:
        id_emp = leer_entero("Ingrese ID del empleado a buscar: ", minimo=1)
        if not id_emp:
            return
        try:
            emp = self.empleado_dao.buscar_por_id(id_emp)
            if emp:
                print(f"\nEmpleado encontrado:\n  ID: {emp.id_empleado}\n  Nombre: {emp.nombre}\n  Cargo: {emp.cargo}\n  Salario: ${emp.salario:,.0f}\n  Correo: {emp.correo}\n  Telefono: {emp.telefono}\n  Direccion: {emp.direccion}\n  Inicio Contrato: {emp.fecha_inicio_contrato}")
            else:
                print(f"No existe ningun empleado con ID {id_emp}.")
        except DAOError as err:
            print(f"Error: {err}")

    def _actualizar_salario_empleado(self) -> None:
        id_emp = leer_entero("Ingrese ID del empleado: ", minimo=1)
        if not id_emp:
            return
        try:
            emp = self.empleado_dao.buscar_por_id(id_emp)
            if not emp:
                print(f"No se encontro el empleado ID {id_emp}.")
                return
            print(f"Empleado: {emp.nombre} | Salario actual: ${emp.salario:,.0f}")
            nuevo_salario = leer_flotante("Ingrese nuevo salario: ", minimo=0.0)
            if nuevo_salario is None:
                return
            emp.actualizar_salario(nuevo_salario)
            if self.empleado_dao.actualizar(emp):
                print(f"Salario actualizado exitosamente a: ${emp.salario:,.0f}")
            else:
                print("No se pudo actualizar el registro.")
        except (ValueError, DAOError) as err:
            print(f"Error al actualizar salario: {err}")

    def _eliminar_empleado(self) -> None:
        id_emp = leer_entero("Ingrese ID del empleado a eliminar: ", minimo=1)
        if not id_emp:
            return
        confirm = input(f"Esta seguro de eliminar al empleado ID {id_emp}? (s/n): ").strip().lower()
        if confirm == "s":
            try:
                if self.empleado_dao.eliminar(id_emp):
                    print(f"Empleado ID {id_emp} eliminado correctamente.")
                else:
                    print(f"No se encontro ningun empleado con ID {id_emp}.")
            except DAOError as err:
                print(f"Error al eliminar empleado: {err}")

    def menu_departamentos(self) -> None:
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("               GESTION DE DEPARTAMENTOS")
            print("------------------------------------------------------------")
            print("[1] Registrar nuevo departamento")
            print("[2] Listar departamentos")
            print("[3] Buscar departamento y ver empleados")
            print("[4] Asignar empleado a departamento")
            print("[5] Desvincular empleado de departamento")
            print("[6] Eliminar departamento")
            print("[0] Volver al menu principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opcion: ", 0, 6)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._crear_departamento()
            elif opc == 2:
                self._listar_departamentos()
            elif opc == 3:
                self._buscar_departamento()
            elif opc == 4:
                self._asignar_empleado_departamento()
            elif opc == 5:
                self._desvincular_empleado_departamento()
            elif opc == 6:
                self._eliminar_departamento()
            pausar_y_limpiar()

    def _crear_departamento(self) -> None:
        print("\n--- Registro de Departamento ---")
        nombre = leer_texto_no_vacio("Nombre del departamento: ")
        if not nombre:
            return
        gerente = leer_texto_no_vacio("Nombre del gerente a cargo: ")
        try:
            depto = Departamento(id_departamento=None, nombre=nombre, gerente=gerente)
            nuevo_id = self.departamento_dao.guardar(depto)
            print(f"Departamento registrado con ID: {nuevo_id}")
        except DAOError as err:
            print(f"Error al guardar departamento: {err}")

    def _listar_departamentos(self) -> None:
        try:
            deptos = self.departamento_dao.listar()
            print("\n--- Lista de Departamentos ---")
            if not deptos:
                print("No hay departamentos registrados.")
                return
            for d in deptos:
                print(f"ID: {d.id_departamento} | Nombre: {d.nombre} | Gerente: {d.gerente_nombre} | Miembros: {len(d.empleados)}")
        except DAOError as err:
            print(f"Error: {err}")

    def _buscar_departamento(self) -> None:
        id_dep = leer_entero("Ingrese ID del departamento: ", minimo=1)
        if not id_dep:
            return
        try:
            depto = self.departamento_dao.buscar_por_id(id_dep)
            if not depto:
                print(f"No existe departamento con ID {id_dep}.")
                return
            print(f"\nDepartamento: {depto.nombre} | Gerente: {depto.gerente_nombre}")
            print("Empleados asignados:")
            if not depto.empleados:
                print("  (Sin empleados asignados)")
            else:
                for emp in depto.empleados:
                    print(f"  - ID: {emp.id_empleado} | {emp.nombre} ({emp.cargo})")
        except DAOError as err:
            print(f"Error: {err}")

    def _asignar_empleado_departamento(self) -> None:
        id_dep = leer_entero("ID del departamento: ", minimo=1)
        id_emp = leer_entero("ID del empleado a asignar: ", minimo=1)
        if not id_dep or not id_emp:
            return
        try:
            if self.departamento_dao.agregar_empleado(id_dep, id_emp):
                print(f"Empleado {id_emp} asignado al departamento {id_dep} exitosamente.")
            else:
                print("El empleado ya esta asignado o los IDs no existen.")
        except DAOError as err:
            print(f"Error al asignar: {err}")

    def _desvincular_empleado_departamento(self) -> None:
        id_dep = leer_entero("ID del departamento: ", minimo=1)
        id_emp = leer_entero("ID del empleado a desvincular: ", minimo=1)
        if not id_dep or not id_emp:
            return
        try:
            if self.departamento_dao.eliminar_empleado(id_dep, id_emp):
                print(f"Empleado {id_emp} desvinculado del departamento {id_dep}.")
            else:
                print("No se encontro la relacion indicada.")
        except DAOError as err:
            print(f"Error: {err}")

    def _eliminar_departamento(self) -> None:
        id_dep = leer_entero("ID del departamento a eliminar: ", minimo=1)
        if not id_dep:
            return
        confirm = input(f"Confirmar eliminacion del departamento ID {id_dep}? (s/n): ").strip().lower()
        if confirm == "s":
            try:
                if self.departamento_dao.eliminar(id_dep):
                    print(f"Departamento ID {id_dep} eliminado.")
                else:
                    print(f"No existe el departamento ID {id_dep}.")
            except DAOError as err:
                print(f"Error: {err}")

    def menu_proyectos(self) -> None:
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("                 GESTION DE PROYECTOS")
            print("------------------------------------------------------------")
            print("[1] Registrar nuevo proyecto")
            print("[2] Listar proyectos")
            print("[3] Ver detalles y personal asignado a proyecto")
            print("[4] Asignar empleado a proyecto")
            print("[5] Desasignar empleado de proyecto")
            print("[6] Eliminar proyecto")
            print("[7] Consultar clima operativo en terreno (API Externa)")
            print("[8] Historial meteorologico del proyecto")
            print("[0] Volver al menu principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opcion: ", 0, 8)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._crear_proyecto()
            elif opc == 2:
                self._listar_proyectos()
            elif opc == 3:
                self._buscar_proyecto()
            elif opc == 4:
                self._asignar_empleado_proyecto()
            elif opc == 5:
                self._desasignar_empleado_proyecto()
            elif opc == 6:
                self._eliminar_proyecto()
            elif opc == 7:
                self._consultar_clima_proyecto()
            elif opc == 8:
                self._listar_historial_clima()
            pausar_y_limpiar()

    def _crear_proyecto(self) -> None:
        print("\n--- Registro de Proyecto ---")
        nombre = leer_texto_no_vacio("Nombre del proyecto: ")
        if not nombre:
            return
        descripcion = leer_texto_no_vacio("Descripcion: ")
        fecha_inicio = leer_fecha("Fecha de inicio")
        try:
            proy = Proyecto(id_proyecto=None, nombre=nombre, descripcion=descripcion, fecha_inicio=fecha_inicio)
            nuevo_id = self.proyecto_dao.guardar(proy)
            print(f"Proyecto registrado con ID: {nuevo_id}")
        except DAOError as err:
            print(f"Error al guardar proyecto: {err}")

    def _listar_proyectos(self) -> None:
        try:
            proyectos = self.proyecto_dao.listar()
            print("\n--- Lista de Proyectos ---")
            if not proyectos:
                print("No hay proyectos registrados.")
                return
            for p in proyectos:
                horas = self.registro_dao.total_horas_proyecto(p.id_proyecto)
                print(f"ID: {p.id_proyecto} | Nombre: {p.nombre} | Inicio: {p.fecha_inicio} | Personal: {len(p.empleados_asignados)} | Horas Totales: {horas:.1f}")
        except DAOError as err:
            print(f"Error: {err}")

    def _buscar_proyecto(self) -> None:
        id_proy = leer_entero("ID del proyecto: ", minimo=1)
        if not id_proy:
            return
        try:
            proy = self.proyecto_dao.buscar_por_id(id_proy)
            if not proy:
                print(f"No existe proyecto con ID {id_proy}.")
                return
            horas = self.registro_dao.total_horas_proyecto(id_proy)
            print(f"\nProyecto: {proy.nombre}\nDescripcion: {proy.descripcion}\nFecha Inicio: {proy.fecha_inicio}\nHoras trabajadas: {horas:.1f}")
            print("Personal asignado:")
            if not proy.empleados_asignados:
                print("  (Sin personal asignado)")
            else:
                for emp in proy.empleados_asignados:
                    print(f"  - ID: {emp.id_empleado} | {emp.nombre} ({emp.cargo})")
        except DAOError as err:
            print(f"Error: {err}")

    def _asignar_empleado_proyecto(self) -> None:
        id_proy = leer_entero("ID del proyecto: ", minimo=1)
        id_emp = leer_entero("ID del empleado a asignar: ", minimo=1)
        if not id_proy or not id_emp:
            return
        try:
            if self.proyecto_dao.asignar_empleado(id_proy, id_emp):
                print(f"Empleado {id_emp} asignado al proyecto {id_proy} exitosamente.")
            else:
                print("El empleado ya esta asignado o los IDs no son validos.")
        except DAOError as err:
            print(f"Error al asignar: {err}")

    def _desasignar_empleado_proyecto(self) -> None:
        id_proy = leer_entero("ID del proyecto: ", minimo=1)
        id_emp = leer_entero("ID del empleado a desasignar: ", minimo=1)
        if not id_proy or not id_emp:
            return
        try:
            if self.proyecto_dao.desasignar_empleado(id_proy, id_emp):
                print(f"Empleado {id_emp} desasignado del proyecto {id_proy}.")
            else:
                print("No se encontro dicha asignacion.")
        except DAOError as err:
            print(f"Error: {err}")

    def _eliminar_proyecto(self) -> None:
        id_proy = leer_entero("ID del proyecto a eliminar: ", minimo=1)
        if not id_proy:
            return
        confirm = input(f"Confirmar eliminacion del proyecto ID {id_proy}? (s/n): ").strip().lower()
        if confirm == "s":
            try:
                if self.proyecto_dao.eliminar(id_proy):
                    print(f"Proyecto ID {id_proy} eliminado.")
                else:
                    print(f"No existe proyecto con ID {id_proy}.")
            except DAOError as err:
                print(f"Error: {err}")

    def menu_registro_tiempo(self) -> None:
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("             REGISTRO DE HORAS Y TIEMPOS")
            print("------------------------------------------------------------")
            print("[1] Registrar horas trabajadas")
            print("[2] Listar todos los registros de tiempo")
            print("[3] Consultar registros por empleado")
            print("[4] Consultar registros y total por proyecto")
            print("[5] Eliminar registro de tiempo")
            print("[0] Volver al menu principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opcion: ", 0, 5)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._crear_registro_tiempo()
            elif opc == 2:
                self._listar_registros_tiempo()
            elif opc == 3:
                self._registros_por_empleado()
            elif opc == 4:
                self._registros_por_proyecto()
            elif opc == 5:
                self._eliminar_registro_tiempo()
            pausar_y_limpiar()

    def _crear_registro_tiempo(self) -> None:
        print("\n--- Registro de Carga Horaria ---")
        id_emp = leer_entero("ID del empleado: ", minimo=1)
        id_proy = leer_entero("ID del proyecto: ", minimo=1)
        if not id_emp or not id_proy:
            return

        horas = leer_flotante("Horas trabajadas (maximo 24.0): ", minimo=0.1)
        if horas is None:
            return
        descripcion = leer_texto_no_vacio("Descripcion de las tareas realizadas: ")
        fecha = leer_fecha("Fecha del registro")

        try:
            reg = RegistroDeTiempo(
                id_registro=None,
                fecha=fecha,
                horas=horas,
                descripcion_tareas=descripcion,
                id_empleado=id_emp,
                id_proyecto=id_proy,
            )
            nuevo_id = self.registro_dao.guardar(reg)
            print(f"Registro de tiempo guardado exitosamente con ID: {nuevo_id}")
        except (ValueError, DAOError) as err:
            print(f"Error al registrar horas: {err}")

    def _listar_registros_tiempo(self) -> None:
        try:
            registros = self.registro_dao.listar()
            print("\n--- Historial de Tiempos Registrados ---")
            if not registros:
                print("No hay registros de tiempo.")
                return
            for r in registros:
                print(f"ID: {r.id_registro} | Fecha: {r.fecha} | Empleado: {r.id_empleado} | Proyecto: {r.id_proyecto} | Horas: {r.horas} | Tareas: {r.descripcion_tareas}")
        except DAOError as err:
            print(f"Error: {err}")

    def _registros_por_empleado(self) -> None:
        id_emp = leer_entero("ID del empleado: ", minimo=1)
        if not id_emp:
            return
        try:
            registros = self.registro_dao.listar_por_empleado(id_emp)
            print(f"\n--- Registros del Empleado ID {id_emp} ---")
            if not registros:
                print("Sin registros de tiempo para este empleado.")
                return
            for r in registros:
                print(f"ID: {r.id_registro} | Fecha: {r.fecha} | Proyecto: {r.id_proyecto} | Horas: {r.horas} | Tareas: {r.descripcion_tareas}")
            total = RegistroDeTiempo.calcularHorasTotales(registros)
            print(f"Total acumulado por el empleado: {total:.1f} horas.")
        except DAOError as err:
            print(f"Error: {err}")

    def _registros_por_proyecto(self) -> None:
        id_proy = leer_entero("ID del proyecto: ", minimo=1)
        if not id_proy:
            return
        try:
            registros = self.registro_dao.listar_por_proyecto(id_proy)
            print(f"\n--- Registros del Proyecto ID {id_proy} ---")
            if not registros:
                print("Sin registros de tiempo para este proyecto.")
                return
            for r in registros:
                print(f"ID: {r.id_registro} | Fecha: {r.fecha} | Empleado: {r.id_empleado} | Horas: {r.horas} | Tareas: {r.descripcion_tareas}")
            total = RegistroDeTiempo.calcularHorasTotales(registros)
            print(f"Total de horas invertidas en el proyecto: {total:.1f} horas.")
        except DAOError as err:
            print(f"Error: {err}")

    def _eliminar_registro_tiempo(self) -> None:
        id_reg = leer_entero("ID del registro a eliminar: ", minimo=1)
        if not id_reg:
            return
        try:
            if self.registro_dao.eliminar(id_reg):
                print(f"Registro ID {id_reg} eliminado.")
            else:
                print(f"No existe registro con ID {id_reg}.")
        except DAOError as err:
            print(f"Error: {err}")

    def menu_informes(self) -> None:
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("                 INFORMES Y REPORTES")
            print("------------------------------------------------------------")
            print("[1] Generar y guardar informe general del sistema")
            print("[2] Listar informes guardados")
            print("[3] Exportar informe a archivo de texto")
            print("[4] Eliminar informe")
            print("[0] Volver al menu principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opcion: ", 0, 4)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._generar_informe_general()
            elif opc == 2:
                self._listar_informes()
            elif opc == 3:
                self._exportar_informe()
            elif opc == 4:
                self._eliminar_informe()
            pausar_y_limpiar()

    def _generar_informe_general(self) -> None:
        try:
            empleados = self.empleado_dao.listar()
            deptos = self.departamento_dao.listar()
            proyectos = self.proyecto_dao.listar()
            tiempos = self.registro_dao.listar()

            total_salarios = sum(e.salario for e in empleados)
            total_horas = RegistroDeTiempo.calcularHorasTotales(tiempos)

            datos = {
                "Total de Empleados": len(empleados),
                "Planilla Salarial Mensual": f"${total_salarios:,.0f}",
                "Departamentos Activos": len(deptos),
                "Proyectos Registrados": len(proyectos),
                "Total de Horas Trabajadas": f"{total_horas:.1f} hrs",
            }

            informe = Informe(id_informe=None, tipo="Resumen Gerencial EcoTech", fecha_generacion=date.today())
            contenido = informe.generar(datos)

            nuevo_id = self.informe_dao.guardar(informe)
            print("\nInforme generado con exito:")
            print(contenido)
            print(f"Guardado en base de datos con ID: {nuevo_id}")
        except Exception as err:
            print(f"Error al generar informe: {err}")

    def _listar_informes(self) -> None:
        try:
            informes = self.informe_dao.listar()
            print("\n--- Informes Almacenados ---")
            if not informes:
                print("No hay informes registrados.")
                return
            for inf in informes:
                print(f"ID: {inf.id_informe} | Tipo: {inf.tipo} | Fecha: {inf.fecha_generacion}")
        except DAOError as err:
            print(f"Error: {err}")

    def _exportar_informe(self) -> None:
        id_inf = leer_entero("Ingrese ID del informe a exportar: ", minimo=1)
        if not id_inf:
            return
        try:
            inf = self.informe_dao.buscar_por_id(id_inf)
            if not inf:
                print(f"No existe informe con ID {id_inf}.")
                return
            nombre_archivo = input(f"Nombre de archivo de salida (por defecto informe_{id_inf}.txt): ").strip()
            if not nombre_archivo:
                nombre_archivo = f"informe_{id_inf}.txt"
            else:
                nombre_archivo = sanitizar_nombre_archivo(nombre_archivo, extensiones_permitidas=(".txt", ".log"))
            inf.exportar(nombre_archivo)
            print(f"Informe exportado exitosamente al archivo: {nombre_archivo}")
        except Exception as err:
            mostrar_error_seguro("Exportar Informe", err)

    def _eliminar_informe(self) -> None:
        id_inf = leer_entero("ID del informe a eliminar: ", minimo=1)
        if not id_inf:
            return
        try:
            if self.informe_dao.eliminar(id_inf):
                print(f"Informe ID {id_inf} eliminado.")
            else:
                print(f"No existe informe con ID {id_inf}.")
        except DAOError as err:
            print(f"Error: {err}")

    def menu_usuarios(self) -> None:
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("            USUARIOS Y AUTENTICACION SEGURA")
            print("------------------------------------------------------------")
            print("[1] Registrar nuevo usuario")
            print("[2] Registrar nuevo administrador")
            print("[3] Probar autenticacion de credenciales (Hash SHA-256)")
            print("[4] Listar usuarios y administradores")
            print("[5] Eliminar usuario")
            print("[0] Volver al menu principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opcion: ", 0, 5)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._crear_usuario()
            elif opc == 2:
                self._crear_administrador()
            elif opc == 3:
                self._probar_autenticacion()
            elif opc == 4:
                self._listar_usuarios()
            elif opc == 5:
                self._eliminar_usuario()
            pausar_y_limpiar()

    def _crear_usuario(self) -> None:
        print("\n--- Registro de Usuario ---")
        nombre = leer_texto_no_vacio("Nombre completo: ")
        if not nombre:
            return
        correo = leer_texto_no_vacio("Correo electronico: ")
        if not correo:
            return
        clave = leer_texto_no_vacio("Contrasena (minimo 6 caracteres): ")
        if not clave:
            return
        try:
            u = Usuario(None, nombre, correo)
            u.establecer_contrasena(clave)
            nuevo_id = self.usuario_dao.guardar(u)
            print(f"Usuario registrado exitosamente con ID: {nuevo_id}")
        except Exception as err:
            mostrar_error_seguro("Registro Usuario", err)

    def _crear_administrador(self) -> None:
        print("\n--- Registro de Administrador ---")
        nombre = leer_texto_no_vacio("Nombre completo: ")
        if not nombre:
            return
        correo = leer_texto_no_vacio("Correo electronico: ")
        if not correo:
            return
        clave = leer_texto_no_vacio("Contrasena (minimo 6 caracteres): ")
        if not clave:
            return
        nivel = input("Nivel de acceso (Enter para ADMIN): ").strip() or "ADMIN"
        try:
            admin = Administrador(None, nombre, correo, nivel_acceso=nivel)
            admin.establecer_contrasena(clave)
            nuevo_id = self.usuario_dao.guardar(admin)
            print(f"Administrador registrado exitosamente con ID: {nuevo_id}")
        except Exception as err:
            mostrar_error_seguro("Registro Administrador", err)

    def _probar_autenticacion(self) -> None:
        print("\n--- Verificacion de Autenticacion ---")
        correo = leer_texto_no_vacio("Correo electronico: ")
        if not correo:
            return
        clave = leer_texto_no_vacio("Contrasena: ")
        if not clave:
            return
        try:
            usuario = self.usuario_dao.autenticar(correo, clave)
            if usuario:
                tipo = "Administrador" if isinstance(usuario, Administrador) else "Usuario"
                print(f"Autenticacion EXITOSA. Bienvenido/a {usuario.nombre} (Rol: {tipo}).")
            else:
                print("Autenticacion FALLIDA. Correo o contrasena incorrectos.")
        except Exception as err:
            mostrar_error_seguro("Autenticación", err)

    def _listar_usuarios(self) -> None:
        try:
            usuarios = self.usuario_dao.listar()
            print("\n--- Lista de Usuarios ---")
            if not usuarios:
                print("No hay usuarios registrados.")
                return
            for u in usuarios:
                tipo = "ADMIN" if isinstance(u, Administrador) else "USUARIO"
                print(f"ID: {u.id} | Tipo: {tipo} | Nombre: {u.nombre} | Correo: {u.correo}")
        except DAOError as err:
            print(f"Error: {err}")

    def _eliminar_usuario(self) -> None:
        id_u = leer_entero("ID del usuario a eliminar: ", minimo=1)
        if not id_u:
            return
        confirm = input(f"Confirmar eliminacion del usuario ID {id_u}? (s/n): ").strip().lower()
        if confirm == "s":
            try:
                if self.usuario_dao.eliminar(id_u):
                    print(f"Usuario ID {id_u} eliminado.")
                else:
                    print(f"No existe usuario con ID {id_u}.")
            except DAOError as err:
                print(f"Error: {err}")


    def menu_clima_proyectos(self) -> None:
        """Submenú interactivo para la gestión meteorológica de proyectos (Problemática 1)."""
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("     PLANIFICACIÓN OPERATIVA Y CLIMA (API EXTERNA)")
            print("------------------------------------------------------------")
            print("[1] Consultar clima operativo en tiempo real para un proyecto")
            print("[2] Ver última condición meteorológica guardada (Caché local)")
            print("[3] Historial de consultas meteorológicas por proyecto")
            print("[4] Listar todas las mediciones climáticas del sistema")
            print("[0] Volver al menú principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opción: ", 0, 4)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._consultar_clima_proyecto()
            elif opc == 2:
                self._ver_ultimo_clima_proyecto()
            elif opc == 3:
                self._listar_historial_clima()
            elif opc == 4:
                self._listar_todas_mediciones_clima()
            pausar_y_limpiar()

    def _consultar_clima_proyecto(self) -> None:
        print("\n--- Consulta Meteorológica de Proyecto en Tiempo Real ---")
        id_proy = leer_entero("ID del proyecto a evaluar (Enter para omitir asociación): ", minimo=1)
        proy_nombre = ""
        if id_proy:
            try:
                proy = self.proyecto_dao.buscar_por_id(id_proy)
                if proy:
                    proy_nombre = proy.nombre
                    print(f"Proyecto seleccionado: {proy.nombre} (ID: {id_proy})")
                else:
                    print(f"Advertencia: Proyecto ID {id_proy} no existe. Se continuará como consulta libre.")
                    id_proy = None
            except DAOError as err:
                mostrar_error_seguro("Buscar Proyecto", err)

        ciudad = leer_texto_no_vacio("Ciudad o localidad de ejecución (ej: Santiago, Antofagasta, Temuco): ")
        if not ciudad:
            return

        print(f"\nConsultando servicio meteorológico para '{ciudad}'...")
        try:
            registro = self.clima_service.consultar_clima(ciudad, id_proy)
            estado_icono = "FAVORABLE" if registro.es_condicion_favorable() else "ALERTA / ADVERSO"

            print("\n============================================================")
            print("      REPORTE METEOROLÓGICO Y APTITUD OPERATIVA ECOTECH")
            print("============================================================")
            if proy_nombre:
                print(f" Proyecto:          {proy_nombre} [ID: {id_proy}]")
            print(f" Localidad:         {registro.ciudad}")
            print(f" Temperatura:       {registro.temperatura:.1f} °C")
            print(f" Humedad Relativa:  {registro.humedad:.0f} %")
            print(f" Condición:         {registro.estado_clima}")
            print(f" Viabilidad Faenas: {estado_icono}")
            print("------------------------------------------------------------")
            print(f" Directriz Operativa:\n {registro.recomendacion}")
            print("============================================================")

            confirm = input("\n¿Desea guardar esta medición en la base de datos local? (s/n, Enter para Sí): ").strip().lower()
            if confirm != "n":
                nuevo_id = self.clima_dao.guardar(registro)
                print(f"Medición climática persistida exitosamente con ID local: {nuevo_id}")
        except (APIConexionError, APITimeoutError) as err:
            print(f"\n[AVISO DE CONTINGENCIA] {err.mensaje}")
            if id_proy:
                print("Intentando recuperar la última medición guardada en la base de datos local...")
                self._ver_ultimo_clima_proyecto(id_proy)
        except Exception as err:
            mostrar_error_seguro("Consulta Meteorológica", err)

    def _ver_ultimo_clima_proyecto(self, id_proy: Optional[int] = None) -> None:
        if not id_proy:
            id_proy = leer_entero("Ingrese ID del proyecto: ", minimo=1)
            if not id_proy:
                return

        try:
            ultimo = self.clima_dao.obtener_ultimo_clima(id_proy)
            if ultimo:
                print(f"\n--- Último Registro Meteorológico Guardado para Proyecto ID {id_proy} ---")
                print(f"Fecha Registro:   {ultimo.fecha_consulta}")
                print(f"Localidad:        {ultimo.ciudad}")
                print(f"Temperatura:      {ultimo.temperatura:.1f} °C | Humedad: {ultimo.humedad:.0f} %")
                print(f"Condición:        {ultimo.estado_clima}")
                print(f"Recomendación:    {ultimo.recomendacion}")
            else:
                print(f"No hay registros meteorológicos previos guardados para el proyecto ID {id_proy}.")
        except DAOError as err:
            mostrar_error_seguro("Recuperar Clima Local", err)

    def _listar_historial_clima(self) -> None:
        id_proy = leer_entero("ID del proyecto a consultar: ", minimo=1)
        if not id_proy:
            return
        try:
            historial = self.clima_dao.listar_por_proyecto(id_proy)
            print(f"\n--- Historial Meteorológico de Proyecto ID {id_proy} ({len(historial)} registros) ---")
            if not historial:
                print("No hay mediciones climáticas guardadas para este proyecto.")
                return
            for reg in historial:
                print(f"[{reg.fecha_consulta}] ID: {reg.id_registro_clima} | {reg.ciudad} | {reg.temperatura:.1f}°C | {reg.humedad:.0f}% | {reg.estado_clima}")
        except DAOError as err:
            mostrar_error_seguro("Listar Historial Clima", err)

    def _listar_todas_mediciones_clima(self) -> None:
        try:
            todas = self.clima_dao.listar_todos()
            print(f"\n--- Todas las Mediciones Meteorológicas en el Sistema ({len(todas)}) ---")
            if not todas:
                print("No hay mediciones registradas.")
                return
            for reg in todas:
                proy_txt = f"Proyecto ID {reg.id_proyecto}" if reg.id_proyecto else "Sin Proyecto"
                print(f"ID: {reg.id_registro_clima} | {proy_txt} | {reg.ciudad} | {reg.temperatura:.1f}°C | {reg.estado_clima} | {reg.fecha_consulta}")
        except DAOError as err:
            mostrar_error_seguro("Listar Mediciones", err)

    def menu_pagos_internacionales(self) -> None:
        """Submenú interactivo para la gestión de liquidaciones en divisas (Problemática 2)."""
        while True:
            limpiar_pantalla()
            print("\n------------------------------------------------------------")
            print("     PAGOS INTERNACIONALES Y DIVISAS (API EXTERNA)")
            print("------------------------------------------------------------")
            print("[1] Calcular y registrar liquidación en moneda extranjera")
            print("[2] Consultar cotización de divisas en tiempo real (USD, EUR, etc.)")
            print("[3] Historial de pagos internacionales de un empleado")
            print("[4] Historial de pagos internacionales por proyecto")
            print("[5] Listar todas las liquidaciones internacionales")
            print("[0] Volver al menú principal")
            print("------------------------------------------------------------")

            opc = leer_entero("Seleccione una opción: ", 0, 5)
            if opc is None or opc == 0:
                break

            if opc == 1:
                self._calcular_pago_internacional()
            elif opc == 2:
                self._consultar_cotizacion_divisa()
            elif opc == 3:
                self._listar_pagos_empleado()
            elif opc == 4:
                self._listar_pagos_por_proyecto()
            elif opc == 5:
                self._listar_pagos_internacionales()
            pausar_y_limpiar()

    def _calcular_pago_internacional(self) -> None:
        print("\n--- Liquidación de Pago en Moneda Extranjera ---")
        id_emp = leer_entero("ID del empleado a liquidar: ", minimo=1)
        if not id_emp:
            return

        try:
            emp = self.empleado_dao.buscar_por_id(id_emp)
            if not emp:
                print(f"No existe ningún empleado registrado con ID {id_emp}.")
                return

            print(f"Empleado: {emp.nombre} | Cargo: {emp.cargo} | Sueldo base: ${emp.salario:,.0f} CLP")
            moneda_dest = input("Moneda destino de pago (ej: USD, EUR, UF, BRL) [Enter para USD]: ").strip().upper() or "USD"
            id_proy = leer_entero("ID del proyecto asociado (opcional, Enter para omitir): ", minimo=1)
            detalles_extra = input("Detalles adicionales o concepto (opcional): ").strip()

            print(f"\nConsultando tasa de cambio en tiempo real para CLP -> {moneda_dest}...")
            pago = self.divisas_service.calcular_pago_internacional(
                id_empleado=emp.id_empleado,
                salario_origen=emp.salario,
                moneda_destino=moneda_dest,
                id_proyecto=id_proy,
                detalles_adicionales=detalles_extra,
            )

            print("\n============================================================")
            print("         COMPROBANTE DE LIQUIDACIÓN INTERNACIONAL")
            print("============================================================")
            print(f" Empleado:           {emp.nombre} (ID: {emp.id_empleado})")
            if id_proy:
                print(f" Proyecto Vinculado: ID {id_proy}")
            print(f" Salario en Origen:  ${pago.monto_origen:,.2f} {pago.moneda_origen}")
            print(f" Monto Convertido:   ${pago.monto_convertido:,.2f} {pago.moneda_destino}")
            print(f" Tasa de Cambio:     {pago.tipo_cambio:.6f}")
            print(f" Fecha Emisión:      {pago.fecha_pago}")
            print(f" Detalle / Fuente:\n {pago.detalles}")
            print("============================================================")

            confirm = input("\n¿Desea registrar y persistir este pago en la base de datos? (s/n, Enter para Sí): ").strip().lower()
            if confirm != "n":
                nuevo_id = self.pago_dao.guardar(pago)
                print(f"Pago internacional registrado exitosamente con ID: {nuevo_id}")
        except Exception as err:
            mostrar_error_seguro("Liquidación Internacional", err)

    def _consultar_cotizacion_divisa(self) -> None:
        print("\n--- Consulta de Tipo de Cambio en Tiempo Real ---")
        moneda_dest = input("Moneda a cotizar frente a CLP (ej: USD, EUR, UF, BRL) [Enter para USD]: ").strip().upper() or "USD"
        try:
            tasa_info = self.divisas_service.obtener_tasa_cambio(moneda_destino=moneda_dest, moneda_origen="CLP")
            tasa = tasa_info["tasa_directa"]
            ref = tasa_info.get("valor_referencia", 0.0)
            print("\n============================================================")
            print(f" Cotización 1 {moneda_dest} = ${ref:,.2f} CLP")
            print(f" Factor de conversión (1 CLP = {tasa:.6f} {moneda_dest})")
            print(f" Fuente oficial: {tasa_info['fuente']}")
            print(f" Fecha cotización: {tasa_info['fecha_actualizacion']}")
            print("============================================================")
        except Exception as err:
            mostrar_error_seguro("Cotización Divisa", err)

    def _listar_pagos_empleado(self) -> None:
        id_emp = leer_entero("ID del empleado: ", minimo=1)
        if not id_emp:
            return
        try:
            pagos = self.pago_dao.listar_por_empleado(id_emp)
            print(f"\n--- Historial de Pagos Internacionales - Empleado ID {id_emp} ({len(pagos)}) ---")
            if not pagos:
                print("No hay pagos internacionales registrados para este empleado.")
                return
            for p in pagos:
                print(f"ID: {p.id_pago} | {p.fecha_pago} | ${p.monto_origen:,.0f} {p.moneda_origen} -> ${p.monto_convertido:,.2f} {p.moneda_destino} (Tasa: {p.tipo_cambio:.4f})")
        except DAOError as err:
            mostrar_error_seguro("Listar Pagos Empleado", err)

    def _listar_pagos_por_proyecto(self) -> None:
        id_proy = leer_entero("ID del proyecto: ", minimo=1)
        if not id_proy:
            return
        try:
            pagos = self.pago_dao.listar_por_proyecto(id_proy)
            print(f"\n--- Pagos Internacionales - Proyecto ID {id_proy} ({len(pagos)}) ---")
            if not pagos:
                print("No hay pagos internacionales registrados para este proyecto.")
                return
            for p in pagos:
                print(f"ID: {p.id_pago} | Emp ID: {p.id_empleado} | ${p.monto_convertido:,.2f} {p.moneda_destino} | {p.fecha_pago}")
        except DAOError as err:
            mostrar_error_seguro("Listar Pagos Proyecto", err)

    def _listar_pagos_internacionales(self) -> None:
        try:
            pagos = self.pago_dao.listar_todos()
            print(f"\n--- Registro General de Pagos Internacionales ({len(pagos)}) ---")
            if not pagos:
                print("No hay pagos internacionales registrados.")
                return
            for p in pagos:
                proy_txt = f"Proyecto ID {p.id_proyecto}" if p.id_proyecto else "Sin Proyecto"
                print(f"ID: {p.id_pago} | Emp ID: {p.id_empleado} | {proy_txt} | ${p.monto_origen:,.0f} {p.moneda_origen} -> ${p.monto_convertido:,.2f} {p.moneda_destino} | {p.fecha_pago}")
        except DAOError as err:
            mostrar_error_seguro("Listar Pagos", err)


def iniciar_interfaz_crud() -> None:
    """Punto de entrada al menu interactivo principal con control de acceso (Gatekeeper)."""
    try:
        crear_tablas()
    except Exception as err:
        print(f"Advertencia: No fue posible verificar la base de datos: {err}")

    app = SistemaCRUD()

    # Paso 2: Autenticación obligatoria antes de ingresar al sistema (Criterio 3.1.2)
    if not app.iniciar_sesion():
        print("\nCerrando aplicación por falta de autenticación. Hasta pronto.")
        return

    while True:
        limpiar_pantalla()
        rol_usuario = "ADMIN" if isinstance(app.usuario_actual, Administrador) else "USUARIO"
        nombre_usuario = app.usuario_actual.nombre if app.usuario_actual else "Invitado"

        print("\n============================================================")
        print("          SISTEMA DE GESTION ECOTECH SOLUTIONS")
        print(f" Sesión Activa: {nombre_usuario} [{rol_usuario}]")
        print("============================================================")
        print("[1] Gestión de Empleados")
        print("[2] Gestión de Departamentos")
        print("[3] Gestión de Proyectos")
        print("[4] Registro de Horas y Tiempos")
        print("[5] Informes y Reportes")
        print("[6] Planificación Operativa y Clima de Proyectos (API Externa)")
        print("[7] Gestión de Pagos Internacionales en Divisas (API Externa)")
        print("[8] Usuarios y Control de Acceso")
        print("[0] Cerrar Sesión y Salir")
        print("============================================================")

        opc = leer_entero("Seleccione una opción: ", 0, 8)
        if opc is None or opc == 0:
            limpiar_pantalla()
            print(f"\nCerrando sesión de {nombre_usuario} en EcoTech Solutions. Hasta pronto.\n")
            break

        if opc == 1:
            app.menu_empleados()
        elif opc == 2:
            app.menu_departamentos()
        elif opc == 3:
            app.menu_proyectos()
        elif opc == 4:
            app.menu_registro_tiempo()
        elif opc == 5:
            app.menu_informes()
        elif opc == 6:
            app.menu_clima_proyectos()
        elif opc == 7:
            app.menu_pagos_internacionales()
        elif opc == 8:
            app.menu_usuarios()
